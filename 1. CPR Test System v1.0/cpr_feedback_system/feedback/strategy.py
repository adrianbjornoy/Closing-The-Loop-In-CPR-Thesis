from config import config
from feedback.audio_feedback import AudioFeedback
from feedback.belt_feedback import BeltFeedback
from feedback.box_feedback import BoxFeedback
from feedback.glove_feedback import GloveFeedback
from feedback.screen_feedback import ScreenFeedback

class FeedbackStrategy:
    @staticmethod
    def create(cfg):
        mode = cfg["feedback"].get("mode", "audio")
        print(f"Feedback mode: {mode}")
        if mode == "audio":
            return AudioFeedback()
        elif mode == "belt":
            return BeltFeedback()
        elif mode == "glove":
            return GloveFeedback()
        elif mode == "box":
            return BoxFeedback()
        elif mode == "screen":
            return ScreenFeedback()
        else:
            raise ValueError(f"unknown feedback mode: {mode}")
