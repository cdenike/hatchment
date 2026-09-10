"""Non-heraldic field treatments: fractal and geometric.

Everything else in this package is grounded in real heraldry. These two are
not, and it is worth saying so plainly: no herald ever blazoned a Sierpinski
gasket. They exist because a shield is a good frame for a pattern, and the
braille renderer is good at bold repeating forms.

Every generator takes the roll's rng and draws its own parameters from it --
depth, count, rotation, phase, mode. Without that a pattern name would always
produce the same picture, and twenty names would give you twenty pictures rather
than twenty families of them.

Recursion depth is capped low on purpose: the target is 50-110 dots across, so a
fourth or fifth subdivision stops being a pattern and becomes grey. Ink is kept
under about half the shield, because the legibility gate discards anything
denser -- a pattern that fails it does not look bad, it simply never appears.
"""

import math

W, H = 100.0, 115.0
CX, CY = 50.0, 54.0


def _pick(rng, label, roll):
    """Roll a pattern's headline parameter, and remember how to say it.

    Every generator opens by rolling the one number that decides what the
    picture is -- iterations, points, rings, spokes. The blazon wants to name
    it, but the drawing happens later and elsewhere, from a fresh generator
    seeded the same way. Rather than duplicate each roll in a table that would
    silently drift out of step, the generator records its own answer on the rng
    it was handed, and `headline()` below replays the roll to read it back.
    """
    value = roll()
    # The template and the number travel separately, because how a number is
    # written is the blazon's business: it spells its counts in words.
    rng.headline = (label, int(value))
    return value


def headline(pool, name, seed):
    """(template, value) the named pattern will draw from `seed`, or None.

    The generator is run for its parameter and its shapes are thrown away. It
    is pure string-building with no I/O, and running it is what keeps the words
    honest: the number named is the number rolled, from the same seed the
    drawing will use, rather than a second guess at it kept in a table.
    """
    import random
    rng = random.Random(seed)
    rng.headline = None
    try:
        pool[name](rng)
    except Exception:
        return None
    return rng.headline


def _poly(pts):
    return '<polygon points="%s"/>' % " ".join("%.2f,%.2f" % p for p in pts)


def _outline(pts, width=3.2):
    return ('<polygon points="%s" fill="none" stroke="#000" stroke-width="%.1f"/>'
            % (" ".join("%.2f,%.2f" % p for p in pts), width))


def _ring(r_outer, r_inner, cx=CX, cy=CY):
    """An annulus as one even-odd path, so it needs no second fill colour."""
    return ('<path fill-rule="evenodd" d="'
            'M %.2f %.2f a %.2f %.2f 0 1 0 0.01 0 Z '
            'M %.2f %.2f a %.2f %.2f 0 1 0 0.01 0 Z"/>'
            % (cx, cy - r_outer, r_outer, r_outer,
               cx, cy - r_inner, r_inner, r_inner))


def _regular(n, r, rot=0.0, cx=CX, cy=CY, squash=1.06):
    return [(cx + r * math.cos(math.radians(rot + i * 360.0 / n)),
             cy + r * math.sin(math.radians(rot + i * 360.0 / n)) * squash)
            for i in range(n)]


# --- fractal ---------------------------------------------------------------

def sierpinski(rng):
    depth = _pick(rng, "of %s iterations", lambda: rng.randint(3, 5))
    inverted = rng.random() < 0.4
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

    if inverted:
        rec((CX, H - 8.0), (W - 2.0, 6.0), (2.0, 6.0), depth)
    else:
        rec((CX, 4.0), (W - 2.0, H - 8.0), (2.0, H - 8.0), depth)
    return out


def sierpinski_carpet(rng):
    depth = _pick(rng, "of %s iterations", lambda: rng.randint(2, 3))
    out = []

    def rec(x, y, w, h, d):
        w3, h3 = w / 3.0, h / 3.0
        # The punched-out centre at this level is what gets drawn.
        out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f"/>'
                   % (x + w3, y + h3, w3, h3))
        if d == 0:
            return
        for r in range(3):
            for c in range(3):
                if r == 1 and c == 1:
                    continue
                rec(x + c * w3, y + r * h3, w3, h3, d - 1)

    rec(4.0, 6.0, W - 8.0, H - 16.0, depth)
    return out


def vicsek(rng):
    depth = _pick(rng, "of %s iterations", lambda: rng.randint(2, 3))
    saltire = rng.random() < 0.5
    out = []

    def rec(x, y, w, h, d):
        if d == 0:
            out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f"/>'
                       % (x, y, w, h))
            return
        w3, h3 = w / 3.0, h / 3.0
        cells = ([(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)] if saltire
                 else [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)])
        for c, r in cells:
            rec(x + c * w3, y + r * h3, w3, h3, d - 1)

    rec(6.0, 10.0, W - 12.0, H - 24.0, depth)
    return out


def koch(rng):
    depth = _pick(rng, "of %s iterations", lambda: rng.randint(2, 4))
    sides = rng.choice([3, 4, 6])

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
        return (seg(p, a, d - 1) + seg(a, tip, d - 1)
                + seg(tip, b, d - 1) + seg(b, q, d - 1))

    corners = _regular(sides, 46.0, rot=rng.choice([0, 30, 90]), squash=1.0)
    pts = []
    for i in range(sides):
        pts += seg(corners[i], corners[(i + 1) % sides], depth)
    # Outlined, not filled: a filled snowflake covers most of the shield and the
    # gate discards it, and the outline shows the recursion better anyway.
    return ['<polygon points="%s" fill="none" stroke="#000" stroke-width="3.2"/>'
            % " ".join("%.2f,%.2f" % q for q in pts)]


def mandala(rng):
    petals = _pick(rng, "of %s petals", lambda: rng.choice([6, 8, 10, 12, 16]))
    rings = rng.randint(3, 6)
    inner, outer_r = rng.choice([(0.40, 0.10), (0.34, 0.12), (0.46, 0.08)])
    out = []
    R = 52.0
    for i in range(rings):
        o = R * (1.0 - i / (rings + 0.6))
        out.append(_ring(o, o * 0.93))
    for i in range(petals):
        a = 2 * math.pi * i / petals
        for k, rad in ((inner, outer_r), (0.70, outer_r * 0.65)):
            px, py = CX + R * k * math.cos(a), CY + R * k * math.sin(a)
            out.append('<circle cx="%.2f" cy="%.2f" r="%.2f"/>'
                       % (px, py, R * rad))
    return out


def nested_polygons(rng):
    """Nested regular polygons, each rotated a step on from the last."""
    depth = rng.randint(4, 8)
    sides = _pick(rng, "of %s sides", lambda: rng.choice([3, 4, 5, 6, 8]))
    step = rng.choice([8, 12, 15, 18, 24])
    out = []
    R = 54.0
    for i in range(depth):
        rr = R * (1.0 - i / (depth + 0.4))
        pts = _regular(sides, rr, rot=i * step)
        out.append(_poly(pts) if i == depth - 1 else _outline(pts))
    return out


def h_tree(rng):
    depth = _pick(rng, "of %s iterations", lambda: rng.randint(3, 5))
    out = []

    def rec(x, y, w, h, d):
        if d == 0:
            return
        t = max(1.4, 2.0 * d / depth)
        out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f"/>'
                   % (x - w / 2, y - t / 2, w, t))
        for sx in (-1, 1):
            nx = x + sx * w / 2
            out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f"/>'
                       % (nx - t / 2, y - h / 2, t, h))
            for sy in (-1, 1):
                rec(nx, y + sy * h / 2, w / 2, h / 2, d - 1)

    rec(CX, CY, 62.0, 54.0, depth)
    return out


def cantor_bars(rng):
    depth = _pick(rng, "of %s iterations", lambda: rng.randint(3, 5))
    rows = []

    def rec(x, w, d):
        rows.append((d, x, w))
        if d == 0:
            return
        rec(x, w / 3.0, d - 1)
        rec(x + 2 * w / 3.0, w / 3.0, d - 1)

    rec(5.0, W - 10.0, depth)
    out = []
    band = (H - 20.0) / (depth + 1)
    for d, x, w in rows:
        y = 10.0 + (depth - d) * band
        out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f"/>'
                   % (x, y, w, band * 0.55))
    return out


def flower_of_life(rng):
    """Overlapping circles on a hex lattice, drawn as outlines."""
    rings = _pick(rng, "of %s rings", lambda: rng.randint(2, 3))
    r = rng.choice([13.0, 16.0, 19.0])
    out = []
    for q in range(-rings, rings + 1):
        for s in range(-rings, rings + 1):
            if abs(q + s) > rings:
                continue
            x = CX + r * 1.5 * q
            y = CY + r * math.sqrt(3) * (s + q / 2.0)
            out.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" '
                       'stroke="#000" stroke-width="2.6"/>' % (x, y, r))
    return out


def recursive_circles(rng):
    depth = _pick(rng, "of %s iterations", lambda: rng.randint(3, 4))
    kids = rng.choice([3, 4, 5, 6])
    out = []

    def rec(x, y, r, d):
        out.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" '
                   'stroke="#000" stroke-width="%.1f"/>'
                   % (x, y, r, max(1.8, r * 0.10)))
        if d == 0:
            return
        for i in range(kids):
            a = 2 * math.pi * i / kids
            rec(x + r * 0.62 * math.cos(a), y + r * 0.62 * math.sin(a),
                r * 0.36, d - 1)

    rec(CX, CY, 34.0, depth)
    return out


# --- geometric -------------------------------------------------------------

def concentric(rng):
    rings = _pick(rng, "of %s", lambda: rng.randint(5, 9))
    thin = rng.choice([0.90, 0.92, 0.94])
    out = []
    R = 55.0
    for i in range(rings):
        outer = R * (1.0 - i / float(rings + 0.5))
        out.append(_ring(outer, outer * thin))
    return out


def spokes(rng):
    count = _pick(rng, "of %s", lambda: rng.choice([8, 12, 16, 20, 24]))
    off = rng.random() * 2 * math.pi / count
    out = []
    R = W + H
    for i in range(0, count, 2):
        a1 = 2 * math.pi * i / count + off
        a2 = 2 * math.pi * (i + 1) / count + off
        out.append(_poly([(CX, CY),
                          (CX + R * math.cos(a1), CY + R * math.sin(a1)),
                          (CX + R * math.cos(a2), CY + R * math.sin(a2))]))
    return out


def triangles(rng):
    cols = _pick(rng, "of %s columns", lambda: rng.randint(4, 8))
    w = W / cols
    h = w * rng.choice([0.82, 0.92, 1.05])
    out = []
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


def nested_squares(rng):
    depth = _pick(rng, "of %s", lambda: rng.randint(4, 8))
    step = rng.choice([0, 10, 15, 22])
    out = []
    R = 50.0
    for i in range(depth):
        rr = R * (1.0 - i / float(depth + 1))
        pts = _regular(4, rr, rot=45 + i * step)
        out.append(_poly(pts) if i == depth - 1 else _outline(pts, 3.0))
    return out


def hex_grid(rng):
    r = _pick(rng, "at %d-unit spacing", lambda: rng.choice([9.0, 11.0, 13.0]))
    out = []
    dy = r * math.sqrt(3)
    rows = int(H / dy) + 3
    cols = int(W / (r * 1.5)) + 3
    for row in range(-1, rows):
        for col in range(-1, cols):
            if (row + col) % 2:
                continue
            x = col * r * 1.5
            y = row * dy + (dy / 2 if col % 2 else 0)
            out.append(_poly(_regular(6, r * 0.92, cx=x, cy=y, squash=1.0)))
    return out


def star_polygon(rng):
    """A {n/k} star: n points, every k-th joined. Pentagram and up."""
    n = _pick(rng, "of %s points", lambda: rng.choice([5, 7, 8, 9, 11]))
    k = 2 if n < 7 else rng.choice([2, 3])
    pts = _regular(n, 50.0, rot=-90, squash=1.05)
    order = [pts[(i * k) % n] for i in range(n)]
    return ['<polygon points="%s" fill-rule="evenodd"/>'
            % " ".join("%.2f,%.2f" % p for p in order)]


def lattice(rng):
    """Diagonal bars, in one direction or crossed."""
    spacing = _pick(rng, "at %d-unit spacing", lambda: rng.choice([9.0, 12.0, 15.0]))
    thick = spacing * rng.choice([0.22, 0.30, 0.38])
    both = rng.random() < 0.5
    out = []
    span = int((W + H) / spacing) + 2
    for i in range(-span, span):
        x = i * spacing
        out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" '
                   'transform="rotate(45 %.2f %.2f)"/>'
                   % (x, -H, thick, H * 3, CX, CY))
        if both:
            out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" '
                       'transform="rotate(-45 %.2f %.2f)"/>'
                       % (x, -H, thick, H * 3, CX, CY))
    return out


def square_grid(rng):
    cols = _pick(rng, "of %s columns", lambda: rng.randint(4, 9))
    mode = rng.choice(["check", "outline", "dots"])
    out = []
    s = W / cols
    rows = int(H / s) + 1
    for r in range(rows):
        for c in range(cols):
            x, y = c * s, r * s
            if mode == "check":
                if (r + c) % 2:
                    out.append('<rect x="%.2f" y="%.2f" width="%.2f" '
                               'height="%.2f"/>' % (x, y, s, s))
            elif mode == "outline":
                out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" '
                           'fill="none" stroke="#000" stroke-width="2.4"/>'
                           % (x, y, s, s))
            else:
                out.append('<circle cx="%.2f" cy="%.2f" r="%.2f"/>'
                           % (x + s / 2, y + s / 2, s * 0.24))
    return out


def sunburst(rng):
    """Rays from the centre, with an optional ring around them."""
    rays = _pick(rng, "of %s rays", lambda: rng.choice([12, 16, 20, 24]))
    disc = rng.random() < 0.6
    out = []
    R = W + H
    for i in range(rays):
        a = 2 * math.pi * i / rays
        wdt = math.pi / rays * 0.34
        out.append(_poly([(CX, CY),
                          (CX + R * math.cos(a - wdt), CY + R * math.sin(a - wdt)),
                          (CX + R * math.cos(a + wdt), CY + R * math.sin(a + wdt))]))
    if disc:
        out.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" '
                   'stroke="#000" stroke-width="4"/>' % (CX, CY, 20.0))
    return out


def moire(rng):
    """Two ring sets on slightly different centres, which interfere."""
    n = _pick(rng, "of %s", lambda: rng.randint(6, 9))
    dx = rng.choice([6.0, 9.0, 12.0])
    out = []
    R = 60.0
    for cx in (CX - dx / 2, CX + dx / 2):
        for i in range(n):
            outer = R * (1.0 - i / float(n + 0.5))
            out.append(_ring(outer, outer * 0.95, cx=cx))
    return out


FRACTAL = {
    "sierpinski gasket": sierpinski,
    "sierpinski carpet": sierpinski_carpet,
    "vicsek fractal": vicsek,
    "koch snowflake": koch,
    "mandala": mandala,
    "nested polygons": nested_polygons,
    "h-tree": h_tree,
    "cantor bars": cantor_bars,
    "flower of life": flower_of_life,
    "recursive circles": recursive_circles,
}

GEOMETRIC = {
    "concentric rings": concentric,
    "compass spokes": spokes,
    "triangular tessellation": triangles,
    "nested squares": nested_squares,
    "hexagonal grid": hex_grid,
    "star polygon": star_polygon,
    "diagonal lattice": lattice,
    "square grid": square_grid,
    "sunburst": sunburst,
    "moire rings": moire,
}

ALL = dict(FRACTAL)
ALL.update(GEOMETRIC)


def shapes(name, rng):
    fn = ALL.get(name)
    return fn(rng) if fn else []
