"""
This script visualizes CPR performance metrics (positional error, compression depth, and compression rate)
grouped by the issued target label using boxplots. It uses participant summary data from the final tests
and excludes the no-feedback session (session_index == 4). The goal is to analyze how different target positions
affect performance.
"""


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load summary data
df = pd.read_csv("final_tests_analysis/global_summary.csv")

# Exclude no-feedback session (session_index 4)
df = df[df["session_index"] != 4]

# Function to generate boxplot for a given metric by target label
def plot_metric_by_target(metric, ylabel=None, title=None):
    plt.figure(figsize=(8, 5))
    sns.boxplot(
        data=df,
        x="target_label",
        y=metric,
        order=sorted(df["target_label"].dropna().unique())
    )
    plt.title(title or f"{metric.replace('_', ' ').title()} by Target Label")
    plt.xlabel("Target Label")
    plt.ylabel(ylabel or metric.replace("_", " ").title())
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Plot each metric
plot_metric_by_target("avg_error", ylabel="Position Error [-]", title="Positional Error by Target")
plot_metric_by_target("avg_depth", ylabel="Compression Depth [mm]", title="Compression Depth by Target")
plot_metric_by_target("avg_bpm", ylabel="Compression Rate [BPM]", title="Compression Rate by Target")
