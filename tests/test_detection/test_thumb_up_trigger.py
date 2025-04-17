import sys
import os

# Add the root project directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from detection.thumb_up_trigger import ThumbUpTrigger

if __name__ == "__main__":
    trigger = ThumbUpTrigger()
    trigger.detect()