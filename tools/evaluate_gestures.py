"""Report the fist classifier with the thresholds in config.py on held-out hands.

  python tools/evaluate_gestures.py            the HaGRID test split (data/hagrid-test.json.gz)
  python tools/evaluate_gestures.py <file>     a personal set written by tools/record_landmarks.py

Prints fist precision and recall, then for every other label the share of its hands taken for a fist;
`no_gesture` hands (people's hands at rest in the same photos) stand in for an idle hand. These are photos,
not webcam frames, so the per-frame rates say nothing about false mutes per minute of video. Run in CI.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
import config  # noqa: E402
from gestures import is_fist  # noqa: E402
import gesture_data  # noqa: E402


def evaluate(rows, max_extension=None, max_thumb_reach=None):
    ext = config.FIST_MAX_EXTENSION if max_extension is None else max_extension
    reach = config.FIST_MAX_THUMB_REACH if max_thumb_reach is None else max_thumb_reach
    labels = [label for label, _ in rows]
    predicted = [is_fist(points, ext, reach) for _, points in rows]
    result = gesture_data.scores(predicted, labels)
    per_label = {}
    for p, label in zip(predicted, labels):
        hit, total = per_label.get(label, (0, 0))
        per_label[label] = (hit + p, total + 1)
    result["taken_for_fist"] = {label: hit / total for label, (hit, total) in sorted(per_label.items())}
    result["hands"] = len(rows)
    return result


def main(argv):
    name = argv[0] if argv else "test"
    r = evaluate(gesture_data.load(name))
    print(f"{name}: {r['hands']} hands, thresholds extension {config.FIST_MAX_EXTENSION}, thumb reach {config.FIST_MAX_THUMB_REACH}")
    print(f"fist precision {r['precision']:.3f}  recall {r['recall']:.3f}  (tp {r['tp']}, fp {r['fp']}, fn {r['fn']})")
    print("share of each label taken for a fist:")
    for label, share in r["taken_for_fist"].items():
        print(f"  {label:<16} {share:.3f}")


if __name__ == "__main__":
    main(sys.argv[1:])
