"""
Exploratory Data Analysis — Client-Counselor Matching Dataset
Run: python ml/eda.py
Outputs: eda_output/ folder with PNG plots + printed summary to console
"""

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR  = Path(__file__).parent
DATA_PATH = BASE_DIR / "client_counselor_dataset.csv"
OUT_DIR   = BASE_DIR / "eda_output"
OUT_DIR.mkdir(exist_ok=True)

MATCH_COLORS = ["#E05C5C", "#4C9BE8"]

plt.rcParams.update({
    "figure.facecolor":  "#FAFAF8",
    "axes.facecolor":    "#FAFAF8",
    "axes.titlesize":    12,
    "axes.labelsize":    10,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})


def save(fig, name):
    fig.savefig(OUT_DIR / name, dpi=140, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved -> eda_output/{name}")


# ============================================================
# 1. LOAD & OVERVIEW
# ============================================================
print("=" * 62)
print("1. DATASET OVERVIEW")
print("=" * 62)

df = pd.read_csv(DATA_PATH)
total = len(df)

print(f"  Shape          : {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"  Duplicate rows : {df.duplicated().sum()}")

missing = df.isnull().sum()
missing = missing[missing > 0]
print(f"  Missing values : {len(missing)} column(s) affected" if len(missing) else "  Missing values : none")

print(f"\n  {'Column':<35} {'Dtype':<12} {'Unique':>7}")
print("  " + "-" * 56)
for col in df.columns:
    print(f"  {col:<35} {str(df[col].dtype):<12} {df[col].nunique():>7}")

print(f"\n  Numerical summary:")
print(df[["client_age", "counselor_age", "experience_years"]].describe().round(2).to_string())


# ============================================================
# 2. TARGET VARIABLE
# ============================================================
print("\n" + "=" * 62)
print("2. TARGET — match_success")
print("=" * 62)

vc = df["match_success"].value_counts().sort_index()
print(f"  Class 0 (No Match) : {vc[0]:,}  ({vc[0]/total*100:.1f}%)")
print(f"  Class 1 (Match)    : {vc[1]:,}  ({vc[1]/total*100:.1f}%)")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
fig.suptitle("Target Variable: match_success", fontsize=13, fontweight="bold")

bars = ax1.bar(["No Match (0)", "Match (1)"], vc.values,
               color=MATCH_COLORS, edgecolor="white", width=0.5)
for bar, v in zip(bars, vc.values):
    ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + total * 0.005,
             f"{v:,}", ha="center", fontsize=10, fontweight="bold")
ax1.set_title("Class Counts")
ax1.set_ylabel("Count")

ax2.pie(vc.values, labels=["No Match", "Match"], colors=MATCH_COLORS,
        autopct="%1.1f%%", startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5})
ax2.set_title("Class Proportions")
fig.tight_layout()
save(fig, "01_target_distribution.png")


# ============================================================
# 3. NUMERICAL DISTRIBUTIONS
# ============================================================
print("\n" + "=" * 62)
print("3. NUMERICAL DISTRIBUTIONS")
print("=" * 62)

NUM_COLS = ["client_age", "counselor_age", "experience_years"]

fig, axes = plt.subplots(2, len(NUM_COLS), figsize=(14, 7))
fig.suptitle("Numerical Feature Distributions", fontsize=13, fontweight="bold")

for j, col in enumerate(NUM_COLS):
    for cls, color in zip([0, 1], MATCH_COLORS):
        subset = df[df["match_success"] == cls][col].dropna()
        axes[0, j].hist(subset, bins=25, alpha=0.65, color=color,
                        edgecolor="white", label=f"Match={cls}")
        axes[0, j].axvline(subset.mean(), color=color, linestyle="--", linewidth=1)
    axes[0, j].set_title(col)
    axes[0, j].set_ylabel("Count")
    axes[0, j].legend(fontsize=8)

    bp_data = [df[df["match_success"] == c][col].dropna() for c in [0, 1]]
    bp = axes[1, j].boxplot(bp_data, labels=["No Match", "Match"],
                             patch_artist=True, widths=0.45,
                             medianprops={"color": "black", "linewidth": 2})
    for patch, color in zip(bp["boxes"], MATCH_COLORS):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    axes[1, j].set_title(f"{col} by Match Outcome")
    axes[1, j].set_ylabel(col)

    m0 = df[df["match_success"] == 0][col].mean()
    m1 = df[df["match_success"] == 1][col].mean()
    print(f"  {col:<25} mean(0)={m0:.1f}  mean(1)={m1:.1f}  Δ={m1-m0:+.1f}")

fig.tight_layout()
save(fig, "02_numerical_distributions.png")


# ============================================================
# 4. CATEGORICAL DISTRIBUTIONS
# ============================================================
print("\n" + "=" * 62)
print("4. CATEGORICAL DISTRIBUTIONS")
print("=" * 62)

CAT_COLS = [
    "client_gender", "client_ethnicity", "client_issue",
    "preferred_language", "preferred_modality", "preferred_counselor_gender",
    "previous_counseling_experience",
    "counselor_gender", "counselor_ethnicity", "specialization", "counselor_modality",
]

ncols = 3
nrows = (len(CAT_COLS) + ncols - 1) // ncols
fig, axes = plt.subplots(nrows, ncols, figsize=(16, nrows * 4))
axes_flat = axes.flatten()
fig.suptitle("Categorical Feature Distributions", fontsize=13, fontweight="bold")

for i, col in enumerate(CAT_COLS):
    vc = df[col].value_counts()
    pct = vc / total * 100
    bars = axes_flat[i].bar(vc.index.astype(str), vc.values,
                             color="#4C72B0", edgecolor="white")
    for bar, p in zip(bars, pct):
        axes_flat[i].text(bar.get_x() + bar.get_width() / 2,
                          bar.get_height() + total * 0.004,
                          f"{p:.1f}%", ha="center", fontsize=7.5)
    axes_flat[i].set_title(col)
    axes_flat[i].set_ylabel("Count")
    axes_flat[i].tick_params(axis="x", rotation=30)
    print(f"  {col}: {dict(zip(vc.index.astype(str), vc.values))}")

for j in range(i + 1, len(axes_flat)):
    axes_flat[j].set_visible(False)

fig.tight_layout()
save(fig, "03_categorical_distributions.png")


# ============================================================
# 5. MATCH RATE BY CATEGORICAL FEATURE
# ============================================================
print("\n" + "=" * 62)
print("5. MATCH RATE BY CATEGORY")
print("=" * 62)

overall_rate = df["match_success"].mean() * 100

fig, axes = plt.subplots(nrows, ncols, figsize=(16, nrows * 4))
axes_flat = axes.flatten()
fig.suptitle("Match Rate (%) by Categorical Feature", fontsize=13, fontweight="bold")

for i, col in enumerate(CAT_COLS):
    rates = df.groupby(col)["match_success"].mean().sort_values(ascending=False) * 100
    bar_colors = plt.cm.RdYlGn(np.linspace(0.15, 0.85, len(rates)))
    bars = axes_flat[i].bar(rates.index.astype(str), rates.values,
                             color=bar_colors, edgecolor="white")
    for bar, val in zip(bars, rates.values):
        axes_flat[i].text(bar.get_x() + bar.get_width() / 2,
                          bar.get_height() + 0.5,
                          f"{val:.1f}%", ha="center", fontsize=7.5, fontweight="bold")
    axes_flat[i].axhline(overall_rate, color="#888", linestyle="--",
                         linewidth=0.9, label=f"Overall {overall_rate:.1f}%")
    axes_flat[i].set_title(f"Match Rate by {col}")
    axes_flat[i].set_ylabel("Match Rate (%)")
    axes_flat[i].set_ylim(0, min(100, rates.max() * 1.18))
    axes_flat[i].tick_params(axis="x", rotation=30)
    axes_flat[i].legend(fontsize=7)
    print(f"  {col}:")
    for k, v in rates.items():
        print(f"    {str(k):<28} {v:.1f}%  ({v - overall_rate:+.1f}pp vs avg)")

for j in range(i + 1, len(axes_flat)):
    axes_flat[j].set_visible(False)

fig.tight_layout()
save(fig, "04_match_rate_by_category.png")


# ============================================================
# 6. CORRELATION WITH TARGET
# ============================================================
print("\n" + "=" * 62)
print("6. CORRELATION ANALYSIS")
print("=" * 62)

numeric_df = df.select_dtypes(include=["int64", "float64"]).drop(
    columns=["client_id", "counselor_id"], errors="ignore")
corr = numeric_df.corr(numeric_only=True)
target_corr = corr["match_success"].drop("match_success").sort_values(ascending=False)

print("\n  Correlation with match_success:")
for feat, val in target_corr.items():
    bar_str = ("+" if val >= 0 else "") + "▇" * int(abs(val) * 20)
    print(f"    {feat:<35} {val:+.3f}  {bar_str}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle("Correlation Analysis", fontsize=13, fontweight="bold")

im = ax1.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
ax1.set_xticks(range(len(corr.columns)))
ax1.set_yticks(range(len(corr.index)))
ax1.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=7.5)
ax1.set_yticklabels(corr.index, fontsize=7.5)
for i in range(len(corr)):
    for j in range(len(corr.columns)):
        val = corr.values[i, j]
        if abs(val) >= 0.12:
            ax1.text(j, i, f"{val:.2f}", ha="center", va="center",
                     fontsize=6.5, color="white" if abs(val) > 0.5 else "black")
fig.colorbar(im, ax=ax1, fraction=0.03, pad=0.02)
ax1.set_title("Full Correlation Matrix")

bar_colors = ["#4C9BE8" if v > 0 else "#E05C5C" for v in target_corr.values]
ax2.barh(target_corr.index, target_corr.values, color=bar_colors, edgecolor="white")
ax2.axvline(0, color="black", linewidth=0.8)
ax2.set_title("Feature Correlation with match_success")
ax2.set_xlabel("Pearson r")
fig.tight_layout()
save(fig, "05_correlation_analysis.png")


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 62)
print("EDA SUMMARY")
print("=" * 62)
print(f"  Total pairs        : {len(df):,}")
print(f"  Overall match rate : {df['match_success'].mean()*100:.1f}%")
print(f"  Strongest predictor: {target_corr.index[0]}  (r={target_corr.iloc[0]:+.3f})")
print(f"  Weakest predictor  : {target_corr.index[-1]} (r={target_corr.iloc[-1]:+.3f})")
print(f"  Plots saved to     : {OUT_DIR}")
print("=" * 62)
