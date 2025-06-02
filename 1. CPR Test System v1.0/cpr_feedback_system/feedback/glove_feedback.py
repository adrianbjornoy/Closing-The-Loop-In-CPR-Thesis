from feedback.feedback_base import FeedbackMechanism

class GloveFeedback(FeedbackMechanism):
    def __init__(self):
        super().__init__("glove")
        print(f"Depth target range is [{self.dep_min}, {self.dep_max}]")

    def give_feedback(self, *, cop=None, target=None, error=None, depth=None, timestamp=None):
        tokens = []

        # Disabled depth feedback for the glove
        # if self.focus in ("depth", "both") and depth is not None:
        #     if depth < self.dep_min:
        #         tokens.append("HARDER")

        if self.focus in ("position", "both") and error is not None and cop and target:
            if abs(error) > self.err_thresh:
                y_cop, x_cop = cop
                y_t, x_t = target
                dx = x_t - x_cop
                dy = y_t - y_cop
                if abs(dx) > self.err_thresh:
                    tokens.append("RIGHT" if dx > 0 else "LEFT")
                if abs(dy) > self.err_thresh:
                    tokens.append("DOWN" if dy > 0 else "UP")

        cmd = ",".join(tokens) if tokens else "OFF"
        self._send_command(cmd)
