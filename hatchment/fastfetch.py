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
import pathlib
import re
import subprocess
import time

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

# Narrower than this and the charges stop reading. The ceiling is the size of
# the logo Omarchy itself ships -- its about.txt is 45 columns by 26 rows -- so
# a terminal with room lands on stock size rather than under it, and nothing
# that fits today gets smaller for having been measured.
MIN_COLS, MAX_COLS = 16, 45

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

    Each stream is measured through the descriptor that was found to be a
    terminal, not through shutil, which always measures stdout however it was
    asked. The documented way to run this -- `hatchment --fastfetch --quiet
    >/dev/null` from a shell profile -- redirects stdout and keeps stderr on the
    terminal, which is precisely the case shutil gets wrong.
    """
    for fd in (2, 1):
        if os.isatty(fd):
            try:
                return os.get_terminal_size(fd).columns or None
            except OSError:
                continue
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


def measure(logo_path):
    """(info block width, padding), or (None, None) if fastfetch cannot say.

    Padding is what is left of a full render once the info block and the logo
    are accounted for, so a config that pads differently is handled without
    reading -- and parsing the comments out of -- config.jsonc.

    The logo's own width is taken from the file rather than from a second
    render. Asking fastfetch to draw the logo alone looked like the tidier
    answer, but `--structure ""` renders every module anyway, which made the
    subtraction nonsense and quietly fell back to the default -- a default that
    matched the truth on the config it was written against, so the mistake was
    invisible until the padding changed.
    """
    info = _fastfetch("--logo", "none")
    if info is None:
        return None, None
    info = visible_width(info)

    full = _fastfetch()
    logo = installed_cols(logo_path)
    if full is None or logo is None:
        return info, DEFAULT_PADDING

    padding = visible_width(full) - info - logo
    # Out of range means the widest line was not one with both a logo and info
    # on it -- art taller than the info block, most likely -- so the shipped
    # padding is a better answer than a width derived from it.
    return info, padding if 0 <= padding <= 16 else DEFAULT_PADDING


def fit(logo_path):
    """Logo width to install, fitted to the terminal it will be printed in."""
    cols = terminal_cols()
    info, padding = measure(logo_path)

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


# Omarchy's own config, from the omarchy-settings package. fastfetch reads it
# whenever there is no config in ~/.config/fastfetch -- and a stock Omarchy has
# none there -- so it is both what "Omarchy's fastfetch" means and the template
# for pointing fastfetch at the arms without disturbing anything else about it.
USER_CONFIG = pathlib.Path.home() / ".config/fastfetch/config.jsonc"
SYSTEM_CONFIG = pathlib.Path("/etc/fastfetch/config.jsonc")
STOCK_SOURCE = '"source": "~/.config/omarchy/branding/about.txt"'


def _source_for(logo_path):
    """The logo path as config.jsonc would spell it, with ~ for home."""
    try:
        return "~/" + str(logo_path.relative_to(pathlib.Path.home()))
    except ValueError:
        return str(logo_path)


def wired(logo_path):
    """True when the user's fastfetch config shows this logo."""
    try:
        text = USER_CONFIG.read_text()
    except OSError:
        return False
    return _source_for(logo_path) in text or str(logo_path) in text


def wire(logo_path):
    """Point fastfetch at the arms, where that needs no one's config edited.

    With no config of the user's own -- a stock Omarchy, or one hatchment has
    reset -- Omarchy's is copied into place with the single line naming the logo
    changed, so the layout stays exactly as Omarchy ships it. A config the user
    wrote is theirs: it is not edited, and they are told the one line to change.

    Returns a note worth showing, or None when there was nothing to say.
    """
    if wired(logo_path):
        return None
    source = _source_for(logo_path)
    if USER_CONFIG.exists():
        return ("your fastfetch config shows another logo; set its logo "
                "source to %s to see the arms" % source)
    try:
        stock = SYSTEM_CONFIG.read_text()
    except OSError:
        return "no fastfetch config to point at the arms; see the README"
    if stock.count(STOCK_SOURCE) != 1:
        return ("Omarchy's fastfetch config is not the shape expected; set "
                "its logo source to %s by hand" % source)
    USER_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    USER_CONFIG.write_text(stock.replace(STOCK_SOURCE, '"source": "%s"' % source))
    return "fastfetch now shows the arms"


def unwire(logo_path):
    """Hand fastfetch back to Omarchy's own config. Returns (changed, message).

    Only a config that shows the arms is moved, and only aside: it exists
    because of hatchment, and without it fastfetch falls back to Omarchy's in
    /etc/fastfetch. A config showing anything else is the user's business.
    """
    if not USER_CONFIG.exists():
        return False, "fastfetch was already Omarchy's"
    if not wired(logo_path):
        return False, "your fastfetch config does not show the arms; left alone"
    backup = USER_CONFIG.with_name("%s.bak.%d" % (USER_CONFIG.name, time.time()))
    USER_CONFIG.rename(backup)
    return True, "fastfetch restored to Omarchy's config (yours kept as %s)" % backup.name


def install(logo_path, draw):
    """Wire fastfetch, then write the logo at the width there is room for.

    `draw` renders the arms at a given width. Returns (size, note).

    Measured a second time when the first measurement had no logo to go on.
    Padding comes from a full render with a logo in it, so with none installed
    yet -- a fresh install, or the first set after a reset -- the first fit uses
    a guessed padding, and Omarchy's own config pads more than the guess. Once
    a logo exists the second fit measures the real padding, and a logo at the
    wrong width is redrawn at the right one.
    """
    note = wire(logo_path)
    size = fit(logo_path)
    _write(logo_path, draw(size.cols))
    again = fit(logo_path)
    if again.cols != size.cols:
        _write(logo_path, draw(again.cols))
        size = again
    return size, note


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n")
