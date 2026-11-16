"""The mute gesture: a fist classified from the 21 hand landmarks, kept free of camera and audio imports.

Two measurements decide it, both divided by hand size so the distance from the camera does not matter:
- finger extension: for the index, middle, ring and little finger, the wrist-to-tip distance divided by the
  wrist-to-middle-joint (PIP) distance. A straight finger is well above 1; a curled one folds its tip back
  towards the palm and drops to about 1 or below. The largest of the four is used, so one straight finger
  is enough to say "not a fist".
- thumb reach: the thumb-tip to middle-knuckle distance divided by the hand size. A thumb folded across the
  fingers stays close; a thumbs-up or thumbs-down (the hardest look-alikes) reaches far.
The two thresholds are fitted on recorded hands (tools/fit_fist.py) and reported on held-out ones
(tools/evaluate_gestures.py); config.py holds the fitted values.
"""
import math

WRIST, THUMB_TIP, MIDDLE_MCP = 0, 4, 9
FINGERS = ((8, 6), (12, 10), (16, 14), (20, 18))  # (tip, PIP) of index, middle, ring, little finger


def _distance(points, a, b):
    return math.hypot(points[b][1] - points[a][1], points[b][2] - points[a][2])


def _extensions_and_reach(points):
    """([extension of each of the four fingers], thumb reach), or None when the hand is degenerate."""
    hand_size = _distance(points, WRIST, MIDDLE_MCP)
    if hand_size == 0:
        return None
    extensions = []
    for tip, pip in FINGERS:
        to_pip = _distance(points, WRIST, pip)
        if to_pip == 0:
            return None
        extensions.append(_distance(points, WRIST, tip) / to_pip)
    return extensions, _distance(points, THUMB_TIP, MIDDLE_MCP) / hand_size


def fist_features(points):
    """(largest finger extension, thumb reach) for [id, x, y] points, or None when the hand is degenerate."""
    measured = _extensions_and_reach(points)
    if measured is None:
        return None
    extensions, reach = measured
    return max(extensions), reach


THUMB_MCP = 2


def thumb_extension(points):
    """Wrist-to-thumb-tip distance over wrist-to-thumb-base distance: well above 1 for a thumb held out
    straight, near 1 for a thumb folded over the palm. None when the hand is degenerate."""
    base = _distance(points, WRIST, THUMB_MCP)
    return None if base == 0 else _distance(points, WRIST, THUMB_TIP) / base


def palm_features(points, thumb="reach"):
    """(smallest finger extension, thumb measure), or None. The open palm is the mirror of the fist: the
    smallest extension is high only when every finger is straight, and the thumb is out. `thumb` picks the
    thumb measure: "reach" (tip to middle knuckle over hand size) or "extension" (see thumb_extension)."""
    measured = _extensions_and_reach(points)
    if measured is None:
        return None
    extensions, reach = measured
    if thumb == "reach":
        return min(extensions), reach
    out = thumb_extension(points)
    return None if out is None else (min(extensions), out)


def is_fist(points, max_extension, max_thumb_reach):
    """True when every finger is curled and the thumb is tucked in."""
    features = fist_features(points)
    if features is None:
        return False
    extension, reach = features
    return extension <= max_extension and reach <= max_thumb_reach


def is_palm(points, min_extension, min_thumb, thumb="reach"):
    """True when all four fingers are straight and the thumb is out: an open hand, seen from any side."""
    features = palm_features(points, thumb)
    if features is None:
        return False
    extension, thumb_value = features
    return extension >= min_extension and thumb_value >= min_thumb


class GestureHold:
    """Guardrail: a gesture acts only after `frames` frames in a row, and once per hold.

    `update` returns True on the one frame where the hold completes. The gesture has to be released (one
    frame without it) before it can act again, so holding a fist mutes once instead of flickering.
    """

    def __init__(self, frames):
        if frames < 1:
            raise ValueError("frames must be at least 1")
        self.frames = frames
        self._count = 0

    @property
    def forming(self):
        """True while the gesture is seen, from its first frame until it is released."""
        return self._count > 0

    def update(self, active):
        if not active:
            self._count = 0
            return False
        self._count += 1
        return self._count == self.frames


class PalmHold:
    """Guardrail for the open palm: it acts only after `frames` frames in a row in which the hand stays still.

    "Still" means the middle knuckle stays within `max_move` hand sizes of where it was when the hold began; a
    hand that drifts further starts the count again from where it now is. Like GestureHold it fires once per
    hold and has to be released (one frame without the palm) before it can act again.
    """

    def __init__(self, frames, max_move):
        if frames < 1:
            raise ValueError("frames must be at least 1")
        if max_move <= 0:
            raise ValueError("max_move must be above 0")
        self.frames = frames
        self.max_move = max_move
        self._count = 0
        self._anchor = None

    @property
    def forming(self):
        """True while a palm is seen, from its first frame until it is released."""
        return self._count > 0

    def update(self, active, points=None):
        """`points` are the hand's [id, x, y] landmarks; needed whenever `active` is True."""
        if not active:
            self._count, self._anchor = 0, None
            return False
        size = _distance(points, WRIST, MIDDLE_MCP)
        centre = (points[MIDDLE_MCP][1], points[MIDDLE_MCP][2])
        if self._anchor is None or math.hypot(centre[0] - self._anchor[0], centre[1] - self._anchor[1]) > self.max_move * size:
            self._count, self._anchor = 0, centre
        self._count += 1
        return self._count == self.frames
