import json
import os
import sys

import pytest

import media
from gestures import PalmHold, is_fist, is_palm, palm_features

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import gesture_data  # noqa: E402
import replay_false_triggers  # noqa: E402
from test_gestures import CURLED_TIPS, STRAIGHT_TIPS, THUMB_UP, TUCKED_THUMB, hand  # noqa: E402

THUMB_OUT = (-120, -80)
THUMB_BASE = (-40, -60)  # landmark 2, the thumb knuckle; the shared fixture leaves it at the wrist


def palm_hand(tips, thumb, scale=1.0):
    points = hand(tips, thumb, scale)
    points[2] = [2, THUMB_BASE[0] * scale, THUMB_BASE[1] * scale]
    return points


def open_hand(dx=0.0, scale=1.0):
    return [[i, x + dx, y] for i, x, y in palm_hand(STRAIGHT_TIPS, THUMB_OUT, scale)]


def test_an_open_hand_with_the_thumb_out_is_a_palm():
    assert is_palm(palm_hand(STRAIGHT_TIPS, THUMB_OUT), 1.27, 1.34)


def test_four_fingers_with_the_thumb_tucked_is_not_a_palm():
    assert not is_palm(palm_hand(STRAIGHT_TIPS, TUCKED_THUMB), 1.27, 1.34)


def test_a_fist_and_a_pinch_like_hand_are_not_a_palm():
    assert not is_palm(palm_hand(CURLED_TIPS, THUMB_UP), 1.27, 1.34)
    one_finger_curled = {**STRAIGHT_TIPS, 12: CURLED_TIPS[12]}
    assert not is_palm(palm_hand(one_finger_curled, THUMB_OUT), 1.27, 1.34)


def test_a_hand_is_never_both_a_fist_and_a_palm():
    for tips in (STRAIGHT_TIPS, CURLED_TIPS):
        for thumb in (TUCKED_THUMB, THUMB_OUT, THUMB_UP):
            points = palm_hand(tips, thumb)
            assert not (is_fist(points, 0.77, 0.56) and is_palm(points, 1.27, 1.34))


@pytest.mark.parametrize("scale", [0.25, 2, 4])
def test_palm_features_do_not_depend_on_distance_from_the_camera(scale):
    assert palm_features(palm_hand(STRAIGHT_TIPS, THUMB_OUT, scale)) == pytest.approx(
        palm_features(palm_hand(STRAIGHT_TIPS, THUMB_OUT)))


def test_a_degenerate_hand_has_no_features():
    assert palm_features([[i, 0, 0] for i in range(21)]) is None
    assert not is_palm([[i, 0, 0] for i in range(21)], 1.27, 1.34)


def feed(hold, frames):
    return [hold.update(True, f) for f in frames]


def test_a_still_palm_fires_once_on_the_frame_the_hold_completes():
    hold = PalmHold(frames=5, max_move=0.25)
    fired = feed(hold, [open_hand()] * 8)
    assert fired == [False] * 4 + [True] + [False] * 3


def test_a_moving_palm_does_not_fire_and_restarts_where_it_stops():
    hold = PalmHold(frames=5, max_move=0.25)
    sweeping = [open_hand(dx=60 * i) for i in range(10)]  # 60 px a frame on a hand of size 100
    assert not any(feed(hold, sweeping))
    assert feed(hold, [open_hand(dx=600)] * 5)[-1] is True  # five still frames at the new place


def test_slow_drift_inside_the_limit_still_counts_as_still():
    hold = PalmHold(frames=5, max_move=0.25)
    assert feed(hold, [open_hand(dx=2 * i) for i in range(5)])[-1] is True


def test_the_palm_has_to_be_released_before_it_can_fire_again():
    hold = PalmHold(frames=3, max_move=0.25)
    assert feed(hold, [open_hand()] * 3)[-1] is True
    assert not any(feed(hold, [open_hand()] * 6))
    assert hold.update(False) is False
    assert not hold.forming
    assert feed(hold, [open_hand()] * 3)[-1] is True


def test_forming_is_true_from_the_first_palm_frame():
    hold = PalmHold(frames=5, max_move=0.25)
    assert not hold.forming
    hold.update(True, open_hand())
    assert hold.forming


@pytest.mark.parametrize("frames, move", [(0, 0.25), (5, 0), (5, -1)])
def test_palm_hold_rejects_bad_settings(frames, move):
    with pytest.raises(ValueError):
        PalmHold(frames, move)


def test_toggle_presses_and_releases_the_play_pause_key():
    sent = []
    media.toggle_play_pause(lambda key, flags: sent.append((key, flags)))
    assert sent == [(0xB3, 0), (0xB3, 0x0002)]


def test_scores_accept_a_group_of_labels_as_the_positive_class():
    labels = ["palm", "stop", "stop_inverted", "four", "fist", "no_gesture"]
    predicted = [True, True, False, True, False, False]
    s = gesture_data.scores(predicted, labels, positive=("palm", "stop", "stop_inverted"))
    assert (s["tp"], s["fp"], s["fn"]) == (2, 1, 1)
    assert s["false_positive_rate"] == pytest.approx(1 / 3)
    assert gesture_data.scores([True, False], ["fist", "palm"])["tp"] == 1  # a single label still works


def session_file(tmp_path, spans):
    """A recording of palm frames: spans is a list of (start_second, end_second) at 30 frames a second."""
    path = tmp_path / "session.jsonl"
    lines = []
    for start, end in spans:
        for i in range(int((end - start) * 30)):
            lm = [[x / gesture_data.SCALE, y / gesture_data.SCALE] for _, x, y in open_hand()]
            lines.append(json.dumps({"label": "idle", "t": round(start + i / 30, 3), "lm": lm}))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_replay_counts_one_trigger_per_still_hold_and_a_gap_releases(tmp_path):
    spans = [(0, 2), (5, 7)]  # two separate 2 s holds with the hand out of view between them
    result = replay_false_triggers.replay(replay_false_triggers.load(session_file(tmp_path, spans)))
    assert result["palm"] == 2
    assert result["seconds"] == pytest.approx(7 - 1 / 30, abs=0.1)


def test_replay_ignores_a_palm_shorter_than_the_hold(tmp_path):
    result = replay_false_triggers.replay(replay_false_triggers.load(session_file(tmp_path, [(0, 0.5)])))
    assert result["palm"] == 0


def test_replay_refuses_a_recording_without_time(tmp_path):
    path = tmp_path / "old.jsonl"
    path.write_text(json.dumps({"label": "idle", "lm": [[0, 0]] * 21}) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        replay_false_triggers.load(path)
