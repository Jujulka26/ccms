"""
ML Model Benchmark Evaluation
Run: python evaluate_model.py
Outputs: evaluation_report.txt + evaluation_plots.png
"""

import sys
import warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, ".")

import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, ConfusionMatrixDisplay,
)
from sklearn.dummy import DummyClassifier

from backend.ml import engineer_features_from_df, FEATURE_ORDER

BASE_DIR = Path(__file__).parent

# ── 1. Load data and engineer features ────────────────────────────────────────
print("Loading dataset...")
df_raw = pd.read_csv(str(BASE_DIR / "client_counselor_dataset.csv"))
print(f"  Dataset: {df_raw.shape[0]:,} rows, {df_raw.shape[1]} columns")

X_df = engineer_features_from_df(df_raw)
y = df_raw["match_success"].values[: len(X_df)]   # align after any row drops
X = X_df[FEATURE_ORDER]

print(f"  Features engineered: {X.shape[1]} features, {X.shape[0]:,} samples")
print(f"  Class distribution  — match=1: {y.sum()} ({y.mean()*100:.1f}%)  "
      f"match=0: {(1-y).sum()} ({(1-y).mean()*100:.1f}%)")

# ── 2. Train / test split (same seed as model training) ───────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"\nSplit: {len(X_train):,} train / {len(X_test):,} test (80/20 stratified)")

# ── 3. Load the trained model ─────────────────────────────────────────────────
print("\nLoading model (best_xgb_model.pkl)...")
model = joblib.load(str(BASE_DIR / "best_xgb_model.pkl"))
print(f"  Pipeline steps: {[s[0] for s in model.steps]}")

# ── 4. Evaluate on held-out test set ─────────────────────────────────────────
print("\n" + "="*60)
print("HELD-OUT TEST SET EVALUATION  (20% unseen data)")
print("="*60)

y_pred       = model.predict(X_test)
y_prob       = model.predict_proba(X_test)[:, 1]

acc      = accuracy_score(y_test, y_pred)
prec     = precision_score(y_test, y_pred)
rec      = recall_score(y_test, y_pred)
f1       = f1_score(y_test, y_pred)
roc_auc  = roc_auc_score(y_test, y_prob)

print(f"  Accuracy  : {acc:.4f}  ({acc*100:.2f}%)")
print(f"  Precision : {prec:.4f}")
print(f"  Recall    : {rec:.4f}")
print(f"  F1 Score  : {f1:.4f}")
print(f"  ROC-AUC   : {roc_auc:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["No Match (0)", "Match (1)"]))

# ── 5. Baseline comparison ────────────────────────────────────────────────────
print("="*60)
print("BASELINE COMPARISON")
print("="*60)
baseline = DummyClassifier(strategy="most_frequent", random_state=42)
baseline.fit(X_train, y_train)
y_base_pred = baseline.predict(X_test)
base_acc = accuracy_score(y_test, y_base_pred)
base_f1  = f1_score(y_test, y_base_pred, zero_division=0)
print(f"  Majority-class baseline — Accuracy: {base_acc:.4f}  F1: {base_f1:.4f}")
print(f"  Your XGBoost model     — Accuracy: {acc:.4f}  F1: {f1:.4f}")
print(f"  Improvement over baseline: +{(acc - base_acc)*100:.2f}% accuracy, "
      f"+{(f1 - base_f1)*100:.2f}% F1")

# ── 6. Cross-validation (5-fold) ──────────────────────────────────────────────
print("\n" + "="*60)
print("5-FOLD STRATIFIED CROSS-VALIDATION  (on full dataset)")
print("="*60)

# Note: use the RF step directly for CV since SMOTE is a training-time transform
#       We exclude SMOTE from CV to avoid data leakage from test folds.
rf_only = model.named_steps["model"]
prep     = model.named_steps["prep"]

X_scaled = prep.transform(X)   # apply scaler only (no SMOTE on test folds)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_results = cross_validate(
    rf_only, X_scaled, y,
    cv=cv,
    scoring=["accuracy", "f1", "roc_auc"],
    return_train_score=True,
)

for metric in ["accuracy", "f1", "roc_auc"]:
    test_scores  = cv_results[f"test_{metric}"]
    train_scores = cv_results[f"train_{metric}"]
    print(f"  {metric.upper():<10}  "
          f"CV mean={test_scores.mean():.4f} ± {test_scores.std():.4f}  "
          f"(train={train_scores.mean():.4f})  "
          f"[{test_scores.min():.4f} – {test_scores.max():.4f}]")

overfit_gap = cv_results["train_accuracy"].mean() - cv_results["test_accuracy"].mean()
if overfit_gap > 0.05:
    print(f"\n  WARNING: train/test accuracy gap = {overfit_gap:.4f} — possible overfitting")
else:
    print(f"\n  Train/test gap = {overfit_gap:.4f} — no significant overfitting detected")

# ── 7. Plots ──────────────────────────────────────────────────────────────────
print("\nGenerating evaluation plots...")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("ML Model Benchmark Evaluation — XGBoost (Deployed Model)", fontsize=14, fontweight="bold")

# Plot A: Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["No Match", "Match"])
disp.plot(ax=axes[0], colorbar=False, cmap="Blues")
axes[0].set_title("Confusion Matrix\n(Held-out Test Set)", fontweight="bold")

# Plot B: ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_prob)
axes[1].plot(fpr, tpr, color="#6D28D9", lw=2, label=f"RF (AUC = {roc_auc:.3f})")
axes[1].plot([0, 1], [0, 1], color="gray", linestyle="--", label="Random baseline")
axes[1].set_xlabel("False Positive Rate")
axes[1].set_ylabel("True Positive Rate")
axes[1].set_title("ROC Curve", fontweight="bold")
axes[1].legend()
axes[1].set_xlim([0, 1])
axes[1].set_ylim([0, 1.02])

# Plot C: Feature Importance
feature_importances = rf_only.feature_importances_
sorted_idx = np.argsort(feature_importances)
readable = {
    "issue_score": "Issue Similarity",
    "modality_match": "Modality Match",
    "gender_match": "Gender Match",
    "ethnicity_match": "Ethnicity Match",
    "age_gap": "Age Gap",
    "client_age": "Client Age",
    "counselor_age": "Counselor Age",
    "exp_years": "Experience (Years)",
    "prev_exp": "Previous Experience",
}
labels = [readable.get(FEATURE_ORDER[i], FEATURE_ORDER[i]) for i in sorted_idx]
colors = ["#6D28D9" if feature_importances[i] >= np.median(feature_importances) else "#C4B5FD"
          for i in sorted_idx]
axes[2].barh(labels, feature_importances[sorted_idx], color=colors)
axes[2].set_xlabel("Importance Score")
axes[2].set_title("Feature Importance\n(Random Forest)", fontweight="bold")
axes[2].set_xlim([0, feature_importances.max() * 1.15])
for i, v in enumerate(feature_importances[sorted_idx]):
    axes[2].text(v + 0.002, i, f"{v:.3f}", va="center", fontsize=8)

plt.tight_layout()
plot_path = BASE_DIR / "evaluation_plots.png"
plt.savefig(str(plot_path), dpi=150, bbox_inches="tight")
print(f"  Saved: evaluation_plots.png")

# ── 8. Written report ─────────────────────────────────────────────────────────
report_lines = [
    "ML MODEL BENCHMARK EVALUATION REPORT",
    "=" * 60,
    f"Dataset          : client_counselor_dataset.csv",
    f"Total samples    : {len(X):,}",
    f"Features         : {len(FEATURE_ORDER)}",
    f"Target           : match_success (binary)",
    f"Class balance    : match=1 ({y.mean()*100:.1f}%), match=0 ({(1-y).mean()*100:.1f}%)",
    f"Model            : XGBoost (n=100, max_depth=3, lr=0.1)",
    f"Pipeline         : StandardScaler -> SMOTE -> XGBoost",
    "",
    "TEST SET RESULTS (20% held-out, stratified split, seed=42)",
    "-" * 60,
    f"Accuracy         : {acc:.4f}",
    f"Precision        : {prec:.4f}",
    f"Recall           : {rec:.4f}",
    f"F1 Score         : {f1:.4f}",
    f"ROC-AUC          : {roc_auc:.4f}",
    "",
    "BASELINE COMPARISON",
    "-" * 60,
    f"Majority-class   : Accuracy={base_acc:.4f}  F1={base_f1:.4f}",
    f"RF model         : Accuracy={acc:.4f}  F1={f1:.4f}",
    f"Lift over baseline: +{(acc-base_acc)*100:.2f}% accuracy",
    "",
    "5-FOLD CROSS-VALIDATION",
    "-" * 60,
]
for metric in ["accuracy", "f1", "roc_auc"]:
    s = cv_results[f"test_{metric}"]
    report_lines.append(f"{metric.upper():<12}: mean={s.mean():.4f} ± {s.std():.4f}  range=[{s.min():.4f}–{s.max():.4f}]")

report_lines += [
    "",
    "FEATURE IMPORTANCE (highest to lowest)",
    "-" * 60,
]
for i in np.argsort(feature_importances)[::-1]:
    report_lines.append(f"  {readable.get(FEATURE_ORDER[i], FEATURE_ORDER[i]):<25}: {feature_importances[i]:.4f}")

report_lines += [
    "",
    "VERDICT",
    "-" * 60,
]
if roc_auc >= 0.85 and f1 >= 0.80:
    report_lines.append("Model performance is GOOD — suitable for deployment.")
elif roc_auc >= 0.75:
    report_lines.append("Model performance is ACCEPTABLE — consider further tuning.")
else:
    report_lines.append("Model performance needs improvement before deployment.")

report_text = "\n".join(report_lines)
report_path = BASE_DIR / "evaluation_report.txt"
report_path.write_text(report_text, encoding="utf-8")

print("\n" + "="*60)
print(report_text)
print("="*60)
print(f"\nSaved: evaluation_report.txt")
print("Done.")
