import numpy as np
import random
from config import config

class TargetZone:
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TargetZone, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):  # Prevent re-initialization
            self.mode = config["target"].get("mode", "fixed")
            self.random_bounds = (
                tuple(config["target"].get("random_bounds_y", (2, 10))),
                tuple(config["target"].get("random_bounds_x", (2, 10)))
            )
            self.function = None  # Placeholder for function-based target zones
            self.current_target = self._generate_target()
            self.accumulated_error = 0
            self.initialized = True  # Marks instance as initialized

    def _generate_target(self):
        """Generates target based on mode and selected target name."""
        if self.mode == "fixed":
            target_name = config["feedback"].get("target", "t1")
            key = f"fixed_point_{target_name}"
            target_point = config["target"].get(key)
            print(f"Target position: {target_name}, {target_point}")
            if target_point is None:
                raise ValueError(f"Invalid target '{target_name}' specified in config")

            return tuple(target_point)

        elif self.mode == "random":
            y = random.uniform(*self.random_bounds[0])
            x = random.uniform(*self.random_bounds[1])
            return y, x

        elif self.mode == "function" and self.function:
            return self._find_optimum_from_function()

        else:
            raise ValueError("Invalid mode or missing function for target zone")


    def _find_optimum_from_function(self):
        """Finds the best target point based on an optimization function."""
        y_space = np.linspace(0, 11, 50)  # Fine grid search in y-axis
        x_space = np.linspace(0, 11, 50)  # Fine grid search in x-axis
        y_grid, x_grid = np.meshgrid(y_space, x_space)

        values = self.function(y_grid, x_grid)
        max_index = np.unravel_index(np.argmax(values), values.shape)
        return y_space[max_index[0]], x_space[max_index[1]]

    def get_target(self):
        """Returns the current target point."""
        return self.current_target

    def update_target(self):
        """Refreshes the target if in random or function mode."""
        if self.mode in ["random", "function"]:
            self.current_target = self._generate_target()

    def compute_error(self, y_current, x_current):
        """Computes instantaneous and accumulated error."""
        x_target, y_target = self.current_target
        error = np.sqrt((y_target - y_current) ** 2 + (x_target - x_current) ** 2)
        self.accumulated_error += error
        return error, self.accumulated_error

