"""Put back what hatchment changed, the way Omarchy ships it.

Hatchment dresses three things, and each has a stock form Omarchy itself
defines -- so the defaults are always read from Omarchy, never from a copy kept
here that would drift from the real thing:

- the screensaver art is $OMARCHY_PATH/logo.txt, which is exactly what
  `omarchy branding screensaver reset` copies into place;
- fastfetch is Omarchy's /etc/fastfetch/config.jsonc, which applies whenever
  there is no config in ~/.config/fastfetch -- Omarchy ships none there, so a
  user config showing the arms is the whole of the change (hatchment.fastfetch);
- the menu button is omarchy.menu in the bar layout, with hatchment's widget
  plugin gone (hatchment.menuicon).

Nothing the user might want back is thrown away. A screensaver or fastfetch
config that is not already stock is moved aside under Omarchy's own backup
name, `.bak.<seconds>` -- the convention omarchy-refresh-config uses -- so a
reset can be undone by hand. Only the menu plugin is deleted outright: it is
hatchment's own generated files, and setting the icon again recreates them.
"""

import os
import pathlib
import time

from . import fastfetch, menuicon

OMARCHY_PATH = pathlib.Path(os.environ.get("OMARCHY_PATH", "/usr/share/omarchy"))
STOCK_SCREENSAVER = OMARCHY_PATH / "logo.txt"


def available():
    """True when there is an Omarchy install to take the defaults from."""
    return STOCK_SCREENSAVER.is_file() or menuicon.available()


def _screensaver(path):
    if not STOCK_SCREENSAVER.is_file():
        return False, "no Omarchy logo to restore the screensaver from"
    stock = STOCK_SCREENSAVER.read_bytes()
    if path.is_file() and path.read_bytes() == stock:
        return False, "screensaver was already Omarchy's"
    if path.exists():
        path.rename(path.with_name("%s.bak.%d" % (path.name, time.time())))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(stock)
    return True, "screensaver restored to the Omarchy logo"


def _menu_button():
    if not menuicon.available():
        return False, "no Omarchy bar to restore"
    changed = menuicon.active() or menuicon.PLUGIN_DIR.exists()
    return changed, menuicon.uninstall()


def reset(fastfetch_logo, screensaver_art):
    """Put all three back. Returns (name, changed, message) for each, in order."""
    return [
        ("screensaver",) + _screensaver(screensaver_art),
        ("fastfetch",) + fastfetch.unwire(fastfetch_logo),
        ("menu button",) + _menu_button(),
    ]
