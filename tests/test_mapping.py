import pytest

from mapping import pinch_ratio, pinch_to_percent, percent_to_decibel

LOW, HIGH = 0.15, 1.0


def hand(scale, wrist=(100, 400), middle_mcp=(100, 300), thumb=(60, 250), index=(140, 250), offset=(0, 0)):
    """21 [id, x, y] landmarks; only 0, 4, 8 and 9 matter, the rest are filler. Scaled about the origin."""
    pts = {0: wrist, 4: thumb, 8: index, 9: middle_mcp}
    return [[i, pts.get(i, (0, 0))[0] * scale + offset[0], pts.get(i, (0, 0))[1] * scale + offset[1]] for i in range(21)]


@pytest.mark.parametrize("ratio,expected", [(0, 0), (LOW, 0), (0.575, 50), (HIGH, 100), (3.0, 100)])
def test_pinch_to_percent_is_clamped_and_linear(ratio, expected):
    assert pinch_to_percent(ratio, LOW, HIGH) == pytest.approx(expected)


def test_percent_to_decibel_spans_the_device_range():
    assert percent_to_decibel(0, -65.25, 0.0) == pytest.approx(-65.25)
    assert percent_to_decibel(100, -65.25, 0.0) == pytest.approx(0.0)
    assert percent_to_decibel(50, -60.0, 0.0) == pytest.approx(-30.0)


def test_pinch_ratio_is_pinch_over_hand_size():
    # thumb to index is 80 px, wrist to middle knuckle is 100 px
    assert pinch_ratio(hand(1)) == pytest.approx(0.8)


@pytest.mark.parametrize("scale", [0.25, 0.5, 2, 4])
def test_same_pose_at_another_distance_gives_the_same_volume(scale):
    base = pinch_to_percent(pinch_ratio(hand(1)), LOW, HIGH)
    scaled = pinch_to_percent(pinch_ratio(hand(scale, offset=(37, -12))), LOW, HIGH)
    assert scaled == pytest.approx(base)


def test_a_wider_pinch_gives_a_higher_volume():
    closed = pinch_to_percent(pinch_ratio(hand(1, thumb=(95, 250), index=(105, 250))), LOW, HIGH)
    open_ = pinch_to_percent(pinch_ratio(hand(1, thumb=(30, 250), index=(170, 250))), LOW, HIGH)
    assert closed < pinch_to_percent(pinch_ratio(hand(1)), LOW, HIGH) < open_


def test_zero_hand_size_has_no_ratio():
    assert pinch_ratio(hand(1, wrist=(100, 300), middle_mcp=(100, 300))) is None
