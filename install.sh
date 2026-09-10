#!/bin/bash
# Install hatchment for the current user: no root, nothing outside $HOME.
#
# Everything lands under the XDG user directories, so the desktop entry and the
# icon are picked up by any freedesktop-compliant launcher -- the Omarchy menu
# included -- without touching /usr.

set -euo pipefail

REPO="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"

mkdir -p "$BIN_DIR" "$APP_DIR" "$ICON_DIR"

echo "==> Launcher: $BIN_DIR/hatchment"
# The repo path is baked in rather than installed into site-packages, so the
# command always runs the checkout you installed from -- pull the repo and the
# command updates with it, with no reinstall step to forget.
cat > "$BIN_DIR/hatchment" <<EOF
#!/bin/bash
export PYTHONPATH="$REPO\${PYTHONPATH:+:\$PYTHONPATH}"
exec python3 -m hatchment "\$@"
EOF
chmod +x "$BIN_DIR/hatchment"

echo "==> Icon: $ICON_DIR/hatchment.svg"
install -m644 "$REPO/data/hatchment.svg" "$ICON_DIR/hatchment.svg"

echo "==> Desktop entry: $APP_DIR/hatchment.desktop"
cat > "$APP_DIR/hatchment.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Hatchment
GenericName=Coat of Arms Generator
Comment=Generate a random coat of arms for fastfetch and the screensaver
Exec=$BIN_DIR/hatchment --gui
Icon=hatchment
Terminal=false
Categories=Graphics;2DGraphics;
Keywords=heraldry;coat of arms;shield;blazon;fastfetch;screensaver;
StartupNotify=true
StartupWMClass=org.omarchy.hatchment
EOF

# Launchers cache both of these; without a refresh a fresh install can take a
# session restart to show up.
if command -v update-desktop-database >/dev/null; then
  update-desktop-database "$APP_DIR" 2>/dev/null || true
fi
if command -v gtk-update-icon-cache >/dev/null; then
  gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi

echo
echo "Installed."

# A launcher on a PATH the user does not have is the commonest way this looks
# broken, so say so rather than leaving them to find out.
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) echo "WARNING: $BIN_DIR is not on your PATH."
     echo "         Add it to your shell profile, or the 'hatchment' command"
     echo "         will not be found:"
     echo "           export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
esac

echo
echo "  hatchment              open the window"
echo "  hatchment --help       command line options"
echo
echo "It should also appear in your app launcher as \"Hatchment\"."
