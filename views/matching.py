import base64
import os
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import time

from utils.db import load_counselors
from utils.model import load_resources
from utils.ui import render_hero, open_card, close_card

# ── Custom CSS ────────────────────────────────────────────────────────────────
def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

        /* ── Base reset ───────────────────────────────────────────────── */
        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        .stApp {
            background: #F7F5F0;
        }

        /* ── Hero section ─────────────────────────────────────────────── */
        .hero-wrap {
            background: #1A1A2E;
            border-radius: 20px;
            padding: 56px 52px 48px;
            margin-bottom: 32px;
            position: relative;
            overflow: hidden;
        }
        .hero-wrap::before {
            content: '';
            position: absolute;
            top: -80px; right: -80px;
            width: 320px; height: 320px;
            background: radial-gradient(circle, rgba(139,92,246,0.18) 0%, transparent 70%);
            pointer-events: none;
        }
        .hero-wrap::after {
            content: '';
            position: absolute;
            bottom: -60px; left: 40px;
            width: 220px; height: 220px;
            background: radial-gradient(circle, rgba(16,185,129,0.12) 0%, transparent 70%);
            pointer-events: none;
        }
        .hero-eyebrow {
            display: inline-block;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #A78BFA;
            background: rgba(167,139,250,0.12);
            border: 1px solid rgba(167,139,250,0.25);
            border-radius: 20px;
            padding: 4px 14px;
            margin-bottom: 20px;
        }
        .hero-title {
            font-family: 'DM Serif Display', serif;
            font-size: 42px;
            line-height: 1.15;
            color: #FFFFFF;
            margin: 0 0 16px;
            letter-spacing: -0.5px;
        }
        .hero-subtitle {
            font-size: 16px;
            color: rgba(255,255,255,0.55);
            max-width: 480px;
            line-height: 1.65;
            margin: 0;
        }
        .hero-stats {
            position: relative;
            z-index: 2; /* Float above the image background */
            display: flex;
            gap: 40px;
            margin-top: 40px;
            padding-top: 32px;
            border-top: 1px solid rgba(255,255,255,0.08);
        }
        .hero-stat-num {
            font-family: 'DM Serif Display', serif;
            font-size: 28px;
            color: #FFFFFF;
            line-height: 1;
        }
        .hero-stat-label {
            font-size: 12px;
            color: rgba(255,255,255,0.4);
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        /* ── Hero image blend ─────────────────────────────────────────── */
        .hero-content {
            display: flex;
            align-items: center;
            position: relative;
            z-index: 2;
        }
        .hero-text { 
            flex: 1; 
            min-width: 0; 
            max-width: 60%; /* Prevent text from overlapping the image */
        }
        .hero-image-wrap {
            position: absolute;
            bottom: -48px; /* Anchor it to the bottom of the hero wrap */
            right: -20px;
            width: 50%; /* Let it take up the right half */
            height: 130%; /* Give it plenty of height */
            pointer-events: none; /* Make sure it doesn't block clicks */
            z-index: 1;
        }
        .hero-img {
            width: 100%;
            height: 100%;
            object-fit: contain;
            object-position: right center;
            opacity: 0.85; /* Make it brighter and clearer */
            mix-blend-mode: lighten;
            -webkit-mask-image: linear-gradient(
                to right,
                transparent 0%,
                rgba(0,0,0,0.5) 30%,
                black 60%
            );
            mask-image: linear-gradient(
                to right,
                transparent 0%,
                rgba(0,0,0,0.5) 30%,
                black 60%
            );
        }

        /* ── Form card ────────────────────────────────────────────────── */
        .form-card {
            background: #FFFFFF;
            border-radius: 20px;
            padding: 36px 40px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            margin-bottom: 24px;
        }
        .section-label {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #8B5CF6;
            margin: 0 0 20px;
        }
        .section-divider {
            border: none;
            border-top: 1px solid #F0EDE8;
            margin: 28px 0;
        }

        /* ── Streamlit input overrides ────────────────────────────────── */
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] > div > div {
            border-radius: 10px !important;
            border: 1.5px solid #E5E2DC !important;
            background: #FAFAF8 !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 14px !important;
            transition: border-color 0.2s;
        }
        div[data-testid="stNumberInput"] input:focus,
        div[data-testid="stSelectbox"] > div > div:focus-within {
            border-color: #8B5CF6 !important;
            box-shadow: 0 0 0 3px rgba(139,92,246,0.1) !important;
        }
        label[data-testid="stWidgetLabel"] p {
            font-size: 15px !important;
            font-weight: 600 !important;
            color: #1A1A2E !important;
            margin-bottom: 10px !important;
        }

        /* ── Radio pill buttons (main content only, not sidebar) ─────── */
        [data-testid="block-container"] [data-baseweb="radio"] > div:first-child {
            display: none !important;
        }
        [data-testid="block-container"] [data-baseweb="radio"] {
            padding: 9px 22px !important;
            background: #F7F5F0 !important;
            border: 1.5px solid #E5E2DC !important;
            border-radius: 30px !important;
            cursor: pointer !important;
            transition: background 0.18s ease, border-color 0.18s ease !important;
            margin-right: 2px !important;
        }
        [data-testid="block-container"] [data-baseweb="radio"]:hover {
            border-color: #8B5CF6 !important;
            background: rgba(139,92,246,0.06) !important;
        }
        [data-testid="block-container"] [data-baseweb="radio"]:has(input:checked) {
            background: rgba(139,92,246,0.12) !important;
            border-color: #8B5CF6 !important;
        }
        [data-testid="block-container"] [data-baseweb="radio"]:has(input:checked) p {
            color: #6D28D9 !important;
            font-weight: 700 !important;
        }
        [data-testid="block-container"] [data-baseweb="radio"] p {
            font-size: 14px !important;
            margin: 0 !important;
            color: #4A4A5A !important;
            font-weight: 500 !important;
        }

        /* ── Submit button ────────────────────────────────────────────── */
        div[data-testid="stButton"] button {
            border-radius: 12px !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            padding: 10px 24px !important;
            transition: all 0.2s;
        }
        div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(124,58,237,0.35);
        }
        div[data-testid="stButton"] button[kind="primary"]:hover {
            box-shadow: 0 6px 20px rgba(124,58,237,0.45) !important;
            transform: translateY(-1px);
        }

        /* ── Result cards ─────────────────────────────────────────────── */
        .result-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 28px;
        }
        .result-card {
            background: #FFFFFF;
            border-radius: 20px;
            padding: 28px;
            border: 1px solid rgba(0,0,0,0.06);
        }
        .result-card.primary {
            background: #1A1A2E;
            border-color: transparent;
        }
        .result-card-badge {
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            border-radius: 20px;
            padding: 3px 10px;
            display: inline-block;
            margin-bottom: 18px;
        }
        .badge-primary { background: rgba(139,92,246,0.2); color: #A78BFA; }
        .badge-secondary { background: #F0EDE8; color: #8B8B9A; }

        .compat-score {
            font-family: 'DM Serif Display', serif;
            font-size: 52px;
            line-height: 1;
            color: #FFFFFF;
            margin-bottom: 4px;
        }
        .compat-score-secondary {
            font-family: 'DM Serif Display', serif;
            font-size: 52px;
            line-height: 1;
            color: #1A1A2E;
            margin-bottom: 4px;
        }
        .compat-label {
            font-size: 12px;
            color: rgba(255,255,255,0.45);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 24px;
        }
        .compat-label-secondary {
            font-size: 12px;
            color: #A0A0B0;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 24px;
        }
        .counselor-name {
            font-size: 20px;
            font-weight: 600;
            color: #FFFFFF;
            margin-bottom: 16px;
        }
        .counselor-name-secondary {
            font-size: 20px;
            font-weight: 600;
            color: #1A1A2E;
            margin-bottom: 16px;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.07);
        }
        .info-row-secondary {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #F0EDE8;
        }
        .info-key { font-size: 12px; color: rgba(255,255,255,0.4); }
        .info-key-secondary { font-size: 12px; color: #A0A0B0; }
        .info-val { font-size: 13px; color: rgba(255,255,255,0.85); font-weight: 500; }
        .info-val-secondary { font-size: 13px; color: #2D2D3F; font-weight: 500; }

        /* ── Explanation card ─────────────────────────────────────────── */
        .explain-card {
            background: #FFFFFF;
            border-radius: 20px;
            padding: 32px 36px;
            border: 1px solid rgba(0,0,0,0.06);
            margin-bottom: 24px;
        }
        .explain-title {
            font-family: 'DM Serif Display', serif;
            font-size: 22px;
            color: #1A1A2E;
            margin: 0 0 24px;
        }
        .point-row {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 11px 0;
            border-bottom: 1px solid #F5F3EF;
            font-size: 14px;
        }
        .dot-green {
            width: 8px; height: 8px;
            background: #10B981;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .dot-amber {
            width: 8px; height: 8px;
            background: #F59E0B;
            border-radius: 50%;
            flex-shrink: 0;
        }

        /* ── Table ────────────────────────────────────────────────────── */
        .ranking-card {
            background: #FFFFFF;
            border-radius: 20px;
            padding: 28px 32px;
            border: 1px solid rgba(0,0,0,0.06);
        }
        .ranking-card-title {
            font-family: 'DM Serif Display', serif;
            font-size: 20px;
            color: #1A1A2E;
            margin: 0 0 20px;
        }

        /* ── Tab overrides ────────────────────────────────────────────── */
        div[data-testid="stTabs"] button {
            font-family: 'DM Sans', sans-serif !important;
            font-size: 14px !important;
            font-weight: 500 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ── Domain helpers (unchanged logic) ─────────────────────────────────────────
ISSUE_SIMILARITY = {
    "Anxiety": {"Anxiety": 1.0, "Stress": 0.7, "Trauma": 0.5, "Depression": 0.6},
    "Stress": {"Stress": 1.0, "Anxiety": 0.7, "Trauma": 0.6, "Depression": 0.5},
    "Trauma": {"Trauma": 1.0, "Stress": 0.6, "Anxiety": 0.5, "Depression": 0.4},
    "Depression": {"Depression": 1.0, "Anxiety": 0.6, "Stress": 0.5, "Trauma": 0.4},
}

def issue_similarity_score(client_issue, counselor_specialization):
    return ISSUE_SIMILARITY.get(client_issue, {}).get(counselor_specialization, 0.0)

def previous_experience_value(previous_exp):
    try:
        return float(previous_exp)
    except (TypeError, ValueError):
        return 2.0

def experience_years_value(counselor):
    raw_years = counselor.get("experience_years")
    try:
        return float(raw_years)
    except (TypeError, ValueError):
        return 0.0

def engineer_features_from_df(df):
    rows = []
    for _, row in df.iterrows():
        try:
            client_age = float(row.get("client_age", 0))
            client_issue = row.get("client_issue", "")
            previous_exp = row.get("previous_counseling_experience", 2.0)
            preferred_modality = row.get("preferred_modality", "")
            preferred_c_gender = row.get("preferred_counselor_gender", "No preference")
            counselor_age = float(row.get("counselor_age", 0))
            counselor_gender = row.get("counselor_gender", "")
            counselor_ethnicity = row.get("counselor_ethnicity", "")
            client_ethnicity = row.get("client_ethnicity", "")
            counselor_modalities = [v.strip() for v in str(row.get("counselor_modality", "")).split(",") if v.strip()]
            exp_years = experience_years_value({"experience_years": row.get("experience_years", 0.0)})
            specialization = row.get("specialization", "")
            rows.append({
                "issue_score": issue_similarity_score(client_issue, specialization),
                "modality_match": int(preferred_modality in counselor_modalities),
                "gender_match": 1 if preferred_c_gender == "No preference" else int(preferred_c_gender == counselor_gender),
                "ethnicity_match": int(client_ethnicity == counselor_ethnicity),
                "age_gap": abs(client_age - counselor_age),
                "client_age": client_age,
                "counselor_age": counselor_age,
                "exp_years": exp_years,
                "prev_exp": previous_experience_value(previous_exp),
            })
        except Exception:
            continue
    return pd.DataFrame(rows)

def get_shap_contributions(model_pipeline, background_data, x_row, feature_names):
    try:
        import shap
    except ImportError:
        return None, None, None, "SHAP is not installed. Run: pip install shap"
    try:
        background_df = background_data[feature_names].copy() if isinstance(background_data, pd.DataFrame) else pd.DataFrame(background_data, columns=feature_names)
        if len(background_df) < 10:
            return None, None, None, "Insufficient background data for SHAP explanation (need at least 10 samples)"
        if len(background_df) > 100:
            background_df = background_df.sample(100, random_state=42)

        def predict_positive_class(data):
            data_df = pd.DataFrame(data, columns=feature_names)
            return model_pipeline.predict_proba(data_df)[:, 1]

        explainer = shap.KernelExplainer(predict_positive_class, background_df.values, link="identity")
        shap_values = explainer.shap_values(x_row[feature_names].values, nsamples=200)
        if isinstance(shap_values, list):
            row_contrib = np.array(shap_values[0])
        elif isinstance(shap_values, np.ndarray):
            row_contrib = shap_values[0] if shap_values.ndim == 2 else shap_values
        else:
            row_contrib = np.array(shap_values)
        expected = explainer.expected_value
        if isinstance(expected, list):
            base_value = float(expected[0])
        elif isinstance(expected, np.ndarray):
            base_value = float(expected[0]) if expected.size > 0 else 0.0
        else:
            base_value = float(expected)
        shap_df = pd.DataFrame({"feature": feature_names, "shap_value": row_contrib})
        shap_df["abs_shap"] = shap_df["shap_value"].abs()
        shap_df = shap_df.sort_values("abs_shap", ascending=False)
        return shap_df, row_contrib, base_value, None
    except Exception as exc:
        return None, None, None, f"Unable to generate SHAP explanation: {exc}"

def sorted_options(series):
    return sorted([value for value in series.dropna().unique().tolist() if str(value).strip()])

def modality_help_text(modality_options):
    descriptions = {
        "CBT": "Helps you change negative thoughts and behaviors.",
        "Humanistic": "Focuses on understanding your feelings in a supportive, non-judgmental way.",
        "Mindfulness": "Teaches you to stay calm and aware in the present moment.",
        "REBT": "Helps you challenge unhealthy beliefs and think more positively."
    }
    if not modality_options:
        return "Modality is the counseling approach used in sessions."
    parts = [f"- {m}: {descriptions.get(str(m), 'approach used in counseling sessions')}" for m in modality_options]
    return "Modality is the counseling approach/style:\n\n" + "\n".join(parts)

def render_step_progress(step: int, total: int = 3):
    step_names = ["About You", "Your Needs", "Preferences"]
    pct = int(step / total * 100)
    dots = ""
    for i, name in enumerate(step_names, 1):
        if i < step:
            dot_color, text_color, weight = "#6D28D9", "#6D28D9", "500"
        elif i == step:
            dot_color, text_color, weight = "#8B5CF6", "#8B5CF6", "700"
        else:
            dot_color, text_color, weight = "#DDD8D0", "#C0BAB4", "400"
        dots += (
            f'<div style="flex:1;display:flex;align-items:center;gap:6px;">'
            f'<div style="width:7px;height:7px;border-radius:50%;background:{dot_color};flex-shrink:0;"></div>'
            f'<span style="font-size:11px;color:{text_color};font-weight:{weight};">{name}</span>'
            f'</div>'
        )
    st.markdown(
        f"""
        <div style="margin-bottom: 28px;">
            <div style="background:#EDE8E3;border-radius:99px;height:5px;overflow:hidden;margin-bottom:10px;">
                <div style="background:linear-gradient(90deg,#8B5CF6,#6D28D9);width:{pct}%;height:5px;border-radius:99px;"></div>
            </div>
            <div style="display:flex;">{dots}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def scroll_to_results(anchor_id="match-results-anchor"):
    components.html(
        f"""
        <script>
        const anchor = window.parent.document.getElementById("{anchor_id}");
        if (anchor) {{
            anchor.scrollIntoView({{ behavior: "smooth", block: "start" }});
        }}
        </script>
        """,
        height=0, width=0,
    )

def render_hero_new():
    img_tag = ""
    try:
        with open(os.path.join("assets", "2.png"), "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        img_tag = f'<img src="data:image/png;base64,{b64}" class="hero-img" alt="" />'
    except FileNotFoundError:
        pass

    st.markdown(
        f"""
        <div class="hero-wrap">
            <div class="hero-content">
                <div class="hero-text">
                    <div class="hero-eyebrow">AI-Powered Matching</div>
                    <h1 class="hero-title">Find Your<br><em>Ideal Counselor</em></h1>
                    <p class="hero-subtitle">
                        Our model analyses compatibility across specialization, language,
                        modality and personal fit — ranked by predicted outcome.
                    </p>
                </div>
                <div class="hero-image-wrap">{img_tag}</div>
            </div>
            <div class="hero-stats">
                <div>
                    <div class="hero-stat-num">9</div>
                    <div class="hero-stat-label">Match factors</div>
                </div>
                <div>
                    <div class="hero-stat-num">ML</div>
                    <div class="hero-stat-label">Powered</div>
                </div>
                <div>
                    <div class="hero-stat-num">SHAP</div>
                    <div class="hero-stat-label">Explainability</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_counselor_card(counselor_row, score, is_primary=True):
    c = counselor_row
    langs = c.get("counselor_language", "—")
    mods = c.get("counselor_modality", "—")

    if is_primary:
        st.markdown(
            f"""
            <div class="result-card primary">
                <span class="result-card-badge badge-primary">Top Match</span>
                <div class="compat-score">{score:.1f}%</div>
                <div class="compat-label">Compatibility score</div>
                <div class="counselor-name">{c['name']}</div>
                <div class="info-row"><span class="info-key">Age</span><span class="info-val">{c['age']}</span></div>
                <div class="info-row"><span class="info-key">Gender</span><span class="info-val">{c['gender']}</span></div>
                <div class="info-row"><span class="info-key">Specialization</span><span class="info-val">{c['specialization']}</span></div>
                <div class="info-row"><span class="info-key">Experience</span><span class="info-val">{c['experience_years']} yrs</span></div>
                <div class="info-row"><span class="info-key">Language</span><span class="info-val">{langs}</span></div>
                <div class="info-row" style="border:none"><span class="info-key">Modality</span><span class="info-val">{mods}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="result-card">
                <span class="result-card-badge badge-secondary">2nd Option</span>
                <div class="compat-score-secondary">{score:.1f}%</div>
                <div class="compat-label-secondary">Compatibility score</div>
                <div class="counselor-name-secondary">{c['name']}</div>
                <div class="info-row-secondary"><span class="info-key-secondary">Age</span><span class="info-val-secondary">{c['age']}</span></div>
                <div class="info-row-secondary"><span class="info-key-secondary">Gender</span><span class="info-val-secondary">{c['gender']}</span></div>
                <div class="info-row-secondary"><span class="info-key-secondary">Specialization</span><span class="info-val-secondary">{c['specialization']}</span></div>
                <div class="info-row-secondary"><span class="info-key-secondary">Experience</span><span class="info-val-secondary">{c['experience_years']} yrs</span></div>
                <div class="info-row-secondary"><span class="info-key-secondary">Language</span><span class="info-val-secondary">{langs}</span></div>
                <div class="info-row-secondary" style="border:none"><span class="info-key-secondary">Modality</span><span class="info-val-secondary">{mods}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Main page ─────────────────────────────────────────────────────────────────
def show_matching_page():
    inject_styles()

    model, df_ref = load_resources()
    counselors = load_counselors()

    # Initialize the quiz step if it doesn't exist in session state
    if "quiz_step" not in st.session_state:
        st.session_state.quiz_step = 0

    render_hero_new()

    st.markdown('<div class="form-card">', unsafe_allow_html=True)

    # ── WIZARD STEP 0: Welcome ──────────────────────────────────────────────────
    if st.session_state.quiz_step == 0:
        st.markdown("<h3 style='color: #1A1A2E; text-align: center; margin-bottom: 10px; font-family: \"DM Serif Display\", serif;'>Let's find someone who truly gets you.</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #5A5A6E; margin-bottom: 30px;'>Take a short, guided questionnaire so we can match you with the right counselor based on your unique needs and preferences.</p>", unsafe_allow_html=True)
        
        _, col_btn, _ = st.columns([1, 2, 1])
        if col_btn.button("Begin Questionnaire", use_container_width=True, type="primary"):
            st.session_state.quiz_step = 1
            st.rerun()

    # ── WIZARD STEP 1: Demographics ─────────────────────────────────────────────
    elif st.session_state.quiz_step == 1:
        render_step_progress(1)
        st.markdown("<p style='color:#5A5A6E;margin-bottom:24px;'>To help us find the best fit, tell us a bit about yourself.</p>", unsafe_allow_html=True)

        gender_options = sorted_options(df_ref["client_gender"])
        ethnicity_options = sorted_options(df_ref["client_ethnicity"])

        # Secure values directly to session state
        st.session_state.client_age = st.number_input("What is your age?", min_value=18, max_value=80, value=st.session_state.get("client_age", 25))
        st.write("")
        st.session_state.client_gender = st.radio("How do you identify?", gender_options, horizontal=True, index=gender_options.index(st.session_state.get("client_gender", gender_options[0])) if st.session_state.get("client_gender") in gender_options else 0)
        st.write("")
        st.session_state.client_ethnicity = st.selectbox("What is your cultural background or ethnicity?", ethnicity_options, index=ethnicity_options.index(st.session_state.get("client_ethnicity", ethnicity_options[0])) if st.session_state.get("client_ethnicity") in ethnicity_options else 0)

        st.markdown("<br>", unsafe_allow_html=True)
        _, col2 = st.columns([1, 1])
        if col2.button("Next →", use_container_width=True, type="primary"):
            st.session_state.quiz_step = 2
            st.rerun()

    # ── WIZARD STEP 2: Clinical Needs ───────────────────────────────────────────
    elif st.session_state.quiz_step == 2:
        render_step_progress(2)
        st.markdown("<p style='color:#5A5A6E;margin-bottom:24px;'>Thank you. What is the main challenge you'd like support with today?</p>", unsafe_allow_html=True)

        issue_options = sorted_options(df_ref["client_issue"])

        st.session_state.client_issue = st.radio("Primary focus area", issue_options, horizontal=True, index=issue_options.index(st.session_state.get("client_issue", issue_options[0])) if st.session_state.get("client_issue") in issue_options else 0)
        st.write("")
        st.session_state.previous_exp = st.radio(
            "Have you ever tried counseling before?",
            [0, 1],
            format_func=lambda v: "Yes, I have" if int(v) == 1 else "No, this is my first time",
            horizontal=True,
            index=[0, 1].index(st.session_state.get("previous_exp", 0))
        )

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        if col1.button("← Back", use_container_width=True):
            st.session_state.quiz_step = 1
            st.rerun()
        if col2.button("Next →", use_container_width=True, type="primary"):
            st.session_state.quiz_step = 3
            st.rerun()

    # ── WIZARD STEP 3: Preferences ──────────────────────────────────────────────
    elif st.session_state.quiz_step == 3:
        render_step_progress(3)
        st.markdown("<p style='color:#5A5A6E;margin-bottom:24px;'>Almost done! Do you have any preferences for your counselor's approach?</p>", unsafe_allow_html=True)

        modality_options = sorted_options(df_ref["preferred_modality"])
        lang_options = sorted_options(df_ref["preferred_language"])
        gender_options = sorted_options(df_ref["preferred_counselor_gender"])

        st.session_state.preferred_modality = st.selectbox(
            "Preferred counseling approach (Modality)",
            modality_options,
            help=modality_help_text(modality_options),
            index=modality_options.index(st.session_state.get("preferred_modality", modality_options[0])) if st.session_state.get("preferred_modality") in modality_options else 0
        )
        st.write("")
        st.session_state.preferred_language = st.radio("Preferred language for sessions", lang_options, horizontal=True, index=lang_options.index(st.session_state.get("preferred_language", lang_options[0])) if st.session_state.get("preferred_language") in lang_options else 0)
        st.write("")
        st.session_state.preferred_c_gender = st.radio("Preferred counselor gender", gender_options, horizontal=True, index=gender_options.index(st.session_state.get("preferred_c_gender", gender_options[0])) if st.session_state.get("preferred_c_gender") in gender_options else 0)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        if col1.button("← Back", use_container_width=True):
            st.session_state.quiz_step = 2
            st.rerun()
        if col2.button("Find My Best Match ✨", use_container_width=True, type="primary"):
            st.session_state.quiz_step = 4
            st.rerun()

    # ── WIZARD STEP 4: Results & ML Processing ──────────────────────────────────
    elif st.session_state.quiz_step == 4:
        st.progress(100)
        
        # Safely pull the variables from session state (which keeps your exact variable names for the ML model below)
        client_age = st.session_state.client_age
        client_gender = st.session_state.client_gender
        client_ethnicity = st.session_state.client_ethnicity
        client_issue = st.session_state.client_issue
        previous_exp = st.session_state.previous_exp
        preferred_language = st.session_state.preferred_language
        preferred_modality = st.session_state.preferred_modality
        preferred_c_gender = st.session_state.preferred_c_gender

        _, btn_col = st.columns([3, 1])
        if btn_col.button("↺ Start Over", use_container_width=True):
            st.session_state.quiz_step = 0
            st.rerun()

        with st.spinner("Analyzing compatibility factors to find your ideal match..."):
            time.sleep(1.2) # Small delay to simulate processing and improve UX transition

        if counselors.empty:
            st.error("No counselors in database.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        # ── EXACT ORIGINAL SCORING LOGIC ──────────────────────────────────────────
        rows = []
        for _, counselor in counselors.iterrows():
            exp_years = experience_years_value(counselor)
            counselor_languages = [v.strip() for v in str(counselor.get("counselor_language", "")).split(",") if v.strip()]
            if preferred_language not in counselor_languages:
                continue
            counselor_modalities = [v.strip() for v in str(counselor.get("counselor_modality", "")).split(",") if v.strip()]
            rows.append({
                "issue_score": issue_similarity_score(client_issue, counselor.specialization),
                "modality_match": int(preferred_modality in counselor_modalities),
                "gender_match": 1 if preferred_c_gender == "No preference" else int(preferred_c_gender == counselor.get("gender")),
                "ethnicity_match": int(client_ethnicity == counselor.get("ethnicity")),
                "age_gap": abs(float(client_age) - float(counselor.get("age"))),
                "client_age": client_age,
                "counselor_age": counselor.get("age"),
                "exp_years": exp_years,
                "prev_exp": previous_experience_value(previous_exp),
                "counselor_id": counselor.counselor_id,
            })

        if not rows:
            st.warning(f"No counselors found who support {preferred_language}.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        feature_order = ['issue_score', 'modality_match', 'gender_match', 'ethnicity_match',
                         'age_gap', 'client_age', 'counselor_age', 'exp_years', 'prev_exp']
        input_df = pd.DataFrame(rows)
        X = input_df[feature_order]
        input_df["compatibility"] = model.predict_proba(X)[:, 1] * 100
        ranked = input_df.sort_values("compatibility", ascending=False)

        best = ranked.iloc[0]
        best_c = counselors[counselors.counselor_id == best.counselor_id].iloc[0]
        second = ranked.iloc[1] if len(ranked) > 1 else None
        second_c = counselors[counselors.counselor_id == second.counselor_id].iloc[0] if second is not None else None

        st.markdown('<div id="match-results-anchor"></div>', unsafe_allow_html=True)
        scroll_to_results()

        # ── EXACT ORIGINAL Result cards ───────────────────────────────────────────
        st.markdown('<p class="section-label" style="margin-top:8px">Your Matches</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        with col1:
            render_counselor_card(best_c, best.compatibility, is_primary=True)
        with col2:
            if second_c is not None:
                render_counselor_card(second_c, second.compatibility, is_primary=False)
            else:
                st.info("No second match available.")

        # ── Match Explanation ─────────────────────────────────────────────────────
        st.write("")
        st.markdown('<p class="section-label" style="margin-top:24px">Why this match?</p>', unsafe_allow_html=True)

        positive_points, negative_points = [], []
        positive_points.append(f"Supports your preferred language ({preferred_language})")
        if int(best.modality_match) == 1:
            positive_points.append(f"Modality matches your preference ({preferred_modality})")
        else:
            negative_points.append(f"Modality does not match ({preferred_modality})")
        if float(best.issue_score) >= 0.99:
            positive_points.append(f"Direct specialization in {client_issue}")
        elif float(best.issue_score) >= 0.6:
            positive_points.append(f"Related experience with {client_issue}")
        else:
            negative_points.append(f"Specialization less aligned with {client_issue}")
        if preferred_c_gender != "No preference":
            if int(best.gender_match) == 1:
                positive_points.append(f"Preferred gender matched ({preferred_c_gender})")
            else:
                negative_points.append(f"Preferred gender not matched ({preferred_c_gender})")

        st.markdown('<div class="explain-card">', unsafe_allow_html=True)
        st.markdown('<p class="explain-title">Match explanation</p>', unsafe_allow_html=True)
        exp_col1, exp_col2 = st.columns(2, gap="large")
        with exp_col1:
            st.markdown("**Strengths**")
            for item in positive_points[:4]:
                st.markdown(
                    f'<div class="point-row"><div class="dot-green"></div><span style="color:#2D2D3F;font-size:14px">{item}</span></div>',
                    unsafe_allow_html=True,
                )
        with exp_col2:
            st.markdown("**Things to note**")
            if negative_points:
                for item in negative_points[:4]:
                    st.markdown(
                        f'<div class="point-row"><div class="dot-amber"></div><span style="color:#2D2D3F;font-size:14px">{item}</span></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    '<div class="point-row"><div class="dot-green"></div><span style="color:#2D2D3F;font-size:14px">No major concerns detected</span></div>',
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

        # SHAP expander
        with st.expander("Technical details — SHAP feature contributions", expanded=False):
                best_index = ranked.index[0]
                x_best = X.loc[[best_index]]
                df_ref_engineered = engineer_features_from_df(df_ref)
                background_data = df_ref_engineered if len(df_ref_engineered) > 0 else X.sample(min(25, len(X)), random_state=42)
                shap_df, row_contrib, base_value, shap_error = get_shap_contributions(model, background_data, x_best, feature_order)

                if shap_error:
                    st.info(shap_error)
                else:
                    readable_names = {
                        "issue_score": "Issue Similarity",
                        "modality_match": "Preferred Modality Match",
                        "gender_match": "Preferred Gender Match",
                        "ethnicity_match": "Ethnicity Match",
                        "age_gap": "Age Gap",
                        "client_age": "Client Age",
                        "counselor_age": "Counselor Age",
                        "exp_years": "Counselor Experience (Years)",
                        "prev_exp": "Client Previous Experience",
                    }
                    shap_df["feature"] = shap_df["feature"].map(lambda v: readable_names.get(v, v))
                    st.caption("Positive values increase predicted compatibility. Negative values decrease it.")
                    st.bar_chart(shap_df.set_index("feature")["shap_value"])
                    st.dataframe(
                        shap_df[["feature", "shap_value"]].rename(columns={"shap_value": "contribution"}),
                        use_container_width=True,
                        hide_index=True,
                    )
                    st.markdown("#### Detailed SHAP charts")
                    try:
                        import matplotlib.pyplot as plt
                        import shap
                        feature_labels = [readable_names.get(f, f) for f in feature_order]
                        row_data = x_best.iloc[0][feature_order].values
                        explanation = shap.Explanation(
                            values=row_contrib,
                            base_values=base_value,
                            data=row_data,
                            feature_names=feature_labels,
                        )
                        fig_wf = plt.figure(figsize=(11, 5))
                        shap.plots.waterfall(explanation, max_display=10, show=False)
                        st.pyplot(fig_wf, clear_figure=True)
                        fig_f = plt.figure(figsize=(11, 3))
                        shap.force_plot(base_value, row_contrib, row_data, feature_names=feature_labels, matplotlib=True, show=False)
                        st.pyplot(fig_f, clear_figure=True)
                    except Exception as exc:
                        st.info(f"Could not render SHAP charts: {exc}")

    st.markdown('</div>', unsafe_allow_html=True) # close form-card container