import json

import pytest

import calibration
from calibration import CalibrationError, CalibrationSession, calibrate


def sweep(low, high, frames=100):
    """A pinch opened and closed evenly between `low` and `high`."""
    return [low + (high - low) * i / (frames - 1) for i in range(frames)]


def test_range_is_the_5th_and_95th_percentile():
    assert calibrate(sweep(0.2, 1.2)) == (0.25, 1.15)


def test_one_wild_frame_does_not_stretch_the_range():
    low, high = calibrate(sweep(0.2, 1.2) + [9.0])
    assert low == pytest.approx(0.25, abs=0.01) and high < 1.2


def test_frames_without_a_hand_are_skipped():
    assert calibrate(sweep(0.2, 1.2) + [None] * 50) == calibrate(sweep(0.2, 1.2))


def test_too_few_frames_are_refused():
    with pytest.raises(CalibrationError, match="frames with a hand"):
        calibrate(sweep(0.2, 1.2, frames=calibration.MIN_FRAMES - 1))


def test_a_pinch_that_barely_moved_is_refused():
    with pytest.raises(CalibrationError, match="barely moved"):
        calibrate(sweep(0.5, 0.6))


def test_session_ends_after_its_seconds():
    s = CalibrationSession(started=100.0, seconds=5)
    assert not s.done(104.9) and s.remaining(103.0) == 2.0
    assert s.done(105.0) and s.remaining(110.0) == 0.0


def test_profile_round_trip(tmp_path):
    path = str(tmp_path / "sub" / "calibration.json")
    calibration.save(path, 0.21, 1.07)
    assert calibration.load(path) == (0.21, 1.07)


def test_missing_profile_is_none(tmp_path):
    assert calibration.load(str(tmp_path / "none.json")) is None


@pytest.mark.parametrize("content", ["not json", json.dumps({"pinch_min_ratio": 1.0}),
                                     json.dumps({"pinch_min_ratio": 1.0, "pinch_max_ratio": 0.5})])
def test_a_broken_profile_is_ignored(tmp_path, content):
    path = tmp_path / "calibration.json"
    path.write_text(content, encoding="utf-8")
    assert calibration.load(str(path)) is None
