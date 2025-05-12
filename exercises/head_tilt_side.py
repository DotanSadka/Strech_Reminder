import cv2
import mediapipe as mp

class HeadTiltSideExercise:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.reps_left = 0
        self.reps_right = 0
        self.target_reps = 5
        self.current_side = None  # 'left', 'right', or None

    def detect_head_tilt(self, landmarks):
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE]
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

        # Shoulder width
        shoulder_width = abs(left_shoulder.x - right_shoulder.x)

        # Define horizontal bounds for left/right tilt
        left_threshold = left_shoulder.x - 0.15 * shoulder_width
        right_threshold = right_shoulder.x + 0.15 * shoulder_width

        # Tilt left
        if nose.x < left_threshold:
            if self.current_side != "left":
                self.current_side = "left"
                self.reps_left += 1
        # Tilt right
        elif nose.x > right_threshold:
            if self.current_side != "right":
                self.current_side = "right"
                self.reps_right += 1
        else:
            self.current_side = None  # Reset when centered

    def get_status_message(self):
        return f"Left: {self.reps_left}/{self.target_reps} | Right: {self.reps_right}/{self.target_reps}"

    def run(self):
        cap = cv2.VideoCapture(0)
        pose = self.mp_pose.Pose()

        while cap.isOpened() and (self.reps_left < self.target_reps or self.reps_right < self.target_reps):
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:
                self.detect_head_tilt(results.pose_landmarks.landmark)

                # Draw landmarks
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            cv2.putText(frame, self.get_status_message(), (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2, cv2.LINE_AA)

            cv2.imshow("Head Tilt Side Exercise", frame)
            if cv2.waitKey(5) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
        pose.close()
