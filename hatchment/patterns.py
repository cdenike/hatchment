"""Non-heraldic field treatments: fractal and geometric.

Everything else in this package is grounded in real heraldry. These two are
not, and it is worth saying so plainly: no herald ever blazoned a Sierpinski
gasket. They exist because a shield is a good frame for a pattern, and the
braille renderer is good at bold repeating forms.

Each generator returns SVG shapes drawn in the shield's own 100x115 box, in the
second tincture, over the field. Recursion depth is capped low on purpose: the
target is 50-110 dots across, so a fourth or fifth subdivision stops being a
pattern and becomes grey.
"""

import math

W, H = 100.0, 115.0
CX, CY = 50.0, 54.0


def _poly(pts):
    return '<polygon points="%s"/>' % " ".join("%.2f,%.2f" % p for p in pts)


def _ring(r_outer, r_inner):
    """An annulus as one even-odd path, so it needs no second fill colour."""
    return ('<path fill-rule="evenodd" d="'
            'M %.2f %.2f a %.2f %.2f 0 1 0 0.01 0 Z '
            'M %.2f %.2f a %.2f %.2f 0 1 0 0.01 0 Z"/>'
            % (CX, CY - r_outer, r_outer, r_outer,
               CX, CY - r_inner, r_inner, r_inner))


# --- fractal ---------------------------------------------------------------

def sierpinski(depth=4):
    """The gasket, as filled triangles at the deepest level."""
    out = []

    def rec(a, b, c, d):
        if d == 0:
            out.append(_poly([a, b, c]))
            return
        ab = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        bc = ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2)
        ca = ((c[0] + a[0]) / 2, (c[1] + a[1]) / 2)
        rec(a, ab, ca, d - 1)
        rec(ab, b, bc, d - 1)
        rec(ca, bc, c, d - 1)

    rec((CX, 4.0), (W - 2.0, H - 8.0), (2.0, H - 8.0), depth)
    return out


def mandala(petals=10, rings=5):
    """Radial petals inside concentric rings.

    The closest thing here to what people describe from the experience: rigid
    radial symmetry, repeated identical elements, and structure at more than one
    scale at once.
    """
    out = []
    R = 52.0
    # Thin rings and small petals. Fatter ones fill the shield solid, which the
    # legibility gate then rejects -- the pattern has to be mostly negative
    # space to survive both the gate and the eye.
    for i in range(rings):
        outer = R * (1.0 - i / (rings + 0.6))
        out.append(_ring(outer, outer * 0.93))
    for i in range(petals):
        a = 2 * math.pi * i / petals
        for k, rad in ((0.40, 0.10), (0.70, 0.065)):
            px, py = CX + R * k * math.cos(a), CY + R * k * math.sin(a)
            out.append('<circle cx="%.2f" cy="%.2f" r="%.2f"/>'
                       % (px, py, R * rad))
    return out


def recursive_diamonds(depth=5):
    """Lozenges nested inside each other, each rotated a step further."""
    out = []
    r = 54.0
    for i in range(depth):
        rot = i * 18.0
        rr = r * (1.0 - i / (depth + 0.4))
        pts = []
        for k in range(4):
            a = math.radians(rot + k * 90)
            pts.append((CX + rr * math.cos(a), CY + rr * math.sin(a) * 1.08))
        if i == depth - 1:
            out.append(_poly(pts))          # innermost solid, as a focus
        else:
            # Outlines for the rest. Filling alternate rings puts more than half
            # the shield under ink and the legibility gate throws it away.
            out.append('<polygon points="%s" fill="none" stroke="#000" '
                       'stroke-width="3.4"/>'
                       % " ".join("%.2f,%.2f" % p for p in pts))
    return out


def koch(depth=3):
    """A Koch snowflake, filled."""
    def seg(p, q, d):
        if d == 0:
            return [p]
        px, py = p
        qx, qy = q
        dx, dy = (qx - px) / 3.0, (qy - py) / 3.0
        a = (px + dx, py + dy)
        b = (px + 2 * dx, py + 2 * dy)
        ang = math.atan2(qy - py, qx - px) - math.pi / 3
        L = math.hypot(dx, dy)
        tip = (a[0] + L * math.cos(ang), a[1] + L * math.sin(ang))
        return seg(p, a, d - 1) + seg(a, tip, d - 1) + seg(tip, b, d - 1) + seg(b, q, d - 1)

    R = 48.0
    corners = [(CX + R * math.cos(math.radians(90 + i * 120)),
                CY - R * math.sin(math.radians(90 + i * 120))) for i in range(3)]
    pts = []
    for i in range(3):
        pts += seg(corners[i], corners[(i + 1) % 3], depth)
    return [_poly(pts)]


# --- geometric -------------------------------------------------------------

def concentric(rings=7):
    """Thin rings, not fat ones.

    An inner radius of 0.72 makes each ring thicker than the gap outside it, so
    seven of them merge into a filled disc. 0.88 leaves the gaps wider than the
    strokes, which is what makes it read as rings at all.
    """
    out = []
    R = 55.0
    for i in range(rings):
        outer = R * (1.0 - i / float(rings + 0.5))
        out.append(_ring(outer, outer * 0.91))
    return out


def spokes(count=16):
    """Alternating wedges from the centre, like a ship's compass rose."""
    out = []
    R = W + H
    for i in range(0, count, 2):
        a1 = 2 * math.pi * i / count
        a2 = 2 * math.pi * (i + 1) / count
        out.append(_poly([(CX, CY),
                          (CX + R * math.cos(a1), CY + R * math.sin(a1)),
                          (CX + R * math.cos(a2), CY + R * math.sin(a2))]))
    return out


def triangles(cols=6):
    """A triangular tessellation: every other triangle filled."""
    out = []
    w = W / cols
    h = w * 0.92
    rows = int(H / h) + 2
    for r in range(rows):
        y0, y1 = r * h - 4, (r + 1) * h - 4
        for c in range(cols + 1):
            x = c * w
            if (r + c) % 2:
                out.append(_poly([(x, y0), (x + w, y0), (x + w / 2, y1)]))
            else:
                out.append(_poly([(x + w / 2, y0), (x + w, y1), (x, y1)]))
    return out


def nested_squares(depth=6):
    out = []
    R = 50.0
    for i in range(depth):
        rr = R * (1.0 - i / float(depth + 1))
        rot = i * 15.0
        pts = []
        for k in range(4):
            a = math.radians(rot + 45 + k * 90)
            pts.append((CX + rr * math.cos(a), CY + rr * math.sin(a) * 1.06))
        if i == depth - 1:
            out.append(_poly(pts))
        else:
            out.append('<polygon points="%s" fill="none" stroke="#000" '
                       'stroke-width="3.0"/>'
                       % " ".join("%.2f,%.2f" % p for p in pts))
    return out


FRACTAL = {
    "sierpinski gasket": sierpinski,
    "mandala": mandala,
    "nested lozenges": recursive_diamonds,
    "koch snowflake": koch,
}

GEOMETRIC = {
    "concentric rings": concentric,
    "compass spokes": spokes,
    "triangular tessellation": triangles,
    "nested squares": nested_squares,
}

ALL = dict(FRACTAL)
ALL.update(GEOMETRIC)


def shapes(name):
    fn = ALL.get(name)
    return fn() if fn else []
