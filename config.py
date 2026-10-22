"""All tunable values, read from environment variables (see .env.example)."""
import os


def _number(name, default, cast=float):
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return cast(raw)
    except ValueError:
        raise SystemExit(f"{name} must be a number, got {raw!r}")


CAMERA_INDEX = _number("CAMERA_INDEX", 0, int)
# Thumb-to-index distance as a fraction of the hand size (wrist to middle-finger knuckle) that maps to
# 0% and 100% volume. A fraction, not pixels, so the distance from the camera does not matter.
PINCH_MIN_RATIO = _number("PINCH_MIN_RATIO", 0.15)
PINCH_MAX_RATIO = _number("PINCH_MAX_RATIO", 1.0)
# Weight of the newest frame in the smoothed pinch ratio, above 0 up to 1 (1 turns smoothing off).
SMOOTHING_ALPHA = _number("SMOOTHING_ALPHA", 0.4)
MAX_HANDS = _number("MAX_HANDS", 1, int)
DETECTION_CONFIDENCE = _number("DETECTION_CONFIDENCE", 0.5)

if PINCH_MIN_RATIO >= PINCH_MAX_RATIO:
    raise SystemExit("PINCH_MIN_RATIO must be smaller than PINCH_MAX_RATIO")
if not 0 < SMOOTHING_ALPHA <= 1:
    raise SystemExit("SMOOTHING_ALPHA must be above 0 and at most 1")
