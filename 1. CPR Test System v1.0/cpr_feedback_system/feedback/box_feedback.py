import time
import numpy as np
from feedback.feedback_base import FeedbackMechanism
from config import config

class BoxFeedback(FeedbackMechanism):
    def __init__(self):
        super().__init__("box")

    def give_feedback(self, *, cop=None, target=None, error=None, depth=None, timestamp=None):
        tokens = []

        if self.focus in ("depth", "both") and depth is not None:
            if depth < self.dep_min:
                tokens.append("HARDER")
            # Disabled depth feedback for the box
            # elif depth > self.dep_max:
            #     tokens.append("WEAKER")
            #     pass

        if self.focus in ("position", "both") and error is not None and cop and target:
            y_cop, x_cop = cop
            y_t, x_t = target
            dx = x_t - x_cop
            dy = y_t - y_cop
            if abs(dx) > np.sqrt(self.err_thresh):
                tokens.append("RIGHT" if dx > 0 else "LEFT")
            if abs(dy) > np.sqrt(self.err_thresh):
                tokens.append("DOWN" if dy > 0 else "UP")

        cmd = ",".join(tokens) if tokens else "OFF"
        self._send_command(cmd)
