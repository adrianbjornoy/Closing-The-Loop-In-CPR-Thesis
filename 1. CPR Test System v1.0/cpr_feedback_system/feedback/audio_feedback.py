import time
import pygame
from pathlib import Path
from feedback.feedback_base import FeedbackMechanism
from config import config

class AudioFeedback(FeedbackMechanism):
    def __init__(self):
        pygame.mixer.init()
        sd = Path(config["feedback"]["audio"]["sound_directory"]).resolve()
        cf = config["feedback"]["audio"]

        pygame.mixer.set_num_channels(4)
        self.ch_pos = pygame.mixer.Channel(cf["channel_map"]["position"])
        self.ch_dep = pygame.mixer.Channel(cf["channel_map"]["depth"])

        self.sounds = {name: pygame.mixer.Sound(str((sd / fname).resolve())) for name, fname in cf["sounds"].items()}
        for s in self.sounds.values():
            s.set_volume(cf["volume"])

        self.last_pos = 0
        self.last_dep = 0
        self.cooldown = cf["cooldown"]
        self.err_thresh = cf["error_threshold"]
        self.focus = config["feedback"]["focus"]
        self.dep_min, self.dep_max = self.get_depth_range_for_target()
        self.queued_position_cue = None

    def give_feedback(self, *, cop=None, target=None, error=None, depth=None, timestamp=None):
        now = time.time()

        # check if error is below threshold — no position feedback if so
        position_allowed = (self.focus in ("position", "both")
                            and cop and target
                            and error is not None
                            and abs(error) > self.err_thresh)

        do_depth = self.focus in ("depth", "both") and depth is not None and (depth < self.dep_min or depth > self.dep_max)
        # depth first
        if do_depth and now - self.last_dep >= self.cooldown:
            direc = "harder" if depth < self.dep_min else "weaker"
            if not self.ch_dep.get_busy():
                self.ch_dep.play(self.sounds[direc])
                self.last_dep = now
            return  # skip position if depth fires

        # handle queued position cue if depth just finished
        if self.queued_position_cue and not self.ch_dep.get_busy():
            if not self.ch_pos.get_busy():
                self.ch_pos.play(self.sounds[self.queued_position_cue])
                self.last_pos = now
                self.queued_position_cue = None
            return

        # position logic only if error is outside threshold
        if position_allowed and now - self.last_pos >= self.cooldown:
            y_cop, x_cop = cop
            y_t, x_t = target
            dx = x_t - x_cop  # left/right
            dy = y_t - y_cop  # up/down

            if abs(dx) >= abs(dy):
                cue = "down" if dx > 0 else "up"
            else:
                cue = "right" if dy < 0 else "left"

            if self.ch_dep.get_busy():
                self.queued_position_cue = cue
            elif not self.ch_pos.get_busy():
                self.ch_pos.play(self.sounds[cue])
                self.last_pos = now
