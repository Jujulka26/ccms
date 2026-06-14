import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

BASE_DIR = Path(__file__).parent
df = pd.read_csv(BASE_DIR / "client_counselor_dataset.csv")

ISSUE_SIMILARITY = {
    "Anxiety":    {"Anxiety": 1.0, "Stress": 0.7, "Trauma": 0.6, "Depression": 0.8},
    "Stress":     {"Stress":  1.0, "Anxiety": 0.7, "Trauma": 0.6, "Depression": 0.7},
    "Trauma":     {"Trauma":  1.0, "Stress":  0.6, "Anxiety": 0.6, "Depression": 0.8},
    "Depression": {"Depression": 1.0, "Anxiety": 0.8, "Stress": 0.7, "Trauma": 0.8},
}

MODALITY_ISSUE_FIT = {
    "Anxiety":    {"Cognitive": 1.0, "Behavioral": 0.9, "Humanistic": 0.2, "Psychodynamic": 0.3},
    "Depression": {"Cognitive": 1.0, "Behavioral": 0.8, "Humanistic": 0.7, "Psychodynamic": 0.9},
    "Stress":     {"Cognitive": 0.8, "Behavioral": 0.7, "Humanistic": 0.7, "Psychodynamic": 0.3},
    "Trauma":     {"Behavioral": 1.0, "Cognitive": 0.9, "Humanistic": 0.2, "Psychodynamic": 0.4},
}

df['modality_match'] = df.apply(
    lambda row: int(row['preferred_modality'] in [m.strip() for m in str(row['counselor_modality']).split(',')]),
    axis=1
)
df['gender_match'] = (
    (df['preferred_counselor_gender'] == "No preference") |
    (df['preferred_counselor_gender'] == df['counselor_gender'])
).astype(int)
df['ethnicity_match'] = (df['client_ethnicity'] == df['counselor_ethnicity']).astype(int)
df['issue_match'] = df.apply(
    lambda row: ISSUE_SIMILARITY[row['client_issue']][row['specialization']], axis=1
)
df['exp_issue_fit'] = (df['experience_years'] >= 8).astype(int)
df['prev_exp'] = df['previous_counseling_experience']
df['age_gap'] = (df['client_age'] - df['counselor_age']).abs()
df['modality_issue_fit'] = df.apply(
    lambda row: max(
        MODALITY_ISSUE_FIT.get(row['client_issue'], {}).get(m.strip(), 0.5)
        for m in str(row['counselor_modality']).split(',')
    ),
    axis=1
)

features = [
    'issue_match', 'modality_issue_fit', 'modality_match', 'gender_match',
    'exp_issue_fit', 'ethnicity_match', 'prev_exp', 'age_gap',
]

X = df[features]
y = df['match_success']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

corr = df[features + ['match_success']].corr(numeric_only=True)['match_success'].drop('match_success')
print("\n===== FEATURE CORRELATION WITH TARGET =====")
print(corr.sort_values(ascending=False))

models = {
    "Random Forest":  RandomForestClassifier(n_estimators=100, random_state=42),
    "KNN":            KNeighborsClassifier(n_neighbors=5),
    "Neural Network": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42),
    "LightGBM":       LGBMClassifier(random_state=42, verbose=-1),
    "CatBoost":       CatBoostClassifier(random_state=42, verbose=0),
}

save_names = {
    "Random Forest":  "baseline_rf.pkl",
    "KNN":            "baseline_knn.pkl",
    "Neural Network": "baseline_nn.pkl",
    "LightGBM":       "baseline_lgbm.pkl",
    "CatBoost":       "baseline_cat.pkl",
}

results = []

for name, model in models.items():
    print(f"\nTraining {name}...")

    pipeline = ImbPipeline([
        ('prep',  StandardScaler()),
        ('smote', SMOTE(random_state=42)),
        ('model', model),
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    results.append({
        "Model":    name,
        "Accuracy": round(float(accuracy_score(y_test, y_pred)), 3),
        "F1":       round(float(f1_score(y_test, y_pred)), 3),
        "ROC-AUC":  round(float(roc_auc_score(y_test, y_prob)), 3),
    })

    joblib.dump(pipeline, BASE_DIR / save_names[name])
    print(f"  Saved: {save_names[name]}")

results_df = pd.DataFrame(results)
results_df.to_csv(BASE_DIR / "train_result.csv", index=False)

print("\n===== FINAL RESULTS =====")
print(results_df)

print("\nGenerating chart...")

model_names = results_df["Model"].tolist()
metrics     = ["Accuracy", "F1", "ROC-AUC"]
colors      = ["#6D28D9", "#7C3AED", "#A78BFA", "#F97316", "#10B981"]

x      = np.arange(len(metrics))
width  = 0.10
gap    = 0.01
n      = len(model_names)
starts = -(n - 1) / 2 * (width + gap)

fig, axes = plt.subplots(1, 2, figsize=(20, 7))
fig.patch.set_facecolor("#FAFAF8")

# Left: grouped bar chart
ax = axes[0]
ax.set_facecolor("#FAFAF8")

for i, (model, color) in enumerate(zip(model_names, colors)):
    offset = starts + i * (width + gap)
    vals   = [results_df.loc[results_df["Model"] == model, m].values[0] for m in metrics]
    bars   = ax.bar(x + offset, vals, width, color=color, label=model,
                    zorder=3, edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{val:.3f}", ha="center", va="bottom",
                fontsize=6.5, fontweight="bold", color="#374151")

ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=12, fontweight="bold")
all_vals = results_df[metrics].values.flatten()
ax.set_ylim(max(0.0, all_vals.min() - 0.08), min(1.0, all_vals.max() + 0.07))
ax.set_ylabel("Score", fontsize=11)
ax.set_title("Baseline Model Comparison\n(Accuracy · F1 · ROC-AUC)",
             fontsize=13, fontweight="bold", pad=12)
ax.legend(loc="lower right", framealpha=0.9, fontsize=8)
ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
ax.set_axisbelow(True)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

for m_idx, metric in enumerate(metrics):
    best_val   = results_df[metric].max()
    best_model = results_df.loc[results_df[metric].idxmax(), "Model"]
    m_i        = model_names.index(best_model)
    bar_x      = x[m_idx] + starts + m_i * (width + gap) + width / 2
    ax.text(bar_x, best_val + 0.022, "★", ha="center", va="bottom",
            fontsize=9, color="#F59E0B")

ax.text(0.98, 0.02, "★ = best in metric", transform=ax.transAxes,
        ha="right", va="bottom", fontsize=8, color="#6B7280")

# Right: summary table
ax2 = axes[1]
ax2.set_facecolor("#FAFAF8")
ax2.axis("off")

df_display = results_df.copy()
df_display["Overall"] = df_display[metrics].mean(axis=1).round(4)
df_display = df_display.sort_values("Overall", ascending=False).reset_index(drop=True)

col_labels = ["Model", "Accuracy", "F1", "ROC-AUC", "Overall"]
table_data = [
    [row["Model"], f"{row['Accuracy']:.3f}", f"{row['F1']:.3f}",
     f"{row['ROC-AUC']:.3f}", f"{row['Overall']:.4f}"]
    for _, row in df_display.iterrows()
]

tbl = ax2.table(cellText=table_data, colLabels=col_labels,
                cellLoc="center", loc="center", bbox=[0, 0.05, 1, 0.85])
tbl.auto_set_font_size(False)
tbl.set_fontsize(10)

for j in range(len(col_labels)):
    tbl[0, j].set_facecolor("#6D28D9")
    tbl[0, j].set_text_props(color="white", fontweight="bold")
    tbl[0, j].set_height(0.10)

row_colors = ["#EDE9FE", "#F5F3FF", "#FAF8FF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"]
for i, row_color in enumerate(row_colors[:len(table_data)]):
    for j in range(len(col_labels)):
        tbl[i + 1, j].set_facecolor(row_color)
        tbl[i + 1, j].set_height(0.09)
        if i == 0:
            tbl[i + 1, j].set_text_props(fontweight="bold")

metric_col_map = {"Accuracy": 1, "F1": 2, "ROC-AUC": 3, "Overall": 4}
for metric, col_idx in metric_col_map.items():
    best_row = df_display[metric].idxmax() + 1
    tbl[best_row, col_idx].set_text_props(color="#6D28D9", fontweight="bold")

ax2.set_title("Model Performance Summary\n(sorted by Overall score)",
              fontsize=13, fontweight="bold", pad=12)
ax2.text(0.5, 0.02, "Overall = mean(Accuracy, F1, ROC-AUC)  |  Purple = best in column",
         ha="center", va="center", transform=ax2.transAxes, fontsize=8.5, color="#6B7280")

plt.suptitle("Baseline Model Benchmark — Client-Counselor Matching System",
             fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig(BASE_DIR / "train_result.png", dpi=150, bbox_inches="tight", facecolor="#FAFAF8")
print("Saved: train_result.png")

print("\nDONE")
