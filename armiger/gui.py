"""GTK4/libadwaita front end for armiger.

The preview shows the braille art rather than the SVG on purpose: braille is
what actually gets installed, and the two differ (the SVG keeps Petra Sancta
hatching, the braille flattens to two tones). Previewing the prettier one would
be a promise the install cannot keep.
"""

import os
import pathlib
import random
import subprocess
import threading

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk  # noqa: E402

from .cli import (FASTFETCH_LOGO, SCREENSAVER, draw_at, generate, write)
from .draw import render

APP_ID = "org.omarchy.armiger"

# Preview width. Wider than the fastfetch default so the window shows detail,
# but each install target re-renders at its own width rather than scaling this.
PREVIEW_COLS = 30

# Braille only looks solid in a font whose dot glyphs are drawn to tile edge to
# edge; a generic monospace letter-spaces them and the fills read as a loose
# grid of dots instead of a filled area. Nerd Fonts draw them to tile, and
# JetBrainsMono is what Omarchy ships as its terminal default, so the preview
# matches what the art will look like where it ends up.
CSS = b"""
.arms {
  font-family: "JetBrainsMono Nerd Font", "JetBrainsMono NF", monospace;
  font-size: 15px;
  line-height: 1.0;
  padding: 12px;
}
.blazon { font-size: 15px; font-weight: 600; }
.seed { font-family: monospace; opacity: 0.6; font-size: 11px; }
"""


class ArmigerWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Armiger")
        self.set_default_size(560, 680)

        self.blazon = None
        self.busy = False

        self.toasts = Adw.ToastOverlay()
        view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        view.add_top_bar(header)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        # -- preview --
        frame = Gtk.Frame()
        frame.set_vexpand(True)
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.art = Gtk.Label(label="")
        self.art.add_css_class("arms")
        self.art.set_halign(Gtk.Align.CENTER)
        self.art.set_valign(Gtk.Align.CENTER)
        self.art.set_selectable(True)
        scroller.set_child(self.art)
        frame.set_child(scroller)
        box.append(frame)

        # -- blazon + seed --
        self.blazon_label = Gtk.Label(label="")
        self.blazon_label.add_css_class("blazon")
        self.blazon_label.set_wrap(True)
        self.blazon_label.set_justify(Gtk.Justification.CENTER)
        box.append(self.blazon_label)

        self.seed_label = Gtk.Label(label="")
        self.seed_label.add_css_class("seed")
        self.seed_label.set_selectable(True)
        box.append(self.seed_label)

        # -- theme --
        theme_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        theme_label = Gtk.Label(label="Theme")
        theme_label.set_xalign(0)
        theme_row.append(theme_label)
        self.theme_drop = Gtk.DropDown.new_from_strings(
            ["Both", "Medieval", "Cosmic"])
        self.theme_drop.set_hexpand(True)
        # Re-roll on change so the choice shows itself immediately rather than
        # waiting for the next press of Randomise.
        self.theme_drop.connect("notify::selected", lambda *_: self.roll(None))
        theme_row.append(self.theme_drop)
        box.append(theme_row)

        # -- seed entry, for reproducing arms --
        seed_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.seed_entry = Gtk.Entry()
        self.seed_entry.set_placeholder_text("Type a seed to reproduce arms…")
        self.seed_entry.set_hexpand(True)
        self.seed_entry.connect("activate", lambda *_: self.roll(self.seed_entry.get_text()))
        seed_row.append(self.seed_entry)
        box.append(seed_row)

        # -- actions --
        self.roll_btn = Gtk.Button(label="Randomise")
        self.roll_btn.add_css_class("suggested-action")
        self.roll_btn.add_css_class("pill")
        self.roll_btn.set_hexpand(True)
        self.roll_btn.connect("clicked", lambda *_: self.roll(None))
        box.append(self.roll_btn)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8,
                          homogeneous=True)
        self.ff_btn = Gtk.Button(label="Set fastfetch logo")
        self.ff_btn.connect("clicked", self.on_fastfetch)
        actions.append(self.ff_btn)

        self.ss_btn = Gtk.Button(label="Set screensaver")
        self.ss_btn.connect("clicked", self.on_screensaver)
        actions.append(self.ss_btn)

        self.svg_btn = Gtk.Button(label="Export SVG…")
        self.svg_btn.connect("clicked", self.on_export)
        actions.append(self.svg_btn)
        box.append(actions)

        # Installing screensaver branding can either write quietly or take over
        # the screen to show the result. Default to quiet; asking for the
        # preview should be deliberate.
        self.preview_check = Gtk.CheckButton(
            label="Show the screensaver right away after setting it")
        box.append(self.preview_check)

        view.set_content(box)
        self.toasts.set_child(view)
        self.set_content(self.toasts)

        self.roll(None)

    # -- helpers --

    def toast(self, text):
        self.toasts.add_toast(Adw.Toast(title=text))

    def set_busy(self, busy):
        self.busy = busy
        for b in (self.roll_btn, self.ff_btn, self.ss_btn, self.svg_btn):
            b.set_sensitive(not busy)
        self.roll_btn.set_label("Rolling…" if busy else "Randomise")

    # -- actions --

    def roll(self, seed):
        """Generate on a worker thread; the legibility gate can re-roll many
        times, and each attempt shells out to rsvg-convert and ImageMagick, so
        doing it on the main loop would freeze the window."""
        if self.busy:
            return
        self.set_busy(True)
        seed = seed or os.urandom(8).hex()

        theme = (None, "medieval", "cosmic")[self.theme_drop.get_selected()]

        def work():
            try:
                rng = random.Random(seed)
                blazon, art = generate(rng, PREVIEW_COLS, theme=theme)
                GLib.idle_add(self.show_result, blazon, art, seed)
            except Exception as exc:  # surface it rather than hanging on "Rolling…"
                GLib.idle_add(self.show_error, str(exc))

        threading.Thread(target=work, daemon=True).start()

    def show_result(self, blazon, art, seed):
        self.blazon = blazon
        self.art.set_text(art)
        self.blazon_label.set_text(blazon.describe())
        self.seed_label.set_text("seed: %s" % seed)
        self.seed_entry.set_text("")
        self.set_busy(False)
        return GLib.SOURCE_REMOVE

    def show_error(self, message):
        self.set_busy(False)
        self.toast("Could not render: %s" % message)
        return GLib.SOURCE_REMOVE

    def on_fastfetch(self, _btn):
        if not self.blazon:
            return
        # Re-rendered at the fastfetch width rather than reusing the preview:
        # the sidebar is narrower, and scaling braille art is not a thing.
        write(FASTFETCH_LOGO, draw_at(self.blazon, 22))
        self.toast("Set as fastfetch logo")

    def on_screensaver(self, _btn):
        if not self.blazon:
            return
        write(SCREENSAVER, draw_at(self.blazon, 56))
        self.toast("Set as screensaver branding")
        if self.preview_check.get_active():
            subprocess.run(["omarchy-launch-screensaver", "force"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           check=False)

    def on_export(self, _btn):
        if not self.blazon:
            return
        dialog = Gtk.FileDialog()
        dialog.set_initial_name("arms.svg")
        dialog.save(self, None, self._on_export_done)

    def _on_export_done(self, dialog, result):
        try:
            gfile = dialog.save_finish(result)
        except GLib.Error:
            return  # cancelled
        if not gfile:
            return
        path = pathlib.Path(gfile.get_path())
        path.write_text(render(self.blazon, spacing=5.0, stroke=1.1,
                               solid=False, size=900))
        self.toast("Saved %s" % path.name)


class ArmigerApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        win = self.props.active_window or ArmigerWindow(self)
        win.present()


def main():
    return ArmigerApp().run(None)


if __name__ == "__main__":
    raise SystemExit(main())
