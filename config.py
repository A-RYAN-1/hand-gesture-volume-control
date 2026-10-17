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
# Thumb-to-index distance in pixels that maps to 0% and 100% volume.
PINCH_MIN_PX = _number("PINCH_MIN_PX", 50.0)
PINCH_MAX_PX = _number("PINCH_MAX_PX", 250.0)
MAX_HANDS = _number("MAX_HANDS", 1, int)
DETECTION_CONFIDENCE = _number("DETECTION_CONFIDENCE", 0.5)

if PINCH_MIN_PX >= PINCH_MAX_PX:
    raise SystemExit("PINCH_MIN_PX must be smaller than PINCH_MAX_PX")
