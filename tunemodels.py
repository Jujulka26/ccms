"""
Ensemble: soft-vote Baseline LightGBM + Baseline CatBoost.
Run: python tunemodels.py
Outputs: ensemble.pkl, ensemble_comparison.csv, ensemble_comparison.png
"""

import warnings
import os
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

BASE_DIR = Path(__file__).parent

# ── Feature tables ─────────────────────────────────────────────────────────────
ISSUE_SIMILARITY = {
    "Anxiety":    {"Anxiety": 1.0, "Stress": 0.7, "Trauma": 0.6, "Depression": 0.6},
    "Stress":     {"Stress": 1.0, "Anxiety": 0.7, "Trauma": 0.6, "Depression": 0.6},
    "Trauma":     {"Trauma": 1.0, "Stress": 0.6, "Anxiety": 0.6, "Depression": 0.6},
    "Depression": {"Depression": 1.0, "Anxiety": 0.6, "Stress": 0.6, "Trauma": 0.6},
}

MODALITY_ISSUE_FIT = {
    "Anxiety":    {"CBT": 1.0, "Mindfulness": 0.8, "REBT": 0.7, "Humanistic": 0.4},
    "Depression": {"CBT": 1.0, "Mindfulness": 0.8, "Humanistic": 0.7, "REBT": 0.6},
    "Stress":     {"Mindfulness": 1.0, "CBT": 0.7, "Humanistic": 0.7, "REBT": 0.5},
    "Trauma":     {"CBT": 1.0, "Humanistic": 0.5, "Mindfulness": 0.5, "REBT": 0.5},
}

FEATURES = [
    'issue_score', 'modality_issue_fit', 'modality_match', 'gender_match',
    'exp_issue_weight', 'ethnicity_match', 'prev_exp', 'age_gap',
    'exp_years', 'client_age', 'counselor_age',
]

# ── Feature engineering ────────────────────────────────────────────────────────
def engineer_features(df):
    df = df.copy()
    df['modality_match'] = (df['preferred_modality'] == df['counselor_modality']).astype(int)
    df['gender_match'] = (
        (df['preferred_counselor_gender'] == "No preference") |
        (df['preferred_counselor_gender'] == df['counselor_gender'])
    ).astype(int)
    df['ethnicity_match'] = (df['client_ethnicity'] == df['counselor_ethnicity']).astype(int)
    df['issue_score'] = df.apply(
        lambda r: ISSUE_SIMILARITY[r['client_issue']][r['specialization']], axis=1
    )
    df['prev_exp'] = df['previous_counseling_experience']
    df['age_gap'] = abs(df['client_age'] - df['counselor_age'])
    df['exp_years'] = df['experience_years']
    df['exp_issue_weight'] = (df['experience_years'] >= 8).astype(int)
    df['modality_issue_fit'] = df.apply(
        lambda r: MODALITY_ISSUE_FIT.get(r['client_issue'], {}).get(
            str(r['counselor_modality']).split(',')[0].strip(), 0.5
        ), axis=1
    )
    return df[FEATURES]

# ── Load data ──────────────────────────────────────────────────────────────────
print("Loading dataset...")
df_raw = pd.read_csv(str(BASE_DIR / "client_counselor_dataset.csv"))
X = engineer_features(df_raw)
y = df_raw["match_success"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"Split: {len(X_train):,} train / {len(X_test):,} test")

# ── Load baselines ─────────────────────────────────────────────────────────────
print("\nLoading baselines...")
lgbm = joblib.load(str(BASE_DIR / "baseline_lgbm.pkl"))
cat  = joblib.load(str(BASE_DIR / "baseline_cat.pkl"))

def evaluate(y_true, y_pred, y_prob):
    return {
        "Accuracy": round(float(accuracy_score(y_true, y_pred)), 3),
        "F1":       round(float(f1_score(y_true, y_pred)), 3),
        "ROC-AUC":  round(float(roc_auc_score(y_true, y_prob)), 3),
    }

scores_lgbm = evaluate(y_test, lgbm.predict(X_test), lgbm.predict_proba(X_test)[:, 1])
scores_cat  = evaluate(y_test, cat.predict(X_test),  cat.predict_proba(X_test)[:, 1])
print(f"  Baseline LightGBM : {scores_lgbm}")
print(f"  Baseline CatBoost : {scores_cat}")

# ── Ensemble: average probabilities ───────────────────────────────────────────
print("\nBuilding ensemble (soft voting)...")
avg_prob = (lgbm.predict_proba(X_test)[:, 1] + cat.predict_proba(X_test)[:, 1]) / 2
ens_pred = (avg_prob >= 0.5).astype(int)
scores_ens = evaluate(y_test, ens_pred, avg_prob)
print(f"  Ensemble : {scores_ens}")

joblib.dump({"lgbm": lgbm, "cat": cat}, str(BASE_DIR / "ensemble.pkl"))
print("  Saved: ensemble.pkl")

# ── Save CSV ───────────────────────────────────────────────────────────────────
rows = [
    {"Model": "Baseline LightGBM",   **scores_lgbm},
    {"Model": "Baseline CatBoost",   **scores_cat},
    {"Model": "Ensemble (LGBM+Cat)", **scores_ens},
]
pd.DataFrame(rows).to_csv(str(BASE_DIR / "ensemble_comparison.csv"), index=False)
print("\nSaved: ensemble_comparison.csv")

# ── Chart ──────────────────────────────────────────────────────────────────────
print("Generating chart...")
metrics = ["Accuracy", "F1", "ROC-AUC"]
plot_data = {
    "Baseline LightGBM":   (scores_lgbm, "#C4B5FD"),
    "Baseline CatBoost":   (scores_cat,  "#FCA5A5"),
    "Ensemble (LGBM+Cat)": (scores_ens,  "#059669"),
}

x, width, offsets = np.arange(len(metrics)), 0.25, [-1, 0, 1]

fig, ax = plt.subplots(figsize=(11, 6))
fig.patch.set_facecolor("#FAFAF8")
ax.set_facecolor("#FAFAF8")

for (label, (scores, color)), offset in zip(plot_data.items(), offsets):
    vals = [scores[m] for m in metrics]
    bars = ax.bar(x + offset * width, vals, width, label=label,
                  color=color, zorder=3, edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
                f"{val:.3f}", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color="#374151")

ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=13, fontweight="bold")
all_vals = [s[m] for _, (s, _) in plot_data.items() for m in metrics]
ax.set_ylim(max(0.0, min(all_vals) - 0.08), min(1.0, max(all_vals) + 0.06))
ax.set_ylabel("Score", fontsize=12)
ax.set_title("Ensemble vs Individual Models\nClient-Counselor Matching System",
             fontsize=14, fontweight="bold", pad=14)
ax.legend(fontsize=10, framealpha=0.9)
ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
ax.set_axisbelow(True)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig(str(BASE_DIR / "ensemble_comparison.png"), dpi=150,
            bbox_inches="tight", facecolor="#FAFAF8")
print("Saved: ensemble_comparison.png")

# ── Summary ────────────────────────────────────────────────────────────────────
print("\n" + "=" * 55)
print(f"{'Model':<25} {'Accuracy':>9} {'F1':>9} {'ROC-AUC':>9}")
print("-" * 55)
for row in rows:
    print(f"{row['Model']:<25} {row['Accuracy']:>9.3f} {row['F1']:>9.3f} {row['ROC-AUC']:>9.3f}")
print("=" * 55)
print("\nDeployment model: ensemble.pkl")
