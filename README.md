# armiger

Procedural heraldry for the terminal. Rolls a random coat of arms, renders it as
braille art, and hangs it in your fastfetch logo and your Omarchy screensaver.

```
$ python3 -m armiger --cols 24 --seed house-03
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

Heraldry is a constraint system, not a pile of random shapes, so `armiger`
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
  than a braille cell has, so `armiger` declines the combination instead.
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

## Usage

```bash
python3 -m armiger                          # roll and print
python3 -m armiger --seed my-house          # reproducible arms
python3 -m armiger --cols 32                # wider
python3 -m armiger --simple                 # simplest charges only
python3 -m armiger --svg arms.svg           # hatched vector export
python3 -m armiger --fastfetch              # install as the fastfetch logo
python3 -m armiger --screensaver            # install as screensaver branding
python3 -m armiger --screensaver --no-reload  # ...without taking the screen
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
python3 -m armiger --fastfetch --quiet >/dev/null
```

## Legibility gate

Arms are re-rolled until the render lands between 10% and 52% of dots set.
Outside that band the shield has either collapsed to near-empty or filled in
solid, and neither is worth installing. The measurement counts *dots*, not
cells: a cell-based count calls any textured area full, which is exactly the
distinction the gate exists to catch.

## Requirements

- Python 3.9+ (standard library only)
- `rsvg-convert` (librsvg) — rasterises the vector directly at dot resolution
- ImageMagick (`magick`) — thresholds to 1-bit

Rendering large and downsampling is what ruins this kind of art: a one-pixel
rule resampled to a fraction of a pixel turns grey, and thresholding grey against
a regular grid produces moiré. `rsvg-convert` places the marks on whole dots.

## Credits

The braille packing follows the approach in Caden's `make-logo.py`, which got
the cell geometry right: a braille cell is 2 dots wide by 4 tall, terminal cells
are about 8.5×16px, and the dot grid needs correcting for that.

## Licence

MIT.
