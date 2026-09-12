"""Lines of partition: the edge treatments heraldry uses instead of a straight cut.

Every division and every ordinary in real heraldry can take one of these, and it
is the cheapest source of variety in the whole system -- seven line styles times
the existing divisions and ordinaries, before a charge is even placed.

Each style is a profile: a function from t in 0..1 to a perpendicular offset in
shield units. The caller walks a line, offsets each sample, and gets a polyline
it can build a polygon from.

Amplitude is deliberately generous. At 24 columns the shield is 48 dots across,
so a wave one unit deep is half a dot and simply disappears; these are sized to
survive being thresholded to 1-bit, not to look correct on parchment.

Copyright (C) 2026 Caden DeNike. Free software under the GNU General
Public License, version 3 or later, with no warranty. See LICENSE.
"""

import math

# Style -> (period in shield units, amplitude in shield units).
# Period is how often the feature repeats along the line; too fine and the
# threshold turns it into a grey smear rather than a shape.
STYLES = {
    "plain": (0.0, 0.0),
    "wavy": (26.0, 5.0),
    "engrailed": (22.0, 5.0),
    "invected": (22.0, 5.0),
    "indented": (16.0, 4.5),
    "dancetty": (34.0, 8.0),
    "embattled": (24.0, 5.0),
    "nebuly": (30.0, 7.0),
}

# The ones worth rolling at random. "invected" is engrailed mirrored, which is a
# real distinction on paper and an invisible one at this size, so it is kept in
# STYLES for correctness but left out of the pool.
POOL = ["wavy", "engrailed", "indented", "dancetty", "embattled", "nebuly"]


def _profile(style, u):
    """Perpendicular offset at position u (in repeats), normalised to -1..1."""
    frac = u - math.floor(u)
    if style == "wavy" or style == "nebuly":
        return math.sin(2 * math.pi * frac)
    if style == "engrailed":
        # Scallops biting into one side only: a run of half-circles.
        return -abs(math.sin(math.pi * frac))
    if style == "invected":
        return abs(math.sin(math.pi * frac))
    if style == "indented":
        # Triangular wave.
        return 4 * abs(frac - 0.5) - 1
    if style == "dancetty":
        return 4 * abs(frac - 0.5) - 1
    if style == "embattled":
        # Square wave, with the corners left sharp: merlons want to be square.
        return 1.0 if frac < 0.5 else -1.0
    return 0.0


def points(p0, p1, style, samples=None, phase=0.0, scale=1.0):
    """Walk from p0 to p1, returning a polyline with `style` applied.

    `scale` shrinks the amplitude for lines that must stay inside a narrow
    shape, such as the two edges of a thin ordinary.
    """
    if style == "plain" or style not in STYLES:
        return [p0, p1]

    period, amp = STYLES[style]
    amp *= scale
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length < 1e-6 or period <= 0:
        return [p0, p1]

    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux  # unit perpendicular

    repeats = max(1.0, length / period)
    if samples is None:
        # Embattled needs its corners landing exactly on the step edges, so it
        # is sampled on a grid tied to the period rather than a smooth curve's.
        per_repeat = 4 if style == "embattled" else 12
        samples = max(8, int(repeats * per_repeat))

    out = []
    for i in range(samples + 1):
        t = i / samples
        u = t * repeats + phase
        off = _profile(style, u) * amp
        out.append((x0 + dx * t + nx * off, y0 + dy * t + ny * off))
    return out

