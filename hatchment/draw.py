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

# Heraldic colours for the full-colour export. Heraldry names a tincture, never
# a shade; these are the Wikimedia heraldry palette's, the closest thing to a
# standard and the shades most people have learned to read as these tinctures.
PALETTE = {
    "or": "#fcdd09", "argent": "#ffffff",
    "gules": "#da121a", "azure": "#0f47af", "vert": "#078930",
    "sable": "#000000", "purpure": "#9116a1",
    "murrey": "#8c1c4b", "sanguine": "#a01e1e", "tenné": "#b8621b",
}


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
  <pattern id="murrey" width="{s}" height="{s}" patternUnits="userSpaceOnUse"
           patternTransform="rotate(-45)">
    {bg}
    <rect x="0" y="0" width="{stroke}" height="{s}" fill="#000"/>
    <rect x="0" y="0" width="{s}" height="{stroke}" fill="#000"/>
  </pattern>
  <pattern id="sanguine" width="{s}" height="{s}" patternUnits="userSpaceOnUse"
           patternTransform="rotate(45)">
    {bg}
    <rect x="0" y="0" width="{stroke}" height="{s}" fill="#000"/>
    <rect x="0" y="0" width="{s}" height="{stroke}" fill="#000"/>
  </pattern>
  <pattern id="tenné" width="{s}" height="{s}" patternUnits="userSpaceOnUse">
    {bg}
    <rect x="0" y="0" width="{s}" height="{stroke}" fill="#000"/>
    <rect x="0" y="0" width="{stroke}" height="{s}" fill="#000"
          transform="rotate(-45 {half} {half})"/>
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


def _fur_defs(scale=1.0, colour=False):
    """Ermine, counter-ermine and vair as repeating patterns.

    Furs are already black-and-white by nature, so unlike hatching they need no
    special handling when the rest of the shield flattens to two tones -- they
    are the one pre-modern tincture that was always going to survive this.

    The ermine spot is simplified to its silhouette: a tail with three dots
    above it. The real charge has a finer waist and splayed dots, none of which
    is there at 4 dots across.
    """
    e = 22.0 * scale        # ermine tile
    v = 20.0 * scale        # vair tile
    # Vair is argent and azure; in one ink the bells can only be black.
    bell = PALETTE["azure"] if colour else "#000"

    def spot(colour):
        # Drawn around the tile centre so the pattern tiles without clipping.
        cx, cy = e / 2, e / 2
        w = e * 0.20
        return (f'<path fill="{colour}" d="'
                f'M {cx} {cy - e * 0.06} '
                f'L {cx + w} {cy + e * 0.22} '
                f'L {cx - w} {cy + e * 0.22} Z"/>'
                f'<circle fill="{colour}" cx="{cx}" cy="{cy - e * 0.20}" r="{e * 0.055}"/>'
                f'<circle fill="{colour}" cx="{cx - w * 0.85}" cy="{cy - e * 0.10}" r="{e * 0.055}"/>'
                f'<circle fill="{colour}" cx="{cx + w * 0.85}" cy="{cy - e * 0.10}" r="{e * 0.055}"/>')

    return f"""
  <pattern id="ermine" width="{e}" height="{e}" patternUnits="userSpaceOnUse">
    <rect x="0" y="0" width="{e}" height="{e}" fill="#fff"/>
    {spot('#000')}
  </pattern>
  <pattern id="counter-ermine" width="{e}" height="{e}" patternUnits="userSpaceOnUse">
    <rect x="0" y="0" width="{e}" height="{e}" fill="#000"/>
    {spot('#fff')}
  </pattern>
  <pattern id="vair" width="{v}" height="{v}" patternUnits="userSpaceOnUse">
    <rect x="0" y="0" width="{v}" height="{v}" fill="#fff"/>
    <path fill="{bell}" d="M 0 0 L {v / 2} 0 L {v * 0.42} {v * 0.36}
      Q {v * 0.25} {v * 0.52} {v * 0.08} {v * 0.36} Z"/>
    <path fill="{bell}" d="M {v / 2} {v / 2} L {v} {v / 2} L {v * 0.92} {v * 0.86}
      Q {v * 0.75} {v * 1.02} {v * 0.58} {v * 0.86} Z"/>
  </pattern>"""


def _variation_shapes(name, count, w, h):
    """The second tincture of a variation, painted over the first.

    Only the alternating pieces are drawn; the first tincture is already the
    ground beneath. Everything is clipped to the shield, so pieces deliberately
    overrun the box.
    """
    out = []
    if name == "barry":
        step = h / count
        for i in range(1, count, 2):
            out.append(f'<rect x="-5" y="{i * step}" width="{w + 10}" height="{step}"/>')
    elif name == "paly":
        step = w / count
        for i in range(1, count, 2):
            out.append(f'<rect x="{i * step}" y="-5" width="{step}" height="{h + 10}"/>')
    elif name == "bendy":
        # Diagonal bands, drawn as a rotated strip field wide enough to cover
        # the shield's diagonal.
        step = (w + h) / count
        for i in range(1, count * 2, 2):
            out.append(f'<rect x="{-w + i * step}" y="{-h}" width="{step}" '
                       f'height="{h * 3}" transform="rotate(45 {w / 2} {h / 2})"/>')
    elif name == "checky":
        sx, sy = w / count, h / count
        for r in range(count + 1):
            for c in range(count + 1):
                if (r + c) % 2:
                    out.append(f'<rect x="{c * sx}" y="{r * sy}" width="{sx}" height="{sy}"/>')
    elif name == "lozengy":
        sx, sy = w / count, h / count
        for r in range(-1, count + 1):
            for c in range(-1, count + 1):
                cx = c * sx + (sx / 2 if r % 2 else 0)
                cy = r * sy
                out.append(f'<polygon points="{cx},{cy - sy / 2} {cx + sx / 2},{cy} '
                           f'{cx},{cy + sy / 2} {cx - sx / 2},{cy}"/>')
    elif name == "gyronny":
        # Eight wedges from the fess point; every other one is painted.
        import math
        cx, cy = w / 2, h * 0.45
        R = w + h
        for i in range(0, 8, 2):
            a1 = math.radians(i * 45 - 90)
            a2 = math.radians((i + 1) * 45 - 90)
            p1 = (cx + R * math.cos(a1), cy + R * math.sin(a1))
            p2 = (cx + R * math.cos(a2), cy + R * math.sin(a2))
            out.append(f'<polygon points="{cx},{cy} {p1[0]},{p1[1]} {p2[0]},{p2[1]}"/>')
    elif name == "chevronny":
        step = h / count
        for i in range(1, count * 2, 2):
            y = i * step
            out.append(f'<polygon points="-5,{y} {w / 2},{y - step * 1.1} {w + 5},{y} '
                       f'{w + 5},{y + step} {w / 2},{y + step * -0.1} -5,{y + step}"/>')
    return "".join(out)



def _division_polygon(name, style, w, h):
    """The second tincture's region, with the dividing edge in `style`.

    Built as a polygon that overruns the shield box on every side except the
    dividing edge itself, so the clip decides the outline and only the cut has
    to be right.
    """
    from . import lines
    if name == "per pale":
        edge = lines.points((w / 2, -6), (w / 2, h + 6), style)
        return edge + [(w + 6, h + 6), (w + 6, -6)]
    if name == "per fess":
        y = h * 0.47
        edge = lines.points((-6, y), (w + 6, y), style)
        return edge + [(w + 6, h + 6), (-6, h + 6)]
    if name == "per bend":
        edge = lines.points((0, -6), (w, h), style)
        return edge + [(-6, h + 6)]
    if name == "per chevron":
        apex = (w / 2, h * 0.42)
        left = lines.points((-6, h + 6), apex, style)
        right = lines.points(apex, (w + 6, h + 6), style)
        return left + right[1:] + [(w + 6, -6), (-6, -6)]
    if name == "per bend sinister":
        edge = lines.points((w, -6), (0, h), style)
        return edge + [(w + 6, h + 6)]
    # quarterly and per saltire are two regions each, so they are returned as a
    # list of polygons by _division_regions instead.
    return []


def _division_regions(name, style, w, h):
    """Divisions made of more than one patch of the second tincture.

    Each cut is walked out from the fess point with the line style applied --
    the same edge a per pale or per bend gets. These used to be drawn straight
    whatever the blazon said, so "Quarterly engrailed" showed plain quarters.
    """
    from . import lines
    cx, cy = w / 2, h * 0.47

    def cut(to):
        return lines.points((cx, cy), to, style)

    if name == "quarterly":
        up, down = cut((cx, -6)), cut((cx, h + 6))
        right, left = cut((w + 6, cy)), cut((-6, cy))
        return [up[::-1] + right[1:] + [(w + 6, -6)],
                down[::-1] + left[1:] + [(-6, h + 6)]]
    if name == "per saltire":
        # Four triangles meeting at the fess point; the flanking pair is the
        # second tincture, which is what makes it read as a saltire cut rather
        # than as quarterly turned forty-five degrees.
        return [cut((-6, -6))[::-1] + cut((-6, h + 6))[1:],
                cut((w + 6, -6))[::-1] + cut((w + 6, h + 6))[1:]]
    return []


def _banded_ordinary(name, style, w, h):
    """Ordinaries whose two long edges can carry a line of partition.

    The edges are generated in opposite directions and the second is reversed,
    so the polygon closes as a band rather than crossing itself. Amplitude is
    halved: a wave as deep as a straight-edged fess would eat the band.
    """
    from . import lines
    sc = 0.55
    if name == "fess":
        a, b = h * 0.36, h * 0.58
        top = lines.points((-6, a), (w + 6, a), style, scale=sc)
        bot = lines.points((-6, b), (w + 6, b), style, scale=sc, phase=0.5)
        return top + list(reversed(bot))
    if name == "pale":
        a, b = w * 0.37, w * 0.63
        left = lines.points((a, -6), (a, h + 6), style, scale=sc)
        right = lines.points((b, -6), (b, h + 6), style, scale=sc, phase=0.5)
        return left + list(reversed(right))
    if name == "chief":
        y = h * 0.26
        edge = lines.points((-6, y), (w + 6, y), style, scale=sc)
        return edge + [(w + 6, -6), (-6, -6)]
    if name in ("bend", "bend sinister"):
        # Two parallel diagonals, offset perpendicular to the run. The sinister
        # bend is the same construction run from the other top corner, so it
        # falls out of mirroring the endpoints rather than a second geometry.
        import math
        if name == "bend":
            p0, p1 = (-8, 6), (w + 8, h * 0.82)
        else:
            p0, p1 = (w + 8, 6), (-8, h * 0.82)
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy)
        nx, ny = -dy / L * 24, dx / L * 24
        a = lines.points(p0, p1, style, scale=sc)
        b = lines.points((p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny),
                         style, scale=sc, phase=0.5)
        return a + list(reversed(b))
    return []


def _fill(tincture, solid, colour=False):
    """How to paint one tincture.

    `solid` collapses the palette to two values for targets too small to hold a
    pattern -- metals go white, colours go black. It loses the distinction
    between colours, but a readable two-tone shield beats an illegible seven-tone
    one, and at 40 dots across that is the actual choice.
    """
    # Furs are patterns in both modes: they are black-and-white by nature, so
    # there is nothing to flatten and no reason to lose them.
    if tincture in ("ermine", "counter-ermine", "vair"):
        return f"url(#{tincture})"
    if colour:
        return PALETTE[tincture]
    if solid:
        return "#fff" if tincture in ("or", "argent") else "#000"
    if tincture == "argent":
        return "#fff"
    return f"url(#{tincture})"


def _poly(points):
    return " ".join(f"{x},{y}" for x, y in points)


def _charge_path(name, cx, cy, r, variant=None, outline=1.15):
    """One charge, centred on (cx, cy) with radius r. Silhouettes only.

    `variant` is a pose or form from hatchment.variants; None, or the charge's
    first form, draws the charge as it always was.
    """
    from . import charges, variants
    shape = variants.shape(name, variant) if variant else None
    if shape is None:
        shape = charges.SHAPES.get(name)
    if shape is not None:
        # Drawn in a 200-unit box and scaled into place. The outline width is
        # scaled back up by the same factor, so it matches the older charges'
        # instead of shrinking to a hairline with the shape.
        k = r / 100.0
        return (f'<g transform="translate({cx:.2f} {cy:.2f}) scale({k:.4f})" '
                f'stroke-width="{outline / k:.2f}">{shape}</g>')
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

    if name == "garb":
        # A garb is a wheatsheaf: stalks fanned out, ears at the top, bound at
        # the waist. The band is what stops it reading as a bush.
        return (f'<path d="'
                f'M {cx - r * 0.16} {cy - r * 0.10} '
                f'C {cx - r * 0.70} {cy - r * 0.34} {cx - r * 0.74} {cy - r * 0.74} {cx - r * 0.52} {cy - r * 0.98} '
                f'L {cx - r * 0.22} {cy - r * 0.52} '
                f'L {cx - r * 0.20} {cy - r * 0.96} '
                f'L {cx + r * 0.20} {cy - r * 0.96} '
                f'L {cx + r * 0.22} {cy - r * 0.52} '
                f'L {cx + r * 0.52} {cy - r * 0.98} '
                f'C {cx + r * 0.74} {cy - r * 0.74} {cx + r * 0.70} {cy - r * 0.34} {cx + r * 0.16} {cy - r * 0.10} Z"/>'
                f'<path d="'
                f'M {cx - r * 0.22} {cy + r * 0.02} '
                f'C {cx - r * 0.80} {cy + r * 0.30} {cx - r * 0.66} {cy + r * 0.86} {cx - r * 0.30} {cy + r * 0.98} '
                f'L {cx + r * 0.30} {cy + r * 0.98} '
                f'C {cx + r * 0.66} {cy + r * 0.86} {cx + r * 0.80} {cy + r * 0.30} {cx + r * 0.22} {cy + r * 0.02} Z"/>'
                f'<rect x="{cx - r * 0.56}" y="{cy - r * 0.14}" '
                f'width="{r * 1.12}" height="{r * 0.24}"/>')

    if name == "tree":
        return (f'<circle cx="{cx}" cy="{cy - r * 0.34}" r="{r * 0.62}"/>'
                f'<circle cx="{cx - r * 0.48}" cy="{cy - r * 0.04}" r="{r * 0.38}"/>'
                f'<circle cx="{cx + r * 0.48}" cy="{cy - r * 0.04}" r="{r * 0.38}"/>'
                f'<rect x="{cx - r * 0.13}" y="{cy + r * 0.14}" '
                f'width="{r * 0.26}" height="{r * 0.82}"/>'
                f'<rect x="{cx - r * 0.44}" y="{cy + r * 0.84}" '
                f'width="{r * 0.88}" height="{r * 0.16}"/>')

    if name == "rose":
        # A heraldic rose is flat and five-fold, seen face on -- not a garden
        # rose in profile.
        import math
        out = []
        for i in range(5):
            a = -math.pi / 2 + i * 2 * math.pi / 5
            out.append('<circle cx="%.2f" cy="%.2f" r="%.2f"/>'
                       % (cx + r * 0.58 * math.cos(a),
                          cy + r * 0.58 * math.sin(a), r * 0.44))
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.30}" fill="#fff"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.15}"/>')
        return "".join(out)

    if name == "trefoil":
        return (f'<circle cx="{cx}" cy="{cy - r * 0.46}" r="{r * 0.34}"/>'
                f'<circle cx="{cx - r * 0.42}" cy="{cy + r * 0.06}" r="{r * 0.34}"/>'
                f'<circle cx="{cx + r * 0.42}" cy="{cy + r * 0.06}" r="{r * 0.34}"/>'
                f'<rect x="{cx - r * 0.09}" y="{cy + r * 0.20}" '
                f'width="{r * 0.18}" height="{r * 0.78}"/>')

    if name == "attires":
        # Antlers alone, borne as a charge in their own right.
        def rack(sign):
            sx = sign
            return (f'<path d="'
                    f'M {cx + sx * r * 0.10} {cy + r * 0.94} '
                    f'L {cx + sx * r * 0.22} {cy + r * 0.20} '
                    f'L {cx + sx * r * 0.60} {cy - r * 0.06} '
                    f'L {cx + sx * r * 0.30} {cy - r * 0.04} '
                    f'L {cx + sx * r * 0.42} {cy - r * 0.48} '
                    f'L {cx + sx * r * 0.20} {cy - r * 0.28} '
                    f'L {cx + sx * r * 0.24} {cy - r * 0.84} '
                    f'L {cx + sx * r * 0.02} {cy - r * 0.34} '
                    f'L {cx + sx * r * 0.01} {cy + r * 0.20} Z"/>')
        return rack(-1) + rack(1)

    if name == "bee":
        return (f'<ellipse cx="{cx}" cy="{cy + r * 0.22}" '
                f'rx="{r * 0.40}" ry="{r * 0.62}"/>'
                f'<rect x="{cx - r * 0.42}" y="{cy + r * 0.06}" '
                f'width="{r * 0.84}" height="{r * 0.13}" fill="#fff"/>'
                f'<rect x="{cx - r * 0.38}" y="{cy + r * 0.44}" '
                f'width="{r * 0.76}" height="{r * 0.13}" fill="#fff"/>'
                f'<circle cx="{cx}" cy="{cy - r * 0.52}" r="{r * 0.26}"/>'
                f'<ellipse cx="{cx - r * 0.62}" cy="{cy - r * 0.16}" '
                f'rx="{r * 0.36}" ry="{r * 0.20}" transform="rotate(-28 {cx - r * 0.62} {cy - r * 0.16})"/>'
                f'<ellipse cx="{cx + r * 0.62}" cy="{cy - r * 0.16}" '
                f'rx="{r * 0.36}" ry="{r * 0.20}" transform="rotate(28 {cx + r * 0.62} {cy - r * 0.16})"/>')

    if name == "fish":
        return (f'<path d="'
                f'M {cx + r * 0.92} {cy} '
                f'C {cx + r * 0.30} {cy - r * 0.66} {cx - r * 0.30} {cy - r * 0.66} {cx - r * 0.62} {cy} '
                f'C {cx - r * 0.30} {cy + r * 0.66} {cx + r * 0.30} {cy + r * 0.66} {cx + r * 0.92} {cy} Z"/>'
                f'<path d="M {cx - r * 0.58} {cy} '
                f'L {cx - r * 0.98} {cy - r * 0.42} '
                f'L {cx - r * 0.98} {cy + r * 0.42} Z"/>'
                f'<circle cx="{cx + r * 0.52}" cy="{cy - r * 0.10}" '
                f'r="{r * 0.10}" fill="#fff"/>')

    if name == "banner":
        # A staff with a flag whose fly ripples. The ripple is the point: it is
        # the one charge here that is supposed to look like cloth.
        return (f'<rect x="{cx - r * 0.86}" y="{cy - r}" '
                f'width="{r * 0.16}" height="{r * 2.0}"/>'
                f'<path d="M {cx - r * 0.70} {cy - r * 0.92} '
                f'L {cx + r * 0.92} {cy - r * 0.62} '
                f'Q {cx + r * 0.50} {cy - r * 0.20} {cx + r * 0.92} {cy + r * 0.22} '
                f'L {cx - r * 0.70} {cy - r * 0.08} Z"/>'
                f'<circle cx="{cx - r * 0.78}" cy="{cy - r * 1.06}" r="{r * 0.15}"/>')

    if name == "eagle":
        # Eagle displayed: wings spread, head to dexter, tail below. Symmetric
        # except the head, which is what stops it reading as a bat.
        return (f'<path d="'
                f'M {cx} {cy - r * 0.30} '
                f'L {cx - r * 0.34} {cy - r * 0.52} '
                f'L {cx - r * 0.96} {cy - r * 0.72} '
                f'L {cx - r * 0.72} {cy - r * 0.10} '
                f'L {cx - r * 0.90} {cy + r * 0.30} '
                f'L {cx - r * 0.34} {cy + r * 0.10} '
                f'L {cx - r * 0.18} {cy + r * 0.52} '
                f'L {cx - r * 0.34} {cy + r * 0.96} '
                f'L {cx} {cy + r * 0.72} '
                f'L {cx + r * 0.34} {cy + r * 0.96} '
                f'L {cx + r * 0.18} {cy + r * 0.52} '
                f'L {cx + r * 0.34} {cy + r * 0.10} '
                f'L {cx + r * 0.90} {cy + r * 0.30} '
                f'L {cx + r * 0.72} {cy - r * 0.10} '
                f'L {cx + r * 0.96} {cy - r * 0.72} '
                f'L {cx + r * 0.34} {cy - r * 0.52} Z"/>'
                f'<path d="M {cx - r * 0.16} {cy - r * 0.46} '
                f'L {cx - r * 0.16} {cy - r * 0.86} '
                f'L {cx - r * 0.62} {cy - r * 0.96} '
                f'L {cx - r * 0.20} {cy - r * 1.02} '
                f'L {cx + r * 0.16} {cy - r * 0.84} '
                f'L {cx + r * 0.16} {cy - r * 0.46} Z"/>')

    if name == "annulet":
        return (f'<path fill-rule="evenodd" d="'
                f'M {cx} {cy - r} a {r} {r} 0 1 0 0.01 0 Z '
                f'M {cx} {cy - r * 0.60} a {r * 0.60} {r * 0.60} 0 1 0 0.01 0 Z"/>')

    if name == "sun in splendour":
        # Disc plus alternating straight rays. Sixteen rays is traditional;
        # twelve is what survives when each one is two dots wide.
        import math
        rays = []
        for i in range(12):
            a = math.radians(i * 30)
            a1, a2 = a - 0.13, a + 0.13
            rays.append(
                f'<polygon points="'
                f'{cx + r * 0.62 * math.cos(a1)},{cy + r * 0.62 * math.sin(a1)} '
                f'{cx + r * math.cos(a)},{cy + r * math.sin(a)} '
                f'{cx + r * 0.62 * math.cos(a2)},{cy + r * 0.62 * math.sin(a2)}"/>')
        return f'<circle cx="{cx}" cy="{cy}" r="{r * 0.60}"/>' + "".join(rays)

    if name == "estoile":
        # Six wavy rays. The waviness is what separates an estoile from a
        # mullet; at this size it reads as concave flanks, which is enough.
        import math
        pts = []
        for i in range(12):
            a = -math.pi / 2 + i * math.pi / 6
            rad = r if i % 2 == 0 else r * 0.30
            pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
        return f'<polygon points="{_poly(pts)}"/>'

    if name == "comet":
        import math
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rad = r * 0.52 if i % 2 == 0 else r * 0.22
            pts.append((cx - r * 0.30 + rad * math.cos(a),
                        cy - r * 0.30 + rad * math.sin(a)))
        head = f'<polygon points="{_poly(pts)}"/>'
        tail = (f'<path d="M {cx - r * 0.10} {cy - r * 0.05} '
                f'L {cx + r * 0.95} {cy + r * 0.85} '
                f'L {cx + r * 0.45} {cy + r * 0.95} Z"/>')
        return head + tail

    if name == "increscent":
        # A crescent with its horns to dexter, which is what makes it an
        # increscent rather than a plain crescent.
        return (f'<g transform="rotate(90 {cx} {cy})">'
                f'<path fill-rule="evenodd" d="'
                f'M {cx} {cy - r} a {r} {r} 0 1 0 0.01 0 Z '
                f'M {cx} {cy - r * 1.05} a {r * 0.82} {r * 0.82} 0 1 0 0.01 0 Z"/></g>')

    if name == "orb":
        return (f'<circle cx="{cx}" cy="{cy + r * 0.18}" r="{r * 0.78}"/>'
                f'<rect x="{cx - r * 0.78}" y="{cy + r * 0.02}" '
                f'width="{r * 1.56}" height="{r * 0.20}" fill="#fff"/>'
                f'<rect x="{cx - r * 0.12}" y="{cy - r}" '
                f'width="{r * 0.24}" height="{r * 0.42}"/>'
                f'<rect x="{cx - r * 0.34}" y="{cy - r * 0.84}" '
                f'width="{r * 0.68}" height="{r * 0.20}"/>')

    if name == "sword":
        return (f'<polygon points="{cx},{cy - r} {cx + r * 0.15},{cy - r * 0.72} '
                f'{cx + r * 0.15},{cy + r * 0.30} {cx - r * 0.15},{cy + r * 0.30} '
                f'{cx - r * 0.15},{cy - r * 0.72}"/>'
                f'<rect x="{cx - r * 0.62}" y="{cy + r * 0.30}" '
                f'width="{r * 1.24}" height="{r * 0.20}"/>'
                f'<rect x="{cx - r * 0.12}" y="{cy + r * 0.50}" '
                f'width="{r * 0.24}" height="{r * 0.38}"/>'
                f'<circle cx="{cx}" cy="{cy + r * 0.94}" r="{r * 0.16}"/>')

    if name == "key":
        return (f'<path fill-rule="evenodd" d="'
                f'M {cx} {cy - r} a {r * 0.40} {r * 0.40} 0 1 0 0.01 0 Z '
                f'M {cx} {cy - r * 0.86} a {r * 0.20} {r * 0.20} 0 1 0 0.01 0 Z"/>'
                f'<rect x="{cx - r * 0.10}" y="{cy - r * 0.24}" '
                f'width="{r * 0.20}" height="{r * 1.10}"/>'
                f'<rect x="{cx}" y="{cy + r * 0.50}" '
                f'width="{r * 0.40}" height="{r * 0.16}"/>'
                f'<rect x="{cx}" y="{cy + r * 0.80}" '
                f'width="{r * 0.30}" height="{r * 0.16}"/>')

    if name == "crown":
        return (f'<path d="'
                f'M {cx - r * 0.86} {cy + r * 0.10} L {cx - r * 0.60} {cy - r * 0.62} '
                f'L {cx - r * 0.30} {cy + r * 0.02} L {cx} {cy - r * 0.80} '
                f'L {cx + r * 0.30} {cy + r * 0.02} L {cx + r * 0.60} {cy - r * 0.62} '
                f'L {cx + r * 0.86} {cy + r * 0.10} Z"/>'
                f'<rect x="{cx - r * 0.90}" y="{cy + r * 0.10}" '
                f'width="{r * 1.80}" height="{r * 0.40}"/>'
                f'<circle cx="{cx}" cy="{cy - r * 0.92}" r="{r * 0.13}"/>'
                f'<circle cx="{cx - r * 0.60}" cy="{cy - r * 0.76}" r="{r * 0.11}"/>'
                f'<circle cx="{cx + r * 0.60}" cy="{cy - r * 0.76}" r="{r * 0.11}"/>')

    if name == "portcullis":
        bars = []
        for i in range(4):
            x = cx - r * 0.78 + i * (r * 1.56 / 3)
            bars.append(f'<rect x="{x - r * 0.07}" y="{cy - r * 0.80}" '
                        f'width="{r * 0.14}" height="{r * 1.60}"/>')
            bars.append(f'<polygon points="{x - r * 0.13},{cy + r * 0.80} '
                        f'{x + r * 0.13},{cy + r * 0.80} {x},{cy + r * 1.02}"/>')
        for i in range(3):
            y = cy - r * 0.80 + i * (r * 1.20 / 2)
            bars.append(f'<rect x="{cx - r * 0.85}" y="{y - r * 0.07}" '
                        f'width="{r * 1.70}" height="{r * 0.14}"/>')
        return "".join(bars)

    if name == "chalice":
        return (f'<path d="M {cx - r * 0.60} {cy - r * 0.70} '
                f'L {cx + r * 0.60} {cy - r * 0.70} '
                f'C {cx + r * 0.58} {cy + r * 0.10} {cx + r * 0.22} {cy + r * 0.28} '
                f'{cx + r * 0.10} {cy + r * 0.34} '
                f'L {cx - r * 0.10} {cy + r * 0.34} '
                f'C {cx - r * 0.22} {cy + r * 0.28} {cx - r * 0.58} {cy + r * 0.10} '
                f'{cx - r * 0.60} {cy - r * 0.70} Z"/>'
                f'<rect x="{cx - r * 0.09}" y="{cy + r * 0.34}" '
                f'width="{r * 0.18}" height="{r * 0.40}"/>'
                f'<rect x="{cx - r * 0.52}" y="{cy + r * 0.74}" '
                f'width="{r * 1.04}" height="{r * 0.20}"/>')

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


def _ordinary_shape(name, band="#000"):
    """Ordinaries as polygons in the 0..100 / 0..115 shield box.

    Generously oversized so they run past the shield edge and get clipped -- an
    ordinary that stops short of the border reads as a mistake.

    `band` paints the two drawn as thick strokes, bordure and orle, which a fill
    does not reach. Black in one ink, as they always were; the tincture itself
    in colour, where a black band would be a different coat of arms.
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
    if name == "bordure":
        # A band following the rim. Drawn as the shield outline stroked thickly;
        # the clip trims the outer half, leaving a border of even width.
        return f'<path d="{SHIELD}" fill="none" stroke="{band}" stroke-width="22"/>'
    if name == "orle":
        # The same idea set in from the edge, so a strip of field shows outside
        # it -- that gap is the whole difference from a bordure.
        return ('<g transform="translate(50,57.5) scale(0.80) translate(-50,-57.5)">'
                f'<path d="{SHIELD}" fill="none" stroke="{band}" stroke-width="12"/></g>')
    if name == "canton":
        return '<rect x="-5" y="-5" width="42" height="42"/>'
    if name == "gyron":
        return '<polygon points="-5,-5 50,57 -5,57"/>'
    if name == "pile":
        return '<polygon points="8,-5 92,-5 50,88"/>'
    if name == "pall":
        return ('<polygon points="-6,-6 16,-6 50,44 84,-6 106,-6 '
                '62,58 62,120 38,120 38,58"/>')
    if name == "bend sinister":
        return '<polygon points="110,10 92,-10 -15,90 3,110"/>'
    if name == "fess double":
        return ('<rect x="-5" y="30" width="110" height="15"/>'
                '<rect x="-5" y="62" width="110" height="15"/>')
    if name == "pale double":
        return ('<rect x="24" y="-5" width="15" height="125"/>'
                '<rect x="61" y="-5" width="15" height="125"/>')
    return ""


def _seme_shapes(name, rng, w, h):
    """A field strewn with one small charge, repeated to the edges.

    Rows are offset by half a step so the strewing reads as scattered rather
    than as a grid, and everything overruns the box because the clip is what
    cuts the charges at the rim -- half a charge at the edge is correct.
    """
    cols = rng.choice([4, 5, 6])
    r = (w / cols) * 0.30
    sx = w / cols
    sy = sx * 1.05
    out = []
    row = 0
    y = -sy * 0.4
    while y < h + sy:
        offset = (sx / 2) if row % 2 else 0
        x = -sx * 0.4 + offset
        while x < w + sx:
            out.append(_charge_path(name, x, y, r))
            x += sx
        y += sy
        row += 1
    return "".join(out)


# --- settings --------------------------------------------------------------
# The ground a setting puts along the base, the small charges standing on it,
# and the companions in chief (see hatchment.scenes). Drawn before the main
# charge, which is placed to stand on the ground rather than float over it.

def _ground_top(style, x):
    """Height of the ground's top edge at x, or None if there is nothing to stand on."""
    if style == "mount":
        t = (x + 5) / 110.0
        return (1 - t) ** 2 * 100 + 2 * (1 - t) * t * 70 + t * t * 100
    if style == "trimount":
        for x0, y0, yc, x1, y1 in ((-5, 102, 80, 33, 96), (33, 96, 70, 67, 96),
                                   (67, 96, 80, 105, 102)):
            if x <= x1:
                t = max(0.0, min(1.0, (x - x0) / (x1 - x0)))
                return (1 - t) ** 2 * y0 + 2 * (1 - t) * t * yc + t * t * y1
        return 102.0
    return {"flat": 96.0, "dunes": 94.0, "water": 84.0}.get(style)


def _rim(x):
    """Roughly where the shield's lower edge is at x -- it curves to a point."""
    return 112.0 - 60.0 * (abs(x - 50.0) / 47.0) ** 2.2


def _ground_shape(style, fill1, fill2):
    from . import lines
    edge = 'stroke="#000" stroke-width="1.2"'
    if style == "mount":
        return f'<path d="M -5,120 L -5,100 Q 50,70 105,100 L 105,120 Z" fill="{fill1}" {edge}/>'
    if style == "trimount":
        return (f'<path d="M -5,120 L -5,102 Q 17,80 33,96 Q 50,70 67,96 '
                f'Q 83,80 105,102 L 105,120 Z" fill="{fill1}" {edge}/>')
    if style == "flat":
        return f'<rect x="-5" y="96" width="110" height="24" fill="{fill1}" {edge}/>'
    if style == "dunes":
        top = lines.points((-6, 94), (106, 94), "wavy", scale=0.6)
        return f'<polygon points="{_poly(top + [(106, 120), (-6, 120)])}" fill="{fill1}" {edge}/>'
    if style == "water":
        out = []
        for i, y in enumerate((84, 94, 104)):
            top = lines.points((-6, y), (106, y), "wavy", scale=0.5)
            out.append(f'<polygon points="{_poly(top + [(106, 120), (-6, 120)])}" '
                       f'fill="{fill1 if i % 2 == 0 else fill2}" {edge}/>')
        return "".join(out)
    return ""


def _setting(blazon, solid, colour):
    style = blazon.base_style
    out = [_ground_shape(style, _fill(blazon.base_tincture, solid, colour)
                         if blazon.base_tincture else "none",
                         _fill(blazon.base_tincture2 or blazon.base_tincture, solid, colour)
                         if blazon.base_tincture else "none")]
    if blazon.base_row:
        n = blazon.base_row_count
        standing = _ground_top(style, 50) is not None
        r = 7.5 if standing else 12.0
        items = []
        for i in range(n):
            # Flames and clouds rise from the rim itself, so they keep inside
            # the narrowing point instead of being clipped away beside it.
            x = (6 + 88 * (i + 0.5) / n) if standing else (16 + 68 * (i + 0.5) / n)
            y = (_ground_top(style, x) - r * 0.85) if standing else (_rim(x) - r * 0.7)
            items.append(_charge_path(blazon.base_row, round(x, 2), round(y, 2), r,
                                      blazon.base_row_variant))
        out.append(f'<g fill="{_fill(blazon.base_row_tincture, solid, colour)}" '
                   f'stroke="#000" stroke-width="0.8">{"".join(items)}</g>')
    return "".join(out)


def _companions(blazon, solid, colour):
    n = blazon.companion_count
    spots = {1: [(21, 23)], 2: [(21, 23), (79, 23)],
             3: [(20, 22), (50, 15), (80, 22)]}.get(n, [(21, 23)])
    r = 10.0 if n == 1 else 8.0
    return (f'<g fill="{_fill(blazon.companion_tincture, solid, colour)}" '
            f'stroke="#000" stroke-width="0.9">'
            + "".join(_charge_path(blazon.companion, x, y, r, blazon.companion_variant)
                      for x, y in spots) + '</g>')


def _fimbriation(blazon, cx, cy, r, solid, colour):
    """A narrow edge in the field's tincture round a charge laid on a pattern.

    Heraldry's own answer to a charge crossing something busy: it is
    fimbriated, edged with a band of another tincture, and here that band is
    the field's, so the pattern stops short of the charge on every side.
    """
    if not getattr(blazon, "pattern", None) or not blazon.charge:
        return ""
    edge = _fill(blazon.field, solid, colour)
    w = max(2.5, r * 0.17)
    return (f'<g fill="{edge}" stroke="{edge}" stroke-width="{w:.2f}" '
            f'stroke-linejoin="round">'
            f'{_charge_path(blazon.charge, cx, cy, r, getattr(blazon, "charge_variant", None), outline=w)}'
            f'</g>')


def _make_room(blazon, cx, cy, r):
    """Where a single charge goes once a setting takes the base or the chief."""
    if getattr(blazon, "companion", None):
        r = min(r, 23.0)
    style = getattr(blazon, "base_style", None)
    stand = _ground_top(style, cx) if style else None
    if stand is not None:
        r = min(r, 25.0)
        cy = stand - r * 0.95
    return cx, cy, r


def _make_room_many(blazon, spots, rad):
    """Several charges, lifted clear of a ground and kept below companions."""
    if getattr(blazon, "companion", None):
        rad *= 0.85
        low = min(y for _, y in spots) - rad
        if low < 34:
            spots = [(x, y + (34 - low)) for x, y in spots]
    style = getattr(blazon, "base_style", None)
    stand = _ground_top(style, 50) if style else None
    if stand is not None:
        dy = min(0.0, (stand - rad) - max(y for _, y in spots))
        spots = [(x, y + dy) for x, y in spots]
    return spots, rad


def render(blazon, spacing=6.0, stroke=1.5, solid=False, size=512, ground="#fff",
           outline=3.2, colour=False):
    """Produce the SVG string for a Blazon.

    `ground` paints behind the shield. It exists for the braille transcoder,
    which trims to ink and would otherwise eat the argent areas; a target that
    composites the shield over something of its own -- a bar icon over a bar --
    passes None instead and gets transparency outside the shield edge.

    `colour` paints tinctures in heraldic colour rather than hatching, for
    exports: flat fills have no line spacing, so a patterned field -- rings,
    fractals, semé, all finer than any hatch that reads -- cannot break them up.
    """
    w, h = SHIELD_BOX
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {w} {h}" width="{size}" '
               f'height="{int(size * h / w)}">')
    out.append("<defs>")
    if not colour:
        out.append(_hatch_defs(spacing, stroke))
    out.append(_fur_defs(colour=colour))
    out.append(f'<clipPath id="shield"><path d="{SHIELD}"/></clipPath>')
    out.append("</defs>")

    # White ground first: the transcoder trims to ink, so the shield must sit on
    # something opaque or the trim eats the argent areas.
    if ground:
        out.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="{ground}"/>')
    out.append('<g clip-path="url(#shield)">')

    # Field, then the second half if the arms are divided.
    out.append(f'<rect x="0" y="0" width="{w}" height="{h}" '
               f'fill="{_fill(blazon.field, solid, colour)}"/>')
    if getattr(blazon, "seme", None):
        import random as _r
        _srng = _r.Random(getattr(blazon, "pattern_seed", 0) or 1)
        out.append(f'<g fill="{_fill(blazon.field2, solid, colour)}">'
                   f'{_seme_shapes(blazon.seme, _srng, w, h)}</g>')

    if getattr(blazon, "pattern", None):
        import random as _random
        from . import patterns as _pat
        _rng = _random.Random(getattr(blazon, "pattern_seed", 0))
        shapes = "".join(_pat.shapes(blazon.pattern, _rng))
        # Some patterns are drawn as outlines, stroked in currentColor: black in
        # one ink, the pattern's own tincture in colour.
        ink = PALETTE.get(blazon.field2, "#000") if colour else "#000"
        out.append(f'<g fill="{_fill(blazon.field2, solid, colour)}" '
                   f'color="{ink}">{shapes}</g>')
    elif blazon.variation:
        from .blazon import VARIATIONS
        # The count is rolled per shield; fall back to the first of the
        # variation's own counts for a blazon built before it was.
        count = (getattr(blazon, "variation_count", 0)
                 or VARIATIONS[blazon.variation]["counts"][0])
        shapes = _variation_shapes(blazon.variation, count, w, h)
        out.append(f'<g fill="{_fill(blazon.field2, solid, colour)}">{shapes}</g>')
    elif blazon.division:
        style = getattr(blazon, "line_style", "plain")
        regions = _division_regions(blazon.division, style, w, h)
        if not regions:
            regions = [_division_polygon(blazon.division, style, w, h)]
        fill = _fill(blazon.field2, solid, colour)
        for poly in regions:
            if poly:
                out.append(f'<polygon points="{_poly(poly)}" fill="{fill}"/>')

    # The ordinary, outlined so it stays distinct where its hatching is close to
    # the field's.
    if blazon.ordinary:
        style = getattr(blazon, "line_style", "plain")
        banded = _banded_ordinary(blazon.ordinary, style, w, h) if style != "plain" else []
        if banded:
            shape = f'<polygon points="{_poly(banded)}"/>'
        else:
            shape = _ordinary_shape(
                blazon.ordinary,
                _fill(blazon.ordinary_tincture, solid, colour) if colour else "#000")
        out.append(f'<g fill="{_fill(blazon.ordinary_tincture, solid, colour)}" '
                   f'stroke="#000" stroke-width="1.2">{shape}</g>')

    if getattr(blazon, "base_style", None):
        out.append(_setting(blazon, solid, colour))
    if getattr(blazon, "companion", None):
        out.append(_companions(blazon, solid, colour))

    # Charges. A chief eats the top third of the shield, so anything drawn at
    # the usual height would sit half-under it; drop the whole arrangement.
    if blazon.charge:
        fill = _fill(blazon.charge_tincture, solid, colour)
        drop = 12 if blazon.ordinary == "chief" else 0
        anchor = getattr(blazon, "charge_anchor", "centre")
        if blazon.charge_count == 1:
            # A charge anchored to one half of a divided field is drawn smaller
            # and set into that half, clear of the division line.
            # Drawn large. A charge occupying a third of the shield is normal in
            # real heraldry and essential here: detail below about 20 dots
            # across stops resolving, and these are 2 dots per SVG unit.
            if anchor == "upper":
                cx, cy, r = 50, 28, 19
            elif anchor == "dexter":
                cx, cy, r = 26, 44, 17
            else:
                cx, cy, r = _make_room(blazon, 50, 54 + drop * 0.8, 27)
            out.append(_fimbriation(blazon, cx, cy, r, solid, colour))
            out.append(f'<g fill="{fill}" stroke="#000" stroke-width="1.2">'
                       f'{_charge_path(blazon.charge, cx, cy, r, getattr(blazon, "charge_variant", None))}</g>')
        else:
            # One arrangement per count, rather than truncating a list of three:
            # two charges side by side and four in a square are the standard
            # placings, and slicing a three-spot layout would put them off
            # centre.
            n = blazon.charge_count
            d = drop * 0.6
            layouts = {
                2: ([(31, 46 + d), (69, 46 + d)], 15),
                3: ([(30, 34 + d), (70, 34 + d), (50, 76 + d * 0.4)], 13),
                4: ([(31, 32 + d), (69, 32 + d),
                     (31, 70 + d), (69, 70 + d)], 12),
                5: ([(30, 30 + d), (70, 30 + d), (50, 52 + d),
                     (30, 74 + d), (70, 74 + d)], 10),
            }
            spots, rad = _make_room_many(blazon, *layouts.get(n, layouts[3]))
            for cx, cy in spots:
                out.append(_fimbriation(blazon, cx, cy, rad, solid, colour))
                out.append(f'<g fill="{fill}" stroke="#000" stroke-width="1.1">'
                           f'{_charge_path(blazon.charge, cx, cy, rad, getattr(blazon, "charge_variant", None))}</g>')

    if getattr(blazon, "bordure", None):
        out.append(f'<g fill="none" stroke="{_fill(blazon.bordure, solid, colour)}" '
                   f'stroke-width="20">'
                   f'<path d="{SHIELD}"/></g>'
                   f'<path d="{SHIELD}" fill="none" stroke="#000" '
                   f'stroke-width="1.4" transform="translate(50,57.5) '
                   f'scale(0.80) translate(-50,-57.5)"/>')

    out.append("</g>")
    # The shield outline last, so nothing paints over it.
    out.append(f'<path d="{SHIELD}" fill="none" stroke="#000" stroke-width="{outline}"/>')
    out.append("</svg>")
    return "\n".join(out)
