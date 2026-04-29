"""
XGBoost Tuning + Bagging vs Boosting Comparison
Run: python tune_xgboost.py
Outputs: best_xgb_model.pkl, bagging_vs_boosting.png, tuning_comparison.csv
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
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.compose import ColumnTransformer
from xgboost import XGBClassifier

from backend.ml import engineer_features_from_df, FEATURE_ORDER

BASE_DIR = Path(__file__).parent

# ── Load + engineer features ───────────────────────────────────────────────────
print("Loading dataset...")
df_raw = pd.read_csv(str(BASE_DIR / "client_counselor_dataset.csv"))
X_df   = engineer_features_from_df(df_raw)
X      = X_df[FEATURE_ORDER]
y      = df_raw["match_success"].values[:len(X_df)]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"Split: {len(X_train):,} train / {len(X_test):,} test")

# ── Build XGBoost pipeline (same structure as RF pipeline) ────────────────────
prep = ColumnTransformer(
    transformers=[("num", StandardScaler(), FEATURE_ORDER)]
)

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
    "model__n_estimators":     [100, 200, 300, 400],
    "model__max_depth":        [3, 4, 5, 6, 7],
    "model__learning_rate":    [0.01, 0.05, 0.1, 0.2],
    "model__subsample":        [0.7, 0.8, 0.9, 1.0],
    "model__colsample_bytree": [0.7, 0.8, 0.9, 1.0],
    "model__min_child_weight": [1, 3, 5],
    "model__gamma":            [0, 0.1, 0.2],
}

print("\nRunning RandomizedSearchCV for XGBoost (this may take a few minutes)...")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
search = RandomizedSearchCV(
    xgb_pipeline,
    param_distributions=param_dist,
    n_iter=30,
    scoring="roc_auc",
    cv=cv,
    random_state=42,
    n_jobs=-1,
    verbose=1,
)
search.fit(X_train, y_train)

best_xgb = search.best_estimator_
print(f"\nBest XGBoost params: {search.best_params_}")

# ── Evaluate tuned XGBoost ────────────────────────────────────────────────────
y_pred_xgb = best_xgb.predict(X_test)
y_prob_xgb = best_xgb.predict_proba(X_test)[:, 1]

xgb_acc = accuracy_score(y_test, y_pred_xgb)
xgb_f1  = f1_score(y_test, y_pred_xgb)
xgb_auc = roc_auc_score(y_test, y_prob_xgb)

print(f"\n===== TUNED XGBOOST =====")
print(f"Accuracy : {xgb_acc:.3f}")
print(f"F1       : {xgb_f1:.3f}")
print(f"ROC-AUC  : {xgb_auc:.3f}")

# ── Load tuned RF for comparison ───────────────────────────────────────────────
rf_model   = joblib.load(str(BASE_DIR / "best_rf_model.pkl"))
y_pred_rf  = rf_model.predict(X_test)
y_prob_rf  = rf_model.predict_proba(X_test)[:, 1]

rf_acc = accuracy_score(y_test, y_pred_rf)
rf_f1  = f1_score(y_test, y_pred_rf)
rf_auc = roc_auc_score(y_test, y_prob_rf)

print(f"\n===== TUNED RANDOM FOREST =====")
print(f"Accuracy : {rf_acc:.3f}")
print(f"F1       : {rf_f1:.3f}")
print(f"ROC-AUC  : {rf_auc:.3f}")

# ── Save best XGBoost model ────────────────────────────────────────────────────
joblib.dump(best_xgb, str(BASE_DIR / "best_xgb_model.pkl"))
print("\nSaved: best_xgb_model.pkl")

# ── Save comparison CSV ────────────────────────────────────────────────────────
comparison = pd.DataFrame([
    {"Model": "Random Forest (Bagging)",  "Accuracy": rf_acc,  "F1": rf_f1,  "ROC-AUC": rf_auc},
    {"Model": "XGBoost (Boosting)",       "Accuracy": xgb_acc, "F1": xgb_f1, "ROC-AUC": xgb_auc},
])
comparison.to_csv(str(BASE_DIR / "tuning_comparison.csv"), index=False)
print("Saved: tuning_comparison.csv")

# ── Bagging vs Boosting chart ──────────────────────────────────────────────────
print("\nGenerating bagging vs boosting chart...")

metrics = ["Accuracy", "F1", "ROC-AUC"]
rf_vals  = [rf_acc,  rf_f1,  rf_auc]
xgb_vals = [xgb_acc, xgb_f1, xgb_auc]

x      = np.arange(len(metrics))
width  = 0.30
colors_rf  = "#6D28D9"
colors_xgb = "#F59E0B"

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor("#FAFAF8")
ax.set_facecolor("#FAFAF8")

bars_rf  = ax.bar(x - width/2, rf_vals,  width, label="Random Forest (Bagging)",
                  color=colors_rf,  zorder=3, edgecolor="white", linewidth=0.5)
bars_xgb = ax.bar(x + width/2, xgb_vals, width, label="XGBoost (Boosting)",
                  color=colors_xgb, zorder=3, edgecolor="white", linewidth=0.5)

for bars, vals in [(bars_rf, rf_vals), (bars_xgb, xgb_vals)]:
    for bar, val in zip(bars, vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.004,
            f"{val:.3f}",
            ha="center", va="bottom", fontsize=11, fontweight="bold", color="#374151",
        )

# Winner star per metric
for i, (rv, xv) in enumerate(zip(rf_vals, xgb_vals)):
    if rv >= xv:
        ax.text(x[i] - width/2, rv + 0.018, "★", ha="center", fontsize=11, color="#6D28D9")
    else:
        ax.text(x[i] + width/2, xv + 0.018, "★", ha="center", fontsize=11, color="#F59E0B")

ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=13, fontweight="bold")
ax.set_ylim(0.65, 0.97)
ax.set_ylabel("Score", fontsize=12)
ax.set_title("Bagging vs Boosting — Tuned Model Comparison\nClient-Counselor Matching System",
             fontsize=14, fontweight="bold", pad=14)
ax.legend(fontsize=11, framealpha=0.9)
ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
ax.set_axisbelow(True)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

ax.text(0.98, 0.02, "★ = winner per metric  |  Both models tuned on same dataset & split",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, color="#6B7280")

plt.tight_layout()
out = BASE_DIR / "bagging_vs_boosting.png"
plt.savefig(str(out), dpi=150, bbox_inches="tight", facecolor="#FAFAF8")
print("Saved: bagging_vs_boosting.png")

# ── Final summary ──────────────────────────────────────────────────────────────
print("\n" + "="*55)
print("BAGGING VS BOOSTING — FINAL COMPARISON")
print("="*55)
print(f"{'Metric':<12} {'Random Forest':>16} {'XGBoost':>12} {'Winner':>10}")
print("-"*55)
for m, rv, xv in zip(metrics, rf_vals, xgb_vals):
    winner = "RF" if rv >= xv else "XGBoost"
    print(f"{m:<12} {rv:>16.3f} {xv:>12.3f} {winner:>10}")
print("-"*55)
rf_overall  = np.mean(rf_vals)
xgb_overall = np.mean(xgb_vals)
overall_winner = "RF" if rf_overall >= xgb_overall else "XGBoost"
print(f"{'Overall':<12} {rf_overall:>16.4f} {xgb_overall:>12.4f} {overall_winner:>10}")
print("="*55)
print(f"\nSelected model for deployment: {overall_winner}")
