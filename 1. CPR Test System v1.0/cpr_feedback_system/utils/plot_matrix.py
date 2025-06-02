import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

from core.pressure_mat import PressureMat
from core.serial_reader import SerialReader
from core.target_zone import TargetZone
from utils.logger import log_event
from config import config

def setup_plot():
    fig, (ax_main, ax_error, ax_accum) = plt.subplots(3, 1, figsize=(8, 14), gridspec_kw={'height_ratios': [3, 1, 1]})

    mat = ax_main.imshow(np.zeros((config["matrix"]["rows"], config["matrix"]["cols"])), cmap='viridis', vmin=100, vmax=500)
    fig.colorbar(mat, ax=ax_main)
    scatter_cop = ax_main.scatter([], [], color='red', s=100, label="Center of Pressure")
    scatter_target = ax_main.scatter([], [], color='blue', s=100, marker='x', label="Optimum Target")
    ax_main.legend(loc='upper right', bbox_to_anchor=(1.3, 1))
    ax_main.axis('off')

    error_window = 100
    error_data = deque([0] * error_window, maxlen=error_window)
    accum_error_data = deque([0] * error_window, maxlen=error_window)
    time_data = deque(range(-error_window, 0), maxlen=error_window)

    error_line, = ax_error.plot(time_data, error_data, color='red', label="Instantaneous Error")
    ax_error.set_ylim(0, 5)
    ax_error.set_xlim(-error_window, 0)
    ax_error.set_xlabel("Time (frames)")
    ax_error.set_ylabel("Error")
    ax_error.legend()

    accum_line, = ax_accum.plot(time_data, accum_error_data, color='blue', label="Accumulated Error")
    ax_accum.set_xlim(-error_window, 0)
    ax_accum.set_xlabel("Time (frames)")
    ax_accum.set_ylabel("Accumulated Error")
    ax_accum.legend()

    return fig, ax_main, ax_error, ax_accum, mat, scatter_cop, scatter_target, error_data, accum_error_data, time_data, error_line, accum_line

def update(frame, serial_reader, pressure_mat, target_zone, mat, scatter_cop, scatter_target, error_data, accum_error_data, time_data, error_line, accum_line, ax_error, ax_accum, ax_main):
    matrix = serial_reader.read_matrix()

    if matrix is not None:
        processed_matrix, (y_center, x_center), patch_mask = pressure_mat.process(matrix.T)
        mat.set_array(processed_matrix)

        # remove old rectangle(s)
        for artist in ax_main.patches:
            artist.remove()

        # draw patch if available
        if patch_mask is not None:
            ys, xs = np.where(patch_mask)
            if ys.size > 0 and xs.size > 0:
                x_min, x_max = xs.min() - 0.5, xs.max() + 0.5
                y_min, y_max = ys.min() - 0.5, ys.max() + 0.5
                rect = plt.Rectangle((x_min, y_min), x_max - x_min + 1, y_max - y_min + 1,
                                     edgecolor='white', facecolor='none', linewidth=2, linestyle='--')
                ax_main.add_patch(rect)

        y_target, x_target = target_zone.get_target()

        if y_center is not None and x_center is not None:
            scatter_cop.set_offsets([[x_center, y_center]])
            instant_error, accum_error = target_zone.compute_error(y_center, x_center)

            log_event(processed_matrix, (y_center, x_center), instant_error)
            error_data.append(instant_error)
            accum_error_data.append(accum_error)
            time_data.append(time_data[-1] + 1)

            error_line.set_data(time_data, error_data)
            accum_line.set_data(time_data, accum_error_data)
            ax_error.set_xlim(time_data[0], time_data[-1])
            ax_accum.set_xlim(time_data[0], time_data[-1])
            ax_accum.set_ylim(0, max(accum_error_data) * 1.1 if max(accum_error_data) > 0 else 5)
        else:
            scatter_cop.set_offsets(np.empty((0, 2)))

        if y_target is not None and x_target is not None:
            scatter_target.set_offsets([[x_target, y_target]])

    return [mat, scatter_cop, scatter_target, error_line, accum_line]

def plot_matrix():
    serial_reader = SerialReader()
    pressure_mat = PressureMat()
    target_zone = TargetZone()

    fig, ax_main, ax_error, ax_accum, mat, scatter_cop, scatter_target, error_data, accum_error_data, time_data, error_line, accum_line = setup_plot()

    ani = animation.FuncAnimation(
        fig, update, fargs=(serial_reader, pressure_mat, target_zone, mat, scatter_cop, scatter_target, error_data, accum_error_data, time_data, error_line, accum_line, ax_error, ax_accum, ax_main), interval=100
    )
    plt.show()
    serial_reader.close()

if __name__ == "__main__":
    plot_matrix()
