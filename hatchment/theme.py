"""Read the live Omarchy theme palette.

Omarchy keeps the active theme's files under ~/.local/state/omarchy/current/,
copied there rather than symlinked to the theme source, so this reads the state
directory and not the theme catalogue -- a user theme and a stock one look the
same from here, which is the point.

Everything degrades rather than raising. A missing palette means there is no
Omarchy theme to follow -- plain Arch, or any other desktop -- and the app uses
GENERIC below instead; it is not worth a crash either way.

Copyright (C) 2026 Caden DeNike. Free software under the GNU General
Public License, version 3 or later, with no warranty. See LICENSE.
"""

import pathlib

STATE = pathlib.Path.home() / ".local/state/omarchy/current"
# The palette lives inside the copied theme directory; the name sits beside it.
COLORS = STATE / "theme" / "colors.toml"
NAME = STATE / "theme.name"

# The keys the app actually uses. The palette carries far more (a full ANSI set
# and several background tiers); these are the ones with a job here.
WANTED = ("mode", "accent", "selection", "background", "dark_background",
          "lighter_background", "foreground", "light_foreground", "muted")


# Palette for a system with no Omarchy theme to read. Deliberately not a copy of
# an Omarchy theme: it is a neutral dark surface with a green accent, and every
# colour is opaque. Omarchy windows are translucent because its gtk.css hook
# gives them alpha to sit over a wallpaper the theme also controls; with no
# theme there is no such arrangement, and a window that lets an unknown desktop
# through is a legibility problem rather than a look.
GENERIC = {
    "mode": "dark",
    "background": "#1b1d1e",
    "dark_background": "#121415",
    "lighter_background": "#25282a",
    "foreground": "#e3e6e4",
    "light_foreground": "#ffffff",
    "muted": "#8b918e",
    "accent": "#3fb950",
    "selection": "#2c5c37",
}


def _parse_flat_toml(text):
    """Minimal parser for the flat `key = "value"` shape colors.toml uses.

    tomllib would do this, but it only arrived in 3.11 and this file has no
    tables, arrays or multi-line strings -- nothing that needs a real parser.
    Doing it by hand keeps the package working on older interpreters for the
    sake of about eight lines.
    """
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip('"').strip("'")
        out[key.strip()] = value
    return out


def palette():
    """The current theme's colours as a dict, or None if unavailable."""
    try:
        raw = _parse_flat_toml(COLORS.read_text())
    except OSError:
        return None
    colours = {k: raw[k] for k in WANTED if k in raw}
    return colours or None


def effective_palette():
    """(colours, generic) -- the live Omarchy palette, or the generic one.

    The flag matters to the caller: the generic palette is the app dressing
    itself, so it may also draw a border and insist on opacity, while an
    Omarchy palette is the system's own and is followed rather than decorated.
    """
    colours = palette()
    if colours:
        return colours, False
    return dict(GENERIC), True


def name():
    try:
        return NAME.read_text().strip()
    except OSError:
        return None


def is_dark(colours):
    return (colours or {}).get("mode", "dark") != "light"
