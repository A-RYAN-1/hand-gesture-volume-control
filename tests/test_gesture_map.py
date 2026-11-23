import pytest

import gesture_map
from gesture_map import GestureMapError, DEFAULT_MAP


def test_empty_object_keeps_the_default_map():
    assert gesture_map.parse("{}") == DEFAULT_MAP


def test_no_path_gives_the_default_map():
    assert gesture_map.load("") == DEFAULT_MAP


def test_swapped_map_changes_both_actions():
    assert gesture_map.parse('{"fist": "play_pause", "palm": "mute"}') == {
        "pinch": "volume", "fist": "play_pause", "palm": "mute"}


def test_gestures_left_out_keep_their_default():
    assert gesture_map.parse('{"palm": "lock"}') == {"pinch": "volume", "fist": "mute", "palm": "lock"}


def test_a_gesture_can_be_switched_off():
    assert gesture_map.parse('{"pinch": "none", "fist": "none"}')["pinch"] == "none"


def test_invalid_json_names_the_line():
    with pytest.raises(GestureMapError, match="line 3"):
        gesture_map.parse('{\n"fist": "mute",\n"palm" "lock"\n}')


def test_non_object_is_refused():
    with pytest.raises(GestureMapError, match="JSON object"):
        gesture_map.parse('["fist"]')


def test_unknown_gesture_names_its_line():
    with pytest.raises(GestureMapError, match=r"line 2: unknown gesture 'wave'"):
        gesture_map.parse('{\n"wave": "mute"\n}')


def test_unknown_action_names_its_line_and_the_choices():
    with pytest.raises(GestureMapError, match=r"line 3: fist cannot do 'shout'; use mute, play_pause, lock, none"):
        gesture_map.parse('{\n"palm": "lock",\n"fist": "shout"\n}')


def test_pinch_cannot_fire_a_one_shot_action():
    with pytest.raises(GestureMapError, match="pinch cannot do 'mute'"):
        gesture_map.parse('{"pinch": "mute"}')


def test_a_non_string_action_is_refused():
    with pytest.raises(GestureMapError, match="palm cannot do 5"):
        gesture_map.parse('{"palm": 5}')


def test_one_action_for_two_gestures_is_refused():
    with pytest.raises(GestureMapError, match="mute is already used by fist"):
        gesture_map.parse('{"palm": "mute"}')


def test_two_gestures_set_to_none_are_allowed():
    assert gesture_map.parse('{"fist": "none", "palm": "none"}')["palm"] == "none"


def test_load_reads_a_file_and_prefixes_errors_with_the_path(tmp_path):
    good = tmp_path / "good.json"
    good.write_text('{"fist": "lock"}', encoding="utf-8")
    assert gesture_map.load(str(good))["fist"] == "lock"
    bad = tmp_path / "bad.json"
    bad.write_text('{"fist": "shout"}', encoding="utf-8")
    with pytest.raises(GestureMapError, match=r"bad\.json, line 1"):
        gesture_map.load(str(bad))


def test_missing_file_is_a_plain_error(tmp_path):
    with pytest.raises(GestureMapError, match="cannot read"):
        gesture_map.load(str(tmp_path / "nope.json"))
