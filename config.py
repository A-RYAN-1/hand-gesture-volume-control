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
# Key that toggles the volume lock while the preview window is focused: a single character.
LOCK_KEY = os.environ.get("LOCK_KEY") or "l"
# Key that starts a calibration of your own pinch range, and where that range is saved and read at start.
CALIBRATE_KEY = os.environ.get("CALIBRATE_KEY") or "c"
CALIBRATION_SECONDS = _number("CALIBRATION_SECONDS", 5.0)
CALIBRATION_FILE = os.environ.get("CALIBRATION_FILE") or os.path.join(
    os.path.expanduser("~"), ".hand-gesture-volume-control", "calibration.json")
# Fist (mute) thresholds, fitted by tools/fit_fist.py on the HaGRID fit split (2026-11-12); see gestures.py.
FIST_MAX_EXTENSION = _number("FIST_MAX_EXTENSION", 0.77)
FIST_MAX_THUMB_REACH = _number("FIST_MAX_THUMB_REACH", 0.56)
# Frames in a row a fist must be held before it toggles mute (about a third of a second at 30 frames a second).
MUTE_HOLD_FRAMES = _number("MUTE_HOLD_FRAMES", 10, int)
MAX_HANDS = _number("MAX_HANDS", 1, int)
DETECTION_CONFIDENCE = _number("DETECTION_CONFIDENCE", 0.5)

if PINCH_MIN_RATIO >= PINCH_MAX_RATIO:
    raise SystemExit("PINCH_MIN_RATIO must be smaller than PINCH_MAX_RATIO")
if not 0 < SMOOTHING_ALPHA <= 1:
    raise SystemExit("SMOOTHING_ALPHA must be above 0 and at most 1")
if len(LOCK_KEY) != 1:
    raise SystemExit("LOCK_KEY must be a single character")
if len(CALIBRATE_KEY) != 1 or CALIBRATE_KEY == LOCK_KEY:
    raise SystemExit("CALIBRATE_KEY must be a single character other than LOCK_KEY")
if CALIBRATION_SECONDS <= 0:
    raise SystemExit("CALIBRATION_SECONDS must be above 0")
if FIST_MAX_EXTENSION <= 0 or FIST_MAX_THUMB_REACH <= 0:
    raise SystemExit("FIST_MAX_EXTENSION and FIST_MAX_THUMB_REACH must be above 0")
if MUTE_HOLD_FRAMES < 1:
    raise SystemExit("MUTE_HOLD_FRAMES must be at least 1")
