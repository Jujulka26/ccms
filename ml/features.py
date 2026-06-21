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

FEATURE_ORDER = [
    "issue_match", "modality_issue_fit", "modality_match", "gender_match",
    "exp_issue_fit", "ethnicity_match", "prev_exp", "age_gap",
]
