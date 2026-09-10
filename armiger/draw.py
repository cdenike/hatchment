"""Draw a Blazon as monochrome SVG.

The whole image is black on white with no greys, because the end target is a
1-bit braille cell. Tinctures are Petra Sancta hatching rather than fills, and
hatch spacing is a parameter: at small sizes the lines merge into a smudge, so
the caller widens the spacing or asks for solid fills instead.
"""

# The shield is a classic heater: straight sides, a shoulder, then curves to a
# point. Drawn in a 0..100 wide, 0..115 tall box.
SHIELD = ("M 3,3 L 97,3 L 97,52 "
          "C 97,86 74,105 50,112 "
          "C 26,105 3,86 3,52 Z")

SHIELD_BOX = (100, 115)


def _hatch_defs(spacing, stroke):
    """Petra Sancta patterns, sized to the caller's spacing.

    Every pattern lays down an opaque white tile before its marks. Without it
    the tile is transparent and whatever was painted underneath shows through,
    so a second tincture drawn over a first reads as both at once -- dots on top
    of diagonals rather than dots instead of them.
    """
    s = spacing
    half = s / 2.0
    bg = f'<rect x="0" y="0" width="{s}" height="{s}" fill="#fff"/>'
    return f"""
  <pattern id="or" width="{s}" height="{s}" patternUnits="userSpaceOnUse">
    {bg}
    <circle cx="{half}" cy="{half}" r="{stroke * 0.75}" fill="#000"/>
  </pattern>
  <pattern id="gules" width="{s}" height="{s}" patternUnits="userSpaceOnUse">
    {bg}
    <rect x="0" y="0" width="{stroke}" height="{s}" fill="#000"/>
  </pattern>
  <pattern id="azure" width="{s}" height="{s}" patternUnits="userSpaceOnUse">
    {bg}
    <rect x="0" y="0" width="{s}" height="{stroke}" fill="#000"/>
  </pattern>
  <pattern id="vert" width="{s}" height="{s}" patternUnits="userSpaceOnUse"
           patternTransform="rotate(45)">
    {bg}
    <rect x="0" y="0" width="{stroke}" height="{s}" fill="#000"/>
  </pattern>
  <pattern id="purpure" width="{s}" height="{s}" patternUnits="userSpaceOnUse"
           patternTransform="rotate(-45)">
    {bg}
    <rect x="0" y="0" width="{stroke}" height="{s}" fill="#000"/>
  </pattern>
  <pattern id="sable" width="{s}" height="{s}" patternUnits="userSpaceOnUse">
    {bg}
    <rect x="0" y="0" width="{stroke}" height="{s}" fill="#000"/>
    <rect x="0" y="0" width="{s}" height="{stroke}" fill="#000"/>
  </pattern>"""


def _fill(tincture, solid):
    """How to paint one tincture.

    `solid` collapses the palette to two values for targets too small to hold a
    pattern -- metals go white, colours go black. It loses the distinction
    between colours, but a readable two-tone shield beats an illegible seven-tone
    one, and at 40 dots across that is the actual choice.
    """
    if solid:
        return "#fff" if tincture in ("or", "argent") else "#000"
    if tincture == "argent":
        return "#fff"
    return f"url(#{tincture})"


def _poly(points):
    return " ".join(f"{x},{y}" for x, y in points)


def _charge_path(name, cx, cy, r):
    """One charge, centred on (cx, cy) with radius r. Silhouettes only."""
    if name == "roundel":
        return f'<circle cx="{cx}" cy="{cy}" r="{r}"/>'

    if name == "billet":
        return (f'<rect x="{cx - r * 0.62}" y="{cy - r}" '
                f'width="{r * 1.24}" height="{r * 2}"/>')

    if name == "lozenge":
        pts = [(cx, cy - r), (cx + r * 0.72, cy), (cx, cy + r), (cx - r * 0.72, cy)]
        return f'<polygon points="{_poly(pts)}"/>'

    if name == "mullet":
        import math
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rad = r if i % 2 == 0 else r * 0.42
            pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
        return f'<polygon points="{_poly(pts)}"/>'

    if name == "crescent":
        # Two overlapping circles, the upper one punched out by fill-rule.
        return (f'<path fill-rule="evenodd" d="'
                f'M {cx} {cy - r} a {r} {r} 0 1 0 0.01 0 Z '
                f'M {cx} {cy - r * 1.05} a {r * 0.82} {r * 0.82} 0 1 0 0.01 0 Z"/>')

    if name == "fleur-de-lis":
        # Deliberately blocky: a fleur with real curves vanishes when downsampled.
        return (f'<path d="'
                f'M {cx} {cy - r} '
                f'C {cx + r * 0.30} {cy - r * 0.45} {cx + r * 0.16} {cy - r * 0.25} {cx + r * 0.14} {cy - r * 0.05} '
                f'C {cx + r * 0.55} {cy - r * 0.50} {cx + r * 0.86} {cy - r * 0.02} {cx + r * 0.40} {cy + r * 0.36} '
                f'L {cx + r * 0.40} {cy + r * 0.52} '
                f'L {cx - r * 0.40} {cy + r * 0.52} '
                f'L {cx - r * 0.40} {cy + r * 0.36} '
                f'C {cx - r * 0.86} {cy - r * 0.02} {cx - r * 0.55} {cy - r * 0.50} {cx - r * 0.14} {cy - r * 0.05} '
                f'C {cx - r * 0.16} {cy - r * 0.25} {cx - r * 0.30} {cy - r * 0.45} {cx} {cy - r} Z"/>'
                f'<rect x="{cx - r * 0.62}" y="{cy + r * 0.52}" '
                f'width="{r * 1.24}" height="{r * 0.22}"/>')

    if name == "tower":
        w = r * 1.30
        return (f'<path d="'
                f'M {cx - w / 2} {cy + r} L {cx - w / 2} {cy - r * 0.36} '
                f'L {cx - w / 2} {cy - r * 0.72} L {cx - w * 0.28} {cy - r * 0.72} '
                f'L {cx - w * 0.28} {cy - r * 0.46} L {cx - w * 0.10} {cy - r * 0.46} '
                f'L {cx - w * 0.10} {cy - r * 0.72} L {cx + w * 0.10} {cy - r * 0.72} '
                f'L {cx + w * 0.10} {cy - r * 0.46} L {cx + w * 0.28} {cy - r * 0.46} '
                f'L {cx + w * 0.28} {cy - r * 0.72} L {cx + w / 2} {cy - r * 0.72} '
                f'L {cx + w / 2} {cy + r} Z"/>')

    return f'<circle cx="{cx}" cy="{cy}" r="{r}"/>'


def _ordinary_shape(name):
    """Ordinaries as polygons in the 0..100 / 0..115 shield box.

    Generously oversized so they run past the shield edge and get clipped -- an
    ordinary that stops short of the border reads as a mistake.
    """
    if name == "fess":
        return f'<rect x="-5" y="40" width="110" height="26"/>'
    if name == "pale":
        return f'<rect x="37" y="-5" width="26" height="125"/>'
    if name == "cross":
        return ('<rect x="-5" y="40" width="110" height="24"/>'
                '<rect x="38" y="-5" width="24" height="125"/>')
    if name == "bend":
        return ('<polygon points="-10,10 8,-10 115,90 97,110"/>')
    if name == "saltire":
        return ('<polygon points="-10,8 6,-10 115,95 99,113"/>'
                '<polygon points="110,8 94,-10 -15,95 1,113"/>')
    if name == "chevron":
        return ('<polygon points="50,32 108,92 108,116 50,56 -8,116 -8,92"/>')
    if name == "chief":
        return '<rect x="-5" y="-5" width="110" height="34"/>'
    return ""


def render(blazon, spacing=6.0, stroke=1.5, solid=False, size=512):
    """Produce the SVG string for a Blazon."""
    w, h = SHIELD_BOX
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {w} {h}" width="{size}" '
               f'height="{int(size * h / w)}">')
    out.append("<defs>")
    out.append(_hatch_defs(spacing, stroke))
    out.append(f'<clipPath id="shield"><path d="{SHIELD}"/></clipPath>')
    out.append("</defs>")

    # White ground first: the transcoder trims to ink, so the shield must sit on
    # something opaque or the trim eats the argent areas.
    out.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="#fff"/>')
    out.append('<g clip-path="url(#shield)">')

    # Field, then the second half if the arms are divided.
    out.append(f'<rect x="0" y="0" width="{w}" height="{h}" '
               f'fill="{_fill(blazon.field, solid)}"/>')
    if blazon.division:
        from .blazon import DIVISIONS
        poly = DIVISIONS[blazon.division][1]
        scaled = [(x, y * h / 100.0) for x, y in poly]
        out.append(f'<polygon points="{_poly(scaled)}" '
                   f'fill="{_fill(blazon.field2, solid)}"/>')

    # The ordinary, outlined so it stays distinct where its hatching is close to
    # the field's.
    if blazon.ordinary:
        shape = _ordinary_shape(blazon.ordinary)
        out.append(f'<g fill="{_fill(blazon.ordinary_tincture, solid)}" '
                   f'stroke="#000" stroke-width="1.2">{shape}</g>')

    # Charges. A chief eats the top third of the shield, so anything drawn at
    # the usual height would sit half-under it; drop the whole arrangement.
    if blazon.charge:
        fill = _fill(blazon.charge_tincture, solid)
        drop = 12 if blazon.ordinary == "chief" else 0
        anchor = getattr(blazon, "charge_anchor", "centre")
        if blazon.charge_count == 1:
            # A charge anchored to one half of a divided field is drawn smaller
            # and set into that half, clear of the division line.
            if anchor == "upper":
                cx, cy, r = 50, 27, 15
            elif anchor == "dexter":
                cx, cy, r = 26, 44, 14
            else:
                cx, cy, r = 50, 52 + drop, 20
            out.append(f'<g fill="{fill}" stroke="#000" stroke-width="1.2">'
                       f'{_charge_path(blazon.charge, cx, cy, r)}</g>')
        else:
            spots = [(30, 34 + drop), (70, 34 + drop), (50, 76 + drop * 0.4)]
            for cx, cy in spots[:blazon.charge_count]:
                out.append(f'<g fill="{fill}" stroke="#000" stroke-width="1.1">'
                           f'{_charge_path(blazon.charge, cx, cy, 13)}</g>')

    out.append("</g>")
    # The shield outline last, so nothing paints over it.
    out.append(f'<path d="{SHIELD}" fill="none" stroke="#000" stroke-width="3.2"/>')
    out.append("</svg>")
    return "\n".join(out)
