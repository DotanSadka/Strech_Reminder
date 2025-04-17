# Placeholder for thumb_up_trigger.py
import cv2
import mediapipe as mp

# thumb_up_trigger.py אחראי לזהות את תנועת ה-"לייק" (אגודל מורם) כדי להתחיל תרגיל


class ThumbUpTrigger:
    def __init__(self, detection_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=detection_confidence)
        self.thumb_tip_id = 4
        self.thumb_mcp_id = 2
        self.triggered = False

    def detect(self):
        cap = cv2.VideoCapture(0)

        # Set up full screen window
        cv2.namedWindow("Thumbs Up Trigger", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Thumbs Up Trigger", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        print("🔍 Looking for a thumbs up to start...")

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                continue

            # Flip horizontally (mirror effect)
            frame = cv2.flip(frame, 1)

            # Convert to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(image)
            
            # Default subtitle text
            overlay_text = "Show a thumbs up to begin"

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    thumb_tip = hand_landmarks.landmark[self.thumb_tip_id]
                    thumb_mcp = hand_landmarks.landmark[self.thumb_mcp_id]

                    # Check if thumb is up and not already triggered
                    if not self.triggered and thumb_tip.y < thumb_mcp.y:
                        print("👍 Thumbs up detected! Starting exercise.")
                        self.triggered = True

            # Update subtitle if detected
            if self.triggered:
                overlay_text = "👍 Exercise started!"


            # Draw subtitle on screen
            cv2.putText(frame, overlay_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1.2, (0, 255, 0), 3, cv2.LINE_AA)

            cv2.imshow("Thumbs Up Trigger", frame)

            if cv2.waitKey(5) & 0xFF == 27:  # ESC to quit
                break

        # cap.release()
        # cv2.destroyAllWindows()
        return False

