"""Jitter of the volume before and after smoothing, on a synthetic noisy pinch (no webcam needed).

A held pinch at a fixed ratio plus Gaussian landmark noise stands in for a steady hand. Jitter is the
standard deviation of the resulting volume in percentage points; lag is the frames needed to reach 90%
of a step from 0% to 100%.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config  # noqa: E402
from mapping import pinch_to_percent, smooth  # noqa: E402

HELD_RATIO = 0.575
NOISE_STD = 0.03
FRAMES = 3000
SEED = 7


def volumes(ratios, alpha):
    out, smoothed = [], None
    for ratio in ratios:
        smoothed = smooth(smoothed, ratio, alpha)
        out.append(pinch_to_percent(smoothed, config.PINCH_MIN_RATIO, config.PINCH_MAX_RATIO))
    return np.array(out)


def jitter(alpha):
    noise = np.random.default_rng(SEED).normal(0, NOISE_STD, FRAMES)
    return float(volumes(HELD_RATIO + noise, alpha).std())


def lag_frames(alpha):
    step = np.concatenate([np.full(1, config.PINCH_MIN_RATIO), np.full(100, config.PINCH_MAX_RATIO)])
    return int(np.argmax(volumes(step, alpha) >= 90))


if __name__ == "__main__":
    for label, alpha in (("off", 1.0), ("default", config.SMOOTHING_ALPHA)):
        print(f"alpha {alpha} ({label}): jitter {jitter(alpha):.2f} points, 90% of a step after {lag_frames(alpha)} frames")
