"""Pure functions that turn a pinch into a volume, kept free of camera and audio imports so they can be tested."""
import math

import numpy as np

WRIST, MIDDLE_MCP = 0, 9
THUMB_TIP, INDEX_TIP = 4, 8


def _distance(points, a, b):
    """Pixel distance between landmarks `a` and `b` in a list of [id, x, y] points."""
    return math.hypot(points[b][1] - points[a][1], points[b][2] - points[a][2])


def pinch_ratio(points):
    """Thumb-tip to index-tip distance divided by the wrist to middle-finger-knuckle distance.

    The hand-size reference scales with the hand, so the ratio is the same at any distance from the
    camera. Returns None when the reference is zero, which means the landmarks are not usable.
    """
    hand_size = _distance(points, WRIST, MIDDLE_MCP)
    if hand_size == 0:
        return None
    return _distance(points, THUMB_TIP, INDEX_TIP) / hand_size


def pinch_to_percent(ratio, low, high):
    """0 at or below `low`, 100 at or above `high`, linear between."""
    return float(np.interp(ratio, [low, high], [0, 100]))


def percent_to_decibel(percent, min_db, max_db):
    """Windows endpoint volume is set in decibels over the device's own range."""
    return float(np.interp(percent, [0, 100], [min_db, max_db]))


def smooth(previous, current, alpha):
    """Exponential moving average of the pinch ratio: `alpha` 1 follows the raw signal, lower is steadier.

    `previous` is None for the first frame after a hand appears, which starts the average at `current`.
    """
    if previous is None:
        return current
    return alpha * current + (1 - alpha) * previous
