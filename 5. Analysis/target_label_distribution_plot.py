"""
Visualizes the distribution of CPR target positions across sessions,
with grouping by feedback modality.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------- CONFIGURATION ------------------------------------
_FEEDBACK_MAP = {
    "audio": "Voice Commands",
    "belt": "Belt",
    "glove": "Glove",
    "box": "Box",
    "screen": "Performance Bar Display",
}

_FEEDBACK_ORDER = ["Box", "Glove", "Belt", "Voice Commands", "Performance Bar Display"]

_COLOR_PALETTE = {
    "Box": "green",
    "Glove": "red",
    "Belt": "orange",
    "Voice Commands": "blue",
    "Performance Bar Display": "purple",
}


# ---------------------- DATA LOADING -------------------------------------
def load_summary(path="final_tests_analysis/global_summary.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["feedback_mode_readable"] = df["feedback_mode"].map(_FEEDBACK_MAP).fillna("Unknown")
    df = df[df["session_index"] != 4]
    return df


# ---------------------- PLOTTING FUNCTIONS -------------------------------
def plot_target_label_counts(df: pd.DataFrame) -> None:
    plt.figure(figsize=(8, 5))
    sns.countplot(
        data=df,
        x="target_label",
        order=sorted(df["target_label"].dropna().unique())
    )
    plt.title("Frequency of Target Positions Issued")
    plt.xlabel("Target Label")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()


def plot_target_by_feedback(df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    ax = sns.countplot(
        data=df,
        x="target_label",
        hue="feedback_mode_readable",
        order=sorted(df["target_label"].dropna().unique()),
        hue_order=_FEEDBACK_ORDER,
        palette=_COLOR_PALETTE,
    )
    plt.title("Target Positions by Feedback Mode")
    plt.xlabel("Target Label")
    plt.ylabel("Count")

    # Reorder legend to match custom order
    handles, labels = ax.get_legend_handles_labels()
    label_to_handle = dict(zip(labels, handles))
    reordered_handles = [label_to_handle[label] for label in _FEEDBACK_ORDER if label in labels]
    reordered_labels = [label for label in _FEEDBACK_ORDER if label in labels]
    plt.legend(
        reordered_handles,
        reordered_labels,
        title="Feedback Mode",
        bbox_to_anchor=(1.05, 1),
        loc="upper left"
    )

    plt.tight_layout()
    plt.show()


# ---------------------- MAIN --------------------------------------------
if __name__ == "__main__":
    df_summary = load_summary()
    plot_target_label_counts(df_summary)
    plot_target_by_feedback(df_summary)
