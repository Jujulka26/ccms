import sys
import warnings
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

BASE_DIR = Path(__file__).parent



ISSUE_SIMILARITY = {
    "Anxiety":    {"Anxiety": 1.0, "Stress": 0.7, "Trauma": 0.6, "Depression": 0.6},
    "Stress":     {"Stress":  1.0, "Anxiety": 0.7, "Trauma": 0.6, "Depression": 0.6},
    "Trauma":     {"Trauma":  1.0, "Stress":  0.6, "Anxiety": 0.6, "Depression": 0.6},
    "Depression": {"Depression": 1.0, "Anxiety": 0.6, "Stress": 0.6, "Trauma": 0.6},
}

MODALITY_ISSUE_FIT = {
    "Anxiety":    {"Cognitive": 1.0, "Behavioral": 0.9, "Humanistic": 0.2, "Psychodynamic": 0.3},
    "Depression": {"Cognitive": 1.0, "Behavioral": 0.8, "Humanistic": 0.7, "Psychodynamic": 0.9},
    "Stress":     {"Cognitive": 0.8, "Behavioral": 0.7, "Humanistic": 0.7, "Psychodynamic": 0.3},
    "Trauma":     {"Behavioral": 1.0, "Cognitive": 0.9, "Humanistic": 0.2, "Psychodynamic": 0.4},
}

FEATURES = [
    'issue_match', 'modality_issue_fit', 'modality_match', 'gender_match',
    'exp_issue_fit', 'ethnicity_match', 'prev_exp', 'age_gap',
]


def engineer_features(df):
    df = df.copy()
    df['modality_match']     = df.apply(
        lambda row: int(row['preferred_modality'] in [m.strip() for m in str(row['counselor_modality']).split(',')]),
        axis=1
    )
    df['gender_match']       = ((df['preferred_counselor_gender'] == "No preference") |
                                (df['preferred_counselor_gender'] == df['counselor_gender'])).astype(int)
    df['ethnicity_match']    = (df['client_ethnicity'] == df['counselor_ethnicity']).astype(int)
    df['issue_match']        = df.apply(lambda r: ISSUE_SIMILARITY[r['client_issue']][r['specialization']], axis=1)
    df['exp_issue_fit']      = (df['experience_years'] >= 8).astype(int)
    df['prev_exp']           = df['previous_counseling_experience']
    df['age_gap']            = (df['client_age'] - df['counselor_age']).abs()
    df['modality_issue_fit'] = df.apply(
        lambda r: max(
            MODALITY_ISSUE_FIT.get(r['client_issue'], {}).get(m.strip(), 0.5)
            for m in str(r['counselor_modality']).split(',')
        ), axis=1)
    return df[FEATURES]


def evaluate(pipeline, X_t, y_t):
    y_pred = pipeline.predict(X_t)
    y_prob = pipeline.predict_proba(X_t)[:, 1]
    return {
        "Accuracy": round(float(accuracy_score(y_t, y_pred)), 3),
        "F1":       round(float(f1_score(y_t, y_pred)), 3),
        "ROC-AUC":  round(float(roc_auc_score(y_t, y_prob)), 3),
    }, y_prob


print("Loading dataset...")
df_raw = pd.read_csv(BASE_DIR / "client_counselor_dataset.csv")
X = engineer_features(df_raw)
y = df_raw["match_success"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"Split: {len(X_train):,} train / {len(X_test):,} test")

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print("\nEvaluating baselines (LightGBM / CatBoost)...")
base_lgbm = joblib.load(BASE_DIR / "baseline_lgbm.pkl")
base_cat  = joblib.load(BASE_DIR / "baseline_cat.pkl")
scores_base_lgbm, _ = evaluate(base_lgbm, X_test, y_test)
scores_base_cat,  _ = evaluate(base_cat,  X_test, y_test)
print(f"  Baseline LightGBM : {scores_base_lgbm}")
print(f"  Baseline CatBoost : {scores_base_cat}")

# ── Tune LightGBM ──────────────────────────────────────────────────────────────
print("\nTuning LightGBM (n_iter=50)...")
lgbm_pipe = ImbPipeline([
    ("prep",  StandardScaler()),
    ("smote", SMOTE(random_state=42)),
    ("model", LGBMClassifier(random_state=42, verbose=-1)),
])
lgbm_params = {
    "model__n_estimators":      [100, 200, 300, 400, 500],
    "model__max_depth":         [3, 4, 5, 6, 7, 8],
    "model__learning_rate":     [0.01, 0.03, 0.05, 0.08, 0.1, 0.15, 0.2],
    "model__num_leaves":        [20, 31, 50, 70, 100],
    "model__subsample":         [0.6, 0.7, 0.8, 0.9, 1.0],
    "model__colsample_bytree":  [0.6, 0.7, 0.8, 0.9, 1.0],
    "model__min_child_samples": [5, 10, 20, 30, 50],
    "model__reg_alpha":         [0, 0.1, 0.5, 1.0],
    "model__reg_lambda":        [0.5, 1.0, 2.0, 3.0],
}
lgbm_search = RandomizedSearchCV(
    lgbm_pipe, lgbm_params, n_iter=50, scoring="roc_auc",
    cv=cv, random_state=42, n_jobs=-1, verbose=1,
)
lgbm_search.fit(X_train, y_train)
tuned_lgbm = lgbm_search.best_estimator_
scores_tuned_lgbm, _ = evaluate(tuned_lgbm, X_test, y_test)
print(f"  Best params : {lgbm_search.best_params_}")
print(f"  Tuned LightGBM : {scores_tuned_lgbm}")
joblib.dump(tuned_lgbm, BASE_DIR / "tuned_lgbm.pkl")
print("  Saved: tuned_lgbm.pkl")

# ── Tune CatBoost ──────────────────────────────────────────────────────────────
print("\nTuning CatBoost (n_iter=50)...")
cat_pipe = ImbPipeline([
    ("prep",  StandardScaler()),
    ("smote", SMOTE(random_state=42)),
    ("model", CatBoostClassifier(random_state=42, verbose=0)),
])
cat_params = {
    "model__iterations":        [100, 200, 300, 500],
    "model__depth":             [4, 5, 6, 7, 8],
    "model__learning_rate":     [0.01, 0.03, 0.05, 0.08, 0.1, 0.15],
    "model__l2_leaf_reg":       [1, 3, 5, 7, 10],
    "model__subsample":         [0.6, 0.7, 0.8, 0.9, 1.0],
    "model__colsample_bylevel": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    "model__min_data_in_leaf":  [1, 3, 5, 10, 20],
}
cat_search = RandomizedSearchCV(
    cat_pipe, cat_params, n_iter=50, scoring="roc_auc",
    cv=cv, random_state=42, n_jobs=-1, verbose=1,
)
cat_search.fit(X_train, y_train)
tuned_cat = cat_search.best_estimator_
scores_tuned_cat, _ = evaluate(tuned_cat, X_test, y_test)
print(f"  Best params : {cat_search.best_params_}")
print(f"  Tuned CatBoost : {scores_tuned_cat}")
joblib.dump(tuned_cat, BASE_DIR / "tuned_cat.pkl")
print("  Saved: tuned_cat.pkl")

# ── Save results CSV ───────────────────────────────────────────────────────────
rows = [
    {"Model": "Baseline LightGBM", **scores_base_lgbm},
    {"Model": "Baseline CatBoost", **scores_base_cat},
    {"Model": "Tuned LightGBM",    **scores_tuned_lgbm},
    {"Model": "Tuned CatBoost",    **scores_tuned_cat},
]
pd.DataFrame(rows).to_csv(BASE_DIR / "tuned_result.csv", index=False)
print("Saved: tuned_result.csv")

# ── Chart ──────────────────────────────────────────────────────────────────────
print("Generating chart...")
metrics = ["Accuracy", "F1", "ROC-AUC"]
plot_data = {
    "Baseline LightGBM": (scores_base_lgbm, "#C4B5FD"),
    "Baseline CatBoost": (scores_base_cat,  "#FCA5A5"),
    "Tuned LightGBM":    (scores_tuned_lgbm, "#7C3AED"),
    "Tuned CatBoost":    (scores_tuned_cat,  "#DC2626"),
}

x       = np.arange(len(metrics))
width   = 0.14
offsets = [-1.5, -0.5, 0.5, 1.5]

fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor("#FAFAF8")
ax.set_facecolor("#FAFAF8")

for (label, (scores, color)), offset in zip(plot_data.items(), offsets):
    vals  = [scores[m] for m in metrics]
    hatch = "//" if label == "Tuned LightGBM" else None
    bars  = ax.bar(x + offset * width, vals, width, label=label,
                   color=color, zorder=3, edgecolor="white", linewidth=0.5,
                   hatch=hatch)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
                f"{val:.3f}", ha="center", va="bottom",
                fontsize=7.5, fontweight="bold", color="#374151")

ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=13, fontweight="bold")
all_vals = [s[m] for _, (s, _) in plot_data.items() for m in metrics]
ax.set_ylim(max(0.0, min(all_vals) - 0.08), min(1.0, max(all_vals) + 0.09))
ax.set_ylabel("Score", fontsize=12)
ax.set_title(
    f"Baseline vs Tuned — LightGBM & CatBoost\n"
    f"Deployed: Tuned LightGBM  (ROC-AUC: {scores_tuned_lgbm['ROC-AUC']:.3f})  // = selected",
    fontsize=13, fontweight="bold", pad=14,
)
ax.legend(fontsize=8.5, framealpha=0.9, loc="lower right")
ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
ax.set_axisbelow(True)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig(BASE_DIR / "tuned_result.png", dpi=150,
            bbox_inches="tight", facecolor="#FAFAF8")
print("Saved: tuned_result.png")

print("\n" + "=" * 65)
print(f"{'Model':<30} {'Accuracy':>9} {'F1':>9} {'ROC-AUC':>9}")
print("-" * 65)
for row in rows:
    print(f"{row['Model']:<30} {row['Accuracy']:>9.3f} {row['F1']:>9.3f} {row['ROC-AUC']:>9.3f}")
print("=" * 65)
print("\nDONE")
