# hands_up.py

import cv2
import mediapipe as mp
import math
import numpy as np

class HandsUpExercise:
    def __init__(self, target_reps=5):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils
        self.counter = 0
        self.stage = None
        self.target_reps = target_reps

    def get_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return 360 - angle if angle > 180.0 else angle

    def run(self):
        cap = cv2.VideoCapture(0)
        cv2.namedWindow("StretchVision", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("StretchVision", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        while cap.isOpened():
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)

            overlay_text = "Raise your arms to shoulder height to begin"

            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark

                rw, lw = lm[self.mp_pose.PoseLandmark.RIGHT_WRIST.value], lm[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
                rs = lm[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

                hands_dist = math.hypot(rw.x - lw.x, rw.y - lw.y)
                hands_level = abs(rw.y - rs.y) < 0.1 and abs(lw.y - rs.y) < 0.1

                if hands_level and hands_dist > 0.4:
                    self.stage = 'open'
                    overlay_text = "Arms open - ready to clap!"
                elif rw.y < rs.y and hands_dist < 0.1 and self.stage == 'open':
                    self.stage = 'clap'
                    self.counter += 1
                    overlay_text = f"Clap #{self.counter}"
                    print(f"Repetition #{self.counter}")

                    if self.counter >= self.target_reps:
                        overlay_text = "Exercise completed successfully!"
                        print(overlay_text)
                        self.counter = 0
                        self.stage = None

                self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            # Show overlay text
            cv2.putText(frame, overlay_text, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)
            cv2.imshow("StretchVision", frame)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
