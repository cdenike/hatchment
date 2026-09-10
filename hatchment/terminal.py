"""Measure the shape of a terminal cell on this system.

Braille art is dots packed 2 wide by 4 tall into a character cell, so how tall
the art comes out for a given width depends on the cell's proportions -- which
belong to the user's font, at the user's size, on the user's display, and are
therefore not something this program can know by assuming.

Terminals that fill in the pixel fields of TIOCGWINSZ report it directly, which
is every terminal Omarchy ships. Nothing is asked of the terminal and nothing is
read back: no escape sequence, no raw mode, no timeout waiting for a reply that
a terminal without the feature will never send.

Only the ratio is used, never the absolute size, because the ratio is the part
that survives display scaling: a window rendered at 2x reports both dimensions
doubled and divides back to the same shape.
"""

import fcntl
import struct
import termios


def cell_size(fd):
    """(width, height) of one character cell in pixels, or None.

    None covers a terminal that leaves the pixel fields at zero, a descriptor
    that is not a terminal at all, and platforms without the ioctl.
    """
    try:
        rows, cols, xpixel, ypixel = struct.unpack(
            "HHHH", fcntl.ioctl(fd, termios.TIOCGWINSZ, b"\0" * 8))
    except (OSError, ValueError, AttributeError):
        return None
    if not (rows and cols and xpixel and ypixel):
        return None
    return (xpixel / cols, ypixel / rows)


def cell_ratio(default=None):
    """Cell width divided by cell height, measured, or `default`.

    stderr first: the documented way to install a logo redirects stdout, so
    stdin and stderr are likelier to still be attached to the terminal.
    """
    for fd in (2, 0, 1):
        size = cell_size(fd)
        if size:
            return size[0] / size[1]
    return default
