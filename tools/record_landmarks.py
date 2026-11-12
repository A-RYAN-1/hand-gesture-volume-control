"""Record your own labelled hands for tools/evaluate_gestures.py: landmarks only, never a picture.

  python tools/record_landmarks.py fist 20 me.jsonl        hold a fist in view for 20 seconds
  python tools/record_landmarks.py idle 60 me.jsonl        use the computer as usual for a minute
  python tools/evaluate_gestures.py me.jsonl

Each line of the output is {"label": ..., "lm": 21 [x, y] pairs as fractions of the frame}, appended, so one
file collects several recordings. Label the recordings of anything that is not a fist with any other word;
a minute of `idle` frames gives a per-frame false mute rate for your own camera and desk.
"""
import json
import os
import sys
import time

import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config  # noqa: E402
from handdetect import HandTracker  # noqa: E402


def main(label, seconds, out):
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open camera {config.CAMERA_INDEX}; set the CAMERA_INDEX environment variable")
    tracker = HandTracker()
    ends, frames, kept = time.monotonic() + seconds, 0, 0
    try:
        with open(out, "a", encoding="utf-8") as f:
            while time.monotonic() < ends:
                ok, frame = cap.read()
                if not ok:
                    break
                frames += 1
                hand = tracker.first_hand(cv2.flip(frame, 1))
                if hand is not None:
                    f.write(json.dumps({"label": label, "lm": [[round(p.x, 4), round(p.y, 4)] for p in hand.landmark]}) + "\n")
                    kept += 1
    finally:
        cap.release()
    print(f"{label}: {kept} of {frames} frames had a hand, appended to {out}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(sys.argv[1], float(sys.argv[2]), sys.argv[3])
