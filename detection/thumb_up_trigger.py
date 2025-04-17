# Placeholder for thumb_up_trigger.py
import cv2
import mediapipe as mp

# thumb_up_trigger.py אחראי לזהות את תנועת ה-"לייק" (אגודל מורם) כדי להתחיל תרגיל


class ThumbUpTrigger:
    def __init__(self, detection_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils  # To draw landmarks
        self.hands = self.mp_hands.Hands(min_detection_confidence=detection_confidence)
        self.thumb_tip_id = 4
        self.thumb_mcp_id = 2
        self.triggered = False

    def detect(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("❌ Error: Could not open webcam.")
            return False

        print("🔍 Looking for a thumbs up to start (press ESC to quit)...")

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("⚠️ Warning: Skipped a frame.")
                continue

            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(image)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    thumb_tip = hand_landmarks.landmark[self.thumb_tip_id]
                    thumb_mcp = hand_landmarks.landmark[self.thumb_mcp_id]

                    # New logic: other fingers are down
                    fingers_down = all(
                        hand_landmarks.landmark[tip].y > hand_landmarks.landmark[mcp].y
                        for tip, mcp in [(8, 5), (12, 9), (16, 13), (20, 17)]
                    )

                    if thumb_tip.y < thumb_mcp.y and fingers_down:
                        print("👍 Thumbs up detected! Starting exercise.")
                        self.triggered = True
                        cap.release()
                        cv2.destroyAllWindows()
                        return True


                    # Draw landmarks on the hand
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )

            cv2.imshow("Thumbs Up Trigger", frame)

            if cv2.waitKey(5) & 0xFF == 27:  # ESC
                print("👋 Exiting thumbs-up detection.")
                break

        cap.release()
        cv2.destroyAllWindows()
        return False

# #class ThumbUpTrigger:
#     def __init__(self, detection_confidence=0.7):
#         self.mp_hands = mp.solutions.hands
#         self.hands = self.mp_hands.Hands(static_image_mode=False,
#                                          max_num_hands=1,
#                                          min_detection_confidence=detection_confidence)
#         self.mp_draw = mp.solutions.drawing_utils
#         self.triggered = False

#     def is_thumb_up(self, hand_landmarks):
#         thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
#         thumb_ip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP]
#         index_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_MCP]

#         return thumb_tip.y < thumb_ip.y and thumb_tip.y < index_mcp.y

#     def check_trigger(self, frame):
#         """
#         בודק אם יש תנועת 'לייק' ומחזיר True עם פריים מעודכן
#         """
#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = self.hands.process(frame_rgb)
#         triggered = False

#         if results.multi_hand_landmarks:
#             for hand_landmarks in results.multi_hand_landmarks:
#                 # צייר את היד
#                 self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

#                 if self.is_thumb_up(hand_landmarks):
#                     triggered = True
#                     # מצייר את אייקון הלייק
#                     h, w, _ = frame.shape
#                     cv2.putText(frame, "👍", (w//2 - 30, h//2 - 30),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
#                     cv2.putText(frame, "Triggered!", (w//2 - 100, h//2 + 40),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

#         return triggered, frame