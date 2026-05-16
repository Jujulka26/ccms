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
y    = df_raw["match_success"].values[:len(X_df)]
X    = X_df[FEATURE_ORDER]

print(f"  Features: {X.shape[1]}, Samples: {X.shape[0]:,}")
print(f"  Class balance — match=1: {y.sum()} ({y.mean()*100:.1f}%)  "
      f"match=0: {(1-y).sum()} ({(1-y).mean()*100:.1f}%)")

# ── 2. Train / test split ─────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"\nSplit: {len(X_train):,} train / {len(X_test):,} test (80/20 stratified)")

# ── 3. Load ensemble (deployed model) ────────────────────────────────────────
print("\nLoading model (ensemble.pkl)...")
model = joblib.load(str(BASE_DIR / "ensemble.pkl"))
print("  Loaded: SoftVotingEnsemble (LightGBM + CatBoost)")

# ── 4. Evaluate on held-out test set ─────────────────────────────────────────
print("\n" + "="*60)
print("HELD-OUT TEST SET EVALUATION  (20% unseen data)")
print("="*60)

y_pred  = model.predict(X_test)
y_prob  = model.predict_proba(X_test)[:, 1]

acc     = accuracy_score(y_test, y_pred)
prec    = precision_score(y_test, y_pred)
rec     = recall_score(y_test, y_pred)
f1      = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_prob)

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
base_acc    = accuracy_score(y_test, y_base_pred)
base_f1     = f1_score(y_test, y_base_pred, zero_division=0)
print(f"  Majority-class baseline — Accuracy: {base_acc:.4f}  F1: {base_f1:.4f}")
print(f"  Ensemble               — Accuracy: {acc:.4f}  F1: {f1:.4f}")
print(f"  Improvement: +{(acc - base_acc)*100:.2f}% accuracy, +{(f1 - base_f1)*100:.2f}% F1")

# ── 6. Component comparison on test set ──────────────────────────────────────
print("\n" + "="*60)
print("COMPONENT COMPARISON  (same held-out test set)")
print("="*60)

lgbm_pipe = model._lgbm
cat_pipe  = model._cat

for label, pipe in [("Tuned LightGBM", lgbm_pipe), ("Tuned CatBoost", cat_pipe), ("Ensemble", model)]:
    yp   = pipe.predict(X_test)
    ypr  = pipe.predict_proba(X_test)[:, 1]
    print(f"  {label:<22}  "
          f"Acc={accuracy_score(y_test, yp):.4f}  "
          f"F1={f1_score(y_test, yp):.4f}  "
          f"ROC-AUC={roc_auc_score(y_test, ypr):.4f}")

lgbm_only = lgbm_pipe.named_steps["model"]

# ── 7. Cross-validation on both components ────────────────────────────────────
print("\n" + "="*60)
print("5-FOLD STRATIFIED CROSS-VALIDATION  (LightGBM & CatBoost)")
print("="*60)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_results = {}

for label, pipe in [("LightGBM", lgbm_pipe), ("CatBoost", cat_pipe)]:
    inner_model = pipe.named_steps["model"]
    X_scaled    = pipe.named_steps["prep"].transform(X)
    res = cross_validate(
        inner_model, X_scaled, y,
        cv=cv,
        scoring=["accuracy", "f1", "roc_auc"],
        return_train_score=True,
    )
    cv_results[label] = res
    print(f"\n  {label}")
    for metric in ["accuracy", "f1", "roc_auc"]:
        ts = res[f"test_{metric}"]
        tr = res[f"train_{metric}"]
        print(f"    {metric.upper():<10}  CV={ts.mean():.4f} ± {ts.std():.4f}  "
              f"train={tr.mean():.4f}  [{ts.min():.4f}–{ts.max():.4f}]")
    gap = res["train_accuracy"].mean() - res["test_accuracy"].mean()
    if gap > 0.05:
        print(f"    WARNING: train/test gap={gap:.4f} — possible overfitting")
    else:
        print(f"    Train/test gap={gap:.4f} — no significant overfitting")

# ── 8. Plots ──────────────────────────────────────────────────────────────────
print("\nGenerating evaluation plots...")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("ML Model Evaluation — Ensemble (LightGBM + CatBoost)",
             fontsize=14, fontweight="bold")

# Plot A: Confusion Matrix
cm   = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["No Match", "Match"])
disp.plot(ax=axes[0], colorbar=False, cmap="Blues")
axes[0].set_title("Confusion Matrix\n(Held-out Test Set)", fontweight="bold")

# Plot B: ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_prob)
axes[1].plot(fpr, tpr, color="#6D28D9", lw=2, label=f"Ensemble (AUC = {roc_auc:.3f})")
axes[1].plot([0, 1], [0, 1], color="gray", linestyle="--", label="Random baseline")
axes[1].set_xlabel("False Positive Rate")
axes[1].set_ylabel("True Positive Rate")
axes[1].set_title("ROC Curve", fontweight="bold")
axes[1].legend()
axes[1].set_xlim([0, 1])
axes[1].set_ylim([0, 1.02])

# Plot C: Feature Importance (averaged across LightGBM + CatBoost)
cat_only   = cat_pipe.named_steps["model"]
lgbm_imp   = lgbm_only.booster_.feature_importance(importance_type="gain").astype(float)
cat_imp    = cat_only.get_feature_importance().astype(float)
lgbm_imp  /= lgbm_imp.sum()
cat_imp   /= cat_imp.sum()
feature_importances = (lgbm_imp + cat_imp) / 2
sorted_idx = np.argsort(feature_importances)
readable = {
    "issue_match":        "Issue Similarity",
    "modality_issue_fit": "Issue-Modality Fit",
    "modality_match":     "Preferred Modality Match",
    "gender_match":       "Preferred Gender Match",
    "exp_issue_fit":      "Counselor Seniority",
    "ethnicity_match":    "Ethnicity Match",
    "prev_exp":           "Client Previous Experience",
    "age_gap":            "Age Gap",
}
labels = [readable.get(FEATURE_ORDER[i], FEATURE_ORDER[i]) for i in sorted_idx]
colors = ["#6D28D9" if feature_importances[i] >= np.median(feature_importances) else "#C4B5FD"
          for i in sorted_idx]
axes[2].barh(labels, feature_importances[sorted_idx], color=colors)
axes[2].set_xlabel("Relative Importance (normalized)")
axes[2].set_title("Feature Importance\n(LightGBM + CatBoost averaged)", fontweight="bold")
axes[2].set_xlim([0, feature_importances.max() * 1.15])
for i, v in enumerate(feature_importances[sorted_idx]):
    axes[2].text(v + 0.002, i, f"{v:.3f}", va="center", fontsize=8)

plt.tight_layout()
plt.savefig(str(BASE_DIR / "evaluation_plots.png"), dpi=150, bbox_inches="tight")
print("  Saved: evaluation_plots.png")

# ── 8. Written report ─────────────────────────────────────────────────────────
report_lines = [
    "ML MODEL EVALUATION REPORT",
    "=" * 60,
    f"Dataset       : client_counselor_dataset.csv",
    f"Total samples : {len(X):,}",
    f"Features      : {len(FEATURE_ORDER)}",
    f"Target        : match_success (binary)",
    f"Class balance : match=1 ({y.mean()*100:.1f}%), match=0 ({(1-y).mean()*100:.1f}%)",
    f"Model         : Ensemble (LightGBM + CatBoost)",
    f"Pipeline      : Soft-voting ensemble of two tuned pipelines",
    "",
    "TEST SET RESULTS (20% held-out, stratified split, seed=42)",
    "-" * 60,
    f"Accuracy      : {acc:.4f}",
    f"Precision     : {prec:.4f}",
    f"Recall        : {rec:.4f}",
    f"F1 Score      : {f1:.4f}",
    f"ROC-AUC       : {roc_auc:.4f}",
    "",
    "BASELINE COMPARISON",
    "-" * 60,
    f"Majority-class : Accuracy={base_acc:.4f}  F1={base_f1:.4f}",
    f"Ensemble       : Accuracy={acc:.4f}  F1={f1:.4f}",
    f"Lift over baseline: +{(acc-base_acc)*100:.2f}% accuracy",
    "",
    "5-FOLD CROSS-VALIDATION",
    "-" * 60,
]
for cv_label in ["LightGBM", "CatBoost"]:
    res = cv_results[cv_label]
    report_lines.append(f"  {cv_label}")
    for metric in ["accuracy", "f1", "roc_auc"]:
        s = res[f"test_{metric}"]
        report_lines.append(f"    {metric.upper():<10}: mean={s.mean():.4f} ± {s.std():.4f}  "
                            f"[{s.min():.4f}–{s.max():.4f}]")
report_lines += [
    "",
    "FEATURE IMPORTANCE (highest to lowest, LightGBM + CatBoost averaged)",
    "-" * 60,
]
for i in np.argsort(feature_importances)[::-1]:
    label = readable.get(FEATURE_ORDER[i], FEATURE_ORDER[i])
    report_lines.append(f"  {label:<30}: {feature_importances[i]:.4f}  ({feature_importances[i]*100:.1f}%)")

report_lines += ["", "VERDICT", "-" * 60]
if roc_auc >= 0.85 and f1 >= 0.75:
    report_lines.append("Model performance is GOOD — suitable for deployment.")
elif roc_auc >= 0.75:
    report_lines.append("Model performance is ACCEPTABLE — consider further tuning.")
else:
    report_lines.append("Model performance needs improvement before deployment.")

report_text = "\n".join(report_lines)
(BASE_DIR / "evaluation_report.txt").write_text(report_text, encoding="utf-8")

print("\n" + "="*60)
print(report_text)
print("="*60)
print("\nSaved: evaluation_report.txt")
print("Done.")
