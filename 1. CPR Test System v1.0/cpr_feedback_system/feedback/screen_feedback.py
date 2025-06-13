import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from feedback.feedback_base import FeedbackMechanism
from config import config

class ScreenFeedback(FeedbackMechanism):
    def __init__(self):
        self.focus = config["feedback"].get("focus", "position")
        self.dep_min, self.dep_max = self.get_depth_range_for_target()
        scfg = config["feedback"].get("screen", {})
        self.pos_weight = scfg.get("position_weight", 1.0)
        self.dep_weight = scfg.get("depth_weight", 1.0)
        self._queue = deque()
        self.best_score = 0

        # compute theoretical max score based on weights and mode
        if self.focus == "position":
            self.max_score = self.pos_weight * 8
        elif self.focus == "depth":
            self.max_score = self.dep_weight * 8
        elif self.focus == "both":
            total_weight = self.pos_weight + self.dep_weight
            self.max_score = (self.pos_weight * 8 + self.dep_weight * 8) / total_weight
        else:
            self.max_score = 8  # fallback

        # visualization setup
        self.fig, self.ax = plt.subplots(figsize=(4, 6))
        self.bar = self.ax.bar([0], [0], width=0.5, color='skyblue')
        self.best_score = 0
        self.best_line = self.ax.plot([-0.25, 0.25], [0, 0], 'k--')[0]
        self.best_text = self.ax.text(0.3, 0.2, "", ha="left", va="bottom", fontsize=14)
        self.ax.set_ylim(0, self.max_score)
        self.ax.set_xlim(-0.25, 0.25)
        self.ax.set_xticks([])
        self.ax.set_ylabel("Blood Flow")
        self.ax.set_title("Live Feedback Bar (Higher is Better)")
        self.ax.legend()

        self.ani = animation.FuncAnimation(self.fig, self._update_plot, interval=100)

    def set_stop_event(self, stop_event):
        self.stop_event = stop_event

    def _score(self, error=None, depth=None):
        pos_score = max(0, 8 - error) if error is not None else 0
        if depth is not None and self.dep_min < depth < self.dep_max:
            depth_score = 8
        elif depth is not None:
            delta = min(abs(depth - self.dep_min), abs(depth - self.dep_max))
            depth_score = max(0, 8 - delta * 0.5)
        else:
            depth_score = 0

        if self.focus == "position":
            return self.pos_weight * pos_score
        elif self.focus == "depth":
            return self.dep_weight * depth_score
        elif self.focus == "both":
            total_weight = self.pos_weight + self.dep_weight
            combined = (self.pos_weight * pos_score + self.dep_weight * depth_score) / total_weight if total_weight > 0 else 0
            return combined
        else:
            return 0

    def _update_plot(self, frame):
        if self._queue:
            error, depth = self._queue.popleft()
            score = self._score(error=error, depth=depth)
            self.bar[0].set_height(score)

            if score > self.best_score:
                self.best_score = score
                self.best_line.set_ydata([score, score])
                self.best_text.set_position((0, score))
                self.best_text.set_text(f"Best so far: {score:.2f}")

        return [self.bar[0], self.best_line, self.best_text]


    def give_feedback(self, *, cop=None, target=None, error=None, depth=None, timestamp=None):
        self._queue.append((error, depth))

    def start(self):
        plt.show()
        if hasattr(self, 'stop_event') and self.stop_event:
            self.stop_event.set()