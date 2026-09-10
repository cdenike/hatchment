# hatchment

Procedural heraldry for the terminal. Rolls a random coat of arms, renders it as
braille art, and hangs it in your fastfetch logo and your Omarchy screensaver.

```
$ hatchment --cols 24 --seed house-03
Per fess sable and or, a mullet or

⢰⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⡆
⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⢸⣿⣿⣿⣿⣿⣿⣿⣿⣷⡄  ⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⡇
⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⣴⣦⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⢸⡛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⢛⡇
⠸⡇                    ⢸⠇
 ⢷                    ⡾
 ⠈⣧                  ⡼⠁
  ⠈⢷⡀              ⢀⡾⠁
    ⠙⢦⡀          ⢀⡴⠋
      ⠙⠶⣄⡀    ⢀⣠⠶⠋
        ⠈⠙⠓⠶⠶⠚⠋⠁
```

## Why it looks like that

Heraldry is a constraint system, not a pile of random shapes, so `hatchment`
generates the way a herald designs: pick a field, divide it *or* lay an ordinary
across it, then charge it — checking the **rule of tincture** at every step
(never metal on metal, never colour on colour). That rule exists to keep arms
legible at a distance, which turns out to be the same problem as keeping them
legible at 48 dots across.

Three constraints fall out of the target rather than the tradition:

- **A divided field never takes an ordinary.** The rule of tincture makes a
  divided field one metal and one colour, so an ordinary laid across it
  contrasts with exactly one half and disappears against the other. Heraldry
  answers this by counterchanging along the division; that needs more resolution
  than a braille cell has, so `hatchment` declines the combination instead.
- **A centred charge never sits on a divided field.** Per pale and per bend run
  straight through the fess point and per chevron meets there, so a charge in the
  middle is half on each tincture and vanishes into one of them. Per fess and per
  pale leave a whole half in one flat tincture, and a charge goes *there*.
- **Contrast is judged against whatever is actually underneath.** A chief sits at
  the top of the shield while a charge sits at the fess point, so colouring the
  charge against the chief lands it metal-on-metal in the field.

## Tinctures, and where they go

The SVG export uses **Petra Sancta hatching** — vertical rules for gules,
horizontal for azure, dots for or — the convention engravers have used to encode
colour in one ink since the 1630s.

The braille output does not. Hatching was tried, rasterised crisply at dot
resolution rather than downsampled, and measured: any hatch period coarse enough
to survive a braille cell is coarse enough to read as graph paper, and the
ordinary and charge stop separating from the field. Braille output flattens to
two tones instead. It loses *which* colour a tincture is and keeps the shapes,
which is the right trade when the shapes are all a 24-column shield can carry.

## Patterns, furs and themes

### Variations of the field

Instead of a flat ground, a shield may carry a repeating two-tincture pattern:
**barry**, **paly**, **bendy**, **checky**, **lozengy**, **gyronny** and
**chevronny**. These are the best thing in the whole vocabulary for this target
— already two-tone by definition, so nothing is lost flattening them, and the
repeat gives texture that hatching could never survive at this size.

A variation stands alone. It alternates metal and colour across the entire
shield, so an ordinary or a centred charge has no single tincture beneath it —
the divided-field problem, everywhere at once.

### Furs

**Ermine** (white strewn with black tails), **counter-ermine** (its inverse) and
**vair** (interlocking bells). Furs are the third class of tincture alongside
metals and colours, and the most medieval thing you can put on a shield. Unlike
a variation a fur behaves as an ordinary ground, so it takes charges normally —
ermine counts as a metal for contrast, counter-ermine as a colour.

Furs survive the two-tone flattening untouched: they were always black and
white, so there is nothing to lose.

### Themes

```bash
hatchment --theme cosmic      # the themes are alphabetical throughout
hatchment --theme fractal
hatchment --theme geometric
hatchment --theme medieval
hatchment --theme natural
```

Themes filter the charge table; they do not add a separate vocabulary, because
heraldry already had both registers.

- **Medieval** — tower, sword, key, crown, portcullis, chalice, fleur-de-lis,
  billet, banner, and rearing lion and horse
- **Cosmic** — sun in splendour, estoile, comet, increscent, orb, mullet,
  crescent, annulet, eagle
- **Natural** — garb (a wheatsheaf), tree, rose, trefoil, attires (a pair of
  antlers borne without the stag), stag, bee, fish, horse, lion, eagle
- **Fractal** — Sierpinski gasket, Sierpinski carpet, Vicsek fractal, Koch
  snowflake, mandala, nested polygons, H-tree, Cantor bars, flower of life,
  recursive circles
- **Geometric** — concentric rings, compass spokes, triangular tessellation,
  nested squares, hexagonal grid, star polygon, diagonal lattice, square grid,
  sunburst, moiré rings

Ten of each, and each is a *family* rather than a picture: every generator draws
its own depth, count, rotation, phase and mode from the roll's rng, so the same
name gives a different figure every time. Star polygons vary their {n/k}
schläfli pair, the square grid switches between chequer, outline and dots, the
Sierpinski gasket inverts. The parameters are pinned to a seed stored on the
arms, because the same arms get rendered at three different widths and have to
come out the same picture each time.

The last two are **not heraldry and do not pretend to be** — no herald ever
blazoned a Sierpinski gasket. They treat the shield as a frame for a pattern,
and take nothing else: an ordinary or a charge over a fractal is noise on noise.
Recursion depth is capped low, because at 50-110 dots across a fourth or fifth
subdivision stops being a pattern and turns grey.

Every one of them is tuned to clear the legibility gate. Three did not at first
(`concentric rings`, `nested lozenges`, `nested squares`) and would simply never
have appeared: filling alternate rings puts over half the shield under ink. They
are outlines now, with only the innermost shape solid.

Choosing a theme also changes the *shape* of the arms, not just the charges: a
themed roll keeps variations rare and favours arrangements that can carry a
charge. Otherwise picking "cosmic" would happily hand you a barry field with
nothing cosmic anywhere on it.

**All** rolls a mode per shield rather than simply not filtering. That is the
only way the pattern themes appear in it at all — fractals and geometrics are
gated on the theme name, so an unfiltered roll could never reach them however
long it ran. The modes are the five themes plus *free*, which is unfiltered
heraldry; free is kept as its own mode because a theme suppresses variations and
furs to make room for its charges, and without it barry, checky and ermine would
nearly vanish from the one setting meant to show everything.

Measured over 48 rolls of All: 18 charged arms, 10 geometric patterns, 9
variations, 6 fractals, 5 plain.

### Lines of partition

Every division and every band can be cut with a shaped edge instead of a
straight one — **wavy**, **engrailed**, **indented**, **dancetty**,
**embattled**, **nebuly**. This is the cheapest variety in the whole system:
six edge treatments multiplying every division and every band, before a charge
is placed.

Amplitudes are deliberately larger than a herald would draw. At 24 columns the
shield is 48 dots across, so a wave one unit deep is half a dot and simply
disappears; these are sized to survive being thresholded to 1-bit, not to look
correct on parchment. A cross or a saltire stays straight — styling every arm
is more geometry than it earns at this size.

### Beasts and banners

`lion` and `horse` rearing, `eagle` displayed, and a `banner` whose fly ripples.
These are complexity 4, which means they only appear at **26 columns or wider**:
below roughly 50 dots across a beast stops reading as an animal and becomes a
blot, so the generator is restricted to shapes whose silhouette survives —
stars, crescents, towers — rather than being allowed to pick a lion and produce
mush. The fastfetch logo renders at 30 columns, so they show up there.

## Plain language

The blazon is technical Norman-French word order. Under it, in quotes, the same
arms as an ordinary sentence:

```
Per pale nebuly vert and argent, a sun in splendour or
"Green on the left, silver on the right along a cloud-shaped edge, with a gold sun"
```

The language follows the user's locale (`LC_ALL`, `LC_MESSAGES`, then `LANG`).
Only English ships. The glossary is one table per language, so adding one is
data rather than code — but shipping translations that cannot be checked would
be worse than shipping none, so `LANGS` has a single entry and everything else
falls back to English.

## How much room there is

Measured, not estimated: **120 consecutive rolls produce 117 distinct blazons**,
with every feature class represented and none rejected by the legibility gate.

The vocabulary the roll draws from:

| | |
|---|---|
| Divisions | 7 — per pale, fess, bend, bend sinister, chevron, saltire, quarterly |
| Ordinaries | 16 — including bordure, orle, canton, gyron, pile, pall, and doubled bars |
| Variations | 7 |
| Lines of partition | 6 |
| Charges | 30, in counts of 1, 2, 3, 4 or 5, in four arrangements |
| Semé | 12 charges strewn across the field |
| Patterns | 20 fractal and geometric, each parameterised |
| Tinctures | 7 plus 3 furs |

Two of those do most of the widening. **Semé** — a field strewn with a small
charge repeated to the edges — multiplies by the charge list rather than adding
to it. And a **bordure** sits round the rim touching nothing else, so unlike
every other element it can go on top of whatever was built first, which is
exactly why real heraldry uses it to difference one branch of a family from
another.

Semé always takes a light ground. Flattened to two tones a colour field is solid
black and the strewn charges become white holes in it: legible in principle,
over the gate's ink ceiling in practice, so it would have been rolled and thrown
away every single time.

## Graphical interface

```bash
hatchment
```

A GTK4/libadwaita window: **Randomise** to roll, then **Set fastfetch logo** or
**Set screensaver** to install the arms in front of you. **Export SVG…** saves
the hatched vector. Type a seed to reproduce arms you liked, and setting the
screensaver only takes over the screen if you tick the box.

It ships a desktop entry, so it also shows up in the app launcher.

Under a tiling compositor — Hyprland, Sway, river, niri — the window drops its
client-side titlebar buttons. Nothing is dragged by the titlebar there and the
window is closed with a keybinding, so a close button is dead weight and one
more thing to mis-click. Floating desktops keep theirs.

Two things worth knowing about the preview:

- It shows the **braille**, not the SVG. The two genuinely differ — the SVG keeps
  its hatching, the braille flattens to two tones — and previewing the prettier
  one would be a promise the install cannot keep.
- Braille looks **dottier in the window than in your terminal**. Terminals
  synthesise braille cells as solid blocks; GTK draws the font's actual dot
  glyphs. Same characters, same file, different rasteriser.

### Following the Omarchy theme

The window follows the active Omarchy theme, and re-tints live when it changes —
no restart.

Most of that is not this app's doing, and shouldn't be. Omarchy ships a
`theme-set` hook that renders `~/.config/gtk-4.0/gtk.css` from the active
theme's `colors.toml` on every change, so *every* GTK app already follows the
theme; GTK loads that file at USER priority, above anything an application sets
for itself. Hatchment detects that stylesheet and stays out of its way — including
leaving its deliberate alpha alone, so the window sits over the wallpaper like
the rest of the desktop rather than punching an opaque rectangle through it.

What the app does set is the **arms' colour**, taken from the theme's `accent`.
The art is a plain label, so with no rule it would inherit the window foreground
and read as ordinary text. It is the one purely decorative thing on screen, so
it gets the loudest colour in the palette.

Where no retint hook exists, the app falls back to applying the palette to
libadwaita's named colours itself, so it still matches on a bare system.

Two details that cost a debugging round each, recorded so they don't again:

- **Reloading a `Gtk.CssProvider` in place does not re-resolve `@define-color`.**
  The plain rules update and the named colours do not, leaving the window half
  in the new theme and half in the old. Removing the provider and adding a fresh
  one invalidates everything properly.
- **The palette is under `current/theme/colors.toml`**, while `theme.name` sits
  beside it in `current/`. Both are watched, because `omarchy theme set` and
  `omarchy theme refresh` touch different ones.

## Usage

```bash
hatchment                          # roll and print
hatchment --seed my-house          # reproducible arms
hatchment --cols 32                # wider
hatchment --simple                 # simplest charges only
hatchment --svg arms.svg           # hatched vector export
hatchment --fastfetch              # install as the fastfetch logo
hatchment --screensaver            # install as screensaver branding
hatchment --screensaver --no-reload  # ...without taking the screen
```

Every roll prints its seed, so arms you like can be recovered exactly.

### Wiring it into fastfetch

`--fastfetch` writes `~/.config/fastfetch/coat-of-arms.txt`. Point fastfetch at
it once:

```jsonc
"logo": {
  "type": "file",
  "source": "~/.config/fastfetch/coat-of-arms.txt"
}
```

### Wiring it into the Omarchy screensaver

`--screensaver` writes `~/.config/omarchy/branding/screensaver.txt`, which is the
same file `omarchy branding screensaver` manages, rendered wider since the
screensaver has more room than a fastfetch sidebar. Without `--no-reload` it
also runs `omarchy-launch-screensaver force`, which puts the screensaver on
screen immediately so you can see the result.

New arms every login, if you want them — add to your shell profile:

```bash
hatchment --fastfetch --quiet >/dev/null
```

## Legibility gate

Arms are re-rolled until the render lands between 10% and 52% of dots set.
This biases the mix: variations clear the gate every time while other forms sit
around 63-75%, so variations end up commoner among survivors (~36%) than the
26% they are rolled at.
Outside that band the shield has either collapsed to near-empty or filled in
solid, and neither is worth installing. The measurement counts *dots*, not
cells: a cell-based count calls any textured area full, which is exactly the
distinction the gate exists to catch.

## Install

### Arch, as a real package

```bash
git clone https://github.com/cdenike/hatchment.git
cd hatchment/packaging/aur
makepkg -si
```

This builds and installs a proper pacman package — `pacman -Qi hatchment` will
find it, and `pacman -R hatchment` removes it cleanly. The AUR is only an index
that hosts PKGBUILDs; the PKGBUILD here is the same one, so nothing is lost by
fetching it from this repository instead.

### Anywhere else, or without root

```bash
git clone https://github.com/cdenike/hatchment.git
cd hatchment
./install.sh
```

No root, nothing outside `$HOME`. It puts a launcher in `~/.local/bin`, the icon
in `~/.local/share/icons/hicolor/scalable/apps`, and a desktop entry in
`~/.local/share/applications`, then refreshes the desktop and icon caches so a
fresh install shows up without a session restart. The launcher points at the
checkout you installed from, so `git pull` updates the command with no reinstall.

Afterwards:

- **`hatchment`** opens the window
- **`hatchment --help`** and any other argument runs the command line
- **Hatchment** appears in your app launcher, Omarchy's menu included

## Requirements

- Python 3.9+, standard library only
- `rsvg-convert` (librsvg) — the one external program, ~10 MiB
- GTK4 and libadwaita, for the window only; the command line needs neither

That is the whole dependency list. Thresholding the rasteriser's output to 1-bit
used to be a second call out to **ImageMagick** — 21.8 MiB of dependency, and a
process spawn on every render, to compare bytes against a number. It is ~90
lines of `zlib` and `struct` instead: parse IHDR, concatenate IDAT, inflate,
undo the five scanline filters, threshold. Dropping it made rendering **3.7×
faster** (27 ms → 7.3 ms per shield) and halved what has to be installed.

The replacement was checked against the thing it replaced rather than assumed
equivalent: 190 renders across every theme and all three output widths,
byte-identical. The first attempt was *not* — an exclusive comparison inked
0-126 where ImageMagick inks 0-127, which shifted every anti-aliased edge pixel
by one level and changed the outline of most shields.

Rendering large and downsampling is what ruins this kind of art: a one-pixel
rule resampled to a fraction of a pixel turns grey, and thresholding grey against
a regular grid produces moiré. `rsvg-convert` places the marks on whole dots.

## Credits

The braille packing follows the approach in Caden's `make-logo.py`, which got
the cell geometry right: a braille cell is 2 dots wide by 4 tall, terminal cells
are about 8.5×16px, and the dot grid needs correcting for that.

## Licence

MIT.
