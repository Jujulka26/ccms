import pandas as pd
import joblib

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

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
# 3. FEATURE ENGINEERING
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
y = df['match_success']

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
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ============================================================
# 7. PIPELINE
# ============================================================
rf = RandomForestClassifier(random_state=42)

pipeline = ImbPipeline([
    ('prep', preprocessor),
    ('smote', SMOTE(random_state=42)),
    ('model', rf)
])

# ============================================================
# 8. PARAMETER GRID
# ============================================================
param_grid = {
    'model__n_estimators': [100, 200, 300],
    'model__max_depth': [None, 10, 20],
    'model__min_samples_split': [2, 5, 10],
    'model__min_samples_leaf': [1, 2, 4],
    'model__max_features': ['sqrt', 'log2']
}

# ============================================================
# 9. GRID SEARCH
# ============================================================
grid = GridSearchCV(
    pipeline,
    param_grid,
    cv=3,
    scoring='f1',
    n_jobs=-1,
    verbose=1
)

print("🔍 Tuning Random Forest...")
grid.fit(X_train, y_train)

# ============================================================
# 10. BEST MODEL
# ============================================================
best_model = grid.best_estimator_

print("\n🔥 Best Parameters:")
print(grid.best_params_)

# ============================================================
# 11. EVALUATION
# ============================================================
y_pred = best_model.predict(X_test)
y_prob = best_model.predict_proba(X_test)[:, 1]

print("\n===== TUNED RANDOM FOREST =====")
print("Accuracy:", round(accuracy_score(y_test, y_pred), 3))
print("F1:", round(f1_score(y_test, y_pred), 3))
print("ROC-AUC:", round(roc_auc_score(y_test, y_prob), 3))

# ============================================================
# 12. SAVE MODEL
# ============================================================
joblib.dump(best_model, "best_rf_model.pkl")
print("\n✅ Model saved as best_rf_model.pkl")