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

Exports are in **heraldic colour** — gules red, azure blue, or gold — as flat
fills. `--hatched` draws the SVG in **Petra Sancta hatching** instead — vertical
rules for gules, horizontal for azure, dots for or — the convention engravers
have used to encode colour in one ink since the 1630s. It suits plain arms, but
on a patterned field the shapes are finer than any hatch spacing that reads:
each ring or fractal cell catches a fragment of a line, and the lines stop
meeting. Flat colour has no spacing to fall between, which is why it is the
default.

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
hatchment --theme mythic
hatchment --theme natural
```

Themes filter the charge table; they do not add a separate vocabulary, because
heraldry already had both registers.

- **Medieval** — tower, sword, key, crown, portcullis, chalice, fleur-de-lis,
  billet, banner, rearing lion and horse, and the tools and emblems of the
  period: anchor, axe, hammer, anvil, bell, horseshoe, wheel, harp, bugle horn,
  arrow, helm, lymphad (a galley), book, hourglass, scales, heart, open hand,
  cross patée, cross crosslet
- **Cosmic** — sun in splendour, estoile, comet, increscent, orb, mullet,
  crescent, annulet, eagle, ringed planet, compass rose, yin and yang, and the
  zodiac's ram, bull, crab and scorpion

### Poses and forms

Most charges can be drawn more than one way, and heraldry names the ways: a
lion **rampant**, **passant** (walking), **sejant** (sitting), **couchant**
(lying) or just a **lion's head**; a horse rearing, walking, galloping or its
head; a stag standing, leaping, **lodged** or its head **caboshed**; an eagle
displayed, **close**, rising or **double-headed**. Wolves, bears, boars, bulls,
rams, hounds, hares, unicorns, pegasi and dragons (and the **wyvern**) have
theirs; so do fish, serpents (**nowed**, or the ouroboros) and ravens.

Things have forms: pine, palm and uprooted trees; the scimitar and the sword
inverted; mural, eastern and royal crowns; the castle; the covered cup, the
fouled anchor, the Catherine wheel, the **pheon**, the Norman helm, the
sailing ship, the closed book, the pennon; the flaming heart, the skull and
crossbones, the eye of providence, the double axe, Thor's hammer; the cross
**moline**, **fleury**, **bottony**, **potent**, Celtic, Latin and Maltese;
six- and eight-pointed and pierced mullets; the triquetra and the triskelion
of three legs. The cosmic register has the sun in glory, with a face or
eclipsed; the decrescent and the full moon; the streaming comet; the armillary
sphere; the planet with moons; the compass star — and two more charges, the
spiral galaxy and the constellation.

The first form of each is the one it always had, and needs no word: "a lion
or" is rampant. Others name themselves — "a lion passant or" — and a
description can ask for one: *a walking lion*, *a lion's head*, *a palm tree*,
*a Celtic cross*, *three flying ravens*.

### Seeds from earlier versions

A seed carries the vocabulary it was made in, by its length. Seeds from before
0.1.8 are sixteen hex digits, and 0.1.8's are eighteen; each still rolls from
the charges and patterns of its time, so arms you kept the seed of come back
the same. New seeds are twenty digits and draw on everything, poses and forms
included.
- **Natural** — garb (a wheatsheaf), tree, rose, trefoil, attires (a pair of
  antlers borne without the stag), stag, bee, fish, horse, lion, eagle, wolf,
  bear, boar, fox, bull, ram, hare, hound, elephant, owl, raven, swan, martlet
  (the heraldic swallow), cockerel, butterfly, bat, spider, scorpion, serpent,
  frog, tortoise, crab, dolphin, escallop (a scallop shell), mountain, cloud,
  acorn, oak leaf, thistle, bunch of grapes
- **Mythic** — dragon, griffin, unicorn, phoenix, pegasus, with the serpent,
  wolf, raven, owl and bat, and the older symbols: eye, skull, flame,
  thunderbolt, triskele, Bowen knot, ankh
- **Fractal** — Sierpinski gasket, Sierpinski carpet, Vicsek fractal, Koch
  snowflake, mandala, nested polygons, H-tree, Cantor bars, flower of life,
  recursive circles, dragon curve, Hilbert curve, Lévy curve, Gosper curve,
  Pythagoras tree, branching tree, Apollonian gasket, T-square, pentaflake,
  hexaflake
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
mush. Whether they can appear in your fastfetch logo therefore depends on your
terminal: the logo is sized to the room beside the info block, so a wide
terminal gets beasts and a narrow sidebar gets towers and stars.

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

Measured, not estimated, and measured at a scale where collisions can actually
show up:

| rolls | distinct blazons | |
|---|---|---|
| 120 | **120** | every one different |
| 1,000 | **967** | 96.7% |
| 5,000 | **4,110** | 82.2% |
| 20,000 | **11,834** | 59.2% |

Every feature class is represented and none of it costs legibility: across 200
gated rolls, not one ended outside the ink band, which is the gate giving up.

The vocabulary the roll draws from:

| | |
|---|---|
| Divisions | 7 — per pale, fess, bend, bend sinister, chevron, saltire, quarterly |
| Ordinaries | 16 — including bordure, orle, canton, gyron, pile, pall, and doubled bars |
| Variations | 7, in 17 counted forms — barry of six, eight or ten, gyronny of eight or twelve |
| Lines of partition | 6 |
| Charges | 30, in counts of 1, 2, 3, 4 or 5, in four arrangements |
| Semé | 14 charges strewn across the field |
| Patterns | 20 fractal and geometric, each parameterised and each naming its parameter |
| Tinctures | 7 plus 3 stains, plus 3 furs |

Three things widened it most recently. The **stains** — murrey, sanguine and
tenné — are later and rarer than the core five tinctures but perfectly real, and
each one multiplies every choice ever made against a colour: field, ordinary,
charge, bordure, and the second half of a division. They are held to a minority
of colour rolls, because arms where a stain is as likely as gules stop reading
as heraldry.

**Variations count their pieces.** A barry of six and a barry of ten are not the
same arms and heraldry says so in the blazon, so the count is rolled per shield
and named — except for checky and lozengy, which ordinary usage names without a
count, so theirs varies the drawing without pretending the words changed.

**Patterns name their own parameter.** A mandala of six petals and one of
sixteen were always different pictures; now they are different words too. The
figure is not asked twice: the generator records what it rolled, and the blazon
replays it from the same seed the drawing will use, so the number named is the
number drawn rather than a second guess kept in a table. That one change did
most of the work — the pattern themes went from 316 distinct blazons in 5,000
rolls to 1,197 and 1,638.

What was deliberately *not* added: more lines of partition. The list stops at
six for the same reason `invected` is defined but never rolled — mirrored
scallops are a real distinction on parchment and an invisible one at 48 dots
across, and a vocabulary that grows without the picture changing is a longer
list, not more arms.

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
**Set screensaver** to install the arms in front of you. **Export SVG…** and
**Export PNG…** save the arms in full heraldic colour. Type a seed to reproduce
arms you liked, and setting the screensaver only takes over the screen if you
tick the box. **Restore Omarchy defaults…**, at the bottom, undoes all three
installs after asking — see [Back to stock](#back-to-stock).

**Describe your arms** takes a few words — *three gold lions on red, a blue
border* — and makes arms from them; see [Describing your arms](#describing-your-arms).
While a description is in the box, **Randomise** keeps to it and varies only
what it leaves open. Clear it to roll freely again.

It ships a desktop entry, so it also shows up in the app launcher.

Under a tiling compositor — Hyprland, Sway, river, niri — the window drops its
client-side titlebar buttons. Nothing is dragged by the titlebar there and the
window is closed with a keybinding, so a close button is dead weight and one
more thing to mis-click. Floating desktops keep theirs.

Two things worth knowing about the preview:

- It shows the **braille**, not the SVG. The two genuinely differ — the export is in
  colour, the braille flattens to two tones — and previewing the prettier
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

## Describing your arms

A description names what you want; anything it does not name is rolled. It
reads plain English and heraldry alike — *three gold lions on red* and
*Gules, three lions or* make the same arms.

```text
three gold lions on red, a blue border
a black eagle on a silver field
quartered red and gold with a white star
blue strewn with gold stars
red and white stripes
a wavy green band on white
a gold and blue mandala
something cosmic in blue and silver
```

- **Colours** — plain or heraldic: red or gules, blue or azure, gold or or,
  silver or white or argent, black or sable, green or vert, purple or purpure,
  plus orange (tenné), mulberry (murrey), blood red (sanguine), and the furs
  ermine, counter-ermine and vair.
- **Charges** — lions, eagles, stags, horses, fish, bees, trees, roses, clover,
  towers, swords, keys, crowns, cups, banners, gates, wheatsheaves, antlers,
  stars, moons, suns, comets, orbs, fleurs-de-lis, and plain shapes: discs,
  rings, diamonds, rectangles. Say how many — *a*, *two*, *three*, up to five.
- **Ordinaries** — a cross, a diagonal cross (saltire), a band across (fess)
  or down (pale), a diagonal band (bend), a chevron, a band across the top
  (chief), a corner square (canton), an inner border (orle), a border.
- **Fields** — split vertically, horizontally or diagonally, quartered;
  stripes, checkered, diamond pattern, pinwheel; *strewn with* a small charge.
- **Edges** — wavy, scalloped, zigzag, crenellated, cloudy.
- **Themes and patterns** — cosmic, medieval, natural, fractal, geometric, or a
  pattern by name: mandala, sunburst, snowflake, flower of life, honeycomb…

A colour belongs to whatever it sits next to: *gold lion* and *a lion or* both
colour the lion, *on red* colours the field, and *red and white stripes*
colours both halves. Anything left uncoloured is given a tincture that stands
out against what is under it.

It is a phrase reader, not a language model: offline, instant, and the same
words with the same seed always make the same arms. What it cannot use, it
says under the box — a word it does not know (with a suggestion if one is
close), two colours that break the rule of tincture, a sixth lion. Colour on
colour is drawn as asked; it shows in a colour export but merges in the
terminal's two tones, and the note says so.

## Usage

```bash
hatchment                          # roll and print
hatchment --seed my-house          # reproducible arms
hatchment --prompt "three gold lions on red, a blue border"   # describe them
hatchment --cols 32                # wider
hatchment --simple                 # simplest charges only
hatchment --svg arms.svg           # full-colour vector export
hatchment --svg arms.svg --hatched # ...in one-ink engraver's hatching
hatchment --fastfetch              # install as the fastfetch logo
hatchment --screensaver            # install as screensaver branding
hatchment --screensaver --no-reload  # ...without taking the screen
hatchment --menu-icon              # wear the arms as the Omarchy menu button
hatchment --menu-icon-off          # put Omarchy's own button back
hatchment --stock                  # put back all three, as Omarchy ships them
```

Every roll prints its seed, so arms you like can be recovered exactly.

### Wiring it into fastfetch

`--fastfetch` writes `~/.config/fastfetch/coat-of-arms.txt`, sized to the room
your terminal actually has: the logo shares its lines with the info block, so
the width is `terminal - info - padding`, less one spare column. All three are
measured rather than assumed — `fastfetch --logo none` renders the info block on
its own, and the gap between that and a full render is the padding, so a config
that pads differently is accounted for without parsing `config.jsonc`.

Run it from the terminal you actually use for fastfetch — that is the one it
measures. Run from a pipe or from the GUI, where there is no terminal to ask, it
keeps the width of the logo already installed, on the grounds that whatever
wrote that file last did have one; failing that it uses 24 columns, which leaves
an 80-column terminal enough for the default info block.

If you have no fastfetch config of your own — and Omarchy ships none in
`~/.config/fastfetch`, using `/etc/fastfetch/config.jsonc` instead — setting the
logo points fastfetch at it for you: Omarchy's config is copied into place with
the one line naming the logo changed, and the rest of the layout kept exactly as
Omarchy ships it. A config of your own is never edited; point it at the arms
yourself:

```jsonc
"logo": {
  "type": "file",
  "source": "~/.config/fastfetch/coat-of-arms.txt"
}
```

### Wiring it into the Omarchy screensaver

`--screensaver` writes `~/.config/omarchy/branding/screensaver.txt`, which is the
same file `omarchy branding screensaver` manages, rendered to fit the screen it
will actually appear on — the shield takes about 60% of the screen's height, and
where there are several monitors the smallest one decides, since every
screensaver window reads this one file. Without `--no-reload` it
also runs `omarchy-launch-screensaver force`, which puts the screensaver on
screen immediately so you can see the result.

The terminal it will be shown in does not exist yet at that point, so asking how
big it is would measure the wrong window: the grid is worked out from the
monitor geometry instead, against the 18pt font `omarchy-launch-screensaver`
pins for the screensaver in all four terminals it supports. With no compositor
to ask, it falls back to 24 columns, which fits the shortest screen this is
likely to run on. Art that is a little small is a modest shield on a wide
screen; art that is taller than the terminal is clipped, and ttfx then has
nothing left to centre.

### Wearing the arms on the bar

`--menu-icon` puts the arms on the button at the left end of the Omarchy bar,
where the Omarchy mark normally sits. In the window it is the **Set menu icon**
button, beside the other two install buttons.

That button is a glyph — `text: "\ue900"` in Omarchy's icon font — so there is
no icon path to point at and nothing in `shell.json` to override. What the bar
does support is third-party widgets, so this installs one:
`~/.config/omarchy/plugins/hatchment.menu/`, holding a manifest, a small
`BarWidget.qml` that draws an image, and the arms as a PNG. Setting the icon
again just replaces the PNG.

The Omarchy menu plugin is left enabled and untouched. Its manifest sets
`keepLoaded`, so the menu is still there to be summoned even with its own bar
widget out of the layout — which is why the replacement button only has to run
the same two commands the original does: the menu on left click, a terminal on
right click.

The whole change to your config is one id in the bar layout,
`omarchy.menu` → `hatchment.menu`. `--menu-icon-off` swaps it back in place.
`shell.json` is rewritten atomically and with the same indentation and key
order Omarchy's own writers use, so it neither gets caught half-written by the
shell's hot reload nor churns the file's formatting.

The icon is drawn solid rather than hatched, on nothing rather than on white:
hatching is mush at seventeen pixels, and a white ground would put a pale
square on the bar instead of a shield.

### Back to stock

`--stock`, or **Restore Omarchy defaults…** in the window, puts back what the
three installs changed, reading the defaults from Omarchy itself rather than
from copies kept here:

- **Screensaver** — `$OMARCHY_PATH/logo.txt` is copied back into
  `~/.config/omarchy/branding/screensaver.txt`, which is exactly what
  `omarchy branding screensaver reset` does.
- **fastfetch** — a `~/.config/fastfetch/config.jsonc` that shows the arms is
  moved aside, and fastfetch falls back to Omarchy's own config. One that shows
  anything else is yours, and is left alone.
- **Menu button** — `omarchy.menu` goes back into the bar layout and the
  `hatchment.menu` plugin is removed.

The screensaver art and fastfetch config are moved aside rather than deleted,
as `<name>.bak.<seconds>` — the same naming `omarchy-refresh-config` uses — so a
reset can be undone by hand. The menu plugin is deleted outright; it is only
hatchment's generated files, and setting the icon again recreates it. Setting
the fastfetch logo afterwards wires fastfetch up again from Omarchy's config.

`--stock` shows the restored screensaver straight away unless `--no-reload` is
given; in the window, the same box that governs setting the screensaver decides.

### Cell shape

Braille packs dots 2 across and 4 down into a character cell, so how tall the
art comes out for a given width depends on the cell's proportions — which belong
to your font, at your size, on your display. Terminals that fill in the pixel
fields of `TIOCGWINSZ` are asked directly, which is every terminal Omarchy
ships; nothing is sent to the terminal and nothing is read back, so a terminal
without the feature costs no round-trip and simply falls back to cells of about
8.5x16px. Only the ratio is used, never the absolute size, because the ratio is
what survives display scaling — a window rendered at 2x reports both dimensions
doubled and divides back to the same shape.

On the machine this was written on the real cell is 16x31, a dot ratio of
1.0323 against the fallback's 1.0625: about a 3% error in the shield's height,
and a shape the program has no business assuming on anyone else's behalf.

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
