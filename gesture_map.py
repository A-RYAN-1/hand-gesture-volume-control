"""Which action each recognised gesture triggers, read from a JSON file; free of camera and audio imports.

The file is one object, for example {"fist": "play_pause", "palm": "mute"}. Gestures left out keep their
default, so a file only lists what it changes. Mistakes are refused with a plain message that names the line.
"""
import json

DEFAULT_MAP = {"pinch": "volume", "fist": "mute", "palm": "play_pause"}
# The pinch is a continuous distance, so it can only drive the volume or nothing; fist and palm are held
# gestures that fire once, so they take the one-shot actions.
ALLOWED = {
    "pinch": ("volume", "none"),
    "fist": ("mute", "play_pause", "lock", "none"),
    "palm": ("mute", "play_pause", "lock", "none"),
}


class GestureMapError(ValueError):
    """The map file cannot be used; the message says why and where."""


def _line_of(text, key):
    """1-based line of the first `"key"` in the file text, or None."""
    needle = json.dumps(key)
    for number, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return number
    return None


def _where(text, key):
    line = _line_of(text, key)
    return f"line {line}" if line else "the file"


def parse(text):
    """The full gesture-to-action map for the JSON `text`, defaults filled in. Raises GestureMapError."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise GestureMapError(f"not valid JSON at line {e.lineno}, column {e.colno}: {e.msg}") from None
    if not isinstance(data, dict):
        raise GestureMapError("line 1: the map must be a JSON object such as {\"fist\": \"mute\"}")
    for gesture, action in data.items():
        if gesture not in ALLOWED:
            raise GestureMapError(f"{_where(text, gesture)}: unknown gesture {gesture!r}; use {', '.join(ALLOWED)}")
        if not isinstance(action, str) or action not in ALLOWED[gesture]:
            raise GestureMapError(
                f"{_where(text, gesture)}: {gesture} cannot do {action!r}; use {', '.join(ALLOWED[gesture])}")
    merged = {**DEFAULT_MAP, **data}
    seen = {}
    for gesture, action in merged.items():
        if action in ("none", "volume"):
            continue
        if action in seen:
            raise GestureMapError(
                f"{_where(text, gesture)}: {action} is already used by {seen[action]}; give each action to one gesture")
        seen[action] = gesture
    return merged


def load(path):
    """The map from the file at `path`; the default map when `path` is empty. Raises GestureMapError."""
    if not path:
        return dict(DEFAULT_MAP)
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise GestureMapError(f"cannot read {path}: {e.strerror}") from None
    try:
        return parse(text)
    except GestureMapError as e:
        raise GestureMapError(f"{path}, {e}") from None
