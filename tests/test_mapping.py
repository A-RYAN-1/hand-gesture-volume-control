import pytest

from mapping import pinch_to_percent, percent_to_decibel


@pytest.mark.parametrize("length,expected", [(0, 0), (50, 0), (150, 50), (250, 100), (900, 100)])
def test_pinch_to_percent_is_clamped_and_linear(length, expected):
    assert pinch_to_percent(length, 50, 250) == pytest.approx(expected)


def test_percent_to_decibel_spans_the_device_range():
    assert percent_to_decibel(0, -65.25, 0.0) == pytest.approx(-65.25)
    assert percent_to_decibel(100, -65.25, 0.0) == pytest.approx(0.0)
    assert percent_to_decibel(50, -60.0, 0.0) == pytest.approx(-30.0)
