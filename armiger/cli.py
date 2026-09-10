"""armiger -- generate a random coat of arms and wear it on your desktop."""

import argparse
import os
import pathlib
import random
import subprocess
import sys

from .blazon import Blazon
from .draw import render
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
    return to_braille(render(blazon, solid=True), cols)


def generate(rng, cols, max_complexity=3, attempts=60):
    """Roll arms until one renders legibly at `cols` wide."""
    last = None
    for _ in range(attempts):
        blazon = Blazon(rng).generate(max_complexity=max_complexity)
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
        prog="armiger",
        description="Generate a random coat of arms as braille art.")
    p.add_argument("--seed", help="reproduce a specific coat of arms")
    p.add_argument("--cols", type=int, default=24,
                   help="width in terminal columns (default: 24)")
    p.add_argument("--simple", action="store_true",
                   help="restrict to the simplest charges")
    p.add_argument("--fastfetch", action="store_true",
                   help="install as the fastfetch logo")
    p.add_argument("--screensaver", action="store_true",
                   help="install as the Omarchy screensaver branding")
    p.add_argument("--svg", metavar="PATH",
                   help="also write the full-colour-hatched SVG here")
    p.add_argument("--no-reload", action="store_true",
                   help="install screensaver branding without restarting it "
                        "(the restart takes over the screen)")
    p.add_argument("--quiet", action="store_true", help="print nothing but the art")
    args = p.parse_args(argv)

    seed = args.seed if args.seed is not None else os.urandom(8).hex()
    rng = random.Random(seed)

    blazon, art = generate(rng, args.cols,
                           max_complexity=1 if args.simple else 3)

    if not args.quiet:
        print(blazon.describe())
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
        write(FASTFETCH_LOGO, art)
        if not args.quiet:
            print("\n-> %s" % FASTFETCH_LOGO, file=sys.stderr)

    if args.screensaver:
        # The screensaver has far more room than the fastfetch sidebar, so it
        # gets its own render rather than a scaled-up copy of a 24-column one,
        # which would just be blocky.
        write(SCREENSAVER, draw_at(blazon, 56))
        if not args.quiet:
            print("-> %s" % SCREENSAVER, file=sys.stderr)
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
