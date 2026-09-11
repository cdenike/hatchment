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
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Pango  # noqa: E402

from . import fastfetch, menuicon, prompt, screensaver, stock, theme
from .gloss import plain
from .cli import (FASTFETCH_LOGO, SCREENSAVER,
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

# The history thumbnails. Twelve columns is seven rows of braille: enough for
# the silhouette, the division or ordinary across it, and roughly what is on it.
# Seven columns was tried first and is genuinely too small -- 14 dots across
# cannot hold an interior, and the shield's own outline falls below one dot and
# vanishes, so light arms lost their edge and dark ones became a blot.
# Rendering them is another rsvg call per roll, so it happens on the worker
# thread with the preview rather than while a menu is opening.
THUMB_COLS = 12

# How many rolls the menu remembers. Long enough to get back to the one you
# liked three rolls ago, short enough that the popover is a list rather than a
# scrollback.
HISTORY_MAX = 24

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
.prompt-note { opacity: 0.7; font-size: 12px; }
.thumb {
  font-family: "JetBrainsMono Nerd Font", "JetBrainsMono NF", monospace;
  font-size: 9px;
  line-height: 1.0;
}
.history-blazon { font-size: 13px; }
.history-empty { opacity: 0.6; padding: 12px; }
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


def build_css(colours, generic=False):
    """Base styling, the accent for the art, and a palette fallback.

    The art's colour is ours to set in every case: it is a plain label, so
    without a rule it takes the window foreground, and the accent is the whole
    point of asking. The named colours below are only a fallback for systems
    with no retint hook -- where one exists, it wins and is better.

    `generic` says the palette is the app's own rather than the system's, which
    happens on a machine with no Omarchy theme to read. Then the window also
    gets a border in the accent: with a theme, the desktop is already saying
    where this window ends, and with none it has to say so itself.
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
        if generic:
            css += ("\nwindow.background {"
                    " border: 1px solid %s; border-radius: 12px; }\n" % accent)

    return ("\n".join(defs) + "\n" + css).encode()


class HatchmentWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Hatchment")
        self.set_default_size(560, 680)

        self.blazon = None
        self.busy = False
        self._focus_before_busy = None

        self.toasts = Adw.ToastOverlay()
        view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        header.pack_start(self._build_history_button())
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

        # -- description: arms from a few words --
        # A description is a standing instruction, like the theme: while it is
        # there, every roll honours it and varies only what it leaves open, so
        # Randomise gives another take on the same arms. Clearing it goes back
        # to rolling freely.
        prompt_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.prompt_entry = Gtk.Entry()
        self.prompt_entry.set_placeholder_text(
            "Describe your arms — e.g. three gold lions on red, a blue border")
        self.prompt_entry.set_tooltip_text(
            "Whatever you name is kept; the rest is rolled. Randomise keeps "
            "using the description until you clear it.")
        self.prompt_entry.set_hexpand(True)
        self.prompt_entry.set_icon_from_icon_name(
            Gtk.EntryIconPosition.SECONDARY, "edit-clear-symbolic")
        self.prompt_entry.set_icon_tooltip_text(
            Gtk.EntryIconPosition.SECONDARY, "Clear, and roll freely again")
        self.prompt_entry.connect("icon-press", self._clear_prompt)
        self.prompt_entry.connect("activate", lambda *_: self.roll(None))
        prompt_row.append(self.prompt_entry)
        self.prompt_btn = Gtk.Button(label="Create")
        self.prompt_btn.connect("clicked", lambda *_: self.roll(None))
        prompt_row.append(self.prompt_btn)
        box.append(prompt_row)

        # What the description could not be held to, said plainly: a word
        # hatchment does not know, a colour with nowhere to go.
        self.prompt_note = Gtk.Label(label="")
        self.prompt_note.add_css_class("prompt-note")
        self.prompt_note.set_wrap(True)
        self.prompt_note.set_xalign(0)
        self.prompt_note.set_visible(False)
        box.append(self.prompt_note)

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

        # Installing and exporting are different kinds of act -- one dresses the
        # desktop, the other hands you a file -- and five buttons in one
        # homogeneous row leaves each too narrow to read its own label.
        self.menu_btn = Gtk.Button(label="Set menu icon")
        self.menu_btn.connect("clicked", self.on_menu_icon)
        if not menuicon.available():
            self.menu_btn.set_sensitive(False)
            self.menu_btn.set_tooltip_text(
                "Needs an Omarchy shell config at ~/.config/omarchy/shell.json")
        actions.append(self.menu_btn)
        box.append(actions)

        exports = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8,
                          homogeneous=True)
        self.svg_btn = Gtk.Button(label="Export SVG…")
        self.svg_btn.connect("clicked", self.on_export, "svg")
        exports.append(self.svg_btn)

        self.png_btn = Gtk.Button(label="Export PNG…")
        self.png_btn.connect("clicked", self.on_export, "png")
        exports.append(self.png_btn)
        box.append(exports)

        # Installing screensaver branding can either write quietly or take over
        # the screen to show the result. Default to quiet; asking for the
        # preview should be deliberate.
        self.preview_check = Gtk.CheckButton(
            label="Show the screensaver right away after setting it")
        box.append(self.preview_check)

        # Undoing all three installs is rarer than any of them and reaches
        # further, so it sits apart below everything and asks before it acts.
        # Flat, so it does not compete with Randomise for the eye.
        self.stock_btn = Gtk.Button(label="Restore Omarchy defaults…")
        self.stock_btn.add_css_class("flat")
        self.stock_btn.add_css_class("destructive-action")
        self.stock_btn.connect("clicked", self.on_stock)
        if not stock.available():
            self.stock_btn.set_sensitive(False)
            self.stock_btn.set_tooltip_text(
                "Needs an Omarchy install to take the defaults from")
        box.append(self.stock_btn)

        view.set_content(box)
        self.toasts.set_child(view)
        self.set_content(self.toasts)

        self.roll(None)

    # -- history --

    def _build_history_button(self):
        """The Recent menu: every roll this session, newest first.

        A roll is cheap to look at and expensive to reproduce -- you cannot get
        back to arms you liked unless you noted the seed, and nobody notes the
        seed before they know they liked it. So the window keeps them.
        """
        self.history = []
        self.history_list = Gtk.ListBox()
        self.history_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.history_list.connect("row-activated", self.on_history_row)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_min_content_width(360)
        scroller.set_max_content_height(400)
        scroller.set_propagate_natural_height(True)
        # Without this the scroller offers its minimum width, and the row's
        # first child -- the thumbnail -- is what gets squeezed out of it.
        scroller.set_propagate_natural_width(True)
        scroller.set_child(self.history_list)

        self.history_pop = Gtk.Popover()
        self.history_pop.set_child(scroller)

        button = Gtk.MenuButton(label="Recent")
        button.set_tooltip_text("Arms rolled this session")
        button.set_popover(self.history_pop)
        self.history_btn = button
        self._rebuild_history()
        return button

    def _remember(self, blazon, art, seed, thumb, text, gloss, prompt_text="",
                  notes=()):
        self.history.insert(0, {"blazon": blazon, "art": art, "seed": seed,
                                "thumb": thumb, "text": text, "gloss": gloss,
                                "prompt": prompt_text, "notes": list(notes)})
        del self.history[HISTORY_MAX:]
        self._rebuild_history()

    def _rebuild_history(self):
        """Rebuild the whole list rather than diffing it.

        It is at most HISTORY_MAX rows and only changes once per roll, so the
        bookkeeping a diff would need costs more than the rebuild it saves.
        """
        while True:
            child = self.history_list.get_first_child()
            if child is None:
                break
            self.history_list.remove(child)

        self.history_btn.set_sensitive(bool(self.history))
        if not self.history:
            label = Gtk.Label(label="Nothing rolled yet")
            label.add_css_class("history-empty")
            row = Gtk.ListBoxRow()
            row.set_activatable(False)
            row.set_child(label)
            self.history_list.append(row)
            return

        for entry in self.history:
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            box.set_margin_top(6)
            box.set_margin_bottom(6)
            box.set_margin_start(8)
            box.set_margin_end(8)

            thumb = Gtk.Label(label=entry["thumb"].rstrip("\n"))
            thumb.add_css_class("thumb")
            thumb.set_valign(Gtk.Align.CENTER)
            # Reserve the shield's full width, so a long blazon beside it
            # cannot push the picture down to a sliver.
            thumb.set_width_chars(THUMB_COLS)
            thumb.set_xalign(0)
            box.append(thumb)

            # The blazon alone. The seed is what reproduces arms, not what
            # identifies them to a reader, and a row that has to be read at a
            # glance should carry the name rather than the serial number -- the
            # seed is still on the window once a row is picked.
            blazon_label = Gtk.Label(label=entry["text"])
            blazon_label.add_css_class("history-blazon")
            blazon_label.set_xalign(0)
            blazon_label.set_hexpand(True)
            blazon_label.set_valign(Gtk.Align.CENTER)
            blazon_label.set_wrap(True)
            blazon_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            blazon_label.set_lines(2)
            blazon_label.set_ellipsize(Pango.EllipsizeMode.END)
            blazon_label.set_max_width_chars(32)
            box.append(blazon_label)

            row = Gtk.ListBoxRow()
            row.set_child(box)
            self.history_list.append(row)

    def on_history_row(self, _list, row):
        """Bring a past roll back as the current arms.

        The art is the one rendered when it was rolled, not a fresh render:
        re-deriving it would shell out again for a picture already in hand, and
        the gate can re-roll, so a regenerated shield might not even match.
        """
        index = row.get_index()
        if not (0 <= index < len(self.history)):
            return
        entry = self.history[index]
        self.history_pop.popdown()
        self.blazon = entry["blazon"]
        self.art.set_text(entry["art"])
        self.blazon_label.set_text(entry["text"])
        self.gloss_label.set_text(entry["gloss"])
        self.seed_label.set_text("seed: %s" % entry["seed"])
        self.seed_entry.set_text("")
        # The description comes back with the arms: it and the seed together
        # are what reproduce them, and the next roll should honour it again.
        self.prompt_entry.set_text(entry.get("prompt", ""))
        self._show_notes(entry.get("notes", ()))

    # -- helpers --

    def toast(self, text):
        self.toasts.add_toast(Adw.Toast(title=text))

    def _show_notes(self, notes):
        self.prompt_note.set_text("\n".join(n[0].upper() + n[1:] for n in notes))
        self.prompt_note.set_visible(bool(notes))

    def _clear_prompt(self, entry, *_):
        entry.set_text("")
        self._show_notes(())

    def set_busy(self, busy):
        """Disable the buttons for the duration of a roll, and keep the focus.

        Disabling the focused widget takes focus off it, and the next focusable
        thing in this window is the art label -- which is selectable, so it can
        hold focus, and a focused selectable label draws a text caret at the
        start of its text. That caret lands against the shield's top-left
        corner and reads as a rendering fault: it appeared on launch, because
        the window rolls once on startup, and came back on every roll after.
        """
        self.busy = busy
        if busy:
            self._focus_before_busy = self.get_focus()
        for b in (self.roll_btn, self.ff_btn, self.ss_btn, self.menu_btn,
                  self.svg_btn, self.png_btn, self.stock_btn, self.prompt_btn):
            b.set_sensitive(not busy
                            and (b is not self.menu_btn or menuicon.available())
                            and (b is not self.stock_btn or stock.available()))
        self.roll_btn.set_label("Rolling…" if busy else "Randomise")
        if not busy:
            # Back where it was -- unless that was the art label, or nothing,
            # or something still disabled. The seed entry is never disabled, so
            # someone who typed a seed and pressed Enter keeps their cursor.
            target = self._focus_before_busy
            if target is None or target is self.art or not target.get_sensitive():
                target = self.roll_btn
            target.grab_focus()

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
        text = self.prompt_entry.get_text().strip()
        wishes = prompt.parse(text) if text else None
        notes = wishes.notes if wishes else []

        def work():
            try:
                rng = random.Random(seed)
                blazon, art = generate(rng, PREVIEW_COLS, theme=theme,
                                       wishes=wishes)
                # Rendered here rather than when the menu opens: it is another
                # rsvg call, and a popover that shells out while it animates
                # stutters.
                thumb = draw_at(blazon, THUMB_COLS)
                GLib.idle_add(self.show_result, blazon, art, seed, thumb,
                              text, notes)
            except BaseException as exc:  # never leave the UI stuck on "Rolling…"
                GLib.idle_add(self.show_error, str(exc))

        threading.Thread(target=work, daemon=True).start()

    def show_result(self, blazon, art, seed, thumb="", text="", notes=()):
        """Put a finished roll on screen.

        Everything here is wrapped, and set_busy(False) is in a finally, because
        this runs inside a GLib idle callback: an exception raised here does not
        propagate anywhere useful, it just abandons the rest of the function.
        When that included re-enabling the buttons, one missing glossary entry
        left every control disabled and the window looking hung -- which is
        exactly what happened.
        """
        try:
            self.blazon = blazon
            self.art.set_text(art)
            self.blazon_label.set_text(blazon.describe())
            try:
                gloss = plain(blazon)
            except Exception:
                gloss = None       # decoration; never worth failing a roll over
            self.gloss_label.set_text("\u201c%s\u201d" % gloss if gloss else "")
            self.seed_label.set_text("seed: %s" % seed)
            self.seed_entry.set_text("")
            self._show_notes(notes)
            self._remember(blazon, art, seed, thumb, blazon.describe(),
                           self.gloss_label.get_text(), text, notes)
        except Exception as exc:
            self.toast("Could not display arms: %s" % exc)
        finally:
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
        blazon = self.blazon
        size, note = fastfetch.install(FASTFETCH_LOGO,
                                       lambda cols: draw_at(blazon, cols))
        self.toast("Set as fastfetch logo (%s)" % size)
        if note:
            self.toast(note[0].upper() + note[1:])

    def on_menu_icon(self, _btn):
        """Put the current arms on the Omarchy menu button.

        Always sets rather than toggling: the button is next to the other two
        install buttons and should mean what they mean, and a control that
        removed the icon on a second press would fight the obvious way of
        keeping the bar in step with a new roll. `--menu-icon-off` undoes it.
        """
        if not self.blazon or not menuicon.available():
            return
        try:
            result = menuicon.install(self.blazon)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            self.toast("Could not set the menu icon: %s" % exc)
            return
        self.toast(result.capitalize())

    def on_screensaver(self, _btn):
        if not self.blazon:
            return
        # Sized to the screen rather than to a constant: see hatchment.screensaver.
        size = screensaver.fit()
        write(SCREENSAVER, draw_at(self.blazon, size.cols))
        # The preview goes before the toast deliberately. Anything raised in a
        # GTK callback abandons the rest of the function without propagating
        # anywhere useful, so the part the user actually asked for must not sit
        # behind a decorative one -- which is exactly how a formatting error in
        # the toast came to look like a broken preview button.
        if self.preview_check.get_active():
            try:
                subprocess.run(["omarchy-launch-screensaver", "force"],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, check=False)
            except OSError:
                self.toast("Could not launch the screensaver")
                return
        self.toast("Set as screensaver branding (%s)" % size)

    def on_stock(self, _btn):
        """Ask, then put back Omarchy's screensaver, fastfetch and menu button.

        Asks because it undoes three things at once and a click is easy to
        make; says which three because "defaults" on its own does not.
        """
        dialog = Adw.AlertDialog(
            heading="Restore Omarchy defaults?",
            body="The screensaver goes back to the Omarchy logo, fastfetch "
                 "back to Omarchy's own config, and the menu button back to "
                 "Omarchy's. The screensaver art and fastfetch config you have "
                 "now are kept beside the originals as .bak files.")
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("restore", "Restore")
        dialog.set_response_appearance("restore",
                                       Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        dialog.connect("response", self._on_stock_response)
        dialog.present(self)

    def _on_stock_response(self, _dialog, response):
        if response != "restore":
            return
        try:
            results = stock.reset(FASTFETCH_LOGO, SCREENSAVER)
        except (OSError, subprocess.SubprocessError) as exc:
            self.toast("Could not restore the defaults: %s" % exc)
            return
        changed = [name for name, did, _ in results if did]
        # Same rule as setting the screensaver: take the screen only if asked.
        if "screensaver" in changed and self.preview_check.get_active():
            try:
                subprocess.run(["omarchy-launch-screensaver", "force"],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, check=False)
            except OSError:
                pass
        if not changed:
            self.toast("Already on Omarchy's defaults")
            return
        names = (", ".join(changed[:-1]) + " and " + changed[-1]
                 if len(changed) > 1 else changed[0])
        self.toast("Restored Omarchy's %s" % names)

    def on_export(self, _btn, fmt="svg"):
        """Save the arms as vector or raster.

        Both export the arms in heraldic colour rather than the braille. The
        export used to be Petra Sancta hatching, and hatching breaks up on a
        patterned field: rings, fractals and semé are finer than any hatch
        spacing that reads, so each shape caught a fragment of a line and the
        lines stopped meeting. Flat colour has no spacing to fall between.
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

        svg = render(self.blazon, colour=True, size=900)
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
        colours, generic = theme.effective_palette()
        display = Gdk.Display.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_data(build_css(colours, generic))
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
