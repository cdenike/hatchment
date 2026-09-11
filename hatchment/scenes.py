"""Settings: where a charge is, drawn the way heraldry draws it.

"A horse in a meadow" has no heraldic word for the meadow, but heraldry does
draw ground, water and sky -- a mount vert in base, barry wavy argent and
azure for water, a sun in chief, a field semé of stars for the night -- and a
scene built from those is still arms rather than a picture pasted on a
shield. Each setting is a recipe in those terms.

    ground     the shape along the base, and its tincture(s)
    row        small charges standing along it: (charge, variant, count, tincture)
    companion  charges in chief: (charge, variant, count, tincture)
    seme       small charges strewn over the field: (charge, tincture)
    field      the field it suggests, used only when a description gives none

Ground styles: a mount (one hill), a trimount (three), a flat base, dunes,
water, or none with flames or clouds rising from the rim.
"""

from .charges import article

SETTINGS = {
    "garden": {"ground": ("mount", "vert", None), "row": ("rose", None, 5, "gules"),
               "field": "argent"},
    "meadow": {"ground": ("mount", "vert", None), "row": ("rose", None, 6, "or"),
               "field": "argent"},
    "forest": {"ground": ("mount", "vert", None), "row": ("tree", "pine", 4, "vert"),
               "field": "argent"},
    "jungle": {"ground": ("mount", "vert", None), "row": ("tree", "palm", 3, "vert"),
               "field": "or"},
    "farm": {"ground": ("mount", "vert", None), "row": ("garb", None, 3, "or"),
             "field": "argent"},
    "mountains": {"ground": ("trimount", "vert", None), "field": "argent"},
    "hill": {"ground": ("mount", "vert", None), "field": "argent"},
    "snow": {"ground": ("mount", "argent", None), "row": ("tree", "pine", 3, "vert"),
             "field": "azure"},
    "sea": {"ground": ("water", "azure", "argent"), "field": "argent"},
    "desert": {"ground": ("dunes", "or", None),
               "companion": ("sun in splendour", None, 1, "or"), "field": "azure"},
    "fire": {"ground": ("flames", None, None), "row": ("flame", None, 5, "or"),
             "field": "gules"},
    "clouds": {"ground": ("clouds", None, None), "row": ("cloud", None, 3, "argent"),
               "field": "azure"},
    "sky": {"companion": ("sun in splendour", None, 1, "or"), "field": "azure"},
    "sunrise": {"companion": ("sun in splendour", None, 1, "or"), "field": "azure"},
    "sunset": {"companion": ("sun in splendour", None, 1, "or"), "field": "gules"},
    "night": {"seme": ("mullet", "argent"), "field": "azure"},
    "moonlight": {"companion": ("crescent", "full", 1, "argent"), "field": "azure"},
    "space": {"seme": ("mullet", "argent"),
              "companion": ("ringed planet", None, 1, "or"), "field": "sable"},
    "storm": {"ground": ("clouds", None, None), "row": ("cloud", None, 3, "argent"),
              "companion": ("thunderbolt", None, 2, "or"), "field": "sable"},
}

# The words a description may use for each. Plurals of charges ("mountains",
# "clouds") are listed outright, so they read as a setting rather than as
# several of the charge.
WORDS = {
    "garden": ["garden", "gardens", "flower garden", "flowerbed", "flower bed",
               "rose garden"],
    "meadow": ["meadow", "meadows", "pasture", "grassland", "grass", "lawn",
               "prairie", "green field", "field of flowers", "countryside"],
    "forest": ["forest", "woods", "wood", "woodland", "pine forest", "grove"],
    "jungle": ["jungle", "rainforest", "tropics", "tropical", "island", "oasis"],
    "farm": ["farm", "farmland", "harvest", "wheat field", "cornfield", "fields"],
    "mountains": ["mountains", "highlands", "peaks", "alps", "mountain range"],
    "hill": ["hills", "hilltop", "on a hill"],
    "snow": ["snow", "snowy", "winter", "arctic", "ice", "frozen", "tundra"],
    "sea": ["sea", "ocean", "lake", "river", "water", "waves", "beach", "shore",
            "coast", "pond", "bay", "harbour", "harbor", "stream", "seas"],
    "desert": ["desert", "dunes", "sand", "sands", "savanna", "savannah"],
    "fire": ["in flames", "from flames", "from the flames", "on fire", "inferno",
             "volcano", "hellfire", "hell", "flames below"],
    "clouds": ["clouds", "heaven", "heavens", "the clouds", "above the clouds"],
    "sky": ["sky", "skies", "sunny", "sunshine", "daylight", "daytime",
            "blue sky", "sunlight"],
    "sunrise": ["sunrise", "dawn", "morning", "daybreak"],
    "sunset": ["sunset", "dusk", "evening", "twilight"],
    "night": ["night", "nighttime", "night sky", "starry sky", "starry night",
              "under the stars", "starlight", "midnight", "at night"],
    "moonlight": ["moonlight", "moonlit", "moonrise", "under the moon"],
    "space": ["space", "outer space", "cosmos", "the void", "universe",
              "among the stars"],
    "storm": ["storm", "stormy", "thunderstorm", "tempest", "thunder"],
}

GROUND_KEYS = ("ground", "row")
SKY_KEYS = ("companion", "seme")


_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
          8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}


def _number(numbers, n):
    """A count spelled out: a gloss's own words first, then plain English."""
    return numbers.get(n) or _WORDS.get(n, str(n))


def blazon_phrases(b, named, numbers):
    """The setting in heraldic words, to follow the charge in a blazon."""
    out = []
    if getattr(b, "companion", None):
        n = b.companion_count
        word = named(b.companion, b.companion_variant, n)
        if n == 1:
            out.append("in dexter chief %s %s %s" % (article(word), word,
                                                     b.companion_tincture))
        else:
            out.append("in chief %s %s %s" % (_number(numbers, n), word,
                                              b.companion_tincture))
    style = getattr(b, "base_style", None)
    if style:
        row = ""
        if b.base_row:
            n = b.base_row_count
            row = "%s %s %s" % (_number(numbers, n),
                                named(b.base_row, b.base_row_variant, n),
                                b.base_row_tincture)
        bearing = (" bearing " + row) if row else ""
        if style == "mount":
            out.append("in base a mount %s%s" % (b.base_tincture, bearing))
        elif style == "trimount":
            out.append("in base a trimount %s%s" % (b.base_tincture, bearing))
        elif style == "flat":
            out.append("a base %s%s" % (b.base_tincture, bearing))
        elif style == "dunes":
            out.append("a base wavy %s" % b.base_tincture)
        elif style == "water":
            out.append("in base barry wavy %s and %s"
                       % (b.base_tincture, b.base_tincture2))
        elif row:
            out.append("issuant from the base " + row)
    return out


def plain_phrases(b, colour, named, numbers):
    """The same setting in ordinary words, for the gloss."""
    out = []
    if getattr(b, "companion", None):
        n = b.companion_count
        shade = colour(b.companion_tincture)
        word = named(b.companion, b.companion_variant, n)
        if n == 1:
            out.append("%s %s %s in the top corner" % (article(shade), shade, word))
        else:
            out.append("%s %s %s above" % (_number(numbers, n), shade, word))
    style = getattr(b, "base_style", None)
    if style:
        row = ""
        if b.base_row:
            n = b.base_row_count
            row = "%s %s %s" % (_number(numbers, n), colour(b.base_row_tincture),
                                named(b.base_row, b.base_row_variant, n))
        bearing = (" bearing " + row) if row else ""
        ground = colour(b.base_tincture) if b.base_tincture else ""
        if style == "mount":
            out.append("%s %s hill below%s" % (article(ground), ground, bearing))
        elif style == "trimount":
            out.append("%s hills below%s" % (ground, bearing))
        elif style == "flat":
            out.append("%s ground below%s" % (ground, bearing))
        elif style == "dunes":
            out.append("%s dunes below" % ground)
        elif style == "water":
            out.append("%s and %s waves below"
                       % (ground, colour(b.base_tincture2)))
        elif row:
            out.append(row + " rising from below")
    return out
