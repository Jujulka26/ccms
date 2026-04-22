import pandas as pd
import joblib

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer

from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier

# ============================================================
# 1. LOAD DATA
# ============================================================
df = pd.read_csv("client_counselor_dataset.csv")

# ============================================================
# 2. ISSUE SIMILARITY
# ============================================================
ISSUE_SIMILARITY = {
    "Anxiety": {"Anxiety": 1.0, "Stress": 0.7, "Trauma": 0.5, "Depression": 0.6},
    "Stress": {"Stress": 1.0, "Anxiety": 0.7, "Trauma": 0.6, "Depression": 0.5},
    "Trauma": {"Trauma": 1.0, "Stress": 0.6, "Anxiety": 0.5, "Depression": 0.4},
    "Depression": {"Depression": 1.0, "Anxiety": 0.6, "Stress": 0.5, "Trauma": 0.4}
}

# ============================================================
# 3. FEATURE ENGINEERING (same as your app)
# ============================================================
df['modality_match'] = (df['preferred_modality'] == df['counselor_modality']).astype(int)

df['gender_match'] = (
    (df['preferred_counselor_gender'] == "No preference") |
    (df['preferred_counselor_gender'] == df['counselor_gender'])
).astype(int)

df['ethnicity_match'] = (
    df['client_ethnicity'] == df['counselor_ethnicity']
).astype(int)

df['issue_score'] = df.apply(
    lambda row: ISSUE_SIMILARITY[row['client_issue']][row['specialization']],
    axis=1
)

df['prev_exp'] = df['previous_counseling_experience']
df['exp_years'] = df['experience_years']
df['age_gap'] = abs(df['client_age'] - df['counselor_age'])

# ============================================================
# 4. FEATURES
# ============================================================
features = [
    'issue_score',
    'modality_match',
    'gender_match',
    'ethnicity_match',
    'age_gap',
    'client_age',
    'counselor_age',
    'exp_years',
    'prev_exp'
]

X = df[features]
y = df['match_success']  # ⚠️ your target

# ============================================================
# 5. PREPROCESSING
# ============================================================
preprocessor = ColumnTransformer([
    ('num', StandardScaler(), features),
])

# ============================================================
# 6. SPLIT
# ============================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ============================================================
# 7. MODELS
# ============================================================
models = {
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "KNN": KNeighborsClassifier(n_neighbors=5),
    "Neural Network": MLPClassifier(hidden_layer_sizes=(64,32), max_iter=500, random_state=42),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
}

results = []

# ============================================================
# 8. TRAIN + EVALUATE
# ============================================================
for name, model in models.items():
    print(f"\nTraining {name}...")

    pipeline = ImbPipeline([
        ('prep', preprocessor),
        ('smote', SMOTE(random_state=42)),
        ('model', model)
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_prob)

    results.append({
        "Model": name,
        "Accuracy": round(acc, 3),
        "F1": round(f1, 3),
        "ROC-AUC": round(roc, 3)
    })

    # Save model
    joblib.dump(pipeline, f"{name}.pkl")

# ============================================================
# 9. SAVE RESULTS
# ============================================================
results_df = pd.DataFrame(results)
results_df.to_csv("model_results.csv", index=False)

print("\n===== FINAL RESULTS =====")
print(results_df)

corr = df[features + ['match_success']].corr()['match_success'].drop('match_success')
print("\n===== FEATURE CORRELATION WITH TARGET =====")
print(corr.sort_values(ascending=False))

print("\nDONE ✅")