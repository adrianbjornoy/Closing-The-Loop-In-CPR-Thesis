"""
This script visualizes Likert-scale responses for a selected CPR feedback prototype.
It loads labeled summary data from a JSON file, applies directional alignment for 
negatively worded questions, and generates a diverging horizontal bar chart 
representing response distribution percentages for each question.

The chart helps compare user perceptions across Likert categories, including:
'Strongly Disagree', 'Disagree', 'Neutral', 'Agree', and 'Strongly Agree'.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === Configuration ===
prototype_index = 4  # Select prototype by index from JSON file
json_path = "final_tests_analysis/likert_summary_labeled.json"
negatively_framed = ["Q2", "Q3", "Q4", "Q6"] # Inverts the scale of selected questions

# Color scheme and response labels
colors = ["#d73027", "#fdae61", "#f0f0f0", "#abd9e9", "#4575b4"]
labels = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
neg_ratings = [1, 2]
neutral_rating = 3
pos_ratings = [4, 5]

# === Load JSON Data ===
with open(json_path) as f:
    data = json.load(f)

statement_map = data["statements"]
prototypes = list(data["prototypes"].keys())
prototype = prototypes[prototype_index]
responses = data["prototypes"][prototype]

# === Parse and Align Data ===
records = []
for statement_id, rating_counts in responses.items():
    question = f"Q{list(statement_map.keys()).index(statement_id)+1}"
    for rating_str, count in rating_counts.items():
        records.append({
            "prototype": prototype,
            "question": question,
            "rating": int(rating_str),
            "count": count
        })

df = pd.DataFrame(records)
df["aligned_rating"] = df.apply(
    lambda row: 6 - row["rating"] if row["question"] in negatively_framed else row["rating"],
    axis=1
)

# Prepare data
pivot = df.pivot_table(index="question", columns="aligned_rating", values="count", aggfunc='sum', fill_value=0)
pivot = pivot[sorted(pivot.columns)]
pivot_prop = pivot.div(pivot.sum(axis=1), axis=0)

questions = pivot_prop.index.tolist()
ratings = pivot_prop.columns.tolist()

# === Plotting ===
fig, ax = plt.subplots(figsize=(10, len(questions) * 1.2))
y_pos = np.arange(len(questions))

# Neutral bars
neutral_vals = [pivot_prop[neutral_rating].get(q, 0) * 100 for q in questions]
neutral_left = [-val / 2 for val in neutral_vals]
neutral_width = neutral_vals
ax.barh(y_pos, neutral_width, left=neutral_left,
        color=colors[neutral_rating - 1], edgecolor='white', label=labels[neutral_rating - 1])

# Negative bars
lefts = [-neutral_vals[i] / 2 for i in range(len(questions))]
for rating in reversed(neg_ratings):
    vals = [-pivot_prop[rating].get(q, 0) * 100 for q in questions]
    ax.barh(y_pos, vals, left=lefts, color=colors[rating - 1], edgecolor='white', label=labels[rating - 1])
    lefts = [lefts[j] + vals[j] for j in range(len(vals))]

# Positive bars
lefts = [neutral_vals[i] / 2 for i in range(len(questions))]
for rating in pos_ratings:
    vals = [pivot_prop[rating].get(q, 0) * 100 for q in questions]
    ax.barh(y_pos, vals, left=lefts, color=colors[rating - 1], edgecolor='white', label=labels[rating - 1])
    lefts = [lefts[j] + vals[j] for j in range(len(vals))]

# Add percentage labels to bars
ax.axvline(0, color='gray', linewidth=1)

for i, q in enumerate(questions):
    total_left = -neutral_vals[i] / 2
    for rating in reversed(neg_ratings):
        val = pivot_prop[rating].get(q, 0) * 100
        if val > 5:
            ax.text(total_left - val / 2, i, f"{int(val)}%", ha='center', va='center', fontsize=9)
        total_left -= val

    if neutral_vals[i] > 5:
        ax.text(0, i, f"{int(neutral_vals[i])}%", ha='center', va='center', fontsize=9)

    total_right = neutral_vals[i] / 2
    for rating in pos_ratings:
        val = pivot_prop[rating].get(q, 0) * 100
        if val > 5:
            ax.text(total_right + val / 2, i, f"{int(val)}%", ha='center', va='center', fontsize=9)
        total_right += val

# Sort legend in correct order
handles, legend_labels = ax.get_legend_handles_labels()
ordered_labels = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
ordered_handles = [handles[legend_labels.index(label)] for label in ordered_labels]

# Optional: enable legend
# ax.legend(ordered_handles, ordered_labels, title="Response", bbox_to_anchor=(1.05, 1), loc='upper left')

# Final formatting
ax.set_yticks(y_pos)
ax.set_yticklabels(questions)
ax.invert_yaxis()
ax.set_xlabel("Percentage")
ax.set_xlim(-80, 90) 
ax.set_title(f"Likert Scale Feedback for Prototype: {prototype}")
plt.tight_layout()
plt.show()