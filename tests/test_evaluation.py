"""Regression floor for the fist classifier on the held-out HaGRID split.

Measured 2026-11-12 with the thresholds in config.py: precision 0.934, recall 0.785, idle (`no_gesture`)
hands taken for a fist 0.004. The floors sit a little below, so a change that makes the classifier
clearly worse fails CI. They are not targets to tune towards: the split is held out.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import gesture_data  # noqa: E402
from evaluate_gestures import evaluate  # noqa: E402


def test_fist_classifier_keeps_its_held_out_numbers():
    r = evaluate(gesture_data.load("test"))
    assert r["precision"] >= 0.90
    assert r["recall"] >= 0.75
    assert r["taken_for_fist"]["no_gesture"] <= 0.02


def test_palm_classifier_keeps_its_held_out_numbers():
    """Measured 2026-11-16 (CI run 43905261892) with the thresholds fitted on the fit split: precision 0.644,
    recall 0.751; idle (`no_gesture`) hands 0.267 and `four` 0.260 taken for an open palm. A single photo of
    a relaxed open hand looks like a palm, which is why play/pause also needs the hand held still."""
    from evaluate_gestures import evaluate_palm

    r = evaluate_palm(gesture_data.load("test"))
    assert r["precision"] >= 0.58
    assert r["recall"] >= 0.68
    assert r["taken_for_palm"]["no_gesture"] <= 0.32
