import matplotlib.pyplot as plt
import matplotlib.animation as animation
from utils.compression_tracker import CompressionTracker
from core.serial_reader import SerialReader
from utils.logger import log_event

def plot_depth_stream(serial_reader=None):
    """Shows a live bar plot of compression depth with BPM and feedback coloring."""

    if serial_reader is None:
        serial_reader = SerialReader()

    # config
    MAX_DEPTH = 70
    TARGET_MIN = 50
    TARGET_MAX = 60

    # initialize compression tracker
    compression_tracker = CompressionTracker(window_size=3)

    # matplotlib setup
    fig, ax = plt.subplots(figsize=(4, 6))
    bar = ax.bar([0], [0], width=0.5, color='skyblue')
    label = ax.text(0, MAX_DEPTH - 5, "", ha='center', fontsize=14)
    bpm_label = ax.text(0, 5, "", ha='center', fontsize=12)

    ax.set_ylim(0, MAX_DEPTH)
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylabel("Compression Depth (mm)")
    ax.set_title("Current Compression Depth")
    ax.set_xticks([])

    def update(frame):
        compression = serial_reader.read_compression()
        if compression is not None:
            depth, timestamp = compression
            bar[0].set_height(depth)
            label.set_text(f"{depth:.1f} mm")

            # color feedback based on depth
            if TARGET_MIN <= depth <= TARGET_MAX:
                bar[0].set_color("limegreen")
            elif depth < TARGET_MIN:
                bar[0].set_color("orange")
            else:
                bar[0].set_color("red")

            # record compression and calculate bpm
            bpm = compression_tracker.record_compression()
            bpm_text = f"{bpm:.1f} BPM" if bpm else ""
            bpm_label.set_text(bpm_text)

            # log depth and bpm
            log_event(depth=depth, bpm=bpm)

        return list(bar) + [label, bpm_label]

    ani = animation.FuncAnimation(fig, update, interval=100)
    plt.show()
    serial_reader.close()
