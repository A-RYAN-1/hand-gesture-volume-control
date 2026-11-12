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
