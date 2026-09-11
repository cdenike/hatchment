"""Wear the arms as the Omarchy menu button.

The button at the left end of the bar is a glyph -- `text: "\\ue900"` in
Omarchy's icon font -- so there is no icon path to point at and nothing in
shell.json to override. What the bar does support is third-party widgets, so
this installs one: a widget that draws an image and, when pressed, runs the
same two commands Omarchy's own menu button runs.

The Omarchy menu plugin itself is left enabled and untouched. Its manifest sets
keepLoaded, so the menu is still there to be summoned even when its bar widget
is not in the layout -- which is why this only has to replace the button.

Nothing here is destructive: the swap is one id in the bar layout, restore()
puts the original back, and uninstall() removes the plugin directory as well.
"""

import json
import os
import pathlib
import shutil
import subprocess
import tempfile

from .draw import render

PLUGIN_ID = "hatchment.menu"
OMARCHY_ID = "omarchy.menu"

CONFIG = pathlib.Path.home() / ".config/omarchy"
SHELL_JSON = CONFIG / "shell.json"
PLUGIN_DIR = CONFIG / "plugins" / PLUGIN_ID
ICON = PLUGIN_DIR / "arms.png"

# Rendered well above bar size: the widget asks for twice the device pixel
# ratio, and a shield resampled down stays crisp where one scaled up does not.
ICON_PX = 256

MANIFEST = {
    "schemaVersion": 1,
    "id": PLUGIN_ID,
    "name": "Hatchment menu",
    "version": "1.0.0",
    "author": "hatchment",
    "license": "MIT",
    "description": "The Omarchy menu button, wearing the current coat of arms",
    "kinds": ["bar-widget"],
    "entryPoints": {"barWidget": "BarWidget.qml"},
    "barWidget": {
        "displayName": "Hatchment menu",
        "description": "Opens the Omarchy menu; shows the arms hatchment installed",
        "category": "Custom",
        "allowMultiple": False,
        "defaultSection": "left",
    },
}

# `source` is relative to this file, so the widget has no path to get wrong and
# the plugin directory can be moved or copied to another machine intact.
# cache is off because the file is replaced in place on every install: a cached
# copy would leave the bar wearing the previous roll's arms.
BAR_WIDGET = '''import QtQuick
import qs.Ui

// Written by hatchment. Edits here are replaced the next time arms are set.
BarWidget {
  id: root
  moduleName: "%(id)s"

  readonly property real barSize: bar ? bar.barSize : 26
  readonly property real iconSize: Math.round(barSize * 0.64)

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: ""
    // The button sizes itself from its label and hides when it has none, so an
    // icon-only button has to say it has something to show and how wide it is.
    hasVisualContent: true
    fixedWidth: root.iconSize + 15
    tooltipText: "Omarchy menu"

    onPressed: function(which) {
      if (!root.bar) return
      if (which === Qt.RightButton) root.bar.run("xdg-terminal-exec")
      else root.bar.run("omarchy-shell shell toggle omarchy.menu '{\\"menu\\":\\"root\\"}'")
    }

    Image {
      anchors.centerIn: parent
      width: root.iconSize
      height: root.iconSize
      source: "arms.png"
      sourceSize.width: Math.round(root.iconSize * Screen.devicePixelRatio * 2)
      fillMode: Image.PreserveAspectFit
      asynchronous: true
      cache: false
      smooth: true
    }
  }
}
''' % {"id": PLUGIN_ID}


def available():
    """True when there is an Omarchy shell config to install into."""
    return SHELL_JSON.is_file()


def _layout(cfg):
    return (cfg.get("bar") or {}).get("layout") or {}


def active():
    """True when the bar is currently wearing the arms."""
    try:
        cfg = json.loads(SHELL_JSON.read_text())
    except (OSError, ValueError):
        return False
    return any(w.get("id") == PLUGIN_ID
               for widgets in _layout(cfg).values() for w in widgets)


def _write_shell_json(cfg):
    """Replace shell.json atomically, in the shape the rest of the system writes.

    The shell hot-reloads this file, so a partially written one would be read
    mid-write. Indent and key order match what omarchy's own writers produce
    (`jq -S --indent 2`), so this does not churn the file's formatting back and
    forth with them.
    """
    tmp = tempfile.NamedTemporaryFile("w", dir=str(SHELL_JSON.parent),
                                      prefix=".shell.json.", delete=False)
    try:
        json.dump(cfg, tmp, indent=2, sort_keys=True)
        tmp.write("\n")
        tmp.close()
        os.replace(tmp.name, SHELL_JSON)
    except BaseException:
        pathlib.Path(tmp.name).unlink(missing_ok=True)
        raise


def _swap(old_id, new_id, insert_section="left"):
    """Rename one widget id in the bar layout, or add it if it is not there."""
    cfg = json.loads(SHELL_JSON.read_text())
    layout = _layout(cfg)
    for widgets in layout.values():
        for widget in widgets:
            if widget.get("id") == old_id:
                widget["id"] = new_id
                _write_shell_json(cfg)
                return True
    if any(w.get("id") == new_id for ws in layout.values() for w in ws):
        return False                      # already there; nothing to do
    layout.setdefault(insert_section, []).insert(0, {"id": new_id})
    _write_shell_json(cfg)
    return True


def _rescan():
    """Ask the shell to pick up a plugin directory it has not seen before."""
    try:
        subprocess.run(["omarchy-shell", "shell", "rescanPlugins"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=10, check=False)
    except (OSError, subprocess.SubprocessError):
        pass                              # the bar reloads on its own soon enough


def write_icon(blazon):
    """Render the arms to the plugin's icon file.

    Solid rather than hatched, and on nothing rather than on white: hatching is
    mush at 17 pixels, and a white ground would put a pale square on the bar
    instead of a shield.
    """
    svg = render(blazon, solid=True, size=ICON_PX, ground=None)
    png = subprocess.run(["rsvg-convert", "-w", str(ICON_PX), "-f", "png"],
                         input=svg.encode(), capture_output=True,
                         check=True).stdout
    PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
    ICON.write_bytes(png)


def install(blazon):
    """Put the arms on the bar. Returns what happened, for the caller to report."""
    PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
    (PLUGIN_DIR / "manifest.json").write_text(json.dumps(MANIFEST, indent=2) + "\n")
    (PLUGIN_DIR / "BarWidget.qml").write_text(BAR_WIDGET)
    write_icon(blazon)
    swapped = _swap(OMARCHY_ID, PLUGIN_ID)
    _rescan()
    return "menu icon set" if swapped else "menu icon updated"


def restore():
    """Put Omarchy's own menu button back."""
    if not active():
        return "menu icon was not set"
    _swap(PLUGIN_ID, OMARCHY_ID)
    _rescan()
    return "Omarchy menu icon restored"


def uninstall():
    """Omarchy's button back, and the widget plugin removed with it."""
    result = restore()
    if PLUGIN_DIR.exists():
        shutil.rmtree(PLUGIN_DIR)
        _rescan()                         # so the shell forgets the plugin too
        if result == "menu icon was not set":
            result = "menu icon plugin removed"
    return result
