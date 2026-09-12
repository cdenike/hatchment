"""hatchment -- generate a random coat of arms and wear it on your desktop.

Copyright (C) 2026 Caden DeNike. Free software under the GNU General
Public License, version 3 or later, with no warranty. See LICENSE.
"""

import argparse
import os
import pathlib
import random
import subprocess
import sys

from . import __version__, fastfetch, menuicon, prompt, screensaver, stock
from .blazon import THEMES, Blazon, new_seed, vocabulary_for
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


def generate(rng, cols, max_complexity=None, attempts=60, theme=None,
             wishes=None, vocab=1):
    """Roll arms until one renders legibly at `cols` wide.

    `wishes`, from hatchment.prompt, fixes whatever a description named and
    leaves the rest to the roll. When it named everything there is nothing left
    to re-roll, so the same arms coming back three times ends the search rather
    than rendering them sixty times over.
    """
    if max_complexity is None:
        max_complexity = complexity_for(cols)
    last, repeats = None, 0
    for _ in range(attempts):
        if wishes is not None:
            blazon = prompt.compose(wishes, rng, theme=theme,
                                    max_complexity=max_complexity, vocab=vocab)
            repeats = repeats + 1 if last and blazon.describe() == last[0].describe() else 0
        else:
            blazon = Blazon(rng, theme=theme, vocab=vocab).generate(
                max_complexity=max_complexity)
        art = draw_at(blazon, cols)
        last = (blazon, art)
        if INK_MIN <= ink_ratio(art) <= INK_MAX:
            return blazon, art
        if repeats >= 2:
            break
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
    # Worth having for its own sake, and worth having because the arms this
    # draws depend on the version: a seed rolls in the vocabulary of the
    # release that made it, so "which version is this?" is a question about the
    # output and not only about the package.
    p.add_argument("--version", action="version",
                   version="hatchment %s" % __version__,
                   help="print the version and exit")
    p.add_argument("--seed", help="reproduce a specific coat of arms")
    p.add_argument("--prompt", metavar="TEXT",
                   help='describe the arms, e.g. "three gold lions on red, a '
                        'blue border"; anything left out is rolled')
    p.add_argument("--cols", type=int, default=24,
                   help="width in terminal columns (default: 24)")
    p.add_argument("--simple", action="store_true",
                   help="restrict to the simplest charges")
    p.add_argument("--theme", choices=THEMES,
                   help="draw charges from one register only "
                        "(default: both)")
    p.add_argument("--fastfetch", action="store_true",
                   help="install as the fastfetch logo, pointing fastfetch at "
                        "it if you have no fastfetch config of your own")
    p.add_argument("--screensaver", action="store_true",
                   help="install as the Omarchy screensaver branding")
    p.add_argument("--menu-icon", action="store_true",
                   help="wear the arms as the Omarchy menu button")
    p.add_argument("--menu-icon-off", action="store_true",
                   help="put Omarchy's own menu button back")
    p.add_argument("--stock", action="store_true",
                   help="put back Omarchy's own screensaver, fastfetch logo "
                        "and menu button (what they replace is kept as .bak)")
    p.add_argument("--svg", metavar="PATH",
                   help="also write the arms here as a full-colour SVG")
    p.add_argument("--hatched", action="store_true",
                   help="draw the --svg in Petra Sancta hatching, one ink, "
                        "instead of colour")
    p.add_argument("--no-reload", action="store_true",
                   help="install screensaver branding without restarting it "
                        "(the restart takes over the screen)")
    p.add_argument("--quiet", action="store_true", help="print nothing but the art")
    args = p.parse_args(argv)

    # Restoring needs no arms, so it happens before the roll rather than after
    # generating a shield nobody asked to see.
    if args.stock:
        results = stock.reset(FASTFETCH_LOGO, SCREENSAVER)
        for _name, _changed, message in results:
            print(message, file=sys.stderr)
        # The same preview rule as installing: show the screensaver that is now
        # in place, unless asked not to take the screen.
        if not args.no_reload and any(name == "screensaver" and changed
                                      for name, changed, _ in results):
            subprocess.run(["omarchy-launch-screensaver", "force"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           check=False)
    elif args.menu_icon_off:
        print(menuicon.restore(), file=sys.stderr)
    if ((args.stock or args.menu_icon_off)
            and not (args.fastfetch or args.screensaver or args.menu_icon)):
        return 0

    seed = args.seed if args.seed is not None else new_seed()
    rng = random.Random(seed)

    wishes = prompt.parse(args.prompt) if args.prompt else None
    blazon, art = generate(rng, args.cols,
                           max_complexity=1 if args.simple else 3,
                           theme=args.theme, wishes=wishes,
                           vocab=vocabulary_for(seed, args.theme))

    if not args.quiet:
        print(blazon.describe())
        gloss = plain(blazon)
        if gloss:
            print('\u201c%s\u201d' % gloss)
        print("seed: %s" % seed)
        if wishes and wishes.notes:
            # After the arms they are about, not before: stderr is unbuffered
            # and would otherwise jump ahead of everything printed so far.
            sys.stdout.flush()
            for note in wishes.notes:
                print("note: %s" % note, file=sys.stderr)
        print()
    print(art)

    if args.svg:
        # Colour unless asked otherwise. Hatching is how an engraver prints
        # colour in one ink, and it breaks up on a patterned field -- rings and
        # fractals are finer than any hatch spacing that reads -- so it is kept
        # for arms that want the engraved look rather than made the default.
        pathlib.Path(args.svg).write_text(
            render(blazon, spacing=5.0, stroke=1.1, size=900) if args.hatched
            else render(blazon, colour=True, size=900))

    if args.fastfetch:
        # The logo shares its lines with the info block, so the terminal decides
        # how wide it may be -- see hatchment.fastfetch. A constant here was
        # only ever right in a terminal the width of the one it was picked in.
        size, note = fastfetch.install(FASTFETCH_LOGO,
                                       lambda cols: draw_at(blazon, cols))
        if not args.quiet:
            print("\n-> %s (%s)" % (FASTFETCH_LOGO, size), file=sys.stderr)
            if note:
                print("   %s" % note, file=sys.stderr)

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
