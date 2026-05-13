import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.base import clone
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

BASE_DIR = Path(__file__).parent

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

features = [
    'issue_score', 'modality_issue_fit', 'modality_match',
    'gender_match', 'exp_issue_weight', 'ethnicity_match', 'prev_exp', 'age_gap',
    'exp_years', 'client_age', 'counselor_age',
]

# ── Feature engineering ────────────────────────────────────────────────────────
def _exp_issue_weight(row):
    return 1 if float(row['experience_years']) >= 8 else 0

df = pd.read_csv(str(BASE_DIR / "client_counselor_dataset.csv"))

df['modality_match']     = (df['preferred_modality'] == df['counselor_modality']).astype(int)
df['gender_match']       = ((df['preferred_counselor_gender'] == "No preference") | (df['preferred_counselor_gender'] == df['counselor_gender'])).astype(int)
df['ethnicity_match']    = (df['client_ethnicity'] == df['counselor_ethnicity']).astype(int)
df['issue_score']        = df.apply(lambda r: ISSUE_SIMILARITY[r['client_issue']][r['specialization']], axis=1)
df['exact_spec_match']   = (df['client_issue'] == df['specialization']).astype(int)
df['prev_exp']           = df['previous_counseling_experience']
df['age_gap']            = abs(df['client_age'] - df['counselor_age'])
df['exp_issue_weight']   = df.apply(_exp_issue_weight, axis=1)
df['modality_issue_fit'] = df.apply(lambda r: MODALITY_ISSUE_FIT.get(r['client_issue'], {}).get(str(r['counselor_modality']).split(',')[0].strip(), 0.5), axis=1)

X = df[features]
y = df['match_success']

# ── Fixed train/test split ─────────────────────────────────────────────────────
X_train_full, X_test, y_train_full, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

# ── Models ─────────────────────────────────────────────────────────────────────
models = {
    "Random Forest":  RandomForestClassifier(n_estimators=100, random_state=42),
    "KNN":            KNeighborsClassifier(n_neighbors=5),
    "Neural Network": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42),
    "LightGBM":       LGBMClassifier(random_state=42, verbose=-1),
    "CatBoost":       CatBoostClassifier(random_state=42, verbose=0),
}

preprocessor = ColumnTransformer([('num', StandardScaler(), features)])

fractions  = [0.25, 0.50, 0.75, 1.00]
train_sizes = [int(len(X_train_full) * f) for f in fractions]

print(f"Test set fixed at {len(X_test):,} rows")
print(f"Training sizes: {train_sizes}\n")

# ── Run learning curve ─────────────────────────────────────────────────────────
results = []

for name, model in models.items():
    print(f"Running {name}...")
    for frac, size in zip(fractions, train_sizes):
        if frac == 1.0:
            X_sub, y_sub = X_train_full, y_train_full
        else:
            X_sub, _, y_sub, _ = train_test_split(
                X_train_full, y_train_full,
                train_size=size,
                random_state=42,
                stratify=y_train_full,
            )

        pipeline = ImbPipeline([
            ('prep',  clone(preprocessor)),
            ('smote', SMOTE(random_state=42)),
            ('model', clone(model)),
        ])
        pipeline.fit(X_sub, y_sub)

        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]

        results.append({
            "Model":    name,
            "Fraction": frac,
            "Size":     size,
            "Accuracy": round(float(accuracy_score(y_test, y_pred)), 3),
            "F1":       round(float(f1_score(y_test, y_pred)), 3),
            "ROC-AUC":  round(float(roc_auc_score(y_test, y_prob)), 3),
        })

results_df = pd.DataFrame(results)
results_df.to_csv(str(BASE_DIR / "learning_curve_results.csv"), index=False)
print("\nSaved: learning_curve_results.csv")

# ── Print table ────────────────────────────────────────────────────────────────
print("\n===== LEARNING CURVE RESULTS =====")
pivot = results_df.pivot_table(index='Model', columns='Fraction', values='F1')
print("\nF1 Score by Training Fraction:")
print(pivot.round(3).to_string())

# ── Plot ───────────────────────────────────────────────────────────────────────
metrics = ["Accuracy", "F1", "ROC-AUC"]
colors  = {
    "Random Forest":  "#F97316",
    "KNN":            "#EAB308",
    "Neural Network": "#22C55E",
    "LightGBM":       "#8B5CF6",
    "CatBoost":       "#EC4899",
}

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.patch.set_facecolor("#FAFAF8")

for ax, metric in zip(axes, metrics):
    ax.set_facecolor("#FAFAF8")
    for name in models:
        sub = results_df[results_df["Model"] == name].sort_values("Fraction")
        ax.plot(
            sub["Size"], sub[metric],
            marker="o", linewidth=2, markersize=5,
            label=name, color=colors[name],
        )
    ax.set_title(metric, fontsize=13, fontweight="bold")
    ax.set_xlabel("Training Size", fontsize=10)
    ax.set_ylabel("Score", fontsize=10)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.set_xticks(train_sizes)
    ax.set_xticklabels([f"{s:,}\n({int(f*100)}%)" for s, f in zip(train_sizes, fractions)], fontsize=8)

axes[0].legend(fontsize=8, framealpha=0.9)
fig.suptitle(
    "Learning Curves — All Models\nClient-Counselor Matching System",
    fontsize=14, fontweight="bold", y=1.02,
)

plt.tight_layout()
plt.savefig(str(BASE_DIR / "learning_curves.png"), dpi=150, bbox_inches="tight", facecolor="#FAFAF8")
print("Saved: learning_curves.png")
print("\nDONE")
