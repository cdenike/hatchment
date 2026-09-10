"""Read the live Omarchy theme palette.

Omarchy keeps the active theme's files under ~/.local/state/omarchy/current/,
copied there rather than symlinked to the theme source, so this reads the state
directory and not the theme catalogue -- a user theme and a stock one look the
same from here, which is the point.

Everything degrades to None rather than raising. A missing palette means the app
falls back to whatever libadwaita would have done on its own, which is a
perfectly good look; it is not worth a crash.
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


def name():
    try:
        return NAME.read_text().strip()
    except OSError:
        return None


def is_dark(colours):
    return (colours or {}).get("mode", "dark") != "light"
