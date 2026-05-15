from pathlib import Path
from functools import lru_cache
import numpy as np
import pandas as pd
import joblib

BASE_DIR = Path(__file__).parent.parent / "ml"

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

FEATURE_ORDER = [
    "issue_score", "modality_issue_fit", "modality_match", "gender_match",
    "exp_issue_weight", "ethnicity_match", "prev_exp", "age_gap",
    "counselor_age",
]


@lru_cache(maxsize=1)
def load_resources():
    # ensemble.pkl is a dict {"lgbm": pipeline, "cat": pipeline}
    ensemble = joblib.load(str(BASE_DIR / "ensemble.pkl"))
    df_ref = pd.read_csv(str(BASE_DIR / "client_counselor_dataset.csv"))
    return ensemble, df_ref


def _issue_score(client_issue: str, specialization: str) -> float:
    return ISSUE_SIMILARITY.get(client_issue, {}).get(specialization, 0.0)


def _modality_fit(client_issue: str, counselor_modality: str) -> float:
    primary = str(counselor_modality).split(",")[0].strip()
    return MODALITY_ISSUE_FIT.get(client_issue, {}).get(primary, 0.5)


def _exp_issue_weight(experience_years) -> int:
    try:
        return 1 if float(experience_years) >= 8 else 0
    except (TypeError, ValueError):
        return 0


def _prev_exp_value(val) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def _exp_years_value(val) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def run_match(match_req, counselors: list[dict]) -> dict:
    client_age        = match_req.client_age
    client_issue      = match_req.client_issue
    client_ethnicity  = match_req.client_ethnicity
    previous_exp      = match_req.previous_exp
    preferred_language  = match_req.preferred_language
    preferred_modality  = match_req.preferred_modality
    preferred_c_gender  = match_req.preferred_c_gender
    exclude_ids = set(getattr(match_req, "exclude_ids", []) or [])

    ensemble, _ = load_resources()

    rows = []
    for c in counselors:
        if c.get("counselor_id") in exclude_ids:
            continue
        counselor_languages = [v.strip() for v in str(c.get("counselor_language", "")).split(",") if v.strip()]
        if preferred_language not in counselor_languages:
            continue
        counselor_modalities = [v.strip() for v in str(c.get("counselor_modality", "")).split(",") if v.strip()]
        exp_yrs = _exp_years_value(c.get("experience_years"))
        rows.append({
            "counselor_id":      c["counselor_id"],
            "issue_score":       _issue_score(client_issue, c.get("specialization", "")),
            "modality_issue_fit": _modality_fit(client_issue, c.get("counselor_modality", "")),
            "modality_match":    int(preferred_modality in counselor_modalities),
            "gender_match":      1 if preferred_c_gender == "No preference" else int(preferred_c_gender == c.get("gender", "")),
            "exp_issue_weight":  _exp_issue_weight(exp_yrs),
            "ethnicity_match":   int(client_ethnicity == c.get("ethnicity", "")),
            "prev_exp":          _prev_exp_value(previous_exp),
            "age_gap":           abs(float(client_age) - float(c.get("age", 0))),
            "counselor_age":     float(c.get("age", 0)),
        })

    if not rows:
        return {"error": f"No counselors found who support {preferred_language}."}

    df = pd.DataFrame(rows)
    X = df[FEATURE_ORDER]

    # Soft-vote ensemble: average probabilities from LightGBM + CatBoost
    prob_lgbm = ensemble["lgbm"].predict_proba(X)[:, 1]
    prob_cat  = ensemble["cat"].predict_proba(X)[:, 1]
    avg = (prob_lgbm + prob_cat) / 2

    # Temperature scaling T=1.2: divide logits by T to spread high-confidence scores
    # without a hard ceiling. ECE stays at ~0.042 (well-calibrated).
    T = 1.5
    avg = np.clip(avg, 1e-7, 1 - 1e-7)
    logits = np.log(avg / (1 - avg))
    df["compatibility"] = (1 / (1 + np.exp(-logits / T))) * 100

    ranked = df.sort_values("compatibility", ascending=False)
    counselor_map = {c["counselor_id"]: c for c in counselors}

    def build_match(row) -> dict:
        c = counselor_map[row["counselor_id"]]
        return {
            "counselor_id":       int(c["counselor_id"]),
            "name":               c.get("name"),
            "age":                int(c.get("age", 0)),
            "gender":             c.get("gender"),
            "ethnicity":          c.get("ethnicity"),
            "specialization":     c.get("specialization"),
            "counselor_language": c.get("counselor_language"),
            "counselor_modality": c.get("counselor_modality"),
            "experience_years":   int(c.get("experience_years", 0)),
            "about_me":           c.get("about_me"),
            "expertise_tags":     c.get("expertise_tags"),
            "helpful_thought_1":  c.get("helpful_thought_1"),
            "helpful_thought_2":  c.get("helpful_thought_2"),
            "modality_desc":      c.get("modality_desc"),
            "image":              c.get("image"),
            "compatibility_score": float(row["compatibility"]),
            "issue_score":        float(row["issue_score"]),
            "modality_match":     int(row["modality_match"]),
            "gender_match":       int(row["gender_match"]),
            "ethnicity_match":    int(row["ethnicity_match"]),
            "features":           {f: float(row[f]) for f in FEATURE_ORDER},
        }

    best_row    = ranked.iloc[0]
    best_features = {f: float(best_row[f]) for f in FEATURE_ORDER}
    top_n       = min(5, len(ranked))
    matches     = [build_match(ranked.iloc[i]) for i in range(top_n)]

    return {
        "top_match":    matches[0],
        "second_match": matches[1] if len(matches) > 1 else None,
        "matches":      matches,
        "best_features": best_features,
    }


def get_reference_data() -> dict:
    _, df_ref = load_resources()

    def sorted_unique(col):
        return sorted([v for v in df_ref[col].dropna().unique().tolist() if str(v).strip()])

    return {
        "client_gender":              sorted_unique("client_gender"),
        "client_ethnicity":           sorted_unique("client_ethnicity"),
        "client_issue":               sorted_unique("client_issue"),
        "preferred_modality":         sorted_unique("preferred_modality"),
        "preferred_language":         sorted_unique("preferred_language"),
        "preferred_counselor_gender": sorted_unique("preferred_counselor_gender"),
    }


def engineer_features_from_df(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        try:
            client_issue       = row.get("client_issue", "")
            preferred_modality = row.get("preferred_modality", "")
            preferred_c_gender = row.get("preferred_counselor_gender", "No preference")
            counselor_modalities = [v.strip() for v in str(row.get("counselor_modality", "")).split(",") if v.strip()]
            exp_yrs = _exp_years_value(row.get("experience_years", 0))
            rows.append({
                "issue_score":        _issue_score(client_issue, row.get("specialization", "")),
                "modality_issue_fit": _modality_fit(client_issue, row.get("counselor_modality", "")),
                "modality_match":     int(preferred_modality in counselor_modalities),
                "gender_match":       1 if preferred_c_gender == "No preference" else int(preferred_c_gender == row.get("counselor_gender", "")),
                "exp_issue_weight":   _exp_issue_weight(exp_yrs),
                "ethnicity_match":    int(row.get("client_ethnicity", "") == row.get("counselor_ethnicity", "")),
                "prev_exp":           _prev_exp_value(row.get("previous_counseling_experience", 0)),
                "age_gap":            abs(float(row.get("client_age", 0)) - float(row.get("counselor_age", 0))),
                "counselor_age":      float(row.get("counselor_age", 0)),
            })
        except Exception:
            continue
    return pd.DataFrame(rows)


_shap_explainer = None


def _get_shap_explainer():
    global _shap_explainer
    if _shap_explainer is None:
        import shap
        ensemble, _ = load_resources()
        _shap_explainer = shap.TreeExplainer(ensemble["lgbm"].named_steps['model'])
    return _shap_explainer


def compute_shap(features: dict) -> dict:
    try:
        import shap
    except ImportError:
        return {"error": "SHAP not installed. Run: pip install shap", "shap_values": [], "base_value": 0.0, "feature_names": [], "feature_values": []}

    try:
        ensemble, _ = load_resources()
        explainer = _get_shap_explainer()

        feature_values = [features.get(f, 0.0) for f in FEATURE_ORDER]
        x_row = pd.DataFrame([{f: features.get(f, 0.0) for f in FEATURE_ORDER}])

        x_scaled = ensemble["lgbm"].named_steps['prep'].transform(x_row[FEATURE_ORDER])
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
            "shap_values":   row_contrib,
            "base_value":    base_value,
            "feature_names": list(FEATURE_ORDER),
            "feature_values": feature_values,
            "error": None,
        }
    except Exception as exc:
        return {"error": str(exc), "shap_values": [], "base_value": 0.0, "feature_names": [], "feature_values": []}
