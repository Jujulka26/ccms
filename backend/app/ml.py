from pathlib import Path
from functools import lru_cache
import warnings
import numpy as np
import pandas as pd
import joblib

from db import MAX_CASELOAD  # single source of truth for the capacity cap

# Coarse availability blocks: a counselor's general working times. Used as a
# hard pre-filter in matching (like language), NOT a model feature, so it needs
# no retraining and is unrelated to booking.
TIME_BLOCKS = ["Weekday Morning", "Weekday Afternoon", "Weekday Evening", "Weekend"]

# app/ml.py is at backend/app/ml.py, so parent.parent.parent = ccms/
BASE_DIR = Path(__file__).parent.parent.parent / "ml"


ISSUE_SIMILARITY = {
    "Anxiety":    {"Anxiety": 1.0, "Stress": 0.7, "Trauma": 0.6, "Depression": 0.6},
    "Stress":     {"Stress": 1.0, "Anxiety": 0.7, "Trauma": 0.6, "Depression": 0.6},
    "Trauma":     {"Trauma": 1.0, "Stress": 0.6, "Anxiety": 0.6, "Depression": 0.6},
    "Depression": {"Depression": 1.0, "Anxiety": 0.6, "Stress": 0.6, "Trauma": 0.6},
}

MODALITY_ISSUE_FIT = {
    "Anxiety":    {"Cognitive": 1.0, "Behavioral": 0.9, "Humanistic": 0.2, "Psychodynamic": 0.3},
    "Depression": {"Cognitive": 1.0, "Behavioral": 0.8, "Humanistic": 0.7, "Psychodynamic": 0.9},
    "Stress":     {"Cognitive": 0.8, "Behavioral": 0.7, "Humanistic": 0.7, "Psychodynamic": 0.3},
    "Trauma":     {"Behavioral": 1.0, "Cognitive": 0.9, "Humanistic": 0.2, "Psychodynamic": 0.4},
}

FEATURE_ORDER = [
    "issue_match", "modality_issue_fit", "modality_match", "gender_match",
    "exp_issue_fit", "ethnicity_match", "prev_exp", "age_gap",
]


@lru_cache(maxsize=1)
def load_resources():
    model = joblib.load(str(BASE_DIR / "tuned_lgbm.pkl"))
    df_ref = pd.read_csv(str(BASE_DIR / "client_counselor_dataset.csv"))
    return model, df_ref


def _issue_match(client_issue: str, specialization: str) -> float:
    return ISSUE_SIMILARITY.get(client_issue, {}).get(specialization, 0.0)


def _modality_fit(client_issue: str, counselor_modality: str) -> float:
    mods = [m.strip() for m in str(counselor_modality).split(",") if m.strip()]
    return max(MODALITY_ISSUE_FIT.get(client_issue, {}).get(m, 0.5) for m in mods)


def _exp_issue_fit(exp_year) -> int:
    try:
        return 1 if float(exp_year) >= 8 else 0
    except (TypeError, ValueError):
        return 0


def _prev_exp_value(val) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def _exp_years_value(val) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def run_match(match_req, counselors: list[dict]) -> dict:
    client_age          = match_req.client_age
    client_issue        = match_req.client_issue
    client_ethnicity    = match_req.client_ethnicity
    prev_exp            = match_req.prev_exp
    preferred_language  = match_req.preferred_language
    preferred_modality  = match_req.preferred_modality
    preferred_c_gender  = match_req.preferred_c_gender
    preferred_time      = getattr(match_req, "preferred_time", "Any time") or "Any time"
    exclude_ids = set(getattr(match_req, "exclude_ids", []) or [])

    model, _ = load_resources()

    rows = []
    for c in counselors:
        if c.get("counselor_id") in exclude_ids:
            continue
        # caseload = open cases (pending + approved). A counselor leaves the pool
        # once committed to MAX_CASELOAD, so we never over-route applicants.
        if _prev_exp_value(c.get("caseload")) >= MAX_CASELOAD:
            continue
        counselor_languages  = [v.strip() for v in str(c.get("counselor_language", "")).split(",") if v.strip()]
        if preferred_language not in counselor_languages:
            continue
        # Availability filter (hard, like language). A counselor who hasn't
        # declared any availability is left in (benefit of the doubt); one who
        # has declared blocks must cover the client's chosen time.
        if preferred_time != "Any time":
            counselor_availability = [v.strip() for v in str(c.get("availability") or "").split(",") if v.strip()]
            if counselor_availability and preferred_time not in counselor_availability:
                continue
        counselor_modalities = [v.strip() for v in str(c.get("counselor_modality", "")).split(",") if v.strip()]
        exp_yrs = _exp_years_value(c.get("experience_years"))
        rows.append({
            "counselor_id":       c["counselor_id"],
            "issue_match":        _issue_match(client_issue, c.get("specialization", "")),
            "modality_issue_fit": _modality_fit(client_issue, c.get("counselor_modality", "")),
            "modality_match":     int(preferred_modality in counselor_modalities),
            "gender_match":       1 if preferred_c_gender == "No preference" else int(preferred_c_gender == c.get("gender", "")),
            "exp_issue_fit":      _exp_issue_fit(exp_yrs),
            "ethnicity_match":    int(client_ethnicity == c.get("ethnicity", "")),
            "prev_exp":           _prev_exp_value(prev_exp),
            "age_gap":            abs(float(client_age) - float(c.get("age", 0))),
        })

    if not rows:
        return {"error": f"No available counselors right now. They may be fully booked, or none currently support {preferred_language}. Please adjust your preferences or try again later."}

    df = pd.DataFrame(rows)
    X  = df[FEATURE_ORDER]

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="X does not have valid feature names")
        prob = model.predict_proba(X)[:, 1]

    prob = np.clip(prob, 1e-7, 1 - 1e-7)

    # Tier by issue-specialization fit, then let the model rank within each tier.
    # Exact-issue specialists sit in the top band, related issues in a clearly
    # lower band, weak or unrelated in the lowest. The bands do not overlap, so a
    # non-specialist can never outrank a specialist; the model probability only
    # positions counselors within their own band.
    im = df["issue_match"].to_numpy()
    lo = np.select([im >= 1.0, im >= 0.55], [70.0, 40.0], default=10.0)
    hi = np.select([im >= 1.0, im >= 0.55], [99.0, 65.0], default=38.0)
    df["compatibility"] = lo + (hi - lo) * prob

    ranked        = df.sort_values("compatibility", ascending=False)
    counselor_map = {c["counselor_id"]: c for c in counselors}

    def build_match(row) -> dict:
        c = counselor_map[row["counselor_id"]]
        return {
            "counselor_id":        int(c["counselor_id"]),
            "name":                c.get("name"),
            "age":                 int(c.get("age", 0)),
            "gender":              c.get("gender"),
            "ethnicity":           c.get("ethnicity"),
            "specialization":      c.get("specialization"),
            "counselor_language":  c.get("counselor_language"),
            "counselor_modality":  c.get("counselor_modality"),
            "experience_years":    int(c.get("experience_years", 0)),
            "caseload":            _prev_exp_value(c.get("caseload")),
            "availability":        c.get("availability"),
            "about_me":            c.get("about_me"),
            "expertise_tags":      c.get("expertise_tags"),
            "helpful_thought_1":   c.get("helpful_thought_1"),
            "helpful_thought_2":   c.get("helpful_thought_2"),
            "modality_desc":       c.get("modality_desc"),
            "image":               c.get("image"),
            "compatibility_score": float(row["compatibility"]),
            "issue_match":         float(row["issue_match"]),
            "modality_match":      int(row["modality_match"]),
            "gender_match":        int(row["gender_match"]),
            "ethnicity_match":     int(row["ethnicity_match"]),
            "features":            {f: float(row[f]) for f in FEATURE_ORDER},
        }

    best_row      = ranked.iloc[0]
    best_features = {f: float(best_row[f]) for f in FEATURE_ORDER}
    top_n         = min(5, len(ranked))
    matches       = [build_match(ranked.iloc[i]) for i in range(top_n)]

    return {
        "top_match":     matches[0],
        "second_match":  matches[1] if len(matches) > 1 else None,
        "matches":       matches,
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
        "preferred_time":             ["Any time"] + TIME_BLOCKS,
    }


def engineer_features_from_df(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        try:
            client_issue         = row.get("client_issue", "")
            preferred_modality   = row.get("preferred_modality", "")
            preferred_c_gender   = row.get("preferred_counselor_gender", "No preference")
            counselor_modalities = [v.strip() for v in str(row.get("counselor_modality", "")).split(",") if v.strip()]
            exp_yrs = _exp_years_value(row.get("experience_years", 0))
            rows.append({
                "issue_match":        _issue_match(client_issue, row.get("specialization", "")),
                "modality_issue_fit": _modality_fit(client_issue, row.get("counselor_modality", "")),
                "modality_match":     int(preferred_modality in counselor_modalities),
                "gender_match":       1 if preferred_c_gender == "No preference" else int(preferred_c_gender == row.get("counselor_gender", "")),
                "exp_issue_fit":      _exp_issue_fit(exp_yrs),
                "ethnicity_match":    int(row.get("client_ethnicity", "") == row.get("counselor_ethnicity", "")),
                "prev_exp":           _prev_exp_value(row.get("previous_counseling_experience", 0)),
                "age_gap":            abs(float(row.get("client_age", 0)) - float(row.get("counselor_age", 0))),
            })
        except Exception:
            continue
    return pd.DataFrame(rows)


_shap_explainer = None


def _get_shap_explainer():
    global _shap_explainer
    if _shap_explainer is None:
        import shap
        model, _ = load_resources()
        _shap_explainer = shap.TreeExplainer(model.named_steps["model"])
    return _shap_explainer


def compute_shap(features: dict) -> dict:
    try:
        import shap
    except ImportError:
        return {"error": "SHAP not installed.", "shap_values": [], "base_value": 0.0, "feature_names": [], "feature_values": []}

    try:
        model, _  = load_resources()
        explainer = _get_shap_explainer()

        feature_values = [features.get(f, 0.0) for f in FEATURE_ORDER]
        x_row     = pd.DataFrame([{f: features.get(f, 0.0) for f in FEATURE_ORDER}])
        x_scaled  = model.named_steps["prep"].transform(x_row[FEATURE_ORDER])
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
            "shap_values":    row_contrib,
            "base_value":     base_value,
            "feature_names":  list(FEATURE_ORDER),
            "feature_values": feature_values,
            "error":          None,
        }
    except Exception as exc:
        return {"error": str(exc), "shap_values": [], "base_value": 0.0, "feature_names": [], "feature_values": []}
