"""Entry point.

Bare `hatchment` opens the window, because that is what someone typing the
program's name into a terminal almost always wants. Any argument means the
caller has something specific in mind, so it goes to the command line instead --
which also keeps `hatchment --help` and `hatchment --fastfetch` behaving the way
a shell user expects rather than opening a window and ignoring them.

Copyright (C) 2026 Caden DeNike. Free software under the GNU General
Public License, version 3 or later, with no warranty. See LICENSE.
"""

import sys


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv

    if argv and argv[0] == "--gui":
        argv = argv[1:]
    elif argv:
        from .cli import main as cli_main
        return cli_main(argv)

    try:
        from .gui import main as gui_main
    except Exception as exc:
        # GTK missing is the likely cause, and dying with a bare ImportError
        # traceback would not say so.
        print("Could not start the window: %s" % exc, file=sys.stderr)
        print("Install GTK4 and libadwaita (python-gobject gtk4 libadwaita), "
              "or use the command line: hatchment --help", file=sys.stderr)
        return 1
    return gui_main()


if __name__ == "__main__":
    raise SystemExit(main())
