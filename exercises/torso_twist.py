import cv2
import mediapipe as mp
import time

class TorsoTwistExercise:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils

        self.reps_right = 0
        self.reps_left = 0
        self.target_reps = 5
        self.last_twist = None
        self.cooldown_start = 0
        self.cooldown_secs = 1  # Prevent double counting within 1 second

    def detect_twist(self, landmarks):
        left_sh = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_sh = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

        diff_z = left_sh.z - right_sh.z

        current_time = time.time()
        if current_time - self.cooldown_start < self.cooldown_secs:
            return None  # In cooldown, don't count

        if diff_z > 0.15:  # Left is back -> twisting RIGHT
            if self.last_twist != "right":
                self.reps_right += 1
                self.last_twist = "right"
                self.cooldown_start = current_time
                return "right"
        elif diff_z < -0.15:  # Right is back -> twisting LEFT
            if self.last_twist != "left":
                self.reps_left += 1
                self.last_twist = "left"
                self.cooldown_start = current_time
                return "left"
        return None

    def run(self):
        cap = cv2.VideoCapture(0)

        while cap.isOpened() and (self.reps_right < self.target_reps or self.reps_left < self.target_reps):
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb)

            if results.pose_landmarks:
                direction = self.detect_twist(results.pose_landmarks.landmark)
                if direction:
                    print(f"Twist {direction}! Right: {self.reps_right}/5, Left: {self.reps_left}/5")

                self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            status = f"Right: {self.reps_right}/5 | Left: {self.reps_left}/5"
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("Torso Twist Test", frame)
            if cv2.waitKey(5) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
        self.pose.close()
