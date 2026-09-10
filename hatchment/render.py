"""Render SVG to braille art at an exact character-cell size.

A braille cell is 2 dots wide by 4 tall, so a WxH cell grid is a (2W)x(4H) dot
bitmap. Terminal cells are roughly 8.5x16px, making dots about 4.25x4.0px --
nearly square, but not quite, so the dot grid is corrected for that.

The braille-packing approach here follows the make-logo.py already in
~/.config/fastfetch, which got this right; this version adds SVG input and
sizing driven by the target rather than by hand.
"""

import subprocess

# Braille dot numbering is historical, not raster order: dots 1-6 came first and
# 7-8 were bolted underneath, so the bottom row is bits 6 and 7.
BIT = {(0, 0): 0, (1, 0): 1, (2, 0): 2, (3, 0): 6,
       (0, 1): 3, (1, 1): 4, (2, 1): 5, (3, 1): 7}

DOT_ASPECT = 4.25 / 4.0  # dot width / height in px


def _run(cmd, stdin=None, timeout=20):
    """Run a converter, refusing to wait on it forever.

    Without a timeout a wedged rsvg-convert or ImageMagick blocks the calling
    thread indefinitely, and in the GUI that thread is holding the flag that
    keeps the buttons disabled -- so one stuck child process reads to the user
    as the whole app hanging.
    """
    return subprocess.run(cmd, input=stdin, capture_output=True,
                          check=True, timeout=timeout).stdout


def hatch_params(cols):
    """Hatch spacing and stroke, in SVG units, tuned to the output width.

    Both are derived from the dot grid rather than fixed, because hatching only
    reads when its period is a whole number of dots. The shield is 100 units
    wide and the grid is 2*cols dots, so a unit is cols/50 dots; aim for a line
    every ~7 dots about 2 dots thick.
    """
    dots_per_unit = (cols * 2) / 100.0
    spacing = max(3.0, 7.0 / dots_per_unit)
    stroke = max(0.8, 2.0 / dots_per_unit)
    return spacing, stroke


def bitmap(svg_bytes, dots_w, dots_h, threshold, blur):
    """Rasterise the SVG straight to the dot grid.

    Rendering large and downsampling is what kills hatching: a one-pixel rule
    resampled to a fraction of a pixel becomes grey, and thresholding grey
    against a regular grid produces moire -- the tinctures turn to mush and the
    charge drowns in it. rsvg-convert rasterises the vector at exactly the
    target size instead, so a hatch line is placed on whole dots and stays a
    line all the way down.
    """
    png = _run(["rsvg-convert", "-w", str(dots_w), "-h", str(dots_h),
                "--background-color", "white", "-f", "png"], stdin=svg_bytes)
    cmd = ["magick", "png:-", "-colorspace", "gray"]
    if blur:
        cmd += ["-blur", "0x%s" % blur]
    cmd += ["-threshold", "%s%%" % threshold, "-compress", "none", "pbm:-"]
    out = _run(cmd, stdin=png).decode()

    toks = []
    for line in out.splitlines():
        if line.startswith("#"):
            continue
        toks += line.split()
    assert toks[0] == "P1", "expected a plain PBM from ImageMagick"
    w, h = int(toks[1]), int(toks[2])
    vals = [int(t) for t in toks[3:3 + w * h]]
    return [vals[y * w:(y + 1) * w] for y in range(h)]


def encode(grid):
    h, w = len(grid), len(grid[0])
    rows = []
    for cy in range(0, h, 4):
        row = ""
        for cx in range(0, w, 2):
            bits = 0
            for (r, c), b in BIT.items():
                y, x = cy + r, cx + c
                if y < h and x < w and grid[y][x]:
                    bits |= 1 << b
            row += chr(0x2800 + bits) if bits else " "
        rows.append(row.rstrip())
    # Trim blank leading/trailing rows so the art sits flush in its box.
    while rows and not rows[0].strip():
        rows.pop(0)
    while rows and not rows[-1].strip():
        rows.pop()
    return "\n".join(rows)


def to_braille(svg, cols, aspect=100.0 / 115.0, threshold=50, blur=None):
    """Render an SVG string to braille art `cols` characters wide.

    `aspect` is the source's width/height. It is passed in rather than measured
    because the shield's box is known and fixed; trimming to ink would instead
    measure whatever the arms happen to reach, so identical shields would come
    out at different heights depending on their charges.
    """
    dots_w = cols * 2
    rows = max(1, round(dots_w * DOT_ASPECT / aspect / 4))
    grid = bitmap(svg.encode(), dots_w, rows * 4, threshold, blur)
    return encode(grid)
