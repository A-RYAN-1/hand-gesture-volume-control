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
# Open-palm (play and pause) thresholds, fitted by tools/fit_palm.py on the HaGRID fit split; see gestures.py.
# Fitted 2026-11-16 (CI run 43904733765).
PALM_MIN_EXTENSION = _number("PALM_MIN_EXTENSION", 1.27)
PALM_MIN_THUMB_EXTENSION = _number("PALM_MIN_THUMB_EXTENSION", 1.34)
# Frames in a row the open palm must be held still, and how far the hand may drift in that time as a fraction
# of the hand size, before play and pause is sent (30 frames is about a second). PALM_PLAY_PAUSE=0 turns it off.
PALM_HOLD_FRAMES = _number("PALM_HOLD_FRAMES", 30, int)
PALM_STILL_MOVE = _number("PALM_STILL_MOVE", 0.25)
PALM_PLAY_PAUSE = (os.environ.get("PALM_PLAY_PAUSE") or "1").lower() not in ("0", "false", "no")
# Frames in a row a fist must be held before it toggles mute (about a third of a second at 30 frames a second).
MUTE_HOLD_FRAMES = _number("MUTE_HOLD_FRAMES", 10, int)
# Background mode: no preview window; Ctrl+Alt plus the lock, calibrate and quit keys work from any window,
# and a small indicator shows the volume for INDICATOR_SECONDS after it changes. Also set by --background.
BACKGROUND = (os.environ.get("BACKGROUND") or "").lower() in ("1", "true", "yes")
QUIT_KEY = os.environ.get("QUIT_KEY") or "q"
INDICATOR_SECONDS = _number("INDICATOR_SECONDS", 2.0)
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
if not (len(QUIT_KEY) == 1 and QUIT_KEY.isalnum() and QUIT_KEY not in (LOCK_KEY, CALIBRATE_KEY)):
    raise SystemExit("QUIT_KEY must be one letter or digit other than LOCK_KEY and CALIBRATE_KEY")
if not (LOCK_KEY.isalnum() and CALIBRATE_KEY.isalnum()):
    raise SystemExit("LOCK_KEY and CALIBRATE_KEY must be a letter or digit so they can be Ctrl+Alt hotkeys")
if INDICATOR_SECONDS <= 0:
    raise SystemExit("INDICATOR_SECONDS must be above 0")
if CALIBRATION_SECONDS <= 0:
    raise SystemExit("CALIBRATION_SECONDS must be above 0")
if FIST_MAX_EXTENSION <= 0 or FIST_MAX_THUMB_REACH <= 0:
    raise SystemExit("FIST_MAX_EXTENSION and FIST_MAX_THUMB_REACH must be above 0")
if MUTE_HOLD_FRAMES < 1:
    raise SystemExit("MUTE_HOLD_FRAMES must be at least 1")
if PALM_MIN_EXTENSION <= 0 or PALM_MIN_THUMB_EXTENSION <= 0:
    raise SystemExit("PALM_MIN_EXTENSION and PALM_MIN_THUMB_EXTENSION must be above 0")
if PALM_HOLD_FRAMES < 1:
    raise SystemExit("PALM_HOLD_FRAMES must be at least 1")
if PALM_STILL_MOVE <= 0:
    raise SystemExit("PALM_STILL_MOVE must be above 0")
