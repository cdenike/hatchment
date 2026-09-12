"""Other ways to draw a charge: the poses and forms heraldry already names.

A lion need not be rampant. Heraldry has words for a lion walking (passant),
sitting (sejant), lying down (couchant) and for its head alone, and the same
for most beasts; trees, swords, crowns, crosses and knots have forms of their
own. Each is a variant of a charge rather than a charge of its own, so the
rest of the vocabulary -- themes, complexity, contrast -- stays with the
charge, and only the drawing and the words change.

The first variant of every charge is the drawing it already had, named by
nothing: an unqualified lion in a blazon is rampant, so "a lion or" still
means what it did. Others add their word -- "a lion passant or".

Variants are chosen only for seeds made from 0.1.9 on (see
blazon.vocabulary_for), and from a generator derived from the roll's state
rather than drawn from it, so choosing one never shifts anything else a roll
picks.

Drawn in the same 200-unit box as hatchment.charges.

Copyright (C) 2026 Caden DeNike. Free software under the GNU General
Public License, version 3 or later, with no warranty. See LICENSE.
"""

import math
import random

from .charges import (WHITE, _band, _both, _circle, _ellipse, _eye, _mirror,
                      _path, _poly, _rect, _ring, _rotate)

# --- beasts in other poses -------------------------------------------------------
# Facing dexter like the rest; heads are "erased" -- torn off, with a ragged
# edge -- which is the commoner treatment and reads as a head, not a bust.

LION_PASSANT = (_poly([
    (-96, -40), (-92, -54), (-80, -62), (-76, -76), (-66, -66), (-60, -82),
    (-50, -68), (-40, -80), (-36, -62), (-24, -66), (-28, -48), (-10, -40),
    (40, -38), (60, -34), (70, -24), (72, -6), (68, 10), (72, 40), (76, 90),
    (62, 90), (58, 50), (50, 40), (46, 56), (48, 90), (34, 90), (32, 40),
    (20, 30), (-20, 30), (-26, 50), (-24, 90), (-38, 90), (-40, 46),
    (-46, 40), (-58, 34), (-76, 40), (-84, 34), (-80, 26), (-60, 20),
    (-54, 10), (-58, 4), (-66, -10), (-74, -4), (-78, -18), (-86, -24),
    (-92, -30)])
    + _band([(70, -26), (84, -44), (80, -66), (70, -78)], 7)
    + _poly([(62, -76), (64, -96), (72, -84), (82, -94), (80, -74), (70, -70)])
    + _eye(-80, -46, 3.5))

LION_SEJANT = (_poly([
    (-70, -78), (-64, -90), (-54, -100), (-44, -88), (-34, -98), (-28, -84),
    (-16, -88), (-18, -72), (-6, -70), (-12, -54), (0, -40), (14, -10),
    (34, 20), (50, 48), (58, 72), (56, 94), (10, 94), (8, 84), (20, 80),
    (16, 68), (-8, 62), (-20, 94), (-50, 94), (-52, 86), (-44, 82),
    (-44, 20), (-50, -10), (-58, -30), (-62, -46), (-70, -52), (-80, -58),
    (-78, -68)])
    + _band([(52, 60), (78, 40), (84, 10), (76, -12)], 7)
    + _poly([(68, -10), (70, -32), (78, -20), (88, -30), (86, -10), (78, -4)])
    + _eye(-60, -76, 3.5))

LION_COUCHANT = (_poly([
    (-96, 0), (-92, -14), (-80, -22), (-76, -38), (-66, -28), (-60, -44),
    (-50, -30), (-40, -40), (-36, -22), (-24, -24), (-26, -6), (-10, 4),
    (30, 6), (64, 14), (80, 30), (84, 50), (80, 64), (40, 70), (0, 70),
    (-40, 70), (-80, 72), (-96, 68), (-96, 58), (-70, 56), (-54, 48),
    (-58, 28), (-70, 16), (-86, 10), (-94, 6)])
    + _band([(82, 44), (94, 28), (92, 6)], 7)
    + _poly([(84, 4), (86, -16), (94, -4), (100, -12), (98, 8)])
    + _eye(-82, -8, 3.5))

LION_HEAD = (_poly([
    (-80, -10), (-84, -26), (-72, -40), (-70, -56), (-60, -70), (-54, -90),
    (-40, -72), (-28, -96), (-16, -70), (0, -88), (6, -62), (26, -76),
    (22, -50), (44, -56), (34, -30), (56, -28), (40, -6), (60, 4), (40, 20),
    (56, 36), (30, 40), (40, 70), (24, 60), (18, 86), (4, 66), (-6, 92),
    (-16, 64), (-30, 80), (-34, 56), (-40, 40), (-56, 30), (-64, 20),
    (-58, 14), (-74, 20), (-84, 14), (-76, 6), (-86, 0)])
    + _eye(-56, -30, 6))

_HORSE_HEADPART = [(-98, -40), (-90, -54), (-76, -62), (-70, -78), (-64, -62),
                   (-54, -56), (-40, -30), (-20, -16)]
_HORSE_MANE = _poly([(-66, -64), (-56, -70), (-50, -58), (-40, -60), (-40, -46),
                     (-28, -46), (-30, -32), (-18, -30), (-24, -20), (-40, -30),
                     (-54, -52)])
_HORSE_TAIL = _path("M 66,-12 Q 94,-10 94,24 Q 94,56 100,70 Q 78,64 76,30 "
                    "Q 74,6 64,0 Z")

HORSE_PASSANT = (_HORSE_TAIL + _poly(_HORSE_HEADPART + [
    (40, -18), (64, -12), (72, 30), (74, 92), (60, 92), (56, 46), (44, 44),
    (42, 92), (28, 92), (26, 40), (-26, 38), (-30, 92), (-44, 92), (-46, 40),
    (-54, 36), (-64, 50), (-80, 48), (-84, 56), (-92, 50), (-80, 38),
    (-66, 34), (-68, 20), (-74, 0), (-82, -26), (-92, -28)])
    + _HORSE_MANE + _eye(-80, -50, 3))

HORSE_COURANT = (
    _path("M 66,-10 Q 90,-26 100,-6 Q 84,-4 78,10 Z")
    + _poly(_HORSE_HEADPART + [
        (40, -18), (64, -12), (74, 4), (86, 20), (100, 34), (96, 42), (80, 30),
        (66, 24), (70, 38), (90, 60), (84, 66), (60, 44), (44, 36), (0, 32),
        (-30, 30), (-50, 40), (-80, 50), (-98, 48), (-98, 40), (-78, 40),
        (-60, 28), (-72, 22), (-96, 18), (-96, 10), (-70, 12), (-66, 0),
        (-74, -6), (-82, -26), (-92, -28)])
    + _HORSE_MANE + _eye(-80, -50, 3))

HORSE_HEAD = (_poly([
    (-92, -10), (-96, -24), (-84, -40), (-62, -56), (-56, -76), (-48, -58),
    (-40, -60), (-30, -58), (-24, -66), (-18, -48), (-8, -54), (-6, -34),
    (6, -38), (4, -18), (16, -20), (12, 0), (26, 4), (22, 20), (34, 30),
    (40, 70), (26, 58), (20, 84), (6, 64), (-4, 88), (-14, 62), (-24, 78),
    (-30, 54), (-40, 30), (-56, 10), (-70, 4), (-86, 2)])
    + _eye(-66, -34, 5) + _circle(-88, -14, 3, WHITE))


def _antlers(dy=0):
    return (_band([(-74, -56 + dy), (-80, -78 + dy), (-70, -92 + dy),
                   (-78, -100 + dy)], 6)
            + _band([(-78, -72 + dy), (-94, -84 + dy)], 5)
            + _band([(-72, -88 + dy), (-60, -98 + dy)], 5)
            + _band([(-66, -58 + dy), (-56, -80 + dy), (-44, -92 + dy),
                     (-40, -100 + dy)], 6)
            + _band([(-58, -76 + dy), (-42, -78 + dy)], 5)
            + _band([(-48, -88 + dy), (-56, -100 + dy)], 5))


STAG_COURANT = (_poly([
    (-94, -40), (-90, -50), (-78, -58), (-62, -50), (-50, -30), (-30, -18),
    (40, -18), (62, -12), (70, -18), (72, -8), (66, -2), (80, 14), (98, 30),
    (94, 38), (76, 26), (62, 20), (66, 34), (86, 56), (80, 62), (56, 42),
    (42, 32), (-30, 28), (-46, 38), (-76, 48), (-96, 46), (-96, 38),
    (-74, 36), (-58, 24), (-70, 18), (-94, 12), (-94, 4), (-66, 6),
    (-62, -4), (-70, -20), (-84, -34), (-92, -36)])
    + _antlers() + _eye(-80, -48, 3))

STAG_LODGED = (_poly([
    (-94, -2), (-90, -12), (-78, -20), (-62, -12), (-52, 6), (-30, 16),
    (40, 16), (64, 22), (72, 16), (74, 26), (68, 32), (72, 50), (64, 66),
    (20, 68), (10, 74), (-20, 74), (-30, 68), (-60, 70), (-76, 64),
    (-60, 56), (-58, 40), (-70, 18), (-84, 4), (-92, 2)])
    + _antlers(38) + _eye(-80, -10, 3))


def _caboshed():
    side = (_band([(-16, -14), (-30, -50), (-44, -80), (-40, -100)], 7)
            + _band([(-28, -44), (-54, -50)], 6)
            + _band([(-40, -72), (-64, -80)], 6)
            + _band([(-36, -58), (-22, -78)], 6))
    mirrored = side.replace('points="', 'transform="scale(-1 1)" points="')
    return (side + mirrored
            + _both([(-24, -6), (-58, -24), (-30, 10)])
            + _path("M -26,-10 Q -30,40 -12,70 Q 0,86 12,70 Q 30,40 26,-10 "
                    "Q 0,-26 -26,-10 Z")
            + _eye(-12, 16) + _eye(12, 16))


STAG_CABOSHED = _caboshed()

EAGLE_DOUBLE = (
    _both([(-8, -24), (-20, -60), (-30, -74), (-50, -72), (-38, -86),
           (-20, -90), (-8, -70), (0, -40)])
    + _poly([(0, -20), (-30, -40), (-96, -64), (-80, -30), (-96, -10),
             (-70, -6), (-90, 20), (-40, 10), (-24, 40), (-40, 90), (0, 64),
             (40, 90), (24, 40), (40, 10), (90, 20), (70, -6), (96, -10),
             (80, -30), (96, -64), (30, -40)])
    + _eye(-26, -80, 3) + _eye(26, -80, 3))

EAGLE_CLOSE = (_poly([
    (-86, -48), (-80, -62), (-64, -72), (-44, -70), (-32, -56), (-22, -30),
    (20, -20), (52, 4), (74, 40), (96, 70), (78, 80), (50, 56), (20, 50),
    (6, 62), (16, 92), (2, 92), (-6, 70), (-14, 92), (-28, 92), (-18, 62),
    (-30, 40), (-44, 14), (-50, -20), (-60, -44), (-72, -46), (-80, -42)])
    + _band([(-20, -16), (50, 40)], 4, WHITE) + _eye(-58, -60))

EAGLE_RISING = (
    _poly([(-30, -40), (-44, -98), (-30, -80), (-24, -100), (-14, -74)])
    + _poly([
        (-86, -48), (-80, -62), (-64, -72), (-44, -70), (-32, -56), (-22, -30),
        (20, -20), (52, 4), (74, 40), (96, 70), (78, 80), (50, 56), (20, 50),
        (6, 62), (16, 92), (2, 92), (-6, 70), (-14, 92), (-28, 92), (-18, 62),
        (-30, 40), (-44, 14), (-50, -20), (-60, -44), (-72, -46), (-80, -42)])
    + _poly([(-20, -30), (-10, -96), (4, -70), (16, -96), (24, -66), (40, -90),
             (40, -56), (58, -76), (50, -40), (10, -10)])
    + _eye(-58, -60))

WOLF_RAMPANT = (
    _path("M 44,20 Q 80,20 90,50 Q 96,80 78,92 Q 76,60 46,40 Z")
    + _poly([
        (-80, -66), (-66, -76), (-52, -80), (-50, -100), (-40, -82),
        (-34, -98), (-28, -78), (-16, -66), (-4, -50), (14, -36), (30, -10),
        (42, 14), (48, 22), (46, 40), (44, 60), (52, 80), (60, 92), (58, 98),
        (30, 98), (28, 88), (34, 84), (28, 66), (18, 56), (4, 52), (-10, 60),
        (-30, 64), (-44, 62), (-50, 70), (-56, 66), (-52, 58), (-46, 52),
        (-30, 50), (-12, 40), (-4, 30), (-10, 10), (-30, 4), (-56, 2),
        (-66, 8), (-76, 6), (-80, -2), (-74, -8), (-60, -8), (-36, -12),
        (-22, -22), (-26, -34), (-46, -40), (-66, -46), (-74, -44),
        (-80, -52), (-74, -58), (-60, -56), (-44, -58), (-60, -60),
        (-76, -60)])
    + _eye(-52, -68, 3.5))

WOLF_HEAD = (_poly([
    (-96, -10), (-88, -24), (-60, -40), (-50, -70), (-38, -46), (-28, -74),
    (-16, -44), (4, -30), (20, -4), (30, 24), (40, 60), (26, 50), (20, 78),
    (6, 58), (-4, 84), (-16, 56), (-26, 72), (-32, 48), (-44, 30),
    (-64, 16), (-86, 8), (-92, 0)])
    + _eye(-52, -24, 5))

BEAR_RAMPANT = (_poly([
    (-70, -60), (-66, -72), (-52, -80), (-50, -94), (-40, -92), (-38, -80),
    (-20, -76), (0, -60), (16, -30), (24, 10), (30, 50), (40, 80), (42, 96),
    (10, 96), (10, 84), (18, 78), (10, 56), (-4, 60), (-10, 96), (-40, 96),
    (-40, 84), (-28, 78), (-26, 40), (-30, 10), (-50, 0), (-80, -6),
    (-88, -16), (-80, -26), (-52, -30), (-48, -44), (-58, -54), (-66, -52)])
    + _eye(-56, -70))

BEAR_HEAD = (_poly([
    (-96, 0), (-94, -14), (-70, -30), (-60, -56), (-50, -70), (-44, -80),
    (-32, -76), (-30, -62), (-10, -56), (10, -40), (24, -14), (30, 20),
    (40, 56), (26, 46), (20, 74), (6, 54), (-4, 80), (-16, 52), (-26, 66),
    (-34, 40), (-52, 24), (-74, 16), (-92, 10)])
    + _eye(-54, -24, 5))

BOAR_HEAD = (_poly([
    (-98, 4), (-96, -12), (-76, -18), (-64, -36), (-56, -60), (-44, -40),
    (-32, -50), (-24, -40), (-14, -54), (-6, -40), (6, -52), (12, -36),
    (24, -40), (28, -20), (36, 0), (40, 40), (40, 70), (-20, 70), (-40, 50),
    (-60, 30), (-80, 20), (-94, 16)])
    + _poly([(-84, 6), (-66, -8), (-70, 10)], WHITE) + _eye(-58, -18, 5))

BULL_HEAD = (
    _both([(-24, -26), (-60, -34), (-84, -58), (-92, -90), (-76, -70),
           (-58, -50), (-30, -12)])
    + _both([(-30, -10), (-62, -4), (-34, 6)])
    + _path("M -30,-30 Q -36,40 -16,80 Q 0,92 16,80 Q 36,40 30,-30 "
            "Q 0,-44 -30,-30 Z")
    + _eye(-14, 0, 5) + _eye(14, 0, 5)
    + _circle(-8, 70, 4, WHITE) + _circle(8, 70, 4, WHITE))

RAM_HEAD = (_poly([
    (-96, 10), (-94, -4), (-74, -24), (-56, -40), (-36, -44), (-10, -36),
    (10, -20), (22, 10), (30, 50), (16, 42), (10, 68), (-4, 48), (-14, 72),
    (-24, 46), (-36, 56), (-44, 34), (-64, 26), (-84, 22)])
    + _ring(-26, -40, 30, 16) + _eye(-60, -20, 4))

HOUND_SEJANT = (
    _band([(26, 70), (54, 62), (68, 40)], 7)
    + _poly([
        (-86, -40), (-82, -50), (-64, -58), (-52, -60), (-44, -50), (-36, -34),
        (-24, -14), (-4, 10), (16, 34), (28, 60), (32, 92), (0, 92), (2, 82),
        (12, 78), (6, 66), (-16, 62), (-20, 92), (-40, 92), (-40, 84),
        (-34, 80), (-36, 24), (-42, 0), (-50, -18), (-60, -30), (-72, -32),
        (-84, -32)])
    + _poly([(-56, -56), (-40, -48), (-48, -26)]) + _eye(-64, -48, 3))

HARE_SEJANT = (
    _circle(44, 64, 12)
    + _poly([
        (-80, -10), (-76, -22), (-60, -30), (-66, -80), (-56, -84), (-48, -34),
        (-40, -84), (-30, -80), (-34, -30), (-20, -10), (10, 20), (34, 50),
        (46, 80), (40, 94), (-4, 94), (0, 84), (16, 80), (6, 66), (-20, 66),
        (-24, 94), (-44, 94), (-40, 84), (-36, 40), (-44, 14), (-60, 4),
        (-74, 0)])
    + _eye(-62, -16, 3))

_UNICORN_EXTRAS = (_poly([(-72, -72), (-100, -96), (-78, -60)])
                   + _poly([(-94, -34), (-96, -18), (-86, -30)]))

UNICORN_PASSANT = (
    _band([(66, -12), (84, 10), (90, 40)], 7) + _circle(90, 46, 10)
    + _poly(_HORSE_HEADPART + [
        (40, -18), (64, -12), (72, 30), (74, 92), (60, 92), (56, 46), (44, 44),
        (42, 92), (28, 92), (26, 40), (-26, 38), (-30, 92), (-44, 92),
        (-46, 40), (-54, 36), (-64, 50), (-80, 48), (-84, 56), (-92, 50),
        (-80, 38), (-66, 34), (-68, 20), (-74, 0), (-82, -26), (-92, -28)])
    + _HORSE_MANE + _UNICORN_EXTRAS + _eye(-80, -50, 3))

UNICORN_HEAD = (HORSE_HEAD + _poly([(-58, -64), (-92, -100), (-66, -56)])
                + _poly([(-86, 2), (-90, 24), (-76, 6)]))

PEGASUS_SALIENT = (
    _path("M 40,18 Q 70,10 76,40 Q 80,70 96,80 Q 70,84 62,56 Q 58,34 40,30 Z")
    + _poly([(-20, -44), (-4, -96), (6, -72), (24, -94), (26, -66), (46, -84),
             (42, -56), (62, -64), (48, -34), (8, -20)])
    + _poly([
        (-84, -50), (-80, -62), (-66, -80), (-60, -96), (-54, -80), (-48, -78),
        (-36, -66), (-20, -44), (0, -20), (20, 4), (38, 20), (46, 36),
        (44, 58), (52, 80), (56, 96), (38, 96), (36, 84), (30, 66), (22, 54),
        (16, 64), (20, 82), (22, 96), (6, 96), (4, 84), (0, 62), (-6, 50),
        (-20, 36), (-30, 26), (-46, 24), (-58, 34), (-68, 30), (-72, 22),
        (-62, 16), (-48, 12), (-36, 8), (-38, 0), (-52, -12), (-66, -8),
        (-72, -16), (-66, -24), (-50, -24), (-38, -22), (-40, -34),
        (-50, -46), (-62, -48), (-74, -44), (-82, -44)])
    + _eye(-68, -66, 3))

DRAGON_PASSANT = (
    _band([(58, -4), (84, -10), (96, -30), (94, -56)], 10)
    + _poly([(88, -60), (96, -82), (100, -54)])
    + _poly([(-20, -20), (-10, -90), (10, -70), (30, -96), (40, -66),
             (62, -84), (60, -50), (80, -56), (60, -26), (20, -18)])
    + _poly([
        (-96, -50), (-84, -60), (-70, -62), (-66, -78), (-58, -62), (-46, -52),
        (-36, -30), (-10, -20), (40, -20), (60, -10), (60, 10), (66, 40),
        (70, 90), (56, 90), (50, 44), (40, 40), (36, 90), (22, 90), (20, 36),
        (-24, 34), (-26, 90), (-40, 90), (-44, 40), (-52, 36), (-56, 90),
        (-70, 90), (-66, 20), (-72, -8), (-80, -30), (-92, -36)])
    + _eye(-78, -50, 3.5))

WYVERN = (
    _band([(16, 50), (50, 60), (76, 76), (80, 94), (60, 96)], 10)
    + _poly([(52, 90), (40, 100), (58, 100)])
    + _poly([(-14, -30), (20, -96), (36, -70), (56, -94), (64, -62),
             (90, -70), (80, -34), (30, -20)])
    + _poly([
        (-70, -70), (-58, -80), (-50, -96), (-44, -78), (-30, -70), (-26, -50),
        (-14, -30), (6, -10), (20, 20), (16, 50), (30, 70), (26, 90), (10, 90),
        (6, 70), (-10, 56), (-16, 90), (-32, 90), (-26, 56), (-30, 30),
        (-40, 10), (-44, -20), (-50, -44), (-62, -58), (-72, -62)])
    + _eye(-54, -70, 3.5))

# --- creatures and nature ------------------------------------------------------

FISH_HAURIANT = (
    _poly([(0, 58), (-40, 98), (40, 98)])
    + _path("M 0,-92 C 60,-30 60,30 0,62 C -60,30 -60,-30 0,-92 Z")
    + _poly([(30, -4), (58, 10), (32, 20)]) + _eye(0, -60, 6))


def _serpent_nowed():
    pts = [(50 * math.sin(2 * t), 80 * math.sin(t))
           for t in [i * 2 * math.pi / 60 for i in range(61)]]
    pts = [(-8, -96)] + pts[4:]
    return (_band(pts, 16) + _ellipse(-10, -96, 13, 16)
            + _poly([(-14, -110), (-20, -118), (-8, -112)]) + _eye(-14, -98, 3))


SERPENT_NOWED = _serpent_nowed()

OUROBOROS = (_ring(0, 6, 82, 62) + _ellipse(-40, -66, 22, 16, rotate=-30)
             + _poly([(-20, -78), (-4, -88), (-10, -70)]) + _eye(-46, -70, 4))

RAVEN_VOLANT = (
    _path("M -20,10 Q -6,50 20,72 L 22,50 L 36,62 L 32,36 Q 22,16 10,10 Z")
    + _path("M -54,-14 Q 0,-26 46,-12 L 96,-28 L 84,2 L 96,28 L 44,10 "
            "Q 0,20 -54,8 Z")
    + _circle(-60, -4, 15)
    + _poly([(-72, -9), (-98, -2), (-72, 3)])
    + _path("M -30,-12 Q -20,-60 8,-98 L 14,-76 L 28,-96 L 30,-72 L 46,-88 "
            "L 44,-62 L 62,-72 L 52,-42 Q 32,-20 20,-12 Z")
    + _eye(-64, -8, 3.5))

TREE_PINE = (_rect(-10, 42, 20, 50)
             + _poly([(0, -100), (40, -50), (20, -50), (60, -6), (30, -6),
                      (76, 42), (-76, 42), (-30, -6), (-60, -6), (-20, -50),
                      (-40, -50)]))

TREE_PALM = (
    _band([(10, 96), (4, 50), (-4, 0), (-2, -46)], 14)
    + _path("M -2,-50 Q -50,-90 -96,-50 Q -50,-66 -2,-50 Z")
    + _path("M -2,-50 Q -40,-110 -80,-90 Q -40,-80 -2,-50 Z")
    + _path("M -2,-50 Q 0,-110 30,-100 Q 10,-80 -2,-50 Z")
    + _path("M -2,-50 Q 50,-100 90,-76 Q 40,-74 -2,-50 Z")
    + _path("M -2,-50 Q 60,-60 96,-20 Q 50,-40 -2,-50 Z")
    + _circle(-8, -42, 7) + _circle(6, -38, 7))

TREE_UPROOTED = (
    _band([(0, 56), (-30, 70), (-60, 96)], 8)
    + _band([(0, 56), (-10, 80), (-20, 98)], 7)
    + _band([(0, 56), (12, 80), (24, 98)], 7)
    + _band([(0, 56), (34, 70), (62, 94)], 8)
    + _rect(-10, -10, 20, 70)
    + _circle(0, -50, 44) + _circle(-44, -24, 30) + _circle(44, -24, 30))


def _rose_head(cx, cy, r):
    out = ""
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        out += _circle(round(cx + r * 0.58 * math.cos(a), 1),
                       round(cy + r * 0.58 * math.sin(a), 1), round(r * 0.44, 1))
    return out + _circle(cx, cy, round(r * 0.30, 1), WHITE) + _circle(cx, cy, round(r * 0.15, 1))


ROSE_SLIPPED = (
    _band([(0, -20), (0, 96)], 8)
    + _path("M 0,30 Q -50,10 -70,40 Q -40,50 0,40 Z")
    + _path("M 0,60 Q 50,40 70,70 Q 40,80 0,70 Z")
    + _rose_head(0, -44, 50))

ACORN_SLIPPED = (
    _band([(0, -40), (0, 96)], 6)
    + _path("M 0,30 Q -30,0 -70,10 Q -60,30 -70,50 Q -30,50 0,40 Z")
    + _path("M 0,64 Q 30,34 70,44 Q 60,64 70,84 Q 30,84 0,74 Z")
    + _path("M -22,-50 L 22,-50 Q 24,-6 0,12 Q -24,-6 -22,-50 Z")
    + _path("M -30,-50 Q -30,-80 0,-80 Q 30,-80 30,-50 Z"))

MOUNT = _path("M -100,92 Q -60,-60 0,-70 Q 60,-60 100,92 Z")

FLAMING_HEART = (
    _path("M -40,-40 Q -50,-70 -30,-96 Q -26,-66 -10,-60 Q -14,-86 4,-100 "
          "Q 10,-70 20,-60 Q 30,-80 40,-90 Q 44,-60 34,-40 Z")
    + _path("M 0,96 C -44,62 -82,34 -82,-6 C -82,-44 -34,-58 0,-22 "
            "C 34,-58 82,-44 82,-6 C 82,34 44,62 0,96 Z"))


def _bone(a, b):
    (x0, y0), (x1, y1) = a, b
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    nx, ny = -dy / length * 8, dx / length * 8
    knobs = "".join(_circle(round(x + sx * nx, 1), round(y + sx * ny, 1), 9)
                    for x, y in (a, b) for sx in (-1, 1))
    return _band([a, b], 14) + knobs


SKULL_CROSSBONES = (
    _bone((-80, -10), (80, 90)) + _bone((80, -10), (-80, 90))
    + _path("M -46,-10 Q -60,-84 0,-86 Q 60,-84 46,-10 L 36,4 L 32,22 "
            "L -32,22 L -36,4 Z")
    + _rect(-26, 18, 52, 20)
    + "".join(_band([(x, 22), (x, 38)], 3, WHITE) for x in (-12, 0, 12))
    + _ellipse(-20, -40, 13, 14, WHITE) + _ellipse(20, -40, 13, 14, WHITE)
    + _poly([(0, -20), (-7, -4), (7, -4)], WHITE))

EYE_PROVIDENCE = (
    "".join(_poly(_rotate([(-4, -70), (0, -100), (4, -70)], a))
            for a in range(-60, 61, 30))
    + _poly([(0, -96), (90, 70), (-90, 70)])
    + _path("M -50,20 Q 0,-20 50,20 Q 0,60 -50,20 Z", WHITE)
    + _circle(0, 20, 16))

# --- objects -------------------------------------------------------------------

AXE_DOUBLE = (
    _rect(-6, -96, 12, 192)
    + _path("M 6,-70 Q 40,-80 80,-96 Q 100,-50 80,-4 Q 40,-20 6,-30 Z")
    + _path("M -6,-70 Q -40,-80 -80,-96 Q -100,-50 -80,-4 Q -40,-20 -6,-30 Z"))

HAMMER_THOR = (
    _ring(0, -84, 13, 6) + _rect(-13, -72, 26, 74)
    + "".join(_band([(-13, y), (13, y + 6)], 4, WHITE) for y in (-60, -44, -28, -12))
    + _path("M -64,0 Q 0,-8 64,0 L 86,46 L 46,34 L 0,56 L -46,34 L -86,46 Z")
    + _band([(-50, 18), (50, 18)], 4, WHITE))

def _catherine_wheel():
    spikes = ""
    for i in range(12):
        a = math.radians(i * 30)
        spikes += _poly([(80 * math.cos(a - 0.12), 80 * math.sin(a - 0.12)),
                         (100 * math.cos(a), 100 * math.sin(a)),
                         (80 * math.cos(a + 0.12), 80 * math.sin(a + 0.12))])
    return (spikes + _ring(0, 0, 80, 62)
            + "".join('<rect x="-5" y="-64" width="10" height="64" '
                      'transform="rotate(%d)"/>' % (i * 45) for i in range(8))
            + _circle(0, 0, 16))


WHEEL_CATHERINE = _catherine_wheel()

PHEON = (_rect(-10, -100, 20, 50)
         + _path("M -84,-52 L -30,-52 Q -20,-10 0,6 Q 20,-10 30,-52 L 84,-52 "
                 "L 0,96 Z"))

HELM_NORMAN = (
    _rect(-7, 40, 14, 50)
    + _path("M -56,40 Q -60,-40 0,-96 Q 60,-40 56,40 Z")
    + _rect(-60, 30, 120, 16)
    + "".join(_circle(x, 38, 3, WHITE) for x in (-44, -22, 22, 44)))


def _ship():
    out = _poly([(-96, 20), (96, 10), (70, 70), (-70, 70)])
    out += _rect(-96, 4, 26, 18) + _rect(66, -6, 30, 18)
    for x, top in ((-40, -70), (0, -96), (40, -70)):
        out += _rect(x - 4, top, 8, 24 - top)
        out += _poly([(x - 28, top + 12), (x + 28, top + 12), (x + 24, 0),
                      (x - 24, 0)])
        out += _poly([(x + 4, top), (x + 26, top + 6), (x + 4, top + 12)])
    return out


SHIP = _ship()

BOOK_CLOSED = (
    _rect(-70, -90, 140, 180) + _rect(-70, -90, 20, 180)
    + _band([(-36, -70), (56, -70), (56, 70), (-36, 70)], 4, WHITE, closed=True)
    + _rect(40, -10, 40, 20))

PENNON = (_rect(-86, -96, 12, 196)
          + _path("M -74,-90 L 96,-70 L 60,-40 L 96,-10 L -74,0 Z")
          + _circle(-80, -98, 9))

COVERED_CUP = (
    _circle(0, -84, 10) + _path("M -60,-42 Q 0,-90 60,-42 Z")
    + _path("M -56,-40 L 56,-40 C 54,30 20,48 10,54 L -10,54 "
            "C -20,48 -54,30 -56,-40 Z")
    + _rect(-8, 54, 16, 26) + _rect(-46, 80, 92, 16))

SWORD_SCIMITAR = (
    _path("M -8,50 Q -24,-30 40,-98 Q 16,-30 10,50 Z")
    + _rect(-34, 50, 68, 10) + _rect(-6, 60, 12, 26) + _circle(0, 92, 8))

SWORD_INVERTED = (
    _poly([(0, 100), (15, 72), (15, -30), (-15, -30), (-15, 72)])
    + _rect(-62, -50, 124, 20) + _rect(-12, -88, 24, 38) + _circle(0, -94, 16))


def _mural_crown():
    pts = [(-80, 40), (-80, -56)]
    for left in (-80, -36, 12, 56):
        pts += [(left, -56), (left + 24, -56), (left + 24, -34)]
        if left < 56:
            pts += [(left + 44, -34)]
    pts += [(80, -56), (80, 40)]
    pts = [p for i, p in enumerate(pts) if i == 0 or p != pts[i - 1]]
    return (_poly(pts) + _band([(-80, 4), (80, 4)], 4, WHITE)
            + "".join(_band([(x, -30), (x, 4)], 4, WHITE) for x in (-40, 0, 40))
            + "".join(_band([(x, 4), (x, 40)], 4, WHITE) for x in (-60, -20, 20, 60)))


CROWN_MURAL = _mural_crown()

CROWN_EASTERN = (_rect(-80, 0, 160, 40)
                 + "".join(_poly([(x - 16, 0), (x, -70), (x + 16, 0)])
                           for x in (-64, -32, 0, 32, 64)))

CROWN_ROYAL = (
    _band([(-70, 20), (-60, -30), (-30, -56), (0, -60)], 10)
    + _band([(70, 20), (60, -30), (30, -56), (0, -60)], 10)
    + _band([(0, 20), (0, -60)], 10)
    + _circle(0, -70, 12) + _rect(-3, -100, 6, 22) + _rect(-10, -92, 20, 6)
    + _rect(-76, 20, 152, 40)
    + "".join(_circle(x, 40, 6, WHITE) for x in (-48, -16, 16, 48)))


def _castle():
    def crenellate(x0, x1, top, merlon=10):
        pts, x = [(x0, top)], x0
        while x + merlon * 2 <= x1 + 0.1:
            pts += [(x + merlon, top), (x + merlon, top + 10),
                    (x + merlon * 2, top + 10), (x + merlon * 2, top)]
            x += merlon * 2
        return pts + [(x1, top)]

    outline = ([(-90, 92)] + crenellate(-90, -50, -40) + [(-50, 0)]
               + crenellate(-50, -24, 0, 6.5)[1:] + [(-24, -80)]
               + crenellate(-24, 24, -80, 6)[1:] + [(24, 0)]
               + crenellate(24, 50, 0, 6.5)[1:] + [(50, -40)]
               + crenellate(50, 90, -40)[1:] + [(90, 92)])
    return (_poly(outline)
            + _path("M -16,92 L -16,52 Q 0,32 16,52 L 16,92 Z", WHITE)
            + "".join(_rect(x - 4, y, 8, 14, WHITE)
                      for x, y in ((-70, -16), (70, -16), (0, -54))))


CASTLE = _castle()

# --- crosses -------------------------------------------------------------------
# Each is one outline, built as a quarter and turned four times, so the arms
# meet without seams where separate shapes would draw an outline between them.


def _cross(arm):
    """Four copies of a top arm, from (x, -y) round to (-x, -y), as one polygon."""
    outline = []
    for _ in range(4):
        outline += arm[:-1]
        arm = [(y, -x) for x, y in arm]
    return _poly(outline)


CROSS_MOLINE = _cross([
    (10, -10), (10, -46), (20, -54), (34, -60), (44, -72), (46, -86),
    (40, -96), (32, -88), (26, -78), (16, -72), (6, -70), (0, -64),
    (-6, -70), (-16, -72), (-26, -78), (-32, -88), (-40, -96), (-46, -86),
    (-44, -72), (-34, -60), (-20, -54), (-10, -46), (-10, -10)])

CROSS_FLEURY = _cross([
    (10, -10), (10, -50), (22, -52), (34, -62), (36, -76), (28, -80),
    (20, -72), (12, -68), (8, -76), (10, -88), (0, -100), (-10, -88),
    (-8, -76), (-12, -68), (-20, -72), (-28, -80), (-36, -76), (-34, -62),
    (-22, -52), (-10, -50), (-10, -10)])

CROSS_POTENT = _cross([
    (10, -10), (10, -66), (34, -66), (34, -96), (-34, -96), (-34, -66),
    (-10, -66), (-10, -10)])

CROSS_MALTESE = _cross([(6, -6), (32, -96), (0, -70), (-32, -96), (-6, -6)])

CROSS_BOTTONY = (
    _rect(-10, -80, 20, 160) + _rect(-80, -10, 160, 20)
    + "".join(_circle(round(x, 1), round(y, 1), 13)
              for a in (0, 90, 180, 270)
              for x, y in _rotate([(0, -86), (-16, -72), (16, -72)], a)))

CROSS_CELTIC = (_ring(0, -39, 46, 34) + _rect(-11, -96, 22, 192)
                + _rect(-70, -50, 140, 22))

CROSS_LATIN = _rect(-11, -96, 22, 192) + _rect(-60, -60, 120, 22)

# --- stars and knots -------------------------------------------------------------


def _star(points, inner, hole=0):
    pts = []
    for i in range(points * 2):
        a = -math.pi / 2 + i * math.pi / points
        radius = 100 if i % 2 == 0 else inner
        pts.append((radius * math.cos(a), radius * math.sin(a)))
    return _poly(pts) + (_circle(0, 0, hole, WHITE) if hole else "")


MULLET_SIX = _star(6, 48)
MULLET_EIGHT = _star(8, 50)
MULLET_PIERCED = _star(5, 42, hole=20)
ESTOILE_EIGHT = _star(8, 26)


def _triquetra():
    pts = [(28 * (math.sin(t) + 2 * math.sin(2 * t)),
            28 * (math.cos(t) - 2 * math.cos(2 * t)) + 8)
           for t in [i * 2 * math.pi / 90 for i in range(90)]]
    return _band(pts, 12, closed=True)


TRIQUETRA = _triquetra()


def _triskelion():
    leg = [(0, 0), (0, -52), (34, -80)]
    foot = [(28, -90), (58, -84), (54, -74), (36, -70)]
    return ("".join(_band(_rotate(leg, k * 120), 18) + _poly(_rotate(foot, k * 120))
                    for k in range(3))
            + _circle(0, 0, 16))


TRISKELION = _triskelion()

# --- cosmic --------------------------------------------------------------------


def _sun_rays(count, inner, outer, wavy=False):
    out = ""
    for i in range(count):
        a = i * 2 * math.pi / count
        if wavy and i % 2:
            pts = []
            for j in range(9):
                t = j / 8.0
                rad = inner + (outer - inner) * t
                off = 0.10 * math.sin(t * 2 * math.pi)
                pts.append((rad * math.cos(a + off), rad * math.sin(a + off)))
            out += _band(pts, 7)
        else:
            out += _poly([(inner * math.cos(a - 0.14), inner * math.sin(a - 0.14)),
                          (outer * math.cos(a), outer * math.sin(a)),
                          (inner * math.cos(a + 0.14), inner * math.sin(a + 0.14))])
    return out


SUN_GLORY = _sun_rays(16, 54, 100, wavy=True) + _circle(0, 0, 56)

SUN_FACE = (_sun_rays(12, 58, 100) + _circle(0, 0, 60)
            + _circle(-20, -12, 7, WHITE) + _circle(20, -12, 7, WHITE)
            + _path("M -24,18 Q 0,40 24,18 Q 0,30 -24,18 Z", WHITE))

SUN_ECLIPSED = (_sun_rays(12, 58, 100) + _ring(0, 0, 60, 46)
                + _circle(0, 0, 40))

DECRESCENT = ('<g transform="rotate(-90)"><path fill-rule="evenodd" d="'
              'M 0 -100 a 100 100 0 1 0 0.01 0 Z '
              'M 0 -105 a 82 82 0 1 0 0.01 0 Z"/></g>')

FULL_MOON = (_circle(0, 0, 90)
             + _circle(-30, -26, 14, WHITE) + _circle(26, 20, 20, WHITE)
             + _circle(34, -34, 9, WHITE) + _circle(-24, 40, 10, WHITE))

COMET_STREAMING = (
    _path("M -30,-30 Q 30,-10 96,70 Q 20,20 -40,-10 Z")
    + _path("M -30,-30 Q 10,10 60,96 Q 0,30 -44,-16 Z")
    + _star(5, 22).replace('points="', 'transform="translate(-44 -44) scale(0.5)" points="'))

ARMILLARY = (
    _rect(-6, 60, 12, 26) + _rect(-40, 84, 80, 12)
    + '<g transform="rotate(-24)">' + _band(
        [(80 * math.cos(t), 24 * math.sin(t))
         for t in [i * 2 * math.pi / 60 for i in range(60)]], 8, closed=True)
    + '</g>'
    + _ring(0, 0, 80, 70)
    + _band([(0, -80), (0, 80)], 6)
    + _circle(0, 0, 14))

PLANET_MOONS = (_circle(0, 0, 50) + _circle(-78, -58, 14) + _circle(76, -30, 10)
                + _circle(58, 70, 16)
                + _band([(-40, 10), (40, -10)], 6, WHITE))

COMPASS_STAR = _star(4, 22) + _star(4, 22).replace(
    'points="', 'transform="rotate(45) scale(0.62)" points="') + _circle(0, 0, 8, WHITE)

from .charges import SHAPES as _SHAPES  # noqa: E402

ANCHOR_FOULED = _SHAPES["anchor"] + _band(
    [(-44, -56), (22, -40), (-22, -8), (30, 22), (-12, 50), (40, 70)], 6)

# --- the table ---------------------------------------------------------------------
#
# charge: [(key, blazon, blazon plural, plain, plain plural, names, poses, shape)]
#
# The first entry is the charge as it was, named and drawn by nothing extra.
# `names` identify the variant on their own in a description ("a scimitar",
# "a lion's head"); `poses` qualify a charge that is named ("a walking lion").

VARIANTS = {
    "lion": [
        ("rampant", None, None, None, None, [], ["rampant", "rearing"], None),
        ("passant", "lion passant", "lions passant", "walking lion", "walking lions",
         [], ["passant", "walking", "striding", "prowling"], LION_PASSANT),
        ("sejant", "lion sejant", "lions sejant", "sitting lion", "sitting lions",
         [], ["sejant", "sitting", "seated"], LION_SEJANT),
        ("couchant", "lion couchant", "lions couchant", "lying lion", "lying lions",
         [], ["couchant", "lying", "resting", "sleeping"], LION_COUCHANT),
        ("head", "lion's head", "lions' heads", "lion's head", "lions' heads",
         ["lion's head", "lion head", "lions' heads", "lion heads"], ["head"],
         LION_HEAD),
    ],
    "horse": [
        ("forcene", None, None, None, None, [], ["rearing", "forcene", "rampant"], None),
        ("passant", "horse passant", "horses passant", "walking horse",
         "walking horses", [], ["passant", "walking", "trotting"], HORSE_PASSANT),
        ("courant", "horse courant", "horses courant", "galloping horse",
         "galloping horses", [], ["courant", "galloping", "running"], HORSE_COURANT),
        ("head", "horse's head", "horses' heads", "horse's head", "horses' heads",
         ["horse's head", "horse head"], ["head"], HORSE_HEAD),
    ],
    "stag": [
        ("statant", None, None, None, None, [], ["standing", "statant", "at gaze"], None),
        ("courant", "stag courant", "stags courant", "leaping stag", "leaping stags",
         [], ["courant", "leaping", "running", "springing"], STAG_COURANT),
        ("lodged", "stag lodged", "stags lodged", "lying stag", "lying stags",
         [], ["lodged", "lying", "resting"], STAG_LODGED),
        ("caboshed", "stag's head caboshed", "stags' heads caboshed", "stag's head",
         "stags' heads", ["stag's head", "stag head", "deer head", "deer's head"],
         ["head", "caboshed"], STAG_CABOSHED),
    ],
    "eagle": [
        ("displayed", None, None, None, None, [], ["displayed", "spread"], None),
        ("double", "double-headed eagle", "double-headed eagles", "two-headed eagle",
         "two-headed eagles", ["double-headed eagle", "two-headed eagle",
                               "double headed eagle"], ["double-headed", "two-headed"],
         EAGLE_DOUBLE),
        ("close", "eagle close", "eagles close", "perched eagle", "perched eagles",
         [], ["close", "perched"], EAGLE_CLOSE),
        ("rising", "eagle rising", "eagles rising", "rising eagle", "rising eagles",
         [], ["rising", "soaring"], EAGLE_RISING),
    ],
    "wolf": [
        ("passant", None, None, None, None, [], ["passant", "walking", "prowling"], None),
        ("rampant", "wolf rampant", "wolves rampant", "rearing wolf", "rearing wolves",
         [], ["rampant", "rearing"], WOLF_RAMPANT),
        ("head", "wolf's head", "wolves' heads", "wolf's head", "wolves' heads",
         ["wolf's head", "wolf head"], ["head"], WOLF_HEAD),
    ],
    "bear": [
        ("passant", None, None, None, None, [], ["passant", "walking"], None),
        ("rampant", "bear rampant", "bears rampant", "standing bear", "standing bears",
         [], ["rampant", "rearing", "standing"], BEAR_RAMPANT),
        ("head", "bear's head", "bears' heads", "bear's head", "bears' heads",
         ["bear's head", "bear head"], ["head"], BEAR_HEAD),
    ],
    "boar": [
        ("passant", None, None, None, None, [], ["passant", "walking"], None),
        ("head", "boar's head", "boars' heads", "boar's head", "boars' heads",
         ["boar's head", "boar head"], ["head"], BOAR_HEAD),
    ],
    "bull": [
        ("passant", None, None, None, None, [], ["passant", "walking"], None),
        ("head", "bull's head caboshed", "bulls' heads caboshed", "bull's head",
         "bulls' heads", ["bull's head", "bull head", "ox head"], ["head", "caboshed"],
         BULL_HEAD),
    ],
    "ram": [
        ("statant", None, None, None, None, [], ["statant", "standing"], None),
        ("head", "ram's head", "rams' heads", "ram's head", "rams' heads",
         ["ram's head", "ram head"], ["head"], RAM_HEAD),
    ],
    "hound": [
        ("courant", None, None, None, None, [], ["courant", "running"], None),
        ("sejant", "hound sejant", "hounds sejant", "sitting hound", "sitting hounds",
         [], ["sejant", "sitting", "seated"], HOUND_SEJANT),
    ],
    "hare": [
        ("courant", None, None, None, None, [], ["courant", "running"], None),
        ("sejant", "hare sejant", "hares sejant", "sitting hare", "sitting hares",
         [], ["sejant", "sitting", "seated"], HARE_SEJANT),
    ],
    "unicorn": [
        ("rampant", None, None, None, None, [], ["rampant", "rearing", "salient"], None),
        ("passant", "unicorn passant", "unicorns passant", "walking unicorn",
         "walking unicorns", [], ["passant", "walking"], UNICORN_PASSANT),
        ("head", "unicorn's head", "unicorns' heads", "unicorn's head",
         "unicorns' heads", ["unicorn's head", "unicorn head"], ["head"], UNICORN_HEAD),
    ],
    "pegasus": [
        ("passant", None, None, None, None, [], ["passant", "walking"], None),
        ("salient", "pegasus salient", "pegasi salient", "rearing winged horse",
         "rearing winged horses", [], ["salient", "rearing", "rampant"],
         PEGASUS_SALIENT),
    ],
    "dragon": [
        ("segreant", None, None, None, None, [], ["rampant", "rearing", "segreant"], None),
        ("passant", "dragon passant", "dragons passant", "walking dragon",
         "walking dragons", [], ["passant", "walking"], DRAGON_PASSANT),
        ("wyvern", "wyvern", "wyverns", "wyvern", "wyverns",
         ["wyvern", "wyverns", "two-legged dragon"], [], WYVERN),
    ],
    "fish": [
        ("naiant", None, None, None, None, [], ["naiant", "swimming"], None),
        ("hauriant", "fish hauriant", "fish hauriant", "leaping fish", "leaping fish",
         [], ["hauriant", "leaping", "upright"], FISH_HAURIANT),
    ],
    "serpent": [
        ("erect", None, None, None, None, [], ["erect"], None),
        ("nowed", "serpent nowed", "serpents nowed", "knotted snake", "knotted snakes",
         ["knotted snake", "knotted serpent"], ["nowed", "knotted"], SERPENT_NOWED),
        ("ouroboros", "serpent in annulet", "serpents in annulet",
         "snake eating its tail", "snakes eating their tails",
         ["ouroboros", "snake eating its tail"], ["coiled"], OUROBOROS),
    ],
    "raven": [
        ("standing", None, None, None, None, [], ["standing", "perched"], None),
        ("volant", "raven volant", "ravens volant", "flying raven", "flying ravens",
         [], ["volant", "flying"], RAVEN_VOLANT),
    ],
    "tree": [
        ("leafy", None, None, None, None, [], [], None),
        ("pine", "pine tree", "pine trees", "pine tree", "pine trees",
         ["pine tree", "pine", "fir tree", "fir", "evergreen"], [], TREE_PINE),
        ("palm", "palm tree", "palm trees", "palm tree", "palm trees",
         ["palm tree"], [], TREE_PALM),
        ("eradicated", "tree eradicated", "trees eradicated", "uprooted tree",
         "uprooted trees", ["uprooted tree"], ["eradicated", "uprooted"], TREE_UPROOTED),
    ],
    "rose": [
        ("heraldic", None, None, None, None, [], [], None),
        ("slipped", "rose slipped and leaved", "roses slipped and leaved",
         "rose on a stem", "roses on stems", ["rose on a stem", "long-stemmed rose"],
         ["slipped", "stemmed"], ROSE_SLIPPED),
    ],
    "acorn": [
        ("plain", None, None, None, None, [], [], None),
        ("slipped", "acorn slipped and leaved", "acorns slipped and leaved",
         "acorn on a sprig", "acorns on sprigs", [], ["slipped"], ACORN_SLIPPED),
    ],
    "mountain": [
        ("range", None, None, None, None, [], [], None),
        ("mount", "mount", "mounts", "hill", "hills", ["mount", "hill", "hillock"],
         [], MOUNT),
    ],
    "heart": [
        ("plain", None, None, None, None, [], [], None),
        ("flaming", "flaming heart", "flaming hearts", "flaming heart", "flaming hearts",
         ["flaming heart", "heart on fire", "burning heart"], ["flaming", "burning"],
         FLAMING_HEART),
    ],
    "skull": [
        ("plain", None, None, None, None, [], [], None),
        ("crossbones", "skull and crossbones", "skulls and crossbones",
         "skull and crossbones", "skulls and crossbones",
         ["skull and crossbones", "jolly roger", "crossbones"], [], SKULL_CROSSBONES),
    ],
    "eye": [
        ("plain", None, None, None, None, [], [], None),
        ("providence", "eye of providence", "eyes of providence", "all-seeing eye",
         "all-seeing eyes", ["eye of providence", "all-seeing eye", "all seeing eye"],
         [], EYE_PROVIDENCE),
    ],
    "axe": [
        ("plain", None, None, None, None, [], [], None),
        ("double", "double-headed axe", "double-headed axes", "double-headed axe",
         "double-headed axes", ["double axe", "double-headed axe", "labrys"],
         ["double-headed"], AXE_DOUBLE),
    ],
    "hammer": [
        ("plain", None, None, None, None, [], [], None),
        ("thor", "hammer of Thor", "hammers of Thor", "Thor's hammer", "Thor's hammers",
         ["thor's hammer", "mjolnir", "mjölnir", "hammer of thor"], [], HAMMER_THOR),
    ],
    "wheel": [
        ("cart", None, None, None, None, [], [], None),
        ("catherine", "Catherine wheel", "Catherine wheels", "spiked wheel",
         "spiked wheels", ["catherine wheel", "spiked wheel"], ["spiked"],
         WHEEL_CATHERINE),
    ],
    "arrow": [
        ("plain", None, None, None, None, [], [], None),
        ("pheon", "pheon", "pheons", "arrowhead", "arrowheads",
         ["pheon", "arrowhead", "broad arrow"], [], PHEON),
    ],
    "helm": [
        ("great", None, None, None, None, [], [], None),
        ("norman", "Norman helm", "Norman helms", "Norman helmet", "Norman helmets",
         ["norman helm", "norman helmet", "viking helmet", "conical helmet"], [],
         HELM_NORMAN),
    ],
    "lymphad": [
        ("galley", None, None, None, None, [], [], None),
        ("ship", "ship", "ships", "sailing ship", "sailing ships",
         ["sailing ship", "carrack", "ship with sails", "tall ship"], [], SHIP),
    ],
    "book": [
        ("open", None, None, None, None, [], ["open"], None),
        ("closed", "book closed", "books closed", "closed book", "closed books",
         ["closed book"], ["closed", "shut"], BOOK_CLOSED),
    ],
    "banner": [
        ("flag", None, None, None, None, [], [], None),
        ("pennon", "pennon", "pennons", "swallow-tailed pennant",
         "swallow-tailed pennants", ["pennon", "pennant", "swallowtail"], [], PENNON),
    ],
    "chalice": [
        ("open", None, None, None, None, [], [], None),
        ("covered", "covered cup", "covered cups", "lidded cup", "lidded cups",
         ["covered cup", "lidded cup"], ["covered", "lidded"], COVERED_CUP),
    ],
    "anchor": [
        ("plain", None, None, None, None, [], [], None),
        ("fouled", "anchor fouled", "anchors fouled", "roped anchor", "roped anchors",
         ["fouled anchor"], ["fouled", "roped"], ANCHOR_FOULED),
    ],
    "sword": [
        ("erect", None, None, None, None, [], ["erect", "upright"], None),
        ("scimitar", "scimitar", "scimitars", "curved sword", "curved swords",
         ["scimitar", "sabre", "saber", "cutlass", "curved sword"], [], SWORD_SCIMITAR),
        ("inverted", "sword inverted", "swords inverted", "sword pointing down",
         "swords pointing down", [], ["inverted", "reversed"], SWORD_INVERTED),
    ],
    "crown": [
        ("ducal", None, None, None, None, [], [], None),
        ("mural", "mural crown", "mural crowns", "castle crown", "castle crowns",
         ["mural crown", "castle crown"], [], CROWN_MURAL),
        ("eastern", "eastern crown", "eastern crowns", "spiked crown", "spiked crowns",
         ["eastern crown", "spiked crown"], [], CROWN_EASTERN),
        ("royal", "royal crown", "royal crowns", "royal crown", "royal crowns",
         ["royal crown", "imperial crown", "king's crown"], [], CROWN_ROYAL),
    ],
    "tower": [
        ("single", None, None, None, None, [], [], None),
        ("castle", "castle", "castles", "castle", "castles",
         ["castle", "fortress"], [], CASTLE),
    ],
    "cross patée": [
        ("patee", None, None, None, None, [], [], None),
        ("maltese", "Maltese cross", "Maltese crosses", "Maltese cross",
         "Maltese crosses", ["maltese cross"], [], CROSS_MALTESE),
    ],
    "cross crosslet": [
        ("crosslet", None, None, None, None, [], [], None),
        ("moline", "cross moline", "crosses moline", "cross with curled ends",
         "crosses with curled ends", ["cross moline", "moline cross"], [], CROSS_MOLINE),
        ("fleury", "cross fleury", "crosses fleury", "cross with lily ends",
         "crosses with lily ends", ["cross fleury", "cross flory", "fleury cross"], [],
         CROSS_FLEURY),
        ("bottony", "cross bottony", "crosses bottony", "cross with trefoil ends",
         "crosses with trefoil ends", ["cross bottony", "budded cross"], [],
         CROSS_BOTTONY),
        ("potent", "cross potent", "crosses potent", "cross with T-shaped ends",
         "crosses with T-shaped ends", ["cross potent", "crutch cross"], [],
         CROSS_POTENT),
        ("celtic", "Celtic cross", "Celtic crosses", "Celtic cross", "Celtic crosses",
         ["celtic cross", "ringed cross"], [], CROSS_CELTIC),
        ("latin", "Latin cross", "Latin crosses", "Latin cross", "Latin crosses",
         ["latin cross", "christian cross", "passion cross"], [], CROSS_LATIN),
    ],
    "mullet": [
        ("five", None, None, None, None, [], [], None),
        ("six", "mullet of six points", "mullets of six points", "six-pointed star",
         "six-pointed stars", ["six-pointed star", "six pointed star"], [], MULLET_SIX),
        ("eight", "mullet of eight points", "mullets of eight points",
         "eight-pointed star", "eight-pointed stars",
         ["eight-pointed star", "eight pointed star"], [], MULLET_EIGHT),
        ("pierced", "mullet pierced", "mullets pierced", "star with a hole",
         "stars with holes", [], ["pierced"], MULLET_PIERCED),
    ],
    "estoile": [
        ("six", None, None, None, None, [], [], None),
        ("eight", "estoile of eight rays", "estoiles of eight rays", "eight-rayed star",
         "eight-rayed stars", ["eight-rayed star"], [], ESTOILE_EIGHT),
    ],
    "bowen knot": [
        ("bowen", None, None, None, None, [], [], None),
        ("triquetra", "triquetra", "triquetras", "three-looped knot",
         "three-looped knots", ["triquetra", "trinity knot"], [], TRIQUETRA),
    ],
    "triskele": [
        ("spiral", None, None, None, None, [], [], None),
        ("legs", "triskelion", "triskelions", "three running legs",
         "sets of three running legs", ["triskelion", "three legs", "isle of man"], [],
         TRISKELION),
    ],
    "sun in splendour": [
        ("splendour", None, None, None, None, [], [], None),
        ("glory", "sun in glory", "suns in glory", "blazing sun", "blazing suns",
         ["sun in glory", "blazing sun"], [], SUN_GLORY),
        ("face", "sun with a face", "suns with faces", "smiling sun", "smiling suns",
         ["sun with a face", "smiling sun", "sun face"], [], SUN_FACE),
        ("eclipsed", "sun eclipsed", "suns eclipsed", "eclipsed sun", "eclipsed suns",
         ["eclipse", "eclipsed sun", "solar eclipse"], ["eclipsed"], SUN_ECLIPSED),
    ],
    "crescent": [
        ("crescent", None, None, None, None, [], [], None),
        ("decrescent", "decrescent", "decrescents", "crescent moon facing left",
         "crescent moons facing left", ["decrescent", "waning moon"], [], DECRESCENT),
        ("full", "moon in her plenitude", "moons in their plenitude", "full moon",
         "full moons", ["full moon", "moon in her plenitude"], [], FULL_MOON),
    ],
    "comet": [
        ("plain", None, None, None, None, [], [], None),
        ("streaming", "comet streaming", "comets streaming", "streaming comet",
         "streaming comets", ["shooting star", "streaming comet"], ["streaming"],
         COMET_STREAMING),
    ],
    "orb": [
        ("royal", None, None, None, None, [], [], None),
        ("armillary", "armillary sphere", "armillary spheres", "armillary sphere",
         "armillary spheres", ["armillary sphere", "armillary", "astrolabe"], [],
         ARMILLARY),
    ],
    "ringed planet": [
        ("ringed", None, None, None, None, [], [], None),
        ("moons", "planet with moons", "planets with moons", "planet with moons",
         "planets with moons", ["planet with moons"], [], PLANET_MOONS),
    ],
    "compass rose": [
        ("rose", None, None, None, None, [], [], None),
        ("star", "compass star", "compass stars", "compass star", "compass stars",
         ["compass star", "north star", "polaris"], [], COMPASS_STAR),
    ],
}


def options(charge):
    return VARIANTS.get(charge, [])


def get(charge, key):
    """The variant entry for a charge and key, or None."""
    for form in VARIANTS.get(charge, ()):
        if form[0] == key:
            return form
    return None


def shape(charge, key):
    form = get(charge, key)
    return form[7] if form else None


def by_pose(charge, word):
    """The key of the variant a pose word asks for, or None if it has none."""
    for form in VARIANTS.get(charge, ()):
        if word in form[6]:
            return form[0]
    return None


def pick(charge, rng):
    """A variant for a charge, without touching the roll's own sequence.

    The generator is seeded from the roll's current state, so the same roll
    always picks the same variant and nothing it goes on to pick shifts. The
    charge's own form counts double: the familiar drawing should still be the
    commonest.
    """
    forms = VARIANTS.get(charge)
    if not forms:
        return None
    side = random.Random(hash(rng.getstate()))
    return side.choices(forms, [2] + [1] * (len(forms) - 1))[0][0]
