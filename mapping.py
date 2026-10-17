"""Pure functions that turn a pinch distance into a volume, kept free of camera and audio imports so they can be tested."""
import numpy as np


def pinch_to_percent(length, low, high):
    """0 at or below `low` pixels, 100 at or above `high`, linear between."""
    return float(np.interp(length, [low, high], [0, 100]))


def percent_to_decibel(percent, min_db, max_db):
    """Windows endpoint volume is set in decibels over the device's own range."""
    return float(np.interp(percent, [0, 100], [min_db, max_db]))
