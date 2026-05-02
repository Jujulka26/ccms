from pathlib import Path
from functools import lru_cache
from typing import Optional
import numpy as np
import pandas as pd
import joblib

BASE_DIR = Path(__file__).parent.parent

ISSUE_SIMILARITY = {
    "Anxiety":    {"Anxiety": 1.0, "Stress": 0.7, "Trauma": 0.5, "Depression": 0.6},
    "Stress":     {"Stress": 1.0, "Anxiety": 0.7, "Trauma": 0.6, "Depression": 0.5},
    "Trauma":     {"Trauma": 1.0, "Stress": 0.6, "Anxiety": 0.5, "Depression": 0.4},
    "Depression": {"Depression": 1.0, "Anxiety": 0.6, "Stress": 0.5, "Trauma": 0.4},
}

FEATURE_ORDER = [
    "issue_score", "modality_match", "gender_match", "ethnicity_match",
    "age_gap", "client_age", "counselor_age", "exp_years", "prev_exp",
]


@lru_cache(maxsize=1)
def load_resources():
    model = joblib.load(str(BASE_DIR / "best_xgb_model.pkl"))
    df_ref = pd.read_csv(str(BASE_DIR / "client_counselor_dataset.csv"))
    return model, df_ref


def _issue_score(client_issue: str, specialization: str) -> float:
    return ISSUE_SIMILARITY.get(client_issue, {}).get(specialization, 0.0)


def _prev_exp_value(val) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return 2.0


def _exp_years_value(val) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def run_match(match_req, counselors: list[dict]) -> dict:
    client_age = match_req.client_age
    client_issue = match_req.client_issue
    client_ethnicity = match_req.client_ethnicity
    previous_exp = match_req.previous_exp
    preferred_language = match_req.preferred_language
    preferred_modality = match_req.preferred_modality
    preferred_c_gender = match_req.preferred_c_gender

    model, _ = load_resources()

    rows = []
    for c in counselors:
        counselor_languages = [v.strip() for v in str(c.get("counselor_language", "")).split(",") if v.strip()]
        if preferred_language not in counselor_languages:
            continue
        counselor_modalities = [v.strip() for v in str(c.get("counselor_modality", "")).split(",") if v.strip()]
        rows.append({
            "counselor_id": c["counselor_id"],
            "issue_score": _issue_score(client_issue, c.get("specialization", "")),
            "modality_match": int(preferred_modality in counselor_modalities),
            "gender_match": 1 if preferred_c_gender == "No preference" else int(preferred_c_gender == c.get("gender", "")),
            "ethnicity_match": int(client_ethnicity == c.get("ethnicity", "")),
            "age_gap": abs(float(client_age) - float(c.get("age", 0))),
            "client_age": float(client_age),
            "counselor_age": float(c.get("age", 0)),
            "exp_years": _exp_years_value(c.get("experience_years")),
            "prev_exp": _prev_exp_value(previous_exp),
        })

    if not rows:
        return {"error": f"No counselors found who support {preferred_language}."}

    df = pd.DataFrame(rows)
    X = df[FEATURE_ORDER]
    df["compatibility"] = model.predict_proba(X)[:, 1] * 100
    ranked = df.sort_values("compatibility", ascending=False)

    counselor_map = {c["counselor_id"]: c for c in counselors}

    def build_match(row) -> dict:
        c = counselor_map[row["counselor_id"]]
        return {
            "counselor_id": int(c["counselor_id"]),
            "name": c.get("name"),
            "age": int(c.get("age", 0)),
            "gender": c.get("gender"),
            "ethnicity": c.get("ethnicity"),
            "specialization": c.get("specialization"),
            "counselor_language": c.get("counselor_language"),
            "counselor_modality": c.get("counselor_modality"),
            "experience_years": int(c.get("experience_years", 0)),
            "about_me": c.get("about_me"),
            "expertise_tags": c.get("expertise_tags"),
            "helpful_thought_1": c.get("helpful_thought_1"),
            "helpful_thought_2": c.get("helpful_thought_2"),
            "compatibility_score": float(row["compatibility"]),
            "issue_score": float(row["issue_score"]),
            "modality_match": int(row["modality_match"]),
            "gender_match": int(row["gender_match"]),
        }

    best_row = ranked.iloc[0]
    best_features = {f: float(best_row[f]) for f in FEATURE_ORDER}

    result = {
        "top_match": build_match(best_row),
        "best_features": best_features,
    }

    if len(ranked) > 1:
        result["second_match"] = build_match(ranked.iloc[1])

    return result


def get_reference_data() -> dict:
    _, df_ref = load_resources()

    def sorted_unique(col):
        return sorted([v for v in df_ref[col].dropna().unique().tolist() if str(v).strip()])

    return {
        "client_gender": sorted_unique("client_gender"),
        "client_ethnicity": sorted_unique("client_ethnicity"),
        "client_issue": sorted_unique("client_issue"),
        "preferred_modality": sorted_unique("preferred_modality"),
        "preferred_language": sorted_unique("preferred_language"),
        "preferred_counselor_gender": sorted_unique("preferred_counselor_gender"),
    }


def engineer_features_from_df(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        try:
            client_issue = row.get("client_issue", "")
            preferred_modality = row.get("preferred_modality", "")
            preferred_c_gender = row.get("preferred_counselor_gender", "No preference")
            counselor_modalities = [v.strip() for v in str(row.get("counselor_modality", "")).split(",") if v.strip()]
            rows.append({
                "issue_score": _issue_score(client_issue, row.get("specialization", "")),
                "modality_match": int(preferred_modality in counselor_modalities),
                "gender_match": 1 if preferred_c_gender == "No preference" else int(preferred_c_gender == row.get("counselor_gender", "")),
                "ethnicity_match": int(row.get("client_ethnicity", "") == row.get("counselor_ethnicity", "")),
                "age_gap": abs(float(row.get("client_age", 0)) - float(row.get("counselor_age", 0))),
                "client_age": float(row.get("client_age", 0)),
                "counselor_age": float(row.get("counselor_age", 0)),
                "exp_years": _exp_years_value(row.get("experience_years", 0)),
                "prev_exp": _prev_exp_value(row.get("previous_counseling_experience", 2.0)),
            })
        except Exception:
            continue
    return pd.DataFrame(rows)


_shap_explainer = None


def _get_shap_explainer():
    global _shap_explainer
    if _shap_explainer is None:
        import shap
        pipeline, _ = load_resources()
        _shap_explainer = shap.TreeExplainer(pipeline.named_steps['model'])
    return _shap_explainer


def compute_shap(features: dict) -> dict:
    try:
        import shap
    except ImportError:
        return {"error": "SHAP is not installed. Run: pip install shap", "shap_values": [], "base_value": 0.0, "feature_names": [], "feature_values": []}

    try:
        pipeline, _ = load_resources()
        explainer = _get_shap_explainer()

        feature_values = [features.get(f, 0.0) for f in FEATURE_ORDER]
        x_row = pd.DataFrame([{f: features.get(f, 0.0) for f in FEATURE_ORDER}])

        # Scale features the same way the model was trained
        x_scaled = pipeline.named_steps['prep'].transform(x_row[FEATURE_ORDER])
        shap_vals = explainer.shap_values(x_scaled)

        if isinstance(shap_vals, list):
            row_contrib = np.array(shap_vals[1]).flatten().tolist()
        else:
            row_contrib = np.array(shap_vals).flatten().tolist()

        expected = explainer.expected_value
        if isinstance(expected, (list, np.ndarray)):
            base_value = float(np.array(expected).flat[-1])
        else:
            base_value = float(expected)

        return {
            "shap_values": row_contrib,
            "base_value": base_value,
            "feature_names": list(FEATURE_ORDER),
            "feature_values": feature_values,
            "error": None,
        }
    except Exception as exc:
        return {"error": str(exc), "shap_values": [], "base_value": 0.0, "feature_names": [], "feature_values": []}
