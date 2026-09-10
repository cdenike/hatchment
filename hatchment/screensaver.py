"""Size the screensaver art to the screen it will be shown on.

The braille art is written to a file once and read back later by ttfx, inside a
fullscreen terminal this process is not running in -- so the usual way of asking
how big the terminal is (`shutil.get_terminal_size`) reports the terminal
hatchment was *launched* from, which is the wrong window on the wrong monitor at
the wrong font size.

What can be known at write time is the screen and the font, and that is enough:
omarchy-launch-screensaver pins the screensaver terminal to 18pt in all four
terminals it supports, and the compositor knows the monitor geometry. The cell
grid follows from those two.

Art that is too small is merely a modest shield on a wide screen. Art that is
taller than the terminal is clipped, and ttfx -- which centres the canvas it is
given -- then has nothing to centre. Every estimate below is therefore biased
towards fewer rows.
"""

import json
import subprocess

from .render import cols_for_rows, fit_cols

# omarchy-launch-screensaver passes --font-size=18 to ghostty and font_size 18
# to kitty, and hands alacritty and foot screensaver configs that both set 18.
# The terminal is chosen by xdg-terminal-exec and so is not known here; the font
# size is the same whichever it picks.
FONT_PT = 18

# A point is 1/72 inch and a pixel 1/96, and the compositor's scale applies to
# both, so this times the scale converts the font size to device pixels.
PX_PER_PT = 96.0 / 72.0

# Cell size as a fraction of the em. Monospace faces differ -- the ones omarchy
# ships sit between roughly 1.2 and 1.35 line height -- so the tall end is used
# rather than an average: overestimating cell height undercounts rows, which
# errs towards art that is too small, and small is the failure that still works.
LINE_HEIGHT = 1.32
CELL_WIDTH = 0.60

# How much of the screen the shield should fill. Height is the binding
# constraint on every ordinary aspect ratio; the width limit only bites on a
# screen that is wider than it is tall by more than the shield's own proportion,
# which is to say a very short window or a monitor in a stacked pair.
HEIGHT_FRACTION = 0.60
WIDTH_FRACTION = 0.50

# Below the floor the charges stop being charges; above the ceiling the render
# is slow and gains nothing, since the original hand-picked 56 was already sized
# for a large desktop monitor.
MIN_COLS, MAX_COLS = 16, 56

# No compositor, no answer, or an answer in a shape this does not understand.
# 24 columns is 15 rows, which fits the shortest screen anyone runs this on.
FALLBACK_COLS = 24


def cell_grid(width, height, scale):
    """Terminal columns and rows a fullscreen 18pt window gets on this monitor.

    `width` and `height` are device pixels and `scale` the compositor's, which
    is how hyprctl reports them: the font is laid out at the scaled size, so the
    grid is a function of the raw pixels and the scale together.
    """
    em = FONT_PT * PX_PER_PT * scale
    return (int(width / (em * CELL_WIDTH)), int(height / (em * LINE_HEIGHT)))


def cols_for_grid(cols, rows):
    """Art width for a terminal of this size, before clamping."""
    return min(cols_for_rows(int(rows * HEIGHT_FRACTION)),
               int(cols * WIDTH_FRACTION))


def monitors():
    """Active monitors as (width, height, scale), or [] if we cannot ask."""
    try:
        out = subprocess.run(["hyprctl", "monitors", "-j"], capture_output=True,
                             text=True, timeout=5, check=True).stdout
        return [(m["width"], m["height"], m.get("scale", 1.0))
                for m in json.loads(out) if not m.get("disabled")]
    except (OSError, subprocess.SubprocessError, ValueError, KeyError):
        return []


def fit():
    """Art size to install, fitted to the smallest screen it will appear on.

    omarchy-launch-screensaver opens the screensaver on every monitor, and all
    of them read this one file -- so the smallest screen sets the size. The
    alternative, fitting the largest, is the bug this exists to prevent: art
    designed on a big monitor arrives on a laptop taller than its screen.
    """
    screens = monitors()
    sizes = [cols_for_grid(*cell_grid(*s)) for s in screens]
    if not sizes:
        return fit_cols(FALLBACK_COLS, "no screen to measure")
    return fit_cols(max(MIN_COLS, min(MAX_COLS, min(sizes))),
                    "fitted to %s" % " + ".join("%dx%d@%gx" % s for s in screens))
