import importlib
import os
import sys

import pytest

import config
from background import VK_CONTROL, VK_MENU, HotkeyPoller, ShowFor, indicator_text, virtual_key

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from startup import script_text  # noqa: E402

LOCK, QUIT = virtual_key("l"), virtual_key("q")


def poller(held):
    """A poller reading the keys currently in the `held` set."""
    return HotkeyPoller({"lock": LOCK, "quit": QUIT}, held.__contains__)


def test_virtual_key_is_the_capital_letter_code():
    assert virtual_key("l") == 0x4C
    assert virtual_key("7") == 0x37


def test_a_key_without_both_modifiers_does_nothing():
    held = {LOCK}
    p = poller(held)
    assert p.poll() == []
    held |= {VK_CONTROL}
    assert p.poll() == []


def test_ctrl_alt_key_fires_once_per_press():
    held = {VK_CONTROL, VK_MENU, LOCK}
    p = poller(held)
    assert p.poll() == ["lock"]
    assert p.poll() == []  # still held: no repeat
    held.discard(LOCK)
    assert p.poll() == []
    held.add(LOCK)
    assert p.poll() == ["lock"]  # released and pressed again


def test_releasing_a_modifier_while_the_key_is_held_re_arms_the_key():
    held = {VK_CONTROL, VK_MENU, QUIT}
    p = poller(held)
    assert p.poll() == ["quit"]
    held.discard(VK_MENU)
    assert p.poll() == []
    held.add(VK_MENU)
    assert p.poll() == ["quit"]


def test_two_hotkeys_in_one_poll_are_both_reported():
    p = poller({VK_CONTROL, VK_MENU, LOCK, QUIT})
    assert p.poll() == ["lock", "quit"]


def test_indicator_text_states_volume_lock_and_mute():
    assert indicator_text(75.4, False, False) == "Volume 75%"
    assert indicator_text(30, True, False) == "Volume 30%  LOCKED"
    assert indicator_text(0, True, True) == "Volume 0%  LOCKED  MUTED"


def test_indicator_shows_for_the_set_time_after_a_change_then_hides():
    show = ShowFor(2.0)
    assert show.visible("Volume 10%", 100.0) is True  # first text counts as a change
    assert show.visible("Volume 10%", 101.9) is True
    assert show.visible("Volume 10%", 102.0) is False
    assert show.visible("Volume 11%", 103.0) is True  # a new text shows it again
    assert show.visible("Volume 11%", 105.1) is False


def test_startup_script_runs_pythonw_hidden_with_the_background_flag():
    text = script_text(r"C:\Python 312\pythonw.exe", r"C:\apps\hand gesture\handdetect.py")
    assert text == (
        'CreateObject("WScript.Shell").Run '
        '"""C:\\Python 312\\pythonw.exe"" ""C:\\apps\\hand gesture\\handdetect.py"" --background", 0, False\r\n'
    )


@pytest.fixture
def fresh_config(monkeypatch):
    yield
    monkeypatch.undo()  # drop the bad value before reloading, or the reload itself would exit
    importlib.reload(config)


def test_background_is_read_from_the_environment(monkeypatch, fresh_config):
    assert config.BACKGROUND is False
    monkeypatch.setenv("BACKGROUND", "1")
    importlib.reload(config)
    assert config.BACKGROUND is True


@pytest.mark.parametrize("name, value", [("QUIT_KEY", "l"), ("QUIT_KEY", "qq"), ("QUIT_KEY", "!"),
                                         ("LOCK_KEY", "!"), ("INDICATOR_SECONDS", "0")])
def test_bad_background_settings_are_rejected(monkeypatch, fresh_config, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(SystemExit):
        importlib.reload(config)
