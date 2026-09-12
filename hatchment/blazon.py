"""Generate a random coat of arms: a blazon, and the SVG that depicts it.

Heraldry is a constraint system, not a pile of random shapes, so the generator
works the way a herald does: pick a field, divide it or not, lay an ordinary
over it, then charge it -- checking the rule of tincture at each step.

Everything renders monochrome. Tinctures become Petra Sancta hatching (vertical
lines for gules, horizontal for azure, dots for or), which is how engravers have
encoded colour in one ink since the 1630s. It is also, conveniently, the only
thing a braille cell can say.

Copyright (C) 2026 Caden DeNike. Free software under the GNU General
Public License, version 3 or later, with no warranty. See LICENSE.
"""

import random
import re

from . import charges, lines, patterns, scenes, variants

# --- Tinctures -------------------------------------------------------------

# Heraldry splits tinctures into metals and colours. The rule of tincture says
# never put metal on metal or colour on colour, which is what keeps arms legible
# at a distance -- exactly the property we need at 40 dots across.
METALS = ["or", "argent"]
COLOURS = ["gules", "azure", "sable", "vert", "purpure"]

# The stains: three further tinctures, later and rarer than the core five but
# perfectly real, and each one multiplies every choice ever made against a
# colour -- field, ordinary, charge, bordure and the second half of a division.
# Held to a minority of colour rolls rather than pooled with the others,
# because arms where a stain is as likely as gules stop reading as heraldry.
STAINS = ["murrey", "sanguine", "tenné"]
STAIN_CHANCE = 0.22

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
    # The stains are hatched as combinations, which is the convention's own
    # answer to running out of single directions. Which combination belongs to
    # which stain is not agreed between sources; these are distinct from each
    # other and from the five above, which is what the convention is for.
    "murrey": {"kind": "bend-sinister-vertical", "density": 0.52},
    "sanguine": {"kind": "lattice", "density": 0.52},
    "tenné": {"kind": "bend-sinister-horizontal", "density": 0.52},
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




def pick_colour(rng):
    """A colour, and now and then a stain."""
    if rng.random() < STAIN_CHANCE:
        return rng.choice(STAINS)
    return rng.choice(COLOURS)


def pick_contrasting(against, rng):
    if is_metal(against):
        return pick_colour(rng)
    return rng.choice(METALS)


def on_pattern(field, pattern, rng):
    """A tincture for a charge laid over a pattern.

    Unlike the field it is edged with, and unlike the pattern it crosses, so
    it reads as a third thing rather than as more of either.
    """
    pool = COLOURS if is_metal(field) else METALS + ["ermine"][:0]
    options = [t for t in pool if t not in (field, pattern)]
    return rng.choice(options or pool)


# --- Vocabulary ------------------------------------------------------------

# Divisions of the field. Each is a pair of half-field polygons in a 0..100 box.
DIVISIONS = ("per pale", "per fess", "per bend", "per bend sinister",
             "per chevron", "quarterly", "per saltire")

# Ordinaries: the bold geometric charges. These are what actually read at low
# resolution, so the generator leans on them heavily.
ORDINARIES = ["cross", "fess", "pale", "bend", "chevron", "saltire", "chief",
              "bordure", "canton", "pile", "orle", "pall", "gyron",
              "bend sinister", "fess double", "pale double"]

# Only these are drawn as a band with two long edges, so only these can carry a
# line of partition. A cross or saltire would need every arm treated, which is
# more geometry than it is worth at this size.
BANDED = ("fess", "pale", "bend", "bend sinister", "chief")

# Variations of the field: a repeating two-tincture pattern instead of a flat
# ground. These are the best thing in the whole vocabulary for this target --
# they are already two-tone by definition, so nothing is lost flattening them,
# and the repeat gives texture that hatching could never survive at this size.
# `counts` is how many pieces the field is divided into, rolled per shield: a
# barry of six and a barry of ten are different arms, and heraldry says so in
# the blazon. `blazoned` marks the ones where it says so -- checky and lozengy
# are named without a count in ordinary usage, so their count varies the
# drawing without pretending the words changed.
VARIATIONS = {
    "barry": {"counts": (6, 8, 10), "blazoned": True},       # horizontal bars
    "paly": {"counts": (6, 8), "blazoned": True},            # vertical pales
    "bendy": {"counts": (6, 8, 10), "blazoned": True},       # diagonal bends
    "checky": {"counts": (6, 8), "blazoned": False},         # checkerboard
    "lozengy": {"counts": (5, 7), "blazoned": False},        # diamonds
    "gyronny": {"counts": (8, 12), "blazoned": True},        # radiating wedges
    "chevronny": {"counts": (5, 6, 8), "blazoned": True},    # stacked chevrons
}

# Furs are the third class of tincture, alongside metals and colours, and they
# are the most medieval thing on a shield. Ermine is a white field strewn with
# black tails; counter-ermine inverts it; vair is interlocking bells.
FURS = ["ermine", "counter-ermine", "vair"]

# Semé: a field strewn with small charges, repeated to the edges and cut off by
# them. One line of vocabulary that multiplies by the whole charge list, and the
# commonest thing in real heraldry that this generator was missing.
LEGACY_SEME = ["mullet", "roundel", "lozenge", "billet", "crescent",
               "fleur-de-lis", "annulet", "trefoil", "estoile", "bee",
               "rose", "garb", "increscent", "orb"]
SEME_CHARGES = LEGACY_SEME + [n for n, m in charges.META.items() if m[5]]

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
    "banner": {"complexity": 3, "themes": {"medieval"}},

    # Natural. Heraldry's own countryside: the garb is a wheatsheaf, the
    # attires a pair of antlers borne without the stag, the rose flat and
    # five-fold rather than a garden rose in profile.
    "garb": {"complexity": 3, "themes": {"natural", "medieval"}},
    "tree": {"complexity": 3, "themes": {"natural"}},
    "rose": {"complexity": 3, "themes": {"natural", "medieval"}},
    "trefoil": {"complexity": 2, "themes": {"natural"}},
    "attires": {"complexity": 3, "themes": {"natural", "medieval"}},
    "stag": {"complexity": 4, "themes": {"natural"}},
    "bee": {"complexity": 4, "themes": {"natural"}},
    "fish": {"complexity": 3, "themes": {"natural"}},
    "lion": {"complexity": 4, "themes": {"medieval", "natural"}},
    "horse": {"complexity": 4, "themes": {"medieval", "natural"}},
    "eagle": {"complexity": 4, "themes": {"medieval", "cosmic", "natural"}},

    # Cosmic.
    "mullet": {"complexity": 1, "themes": {"cosmic", "medieval"}},
    "crescent": {"complexity": 2, "themes": {"cosmic", "medieval"}},
    "sun in splendour": {"complexity": 2, "themes": {"cosmic"}},
    "estoile": {"complexity": 2, "themes": {"cosmic"}},
    "comet": {"complexity": 3, "themes": {"cosmic"}},
    "increscent": {"complexity": 2, "themes": {"cosmic"}},
    "orb": {"complexity": 3, "themes": {"cosmic"}},
}

# The 0.1.8 charges: beasts, birds, the mythic, objects and symbols, drawn in
# hatchment.charges. Marked with the vocabulary they arrived in, so a seed from
# before them still rolls from the table it was rolled from.
for _name, _meta in charges.META.items():
    CHARGES[_name] = {"complexity": _meta[0], "themes": set(_meta[1]),
                      "since": charges.SINCE.get(_name, 1)}

# Fractal and geometric are not heraldry and do not pretend to be: they treat
# the shield as a frame for a pattern rather than as arms.
# Combined themes: a pattern for the field with a charge laid over it,
# fimbriated in the field's tincture so it stays clear of the pattern. Each
# pairs registers that suit each other -- sky over geometry, small living
# things over the airier fractals, symbols over sacred geometry.
COMBOS = {
    "celestial": {
        "patterns": ("concentric rings", "sunburst", "compass spokes",
                     "star polygon", "moire rings", "nested polygons"),
        "charges": ("sun in splendour", "crescent", "increscent", "mullet",
                    "estoile", "comet", "ringed planet", "compass rose",
                    "spiral galaxy", "constellation", "eye", "orb")},
    "enchanted": {
        "patterns": ("flower of life", "recursive circles", "mandala",
                     "koch snowflake", "sierpinski carpet", "hexaflake",
                     "apollonian gasket", "pentaflake", "branching tree"),
        "charges": ("butterfly", "bee", "owl", "stag", "unicorn", "dragon",
                    "phoenix", "rose", "tree", "fish", "swan", "hare",
                    "oak leaf", "acorn", "trefoil")},
    "mystic": {
        "patterns": ("mandala", "flower of life", "recursive circles",
                     "star polygon", "nested polygons", "triangular tessellation",
                     "sierpinski gasket", "hexagonal grid"),
        "charges": ("eye", "triskele", "ankh", "yin-yang", "bowen knot",
                    "crescent", "sun in splendour", "mullet", "estoile", "key",
                    "chalice", "skull", "flame", "hand", "heart")},
    # From 0.1.12: each with its own palette, (field, pattern) pairs, so the
    # themes read as different places rather than as one look recoloured.
    "oceanic": {
        "since": 4,
        "patterns": ("moire rings", "concentric rings", "apollonian gasket",
                     "recursive circles", "gosper curve", "levy curve"),
        "charges": ("fish", "dolphin", "crab", "escallop", "anchor", "lymphad",
                    "serpent", "swan", "tortoise", "compass rose"),
        "fields": (("azure", "argent"), ("argent", "azure"), ("vert", "argent"))},
    "regal": {
        "since": 4,
        "patterns": ("diagonal lattice", "square grid", "star polygon",
                     "nested squares", "triangular tessellation", "vicsek fractal"),
        "charges": ("lion", "eagle", "fleur-de-lis", "crown", "key", "sword",
                    "tower", "orb", "chalice", "unicorn", "griffin", "horse"),
        "fields": (("purpure", "or"), ("gules", "or"), ("or", "purpure"))},
    "wilderness": {
        "since": 4,
        "patterns": ("branching tree", "pythagoras tree", "koch snowflake",
                     "levy curve", "sierpinski gasket", "dragon curve"),
        "charges": ("wolf", "bear", "boar", "stag", "bull", "ram", "fox", "hare",
                    "eagle", "hound", "raven", "owl"),
        # Two pairs, not three: a green field under a gold pattern inks at
        # 0.79 against a 0.52 ceiling, so the legibility gate turned it away
        # every time it was rolled. A palette should list what can be drawn.
        "fields": (("argent", "vert"), ("or", "vert"))},
    "infernal": {
        "since": 4,
        "patterns": ("sunburst", "dragon curve", "star polygon",
                     "sierpinski gasket", "compass spokes", "triangular tessellation"),
        "charges": ("dragon", "phoenix", "skull", "flame", "serpent",
                    "thunderbolt", "bat", "scorpion", "raven"),
        "fields": (("gules", "or"), ("sable", "or"), ("or", "gules"))},
    "nocturnal": {
        "since": 4,
        "patterns": ("concentric rings", "moire rings", "hilbert curve",
                     "sierpinski carpet", "star polygon", "recursive circles"),
        "charges": ("owl", "bat", "crescent", "raven", "wolf", "mullet",
                    "constellation", "estoile", "eye", "spider"),
        "fields": (("azure", "argent"), ("sable", "argent"), ("sable", "or"))},
    "botanical": {
        "since": 4,
        "patterns": ("flower of life", "pentaflake", "hexaflake", "branching tree",
                     "pythagoras tree", "mandala"),
        "charges": ("rose", "trefoil", "thistle", "oak leaf", "acorn",
                    "bunch of grapes", "tree", "garb", "fleur-de-lis", "bee",
                    "butterfly"),
        "fields": (("argent", "vert"), ("gules", "argent"),
                   ("purpure", "or"))},
    "martial": {
        "since": 4,
        "patterns": ("compass spokes", "sunburst", "cantor bars", "nested squares",
                     "t-square", "diagonal lattice"),
        "charges": ("sword", "axe", "hammer", "arrow", "helm", "anvil", "tower",
                    "banner", "horse", "lion", "bugle horn"),
        "fields": (("gules", "argent"), ("argent", "sable"), ("sable", "or"))},
    "alchemical": {
        "since": 4,
        "patterns": ("gosper curve", "hilbert curve", "h-tree", "square grid",
                     "nested polygons", "vicsek fractal", "star polygon"),
        "charges": ("hourglass", "scales", "key", "wheel", "compass rose", "orb",
                    "book", "bell", "eye", "sun in splendour", "crescent", "chalice",
                    "flame"),
        "fields": (("sable", "or"), ("or", "sable"), ("azure", "or"))},
}

THEMES = ("alchemical", "botanical", "celestial", "cosmic", "enchanted",
          "fractal", "geometric", "infernal", "martial", "medieval", "mystic",
          "mythic", "natural", "nocturnal", "oceanic", "regal", "wilderness")
LEGACY_THEMES = ("cosmic", "fractal", "geometric", "medieval", "natural")

# Spelled out, because a blazon counts in words: "Barry of ten", never "of 10".
NUMBER_WORD = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
               7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
               12: "twelve", 16: "sixteen", 20: "twenty", 24: "twenty-four"}

# A few charges are grammatically plural already, so the singular article has to
# be attached to something else: a stag has attires, never "an attires".
BLAZON_NAME = {"attires": "pair of attires", "scales": "pair of scales"}

# What "All" rolls through. Every theme, plus "free": unfiltered heraldry, which
# is what no theme used to mean on its own. Free is kept as its own mode rather
# than dropped, because a theme suppresses variations and furs to make room for
# its charges -- without it, barry and checky and ermine would nearly vanish
# from the one setting that is supposed to show everything.
# What "All" rolls through, by vocabulary: the combined themes join only for
# seeds made from 0.1.11 on, so every earlier seed picks the mode it did.
LEGACY_MODES = LEGACY_THEMES + ("free",)
MODES_1 = ("cosmic", "fractal", "geometric", "medieval", "mythic", "natural",
           "free")
MODES_3 = ("celestial", "cosmic", "enchanted", "fractal", "geometric",
           "medieval", "mystic", "mythic", "natural", "free")
ALL_MODES = THEMES + ("free",)

# Seeds carry the vocabulary they were made in, by their length. Randomise
# made sixteen hex digits before 0.1.8 and eighteen in 0.1.8; each rolls
# against the vocabulary of its time and comes out as the arms it always was.
# Anything else -- a twenty-digit seed from now on, or a word -- gets
# everything, poses and forms included.
_LEGACY_SEED = re.compile(r"[0-9a-f]{16}")
_SEED_0_1_8 = re.compile(r"[0-9a-f]{18}")
_SEED_0_1_9 = re.compile(r"[0-9a-f]{20}")
_SEED_0_1_11 = re.compile(r"[0-9a-f]{22}")


def vocabulary_for(seed, theme=None):
    """0, 1 or 2: the vocabulary a seed was rolled in.

    0 is the charges before 0.1.8; 1 adds the 0.1.8 charges; 2 adds the poses
    and forms of hatchment.variants. A mythic theme takes at least 1, since no
    earlier seed ever had it.
    """
    seed = seed or ""
    if _LEGACY_SEED.fullmatch(seed):
        vocab = 0
    elif _SEED_0_1_8.fullmatch(seed):
        vocab = 1
    elif _SEED_0_1_9.fullmatch(seed):
        vocab = 2
    elif _SEED_0_1_11.fullmatch(seed):
        vocab = 3
    else:
        vocab = 4
    if theme == "mythic":
        vocab = max(vocab, 1)
    if theme in COMBOS:
        vocab = max(vocab, COMBOS[theme].get("since", 3))
    return vocab


def new_seed():
    """A fresh seed: twenty-four hex digits, the shape of the current vocabulary."""
    import os
    return os.urandom(12).hex()


class Blazon:
    """A generated coat of arms, in both formal and drawable form."""

    def __init__(self, rng, theme=None, vocab=1):
        self.rng = rng
        self.vocab = vocab
        # None means draw from both registers.
        self.theme = theme
        self.field = None
        self.fur = None
        self.variation = None
        self.variation_count = 0
        self.division = None
        self.field2 = None
        self.ordinary = None
        self.ordinary_tincture = None
        self.charge = None
        self.charge_tincture = None
        self.charge_count = 0
        self.charge_variant = None
        self.charge_anchor = "centre"
        # A setting, when a description asks for one (see hatchment.scenes).
        # The generator never rolls one, so no seed's arms gain a landscape.
        self.base_style = None
        self.base_tincture = None
        self.base_tincture2 = None
        self.base_row = None
        self.base_row_variant = None
        self.base_row_count = 0
        self.base_row_tincture = None
        self.companion = None
        self.companion_variant = None
        self.companion_count = 0
        self.companion_tincture = None
        self.line_style = "plain"
        self.pattern = None
        self.pattern_seed = 0
        self.seme = None
        self.bordure = None

    def _charge_pool(self, max_complexity):
        pool = []
        for name, meta in CHARGES.items():
            if meta["complexity"] > max_complexity:
                continue
            if meta.get("since", 0) > self.vocab:
                continue
            if self.theme and self.theme not in meta["themes"]:
                continue
            pool.append(name)
        return pool

    # -- generation --

    def generate(self, max_complexity=3):
        rng = self.rng

        # "All" means every theme's options, not the absence of one. Picking a
        # mode per roll is what puts fractals and geometrics in the mix at all:
        # those are gated on the theme name, so an unfiltered roll could never
        # reach them however long it ran.
        if self.theme is None:
            mode = rng.choice(ALL_MODES if self.vocab >= 4 else
                              MODES_3 if self.vocab >= 3 else
                              MODES_1 if self.vocab else LEGACY_MODES)
            self.theme = None if mode == "free" else mode
        # Weighted towards a metal field. Flattened to two tones, a colour field
        # becomes a solid black shield that swallows everything on it, so most
        # arms want a light ground -- which is also how most real arms are
        # built, for the same legibility reason at a different distance.
        roll_f = rng.random()
        if roll_f < 0.10:
            # A fur field, chosen up front rather than as an afterthought.
            self.field = self.fur = rng.choice(FURS)
        elif roll_f < 0.62:
            self.field = rng.choice(METALS)
        else:
            self.field = pick_colour(rng)

        if self.theme in COMBOS:
            return self._combo(max_complexity)

        # The pattern themes replace everything: the shield becomes a frame,
        # and an ordinary or a charge over a fractal is just noise on noise.
        if self.theme in ("fractal", "geometric"):
            pool = (patterns.FRACTAL if self.theme == "fractal"
                    else patterns.GEOMETRIC)
            # Families added later join the pool only for seeds of their time,
            # so an older seed still picks from the pool it was rolled against.
            self.pattern = rng.choice(sorted(
                name for name in pool if patterns.SINCE.get(name, 0) <= self.vocab))
            # The generators randomise their own depth, count and rotation, so
            # the choice has to be pinned here rather than re-rolled at draw
            # time: the same arms are rendered at three different widths, and
            # they must come out the same picture each time.
            self.pattern_seed = rng.getrandbits(32)
            self.field2 = pick_contrasting(self.field, rng)
            return self

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
            self.variation_count = rng.choice(VARIATIONS[self.variation]["counts"])
            self.field2 = pick_contrasting(self.field, rng)
            return self

        # A fur is a tincture, not a pattern, so unlike a variation it behaves
        # as a normal ground and can carry an ordinary or a charge. Ermine is
        # counted as a metal for contrast, counter-ermine as a colour, which is
        # how heralds treat them.

        # A divided field is its own visual interest, so it competes with an
        # ordinary. Pick one or the other, mostly, or arms get noisy.
        # Division and ordinary are mutually exclusive here, and that is a
        # correctness constraint rather than taste. The rule of tincture makes a
        # divided field one metal and one colour, so an ordinary laid across it
        # contrasts with exactly one half and vanishes against the other --
        # "per pale purpure and argent, a cross argent" is invisible on its own
        # dexter side. Heraldry's answer is to counterchange the ordinary along
        # the division, which needs finer resolution than a braille cell has.
        # Semé replaces the plain ground with a strewn one. It still counts as
        # a single tincture underneath for contrast, because the strewn charges
        # are small and sparse enough that an ordinary over them still reads.
        if rng.random() < 0.14:
            # Semé needs a light ground. Flattened to two tones a colour field
            # is solid black, and the strewn charges become white holes in it --
            # legible in principle, over the gate's ink ceiling in practice, so
            # it would be rolled and thrown away every time.
            if not is_metal(self.field):
                self.field = rng.choice(METALS)
                self.fur = None
            self.seme = rng.choice(SEME_CHARGES if self.vocab else LEGACY_SEME)
            self.field2 = pick_contrasting(self.field, rng)

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

        # A bordure sits round the rim and touches nothing else, so unlike every
        # other addition here it can go on top of whatever was just built --
        # which is exactly why real heraldry uses it to difference arms.
        # ...unless the ordinary already is one. Rolling a bordure onto arms
        # that have one blazons "a bordure sable, a bordure tenné" and draws
        # two rims, one inside the other.
        if (rng.random() < 0.20 and not self.pattern
                and self.ordinary != "bordure"):
            self.bordure = pick_contrasting(self.field, rng)

        can_charge = self.charge_anchor is not None and (
            self._ordinary_covers_centre() or self.ordinary is None)
        # With a theme chosen, take every chance to charge; without one, an
        # ordinary is often enough on its own.
        wants_charge = self.ordinary is None or self.theme or rng.random() < 0.4
        if can_charge and wants_charge:
            self._add_charge(max_complexity)
        return self

    def _combo(self, max_complexity):
        """A pattern field with one charge over it, fimbriated to stay clear."""
        rng = self.rng
        spec = COMBOS[self.theme]
        self.pattern = rng.choice(sorted(spec["patterns"]))
        self.pattern_seed = rng.getrandbits(32)
        if spec.get("fields"):
            self.field, self.field2 = rng.choice(spec["fields"])
            self.fur = None
        else:
            self.field2 = pick_contrasting(self.field, rng)
        pool = [c for c in spec["charges"]
                if CHARGES[c]["complexity"] <= max_complexity]
        if pool:
            self.charge = rng.choice(pool)
            self.charge_tincture = on_pattern(self.field, self.field2, rng)
            self.charge_count = rng.choice([1, 1, 1, 2, 3])
            if self.vocab >= 2:
                self.charge_variant = variants.pick(self.charge, rng)
        return self

    def _divide(self):
        rng = self.rng
        self.division = rng.choice(DIVISIONS)
        self.field2 = pick_contrasting(self.field, rng)
        # A line of partition costs nothing and changes the whole silhouette of
        # the cut, so it is worth rolling often.
        if rng.random() < 0.55:
            self.line_style = rng.choice(lines.POOL)

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
        if self.ordinary in BANDED and rng.random() < 0.55:
            self.line_style = rng.choice(lines.POOL)
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
            self.charge_count = rng.choice([1, 1, 2, 3, 3, 4, 5])
        if self.vocab >= 2:
            self.charge_variant = variants.pick(self.charge, rng)

    # Ordinaries occupying the fess point, so a charge placed there sits on
    # them rather than on the field. "fess double" and "pale double" are two
    # bars with a gap between: the gap is exactly where the charge goes, so they
    # leave the centre free. A bordure, orle, canton and gyron never reach it.
    COVERS_CENTRE = ("fess", "pale", "cross", "bend", "saltire", "chevron",
                     "pall", "pile", "bend sinister")

    def _ordinary_covers_centre(self):
        """True when the ordinary passes through the fess point."""
        return self.ordinary in self.COVERS_CENTRE

    # -- description --

    def _pattern_detail(self):
        """" of five iterations", or nothing if the figure has no such number."""
        detail = patterns.headline(patterns.ALL, self.pattern, self.pattern_seed)
        if not detail:
            return ""
        template, value = detail
        # A template asking for %d wants the figure -- a spacing is a
        # measurement. %s wants the word, because counts are spelled.
        if "%d" in template:
            return " " + template % value
        return " " + template % NUMBER_WORD.get(value, value)

    def describe(self):
        """The blazon proper, in something close to heraldic word order."""
        parts = []
        if self.pattern:
            # Not a blazon -- there is no heraldic term for any of this -- so it
            # is named plainly and the tinctures keep their proper names. The
            # figure does name its own headline parameter, though: two mandalas
            # of different petal counts are not the same picture and should not
            # read as the same words.
            parts.append("%s%s, %s and %s" % (self.pattern.capitalize(),
                                              self._pattern_detail(),
                                              self.field, self.field2))
            if self.charge:
                # Edged in the field's tincture to keep clear of the pattern,
                # which heraldry calls fimbriated.
                parts.append("%s fimbriated %s" % (self._charge_words(), self.field))
            return ", ".join(parts)
        if self.variation:
            # Blazon counts the pieces: "Barry of six or and azure".
            n = NUMBER_WORD.get(self.variation_count, "")
            of = (" of %s" % n) if n and VARIATIONS[self.variation]["blazoned"] else ""
            parts.append("%s%s %s and %s" % (self.variation.capitalize(), of,
                                             self.field, self.field2))
        elif self.division:
            # The line style follows the division and precedes the tinctures:
            # "Per fess wavy argent and gules".
            style = "" if self.line_style == "plain" else " " + self.line_style
            parts.append("%s%s %s and %s" % (self.division.capitalize(), style,
                                             self.field, self.field2))
        elif self.seme:
            # "Azure semé of fleurs-de-lis or" -- the field, then what is strewn
            # across it, then the strewing's tincture.
            parts.append("%s semé of %s %s" % (self.field.capitalize(),
                                               self._plural(self.seme),
                                               self.field2))
        else:
            parts.append(self.field.capitalize())

        if self.ordinary:
            style = ("" if self.line_style == "plain" or
                     self.ordinary not in BANDED else " " + self.line_style)
            parts.append("a %s%s %s" % (self.ordinary, style,
                                        self.ordinary_tincture))

        if self.charge:
            parts.append(self._charge_words())
        parts += scenes.blazon_phrases(self, self._named, NUMBER_WORD)
        if self.bordure:
            # A bordure is blazoned last, after everything it surrounds.
            parts.append("a bordure %s" % self.bordure)
        return ", ".join(parts)

    # Charges that do not take a plain "s". "attires" is already plural, so it
    # is its own plural too.
    PLURALS = {"fleur-de-lis": "fleurs-de-lis", "fish": "fish",
               "attires": "attires", "sun in splendour": "suns in splendour"}
    PLURALS.update({n: m[4] for n, m in charges.META.items() if m[4]})

    def _charge_words(self):
        """"a lion passant or", "three mullets argent"."""
        n = self.charge_count
        word = self._named(self.charge, self.charge_variant, n)
        if n == 1:
            return "%s %s %s" % (charges.article(word), word, self.charge_tincture)
        return "%s %s %s" % (NUMBER_WORD.get(n, str(n)), word, self.charge_tincture)

    def _named(self, charge, variant, count):
        """A charge's name in the blazon, singular or plural, in its form."""
        form = variants.get(charge, variant)
        if count == 1:
            return (form and form[1]) or BLAZON_NAME.get(charge, charge)
        return (form and form[2]) or self._plural(charge)

    @classmethod
    def _plural(cls, charge):
        return cls.PLURALS.get(charge, charge + "s")
