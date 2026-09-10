"""GTK4/libadwaita front end for hatchment.

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

from . import theme
from .gloss import plain
from .cli import (FASTFETCH_COLS, FASTFETCH_LOGO, SCREENSAVER,
                  draw_at, generate, write)
from .draw import render

APP_ID = "org.omarchy.hatchment"


def _tiling_wm():
    """True when the compositor closes windows itself.

    Under a tiling compositor the client-side close button is dead weight: the
    window is closed with a keybinding, nothing is dragged by the titlebar, and
    the button is one more thing to mis-click. Hyprland is detected explicitly
    rather than "is this Wayland", because a floating Wayland desktop such as
    GNOME still wants its controls.
    """
    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        return True
    desktops = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    return any(w in desktops for w in ("hyprland", "sway", "river", "niri"))

# Preview width. Wider than the fastfetch default so the window shows detail,
# but each install target re-renders at its own width rather than scaling this.
PREVIEW_COLS = 30

# Braille only looks solid in a font whose dot glyphs are drawn to tile edge to
# edge; a generic monospace letter-spaces them and the fills read as a loose
# grid of dots instead of a filled area. Nerd Fonts draw them to tile, and
# JetBrainsMono is what Omarchy ships as its terminal default, so the preview
# matches what the art will look like where it ends up.
BASE_CSS = """
.arms {
  font-family: "JetBrainsMono Nerd Font", "JetBrainsMono NF", monospace;
  font-size: 15px;
  line-height: 1.0;
  padding: 12px;
}
.blazon { font-size: 15px; font-weight: 600; }
.gloss { font-size: 12px; opacity: 0.72; font-style: italic; }
.seed { font-family: monospace; opacity: 0.6; font-size: 11px; }
"""


USER_GTK_CSS = pathlib.Path.home() / ".config/gtk-4.0/gtk.css"


def _user_stylesheet_themes_gtk():
    """True when something already re-tints GTK from the Omarchy theme.

    Omarchy installs a `theme-set` hook that renders ~/.config/gtk-4.0/gtk.css
    from the active palette on every theme change, so GTK apps follow the theme
    with no help from us. GTK loads that file at USER priority, above an
    application provider, so our named colours would lose to it anyway -- and
    should: it deliberately gives windows alpha 0.78 to sit over the wallpaper,
    which a flat opaque override would trample.
    """
    try:
        return "@define-color window_bg_color" in USER_GTK_CSS.read_text()
    except OSError:
        return False


def build_css(colours):
    """Base styling, the accent for the art, and a palette fallback.

    The art's colour is ours to set in every case: it is a plain label, so
    without a rule it takes the window foreground, and the accent is the whole
    point of asking. The named colours below are only a fallback for systems
    with no retint hook -- where one exists, it wins and is better.
    """
    css = BASE_CSS
    if not colours:
        return css.encode()

    if _user_stylesheet_themes_gtk():
        accent = colours.get("accent")
        if accent:
            css += "\n.arms { color: %s; }\n" % accent
        return css.encode()

    def c(key, fallback=None):
        return colours.get(key, fallback)

    bg = c("background")
    fg = c("foreground")
    accent = c("accent")
    card = c("lighter_background", bg)
    # Text sitting *on* the accent needs to contrast with it, and the darkest
    # background in the palette is the safest bet in a dark theme -- the
    # foreground is usually close to the accent in brightness.
    on_accent = c("dark_background", bg)

    defs = []
    if bg:
        defs += [f"@define-color window_bg_color {bg};",
                 f"@define-color view_bg_color {bg};",
                 f"@define-color headerbar_bg_color {bg};",
                 f"@define-color popover_bg_color {card};",
                 f"@define-color dialog_bg_color {bg};"]
    if fg:
        defs += [f"@define-color window_fg_color {fg};",
                 f"@define-color view_fg_color {fg};",
                 f"@define-color headerbar_fg_color {fg};",
                 f"@define-color popover_fg_color {fg};",
                 f"@define-color dialog_fg_color {fg};"]
    if card:
        defs.append(f"@define-color card_bg_color {card};")
    if accent:
        defs += [f"@define-color accent_bg_color {accent};",
                 f"@define-color accent_color {accent};"]
        if on_accent:
            defs.append(f"@define-color accent_fg_color {on_accent};")
        # The art itself takes the accent: it is the one element on screen that
        # is purely decorative, so it can carry the theme's loudest colour.
        css += "\n.arms { color: %s; }\n" % accent

    return ("\n".join(defs) + "\n" + css).encode()


class HatchmentWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Hatchment")
        self.set_default_size(560, 680)

        self.blazon = None
        self.busy = False

        self.toasts = Adw.ToastOverlay()
        view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        if _tiling_wm():
            header.set_show_end_title_buttons(False)
            header.set_show_start_title_buttons(False)
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

        self.gloss_label = Gtk.Label(label="")
        self.gloss_label.add_css_class("gloss")
        self.gloss_label.set_wrap(True)
        self.gloss_label.set_justify(Gtk.Justification.CENTER)
        box.append(self.gloss_label)

        self.seed_label = Gtk.Label(label="")
        self.seed_label.add_css_class("seed")
        self.seed_label.set_selectable(True)
        box.append(self.seed_label)

        # -- theme --
        theme_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        theme_label = Gtk.Label(label="Theme")
        theme_label.set_xalign(0)
        theme_row.append(theme_label)
        # Alphabetical after the first entry, which is the "no filter" option
        # and belongs at the top rather than sorted in among the filters.
        self.theme_drop = Gtk.DropDown.new_from_strings(
            ["All", "Cosmic", "Fractal", "Geometric", "Medieval", "Natural"])
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
        self.svg_btn.connect("clicked", self.on_export, "svg")
        actions.append(self.svg_btn)

        self.png_btn = Gtk.Button(label="Export PNG…")
        self.png_btn.connect("clicked", self.on_export, "png")
        actions.append(self.png_btn)
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
        for b in (self.roll_btn, self.ff_btn, self.ss_btn, self.svg_btn,
                  self.png_btn):
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

        theme = (None, "cosmic", "fractal", "geometric", "medieval",
                 "natural")[self.theme_drop.get_selected()]

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
        gloss = plain(blazon)
        self.gloss_label.set_text('\u201c%s\u201d' % gloss if gloss else "")
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
        write(FASTFETCH_LOGO, draw_at(self.blazon, FASTFETCH_COLS))
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

    def on_export(self, _btn, fmt="svg"):
        """Save the arms as vector or raster.

        Both export the *hatched* drawing rather than the braille: at file
        resolution there are pixels enough for Petra Sancta tinctures, so an
        exported coat of arms says which colour each tincture is, which the
        two-tone braille cannot.
        """
        if not self.blazon:
            return
        dialog = Gtk.FileDialog()
        dialog.set_initial_name("arms.%s" % fmt)
        # The button chosen decides the format, so the callback is told which
        # one rather than guessing from whatever the user types in the box.
        dialog.save(self, None, lambda d, r: self._on_export_done(d, r, fmt))

    def _on_export_done(self, dialog, result, fmt):
        try:
            gfile = dialog.save_finish(result)
        except GLib.Error:
            return  # cancelled
        if not gfile:
            return

        path = pathlib.Path(gfile.get_path())
        # Writing SVG bytes into a name ending .png would be a file that lies
        # about itself, so the extension is made to match what was written.
        if path.suffix.lower() != "." + fmt:
            path = path.with_suffix("." + fmt)

        svg = render(self.blazon, spacing=5.0, stroke=1.1, solid=False, size=900)
        if fmt == "svg":
            path.write_text(svg)
        else:
            try:
                png = subprocess.run(
                    ["rsvg-convert", "-w", "1024", "--background-color", "white",
                     "-f", "png"],
                    input=svg.encode(), capture_output=True, check=True).stdout
            except (OSError, subprocess.CalledProcessError) as exc:
                self.toast("Could not write PNG: %s" % exc)
                return
            path.write_bytes(png)
        self.toast("Saved %s" % path.name)


class HatchmentApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self):
        self.provider = None
        self.apply_theme()
        self.watch_theme()
        win = self.props.active_window or HatchmentWindow(self)
        win.present()

    def apply_theme(self):
        """Install a *fresh* provider each time rather than reloading one.

        `@define-color` values are resolved into the cascade when a provider is
        parsed, and reloading the same provider in place does not re-resolve
        what already depends on them: the plain rules update, the named colours
        do not, and the window ends up half in the new theme and half in the
        old. Removing the provider and adding a new one invalidates the lot.
        """
        colours = theme.palette()
        display = Gdk.Display.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_data(build_css(colours))
        if self.provider is not None:
            Gtk.StyleContext.remove_provider_for_display(display, self.provider)
        Gtk.StyleContext.add_provider_for_display(
            display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.provider = provider
        # Tell libadwaita which way round the palette is, so the widgets it
        # styles without our named colours still land on the right side.
        style = Adw.StyleManager.get_default()
        style.set_color_scheme(
            Adw.ColorScheme.FORCE_DARK if theme.is_dark(colours)
            else Adw.ColorScheme.FORCE_LIGHT)

    def watch_theme(self):
        """Re-tint when the Omarchy theme changes underneath us.

        Two files are watched, because `omarchy theme set` and `omarchy theme
        refresh` touch different ones: the first rewrites theme.name, the second
        only rewrites the palette in place. Watching the state directory itself
        would be simpler but reports every file the switch rewrites, which is
        dozens of events for one change.
        """
        self._monitors = []
        for path in (theme.NAME, theme.COLORS):
            try:
                gfile = Gio.File.new_for_path(str(path))
                monitor = gfile.monitor_file(Gio.FileMonitorFlags.NONE, None)
            except GLib.Error:
                continue
            monitor.connect("changed", self._on_theme_changed)
            self._monitors.append(monitor)

    def _on_theme_changed(self, _monitor, _f, _other, event):
        if event in (Gio.FileMonitorEvent.CHANGES_DONE_HINT,
                     Gio.FileMonitorEvent.CREATED,
                     Gio.FileMonitorEvent.MOVED_IN):
            # A theme switch rewrites several files; coalesce the burst so the
            # CSS is rebuilt once rather than per file.
            if getattr(self, "_retint_pending", False):
                return
            self._retint_pending = True
            GLib.timeout_add(150, self._retint)

    def _retint(self):
        self._retint_pending = False
        self.apply_theme()
        return GLib.SOURCE_REMOVE


def main():
    return HatchmentApp().run(None)


if __name__ == "__main__":
    raise SystemExit(main())
