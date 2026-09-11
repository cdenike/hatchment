"""Arms from a description: what someone asks for, and a roll for the rest.

A prompt is read against hatchment's own vocabulary, in plain English or in
heraldry's -- "three gold lions on red" and "Gules, three lions or" are the
same arms -- and whatever it names is fixed. What it leaves out is rolled the
way the generator rolls it, so a prompt naming only a lion still gets a field,
a tincture that stands out against it, and legible arms.

It is a reader, not a model: a phrase list and a few rules about which word a
colour belongs to. That keeps it offline, instant and predictable -- the same
words and the same seed always make the same arms -- and it says plainly what
it did not understand rather than guessing at a dragon it cannot draw.
"""

import difflib
import re
from dataclasses import dataclass, field as _default

from . import lines, patterns
from .blazon import (BANDED, FURS, METALS, SEME_CHARGES, VARIATIONS, Blazon,
                     is_metal, pick_colour, pick_contrasting)
from .gloss import EN

# --- vocabulary ----------------------------------------------------------------
#
# Each table maps hatchment's own term to the words someone might use for it.
# The heraldic term is always among them, so a real blazon reads as well as a
# plain description does.

TINCTURE_WORDS = {
    # "or" itself is not listed: it is also the English conjunction, and is
    # read as gold only where a blazon would put it -- see _or_is_tincture.
    "or": ["gold", "golden", "yellow"],
    "argent": ["argent", "silver", "white", "grey", "gray"],
    "gules": ["gules", "red", "scarlet", "crimson", "ruby"],
    "azure": ["azure", "blue", "navy", "sapphire", "sky blue", "pale blue"],
    "vert": ["vert", "green", "emerald"],
    "sable": ["sable", "black"],
    "purpure": ["purpure", "purple", "violet", "lavender", "amethyst"],
    "murrey": ["murrey", "mulberry", "wine", "burgundy", "plum"],
    "sanguine": ["sanguine", "blood red", "blood-red", "dark red", "maroon"],
    "tenné": ["tenné", "tenne", "orange", "tawny", "brown"],
    "ermine": ["ermine"],
    "counter-ermine": ["counter-ermine", "counter ermine", "ermines"],
    "vair": ["vair"],
}

CHARGE_WORDS = {
    "mullet": ["mullet", "star"],
    "estoile": ["estoile", "wavy star"],
    "roundel": ["roundel", "disc", "disk", "ball", "circle"],
    "lozenge": ["lozenge", "diamond"],
    "billet": ["billet", "rectangle", "block", "brick"],
    "annulet": ["annulet", "ring"],
    "fleur-de-lis": ["fleur-de-lis", "fleur de lis", "fleurs-de-lis",
                     "fleurs de lis", "fleur", "lily"],
    "tower": ["tower", "castle", "turret"],
    "sword": ["sword", "blade"],
    "key": ["key"],
    "crown": ["crown", "coronet"],
    "portcullis": ["portcullis", "gate"],
    "chalice": ["chalice", "cup", "goblet", "grail"],
    "banner": ["banner", "flag", "pennant"],
    "garb": ["garb", "wheatsheaf", "sheaf", "wheat"],
    "tree": ["tree", "oak"],
    "rose": ["rose", "flower"],
    "trefoil": ["trefoil", "clover", "shamrock"],
    "attires": ["attires", "antlers", "antler"],
    "stag": ["stag", "deer", "hart"],
    "bee": ["bee"],
    "fish": ["fish"],
    "lion": ["lion", "lioness"],
    "horse": ["horse", "stallion", "steed", "pony"],
    "eagle": ["eagle", "bird", "hawk", "falcon"],
    "crescent": ["crescent", "moon", "crescent moon"],
    "increscent": ["increscent"],
    "sun in splendour": ["sun in splendour", "sun in splendor", "sun"],
    "comet": ["comet"],
    "orb": ["orb", "globe", "planet"],
}

ORDINARY_WORDS = {
    "cross": ["cross"],
    "saltire": ["saltire", "diagonal cross", "x"],
    "fess": ["fess", "fesse", "bar", "band", "stripe", "horizontal band",
             "horizontal stripe",
             "horizontal bar", "band across", "stripe across"],
    "pale": ["pale", "vertical band", "vertical stripe", "vertical bar",
             "band down", "stripe down"],
    "bend": ["bend", "diagonal band", "diagonal stripe", "diagonal bar", "sash"],
    "bend sinister": ["bend sinister", "other diagonal"],
    "chevron": ["chevron", "v shape", "v-shape", "inverted v"],
    "chief": ["chief", "top band", "top stripe", "band across the top",
              "stripe across the top"],
    "orle": ["orle", "inner border"],
    "canton": ["canton", "corner square"],
    "pile": ["pile", "wedge from the top", "downward wedge"],
    "pall": ["pall", "y shape", "y-shape"],
    "gyron": ["gyron", "corner wedge"],
    "fess double": ["fess double", "double fess", "two bars", "twin bars"],
    "pale double": ["pale double", "double pale", "two pales"],
}

# A border goes on as the blazon's bordure, which can sit alongside an
# ordinary, rather than as the ordinary called bordure, which cannot.
BORDER_WORDS = ["bordure", "border", "rim"]

DIVISION_WORDS = {
    "per pale": ["per pale", "split vertically", "halved vertically",
                 "divided vertically", "left and right", "split down the middle"],
    "per fess": ["per fess", "split horizontally", "halved horizontally",
                 "divided horizontally", "top and bottom"],
    "per bend": ["per bend", "split diagonally", "halved diagonally",
                 "divided diagonally"],
    "per bend sinister": ["per bend sinister"],
    "per chevron": ["per chevron"],
    "quarterly": ["quarterly", "quartered", "quarters", "in quarters"],
    "per saltire": ["per saltire"],
}

VARIATION_WORDS = {
    "barry": ["barry", "horizontal stripes", "horizontally striped", "stripes",
              "striped"],
    "paly": ["paly", "vertical stripes", "vertically striped"],
    "bendy": ["bendy", "diagonal stripes", "diagonally striped"],
    "checky": ["checky", "chequy", "checkered", "chequered", "checkerboard",
               "chequerboard", "checks", "checked"],
    "lozengy": ["lozengy", "harlequin", "diamond pattern"],
    "gyronny": ["gyronny", "pinwheel", "wedges"],
    "chevronny": ["chevronny", "zigzag stripes", "stacked chevrons"],
}

LINE_WORDS = {
    "wavy": ["wavy", "wave", "waves", "wavy edge", "wavy line"],
    "engrailed": ["engrailed", "scalloped", "scallops"],
    "indented": ["indented", "zigzag", "zig-zag", "jagged", "sawtooth"],
    "dancetty": ["dancetty", "dancette", "deep zigzag"],
    "embattled": ["embattled", "battlements", "battlemented", "crenellated",
                  "castellated"],
    "nebuly": ["nebuly", "cloudy", "clouds", "cloud"],
}

PATTERN_WORDS = {name: [name] for name in list(patterns.FRACTAL) + list(patterns.GEOMETRIC)}
PATTERN_WORDS["sierpinski gasket"] += ["sierpinski", "sierpinski triangle"]
PATTERN_WORDS["sierpinski carpet"] += ["carpet"]
PATTERN_WORDS["vicsek fractal"] += ["vicsek"]
PATTERN_WORDS["koch snowflake"] += ["koch", "snowflake"]
PATTERN_WORDS["h-tree"] += ["h tree"]
PATTERN_WORDS["cantor bars"] += ["cantor"]
PATTERN_WORDS["concentric rings"] += ["concentric circles", "target"]
PATTERN_WORDS["compass spokes"] += ["spokes", "compass"]
PATTERN_WORDS["triangular tessellation"] += ["triangles", "tessellation"]
PATTERN_WORDS["hexagonal grid"] += ["hexagons", "honeycomb"]
PATTERN_WORDS["star polygon"] += ["pentagram"]
PATTERN_WORDS["diagonal lattice"] += ["lattice"]
PATTERN_WORDS["square grid"] += ["grid"]
PATTERN_WORDS["sunburst"] += ["rays"]
PATTERN_WORDS["moire rings"] += ["moire", "moiré"]

THEME_WORDS = {
    "cosmic": ["cosmic", "space", "celestial", "astral"],
    "fractal": ["fractal"],
    "geometric": ["geometric", "geometry"],
    "medieval": ["medieval", "knightly"],
    "natural": ["natural", "nature"],
}

SEME_WORDS = ["semé of", "seme of", "semé", "seme", "strewn with",
              "scattered with", "powdered with", "sprinkled with",
              "covered in", "covered with", "dotted with"]

FIELD_WORDS = ["field", "background", "ground", "shield", "backdrop"]

NUMBER_WORDS = {1: ["a", "an", "one", "single", "lone"],
                2: ["two", "pair", "couple"], 3: ["three"], 4: ["four"],
                5: ["five"], 6: ["six"], 7: ["seven"], 8: ["eight"],
                9: ["nine"], 10: ["ten"]}

# Words that carry no instruction. Dropped without comment, so that "a big
# fierce lion" is simply a lion rather than a lion and two complaints.
FILLER = {
    "the", "of", "with", "to", "for", "my", "me", "i", "want", "make", "create",
    "give", "please", "some", "coat", "arms", "arm", "that", "is", "are", "be",
    "it", "its", "has", "have", "having", "which", "who", "featuring",
    "features", "showing", "plus", "also", "like", "looking", "style",
    "design", "emblem", "crest", "heraldry", "heraldic", "family", "house",
    "from", "by", "at", "colour", "color", "coloured", "colored", "made",
    "into", "sitting", "standing", "holding", "maybe", "something", "anything",
    "kind", "sort", "just", "very", "really", "each", "all", "both", "bearing",
    "charged", "between", "above", "below", "under", "beneath", "across",
    "down", "middle", "centre", "center", "top", "side", "left", "right",
    "vertically", "horizontally", "diagonally", "split", "divided", "halved",
    "or", "am", "would", "could", "can", "you", "we", "our", "us", "this",
    "big", "small", "large", "little", "tiny", "huge", "giant", "nice",
    "cool", "beautiful", "simple", "bold", "proud", "fierce", "majestic",
    "ancient", "royal", "noble", "rampant", "passant", "displayed", "regal",
    "old", "new", "elegant", "strong", "brave", "mighty", "great", "lot",
    "lots", "many", "several", "one's", "it's", "crossed",
}

# Short names for the charges, for the hint shown when a word is not one.
DRAWABLE = ("lions, eagles, stags, horses, fish, bees, trees, roses, towers, "
            "swords, keys, crowns, stars, moons, suns")

_NOUNS = ("charge", "ordinary", "border", "semeobj", "field", "division",
          "variation", "pattern", "theme")
# Nouns that take two tinctures: a field and its second tincture.
_PAIRED = ("field", "division", "variation", "pattern", "theme")
_PLURAL_KINDS = ("charge", "ordinary", "border", "field")


def _tokens(text):
    text = text.lower().replace("’", "'")
    return re.findall(r"[a-zé]+(?:['-][a-zé]+)*|\d+|[,&]", text)


def _lexicon():
    lex = {}

    def add(kind, table):
        for value, words in table.items():
            for word in words:
                lex.setdefault(tuple(_tokens(word)), (kind, value))

    # Longer and more specific vocabularies first, so a phrase that is in two
    # tables resolves to the one that means more.
    add("pattern", PATTERN_WORDS)
    add("variation", VARIATION_WORDS)
    add("division", DIVISION_WORDS)
    add("ordinary", ORDINARY_WORDS)
    add("border", {"bordure": BORDER_WORDS})
    add("line", LINE_WORDS)
    add("seme", {"seme": SEME_WORDS})
    add("charge", CHARGE_WORDS)
    add("tincture", TINCTURE_WORDS)
    add("theme", THEME_WORDS)
    add("field", {"field": FIELD_WORDS})
    add("number", NUMBER_WORDS)
    add("on", {"on": ["on", "upon", "over", "against", "atop"]})
    add("in", {"in": ["in"]})
    add("and", {"and": ["and"]})
    return lex


LEXICON = _lexicon()
LONGEST = max(len(k) for k in LEXICON)
# Words worth suggesting for a typo: ones that name something. "and" is a
# near miss for "band", and suggesting it would be worse than saying nothing.
VOCABULARY = sorted({" ".join(k) for k, (kind, _) in LEXICON.items()
                     if kind not in ("number", "on", "in", "and")
                     and len(" ".join(k)) > 2})


def _singulars(word):
    out = []
    if word.endswith("ies"):
        out.append(word[:-3] + "y")
    if word.endswith("ves"):
        out.append(word[:-3] + "f")
    if word.endswith("es"):
        out.append(word[:-2])
    if word.endswith("s"):
        out.append(word[:-1])
    return out


def _lookup(words):
    """(kind, value, plural) for a run of words, or None."""
    hit = LEXICON.get(tuple(words))
    if hit:
        return hit + (False,)
    for single in _singulars(words[-1]):
        hit = LEXICON.get(tuple(words[:-1]) + (single,))
        if hit and hit[0] in _PLURAL_KINDS:
            return hit + (True,)
    return None


@dataclass
class _Item:
    kind: str
    value: object
    plural: bool = False
    word: str = ""
    tinctures: list = _default(default_factory=list)


def _or_is_tincture(tokens, i, items):
    """Whether this "or" is gold rather than a conjunction.

    Read as gold only where a blazon puts a tincture: first of all, right after
    the thing it colours ("a lion or"), in a pair after another tincture ("per
    pale argent and or"), or before a comma or the end.
    """
    prev = items[-1].kind if items else None
    nxt = tokens[i + 1] if i + 1 < len(tokens) else None
    return (i == 0 or nxt in (None, ",") or prev in _NOUNS
            or (prev == "and" and len(items) > 1 and items[-2].kind == "tincture"))


def _scan(text):
    tokens = _tokens(text)
    items, unknown = [], []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.isdigit():
            items.append(_Item("number", int(tok), word=tok))
            i += 1
            continue
        if tok in (",", "&"):
            items.append(_Item("and", tok, word=tok))
            i += 1
            continue
        if tok == "or":
            if _or_is_tincture(tokens, i, items):
                items.append(_Item("tincture", "or", word="or"))
            i += 1
            continue
        for size in range(min(LONGEST, len(tokens) - i), 0, -1):
            words = tokens[i:i + size]
            if "," in words or "&" in words:
                continue
            hit = _lookup(words)
            if hit:
                kind, value, plural = hit
                items.append(_Item(kind, value, plural, " ".join(words)))
                i += size
                break
        else:
            if tok not in FILLER and len(tok) > 2:
                unknown.append(tok)
            i += 1
    return items, unknown


def _is_noun(item):
    return (item is not None and item.kind in _NOUNS
            and (item.kind != "theme" or item.value in ("fractal", "geometric")))


def _neighbour(items, index, step):
    """The next item that way, looking past counts ("on a red field")."""
    index += step
    while 0 <= index < len(items) and items[index].kind == "number":
        index += step
    return (index, items[index]) if 0 <= index < len(items) else (index, None)


def _attach_tinctures(items):
    """Give each colour to the thing it describes. Returns (on_field, loose).

    A colour directly before a thing is its adjective ("gold lion"); directly
    after, its blazon ("a lion or", "a lion in gold"); after "on", the ground
    ("on red"). Colours joined by "and" travel together, so "red and white
    stripes" colours both halves. What fits none of those is loose, and is
    placed once the whole description is known.
    """
    on_field, loose = [], []
    i = 0
    while i < len(items):
        if items[i].kind != "tincture":
            i += 1
            continue
        j = i
        while (j + 2 < len(items) and items[j + 1].kind == "and"
               and items[j + 2].kind == "tincture"):
            j += 2
        colours = [items[k].value for k in range(i, j + 1)
                   if items[k].kind == "tincture"]
        nxt = items[j + 1] if j + 1 < len(items) else None
        p, prev = _neighbour(items, i, -1)
        if prev is not None and prev.kind == "in":
            _, prev = _neighbour(items, p, -1)

        target = None
        if _is_noun(nxt) and not nxt.tinctures:
            target = nxt
        elif _is_noun(prev) and not prev.tinctures:
            target = prev
        if target is not None:
            take = 2 if target.kind in _PAIRED else 1
            target.tinctures = colours[:take]
            loose += colours[take:]
        elif prev is not None and prev.kind == "on":
            on_field += colours[:2]
            loose += colours[2:]
        else:
            loose += colours
        i = j + 1
    return on_field, loose


@dataclass
class Wishes:
    """What a description asked for. None means "not said -- roll it"."""

    text: str = ""
    field: str = None
    field2: str = None
    division: str = None
    variation: str = None
    pattern: str = None
    theme: str = None
    ordinary: str = None
    ordinary_t: str = None
    charge: str = None
    charge_t: str = None
    count: int = None
    plural: bool = False
    seme: str = None
    seme_t: str = None
    bordure: bool = False
    bordure_t: str = None
    line: str = None
    loose: list = _default(default_factory=list)
    notes: list = _default(default_factory=list)

    def pattern_mode(self):
        return bool(self.pattern) or self.theme in ("fractal", "geometric")

    def names_shapes(self):
        return self.pattern_mode() or any((
            self.division, self.variation, self.ordinary, self.charge,
            self.seme, self.bordure))


def _plain(tincture):
    return EN["tincture"].get(tincture, tincture)


def parse(text):
    """Read a description into Wishes, with notes on anything not used."""
    w = Wishes(text=text)
    items, unknown = _scan(text)

    # Strewing needs a small charge to strew. A lion "strewn" across the field
    # is taken as the lion it names, drawn once, rather than dropped.
    for index, item in enumerate(items):
        if item.kind != "seme":
            continue
        target = next((it for it in items[index + 1:index + 5]
                       if it.kind == "charge"), None)
        if target is None:
            w.notes.append("strewn with what? Name a small charge, such as stars")
        elif target.value in SEME_CHARGES:
            target.kind = "semeobj"
        else:
            w.notes.append("only small charges can be strewn across a field, "
                           "so the %s became the main charge" % target.word)

    on_field, loose = _attach_tinctures(items)

    def all_of(kind):
        return [it for it in items if it.kind == kind]

    def first(kind):
        found = all_of(kind)
        return found[0] if found else None

    charges = all_of("charge")
    if charges:
        chosen = charges[0]
        w.charge, w.plural = chosen.value, chosen.plural
        w.charge_t = chosen.tinctures[0] if chosen.tinctures else None
        index = items.index(chosen) - 1
        while index >= 0 and items[index].kind in ("tincture", "and"):
            index -= 1
        if index >= 0 and items[index].kind == "number":
            w.count = items[index].value
        others = sorted({c.word for c in charges if c.value != chosen.value})
        if others:
            w.notes.append("one kind of charge fits on these arms; kept the %s, "
                           "left out %s" % (chosen.word, ", ".join("the " + o for o in others)))
    if w.count and w.count > 5:
        w.notes.append("five is the most charges that fit; drew five")
        w.count = 5

    ordinaries = all_of("ordinary")
    if ordinaries:
        w.ordinary = ordinaries[0].value
        w.ordinary_t = (ordinaries[0].tinctures or [None])[0]
        others = sorted({o.word for o in ordinaries if o.value != w.ordinary})
        if others:
            w.notes.append("one ordinary fits; kept the %s, left out %s"
                           % (ordinaries[0].word, ", ".join("the " + o for o in others)))

    border = first("border")
    if border:
        w.bordure = True
        w.bordure_t = (border.tinctures or [None])[0]
    seme = first("semeobj")
    if seme:
        w.seme, w.seme_t = seme.value, (seme.tinctures or [None])[0]

    for kind in ("division", "variation", "pattern", "theme", "line"):
        item = first(kind)
        if item:
            setattr(w, kind, item.value)
    if w.division and w.variation:
        w.notes.append("stripes and a division both fill the field; "
                       "kept the %s" % first("variation").word)
        w.division = None
    if w.pattern and w.pattern in patterns.FRACTAL:
        w.theme = "fractal"
    elif w.pattern:
        w.theme = "geometric"

    # The field's own pair: said of the field itself, of a division or
    # pattern, or after "on".
    pair = []
    for kind in ("field", "division", "variation", "pattern", "theme"):
        for item in all_of(kind):
            pair += item.tinctures
    pair += on_field
    if pair:
        w.field = pair[0]
    if len(pair) > 1:
        w.field2 = pair[1]
    loose = pair[2:] + loose

    if w.pattern_mode():
        dropped = [name for name, on in (
            ("the " + (first("charge").word if charges else ""), w.charge),
            ("the " + (ordinaries[0].word if ordinaries else ""), w.ordinary),
            ("the division", w.division), ("the stripes", w.variation),
            ("the strewing", w.seme), ("the border", w.bordure)) if on]
        if dropped:
            w.notes.append("a pattern fills the whole shield, so %s %s left off"
                           % (", ".join(dropped),
                              "was" if len(dropped) == 1 else "were"))
    elif w.charge and w.division in ("per bend", "per bend sinister",
                                     "per chevron", "quarterly", "per saltire"):
        w.notes.append("a charge on a field cut %s sits across the line, so it "
                       "may not stand out" % w.division)

    if w.line and w.names_shapes() and not _cut(w.division, w.ordinary):
        if w.division:
            w.notes.append("quartered and saltire cuts are drawn straight, so "
                           "the %s edge was left off" % w.line)
        else:
            w.notes.append("a %s edge needs a division or a band to run along"
                           % w.line)

    # Colours with no owner go where a description most likely meant them:
    # the field first, then whatever else was named without a colour.
    if w.names_shapes():
        if w.field2 and not (w.division or w.variation or w.pattern_mode()):
            loose.insert(0, w.field2)
            w.field2 = None
        for attr, wanted in (("field", True),
                             ("field2", bool(w.division or w.variation or w.pattern_mode())),
                             ("charge_t", bool(w.charge)),
                             ("ordinary_t", bool(w.ordinary)),
                             ("bordure_t", w.bordure),
                             ("seme_t", bool(w.seme))):
            if loose and wanted and getattr(w, attr) is None:
                setattr(w, attr, loose.pop(0))
        for spare in loose:
            w.notes.append("no place left for %s" % _plain(spare))
    else:
        w.loose = ([w.field] if w.field else []) + ([w.field2] if w.field2 else []) + loose
        w.field = w.field2 = None

    _clash_notes(w)

    if unknown:
        shown = []
        for word in unknown[:3]:
            close = difflib.get_close_matches(word, VOCABULARY, n=1, cutoff=0.72)
            shown.append("“%s”%s" % (word, " (did you mean %s?)" % close[0]
                                             if close else ""))
        more = len(unknown) - len(shown)
        w.notes.append("not in hatchment's vocabulary: %s%s"
                       % (", ".join(shown), " and %d more" % more if more else ""))
        if not w.charge and not w.pattern_mode():
            w.notes.append("charges it can draw include " + DRAWABLE)
    return w


def _clash_notes(w):
    """Say where two colours someone chose break the rule of tincture.

    Honoured anyway -- they asked for it -- but worth knowing: a colour export
    shows both, and the terminal's two tones turn a colour on a colour into one
    shape.
    """
    covers = w.ordinary in Blazon.COVERS_CENTRE
    pairs = [(w.charge_t, w.ordinary_t if covers else w.field),
             (w.ordinary_t, w.field), (w.bordure_t, w.field),
             (w.seme_t, w.field)]
    if w.division or w.variation:
        pairs.append((w.field2, w.field))
    for top, under in pairs:
        if (top and under and top != under and top not in FURS
                and under not in FURS and is_metal(top) == is_metal(under)):
            kind = "metal" if is_metal(top) else "colour"
            w.notes.append("%s on %s is %s on %s: fine in a colour export, but "
                           "the two merge in the terminal's two tones"
                           % (_plain(top), _plain(under), kind, kind))


# --- composing ------------------------------------------------------------------

HALVES = {"per fess": "upper", "per pale": "dexter"}

# Divisions the renderer draws with a styled edge. Quarterly and per saltire are
# drawn straight whatever their line says, so an edge rolled or asked for there
# would put words in the blazon that the picture does not show.
DRAWN_EDGES = ("per pale", "per fess", "per bend", "per bend sinister",
               "per chevron")


def _cut(division, ordinary):
    """True when these arms have an edge the renderer can draw a line along."""
    return division in DRAWN_EDGES or ordinary in BANDED


def _ground(tinctures, rng):
    """A field for arms whose field was not said.

    The field carries everything else, so it contrasts with the first thing
    that was coloured. With nothing coloured, it is weighted towards a metal
    the way the generator's is, for the same legibility reason.
    """
    for t in tinctures:
        if t:
            return pick_contrasting(t, rng)
    if rng.random() < 0.62:
        return rng.choice(METALS)
    return pick_colour(rng)


def compose(w, rng, theme=None, max_complexity=3):
    """Build arms from Wishes, rolling whatever they leave open."""
    theme = w.theme or theme
    b = Blazon(rng, theme=theme)

    # Nothing shaped was named -- colours, a theme, or nothing usable at all --
    # so the generator picks the shapes and the colours go on afterwards.
    if not w.names_shapes():
        b.generate(max_complexity=max_complexity)
        _recolour(b, w, rng)
        return b

    if w.pattern_mode():
        pool = patterns.FRACTAL if theme == "fractal" else patterns.GEOMETRIC
        b.theme = theme
        b.pattern = w.pattern or rng.choice(sorted(pool))
        b.pattern_seed = rng.getrandbits(32)
        b.field = w.field or _ground([w.field2], rng)
        b.field2 = w.field2 or pick_contrasting(b.field, rng)
        return b

    covers = w.ordinary in Blazon.COVERS_CENTRE
    # A charge on an ordinary through the centre sits on the ordinary, so the
    # ordinary contrasts with the charge and the field with the ordinary --
    # worked out in that order, or a gold lion lands on a gold cross.
    ordinary_t = w.ordinary_t
    if w.ordinary and covers and w.charge_t and not ordinary_t:
        ordinary_t = pick_contrasting(w.charge_t, rng)
    b.field = w.field or _ground(
        [ordinary_t, None if covers else w.charge_t, w.seme_t, w.field2,
         w.bordure_t], rng)
    if b.field in FURS:
        b.fur = b.field

    if w.variation:
        b.variation = w.variation
        b.variation_count = rng.choice(VARIATIONS[w.variation]["counts"])
        b.field2 = w.field2 or pick_contrasting(b.field, rng)
    elif w.division:
        b.division = w.division
        b.field2 = w.field2 or pick_contrasting(b.field, rng)
    if w.seme:
        b.seme = w.seme
        if not (b.division or b.variation):
            b.field2 = w.seme_t or pick_contrasting(b.field, rng)

    if w.ordinary:
        b.ordinary = w.ordinary
        b.ordinary_tincture = ordinary_t or pick_contrasting(b.field, rng)

    cut = _cut(b.division, b.ordinary)
    if cut and w.line:
        b.line_style = w.line
    elif cut and rng.random() < 0.55:
        b.line_style = rng.choice(lines.POOL)

    if w.charge:
        b.charge = w.charge
        b.charge_anchor = HALVES.get(b.division, "centre")
        under = b.ordinary_tincture if covers else b.field
        b.charge_tincture = w.charge_t or pick_contrasting(under, rng)
        if w.count:
            b.charge_count = w.count
        elif w.plural:
            b.charge_count = rng.choice([2, 3, 3, 4, 5])
        else:
            b.charge_count = 1

    if w.bordure:
        b.bordure = w.bordure_t or pick_contrasting(b.field, rng)
    return b


def _recolour(b, w, rng):
    """Lay the description's colours over generated arms, keeping them legible.

    Colours go on in the order a reader would expect -- the field, its second
    tincture, then whatever sits on it -- and anything the description did not
    colour is re-picked if the new colours left it clashing.
    """
    slots = ["field"]
    if b.field2:
        slots.append("field2")
    if b.charge:
        slots.append("charge_tincture")
    if b.ordinary:
        slots.append("ordinary_tincture")
    if b.bordure:
        slots.append("bordure")
    pinned = set()
    for slot, colour in zip(slots, w.loose):
        setattr(b, slot, colour)
        pinned.add(slot)
    b.fur = b.field if b.field in FURS else None

    def keep_apart(slot, under):
        value = getattr(b, slot)
        if value and slot not in pinned and is_metal(value) == is_metal(under):
            setattr(b, slot, pick_contrasting(under, rng))

    if not b.seme:
        keep_apart("field2", b.field)
    keep_apart("ordinary_tincture", b.field)
    keep_apart("bordure", b.field)
    under = (b.ordinary_tincture if b._ordinary_covers_centre() else b.field)
    keep_apart("charge_tincture", under)
    if w.line and _cut(b.division, b.ordinary):
        b.line_style = w.line
