# Placeholder for head_tilt_side.py
import cv2
import mediapipe as mp
import time

class HeadTiltSideExercise:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils

        self.reps = 0
        self.target_reps = 5

        self.state = None  # 'left' or 'right'
        self.cooldown_start = 0
        self.cooldown_secs = 1

    def detect_tilt(self, landmarks):
        left_ear = landmarks[self.mp_pose.PoseLandmark.LEFT_EAR]
        right_ear = landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR]
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

        current_time = time.time()
        if current_time - self.cooldown_start < self.cooldown_secs:
            return None

        # Tilt left: left ear approaches left shoulder
        if abs(left_ear.y - left_shoulder.y) < 0.08:
            if self.state != "left":
                self.state = "left"
                self.cooldown_start = current_time
                return "left"

        # Tilt right: right ear approaches right shoulder
        if abs(right_ear.y - right_shoulder.y) < 0.08:
            if self.state == "left":  # Full cycle completed
                self.reps += 1
                self.state = "right"
                self.cooldown_start = current_time
                return "right"

        return None

    def run(self):
        cap = cv2.VideoCapture(0)

        while cap.isOpened() and self.reps < self.target_reps:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb)

            if results.pose_landmarks:
                direction = self.detect_tilt(results.pose_landmarks.landmark)
                if direction:
                    print(f"Tilt {direction}! Reps: {self.reps}/{self.target_reps}")

                self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            status = f"Reps: {self.reps}/{self.target_reps}"
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("Head Tilt Side", frame)
            if cv2.waitKey(5) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
        self.pose.close()
