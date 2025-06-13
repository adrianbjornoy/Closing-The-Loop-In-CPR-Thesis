"""
Generate box-and-whisker plots of CPR performance metrics (positional error,
compression depth, compression rate) grouped by feedback modality.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configurable mappings ---
_FEEDBACK_MODE_NAMES = {
    "audio": "Voice Commands",
    "belt": "Belt",
    "glove": "Glove",
    "box": "Light Box",
    "screen": "Performance Bar Display",
}

_FEEDBACK_FOCUS_NAMES = {
    "position": "Position",
    "depth": "Depth",
    "both": "Both",
}

_ORDERED_LABELS = [
    "Light Box",
    "Glove",
    "Belt",
    "Voice Commands",
    "Performance Bar Display",
]

_COLOUR_MAP = {
    "Light Box": "green",
    "Glove": "red",
    "Belt": "orange",
    "Voice Commands": "blue",
    "Performance Bar Display": "purple",
}

# --- Load data ---
def load_data(summary_path='final_tests_analysis/global_summary.csv'):
    df = pd.read_csv(summary_path)

    df["feedback_mode_readable"] = (
        df["feedback_mode"].map(_FEEDBACK_MODE_NAMES).fillna(df["feedback_mode"])
    )
    df["feedback_focus_readable"] = (
        df["feedback_focus"].map(_FEEDBACK_FOCUS_NAMES).fillna(df["feedback_focus"])
    )
    return df

# --- Boxplot by feedback mode ---
def plot_box_by_feedback(df, metric, ylabel=None, title=None, save_path=None):
    plt.figure(figsize=(10, 6))

    sns.boxplot(
        data=df[df["session_index"] != 4],
        x="feedback_mode_readable",
        y=metric,
        order=_ORDERED_LABELS,
        palette=_COLOUR_MAP
    )

    plt.title(title or f"{metric.replace('_', ' ').title()} by Feedback Mode", fontsize=14)
    plt.xlabel("Feedback Mode", fontsize=12)
    plt.ylabel(ylabel or metric.replace('_', ' ').title(), fontsize=12)
    plt.grid(True)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300)
    plt.show()

def plot_all_metrics(df, metrics):
    for metric, ylabel, title in metrics:
        plot_box_by_feedback(df, metric, ylabel=ylabel, title=title)

if __name__ == "__main__":
    df_summary = load_data()

    # Define metrics to plot
    metrics_to_plot = [
        ("avg_error", "Positional Error [-]", "Positional Error by Feedback Mode"),
        ("avg_depth", "Compression Depth [mm]", "Compression Depth by Feedback Mode"),
        ("avg_bpm", "Compression Rate [BPM]", "Compression Rate by Feedback Mode")
    ]

    # Plot all
    plot_all_metrics(df_summary, metrics_to_plot)
