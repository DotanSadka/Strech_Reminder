import sys
import os

# Add the root project directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from exercises.hands_up import HandsUpExercise

if __name__ == "__main__":
    exercise = HandsUpExercise()
    exercise.run()
