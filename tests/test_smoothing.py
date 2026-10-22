import importlib.util
import pathlib

import pytest

from mapping import smooth

spec = importlib.util.spec_from_file_location("measure_jitter", pathlib.Path(__file__).parent.parent / "tools" / "measure_jitter.py")
measure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measure)


def test_first_frame_after_a_hand_appears_is_taken_as_is():
    assert smooth(None, 0.7, 0.4) == 0.7


def test_alpha_one_follows_the_raw_signal():
    assert smooth(0.2, 0.9, 1.0) == pytest.approx(0.9)


def test_alpha_blends_the_new_frame_with_the_previous_value():
    assert smooth(0.2, 1.0, 0.25) == pytest.approx(0.4)


def test_a_constant_signal_stays_constant():
    value = None
    for _ in range(20):
        value = smooth(value, 0.5, 0.3)
    assert value == pytest.approx(0.5)


def test_smoothing_at_least_halves_the_jitter_of_a_held_pinch():
    assert measure.jitter(0.4) < 0.6 * measure.jitter(1.0)


def test_smoothing_costs_only_a_few_frames_of_lag():
    assert measure.lag_frames(0.4) <= 6
