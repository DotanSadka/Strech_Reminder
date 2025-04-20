import sys
import cv2
import mediapipe as mp
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QStackedWidget, QCheckBox, QSpinBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap


class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.camera_label = QLabel("Live camera feed will appear here")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setFixedSize(640, 480)
        layout.addWidget(self.camera_label)

        self.start_button = QPushButton("Start Stretching")
        layout.addWidget(self.start_button)

        self.status_label = QLabel("Status: Waiting to start...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        self.rep_counter_label = QLabel("Reps: 0/5")
        self.rep_counter_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.rep_counter_label)


        self.setLayout(layout)


class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.timer_label = QLabel("Set reminder interval (minutes)")
        layout.addWidget(self.timer_label)

        self.timer_spinbox = QSpinBox()
        self.timer_spinbox.setRange(1, 120)
        self.timer_spinbox.setValue(30)
        layout.addWidget(self.timer_spinbox)

        self.calendar_checkbox = QCheckBox("Use work calendar to determine stretch times")
        layout.addWidget(self.calendar_checkbox)

        self.exercise_label = QLabel("Select which stretches to enable")
        layout.addWidget(self.exercise_label)

        self.stretch1 = QCheckBox("Hands Up")
        self.stretch2 = QCheckBox("Neck Tilt")
        self.stretch3 = QCheckBox("Torso Twist")
        self.stretch4 = QCheckBox("Look right left")

        

        layout.addWidget(self.stretch1)
        layout.addWidget(self.stretch2)
        layout.addWidget(self.stretch3)
        layout.addWidget(self.stretch4)

        self.setLayout(layout)



class LogsScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.logs_label = QLabel("Progress and activity logs will show here")
        layout.addWidget(self.logs_label)

        self.setLayout(layout)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StretchVision")
        self.setGeometry(100, 100, 800, 600)

        # Screens
        self.home_screen = HomeScreen()
        self.settings_screen = SettingsScreen()
        self.logs_screen = LogsScreen()

        # Stack and navigation
        self.stack = QStackedWidget()
        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.settings_screen)
        self.stack.addWidget(self.logs_screen)

        nav_layout = QHBoxLayout()
        self.home_button = QPushButton("Home")
        self.settings_button = QPushButton("Settings")
        self.logs_button = QPushButton("Logs")
        nav_layout.addWidget(self.home_button)
        nav_layout.addWidget(self.settings_button)
        nav_layout.addWidget(self.logs_button)

        self.home_button.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.settings_button.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.logs_button.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        main_layout = QVBoxLayout()
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.stack)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Camera and MediaPipe
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.hands_up_enabled = False

        # Start button
        self.home_screen.start_button.clicked.connect(self.start_exercise)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        if results.pose_landmarks and self.hands_up_enabled:
            landmarks = results.pose_landmarks.landmark
            left_hand = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_hand = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            head = landmarks[self.mp_pose.PoseLandmark.NOSE]

            # Detect if both hands are above the head (Y is top-down)
            if left_hand.y < head.y and right_hand.y < head.y:
                self.home_screen.status_label.setText("Hands Up Detected!")
            else:
                self.home_screen.status_label.setText("Do the Hands Up stretch...")

        # Show frame
        qt_image = QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image).scaled(
            self.home_screen.camera_label.width(),
            self.home_screen.camera_label.height(),
            Qt.KeepAspectRatio
        )
        self.home_screen.camera_label.setPixmap(pixmap)

    def start_exercise(self):
        self.hands_up_enabled = self.settings_screen.stretch1.isChecked()
        selected_exercises = []
        if self.hands_up_enabled:
            selected_exercises.append("Hands Up")
        if self.settings_screen.stretch2.isChecked():
            selected_exercises.append("Neck Tilt")
        if self.settings_screen.stretch3.isChecked():
            selected_exercises.append("Torso Twist")
        if self.settings_screen.stretch4.isChecked():
            selected_exercises.append("Look_right_left")

        reminder_minutes = self.settings_screen.timer_spinbox.value()
        message = f"Starting: {', '.join(selected_exercises)}\nReminder every {reminder_minutes} minutes"
        self.home_screen.status_label.setText(message)

    def closeEvent(self, event):
        self.cap.release()
        self.pose.close()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
