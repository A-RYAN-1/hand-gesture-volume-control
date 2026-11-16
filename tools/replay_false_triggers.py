"""Replay a recorded session through the real hold rules and count how often play/pause and mute would fire.

  python tools/record_landmarks.py idle 60 me.jsonl          one minute of ordinary use, landmarks only
  python tools/replay_false_triggers.py me.jsonl             triggers and triggers per minute

Each recorded line carries `t`, seconds since the recording began (lines from before that field are rejected,
because without time a per-minute rate cannot be told). A gap of more than 0.2 s between two lines means
the hand was not seen, which counts as releasing the gesture. The minutes are taken from the recording
length given by `--minutes`, or else the span between the first and last frame with a hand. On an idle
recording every trigger is a false one.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config  # noqa: E402
from gestures import GestureHold, PalmHold, is_fist, is_palm  # noqa: E402
import gesture_data  # noqa: E402

GAP_SECONDS = 0.2


def replay(frames):
    """`frames` is [(t, points)] in time order. Returns {"palm": n, "fist": n, "seconds": span}."""
    palm = PalmHold(config.PALM_HOLD_FRAMES, config.PALM_STILL_MOVE)
    fist = GestureHold(config.MUTE_HOLD_FRAMES)
    counts = {"palm": 0, "fist": 0}
    previous = None
    for t, points in frames:
        if previous is not None and t - previous > GAP_SECONDS:
            palm.update(False)
            fist.update(False)
        fist_seen = is_fist(points, config.FIST_MAX_EXTENSION, config.FIST_MAX_THUMB_REACH)
        palm_seen = not fist_seen and is_palm(points, config.PALM_MIN_EXTENSION, config.PALM_MIN_THUMB_REACH)
        counts["palm"] += bool(palm.update(palm_seen, points if palm_seen else None))
        counts["fist"] += bool(fist.update(fist_seen))
        previous = t
    span = (frames[-1][0] - frames[0][0]) if frames else 0.0
    return {**counts, "seconds": span}


def load(path):
    frames = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if "t" not in row:
                raise SystemExit(f"{path} has lines without a time field `t`; record again with tools/record_landmarks.py")
            points = [[i, x * gesture_data.SCALE, y * gesture_data.SCALE] for i, (x, y) in enumerate(row["lm"])]
            frames.append((row["t"], points))
    return frames


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("file")
    parser.add_argument("--minutes", type=float, help="length of the recording; default is the hand-visible span")
    args = parser.parse_args(argv)
    result = replay(load(args.file))
    minutes = args.minutes if args.minutes else result["seconds"] / 60
    print(f"{args.file}: {minutes:.2f} minutes")
    for name, label in (("palm", "play/pause"), ("fist", "mute")):
        rate = result[name] / minutes if minutes else 0.0
        print(f"  {label}: {result[name]} triggers, {rate:.2f} per minute")


if __name__ == "__main__":
    main(sys.argv[1:])
