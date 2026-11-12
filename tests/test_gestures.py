import pytest

from gestures import GestureHold, fist_features, is_fist

# A hand drawn upright: wrist at the bottom, hand size (wrist to middle knuckle, landmark 9) of 100.
WRIST = (0, 0)
PIPS = {6: (-30, -130), 10: (0, -140), 14: (25, -130), 18: (45, -115)}
STRAIGHT_TIPS = {8: (-35, -190), 12: (0, -200), 16: (30, -185), 20: (55, -160)}
CURLED_TIPS = {8: (-25, -80), 12: (0, -85), 16: (20, -80), 20: (35, -70)}
TUCKED_THUMB, THUMB_UP = (-20, -90), (-120, -160)


def hand(tips, thumb, scale=1.0):
    pts = {0: WRIST, 4: thumb, 9: (0, -100), **PIPS, **tips}
    return [[i, pts.get(i, (0, 0))[0] * scale, pts.get(i, (0, 0))[1] * scale] for i in range(21)]


def test_a_curled_hand_with_the_thumb_tucked_is_a_fist():
    assert is_fist(hand(CURLED_TIPS, TUCKED_THUMB), 1.0, 0.8)


def test_an_open_hand_is_not_a_fist():
    assert not is_fist(hand(STRAIGHT_TIPS, TUCKED_THUMB), 1.0, 0.8)


def test_a_thumbs_up_is_not_a_fist():
    assert not is_fist(hand(CURLED_TIPS, THUMB_UP), 1.0, 0.8)


def test_one_straight_finger_is_enough_to_say_no():
    tips = {**CURLED_TIPS, 8: STRAIGHT_TIPS[8]}
    assert not is_fist(hand(tips, TUCKED_THUMB), 1.0, 0.8)


@pytest.mark.parametrize("scale", [0.25, 0.5, 2, 4])
def test_features_do_not_depend_on_distance_from_the_camera(scale):
    base = fist_features(hand(CURLED_TIPS, TUCKED_THUMB))
    assert fist_features(hand(CURLED_TIPS, TUCKED_THUMB, scale)) == pytest.approx(base)


def test_a_degenerate_hand_is_never_a_fist():
    flat = [[i, 5, 5] for i in range(21)]
    assert fist_features(flat) is None
    assert not is_fist(flat, 10, 10)


def test_hold_acts_once_after_the_set_number_of_frames():
    hold = GestureHold(3)
    assert [hold.update(True) for _ in range(6)] == [False, False, True, False, False, False]


def test_hold_needs_a_release_before_acting_again():
    hold = GestureHold(2)
    seen = [hold.update(a) for a in (True, True, True, False, True, True)]
    assert seen == [False, True, False, False, False, True]


def test_a_gap_restarts_the_count():
    hold = GestureHold(3)
    assert [hold.update(a) for a in (True, True, False, True, True)] == [False] * 5
    assert hold.forming


def test_hold_reports_forming_until_released():
    hold = GestureHold(5)
    assert not hold.forming
    hold.update(True)
    assert hold.forming
    hold.update(False)
    assert not hold.forming


def test_hold_rejects_zero_frames():
    with pytest.raises(ValueError):
        GestureHold(0)
