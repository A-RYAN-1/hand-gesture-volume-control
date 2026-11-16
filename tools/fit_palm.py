"""Fit the two open-palm thresholds on the fit split (data/hagrid-fit.json.gz) and print them.

The same method as tools/fit_fist.py: a grid search over (smallest finger extension, thumb reach) that
maximises F0.5 for "open palm" against every other hand, so precision counts twice as much as recall: a pause
the user did not ask for is worse than a palm that needs a second try. The open palm is the HaGRID labels
`palm`, `stop` and `stop_inverted`. The test split is never read here. Run in CI, not on the laptop.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from gestures import palm_features  # noqa: E402
import gesture_data  # noqa: E402
from fit_fist import f_beta  # noqa: E402

PALM_LABELS = ("palm", "stop", "stop_inverted")
EXTENSIONS = [round(0.80 + 0.01 * i, 2) for i in range(81)]   # 0.80 to 1.60
REACHES = [round(0.20 + 0.01 * i, 2) for i in range(181)]     # 0.20 to 2.00 (covers both thumb measures)


THUMB_MEASURES = ("reach", "extension")


def fit(rows, thumb="reach"):
    feats = [(label, palm_features(points, thumb)) for label, points in rows]
    feats = [(label, f) for label, f in feats if f is not None]
    labels = [label for label, _ in feats]
    best = None
    for ext in EXTENSIONS:
        for reach in REACHES:
            predicted = [f[0] >= ext and f[1] >= reach for _, f in feats]
            s = gesture_data.scores(predicted, labels, positive=PALM_LABELS)
            key = (f_beta(s["precision"], s["recall"]), s["precision"])
            if best is None or key > best[0]:
                best = (key, ext, reach, s)
    return best


def main():
    rows = gesture_data.load("fit")
    for thumb in THUMB_MEASURES:
        (score, _), ext, value, s = fit(rows, thumb)
        print(f"fit split, thumb {thumb}: PALM_MIN_EXTENSION={ext} PALM_MIN_THUMB={value}  F0.5 {score:.3f}  "
              f"precision {s['precision']:.3f} recall {s['recall']:.3f} (tp {s['tp']}, fp {s['fp']}, fn {s['fn']})")


if __name__ == "__main__":
    main()
