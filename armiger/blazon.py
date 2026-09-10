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


def is_metal(tincture):
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

# Charges are simple silhouettes. Anything with interior detail (a lion's mane,
# a spread eagle's feathers) turns to mud below about 60 dots wide, so the
# renderer drops to this list's simplest members when the target is small.
CHARGES = {
    "mullet": {"complexity": 1},      # five-pointed star
    "roundel": {"complexity": 1},
    "lozenge": {"complexity": 1},
    "crescent": {"complexity": 2},
    "billet": {"complexity": 1},
    "fleur-de-lis": {"complexity": 3},
    "tower": {"complexity": 3},
}


class Blazon:
    """A generated coat of arms, in both formal and drawable form."""

    def __init__(self, rng):
        self.rng = rng
        self.field = None
        self.division = None
        self.field2 = None
        self.ordinary = None
        self.ordinary_tincture = None
        self.charge = None
        self.charge_tincture = None
        self.charge_count = 0
        self.charge_anchor = "centre"

    # -- generation --

    def generate(self, max_complexity=3):
        rng = self.rng
        # Weighted towards a metal field. Flattened to two tones, a colour field
        # becomes a solid black shield that swallows everything on it, so most
        # arms want a light ground -- which is also how most real arms are
        # built, for the same legibility reason at a different distance.
        self.field = (rng.choice(METALS) if rng.random() < 0.62
                      else rng.choice(COLOURS))

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
        roll = rng.random()
        if roll < 0.36:
            self._divide()
        elif roll < 0.78:
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
        if can_charge and (self.ordinary is None or rng.random() < 0.4):
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
        pool = [c for c, m in CHARGES.items() if m["complexity"] <= max_complexity]
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
        if self.division:
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
