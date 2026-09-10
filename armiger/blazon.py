"""Generate a random coat of arms: a blazon, and the SVG that depicts it.

Heraldry is a constraint system, not a pile of random shapes, so the generator
works the way a herald does: pick a field, divide it or not, lay an ordinary
over it, then charge it -- checking the rule of tincture at each step.

Everything renders monochrome. Tinctures become Petra Sancta hatching (vertical
lines for gules, horizontal for azure, dots for or), which is how engravers have
encoded colour in one ink since the 1630s. It is also, conveniently, the only
thing a braille cell can say.
"""

import random

# --- Tinctures -------------------------------------------------------------

# Heraldry splits tinctures into metals and colours. The rule of tincture says
# never put metal on metal or colour on colour, which is what keeps arms legible
# at a distance -- exactly the property we need at 40 dots across.
METALS = ["or", "argent"]
COLOURS = ["gules", "azure", "sable", "vert", "purpure"]

# Petra Sancta hatching. `density` is how much ink the pattern lays down at full
# resolution; the renderer uses it to decide what survives a downsample.
HATCH = {
    "argent": {"kind": "plain", "density": 0.0},
    "or": {"kind": "dots", "density": 0.22},
    "gules": {"kind": "vertical", "density": 0.34},
    "azure": {"kind": "horizontal", "density": 0.34},
    "vert": {"kind": "bend", "density": 0.34},
    "purpure": {"kind": "bend-sinister", "density": 0.34},
    "sable": {"kind": "cross", "density": 0.62},
}


# Furs sit outside the metal/colour split in theory, and heralds treat each one
# as whichever it reads as. Flattened to two tones that judgement is simply how
# light the fur draws: ermine and vair are mostly white ground, counter-ermine
# is mostly black.
FUR_IS_METAL = {"ermine": True, "vair": True, "counter-ermine": False}


def is_metal(tincture):
    if tincture in FUR_IS_METAL:
        return FUR_IS_METAL[tincture]
    return tincture in METALS


def contrasts(a, b):
    """True when `a` on `b` satisfies the rule of tincture."""
    return is_metal(a) != is_metal(b)


def pick_contrasting(against, rng):
    pool = COLOURS if is_metal(against) else METALS
    return rng.choice(pool)


# --- Vocabulary ------------------------------------------------------------

# Divisions of the field. Each is a pair of half-field polygons in a 0..100 box.
DIVISIONS = {
    "per pale": [[(0, 0), (50, 0), (50, 100), (0, 100)],
                 [(50, 0), (100, 0), (100, 100), (50, 100)]],
    "per fess": [[(0, 0), (100, 0), (100, 50), (0, 50)],
                 [(0, 50), (100, 50), (100, 100), (0, 100)]],
    "per bend": [[(0, 0), (100, 0), (0, 100)],
                 [(100, 0), (100, 100), (0, 100)]],
    "per chevron": [[(0, 100), (50, 45), (100, 100)],
                    [(0, 0), (100, 0), (100, 100), (50, 45), (0, 100)]],
}

# Ordinaries: the bold geometric charges. These are what actually read at low
# resolution, so the generator leans on them heavily.
ORDINARIES = ["cross", "fess", "pale", "bend", "chevron", "saltire", "chief"]

# Variations of the field: a repeating two-tincture pattern instead of a flat
# ground. These are the best thing in the whole vocabulary for this target --
# they are already two-tone by definition, so nothing is lost flattening them,
# and the repeat gives texture that hatching could never survive at this size.
VARIATIONS = {
    "barry": {"count": 6},        # horizontal bars
    "paly": {"count": 6},         # vertical pales
    "bendy": {"count": 6},        # diagonal bends
    "checky": {"count": 6},       # checkerboard
    "lozengy": {"count": 5},      # diamonds
    "gyronny": {"count": 8},      # wedges radiating from the centre
    "chevronny": {"count": 5},    # stacked chevrons
}

# Furs are the third class of tincture, alongside metals and colours, and they
# are the most medieval thing on a shield. Ermine is a white field strewn with
# black tails; counter-ermine inverts it; vair is interlocking bells.
FURS = ["ermine", "counter-ermine", "vair"]

# Charges are simple silhouettes. Anything with interior detail (a lion's mane,
# a spread eagle's feathers) turns to mud below about 60 dots wide, so the
# renderer drops to this list's simplest members when the target is small.
#
# Themes are a filter over this table, not a separate vocabulary. Heraldry
# already had both registers: castles and swords on one side, and on the other
# a whole celestial cabinet -- the sun in splendour, the estoile with its wavy
# rays, the increscent moon, the comet. Nothing here is invented.
CHARGES = {
    # Neutral shapes, at home in either register.
    "roundel": {"complexity": 1, "themes": {"medieval", "cosmic"}},
    "lozenge": {"complexity": 1, "themes": {"medieval", "cosmic"}},
    "billet": {"complexity": 1, "themes": {"medieval"}},
    "annulet": {"complexity": 1, "themes": {"medieval", "cosmic"}},

    # Medieval.
    "fleur-de-lis": {"complexity": 3, "themes": {"medieval"}},
    "tower": {"complexity": 3, "themes": {"medieval"}},
    "sword": {"complexity": 2, "themes": {"medieval"}},
    "key": {"complexity": 3, "themes": {"medieval"}},
    "crown": {"complexity": 3, "themes": {"medieval"}},
    "portcullis": {"complexity": 3, "themes": {"medieval"}},
    "chalice": {"complexity": 3, "themes": {"medieval"}},

    # Cosmic.
    "mullet": {"complexity": 1, "themes": {"cosmic", "medieval"}},
    "crescent": {"complexity": 2, "themes": {"cosmic", "medieval"}},
    "sun in splendour": {"complexity": 2, "themes": {"cosmic"}},
    "estoile": {"complexity": 2, "themes": {"cosmic"}},
    "comet": {"complexity": 3, "themes": {"cosmic"}},
    "increscent": {"complexity": 2, "themes": {"cosmic"}},
    "orb": {"complexity": 3, "themes": {"cosmic"}},
}

THEMES = ("medieval", "cosmic")


class Blazon:
    """A generated coat of arms, in both formal and drawable form."""

    def __init__(self, rng, theme=None):
        self.rng = rng
        # None means draw from both registers.
        self.theme = theme
        self.field = None
        self.fur = None
        self.variation = None
        self.division = None
        self.field2 = None
        self.ordinary = None
        self.ordinary_tincture = None
        self.charge = None
        self.charge_tincture = None
        self.charge_count = 0
        self.charge_anchor = "centre"

    def _charge_pool(self, max_complexity):
        pool = []
        for name, meta in CHARGES.items():
            if meta["complexity"] > max_complexity:
                continue
            if self.theme and self.theme not in meta["themes"]:
                continue
            pool.append(name)
        return pool

    # -- generation --

    def generate(self, max_complexity=3):
        rng = self.rng
        # Weighted towards a metal field. Flattened to two tones, a colour field
        # becomes a solid black shield that swallows everything on it, so most
        # arms want a light ground -- which is also how most real arms are
        # built, for the same legibility reason at a different distance.
        self.field = (rng.choice(METALS) if rng.random() < 0.62
                      else rng.choice(COLOURS))

        # A variation replaces the flat ground with a repeating two-tincture
        # pattern. It takes nothing else: the pattern alternates metal and
        # colour across the whole shield, so an ordinary or a centred charge has
        # no single tincture beneath it -- the same problem a divided field has,
        # only everywhere at once. Blazoned and drawn, it stands alone.
        # Asking for a theme is asking to see its charges, and a variation takes
        # no charge at all -- so an unthemed roll indulges them freely, while a
        # themed one keeps them rare. Otherwise picking "cosmic" hands you a
        # barry field with nothing cosmic anywhere on it.
        variation_chance = 0.08 if self.theme else 0.26
        if rng.random() < variation_chance:
            self.variation = rng.choice(list(VARIATIONS))
            self.field2 = pick_contrasting(self.field, rng)
            return self

        # A fur is a tincture, not a pattern, so unlike a variation it behaves
        # as a normal ground and can carry an ordinary or a charge. Ermine is
        # counted as a metal for contrast, counter-ermine as a colour, which is
        # how heralds treat them.
        if rng.random() < 0.16:
            self.fur = rng.choice(FURS)
            # The fur *is* the field from here on, so every contrast check
            # downstream compares against it rather than the tincture it
            # replaced.
            self.field = self.fur

        # A divided field is its own visual interest, so it competes with an
        # ordinary. Pick one or the other, mostly, or arms get noisy.
        # Division and ordinary are mutually exclusive here, and that is a
        # correctness constraint rather than taste. The rule of tincture makes a
        # divided field one metal and one colour, so an ordinary laid across it
        # contrasts with exactly one half and vanishes against the other --
        # "per pale purpure and argent, a cross argent" is invisible on its own
        # dexter side. Heraldry's answer is to counterchange the ordinary along
        # the division, which needs finer resolution than a braille cell has.
        # Three ways to build arms, and the third matters: a plain field
        # carrying only charges ("Argent, three mullets gules") is one of the
        # commonest real forms, and it is also the only route to the scattered
        # multi-charge arrangement -- an ordinary crowds it out, and a divided
        # field has no unambiguous ground to scatter across.
        # A themed roll leans towards the arrangements that can actually carry a
        # charge: a bare field, or an ordinary through the centre to sit one on.
        roll = rng.random()
        if roll < (0.14 if self.theme else 0.36):
            self._divide()
        elif roll < (0.50 if self.theme else 0.78):
            self._add_ordinary()
        # else: bare field, charged below.

        # A charge needs one definite tincture beneath it. On a divided field
        # the fess point lands *on* the division line -- per pale and per bend
        # run straight through it, per chevron meets there -- so a charge placed
        # centrally is half on each half, and whichever tincture it contrasts
        # with, it vanishes against the other. Real heraldry answers this by
        # counterchanging the charge, which needs more resolution than a braille
        # cell has. So: charge only where something definite sits underneath.
        # Per fess and per pale leave a whole half in one flat tincture, so a
        # charge can sit there honestly. Per bend and per chevron leave only
        # wedges, which a charge of any size overruns.
        HALVES = {"per fess": "upper", "per pale": "dexter"}
        if self.division:
            self.charge_anchor = HALVES.get(self.division)
        else:
            self.charge_anchor = "centre"

        can_charge = self.charge_anchor is not None and (
            self._ordinary_covers_centre() or self.ordinary is None)
        # With a theme chosen, take every chance to charge; without one, an
        # ordinary is often enough on its own.
        wants_charge = self.ordinary is None or self.theme or rng.random() < 0.4
        if can_charge and wants_charge:
            self._add_charge(max_complexity)
        return self

    def _divide(self):
        rng = self.rng
        self.division = rng.choice(list(DIVISIONS))
        self.field2 = pick_contrasting(self.field, rng)

    # A division and an ordinary of the same geometry restate each other: a
    # chevron laid on a per-chevron field reads as one thick chevron with a
    # seam, not as two charges. Keep them apart.
    ECHOES = {"per pale": "pale", "per fess": "fess",
              "per bend": "bend", "per chevron": "chevron"}

    def _add_ordinary(self):
        rng = self.rng
        pool = list(ORDINARIES)
        echo = self.ECHOES.get(self.division)
        if echo in pool:
            pool.remove(echo)
        self.ordinary = rng.choice(pool)
        # An ordinary sits on the field, so it must contrast with it. On divided
        # arms it crosses both halves; contrast against the first is the
        # convention and keeps at least one edge readable.
        self.ordinary_tincture = pick_contrasting(self.field, rng)

    def _add_charge(self, max_complexity):
        rng = self.rng
        pool = self._charge_pool(max_complexity)
        if not pool:
            return
        self.charge = rng.choice(pool)
        # Contrast has to be judged against what is actually beneath the charge,
        # which is not the same as "the ordinary, if any". A chief sits at the
        # top of the shield while the charge sits at the fess point, so a charge
        # coloured against the chief lands metal-on-metal in the field and
        # disappears. Ask what covers the centre instead.
        # For both divided anchors the half in question is the base field, since
        # the second tincture is painted over it as a polygon.
        under = self.ordinary_tincture if self._ordinary_covers_centre() else self.field
        self.charge_tincture = pick_contrasting(under, rng)
        if self._ordinary_covers_centre() or self.charge_anchor != "centre":
            self.charge_count = 1
        else:
            self.charge_count = rng.choice([1, 1, 1, 3])

    def _ordinary_covers_centre(self):
        """True when the ordinary passes through the fess point."""
        return self.ordinary in ("fess", "pale", "cross", "bend", "saltire", "chevron")

    # -- description --

    def describe(self):
        """The blazon proper, in something close to heraldic word order."""
        parts = []
        if self.variation:
            # Blazon counts the pieces: "Barry of six or and azure".
            n = {6: "six", 5: "five", 8: "eight"}.get(
                VARIATIONS[self.variation]["count"], "")
            of = " of %s" % n if n and self.variation not in ("gyronny",) else ""
            if self.variation == "gyronny":
                of = " of eight"
            parts.append("%s%s %s and %s" % (self.variation.capitalize(), of,
                                             self.field, self.field2))
        elif self.division:
            parts.append("%s %s and %s" % (self.division.capitalize(),
                                           self.field, self.field2))
        else:
            parts.append(self.field.capitalize())

        if self.ordinary:
            article = "a" if self.ordinary != "chief" else "a"
            parts.append("%s %s %s" % (article, self.ordinary, self.ordinary_tincture))

        if self.charge:
            if self.charge_count == 1:
                article = "an" if self.charge[0] in "aeiou" else "a"
                parts.append("%s %s %s" % (article, self.charge,
                                           self.charge_tincture))
            else:
                # Blazon spells its numbers; "3 mullets" is a stock list, not
                # a description of arms.
                words = {2: "two", 3: "three", 4: "four", 5: "five"}
                parts.append("%s %s %s" % (words.get(self.charge_count,
                                                     str(self.charge_count)),
                                           self._plural(self.charge),
                                           self.charge_tincture))
        return ", ".join(parts)

    @staticmethod
    def _plural(charge):
        if charge == "fleur-de-lis":
            return "fleurs-de-lis"
        return charge + "s"
