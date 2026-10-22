import importlib

import pytest

import config


@pytest.fixture(autouse=True)
def restore_config():
    yield
    importlib.reload(config)


def test_defaults_are_a_valid_ratio_range():
    assert 0 < config.PINCH_MIN_RATIO < config.PINCH_MAX_RATIO


def test_ratios_can_be_overridden_from_the_environment(monkeypatch):
    monkeypatch.setenv("PINCH_MIN_RATIO", "0.2")
    monkeypatch.setenv("PINCH_MAX_RATIO", "0.9")
    importlib.reload(config)
    assert (config.PINCH_MIN_RATIO, config.PINCH_MAX_RATIO) == (0.2, 0.9)


def test_min_not_below_max_is_rejected(monkeypatch):
    monkeypatch.setenv("PINCH_MIN_RATIO", "1.5")
    with pytest.raises(SystemExit, match="PINCH_MIN_RATIO"):
        importlib.reload(config)


def test_a_non_number_is_rejected(monkeypatch):
    monkeypatch.setenv("PINCH_MAX_RATIO", "wide")
    with pytest.raises(SystemExit, match="PINCH_MAX_RATIO"):
        importlib.reload(config)


@pytest.mark.parametrize("value", ["0", "1.5", "-0.2"])
def test_smoothing_alpha_outside_zero_to_one_is_rejected(monkeypatch, value):
    monkeypatch.setenv("SMOOTHING_ALPHA", value)
    with pytest.raises(SystemExit, match="SMOOTHING_ALPHA"):
        importlib.reload(config)
