import numpy as np
from config import config

PRESSURE_THRESHOLD = config["matrix"].get("pressure_threshold", 150)
SMOOTHING_ALPHA = config["matrix"].get("smoothing_alpha", 0.2)
HOLD_COP_TIME = config["matrix"].get("hold_cop_time", 5)

class PressureMat:
    def __init__(self):
        self.previous_matrix = None
        self.last_cop = (None, None)
        self.cop_hold_counter = 0

    def process(self, matrix):
        matrix = self.apply_threshold(matrix)
        matrix = self.apply_smoothing(matrix)
        patch_mask = self.detect_patch(matrix)
        center_of_pressure = self.compute_center_of_pressure(matrix)
        return matrix, center_of_pressure, patch_mask

    def apply_threshold(self, matrix):
        return np.where(matrix > PRESSURE_THRESHOLD, matrix, 0)

    def apply_smoothing(self, matrix):
        if self.previous_matrix is None:
            self.previous_matrix = matrix
        smoothed = SMOOTHING_ALPHA * matrix + (1 - SMOOTHING_ALPHA) * self.previous_matrix
        self.previous_matrix = smoothed
        return smoothed

    def detect_patch(self, matrix):
        h, w = matrix.shape
        best_score = -np.inf
        best_mask = None

        for x in range(w):
            for y in range(h - 3):
                mask_1 = np.zeros_like(matrix, dtype=bool)
                mask_1[y:y+4, x] = True
                score_1 = np.sum(matrix * mask_1)
                if score_1 > best_score:
                    best_score = score_1
                    best_mask = mask_1.copy()

                if x < w - 1:
                    mask_2 = np.zeros_like(matrix, dtype=bool)
                    mask_2[y:y+4, x:x+2] = True
                    score_2 = np.sum(matrix * mask_2)
                    if score_2 > best_score:
                        best_score = score_2
                        best_mask = mask_2.copy()

        return best_mask if best_mask is not None else np.zeros_like(matrix, dtype=bool)

    def compute_center_of_pressure(self, matrix):
        total_pressure = np.sum(matrix)
        if total_pressure == 0:
            if self.cop_hold_counter < HOLD_COP_TIME:
                self.cop_hold_counter += 1
                return self.last_cop
            else:
                return None, None

        x_coords, y_coords = np.meshgrid(range(matrix.shape[1]), range(matrix.shape[0]))
        x_center = np.sum(matrix * x_coords) / total_pressure
        y_center = np.sum(matrix * y_coords) / total_pressure

        self.last_cop = (y_center, x_center)
        self.cop_hold_counter = 0
        return y_center, x_center
