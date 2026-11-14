"""Control the Windows master volume with the thumb-to-index pinch seen by the webcam; a held fist mutes."""
import sys
import time

import cv2
import mediapipe as mp
from pycaw.pycaw import AudioUtilities

import calibration
import config
from background import HotkeyPoller, Indicator, ShowFor, indicator_text, virtual_key
from gestures import GestureHold, is_fist
from lock import VolumeLock
from mapping import THUMB_TIP, INDEX_TIP, pinch_ratio, pinch_to_percent, percent_to_decibel, smooth

ESC = 27
NOTICE_SECONDS = 4  # how long the calibration result stays on screen


class HandTracker:
    """Wraps MediaPipe Hands so each frame is processed once."""

    def __init__(self):
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=config.MAX_HANDS,
            min_detection_confidence=config.DETECTION_CONFIDENCE,
        )
        self.draw = mp.solutions.drawing_utils

    def process(self, frame):
        """Returns the landmarks of the first hand as [id, x, y] pixel points, drawing the hand on `frame`."""
        hand = self.first_hand(frame)
        if hand is None:
            return []
        self.draw.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)
        height, width, _ = frame.shape
        return [[i, int(p.x * width), int(p.y * height)] for i, p in enumerate(hand.landmark)]

    def first_hand(self, frame):
        """MediaPipe's landmarks of the first hand (x and y as fractions of the frame), or None."""
        result = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        return result.multi_hand_landmarks[0] if result.multi_hand_landmarks else None


def open_volume_control():
    """The default speaker's endpoint volume (pycaw 2024+ exposes it as a property)."""
    return AudioUtilities.GetSpeakers().EndpointVolume


def main():
    background = config.BACKGROUND or "--background" in sys.argv[1:]
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open camera {config.CAMERA_INDEX}; set the CAMERA_INDEX environment variable")
    tracker = HandTracker()
    volume = open_volume_control()
    min_db, max_db, _ = volume.GetVolumeRange()
    percent = 0.0
    smoothed = None
    lock = VolumeLock()
    pinch_range = calibration.load(config.CALIBRATION_FILE) or (config.PINCH_MIN_RATIO, config.PINCH_MAX_RATIO)
    session = None
    notice, notice_until = "", 0.0
    fist = GestureHold(config.MUTE_HOLD_FRAMES)
    if background:
        hotkeys = HotkeyPoller({"lock": virtual_key(config.LOCK_KEY), "calibrate": virtual_key(config.CALIBRATE_KEY),
                                "quit": virtual_key(config.QUIT_KEY)})
        indicator, show_for = Indicator(), ShowFor(config.INDICATOR_SECONDS)
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Camera error")
                break
            frame = cv2.flip(frame, 1)
            points = tracker.process(frame)
            if points:
                x1, y1 = points[THUMB_TIP][1:]
                x2, y2 = points[INDEX_TIP][1:]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                ratio = pinch_ratio(points)
                fist_seen = session is None and is_fist(points, config.FIST_MAX_EXTENSION, config.FIST_MAX_THUMB_REACH)
                if fist.update(fist_seen):  # no mute while a calibration sweeps the pinch
                    volume.SetMute(not volume.GetMute(), None)
                if session is not None:
                    session.add(ratio)  # the volume stays put while the user sweeps the pinch
                elif ratio is not None and not fist.forming:
                    # a closing fist also closes the pinch: hold the volume until the hand opens again
                    smoothed = smooth(smoothed, ratio, config.SMOOTHING_ALPHA)
                    live_percent = pinch_to_percent(smoothed, *pinch_range)
                    percent = lock.resolve(live_percent)
                    volume.SetMasterVolumeLevel(percent_to_decibel(percent, min_db, max_db), None)
                for point in ((x1, y1), (x2, y2), (cx, cy)):
                    cv2.circle(frame, point, 15, (255, 0, 255), cv2.FILLED)
                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
                if percent == 0:
                    cv2.circle(frame, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
            else:
                smoothed = None
                fist.update(False)
            now = time.monotonic()
            if session is not None and session.done(now):
                try:
                    pinch_range = calibration.calibrate(session.ratios)
                    calibration.save(config.CALIBRATION_FILE, *pinch_range)
                    notice = f"Calibrated: {pinch_range[0]} to {pinch_range[1]}"
                except calibration.CalibrationError as e:
                    notice = f"Calibration failed: {e}"
                session, smoothed, notice_until = None, None, now + NOTICE_SECONDS
            bar_top = int(400 - percent * 2.5)
            cv2.rectangle(frame, (50, 150), (85, 400), (0, 255, 0), 3)
            cv2.rectangle(frame, (50, bar_top), (85, 400), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, f"{int(percent)}%", (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 250, 0), 3)
            if lock.locked:
                cv2.putText(frame, f"LOCKED ({config.LOCK_KEY} to unlock)", (40, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
            if volume.GetMute():
                cv2.putText(frame, "MUTED (hold a fist to unmute)", (40, 60), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
            if session is not None:
                cv2.putText(frame, f"CALIBRATING {session.remaining(now):.0f}s: open and close the pinch", (40, 130),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 0), 2)
            elif now < notice_until:
                cv2.putText(frame, notice[:60], (40, 130), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 0), 2)
            if background:
                actions = hotkeys.poll()
                if session is not None:
                    text = f"Calibrating {session.remaining(now):.0f}s: open and close the pinch"
                elif now < notice_until:
                    text = notice
                else:
                    text = indicator_text(percent, lock.locked, volume.GetMute())
                if show_for.visible(text, now):
                    indicator.show(text)
                else:
                    indicator.hide()
                indicator.pump()
            else:
                cv2.imshow("Hand", frame)
                key = cv2.waitKey(1)
                actions = [name for name, wanted in (("quit", ESC), ("lock", ord(config.LOCK_KEY)),
                                                     ("calibrate", ord(config.CALIBRATE_KEY))) if key == wanted]
            if "quit" in actions:
                break
            if "lock" in actions:
                lock.toggle(percent)
                smoothed = None
            if "calibrate" in actions and session is None:
                session = calibration.CalibrationSession(time.monotonic(), config.CALIBRATION_SECONDS)
    finally:
        cap.release()
        cv2.destroyAllWindows()
        if background:
            indicator.close()


if __name__ == "__main__":
    main()
