import sys
import warnings
import os
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import random
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

NUM_CLIENTS           = 900
NUM_COUNSELORS        = 180
COUNSELORS_PER_CLIENT = 60

GENDERS     = ["Male", "Female"]
ETHNICITIES = ["Malay", "Chinese", "Indian", "Other"]
LANGUAGES   = ["English", "Malay", "Mandarin", "Tamil"]
ISSUES      = ["Anxiety", "Depression", "Stress", "Trauma"]
MODALITIES  = ["CBT", "Humanistic", "Mindfulness", "REBT"]

ISSUE_SIMILARITY = {
    "Anxiety":    {"Anxiety": 1.0, "Stress": 0.7, "Trauma": 0.6, "Depression": 0.6},
    "Stress":     {"Stress":  1.0, "Anxiety": 0.7, "Trauma": 0.6, "Depression": 0.6},
    "Trauma":     {"Trauma":  1.0, "Stress":  0.6, "Anxiety": 0.6, "Depression": 0.6},
    "Depression": {"Depression": 1.0, "Anxiety": 0.6, "Stress": 0.6, "Trauma": 0.6},
}
MODALITY_ISSUE_FIT = {
    "Anxiety":    {"CBT": 1.0, "Mindfulness": 0.8, "REBT": 0.7, "Humanistic": 0.4},
    "Depression": {"CBT": 1.0, "Mindfulness": 0.8, "Humanistic": 0.7, "REBT": 0.6},
    "Stress":     {"Mindfulness": 1.0, "CBT": 0.7, "Humanistic": 0.7, "REBT": 0.5},
    "Trauma":     {"CBT": 1.0, "Humanistic": 0.5, "Mindfulness": 0.5, "REBT": 0.5},
}
EXP_BONUS = {"Trauma": 10, "Anxiety": 7, "Depression": 7, "Stress": 5}

FEATURES = [
    'issue_match', 'modality_issue_fit', 'modality_match', 'gender_match',
    'exp_issue_fit', 'ethnicity_match', 'prev_exp', 'age_gap',
]
FEATURE_LABELS = {
    'issue_match':       'Issue Similarity',
    'modality_match':    'Modality Match',
    'modality_issue_fit':'Issue-Modality Fit',
    'gender_match':      'Gender Match',
    'exp_issue_fit':     'Seniority',
    'ethnicity_match':   'Ethnicity Match',
    'prev_exp':          'Prev Experience',
    'age_gap':           'Age Gap',
}

ISSUE_COEFF = 35
S_MIN       = 33.3   # 35*0.6 + 3.6 + 1.5 + 1 + 1 + 0 + 13*0.4 + 0


def generate_experience_years(age):
    max_exp = max(1, age - 23)
    if max_exp < 8:
        return random.randint(1, max_exp)
    return random.randint(1, 7) if random.random() < 0.7 else random.randint(8, min(20, max_exp))


def generate_dataset(s_max):
    random.seed(42)
    np.random.seed(42)
    clients = []
    for i in range(NUM_CLIENTS):
        clients.append({
            "client_id": i,
            "client_age": random.randint(18, 65),
            "client_gender": random.choices(GENDERS, weights=[0.48, 0.52])[0],
            "client_ethnicity": random.choices(ETHNICITIES, weights=[0.6, 0.25, 0.1, 0.05])[0],
            "client_issue": random.choices(ISSUES, weights=[0.35, 0.3, 0.25, 0.1])[0],
            "previous_counseling_experience": np.random.choice([0, 1], p=[0.6, 0.4]),
            "preferred_language": random.choices(LANGUAGES, weights=[0.5, 0.3, 0.15, 0.05])[0],
            "preferred_modality": random.choices(MODALITIES, weights=[0.4, 0.25, 0.2, 0.15])[0],
            "preferred_counselor_gender": random.choice(["No preference", "Male", "Female"]),
        })
    counselors = []
    for i in range(NUM_COUNSELORS):
        age = random.randint(25, 65)
        exp = generate_experience_years(age)
        exp = min(exp, age - 23)
        exp = max(1, exp)
        counselors.append({
            "counselor_id": i,
            "counselor_age": age,
            "counselor_gender": random.choices(GENDERS, weights=[0.48, 0.52])[0],
            "counselor_ethnicity": random.choices(ETHNICITIES, weights=[0.6, 0.25, 0.1, 0.05])[0],
            "counselor_language": ", ".join(random.sample(LANGUAGES, k=random.choice([1, 2]))),
            "specialization": random.choices(ISSUES, weights=[0.35, 0.3, 0.25, 0.1])[0],
            "counselor_modality": random.choices(MODALITIES, weights=[0.4, 0.25, 0.2, 0.15])[0],
            "experience_years": exp,
        })
    rows = []
    for client in clients:
        for counselor in random.sample(counselors, COUNSELORS_PER_CLIENT):
            langs = counselor["counselor_language"].split(", ")
            if client["preferred_language"] not in langs:
                continue
            S   = 0
            sim = ISSUE_SIMILARITY[client["client_issue"]][counselor["specialization"]]
            S  += ISSUE_COEFF * sim
            modality_match = client["preferred_modality"] == counselor["counselor_modality"]
            S += (11 + sim) if modality_match else (3 + sim)
            if client["previous_counseling_experience"] == 1:
                S += 5.5 + 2 * int(modality_match)
            else:
                S += 1.5
            pref = client["preferred_counselor_gender"]
            S += 5 if (pref == "No preference" or pref == counselor["counselor_gender"]) else 1
            S += 4 if client["client_ethnicity"] == counselor["counselor_ethnicity"] else 1
            if counselor["experience_years"] >= 8:
                S += EXP_BONUS[client["client_issue"]]
            fit = MODALITY_ISSUE_FIT[client["client_issue"]][counselor["counselor_modality"]]
            S += 13 * fit
            age_gap = abs(client["client_age"] - counselor["counselor_age"])
            S += max(0, 20 - age_gap) * 0.10
            base_prob  = (S - S_MIN) / (s_max - S_MIN)
            base_prob += random.uniform(-0.05, 0.05)
            final_prob = max(0.0, min(1.0, base_prob))
            if final_prob > 0.50:
                match_success = 1
            elif final_prob < 0.22:
                match_success = 0
            else:
                match_success = np.random.binomial(1, final_prob)
            rows.append({**client, **counselor, "match_success": match_success})
    return pd.DataFrame(rows)


def engineer_features(df):
    df = df.copy()
    df['modality_match']     = (df['preferred_modality'] == df['counselor_modality']).astype(int)
    df['gender_match']       = ((df['preferred_counselor_gender'] == "No preference") |
                                (df['preferred_counselor_gender'] == df['counselor_gender'])).astype(int)
    df['ethnicity_match']    = (df['client_ethnicity'] == df['counselor_ethnicity']).astype(int)
    df['issue_match']        = df.apply(lambda r: ISSUE_SIMILARITY[r['client_issue']][r['specialization']], axis=1)
    df['exp_issue_fit']      = (df['experience_years'] >= 8).astype(int)
    df['prev_exp']           = df['previous_counseling_experience']
    df['age_gap']            = (df['client_age'] - df['counselor_age']).abs()
    df['modality_issue_fit'] = df.apply(
        lambda r: MODALITY_ISSUE_FIT.get(r['client_issue'], {}).get(
            str(r['counselor_modality']).split(',')[0].strip(), 0.5), axis=1)
    return df[FEATURES]


def train_and_eval(df):
    X = engineer_features(df)
    y = df['match_success'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    importances = {}
    metrics_out = {}
    for name, model in [
        ("LightGBM", LGBMClassifier(random_state=42, verbose=-1)),
        ("CatBoost", CatBoostClassifier(random_state=42, verbose=0)),
    ]:
        pipe = Pipeline([("prep", StandardScaler()), ("model", model)])
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        y_prob = pipe.predict_proba(X_test)[:, 1]
        metrics_out[name] = {
            "Acc": round(float(accuracy_score(y_test, y_pred)), 4),
            "F1":  round(float(f1_score(y_test, y_pred)), 4),
            "AUC": round(float(roc_auc_score(y_test, y_prob)), 4),
        }
        if name == "LightGBM":
            raw = pipe.named_steps["model"].booster_.feature_importance(importance_type="gain").astype(float)
        else:
            raw = pipe.named_steps["model"].get_feature_importance().astype(float)
        importances[name] = raw

    avg_imp = (importances["LightGBM"] / importances["LightGBM"].sum() +
               importances["CatBoost"] / importances["CatBoost"].sum()) / 2
    imp_dict = dict(zip(FEATURES, avg_imp))
    return metrics_out, round(float(y.mean()), 3), imp_dict


print(f"\ncoeff={ISSUE_COEFF}  S_MIN={S_MIN}  gender=5/1  trauma=10  prev_exp=5.5  modfit=13  |  sweep S_MAX 90 -> 82")

COL_W = 10
header_feats = "  ".join(f"{FEATURE_LABELS[f]:>{COL_W}}" for f in FEATURES)
print(f"\n{'S_MAX':>5} | {'Acc':>6} {'F1':>6} {'AUC':>6} {'Bal':>5} | {header_feats}")
print("-" * (5 + 3 + 6*3 + 5 + 3 + len(header_feats) + 4))

records = []
for s_max in range(90, 81, -1):
    df   = generate_dataset(s_max)
    mets, bal, imp = train_and_eval(df)

    avg_acc = round((mets["LightGBM"]["Acc"] + mets["CatBoost"]["Acc"]) / 2, 4)
    avg_f1  = round((mets["LightGBM"]["F1"]  + mets["CatBoost"]["F1"])  / 2, 4)
    avg_auc = round((mets["LightGBM"]["AUC"] + mets["CatBoost"]["AUC"]) / 2, 4)

    feat_vals = "  ".join(f"{imp[f]:>{COL_W}.3f}" for f in FEATURES)
    print(f"   {s_max:>3} | {avg_acc:.4f} {avg_f1:.4f} {avg_auc:.4f} {bal:.3f} | {feat_vals}")
    records.append({"S_MAX": s_max, "Acc": avg_acc, "F1": avg_f1, "AUC": avg_auc, "Balance": bal, **imp})

print()
df_r = pd.DataFrame(records).set_index("S_MAX")
desired = ['issue_match','modality_match','modality_issue_fit','exp_issue_fit','prev_exp','gender_match','ethnicity_match']

def dist_label(bal):
    if bal < 0.450: return "low match"
    if bal < 0.470: return "realistic"
    if bal < 0.490: return "slight lean"
    if bal < 0.510: return "~50/50"
    if bal < 0.530: return "slight lean"
    if bal < 0.550: return "match-heavy"
    return "too skewed"

print(f"\n{'S_MAX':>5} | {'Order':>5} | {'MM-MF':>6} | {'Sn-Pv':>6} | {'Gn-Et':>6} | {'Ac-F1':>6} | {'Match%':>6} | {'Distribution':>12} | Acc    F1    AUC")
print("-"*110)
for smax, row in df_r.iterrows():
    imp = row[FEATURES].to_dict()
    ranked = sorted(imp.items(), key=lambda x: -x[1])
    filtered = [r[0] for r in ranked if r[0] != 'age_gap']
    order_ok = filtered == desired
    mm_mf = imp['modality_match']    - imp['modality_issue_fit']
    sn_pv = imp['exp_issue_fit']     - imp['prev_exp']
    gn_et = imp['gender_match']      - imp['ethnicity_match']
    af    = row['Acc'] - row['F1']
    bal   = row['Balance']
    flag  = " <--" if (order_ok and row['Acc'] >= 0.795 and abs(af) < 0.020) else ""
    print(f"  {smax:>3} | {'YES' if order_ok else 'NO':>5} | {mm_mf:>+.3f} | {sn_pv:>+.3f} | {gn_et:>+.3f} | {af:>+.4f} | {bal*100:>5.1f}%  | {dist_label(bal):>12} | {row['Acc']:.4f} {row['F1']:.4f} {row['AUC']:.4f}{flag}")
