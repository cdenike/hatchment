"""Turn a blazon into plain language.

A blazon is a technical description in Norman-French word order -- "Per fess
sable and or, a mullet or" -- and it is genuinely opaque unless you already read
heraldry. This renders the same arms as an ordinary sentence.

The output language follows the user's locale. Only English ships: the glossary
is a table per language, so adding one is data rather than code, but shipping
translations that cannot be checked would be worse than shipping none. See
LANGS at the bottom for what adding a language involves.
"""

import locale
import os

# --- English glossary ------------------------------------------------------

EN = {
    "tincture": {
        "or": "gold",
        "argent": "silver",
        "gules": "red",
        "azure": "blue",
        "sable": "black",
        "vert": "green",
        "purpure": "purple",
        "ermine": "white with black flecks",
        "counter-ermine": "black with white flecks",
        "vair": "blue and white bell pattern",
    },
    # Each division says how the shield is cut, as "<first> <join> <second>".
    "division": {
        "per pale": ("{a} on the left, {b} on the right"),
        "per fess": ("{a} above, {b} below"),
        "per bend": ("{a} and {b}, split diagonally"),
        "per chevron": ("{a} and {b}, split by a chevron"),
    },
    "variation": {
        "barry": "horizontal stripes of {a} and {b}",
        "paly": "vertical stripes of {a} and {b}",
        "bendy": "diagonal stripes of {a} and {b}",
        "checky": "a {a} and {b} chequerboard",
        "lozengy": "{a} and {b} diamonds",
        "gyronny": "{a} and {b} wedges radiating from the centre",
        "chevronny": "nested {a} and {b} chevrons",
    },
    "ordinary": {
        "cross": "a {t} cross",
        "fess": "a {t} band across the middle",
        "pale": "a {t} band down the middle",
        "bend": "a {t} diagonal band",
        "chevron": "a {t} chevron",
        "saltire": "a {t} diagonal cross",
        "chief": "a {t} band across the top",
    },
    # Charges whose heraldic name is already plain enough are left alone.
    "charge": {
        "mullet": "star",
        "roundel": "disc",
        "lozenge": "diamond",
        "billet": "rectangle",
        "annulet": "ring",
        "crescent": "crescent moon",
        "increscent": "crescent moon facing right",
        "estoile": "wavy-rayed star",
        "comet": "comet",
        "orb": "orb",
        "sun in splendour": "sun",
        "fleur-de-lis": "fleur-de-lis",
        "tower": "tower",
        "sword": "sword",
        "key": "key",
        "crown": "crown",
        "portcullis": "portcullis",
        "chalice": "cup",
        "banner": "banner",
        "lion": "rearing lion",
        "horse": "rearing horse",
        "eagle": "eagle with spread wings",
        "garb": "wheatsheaf",
        "tree": "tree",
        "rose": "rose",
        "trefoil": "clover leaf",
        "attires": "pair of antlers",
        "stag": "stag",
        "bee": "bee",
        "fish": "fish",
    },
    # Lines of partition, as the shape of the edge rather than its name.
    "line": {
        "wavy": "a wavy edge",
        "engrailed": "a scalloped edge",
        "invected": "a scalloped edge",
        "indented": "a zigzag edge",
        "dancetty": "a deep zigzag edge",
        "embattled": "a battlement edge",
        "nebuly": "a cloud-shaped edge",
    },
    "plural": {"sword": "swords", "key": "keys", "cross": "crosses",
               "fleur-de-lis": "fleurs-de-lis", "fish": "fish",
               "wheatsheaf": "wheatsheaves",
               "pair of antlers": "pairs of antlers",
               # Phrases pluralise on their head noun, not their tail: append
               # an "s" to "eagle with spread wings" and you get "wingss".
               "eagle with spread wings": "eagles with spread wings",
               "rearing lion": "rearing lions",
               "rearing horse": "rearing horses",
               "crescent moon": "crescent moons",
               "crescent moon facing right": "crescent moons facing right",
               "wavy-rayed star": "wavy-rayed stars"},
    "numbers": {2: "two", 3: "three", 4: "four", 5: "five"},
    "join": ", with ",
    "and": " and ",
}

LANGS = {"en": EN}


def _table():
    """Pick a glossary from the environment, falling back to English."""
    tag = (os.environ.get("LC_ALL") or os.environ.get("LC_MESSAGES")
           or os.environ.get("LANG") or "")
    if not tag:
        try:
            tag = (locale.getlocale()[0] or "")
        except (ValueError, TypeError):
            tag = ""
    code = tag.split(".")[0].split("_")[0].lower()
    return LANGS.get(code, EN)


def _plural(name, t):
    return t["plural"].get(name, name + "s")


def plain(blazon, table=None):
    """A plain-language sentence for one Blazon, or None if nothing to say."""
    t = table or _table()
    tin = t["tincture"]

    def colour(name):
        return tin.get(name, name)

    parts = []

    pattern = getattr(blazon, "pattern", None)
    if pattern:
        # Pattern themes have no heraldic reading, so the gloss just names the
        # figure and its two tinctures. The blazon line above is already plain
        # English here; this restates it as a phrase rather than a label.
        return "%s in %s and %s" % (pattern.capitalize(),
                                    colour(blazon.field),
                                    colour(blazon.field2))

    if blazon.variation:
        parts.append(t["variation"][blazon.variation].format(
            a=colour(blazon.field), b=colour(blazon.field2)))
    elif blazon.division:
        parts.append(t["division"][blazon.division].format(
            a=colour(blazon.field), b=colour(blazon.field2)))
    elif getattr(blazon, "seme", None):
        word = t["charge"].get(blazon.seme, blazon.seme)
        parts.append("%s strewn with %s %s"
                     % (colour(blazon.field), colour(blazon.field2),
                        _plural(word, t)))
    else:
        parts.append("%s" % colour(blazon.field))

    style = getattr(blazon, "line_style", "plain")
    edge = t["line"].get(style) if style != "plain" else None

    if blazon.ordinary:
        piece = t["ordinary"][blazon.ordinary].format(
            t=colour(blazon.ordinary_tincture))
        # The edge belongs to whichever element was actually cut with it: the
        # ordinary if there is one, otherwise the division.
        if edge:
            piece += " with " + edge
            edge = None
        parts.append(piece)
    elif edge and blazon.division:
        # "along" rather than another ", with", which would collide with the
        # clause the charge adds and read as a list of two unrelated things.
        parts[0] += " along " + edge
        edge = None

    if blazon.charge:
        word = t["charge"].get(blazon.charge, blazon.charge)
        shade = colour(blazon.charge_tincture)
        if blazon.charge_count == 1:
            article = "an" if word[0] in "aeiou" else "a"
            parts.append("%s %s %s" % (article, shade, word))
        else:
            count = t["numbers"].get(blazon.charge_count, str(blazon.charge_count))
            parts.append("%s %s %s" % (count, shade, _plural(word, t)))

    if getattr(blazon, "bordure", None):
        parts.append("a %s border" % colour(blazon.bordure))

    if not parts:
        return None
    head, rest = parts[0], parts[1:]
    if not rest:
        sentence = head
    elif len(rest) == 1:
        sentence = head + t["join"] + rest[0]
    else:
        sentence = head + t["join"] + t["and"].join(rest)
    return sentence[0].upper() + sentence[1:]
