"""Render SVG to braille art at an exact character-cell size.

A braille cell is 2 dots wide by 4 tall, so a WxH cell grid is a (2W)x(4H) dot
bitmap. Terminal cells are roughly 8.5x16px, making dots about 4.25x4.0px --
nearly square, but not quite, so the dot grid is corrected for that.

The braille-packing approach here follows the make-logo.py already in
~/.config/fastfetch, which got this right; this version adds SVG input and
sizing driven by the target rather than by hand.

Only one external program is needed: rsvg-convert, to rasterise the vector.
Thresholding its output to 1-bit used to be a second call, to ImageMagick, for
work the standard library already does -- 21 MiB of dependency and a process
spawn per render to compare bytes against a number.
"""

import struct
import subprocess
import zlib

from .terminal import cell_ratio

# Braille dot numbering is historical, not raster order: dots 1-6 came first and
# 7-8 were bolted underneath, so the bottom row is bits 6 and 7.
BIT = {(0, 0): 0, (1, 0): 1, (2, 0): 2, (3, 0): 6,
       (0, 1): 3, (1, 1): 4, (2, 1): 5, (3, 1): 7}

# Fallback dot width / height, for a terminal that will not say: cells about
# 8.5x16px, which is a common shape but only ever a guess about someone else's
# font. measured_dot_aspect() prefers the real thing.
DOT_ASPECT = 4.25 / 4.0


def measured_dot_aspect():
    """Braille dot width / height on this terminal, or the fallback.

    A cell holds 2 dots across and 4 down, so a dot is half a cell wide and a
    quarter of one tall, and the dot ratio is twice the cell ratio.
    """
    ratio = cell_ratio()
    return 2 * ratio if ratio else DOT_ASPECT

PNG_SIG = b"\x89PNG\r\n\x1a\n"

# Bytes per pixel by PNG colour type, at bit depth 8.
CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


def _run(cmd, stdin=None, timeout=20):
    """Run a converter, refusing to wait on it forever.

    Without a timeout a wedged rsvg-convert blocks the calling thread
    indefinitely, and in the GUI that thread is holding the flag that keeps the
    buttons disabled -- so one stuck child process reads as the whole app
    hanging.
    """
    return subprocess.run(cmd, input=stdin, capture_output=True,
                          check=True, timeout=timeout).stdout


def _unfilter(raw, width, height, bpp):
    """Undo the per-scanline filters PNG applies before compression.

    Each row is prefixed with a filter byte naming one of five predictors, all
    of which reference the pixel to the left, the row above, or both. This is
    the whole of PNG decoding that is not zlib.
    """
    stride = width * bpp
    out = bytearray(stride * height)
    prev = bytearray(stride)
    pos = 0
    for y in range(height):
        ftype = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos + stride])
        pos += stride
        if ftype == 1:      # Sub
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif ftype == 2:    # Up
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ftype == 3:    # Average
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:    # Paeth
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return bytes(out)


def png_to_bits(data, threshold):
    """Decode an 8-bit PNG and threshold it to a grid of 0/1 rows.

    Only what rsvg-convert emits is supported: bit depth 8, non-interlaced.
    Anything else raises rather than guessing, because a silently misread
    bitmap would show up as art that is subtly wrong rather than as an error.
    """
    if not data.startswith(PNG_SIG):
        raise ValueError("not a PNG")

    width = height = bpp = None
    idat = []
    pos = len(PNG_SIG)
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        kind = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        pos += 12 + length          # length + type + body + CRC
        if kind == b"IHDR":
            width, height, depth, colour, _, _, interlace = struct.unpack(
                ">IIBBBBB", body)
            if depth != 8 or interlace or colour not in CHANNELS:
                raise ValueError("unsupported PNG: depth=%d colour=%d "
                                 "interlace=%d" % (depth, colour, interlace))
            bpp = CHANNELS[colour]
        elif kind == b"IDAT":
            idat.append(body)
        elif kind == b"IEND":
            break

    if width is None:
        raise ValueError("PNG has no IHDR")

    pixels = _unfilter(zlib.decompress(b"".join(idat)), width, height, bpp)

    # Ink is dark. Compare the first channel only: the source is pure black on
    # pure white, so luminance weighting would cost a multiply per pixel to
    # reach the same answer.
    # Inclusive: ImageMagick's -threshold 50% inks 0..127, and an exclusive
    # compare here shifted every edge pixel by one level, which changed the
    # outline of most shields.
    cut = int(255 * threshold / 100.0)
    stride = width * bpp
    return [[1 if pixels[y * stride + x * bpp] <= cut else 0
             for x in range(width)]
            for y in range(height)]


def bitmap(svg_bytes, dots_w, dots_h, threshold):
    """Rasterise the SVG straight to the dot grid.

    Rendering large and downsampling is what kills fine detail: a one-pixel rule
    resampled to a fraction of a pixel becomes grey, and thresholding grey
    against a regular grid produces moire. rsvg-convert rasterises the vector at
    exactly the target size instead, so a hatch line is placed on whole dots and
    stays a line all the way down.
    """
    png = _run(["rsvg-convert", "-w", str(dots_w), "-h", str(dots_h),
                "--background-color", "white", "-f", "png"], stdin=svg_bytes)
    return png_to_bits(png, threshold)


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


class Fit:
    """A chosen art size, and the reason it came out that size.

    Carried around together because every caller that picks a size also wants
    to say why: a width that arrives without its reasoning is indistinguishable
    from a magic number, which is what this whole mechanism replaced.

    Deliberately not a namedtuple. A tuple spreads itself across %-formatting,
    so `"...(%s)" % size` raises TypeError rather than printing the size -- and
    a one-line status message is the entire point of this class, so the obvious
    way to use it must not be the broken one.
    """

    __slots__ = ("cols", "rows", "why")

    def __init__(self, cols, rows, why):
        self.cols = cols
        self.rows = rows
        self.why = why

    def __str__(self):
        return "%d cols x %d lines, %s" % (self.cols, self.rows, self.why)

    def __repr__(self):
        return "Fit(cols=%d, rows=%d, why=%r)" % (self.cols, self.rows, self.why)


def fit_cols(cols, why):
    """A Fit for `cols` wide, filling in the height it implies."""
    return Fit(cols, rows_for_cols(cols), why)


def rows_for_cols(cols, aspect=100.0 / 115.0, dot_aspect=None):
    """Height in character cells that `cols` of art will occupy."""
    dot_aspect = measured_dot_aspect() if dot_aspect is None else dot_aspect
    return max(1, round(cols * 2 * dot_aspect / aspect / 4))


def cols_for_rows(rows, aspect=100.0 / 115.0, dot_aspect=None):
    """Widest art that still fits in `rows` character cells.

    The inverse of rows_for_cols, which is not quite the same as dividing: that
    function rounds, so the arithmetic inverse can land one row over the budget.
    Stepping down until it actually fits is what makes this safe to size a
    screen with -- a height that is one row too tall is exactly the failure
    this is here to avoid.
    """
    dot_aspect = measured_dot_aspect() if dot_aspect is None else dot_aspect
    cols = int(rows * 4 * aspect / (2 * dot_aspect))
    while cols > 1 and rows_for_cols(cols, aspect, dot_aspect) > rows:
        cols -= 1
    return max(1, cols)


def to_braille(svg, cols, aspect=100.0 / 115.0, threshold=50, dot_aspect=None):
    """Render an SVG string to braille art `cols` characters wide.

    `aspect` is the source's width/height. It is passed in rather than measured
    because the shield's box is known and fixed; trimming to ink would instead
    measure whatever the arms happen to reach, so identical shields would come
    out at different heights depending on their charges.
    """
    dots_w = cols * 2
    rows = rows_for_cols(cols, aspect, dot_aspect)
    return encode(bitmap(svg.encode(), dots_w, rows * 4, threshold))
