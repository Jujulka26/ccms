"""
XGBoost Hyperparameter Tuning
Run: python tune_xgboost.py
Outputs: tuned_xgb.pkl, tuning_comparison.csv, bagging_vs_boosting.png
"""

import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, ".")

import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from xgboost import XGBClassifier

BASE_DIR = Path(__file__).parent

# ── Feature tables (must match trainmodels.py) ─────────────────────────────────
ISSUE_SIMILARITY = {
    "Anxiety":    {"Anxiety": 1.0, "Stress": 0.7, "Trauma": 0.6, "Depression": 0.6},
    "Stress":     {"Stress": 1.0, "Anxiety": 0.7, "Trauma": 0.6, "Depression": 0.5},
    "Trauma":     {"Trauma": 1.0, "Stress": 0.6, "Anxiety": 0.6, "Depression": 0.6},
    "Depression": {"Depression": 1.0, "Anxiety": 0.6, "Stress": 0.5, "Trauma": 0.6},
}

MODALITY_ISSUE_FIT = {
    "Anxiety":    {"CBT": 1.0, "Mindfulness": 0.8, "REBT": 0.7, "Humanistic": 0.5},
    "Depression": {"CBT": 1.0, "Mindfulness": 0.8, "Humanistic": 0.6, "REBT": 0.6},
    "Stress":     {"Mindfulness": 1.0, "CBT": 0.7, "Humanistic": 0.7, "REBT": 0.5},
    "Trauma":     {"CBT": 1.0, "Humanistic": 0.6, "Mindfulness": 0.5, "REBT": 0.3},
}

FEATURE_ORDER = [
    "issue_score", "modality_match", "gender_match", "ethnicity_match",
    "age_gap", "client_age", "counselor_age", "exp_years", "prev_exp",
    "exp_issue_weight", "modality_issue_fit",
]

# ── Feature engineering ────────────────────────────────────────────────────────
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        try:
            client_issue       = row.get("client_issue", "")
            preferred_modality = row.get("preferred_modality", "")
            preferred_c_gender = row.get("preferred_counselor_gender", "No preference")
            counselor_modalities = [v.strip() for v in str(row.get("counselor_modality", "")).split(",") if v.strip()]
            exp_yrs = float(row.get("experience_years", 0))
            issue_sc = ISSUE_SIMILARITY.get(client_issue, {}).get(row.get("specialization", ""), 0.0)
            modality_primary = str(row.get("counselor_modality", "")).split(",")[0].strip()
            rows.append({
                "issue_score":        issue_sc,
                "modality_match":     int(preferred_modality in counselor_modalities),
                "gender_match":       1 if preferred_c_gender == "No preference" else int(preferred_c_gender == row.get("counselor_gender", "")),
                "ethnicity_match":    int(row.get("client_ethnicity", "") == row.get("counselor_ethnicity", "")),
                "age_gap":            abs(float(row.get("client_age", 0)) - float(row.get("counselor_age", 0))),
                "client_age":         float(row.get("client_age", 0)),
                "counselor_age":      float(row.get("counselor_age", 0)),
                "exp_years":          exp_yrs,
                "prev_exp":           float(row.get("previous_counseling_experience", 0)),
                "exp_issue_weight":   (
                    min(exp_yrs, 15) * 0.6 if client_issue == "Trauma"
                    else min(exp_yrs, 12) * 0.5 if client_issue == "Depression"
                    else min(exp_yrs, 10) * 0.3
                ),
                "modality_issue_fit": MODALITY_ISSUE_FIT.get(client_issue, {}).get(modality_primary, 0.5),
            })
        except Exception:
            continue
    return pd.DataFrame(rows)

# ── Load + engineer features ───────────────────────────────────────────────────
print("Loading dataset...")
df_raw = pd.read_csv(str(BASE_DIR / "client_counselor_dataset.csv"))
X_df   = engineer_features(df_raw)
X      = X_df[FEATURE_ORDER]
y      = df_raw["match_success"].values[:len(X_df)]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"Split: {len(X_train):,} train / {len(X_test):,} test")

# ── Load baseline XGBoost ──────────────────────────────────────────────────────
print("\nLoading baseline XGBoost...")
baseline_xgb = joblib.load(str(BASE_DIR / "baseline_xgb.pkl"))

y_pred_base = baseline_xgb.predict(X_test)
y_prob_base = baseline_xgb.predict_proba(X_test)[:, 1]
base_acc = accuracy_score(y_test, y_pred_base)
base_f1  = f1_score(y_test, y_pred_base)
base_auc = roc_auc_score(y_test, y_prob_base)

print(f"  Accuracy : {base_acc:.3f}")
print(f"  F1       : {base_f1:.3f}")
print(f"  ROC-AUC  : {base_auc:.3f}")

# ── Build tuning pipeline ──────────────────────────────────────────────────────
prep = ColumnTransformer([("num", StandardScaler(), FEATURE_ORDER)])

xgb_pipeline = ImbPipeline(steps=[
    ("prep",  prep),
    ("smote", SMOTE(random_state=42)),
    ("model", XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        verbosity=0,
    )),
])

# ── Hyperparameter search space ────────────────────────────────────────────────
param_dist = {
    "model__n_estimators":     [100, 200, 300, 400, 500],
    "model__max_depth":        [3, 4, 5, 6, 7, 8],
    "model__learning_rate":    [0.01, 0.03, 0.05, 0.08, 0.1, 0.15, 0.2],
    "model__subsample":        [0.6, 0.7, 0.8, 0.9, 1.0],
    "model__colsample_bytree": [0.6, 0.7, 0.8, 0.9, 1.0],
    "model__min_child_weight": [1, 2, 3, 5, 7],
    "model__gamma":            [0, 0.05, 0.1, 0.2, 0.3],
    "model__reg_alpha":        [0, 0.1, 0.5, 1.0],
    "model__reg_lambda":       [0.5, 1.0, 2.0, 3.0],
}

print("\nRunning RandomizedSearchCV (n_iter=50)...")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
search = RandomizedSearchCV(
    xgb_pipeline,
    param_distributions=param_dist,
    n_iter=50,
    scoring="roc_auc",
    cv=cv,
    random_state=42,
    n_jobs=-1,
    verbose=1,
)
search.fit(X_train, y_train)

best_xgb = search.best_estimator_
print(f"\nBest params: {search.best_params_}")

# ── Evaluate tuned XGBoost ─────────────────────────────────────────────────────
y_pred_tuned = best_xgb.predict(X_test)
y_prob_tuned = best_xgb.predict_proba(X_test)[:, 1]

tuned_acc = accuracy_score(y_test, y_pred_tuned)
tuned_f1  = f1_score(y_test, y_pred_tuned)
tuned_auc = roc_auc_score(y_test, y_prob_tuned)

print(f"\n===== TUNED XGBOOST =====")
print(f"Accuracy : {tuned_acc:.3f}")
print(f"F1       : {tuned_f1:.3f}")
print(f"ROC-AUC  : {tuned_auc:.3f}")

# ── Save tuned model ───────────────────────────────────────────────────────────
joblib.dump(best_xgb, str(BASE_DIR / "tuned_xgb.pkl"))
print("\nSaved: tuned_xgb.pkl")

# ── Save comparison CSV ────────────────────────────────────────────────────────
comparison = pd.DataFrame([
    {"Model": "Baseline XGBoost", "Accuracy": base_acc,  "F1": base_f1,  "ROC-AUC": base_auc},
    {"Model": "Tuned XGBoost",    "Accuracy": tuned_acc, "F1": tuned_f1, "ROC-AUC": tuned_auc},
])
comparison[["Accuracy", "F1", "ROC-AUC"]] = comparison[["Accuracy", "F1", "ROC-AUC"]].round(3)
comparison.to_csv(str(BASE_DIR / "tuning_comparison.csv"), index=False)
print("Saved: tuning_comparison.csv")

# ── Chart: Baseline vs Tuned ───────────────────────────────────────────────────
print("\nGenerating comparison chart...")

metrics    = ["Accuracy", "F1", "ROC-AUC"]
base_vals  = [base_acc,  base_f1,  base_auc]
tuned_vals = [tuned_acc, tuned_f1, tuned_auc]

x     = np.arange(len(metrics))
width = 0.30

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor("#FAFAF8")
ax.set_facecolor("#FAFAF8")

bars_base  = ax.bar(x - width/2, base_vals,  width, label="Baseline XGBoost",
                    color="#C4B5FD", zorder=3, edgecolor="white", linewidth=0.5)
bars_tuned = ax.bar(x + width/2, tuned_vals, width, label="Tuned XGBoost",
                    color="#6D28D9", zorder=3, edgecolor="white", linewidth=0.5)

for bars, vals in [(bars_base, base_vals), (bars_tuned, tuned_vals)]:
    for bar, val in zip(bars, vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.004,
            f"{val:.3f}",
            ha="center", va="bottom", fontsize=11, fontweight="bold", color="#374151",
        )

for i, (bv, tv) in enumerate(zip(base_vals, tuned_vals)):
    best_x = x[i] + width/2 if tv >= bv else x[i] - width/2
    ax.text(best_x, max(bv, tv) + 0.018, "★", ha="center", fontsize=11, color="#6D28D9")

ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=13, fontweight="bold")
all_vals = base_vals + tuned_vals
ax.set_ylim(max(0.0, min(all_vals) - 0.08), min(1.0, max(all_vals) + 0.06))
ax.set_ylabel("Score", fontsize=12)
ax.set_title("XGBoost — Baseline vs Tuned\nClient-Counselor Matching System",
             fontsize=14, fontweight="bold", pad=14)
ax.legend(fontsize=11, framealpha=0.9)
ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
ax.set_axisbelow(True)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

ax.text(0.98, 0.02, "★ = better per metric",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, color="#6B7280")

plt.tight_layout()
plt.savefig(str(BASE_DIR / "bagging_vs_boosting.png"), dpi=150, bbox_inches="tight", facecolor="#FAFAF8")
print("Saved: bagging_vs_boosting.png")

# ── Final summary ──────────────────────────────────────────────────────────────
print("\n" + "="*55)
print("BASELINE vs TUNED XGBOOST")
print("="*55)
print(f"{'Metric':<12} {'Baseline':>12} {'Tuned':>12} {'Gain':>10}")
print("-"*55)
for m, bv, tv in zip(metrics, base_vals, tuned_vals):
    print(f"{m:<12} {bv:>12.3f} {tv:>12.3f} {tv-bv:>+10.3f}")
print("-"*55)
print(f"{'Overall':<12} {np.mean(base_vals):>12.4f} {np.mean(tuned_vals):>12.4f} "
      f"{np.mean(tuned_vals)-np.mean(base_vals):>+10.4f}")
print("="*55)
print(f"\nDeployment model: tuned_xgb.pkl")
