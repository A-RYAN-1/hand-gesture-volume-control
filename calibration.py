"""Per-user pinch calibration, kept free of camera and audio imports so it can be tested.

During a short window the user opens and closes the pinch a few times. The 5th and 95th percentiles of the
pinch ratios seen become that user's 0% and 100%, so a small hand or a stiff thumb can still reach both
ends. Percentiles rather than the extremes, so one bad landmark frame does not stretch the range.
"""
import json
import os
from datetime import date

import numpy as np

LOW_PERCENTILE, HIGH_PERCENTILE = 5, 95
MIN_FRAMES = 30
MIN_SPAN = 0.2


class CalibrationError(ValueError):
    """The recorded pinch cannot give a usable range; the message says what to do."""


def calibrate(ratios):
    """(low, high) pinch ratios from the ratios recorded during calibration."""
    values = [r for r in ratios if r is not None]
    if len(values) < MIN_FRAMES:
        raise CalibrationError(f"only {len(values)} frames with a hand; keep the hand in view and try again")
    low, high = (float(v) for v in np.percentile(values, [LOW_PERCENTILE, HIGH_PERCENTILE]))
    if high - low < MIN_SPAN:
        raise CalibrationError("the pinch barely moved; open and close thumb and index fully and try again")
    return round(low, 3), round(high, 3)


class CalibrationSession:
    """Collects pinch ratios for `seconds`, timed by the `now` values the caller passes in."""

    def __init__(self, started, seconds):
        self.ends = started + seconds
        self.ratios = []

    def add(self, ratio):
        self.ratios.append(ratio)

    def remaining(self, now):
        return max(0.0, self.ends - now)

    def done(self, now):
        return now >= self.ends


def save(path, low, high):
    """Write the profile; the folder is created when missing."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"pinch_min_ratio": low, "pinch_max_ratio": high, "calibrated": date.today().isoformat()}, f, indent=1)


def load(path):
    """(low, high) from a saved profile, or None when there is none or it is not usable."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        low, high = float(data["pinch_min_ratio"]), float(data["pinch_max_ratio"])
    except FileNotFoundError:
        return None
    except (ValueError, KeyError, TypeError):
        print(f"Ignoring {path}: not a calibration profile; press the calibration key to make a new one")
        return None
    if not 0 <= low < high:
        print(f"Ignoring {path}: its range is not usable; press the calibration key to make a new one")
        return None
    return low, high
