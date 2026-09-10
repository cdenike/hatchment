"""Size the logo to the terminal fastfetch will be printed in.

The logo shares a line with the info block, so its width is whatever the
terminal has left over: terminal - info - padding. All three are measurable --
fastfetch will render its own info block on request, and the difference between
that and a full render is the padding -- so none of it has to be assumed.

A logo that is too wide does not wrap, it pushes the info block off the right
edge of the terminal, and with `display.disableLinewrap` set (which Omarchy's
config does) the overflow is silently truncated rather than wrapped. Losing the
right-hand end of every line reads as a broken config, so overshooting is the
failure worth avoiding here.
"""

import os
import re
import shutil
import subprocess

from .render import fit_cols

# Every fastfetch module colours its output, so the escape sequences have to
# come off before anything is measured. Colour is all that appears here: no
# cursor movement, which would make column counting much harder.
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

# Padding either side of the logo when a render cannot be measured to derive it.
# The config Omarchy ships pads 1 left and 2 right.
DEFAULT_PADDING = 3

# One column of slack. Filling the terminal exactly is where terminals stop
# agreeing with each other about whether a line that reaches the last column has
# wrapped yet, and the cost of not finding out is one column of shield.
SAFETY = 1

# Narrower than this and the charges stop reading; wider is past the point where
# a sidebar logo is a sidebar. The ceiling is also what the original constant
# was, so nothing that fits today gets smaller for having been measured.
MIN_COLS, MAX_COLS = 16, 44

# Nothing to measure and nothing installed: 24 columns leaves an 80-column
# terminal the ~53 the default info block wants.
FALLBACK_COLS = 24


def visible_width(text):
    """Width of the widest line, ignoring colour."""
    lines = ANSI.sub("", text).splitlines()
    return max((len(line.rstrip()) for line in lines), default=0)


def _fastfetch(*args):
    """Run fastfetch and give back what it printed, or None if it cannot."""
    try:
        return subprocess.run(("fastfetch",) + args, capture_output=True,
                              text=True, timeout=10, check=True).stdout
    except (OSError, subprocess.SubprocessError):
        return None


def terminal_cols():
    """Columns of the terminal in front of the user, or None if there isn't one.

    A pipe or a GUI has no terminal to measure, and the 80-column default
    `shutil.get_terminal_size` substitutes would be a guess wearing a
    measurement's clothes -- so ask the streams directly, and let COLUMNS speak
    for anyone who exports it deliberately.
    """
    for stream in (2, 1):
        if os.isatty(stream):
            return shutil.get_terminal_size((0, 0)).columns or None
    try:
        return int(os.environ["COLUMNS"]) or None
    except (KeyError, ValueError):
        return None


def installed_cols(path):
    """Width of the logo already installed, or None if there isn't one.

    Whatever wrote that file last had a terminal to measure and this run does
    not, which makes it better evidence about the sidebar than any default.
    """
    try:
        return visible_width(path.read_text()) or None
    except OSError:
        return None


def measure():
    """(info block width, padding), or (None, None) if fastfetch cannot say.

    Padding comes from the gap between a full render and one with the logo
    suppressed, so a config that pads differently is accounted for without this
    having to read -- and parse the comments out of -- config.jsonc.
    """
    info = _fastfetch("--logo", "none")
    if info is None:
        return None, None
    info = visible_width(info)

    full = _fastfetch()
    logo = _fastfetch("--structure", "")   # logo alone, no modules
    if full is None or logo is None:
        return info, DEFAULT_PADDING

    padding = visible_width(full) - info - visible_width(logo)
    # A negative or absurd gap means one of the three renders measured something
    # this does not understand; the shipped padding is a better answer than a
    # width computed from it.
    return info, padding if 0 <= padding <= 16 else DEFAULT_PADDING


def fit(logo_path):
    """Logo width to install, fitted to the terminal it will be printed in."""
    cols = terminal_cols()
    info, padding = measure()

    if cols is None or info is None:
        kept = installed_cols(logo_path)
        if kept:
            return fit_cols(_clamp(kept), "kept from the installed logo "
                                          "(no terminal to measure)")
        return fit_cols(FALLBACK_COLS, "no terminal to measure")

    return fit_cols(_clamp(cols - info - padding - SAFETY),
                    "fitted to a %d-col terminal (%d info + %d padding + %d spare)"
                    % (cols, info, padding, SAFETY))


def _clamp(cols):
    return max(MIN_COLS, min(MAX_COLS, cols))
