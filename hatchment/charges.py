"""Charges added in 0.1.8: beasts, birds, small creatures, the mythic, and the
symbols heraldry shares with older traditions.

Each is drawn once in a 200-unit box centred on the origin -- x right, y down,
the charge filling roughly -100..100 -- and placed by draw._charge_path with a
translate and a scale. Authoring in a fixed box keeps the numbers readable and
the shapes comparable; the older charges predate this and are written against
their radius instead.

The rules are the rest of the vocabulary's. Silhouettes, because a braille
cell has one bit. Limbs, strings and antennae are filled polygons rather than
strokes, so they take the charge's tincture in a colour export instead of the
outline's black. Detail that must read as a gap -- an eye, a rib, a nail hole
-- is drawn in white, as the bee's stripes already are.
"""

import math

WHITE = ' fill="#fff"'


def _pts(points):
    return " ".join("%.1f,%.1f" % p for p in points)


def _poly(points, extra=""):
    return '<polygon points="%s"%s/>' % (_pts(points), extra)


def _mirror(points):
    return [(-x, y) for x, y in points]


def _both(points, extra=""):
    """A shape and its mirror image across the vertical axis."""
    return _poly(points, extra) + _poly(_mirror(points), extra)


def _circle(cx, cy, r, extra=""):
    return '<circle cx="%s" cy="%s" r="%s"%s/>' % (cx, cy, r, extra)


def _ellipse(cx, cy, rx, ry, extra="", rotate=0):
    turn = ' transform="rotate(%s %s %s)"' % (rotate, cx, cy) if rotate else ""
    return ('<ellipse cx="%s" cy="%s" rx="%s" ry="%s"%s%s/>'
            % (cx, cy, rx, ry, extra, turn))


def _rect(x, y, w, h, extra=""):
    return '<rect x="%s" y="%s" width="%s" height="%s"%s/>' % (x, y, w, h, extra)


def _path(d, extra=""):
    return '<path d="%s"%s/>' % (d, extra)


def _ring(cx, cy, outer, inner, extra=""):
    """An annulus as one even-odd path."""
    return ('<path fill-rule="evenodd" d="M %s %s a %s %s 0 1 0 0.01 0 Z '
            'M %s %s a %s %s 0 1 0 0.01 0 Z"%s/>'
            % (cx, cy - outer, outer, outer, cx, cy - inner, inner, inner, extra))


def _band(points, width, extra="", closed=False):
    """A polyline thickened into a polygon.

    Filled rather than stroked, so a leg or a string is painted in the charge's
    tincture; a stroke would take the outline's black instead.
    """
    if closed:
        points = list(points) + [points[0], points[1]]
    half = width / 2.0
    left, right = [], []
    n = len(points)
    for i, (x, y) in enumerate(points):
        a = points[max(0, i - 1)]
        b = points[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length * half, dx / length * half
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    return _poly(left + right[::-1], extra)


def _rotate(points, degrees):
    a = math.radians(degrees)
    c, s = math.cos(a), math.sin(a)
    return [(x * c - y * s, x * s + y * c) for x, y in points]


def _eye(x, y, r=4):
    return _circle(x, y, r, WHITE)


SHAPES = {}

# --- beasts ------------------------------------------------------------------
# Passant or courant, facing dexter (the viewer's left), as the lion faces.

SHAPES["wolf"] = _poly([
    (-98, -30), (-80, -38), (-66, -44), (-64, -70), (-54, -48), (-46, -72),
    (-40, -42), (-30, -26), (0, -24), (40, -26), (58, -22), (70, -30),
    (92, -10), (98, 20), (84, 26), (74, 4), (62, 0), (60, 20), (66, 50),
    (64, 92), (52, 92), (48, 54), (40, 40), (38, 56), (36, 92), (26, 92),
    (26, 50), (10, 34), (-24, 34), (-26, 56), (-22, 92), (-32, 92), (-36, 52),
    (-40, 40), (-44, 60), (-42, 92), (-54, 92), (-56, 50), (-58, 20),
    (-66, 0), (-80, -14), (-94, -20)]) + _eye(-72, -30)

SHAPES["bear"] = _poly([
    (-96, -4), (-92, -18), (-76, -30), (-72, -46), (-60, -50), (-54, -38),
    (-36, -46), (-10, -56), (24, -48), (58, -38), (80, -18), (86, 6), (78, 32),
    (80, 92), (60, 92), (56, 58), (46, 58), (44, 92), (24, 92), (20, 50),
    (-22, 50), (-24, 92), (-40, 92), (-42, 56), (-50, 56), (-52, 92),
    (-72, 92), (-70, 30), (-76, 12), (-86, 6)]) + _eye(-74, -18)

SHAPES["boar"] = _poly([
    (-98, -2), (-94, -16), (-80, -22), (-70, -40), (-62, -28), (-50, -44),
    (-38, -36), (-30, -50), (-20, -40), (-10, -54), (0, -42), (12, -54),
    (22, -42), (34, -50), (44, -38), (62, -34), (78, -24), (88, -30),
    (90, -20), (84, -12), (88, 10), (76, 30), (74, 90), (60, 90), (58, 40),
    (44, 40), (42, 90), (28, 90), (28, 42), (-30, 42), (-32, 90), (-46, 90),
    (-48, 40), (-58, 36), (-60, 90), (-74, 90), (-72, 24), (-84, 14),
    (-94, 10)]) + _poly([(-84, 4), (-68, -6), (-72, 8)], WHITE) + _eye(-72, -18)

SHAPES["fox"] = _poly([
    (-98, -20), (-84, -24), (-72, -34), (-70, -62), (-60, -40), (-52, -60),
    (-48, -34), (-38, -22), (30, -20), (50, -24), (70, -44), (90, -66),
    (100, -58), (96, -36), (80, -14), (62, -4), (58, 20), (64, 92), (52, 92),
    (46, 40), (36, 36), (32, 92), (20, 92), (20, 30), (-30, 30), (-32, 92),
    (-44, 92), (-46, 34), (-52, 32), (-56, 92), (-68, 92), (-66, 22),
    (-72, 6), (-86, -6)]) + _eye(-74, -18, 3.5)

SHAPES["bull"] = _poly([
    (-96, -10), (-92, -28), (-84, -34), (-100, -60), (-92, -64), (-78, -42),
    (-68, -44), (-62, -68), (-54, -66), (-60, -40), (-48, -34), (-30, -44),
    (20, -44), (60, -38), (78, -26), (86, -10), (96, 20), (92, 26), (82, 6),
    (80, 30), (82, 92), (64, 92), (60, 50), (44, 48), (44, 92), (26, 92),
    (24, 48), (-26, 48), (-28, 92), (-46, 92), (-48, 46), (-56, 44),
    (-58, 92), (-76, 92), (-74, 26), (-84, 10)]) + _eye(-80, -16)

SHAPES["ram"] = _poly([
    (-94, -4), (-88, -22), (-74, -34), (-56, -38), (-40, -30), (-20, -36),
    (10, -38), (40, -36), (66, -30), (82, -14), (86, 8), (78, 30), (78, 92),
    (62, 92), (60, 46), (44, 46), (44, 92), (28, 92), (26, 46), (-30, 46),
    (-30, 92), (-46, 92), (-48, 46), (-56, 44), (-56, 92), (-72, 92),
    (-70, 24), (-78, 8)]) + _ring(-58, -46, 22, 12) + _eye(-80, -14, 3.5)

SHAPES["hare"] = _poly([
    (-96, -2), (-84, -16), (-72, -18), (-80, -60), (-70, -62), (-62, -22),
    (-56, -60), (-48, -58), (-52, -18), (-40, -8), (-10, -18), (30, -14),
    (60, -4), (74, -12), (84, -6), (76, 6), (72, 24), (96, 52), (90, 62),
    (62, 40), (40, 40), (10, 36), (-30, 34), (-60, 56), (-98, 58), (-96, 48),
    (-64, 40), (-58, 24), (-72, 12), (-88, 8)]) + _eye(-78, -6, 3)

SHAPES["hound"] = _poly([
    (-98, -28), (-86, -30), (-74, -40), (-66, -56), (-60, -40), (-52, -30),
    (-40, -16), (0, -12), (40, -16), (64, -22), (90, -48), (96, -44),
    (72, -10), (64, 6), (70, 30), (94, 60), (86, 68), (56, 40), (40, 34),
    (0, 30), (-30, 28), (-56, 44), (-96, 58), (-98, 48), (-64, 30), (-58, 14),
    (-66, -4), (-80, -12), (-94, -18)]) + _eye(-82, -26, 3)

SHAPES["elephant"] = (_poly([
    (-96, 40), (-90, 20), (-86, -20), (-80, -50), (-60, -70), (-30, -76),
    (20, -72), (60, -60), (84, -40), (90, -10), (96, 20), (90, 22), (86, 8),
    (84, 30), (84, 92), (62, 92), (60, 50), (44, 50), (44, 92), (22, 92),
    (20, 48), (-30, 48), (-32, 92), (-54, 92), (-56, 40), (-62, 20),
    (-70, 20), (-72, 60), (-84, 62)])
    + _path("M -60,-56 Q -16,-62 -18,-8 Q -40,12 -62,-12 Z")
    + _poly([(-70, 10), (-46, 22), (-68, 20)], WHITE) + _eye(-68, -40))

# --- birds -------------------------------------------------------------------

SHAPES["owl"] = (
    _path("M -60,-60 L -40,-92 L -24,-66 Q 0,-74 24,-66 L 40,-92 L 60,-60 "
          "Q 80,-20 70,30 Q 60,80 30,96 L -30,96 Q -60,80 -70,30 "
          "Q -80,-20 -60,-60 Z")
    + _circle(-26, -34, 20, WHITE) + _circle(26, -34, 20, WHITE)
    + _circle(-26, -34, 9) + _circle(26, -34, 9)
    + _poly([(-9, -14), (9, -14), (0, 6)], WHITE))

SHAPES["raven"] = _poly([
    (-98, -40), (-74, -50), (-60, -64), (-40, -66), (-26, -54), (-14, -30),
    (30, -24), (70, -10), (100, 4), (96, 16), (60, 20), (40, 34), (10, 40),
    (-10, 40), (-2, 70), (10, 92), (-4, 92), (-14, 72), (-24, 92), (-38, 92),
    (-24, 66), (-30, 40), (-52, 26), (-62, 6), (-64, -24),
    (-74, -38)]) + _eye(-52, -52)

SHAPES["swan"] = (
    _path("M -60,30 Q -82,10 -58,-2 L 40,-6 Q 70,-8 96,-30 Q 86,20 50,40 Z")
    + _path("M -20,-4 Q 20,-60 84,-72 Q 62,-30 40,-6 Z")
    + _band([(-50, -2), (-70, -24), (-72, -52), (-56, -72), (-60, -88)], 14)
    + _ellipse(-66, -88, 13, 9)
    + _poly([(-76, -92), (-98, -84), (-76, -82)]) + _eye(-64, -90, 3))

# A martlet is a swallow borne without feet -- tufts where the legs would be.
# Round head, folded wing, forked tail: a raised wing reads as a fin.
SHAPES["martlet"] = (
    _path("M -66,-30 Q -20,-44 30,-26 L 96,-52 L 70,-8 L 98,20 L 40,6 "
          "Q -20,26 -70,6 Z")
    + _circle(-62, -14, 20)
    + _poly([(-78, -20), (-98, -12), (-78, -6)])
    + _path("M -34,-28 Q 6,-62 60,-40 Q 20,-22 -20,-12 Z")
    + _band([(-22, -18), (40, -34)], 3, WHITE)
    + _poly([(-24, 16), (-18, 40), (-10, 18)])
    + _poly([(-4, 16), (2, 40), (10, 16)]) + _eye(-68, -18, 3))

SHAPES["cockerel"] = _poly([
    (-90, -30), (-76, -40), (-80, -58), (-70, -56), (-68, -72), (-58, -60),
    (-52, -74), (-46, -56), (-40, -40), (-34, -10), (0, 0), (20, -20),
    (30, -60), (50, -86), (70, -80), (58, -50), (80, -70), (96, -50),
    (74, -30), (96, -10), (80, 10), (60, 20), (40, 40), (10, 46), (8, 70),
    (20, 92), (4, 92), (-2, 74), (-10, 92), (-24, 92), (-10, 68), (-14, 46),
    (-40, 32), (-54, 4), (-64, -16), (-70, -12), (-74, -20),
    (-80, -26)]) + _eye(-60, -34, 3)

# --- small creatures ---------------------------------------------------------

SHAPES["butterfly"] = (
    _path("M -4,-8 C -20,-70 -80,-96 -94,-60 C -100,-24 -60,0 -4,4 Z")
    + _path("M 4,-8 C 20,-70 80,-96 94,-60 C 100,-24 60,0 4,4 Z")
    + _path("M -4,6 C -50,8 -86,40 -70,72 C -54,96 -18,72 -4,26 Z")
    + _path("M 4,6 C 50,8 86,40 70,72 C 54,96 18,72 4,26 Z")
    + _ellipse(0, 4, 9, 48)
    + _band([(-3, -40), (-14, -70), (-30, -86)], 5)
    + _band([(3, -40), (14, -70), (30, -86)], 5)
    + _circle(-30, -86, 6) + _circle(30, -86, 6)
    + _circle(-56, -50, 11, WHITE) + _circle(56, -50, 11, WHITE)
    + _circle(-46, 50, 8, WHITE) + _circle(46, 50, 8, WHITE))

SHAPES["bat"] = _poly([
    (0, -26), (-10, -52), (-18, -26), (-32, -22), (-62, -46), (-100, -34),
    (-88, -14), (-94, 8), (-72, -2), (-66, 22), (-46, 8), (-32, 28),
    (-16, 12), (-8, 36), (0, 42), (8, 36), (16, 12), (32, 28), (46, 8),
    (66, 22), (72, -2), (94, 8), (88, -14), (100, -34), (62, -46), (32, -22),
    (18, -26), (10, -52)]) + _eye(-7, -18, 3) + _eye(7, -18, 3)


def _spider():
    legs = [[(10, -24), (40, -60), (56, -96)], [(14, -10), (56, -36), (86, -56)],
            [(16, 8), (60, 4), (94, 26)], [(14, 24), (50, 50), (66, 94)]]
    out = "".join(_band(leg, 8) + _band(_mirror(leg), 8) for leg in legs)
    return (out + _ellipse(0, 20, 28, 36) + _circle(0, -28, 20)
            + _eye(-7, -34) + _eye(7, -34))


SHAPES["spider"] = _spider()


def _scorpion():
    legs = [[(-16, -8), (-50, -14), (-66, 4)], [(-18, 6), (-54, 10), (-66, 30)],
            [(-16, 20), (-48, 32), (-58, 54)]]
    arm = [(-10, -34), (-40, -54), (-52, -76)]
    claw = [(-52, -76), (-72, -96), (-64, -72), (-84, -78), (-58, -60)]
    out = "".join(_band(l, 6) + _band(_mirror(l), 6) for l in legs)
    out += _band(arm, 10) + _band(_mirror(arm), 10) + _both(claw)
    out += _band([(0, 34), (2, 58), (16, 78), (36, 84), (52, 72), (54, 54)], 12)
    out += _poly([(46, 50), (62, 40), (60, 60)])
    return out + _ellipse(0, 6, 22, 32) + _ellipse(0, -30, 17, 13)


SHAPES["scorpion"] = _scorpion()


def _serpent():
    pts = [(40 * math.sin(t / 40.0 * 2.2 * math.pi), -66 + t * 4.0)
           for t in range(41)]
    hx, hy = pts[0]
    return (_band(pts, 18) + _ellipse(round(hx, 1), hy - 12, 15, 19)
            + _poly([(hx - 3, hy - 30), (hx - 10, hy - 44), (hx, hy - 36),
                     (hx + 10, hy - 44), (hx + 3, hy - 30)])
            + _eye(round(hx - 6, 1), hy - 16, 3))


SHAPES["serpent"] = _serpent()


def _frog():
    hind = [(-30, 30), (-70, 46), (-58, 78), (-90, 92)]
    fore = [(-32, -12), (-64, -26), (-80, -4)]
    return (_band(hind, 14) + _band(_mirror(hind), 14)
            + _band(fore, 12) + _band(_mirror(fore), 12)
            + _ellipse(0, 10, 40, 48) + _ellipse(0, -38, 34, 24)
            + _circle(-22, -58, 12) + _circle(22, -58, 12)
            + _eye(-22, -60, 5) + _eye(22, -60, 5))


SHAPES["frog"] = _frog()


def _tortoise():
    flippers = (_ellipse(-52, -40, 22, 12, rotate=-40)
                + _ellipse(52, -40, 22, 12, rotate=40)
                + _ellipse(-50, 50, 20, 11, rotate=40)
                + _ellipse(50, 50, 20, 11, rotate=-40))
    hexagon = [(26 * math.cos(math.radians(a)), 4 + 26 * math.sin(math.radians(a)))
               for a in range(0, 360, 60)]
    shell = _ellipse(0, 4, 58, 64) + _band(hexagon, 5, WHITE, closed=True)
    for x, y in hexagon:
        shell += _band([(x, y), (x * 2.1, 4 + (y - 4) * 2.3)], 5, WHITE)
    return (flippers + _ellipse(0, -76, 16, 20)
            + _poly([(-6, 64), (6, 64), (0, 88)]) + shell)


SHAPES["tortoise"] = _tortoise()


def _crab():
    legs = [[(-44, 20), (-80, 30), (-94, 54)], [(-40, 34), (-72, 52), (-80, 80)],
            [(-48, 4), (-86, 6), (-100, 26)]]
    arm = [(-34, -6), (-58, -36), (-58, -60)]
    claw = [(-58, -60), (-86, -84), (-70, -60), (-90, -58), (-64, -44)]
    out = "".join(_band(l, 8) + _band(_mirror(l), 8) for l in legs)
    out += _band(arm, 12) + _band(_mirror(arm), 12) + _both(claw)
    out += _band([(-12, -8), (-16, -26)], 5) + _band([(12, -8), (16, -26)], 5)
    return (out + _circle(-16, -28, 7) + _circle(16, -28, 7)
            + _ellipse(0, 14, 52, 34))


SHAPES["crab"] = _crab()

SHAPES["dolphin"] = (
    _path("M -92,-12 L -72,-20 Q -44,-74 18,-64 Q 72,-54 82,-2 Q 86,30 72,58 "
          "L 98,88 L 62,80 L 50,98 L 54,62 Q 60,20 30,-8 Q 0,-28 -40,-8 "
          "L -62,0 Z")
    + _poly([(-12, -62), (8, -90), (22, -60)])
    + _poly([(-30, -14), (-42, 22), (-14, -4)]) + _eye(-52, -26))


def _escallop():
    fan = _path("M 0,74 L -88,-6 Q -92,-40 -70,-66 Q -40,-96 0,-98 "
                "Q 40,-96 70,-66 Q 92,-40 88,-6 Z")
    ears = _poly([(-34, 64), (-46, 94), (46, 94), (34, 64)])
    ribs = "".join(_band([(0, 70), rim], 5, WHITE) for rim in
                   [(-70, -50), (-40, -84), (0, -92), (40, -84), (70, -50)])
    return ears + fan + ribs


SHAPES["escallop"] = _escallop()

# --- the mythic --------------------------------------------------------------
# Rampant or segreant where heraldry rears them, facing dexter like the lion.

SHAPES["dragon"] = (_poly([
    (-62, -70), (-46, -80), (-34, -98), (-28, -80), (-14, -72), (-16, -52),
    (-4, -32), (20, -12), (30, 18), (20, 48), (34, 68), (30, 92), (14, 92),
    (10, 70), (-6, 56), (-14, 92), (-30, 92), (-24, 60), (-30, 30),
    (-44, 20), (-64, 6), (-72, 16), (-82, 4), (-66, -10), (-44, 0),
    (-34, -20), (-40, -44), (-56, -52), (-72, -56), (-80, -64)])
    + _poly([(-4, -32), (28, -98), (44, -72), (64, -94), (72, -62),
             (94, -68), (84, -32), (40, -20)])
    + _band([(22, 40), (56, 44), (80, 26), (90, 0)], 12)
    + _poly([(84, -6), (100, -26), (98, 4)]) + _eye(-44, -68))

SHAPES["griffin"] = (_poly([
    (-80, -54), (-72, -66), (-54, -68), (-46, -88), (-36, -70), (-22, -64),
    (-20, -42), (-6, -26), (16, -8), (26, 22), (18, 50), (32, 70), (28, 92),
    (12, 92), (8, 70), (-8, 56), (-16, 92), (-32, 92), (-26, 60), (-32, 32),
    (-46, 22), (-70, 12), (-84, 24), (-90, 10), (-68, -4), (-46, 4),
    (-36, -16), (-42, -38), (-56, -50), (-66, -52), (-72, -48)])
    + _poly([(-6, -26), (18, -98), (32, -72), (48, -94), (56, -64), (76, -82),
             (76, -50), (96, -58), (82, -26), (30, -16)])
    + _band([(22, 40), (58, 32), (72, 4)], 8) + _circle(74, -4, 10)
    + _eye(-50, -58))

SHAPES["unicorn"] = (_poly([
    (-62, -60), (-56, -74), (-40, -84), (-30, -94), (-26, -78), (-14, -66),
    (-4, -44), (10, -30), (28, -10), (36, 20), (28, 48), (40, 70), (38, 94),
    (22, 94), (18, 70), (2, 56), (-6, 94), (-22, 94), (-16, 60), (-20, 30),
    (-34, 14), (-52, -2), (-66, 8), (-70, -2), (-54, -16), (-34, -8),
    (-28, -26), (-40, -44), (-54, -48)])
    + _poly([(-42, -82), (-76, -100), (-48, -74)])
    + _poly([(-26, -78), (-14, -88), (-12, -72), (0, -78), (-2, -60),
             (10, -62), (4, -44)])
    + _poly([(-58, -50), (-62, -34), (-50, -46)])
    + _band([(32, 30), (62, 22), (74, -8)], 8) + _circle(76, -14, 10)
    + _eye(-44, -68, 3.5))

SHAPES["phoenix"] = (_poly([
    (0, -68), (-10, -60), (-30, -50), (-60, -96), (-70, -80), (-80, -92),
    (-86, -70), (-98, -74), (-84, -40), (-50, -20), (-20, -10), (-14, 20),
    (0, 30), (14, 20), (20, -10), (50, -20), (84, -40), (98, -74), (86, -70),
    (80, -92), (70, -80), (60, -96), (30, -50), (10, -60)])
    + _circle(0, -76, 12) + _poly([(-10, -80), (-28, -72), (-10, -70)])
    + _poly([(-4, -86), (2, -100), (8, -84)])
    + _path("M -64,96 Q -54,58 -32,70 Q -36,36 -10,26 Q 0,52 10,26 "
            "Q 36,36 32,70 Q 54,58 64,96 Z") + _eye(-4, -78, 3))

SHAPES["pegasus"] = (_poly([
    (-98, -40), (-90, -54), (-76, -62), (-70, -78), (-64, -62), (-54, -56),
    (-40, -30), (-20, -16), (40, -18), (64, -12), (76, 0), (94, 30), (86, 34),
    (76, 16), (72, 30), (74, 92), (60, 92), (56, 46), (44, 44), (42, 92),
    (28, 92), (26, 40), (-26, 38), (-30, 92), (-44, 92), (-46, 40), (-54, 36),
    (-58, 92), (-72, 92), (-68, 20), (-74, 0), (-82, -26), (-92, -28)])
    + _poly([(-20, -16), (-22, -62), (0, -98), (6, -72), (24, -94), (26, -64),
             (46, -82), (42, -52), (62, -60), (50, -30), (20, -18)])
    + _eye(-80, -50, 3))

# --- objects -----------------------------------------------------------------

SHAPES["anchor"] = (
    _ring(0, -84, 16, 7) + _rect(-44, -66, 88, 12) + _rect(-7, -72, 14, 152)
    + _path("M -72,28 Q -62,92 0,94 Q 62,92 72,28 L 58,32 Q 50,78 0,80 "
            "Q -50,78 -58,32 Z")
    + _both([(-74, 24), (-90, 48), (-54, 36)]))

SHAPES["axe"] = (
    _rect(-6, -84, 12, 180)
    + _path("M -2,-76 Q -34,-82 -62,-94 Q -96,-44 -62,8 Q -34,-4 -2,-10 Z")
    + _poly([(6, -56), (40, -44), (6, -32)]))

SHAPES["hammer"] = _rect(-7, -48, 14, 144) + _rect(-58, -90, 116, 42)

SHAPES["anvil"] = _path(
    "M -96,-46 Q -60,-40 -40,-52 L 72,-52 L 72,-22 L 42,-22 L 30,20 "
    "L 62,50 L 72,72 L -62,72 L -52,50 L -20,20 L -30,-22 L -52,-26 "
    "Q -82,-30 -96,-46 Z")

SHAPES["bell"] = (
    _ring(0, -90, 12, 5)
    + _path("M -12,-84 L 12,-84 L 14,-72 Q 52,-64 58,-8 Q 62,42 84,64 "
            "L -84,64 Q -62,42 -58,-8 Q -52,-64 -14,-72 Z")
    + _rect(-78, 44, 156, 6, WHITE) + _circle(0, 78, 14))

SHAPES["horseshoe"] = (
    _path("M -60,84 L -78,4 Q -80,-84 0,-88 Q 80,-84 78,4 L 60,84 L 34,84 "
          "L 50,6 Q 50,-54 0,-56 Q -50,-54 -50,6 L -34,84 Z")
    + "".join(_circle(x, y, 5, WHITE) for x, y in
              [(-64, 40), (-66, 0), (-54, -44), (64, 40), (66, 0), (54, -44)]))

SHAPES["wheel"] = (
    _ring(0, 0, 94, 74)
    + "".join('<rect x="-5" y="-76" width="10" height="76" '
              'transform="rotate(%d)"/>' % (i * 45) for i in range(8))
    + _circle(0, 0, 18))


def _harp():
    strings = ""
    for x, top in [(-40, -58), (-16, -66), (8, -68), (32, -62), (56, -58)]:
        bottom = 88 - (x + 64) * 1.039
        strings += _band([(x, top), (x, bottom)], 4, WHITE)
    return (_rect(-76, -66, 16, 158)
            + _path("M -76,-66 Q -24,-106 36,-72 Q 62,-56 84,-86 L 96,-72 "
                    "Q 76,-30 38,-46 Q -12,-78 -60,-50 Z")
            + _band([(-64, 88), (90, -72)], 18) + _rect(-80, 84, 40, 12)
            + strings)


SHAPES["harp"] = _harp()

SHAPES["bugle horn"] = (
    _band([(-56, 20), (-36, 60), (-6, 74), (20, 52), (30, -30)], 6)
    + _path("M -92,30 Q -70,-40 10,-44 L 64,-62 L 72,-44 L 20,-22 "
            "Q -50,-20 -74,40 Z")
    + _poly([(62, -72), (98, -86), (98, -22), (66, -34)]))

SHAPES["arrow"] = (
    _rect(-5, -66, 10, 150) + _poly([(0, -100), (24, -60), (-24, -60)])
    + _both([(-5, 54), (-28, 86), (-28, 62), (-5, 34)]))

SHAPES["helm"] = (
    _path("M 0,-94 Q 30,-104 60,-80 Q 30,-88 10,-80 Z")
    + _path("M -58,92 L -62,-18 Q -62,-92 0,-94 Q 62,-92 62,-18 L 58,92 Z")
    + _rect(-46, -20, 92, 10, WHITE)
    + "".join(_circle(x, y, 4, WHITE) for y in (14, 32, 50)
              for x in (-30, -10, 10, 30)))

SHAPES["lymphad"] = (
    "".join(_band(oar, 6) for oar in
            [[(-60, 56), (-76, 90)], [(-30, 56), (-42, 92)],
             [(0, 56), (-8, 92)], [(30, 56), (26, 92)]])
    + _rect(-5, -92, 10, 110)
    + _path("M -62,-82 L 58,-82 Q 70,-34 58,8 L -62,8 Q -50,-34 -62,-82 Z")
    + _poly([(5, -92), (42, -84), (5, -76)])
    + _poly([(-98, 18), (98, 18), (74, 58), (-74, 58)]))


def _book():
    lines = ""
    for y in (-40, -20, 0, 20, 40):
        lines += _band([(-80, y + 2), (-14, y + 8)], 4, WHITE)
        lines += _band([(80, y + 2), (14, y + 8)], 4, WHITE)
    return (_path("M 0,-58 Q -40,-80 -92,-66 L -92,72 Q -40,56 0,78 "
                  "Q 40,56 92,72 L 92,-66 Q 40,-80 0,-58 Z")
            + _band([(0, -56), (0, 76)], 4, WHITE) + lines)


SHAPES["book"] = _book()

SHAPES["hourglass"] = (
    _rect(-78, -80, 10, 160) + _rect(68, -80, 10, 160)
    + _poly([(-60, -80), (60, -80), (8, 0), (60, 80), (-60, 80), (-8, 0)])
    + _rect(-78, -98, 156, 18) + _rect(-78, 80, 156, 18))

SHAPES["scales"] = (
    _rect(-6, -72, 12, 160) + _rect(-44, 84, 88, 14)
    + _band([(-80, -70), (-98, 6)], 4) + _band([(-80, -70), (-62, 6)], 4)
    + _band([(80, -70), (98, 6)], 4) + _band([(80, -70), (62, 6)], 4)
    + _path("M -100,6 Q -80,40 -60,6 Z") + _path("M 100,6 Q 80,40 60,6 Z")
    + _rect(-88, -78, 176, 10) + _circle(0, -86, 10))

# --- symbols -----------------------------------------------------------------

SHAPES["heart"] = _path(
    "M 0,92 C -52,52 -98,20 -98,-28 C -98,-74 -40,-90 0,-48 "
    "C 40,-90 98,-74 98,-28 C 98,20 52,52 0,92 Z")

SHAPES["hand"] = (
    "".join(_rect(x, top, 20, 100) + _circle(x + 10, top, 10)
            for x, top in [(-48, -78), (-24, -92), (0, -88), (24, -74)])
    + _poly([(-48, 20), (-88, -24), (-74, -38), (-40, -2)])
    + _circle(-81, -31, 10)
    + _path("M -48,0 L 44,0 L 44,62 Q 40,80 20,84 L -24,84 Q -44,80 -48,62 Z")
    + _rect(-34, 80, 64, 20))

SHAPES["eye"] = (_path("M -98,0 Q 0,-84 98,0 Q 0,84 -98,0 Z")
                 + _circle(0, 0, 36, WHITE) + _circle(0, 0, 18))

SHAPES["skull"] = (
    _path("M -64,14 Q -84,-90 0,-94 Q 84,-90 64,14 L 50,32 L 46,58 "
          "L -46,58 L -50,32 Z")
    + _rect(-36, 54, 72, 30)
    + "".join(_band([(x, 58), (x, 84)], 4, WHITE) for x in (-18, 0, 18))
    + _ellipse(-28, -12, 18, 20, WHITE) + _ellipse(28, -12, 18, 20, WHITE)
    + _poly([(0, 12), (-10, 34), (10, 34)], WHITE))

SHAPES["flame"] = (
    _path("M 0,-100 Q 30,-52 20,-22 Q 50,-40 48,-72 Q 90,-10 70,40 "
          "Q 56,92 0,96 Q -56,92 -70,40 Q -82,-2 -50,-42 Q -46,-12 -30,-2 "
          "Q -40,-52 0,-100 Z")
    + _path("M 0,8 Q 28,40 20,66 Q 10,86 0,86 Q -10,86 -20,66 Q -28,40 0,8 Z",
            WHITE))

SHAPES["thunderbolt"] = _poly([
    (22, -100), (-40, -4), (-4, -4), (-30, 100), (52, -22), (14, -22),
    (42, -100)])

SHAPES["mountain"] = (
    _poly([(-100, 92), (-52, -26), (-32, 4), (10, -82), (52, -12), (66, -32),
           (100, 92)])
    + _poly([(10, -82), (-4, -52), (2, -58), (10, -48), (18, -58), (28, -52)],
            WHITE))

SHAPES["cloud"] = _path(
    "M -86,48 A 28 28 0 0 1 -62,2 A 42 42 0 0 1 8,-52 A 38 38 0 0 1 64,-8 "
    "A 30 30 0 0 1 86,48 Z")

SHAPES["acorn"] = (
    _rect(-6, -98, 12, 28)
    + _path("M -40,-18 L 40,-18 Q 46,58 0,92 Q -46,58 -40,-18 Z")
    + _path("M -54,-18 Q -54,-72 0,-74 Q 54,-72 54,-18 Z")
    + "".join(_circle(x, y, 4, WHITE) for x, y in
              [(-30, -38), (0, -40), (30, -38), (-15, -56), (15, -56)]))

SHAPES["oak leaf"] = (
    _path("M 0,-100 Q 20,-86 16,-70 Q 40,-70 36,-50 Q 60,-44 46,-24 "
          "Q 70,-10 50,8 Q 70,26 44,40 Q 56,62 26,64 Q 20,80 6,76 L 4,100 "
          "L -4,100 L -6,76 Q -20,80 -26,64 Q -56,62 -44,40 Q -70,26 -50,8 "
          "Q -70,-10 -46,-24 Q -60,-44 -36,-50 Q -40,-70 -16,-70 "
          "Q -20,-86 0,-100 Z")
    + _band([(0, -88), (0, 72)], 4, WHITE)
    + "".join(_band([(0, y), (sx * 30, y - 16)], 3, WHITE)
              for y in (-40, -8, 26) for sx in (-1, 1)))

SHAPES["thistle"] = (
    _both([(-4, 68), (-58, 40), (-48, 56), (-80, 54), (-56, 70), (-70, 86),
           (-4, 84)])
    + _rect(-5, 38, 10, 62)
    + _poly([(-40, -6), (-56, -70), (-30, -40), (-24, -96), (-8, -50),
             (0, -100), (8, -50), (24, -96), (30, -40), (56, -70), (40, -6)])
    + _ellipse(0, 12, 38, 30))

SHAPES["bunch of grapes"] = (
    _rect(-4, -92, 8, 30)
    + _path("M 4,-70 Q 40,-100 76,-80 Q 54,-54 4,-62 Z")
    + "".join(_circle(x, y, 17) for x, y in
              [(-48, -40), (-16, -40), (16, -40), (48, -40), (-32, -10),
               (0, -10), (32, -10), (-16, 20), (16, 20), (0, 50)]))


def _triskele():
    arm = [(0.0, 0.0)]
    for i in range(28):
        s = i / 27.0
        theta = math.pi / 2 + s * 2.2 * math.pi
        radius = 44 * (1 - s) + 8 * s
        arm.append((radius * math.cos(theta), -52 + radius * math.sin(theta)))
    return ("".join(_band(_rotate(arm, k * 120), 12) for k in range(3))
            + _circle(0, 0, 12))


SHAPES["triskele"] = _triskele()

SHAPES["bowen knot"] = (
    _band([(0, -52), (52, 0), (0, 52), (-52, 0)], 12, closed=True)
    + "".join(_ring(x, y, 22, 11) for x, y in
              [(0, -72), (72, 0), (0, 72), (-72, 0)]))

SHAPES["ankh"] = (
    '<path fill-rule="evenodd" d="M -34,-56 a 34 42 0 1 0 68 0 '
    'a 34 42 0 1 0 -68 0 Z M -18,-56 a 18 28 0 1 0 36 0 '
    'a 18 28 0 1 0 -36 0 Z"/>'
    + _rect(-62, -14, 124, 20) + _poly([(-12, 6), (12, 6), (22, 98), (-22, 98)]))

SHAPES["yin-yang"] = (
    _circle(0, 0, 92, WHITE)
    + _path("M 0,-92 A 92 92 0 0 1 0 92 A 46 46 0 0 1 0 0 "
            "A 46 46 0 0 0 0 -92 Z")
    + _circle(0, -46, 14) + _circle(0, 46, 14, WHITE))

SHAPES["cross patée"] = _poly([
    (-14, -14), (-34, -96), (34, -96), (14, -14), (96, -34), (96, 34),
    (14, 14), (34, 96), (-34, 96), (-14, 14), (-96, 34), (-96, -34)])


def _crosslet():
    top = [(10, -10), (10, -58), (30, -58), (30, -74), (10, -74), (10, -96),
           (-10, -96), (-10, -74), (-30, -74), (-30, -58), (-10, -58),
           (-10, -10)]
    outline, arm = [], top
    for _ in range(4):
        outline += arm[:-1]
        arm = [(y, -x) for x, y in arm]        # a quarter turn to the next arm
    return _poly(outline)


SHAPES["cross crosslet"] = _crosslet()

SHAPES["ringed planet"] = (
    '<g transform="rotate(-22)"><path fill-rule="evenodd" d="'
    'M -96,0 A 96 26 0 1 0 96 0 A 96 26 0 1 0 -96 0 Z '
    'M -72,0 A 72 14 0 1 0 72 0 A 72 14 0 1 0 -72 0 Z"/></g>'
    + _circle(0, 0, 52)
    + '<g transform="rotate(-22)"><path d="M -96,0 A 96 26 0 0 0 96 0 '
    'L 72,0 A 72 14 0 0 1 -72 0 Z"/></g>')


def _compass_rose():
    pts = []
    for k in range(16):
        a = math.radians(-90 + k * 22.5)
        radius = 100 if k % 4 == 0 else 58 if k % 4 == 2 else 16
        pts.append((radius * math.cos(a), radius * math.sin(a)))
    # Half of each cardinal point in white, the way a compass card shades it.
    shade = ""
    for k in (0, 4, 8, 12):
        shade += _poly([(0, 0), pts[k], pts[(k + 1) % 16]], WHITE)
    return _poly(pts) + shade + _circle(0, 0, 8)


SHAPES["compass rose"] = _compass_rose()

# --- the older beasts, redrawn ----------------------------------------------
# The lion, stag and horse predate this box and were drawn as a dozen straight
# segments each. Redrawn here to match the rest: same poses and names -- the
# lion rampant, the stag at gaze, the horse forcene -- so every blazon and
# gloss still describes the picture.

SHAPES["lion"] = (_poly([
    (-64, -74), (-58, -84), (-48, -90), (-40, -100), (-30, -92), (-22, -100),
    (-14, -88), (-4, -94), (-2, -80), (8, -82), (2, -66), (12, -64), (4, -50),
    (14, -36), (30, -10), (42, 14), (48, 22), (46, 40), (44, 60), (52, 80),
    (60, 92), (58, 98), (30, 98), (28, 88), (34, 84), (28, 66), (18, 56),
    (4, 52), (-10, 60), (-30, 64), (-44, 62), (-50, 70), (-56, 66), (-52, 58),
    (-46, 52), (-30, 50), (-12, 40), (-4, 30), (-10, 10), (-30, 4), (-56, 2),
    (-66, 8), (-76, 6), (-80, -2), (-74, -8), (-60, -8), (-36, -12),
    (-22, -22), (-26, -34), (-46, -40), (-66, -46), (-74, -44), (-80, -52),
    (-74, -58), (-60, -56), (-40, -52), (-30, -52), (-40, -58), (-56, -62),
    (-66, -60), (-58, -66), (-62, -68)])
    + _band([(44, 18), (64, 0), (72, -24), (66, -48), (74, -66)], 8)
    + _poly([(66, -62), (70, -86), (78, -72), (88, -84), (86, -64), (96, -62),
             (78, -54)])
    + _eye(-46, -78, 3.5))

SHAPES["stag"] = (_poly([
    (-94, -40), (-90, -50), (-78, -58), (-62, -50), (-50, -30), (-30, -18),
    (40, -18), (62, -12), (70, -18), (72, -8), (66, -4), (68, 14), (60, 40),
    (62, 94), (54, 94), (50, 44), (44, 30), (42, 40), (44, 94), (36, 94),
    (32, 40), (26, 24), (-30, 24), (-32, 94), (-40, 94), (-42, 36), (-48, 30),
    (-50, 94), (-58, 94), (-58, 30), (-62, 10), (-72, -20), (-84, -34),
    (-92, -36)])
    + _band([(-74, -56), (-80, -78), (-70, -92), (-78, -100)], 6)
    + _band([(-78, -72), (-94, -84)], 5) + _band([(-72, -88), (-60, -98)], 5)
    + _band([(-66, -58), (-56, -80), (-44, -92), (-40, -100)], 6)
    + _band([(-58, -76), (-42, -78)], 5) + _band([(-48, -88), (-56, -100)], 5)
    + _poly([(-68, -56), (-52, -66), (-60, -52)])
    + _eye(-80, -48, 3))

SHAPES["horse"] = (
    _path("M 40,18 Q 70,10 76,40 Q 80,70 96,80 Q 70,84 62,56 Q 58,34 40,30 Z")
    + _poly([
        (-84, -50), (-80, -62), (-66, -80), (-60, -96), (-54, -80), (-48, -78),
        (-36, -66), (-20, -44), (0, -20), (20, 4), (38, 20), (46, 36), (44, 58),
        (52, 80), (56, 96), (38, 96), (36, 84), (30, 66), (22, 54), (16, 64),
        (20, 82), (22, 96), (6, 96), (4, 84), (0, 62), (-6, 50), (-20, 36),
        (-30, 26), (-46, 24), (-58, 34), (-68, 30), (-72, 22), (-62, 16),
        (-48, 12), (-36, 8), (-38, 0), (-52, -12), (-66, -8), (-72, -16),
        (-66, -24), (-50, -24), (-38, -22), (-40, -34), (-50, -46),
        (-62, -48), (-74, -44), (-82, -44)])
    + _poly([(-54, -82), (-44, -86), (-42, -74), (-30, -76), (-32, -62),
             (-20, -60), (-24, -46), (-12, -40), (-26, -40), (-36, -56),
             (-48, -70)])
    + _eye(-68, -66, 3))


# --- what each one is --------------------------------------------------------
#
# name: (complexity, themes, plain name, plain plural or None, blazon plural
#        or None, strewable, prompt words)
#
# Complexity follows the older charges': 1 survives anything, 4 needs about 26
# braille columns before the silhouette reads. Strewable ones are small and
# solid enough to repeat across a field as a semé. Plurals are only given where
# adding an "s" would be wrong.

META = {
    "wolf": (4, {"natural", "medieval", "mythic"}, "wolf", "wolves", "wolves", False,
             ["wolf"]),
    "bear": (4, {"natural", "medieval"}, "bear", None, None, False, ["bear"]),
    "boar": (4, {"natural", "medieval"}, "boar", None, None, False,
             ["boar", "pig", "hog", "wild boar"]),
    "fox": (4, {"natural"}, "fox", "foxes", "foxes", False, ["fox", "vixen"]),
    "bull": (4, {"natural", "medieval", "cosmic"}, "bull", None, None, False,
             ["bull", "ox", "cow"]),
    "ram": (4, {"natural", "cosmic"}, "ram", None, None, False, ["ram", "sheep"]),
    "hare": (4, {"natural"}, "hare", None, None, False, ["hare", "rabbit", "bunny"]),
    "hound": (4, {"natural", "medieval"}, "hound", None, None, False,
              ["hound", "dog", "greyhound"]),
    "elephant": (4, {"natural", "medieval"}, "elephant", None, None, False,
                 ["elephant"]),
    "owl": (3, {"natural", "mythic"}, "owl", None, None, False, ["owl"]),
    "raven": (4, {"natural", "medieval", "mythic"}, "raven", None, None, False,
              ["raven", "crow", "blackbird"]),
    "swan": (4, {"natural", "medieval"}, "swan", None, None, False, ["swan"]),
    "martlet": (4, {"natural", "medieval"}, "swallow", None, None, False,
                ["martlet", "swallow"]),
    "cockerel": (4, {"natural", "medieval"}, "rooster", None, None, False,
                 ["cockerel", "rooster", "cock", "chicken"]),
    "butterfly": (3, {"natural"}, "butterfly", "butterflies", "butterflies",
                  False, ["butterfly", "moth"]),
    "bat": (3, {"natural", "mythic"}, "bat", None, None, False, ["bat"]),
    "spider": (3, {"natural"}, "spider", None, None, False, ["spider"]),
    "scorpion": (4, {"natural", "cosmic"}, "scorpion", None, None, False,
                 ["scorpion"]),
    "serpent": (3, {"natural", "mythic"}, "snake", None, None, False,
                ["serpent", "snake", "viper"]),
    "frog": (3, {"natural"}, "frog", None, None, False, ["frog", "toad"]),
    "tortoise": (3, {"natural"}, "turtle", None, None, False,
                 ["tortoise", "turtle"]),
    "crab": (3, {"natural", "cosmic"}, "crab", None, None, False,
             ["crab", "lobster"]),
    "dolphin": (3, {"natural", "medieval"}, "dolphin", None, None, False,
                ["dolphin", "porpoise"]),
    "escallop": (2, {"natural", "medieval"}, "scallop shell", None, None, True,
                 ["escallop", "scallop", "shell", "seashell", "scallop shell"]),
    "dragon": (4, {"mythic", "medieval"}, "dragon", None, None, False,
               ["dragon", "wyvern", "drake"]),
    "griffin": (4, {"mythic", "medieval"}, "griffin", None, None, False,
                ["griffin", "gryphon", "griffon"]),
    "unicorn": (4, {"mythic"}, "unicorn", None, None, False, ["unicorn"]),
    "phoenix": (4, {"mythic", "cosmic"}, "phoenix", "phoenixes", "phoenixes",
                False, ["phoenix", "firebird"]),
    "pegasus": (4, {"mythic"}, "winged horse", None, "pegasi", False,
                ["pegasus", "pegasi", "winged horse"]),
    "anchor": (3, {"medieval"}, "anchor", None, None, False, ["anchor"]),
    "axe": (2, {"medieval"}, "axe", None, None, False, ["axe", "hatchet"]),
    "hammer": (2, {"medieval"}, "hammer", None, None, False, ["hammer", "mallet"]),
    "anvil": (2, {"medieval"}, "anvil", None, None, False, ["anvil"]),
    "bell": (2, {"medieval"}, "bell", None, None, True, ["bell"]),
    "horseshoe": (2, {"medieval"}, "horseshoe", None, None, True, ["horseshoe"]),
    "wheel": (3, {"medieval"}, "wheel", None, None, False,
              ["wheel", "catherine wheel", "cartwheel"]),
    "harp": (3, {"medieval"}, "harp", None, None, False, ["harp", "lyre"]),
    "bugle horn": (3, {"medieval"}, "hunting horn", None, None, False,
                   ["bugle horn", "hunting horn", "horn", "bugle"]),
    "arrow": (2, {"medieval"}, "arrow", None, None, False, ["arrow"]),
    "helm": (2, {"medieval"}, "helmet", None, None, False,
             ["helm", "helmet", "knight's helmet"]),
    "lymphad": (3, {"medieval"}, "galley", None, None, False,
                ["lymphad", "ship", "boat", "galley"]),
    "book": (2, {"medieval"}, "book", None, None, False, ["book", "tome"]),
    "hourglass": (2, {"medieval", "cosmic"}, "hourglass", "hourglasses",
                  "hourglasses", False, ["hourglass", "sand timer"]),
    "scales": (3, {"medieval", "cosmic"}, "pair of scales", "pairs of scales",
               "pairs of scales", False, ["scales", "balance", "justice"]),
    "heart": (1, {"medieval", "natural"}, "heart", None, None, True, ["heart"]),
    "hand": (3, {"medieval"}, "open hand", None, None, False, ["hand", "palm"]),
    "eye": (2, {"cosmic", "mythic"}, "eye", None, None, False, ["eye"]),
    "skull": (3, {"medieval", "mythic"}, "skull", None, None, False, ["skull"]),
    "flame": (2, {"cosmic", "mythic"}, "flame", None, None, True,
              ["flame", "fire", "blaze"]),
    "thunderbolt": (2, {"cosmic", "mythic"}, "lightning bolt", None, None, False,
                    ["thunderbolt", "lightning", "lightning bolt", "bolt"]),
    "mountain": (1, {"natural"}, "mountain", None, None, False,
                 ["mountain", "mount", "hill", "peak"]),
    "cloud": (2, {"natural", "cosmic"}, "cloud", None, None, False, ["cloud"]),
    "acorn": (2, {"natural"}, "acorn", None, None, True, ["acorn"]),
    "oak leaf": (2, {"natural"}, "oak leaf", "oak leaves", "oak leaves", True,
                 ["oak leaf", "leaf"]),
    "thistle": (3, {"natural", "medieval"}, "thistle", None, None, False,
                ["thistle"]),
    "bunch of grapes": (3, {"natural"}, "bunch of grapes", "bunches of grapes",
                        "bunches of grapes", False,
                        ["bunch of grapes", "bunches of grapes", "grapes", "vine"]),
    "triskele": (3, {"mythic", "cosmic"}, "triple spiral", None, None, False,
                 ["triskele", "triskelion", "triple spiral"]),
    "bowen knot": (2, {"medieval", "mythic"}, "looped knot", None, None, False,
                   ["bowen knot", "knot", "celtic knot"]),
    "ankh": (2, {"cosmic", "mythic"}, "ankh", None, None, False, ["ankh"]),
    "yin-yang": (2, {"cosmic"}, "yin and yang", "yin and yang symbols", None,
                 False, ["yin-yang", "yin yang", "yinyang", "yin and yang"]),
    "cross patée": (1, {"medieval"}, "flared cross", "flared crosses",
                    "crosses patée", True,
                    ["cross patée", "cross patee", "cross formée",
                     "flared cross", "templar cross"]),
    "cross crosslet": (1, {"medieval"}, "cross of crosses", "crosses of crosses",
                       "crosses crosslet", True,
                       ["cross crosslet", "crosslet", "cross of crosses"]),
    "ringed planet": (2, {"cosmic"}, "ringed planet", None, None, False,
                      ["ringed planet", "saturn", "planet"]),
    "compass rose": (2, {"cosmic", "medieval"}, "compass rose", None, None, False,
                     ["compass rose", "compass star", "wind rose"]),
}

assert set(META) <= set(SHAPES), set(META) - set(SHAPES)


def article(word):
    """'a' or 'an' by sound rather than spelling: an hourglass, a unicorn."""
    w = word.lower()
    if w.startswith(("uni", "use", "eu", "one", "ewe")):
        return "a"
    if w.startswith(("hour", "honest", "heir")) or w[:1] in "aeiou":
        return "an"
    return "a"


# --- added with the variants -------------------------------------------------------
# Two more for the cosmic register. They arrived after the 0.1.8 vocabulary, so
# SINCE marks them for the seeds of their own time (see blazon.vocabulary_for).

def _galaxy():
    arms = ""
    for start in (0.0, math.pi):
        pts = []
        for i in range(40):
            s = i / 39.0
            theta = start + s * 2.6 * math.pi
            radius = 10 + 84 * s
            pts.append((radius * math.cos(theta), radius * 0.72 * math.sin(theta)))
        arms += _band(pts, 14 - 8 * 0.5)
    return (arms + _ellipse(0, 0, 22, 17)
            + "".join(_circle(x, y, 3, WHITE) for x, y in
                      [(-40, -20), (30, 30), (56, -10), (-60, 26), (10, -46)]))


def _constellation():
    stars = [(-80, -50), (-40, -72), (0, -30), (34, -62), (72, -20), (40, 40),
             (-12, 62)]
    lines = "".join(_band([a, b], 4) for a, b in zip(stars, stars[1:]))

    def twinkle(x, y, r):
        pts = []
        for i in range(8):
            a = -math.pi / 2 + i * math.pi / 4
            rad = r if i % 2 == 0 else r * 0.34
            pts.append((x + rad * math.cos(a), y + rad * math.sin(a)))
        return _poly(pts)

    return lines + "".join(twinkle(x, y, 16 if i % 3 == 0 else 11)
                           for i, (x, y) in enumerate(stars))


SHAPES["spiral galaxy"] = _galaxy()
SHAPES["constellation"] = _constellation()

META.update({
    "spiral galaxy": (3, {"cosmic"}, "spiral galaxy", "spiral galaxies",
                      "spiral galaxies", False,
                      ["spiral galaxy", "galaxy", "milky way", "nebula"]),
    "constellation": (2, {"cosmic"}, "constellation", None, None, False,
                      ["constellation", "big dipper", "plough"]),
})

# The vocabulary each charge arrived in: 1 unless listed.
SINCE = {"spiral galaxy": 2, "constellation": 2}
