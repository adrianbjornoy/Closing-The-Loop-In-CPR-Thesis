import json
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

def load_log(path):
    with open(path, 'r') as f:
        data = [json.loads(line) for line in f if line.strip()]
    df = pd.DataFrame(data)
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s", utc=True).dt.tz_convert("Europe/Oslo")
    df.set_index("datetime", inplace=True)
    return df


def plot_error(df):
    df["error"].plot(title="Error over Time")
    plt.xlabel("Time")
    plt.ylabel("Error")
    plt.grid(True)
    plt.show()


def plot_cop(df):
    df = df.dropna(subset=["cop"])
    df["x_cop"] = df["cop"].apply(lambda v: v[1])
    df["y_cop"] = df["cop"].apply(lambda v: v[0])
    df[["x_cop", "y_cop"]].plot(title="Center of Pressure Over Time")
    plt.xlabel("Time")
    plt.ylabel("COP Coordinate")
    plt.grid(True)
    plt.show()


def animate_matrices(df):
    fig, ax = plt.subplots()
    matrix_shape = np.array(df.iloc[0]["matrix"]).shape
    mat_plot = ax.imshow(np.zeros(matrix_shape), cmap='viridis', vmin=0, vmax=500)
    ax.set_title("Pressure Matrix Animation")

    timestamp_text = fig.text(0.5, 0.02, '', ha='center', va='bottom', fontsize=10)

    def update(i):
        row = df.iloc[i]
        mat_plot.set_array(np.array(row["matrix"]))
        ts = row.name.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        timestamp_text.set_text(f"Timestamp: {ts}")
        return [mat_plot, timestamp_text]

    ani = animation.FuncAnimation(fig, update, frames=len(df), interval=100, blit=False)
    plt.tight_layout()
    plt.show()



def get_latest_log():
    log_dir = "c:/Users/adria/OneDrive/Documents/NTNU/10. Semester/Master/PERSmed/cpr_feedback_system/test_logs"
    if not os.path.exists(log_dir):
        raise FileNotFoundError("No logs directory found.")
    files = [f for f in os.listdir(log_dir) if f.endswith(".ndjson")]
    if not files:
        raise FileNotFoundError("No NDJSON log files found in logs directory.")
    files = sorted(files, key=lambda x: os.path.getctime(os.path.join(log_dir, x)), reverse=True)
    latest_file = files[0]
    return os.path.join(log_dir, latest_file)


def main():
    parser = argparse.ArgumentParser(description="Visualize CPR Feedback Log")
    parser.add_argument("--path", default=None, help="Path to the NDJSON log file")
    parser.add_argument("--plot", choices=["error", "cop", "animate"], default="animate",
                        help="Which plot to generate")
    args = parser.parse_args()

    path = args.path or get_latest_log()
    print(f"Using log file: {path}")

    df = load_log(path)

    if args.plot == "error":
        plot_error(df)
    elif args.plot == "cop":
        plot_cop(df)
    elif args.plot == "animate":
        animate_matrices(df)


if __name__ == "__main__":
    main()

