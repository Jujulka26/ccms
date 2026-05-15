"""
Model Benchmark Comparison Chart
Run: python benchmark_chart.py
Outputs: benchmark_comparison.png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent

df = pd.read_csv(str(BASE_DIR / "model_results.csv"))

models  = df["Model"].tolist()
metrics = ["Accuracy", "F1", "ROC-AUC"]
colors  = ["#6D28D9", "#7C3AED", "#A78BFA", "#C4B5FD"]

x      = np.arange(len(metrics))
width  = 0.18
gap    = 0.02
n      = len(models)
starts = -(n - 1) / 2 * (width + gap)

fig, axes = plt.subplots(1, 2, figsize=(18, 6))
fig.patch.set_facecolor("#FAFAF8")

# ── Left: Grouped bar chart ────────────────────────────────────────────────────
ax = axes[0]
ax.set_facecolor("#FAFAF8")

for i, (model, color) in enumerate(zip(models, colors)):
    offsets = starts + i * (width + gap)
    vals    = [df.loc[df["Model"] == model, m].values[0] for m in metrics]
    bars    = ax.bar(x + offsets, vals, width, color=color, label=model,
                     zorder=3, edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.005,
            f"{val:.3f}",
            ha="center", va="bottom", fontsize=7.5, fontweight="bold", color="#374151",
        )

ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=12, fontweight="bold")
ax.set_ylim(0.65, 0.96)
ax.set_ylabel("Score", fontsize=11)
ax.set_title("Model Benchmark Comparison\n(Accuracy · F1 · ROC-AUC)",
             fontsize=13, fontweight="bold", pad=12)
ax.legend(loc="lower right", framealpha=0.9, fontsize=9)
ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
ax.set_axisbelow(True)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

# Highlight best bar per metric with a star
for m_idx, metric in enumerate(metrics):
    best_val   = df[metric].max()
    best_model = df.loc[df[metric].idxmax(), "Model"]
    m_i        = models.index(best_model)
    bar_x      = x[m_idx] + starts + m_i * (width + gap) + width / 2
    bar_y      = best_val + 0.022
    ax.text(bar_x, bar_y, "★", ha="center", va="bottom",
            fontsize=9, color="#F59E0B")

ax.text(0.98, 0.02, "★ = best in metric", transform=ax.transAxes,
        ha="right", va="bottom", fontsize=8, color="#6B7280")

# ── Right: Summary table ───────────────────────────────────────────────────────
ax2 = axes[1]
ax2.set_facecolor("#FAFAF8")
ax2.axis("off")

df_display = df.copy()
df_display["Overall"] = df_display[["Accuracy", "F1", "ROC-AUC"]].mean(axis=1).round(4)
df_display = df_display.sort_values("Overall", ascending=False).reset_index(drop=True)

col_labels = ["Model", "Accuracy", "F1", "ROC-AUC", "Overall"]
table_data = []
for _, row in df_display.iterrows():
    table_data.append([
        row["Model"],
        f"{row['Accuracy']:.3f}",
        f"{row['F1']:.3f}",
        f"{row['ROC-AUC']:.3f}",
        f"{row['Overall']:.4f}",
    ])

tbl = ax2.table(
    cellText=table_data,
    colLabels=col_labels,
    cellLoc="center",
    loc="center",
    bbox=[0, 0.15, 1, 0.7],
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(11)

# Header styling
for j in range(len(col_labels)):
    tbl[0, j].set_facecolor("#6D28D9")
    tbl[0, j].set_text_props(color="white", fontweight="bold")
    tbl[0, j].set_height(0.12)

# Row styling — highlight best model (rank 1)
row_colors = ["#EDE9FE", "#F5F3FF", "#FAF8FF", "#FFFFFF"]
for i, row_color in enumerate(row_colors):
    for j in range(len(col_labels)):
        tbl[i + 1, j].set_facecolor(row_color)
        tbl[i + 1, j].set_height(0.10)
        if i == 0:
            tbl[i + 1, j].set_text_props(fontweight="bold")

# Bold the best value in each metric column
metric_col_map = {"Accuracy": 1, "F1": 2, "ROC-AUC": 3, "Overall": 4}
for metric, col_idx in metric_col_map.items():
    best_model = df_display.loc[df_display[metric].idxmax(), "Model"]
    best_row   = df_display[df_display["Model"] == best_model].index[0] + 1
    tbl[best_row, col_idx].set_text_props(color="#6D28D9", fontweight="bold")

ax2.set_title("Model Performance Summary Table\n(sorted by Overall score)",
              fontsize=13, fontweight="bold", pad=12)
ax2.text(0.5, 0.08,
         "Overall = mean(Accuracy, F1, ROC-AUC)  |  Purple = best in column",
         ha="center", va="center", transform=ax2.transAxes,
         fontsize=8.5, color="#6B7280")

plt.suptitle("ML Model Benchmark — Client-Counselor Matching System",
             fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()

out = BASE_DIR / "benchmark_comparison.png"
plt.savefig(str(out), dpi=150, bbox_inches="tight", facecolor="#FAFAF8")
print(f"Saved: benchmark_comparison.png")
