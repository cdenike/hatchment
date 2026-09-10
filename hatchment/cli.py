"""hatchment -- generate a random coat of arms and wear it on your desktop."""

import argparse
import os
import pathlib
import random
import subprocess
import sys

from . import fastfetch, menuicon, screensaver
from .blazon import Blazon
from .draw import render
from .gloss import plain
from .render import to_braille

FASTFETCH_LOGO = pathlib.Path.home() / ".config/fastfetch/coat-of-arms.txt"
SCREENSAVER = pathlib.Path.home() / ".config/omarchy/branding/screensaver.txt"

# Ink outside this band means the art has collapsed: a near-empty shield, or a
# near-solid one where the tinctures have run together. Re-roll rather than
# install something unreadable.
INK_MIN, INK_MAX = 0.10, 0.52


def ink_ratio(art):
    """Fraction of *dots* set, not cells.

    Counting cells would call any hatched area full, since hatching touches
    almost every cell while filling few of its dots -- exactly the distinction
    this gate exists to measure.
    """
    total = set_dots = 0
    for line in art.splitlines():
        for ch in line:
            if ch == " ":
                total += 8
                continue
            code = ord(ch) - 0x2800
            if 0 <= code <= 0xFF:
                total += 8
                set_dots += bin(code).count("1")
    return (set_dots / total) if total else 0.0


def draw_at(blazon, cols):
    """Render one blazon at a given width, flattened to two tones.

    Petra Sancta hatching is the right answer on paper and the wrong one here.
    Tried and measured: even rasterised crisply at dot resolution, a hatch
    period wide enough to survive braille is coarse enough to read as graph
    paper, and the ordinary and charge stop separating from the field. Two
    tones lose which colour a tincture is but keep the shapes, and the shapes
    are what a 24-column shield can actually carry. The hatching survives in
    the SVG export, where there are pixels to spare for it.
    """
    # The shield outline is 3.2 units on a 100-unit box, which is 1.5 dots wide
    # at 24 columns and 0.45 at 7 -- and a line thinner than a dot thresholds
    # away, taking the silhouette with it. Widen it for small targets so the
    # shield always has an edge: below 16 columns this is what is left of the
    # drawing. Above that the constant is already wider and nothing changes.
    outline = max(3.2, 50.0 / cols)
    return to_braille(render(blazon, solid=True, outline=outline), cols)


def complexity_for(cols):
    """How much charge detail the target width can actually hold.

    A lion or a horse needs roughly 50 dots across before it stops reading as a
    blot, which is 26 columns. Below that the generator is restricted to shapes
    whose silhouette survives -- stars, crescents, towers -- rather than being
    allowed to pick a beast and produce mush.
    """
    if cols >= 26:
        return 4
    return 3


def generate(rng, cols, max_complexity=None, attempts=60, theme=None):
    """Roll arms until one renders legibly at `cols` wide."""
    if max_complexity is None:
        max_complexity = complexity_for(cols)
    last = None
    for _ in range(attempts):
        blazon = Blazon(rng, theme=theme).generate(max_complexity=max_complexity)
        art = draw_at(blazon, cols)
        last = (blazon, art)
        if INK_MIN <= ink_ratio(art) <= INK_MAX:
            return blazon, art
    # Give back the last roll rather than failing outright; the caller still
    # gets working arms, just not ones that passed the aesthetic gate.
    return last


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n")


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="hatchment",
        description="Generate a random coat of arms as braille art.")
    p.add_argument("--seed", help="reproduce a specific coat of arms")
    p.add_argument("--cols", type=int, default=24,
                   help="width in terminal columns (default: 24)")
    p.add_argument("--simple", action="store_true",
                   help="restrict to the simplest charges")
    p.add_argument("--theme",
                   choices=("cosmic", "fractal", "geometric", "medieval",
                            "natural"),
                   help="draw charges from one register only "
                        "(default: both)")
    p.add_argument("--fastfetch", action="store_true",
                   help="install as the fastfetch logo")
    p.add_argument("--screensaver", action="store_true",
                   help="install as the Omarchy screensaver branding")
    p.add_argument("--menu-icon", action="store_true",
                   help="wear the arms as the Omarchy menu button")
    p.add_argument("--menu-icon-off", action="store_true",
                   help="put Omarchy's own menu button back")
    p.add_argument("--svg", metavar="PATH",
                   help="also write the full-colour-hatched SVG here")
    p.add_argument("--no-reload", action="store_true",
                   help="install screensaver branding without restarting it "
                        "(the restart takes over the screen)")
    p.add_argument("--quiet", action="store_true", help="print nothing but the art")
    args = p.parse_args(argv)

    # Restoring needs no arms, so it happens before the roll rather than after
    # generating a shield nobody asked to see.
    if args.menu_icon_off:
        print(menuicon.restore(), file=sys.stderr)
        if not (args.fastfetch or args.screensaver or args.menu_icon):
            return 0

    seed = args.seed if args.seed is not None else os.urandom(8).hex()
    rng = random.Random(seed)

    blazon, art = generate(rng, args.cols,
                           max_complexity=1 if args.simple else 3,
                           theme=args.theme)

    if not args.quiet:
        print(blazon.describe())
        gloss = plain(blazon)
        if gloss:
            print('\u201c%s\u201d' % gloss)
        print("seed: %s" % seed)
        print()
    print(art)

    if args.svg:
        # The SVG keeps Petra Sancta hatching: at vector resolution the lines
        # read as intended, so the tinctures survive here even though the
        # braille version has to flatten them to two tones.
        pathlib.Path(args.svg).write_text(
            render(blazon, spacing=5.0, stroke=1.1, solid=False, size=900))

    if args.fastfetch:
        # The logo shares its lines with the info block, so the terminal decides
        # how wide it may be -- see hatchment.fastfetch. A constant here was
        # only ever right in a terminal the width of the one it was picked in.
        size = fastfetch.fit(FASTFETCH_LOGO)
        write(FASTFETCH_LOGO, draw_at(blazon, size.cols))
        if not args.quiet:
            print("\n-> %s (%s)" % (FASTFETCH_LOGO, size), file=sys.stderr)

    if args.menu_icon:
        if not menuicon.available():
            print("no Omarchy shell config; menu icon not installed",
                  file=sys.stderr)
        else:
            result = menuicon.install(blazon)
            if not args.quiet:
                print("-> %s (%s)" % (menuicon.ICON, result), file=sys.stderr)

    if args.screensaver:
        # The screensaver gets its own render rather than a scaled-up copy of
        # the printed art -- scaling braille resamples it into mush -- and its
        # width comes from the screen rather than a constant, because a constant
        # is only ever right on the monitor it was chosen on.
        size = screensaver.fit()
        write(SCREENSAVER, draw_at(blazon, size.cols))
        if not args.quiet:
            print("-> %s (%s)" % (SCREENSAVER, size), file=sys.stderr)
        # `force` relaunches the screensaver, which means it takes the screen
        # immediately -- fine when the user asked for a preview, rude in the
        # middle of something, hence the opt-out.
        if not args.no_reload:
            subprocess.run(["omarchy-launch-screensaver", "force"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           check=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
