"""Fit the two fist thresholds on the fit split (data/hagrid-fit.json.gz) and print them.

A grid search over (largest finger extension, thumb reach) that maximises F0.5 for "fist" against every
other hand, so precision counts twice as much as recall: a mute the user did not ask for is worse than a
fist that needs a second try. The test split is never read here. Run in CI, not on the laptop.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from gestures import fist_features  # noqa: E402
import gesture_data  # noqa: E402

BETA = 0.5
EXTENSIONS = [round(0.70 + 0.01 * i, 2) for i in range(71)]   # 0.70 to 1.40
REACHES = [round(0.20 + 0.01 * i, 2) for i in range(131)]     # 0.20 to 1.50


def f_beta(precision, recall, beta=BETA):
    if precision == 0 and recall == 0:
        return 0.0
    return (1 + beta ** 2) * precision * recall / (beta ** 2 * precision + recall)


def fit(rows):
    feats = [(label, fist_features(points)) for label, points in rows]
    feats = [(label, f) for label, f in feats if f is not None]
    labels = [label for label, _ in feats]
    best = None
    for ext in EXTENSIONS:
        for reach in REACHES:
            predicted = [f[0] <= ext and f[1] <= reach for _, f in feats]
            s = gesture_data.scores(predicted, labels)
            key = (f_beta(s["precision"], s["recall"]), s["precision"])
            if best is None or key > best[0]:
                best = (key, ext, reach, s)
    return best


def main():
    (score, _), ext, reach, s = fit(gesture_data.load("fit"))
    print(f"fit split: FIST_MAX_EXTENSION={ext} FIST_MAX_THUMB_REACH={reach}  F0.5 {score:.3f}  "
          f"precision {s['precision']:.3f} recall {s['recall']:.3f} (tp {s['tp']}, fp {s['fp']}, fn {s['fn']})")


if __name__ == "__main__":
    main()
