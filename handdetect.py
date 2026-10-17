"""Control the Windows master volume with the thumb-to-index pinch seen by the webcam."""
import math

import cv2
import mediapipe as mp
from pycaw.pycaw import AudioUtilities

import config
from mapping import pinch_to_percent, percent_to_decibel

THUMB_TIP, INDEX_TIP = 4, 8
ESC = 27


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
        result = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not result.multi_hand_landmarks:
            return []
        hand = result.multi_hand_landmarks[0]
        self.draw.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)
        height, width, _ = frame.shape
        return [[i, int(p.x * width), int(p.y * height)] for i, p in enumerate(hand.landmark)]


def open_volume_control():
    """The default speaker's endpoint volume (pycaw 2024+ exposes it as a property)."""
    return AudioUtilities.GetSpeakers().EndpointVolume


def main():
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open camera {config.CAMERA_INDEX}; set the CAMERA_INDEX environment variable")
    tracker = HandTracker()
    volume = open_volume_control()
    min_db, max_db, _ = volume.GetVolumeRange()
    percent = 0.0
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
                length = math.hypot(x2 - x1, y2 - y1)
                percent = pinch_to_percent(length, config.PINCH_MIN_PX, config.PINCH_MAX_PX)
                volume.SetMasterVolumeLevel(percent_to_decibel(percent, min_db, max_db), None)
                for point in ((x1, y1), (x2, y2), (cx, cy)):
                    cv2.circle(frame, point, 15, (255, 0, 255), cv2.FILLED)
                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
                if length < config.PINCH_MIN_PX:
                    cv2.circle(frame, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
            bar_top = int(400 - percent * 2.5)
            cv2.rectangle(frame, (50, 150), (85, 400), (0, 255, 0), 3)
            cv2.rectangle(frame, (50, bar_top), (85, 400), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, f"{int(percent)}%", (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 250, 0), 3)
            cv2.imshow("Hand", frame)
            if cv2.waitKey(1) == ESC:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
