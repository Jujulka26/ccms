import hashlib
import json as _json
import streamlit as st
import streamlit.components.v1 as components

from frontend.utils.api import get_reference_data, post_match, post_shap, save_intro_request, check_pending_request
from frontend.utils.avatar import avatar_html

# Counselors at/over this many active clients are full: excluded from matching
# and not applyable in the directory (kept in sync with backend ml.MAX_CASELOAD).
MAX_CASELOAD = 5

# ── Custom CSS ────────────────────────────────────────────────────────────────
def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
        .stApp { background: #F5F3FF; }

        .page-header { padding: 24px 0 20px; border-bottom: 1px solid rgba(0,0,0,0.07); margin-bottom: 24px; }
        .page-header-eyebrow {
            display: inline-flex; align-items: center; gap: 6px;
            background: rgba(181,136,247,0.08); border: 1px solid rgba(181,136,247,0.18);
            border-radius: 20px; padding: 3px 12px 3px 10px; margin-bottom: 12px;
            font-size: 10.5px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #B588F7;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .page-header-title { font-family: 'Fraunces', serif; font-size: clamp(26px, 3.2vw, 38px); color: #1C1917; margin: 0 0 8px; letter-spacing: -0.4px; line-height: 1.12; display: block; font-weight: 600; }
        .page-header-sub { font-size: 14px; color: #6B6560; margin: 0; line-height: 1.6; font-family: 'Plus Jakarta Sans', sans-serif; }
        .page-header-stats { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
        .page-header-stat { display: inline-flex; align-items: center; gap: 7px; background: #F5F3FF; border: 1px solid rgba(181,136,247,0.15); border-radius: 20px; padding: 6px 13px; }
        .page-header-stat-num { font-family: 'Fraunces', serif; font-size: 17px; color: #B588F7; line-height: 1; font-weight: 600; }
        .page-header-stat-label { font-size: 11px; color: #A09088; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; font-family: 'Plus Jakarta Sans', sans-serif; }

        .form-card {
            background: radial-gradient(1200px 300px at -10% -30%, rgba(181,136,247,0.06) 0%, transparent 60%), radial-gradient(900px 260px at 110% 120%, rgba(181,136,247,0.05) 0%, transparent 55%), #FFFFFF;
            border-radius: 24px; padding: 28px 36px 24px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 12px 32px -16px rgba(28,25,23,0.08), 0 1px 3px rgba(0,0,0,0.03);
            margin-bottom: 24px;
        }
        .step-header { display: flex; align-items: center; gap: 14px; margin-bottom: 6px; }
        .step-chip { width: 34px; height: 34px; border-radius: 50%; background: linear-gradient(135deg, #B588F7 0%, #83ADF9 100%); color: #FFFFFF; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 14px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(181,136,247,0.4); flex-shrink: 0; }
        .step-title { font-family: 'Fraunces', serif; font-size: 24px; color: #1C1917; line-height: 1.2; font-weight: 600; }
        .step-copy { font-size: 14px; color: #6B6560; margin: 4px 0 16px 48px; line-height: 1.55; font-family: 'Plus Jakarta Sans', sans-serif; }
        .section-divider { border: none; border-top: 1px solid #E5E5E5; margin: 0px 0 20px 0 !important; position: relative; z-index: 10; }
        .anchor-link { display: none !important; }

        [data-testid="block-container"] [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
        [data-testid="stRadio"] > div, [role="radiogroup"] { margin-bottom: 0 !important; padding-bottom: 0 !important; }

        div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] > div > div {
            border-radius: 10px !important; border: 1.5px solid #E5E2DC !important; background: #FAFAF8 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 14px !important; transition: border-color 0.2s;
        }
        div[data-testid="stNumberInput"] input:focus, div[data-testid="stSelectbox"] > div > div:focus-within {
            border-color: #B588F7 !important; box-shadow: 0 0 0 3px rgba(181,136,247,0.1) !important;
        }
        label[data-testid="stWidgetLabel"] p, label[data-testid="stWidgetLabel"] div, label[data-testid="stWidgetLabel"] span {
            font-size: 14px !important; font-weight: 600 !important; color: #1C1917 !important; margin-bottom: 8px !important;
        }

        [data-testid="block-container"] [data-baseweb="radio"] > div:first-child,
        [data-testid="block-container"] [data-baseweb="radio"] input[type="radio"],
        [data-testid="block-container"] [role="radiogroup"] > label > div:first-child {
            position: absolute !important; width: 1px !important; height: 1px !important; opacity: 0 !important; pointer-events: none !important; overflow: hidden !important;
        }
        [data-testid="block-container"] [data-baseweb="radio"] { padding: 9px 22px !important; background: #F5F3FF !important; border: 1.5px solid #F0E8FF !important; border-radius: 30px !important; cursor: pointer !important; transition: background 0.18s ease, border-color 0.18s ease !important; margin-right: 2px !important; }
        [data-testid="block-container"] [data-baseweb="radio"]:hover { border-color: #B588F7 !important; background: rgba(181,136,247,0.05) !important; }
        [data-testid="block-container"] [data-baseweb="radio"]:has(input:checked) { background: rgba(181,136,247,0.08) !important; border-color: #B588F7 !important; }
        [data-testid="block-container"] [data-baseweb="radio"]:has(input:checked) p { font-weight: 700 !important; }
        [data-testid="block-container"] [data-baseweb="radio"] p { font-size: 14px !important; margin: 0 !important; color: #4A4540 !important; font-weight: 500 !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }

        [data-testid="block-container"] div[data-testid="stButton"] button { border-radius: 12px !important; font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 15px !important; font-weight: 600 !important; padding: 10px 24px !important; transition: all 0.2s; width: 100% !important; }
        [data-testid="block-container"] div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(to right, #B588F7 0%, #83ADF9 48%, #2E1065 52%, #2E1065 100%) !important; background-size: 210% 100% !important; background-position: right center !important; transition: background-position 0.4s ease-in-out, box-shadow 0.3s ease, transform 0.15s ease !important; color: #FFFFFF !important; border: none !important; box-shadow: 0 4px 16px rgba(46,16,101,0.45) !important; }
        [data-testid="block-container"] div[data-testid="stButton"] button[kind="primary"]:hover { background-position: left center !important; box-shadow: 0 6px 24px rgba(181,136,247,0.55) !important; transform: translateY(-1px) !important; }

        .result-card { position: relative; background: #FFFFFF; border-radius: 20px; padding: 28px 28px 0; border: 1px solid rgba(0,0,0,0.06); margin-bottom: 0px; overflow: hidden; }
        .dismiss-x { position: absolute; top: 12px; right: 12px; width: 28px; height: 28px; border-radius: 50%; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.18); color: rgba(255,255,255,0.5); font-size: 13px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.18s ease; line-height: 1; z-index: 10; }
        .dismiss-x:hover { background: rgba(239,68,68,0.18); border-color: rgba(239,68,68,0.5); color: #EF4444; }
        .dismiss-x-light { position: absolute; top: 12px; right: 12px; width: 28px; height: 28px; border-radius: 50%; background: rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.1); color: #B0A8A0; font-size: 13px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.18s ease; line-height: 1; z-index: 10; }
        .dismiss-x-light:hover { background: rgba(239,68,68,0.08); border-color: rgba(239,68,68,0.35); color: #EF4444; }
        .st-key-dismiss_0, .st-key-dismiss_1 { display: none !important; }
        [class*="st-key-vp_"] { display: none !important; }
        .result-card.primary { background: #2E1065; border-color: transparent; }
        .card-view-btn { display: block; width: calc(100% + 56px); margin: 24px -28px 0; padding: 14px 28px; background: transparent; border: none; border-top: 1px solid rgba(0,0,0,0.07); color: #B588F7; font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; cursor: pointer; text-align: center; font-family: 'Plus Jakarta Sans', sans-serif; transition: background 0.15s, color 0.15s; }
        .result-card.primary .card-view-btn { border-top-color: rgba(255,255,255,0.08); color: rgba(255,255,255,0.5); }
        .card-view-btn:hover { background: rgba(181,136,247,0.06); color: #B588F7; }
        .result-card.primary .card-view-btn:hover { background: rgba(255,255,255,0.06); color: #FFFFFF; }
        .result-card-badge { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; border-radius: 20px; padding: 4px 12px; display: inline-block; margin-bottom: 0; align-self: flex-start; font-family: 'Plus Jakarta Sans', sans-serif; }
        .badge-primary { background: rgba(181,136,247,0.18); color: #D4B8FC; }
        .badge-secondary { background: #F0EDE8; color: #9C9790; }
        .card-header { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; }
        .card-header-photo { flex-shrink: 0; }
        .card-header-info { flex: 1; min-width: 0; display: flex; flex-direction: column; align-items: flex-start; gap: 6px; }
        .compat-score { font-family: 'Fraunces', serif; font-size: 32px; line-height: 1; color: #FFFFFF; margin: 0; padding-left: 10px; font-weight: 600; }
        .compat-score-secondary { font-family: 'Fraunces', serif; font-size: 32px; line-height: 1; color: #1C1917; margin: 0; padding-left: 10px; font-weight: 600; }
        .compat-label { font-size: 10px; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.08em; margin: 0; padding-left: 10px; font-family: 'Plus Jakarta Sans', sans-serif; }
        .compat-label-secondary { font-size: 10px; color: #A09088; text-transform: uppercase; letter-spacing: 0.08em; margin: 0; padding-left: 10px; font-family: 'Plus Jakarta Sans', sans-serif; }
        .counselor-name { font-size: 18px; font-weight: 700; color: #FFFFFF; margin: 0; padding-left: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; font-family: 'Plus Jakarta Sans', sans-serif; }
        .counselor-name-secondary { font-size: 18px; font-weight: 700; color: #1C1917; margin: 0; padding-left: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; font-family: 'Plus Jakarta Sans', sans-serif; }
        .info-row { display: flex; justify-content: space-between; align-items: center; padding: 11px 0; border-bottom: 1px solid rgba(255,255,255,0.07); }
        .info-row-secondary { display: flex; justify-content: space-between; align-items: center; padding: 11px 0; border-bottom: 1px solid #F0ECE8; }
        .info-key { font-size: 12px; color: rgba(255,255,255,0.4); font-family: 'Plus Jakarta Sans', sans-serif; }
        .info-key-secondary { font-size: 12px; color: #A09088; font-family: 'Plus Jakarta Sans', sans-serif; }
        .info-val { font-size: 13px; color: rgba(255,255,255,0.85); font-weight: 500; font-family: 'Plus Jakarta Sans', sans-serif; }
        .info-val-secondary { font-size: 13px; color: #1C1917; font-weight: 500; font-family: 'Plus Jakarta Sans', sans-serif; }

        .ai-explanation-box { background: linear-gradient(135deg, #F5F3FF 0%, #F5F3FF 100%); border: 1px solid rgba(181,136,247,0.15); border-left: 3px solid #B588F7; border-radius: 0 16px 16px 0; padding: 24px 28px; margin-top: 4px; }
        .ai-badge { display: inline-flex; align-items: center; gap: 6px; background: linear-gradient(135deg, #B588F7, #83ADF9); color: #fff; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; padding: 4px 12px; border-radius: 20px; margin-bottom: 14px; font-family: 'Plus Jakarta Sans', sans-serif; }
        .ai-reason-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 10px; }
        .ai-reason-row:last-child { margin-bottom: 0; }
        .ai-reason-icon { flex-shrink: 0; margin-top: 2px; }
        .ai-reason-text { font-size: 14.5px; color: #2A2420; line-height: 1.5; font-weight: 400; font-family: 'Plus Jakarta Sans', sans-serif; }

        div[data-testid="stTabs"] button { font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 14px !important; font-weight: 500 !important; }

        [data-testid="block-container"] div[data-testid="stButton"] button:not([kind="primary"]) {
            background: transparent !important;
            border: 1.5px solid rgba(181,136,247,0.25) !important;
            color: #B588F7 !important;
            border-radius: 12px !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            letter-spacing: 0.03em !important;
            padding: 10px 20px !important;
            transition: all 0.2s ease !important;
            box-shadow: none !important;
        }
        [data-testid="block-container"] div[data-testid="stButton"] button:not([kind="primary"]):hover {
            background: rgba(181,136,247,0.06) !important;
            border-color: #B588F7 !important;
            color: #B588F7 !important;
        }

        div[data-testid="stExpander"] {
            background: #FFFFFF;
            border: 1px solid rgba(181,136,247,0.14) !important;
            border-radius: 16px !important;
            overflow: hidden;
            margin-bottom: 24px;
            box-shadow: none !important;
        }
        div[data-testid="stExpander"] summary {
            padding: 12px 20px !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            letter-spacing: 0.07em !important;
            text-transform: uppercase !important;
            color: #B588F7 !important;
            background: linear-gradient(135deg, #F5F3FF 0%, #F5F3FF 100%) !important;
            border-radius: 16px !important;
            border-bottom: 1px solid rgba(181,136,247,0.08);
            list-style: none;
        }
        div[data-testid="stExpander"] summary:hover {
            background: linear-gradient(135deg, #F0E8FF 0%, #F5F3FF 100%) !important;
            color: #B588F7 !important;
        }
        div[data-testid="stExpander"] summary svg { color: #B588F7 !important; }
        div[data-testid="stExpander"] > details > div[data-testid="stExpanderDetails"] {
            padding: 24px !important;
            background: #FFFFFF;
        }
        [data-testid="stCustomComponentV1"] {
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def modality_help_text(modality_options):
    descriptions = {
        "Cognitive": "Helps you identify and reframe unhelpful thought patterns (e.g. CBT).",
        "Behavioral": "Focuses on changing behaviours through techniques like exposure and activation.",
        "Humanistic": "Focuses on understanding your feelings in a supportive, non-judgmental way.",
        "Psychodynamic": "Explores how past experiences and unconscious patterns shape you today.",
    }
    if not modality_options:
        return "Modality is the counseling approach used in sessions."
    parts = [f"- {m}: {descriptions.get(str(m), 'approach used in counseling sessions')}" for m in modality_options]
    return "Modality is the counseling approach/style:\n\n" + "\n".join(parts)


def render_step_progress(step: int, total: int = 3):
    step_names = ["About You", "Your Needs", "Preferences"]
    nodes_html = ""
    for i, name in enumerate(step_names, 1):
        if i < step:
            circle_bg = "linear-gradient(135deg,#B588F7 0%,#83ADF9 100%)"
            circle_color = "#FFFFFF"; circle_border = "none"; shadow = "0 4px 12px rgba(181,136,247,0.30)"
            label_color = "#B588F7"; weight = "600"; inner = "✓"
        elif i == step:
            circle_bg = "linear-gradient(135deg,#B588F7 0%,#83ADF9 100%)"
            circle_color = "#FFFFFF"; circle_border = "none"; shadow = "0 6px 16px rgba(14,24,35,0.35), 0 0 0 4px rgba(26,35,50,0.12)"
            label_color = "#1C1917"; weight = "700"; inner = str(i)
        else:
            circle_bg = "#FFFFFF"; circle_color = "#B0A9A0"; circle_border = "1.5px solid #F0E8FF"
            shadow = "none"; label_color = "#B0A9A0"; weight = "500"; inner = str(i)
        nodes_html += (
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:8px;z-index:2;background:transparent;">'
            f'<div style="width:34px;height:34px;border-radius:50%;background:{circle_bg};color:{circle_color};'
            f'border:{circle_border};display:flex;align-items:center;justify-content:center;'
            f'font-family:\'Plus Jakarta Sans\',sans-serif;font-weight:700;font-size:13px;box-shadow:{shadow};">{inner}</div>'
            f'<span style="font-size:11.5px;color:{label_color};font-weight:{weight};letter-spacing:0.02em;font-family:\'Plus Jakarta Sans\',sans-serif;">{name}</span>'
            f'</div>'
        )
    fill_pct = max(0, min(100, int((step - 1) / (total - 1) * 100))) if total > 1 else 0
    st.markdown(
        f"""
        <div style="position:relative;padding:4px 8px 8px;margin-bottom:30px;">
            <div style="position:absolute;left:calc(8px + 17px);right:calc(8px + 17px);top:calc(4px + 17px);height:2px;background:#EDE8E3;border-radius:2px;z-index:1;"></div>
            <div style="position:absolute;left:calc(8px + 17px);top:calc(4px + 17px);width:calc((100% - 16px - 34px) * {fill_pct} / 100);height:2px;background:linear-gradient(90deg,#B588F7,#83ADF9);border-radius:2px;z-index:1;"></div>
            <div style="display:flex;justify-content:space-between;align-items:flex-start;position:relative;">{nodes_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_step_header(number: int, title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="step-header"><div class="step-chip">{number}</div><div class="step-title">{title}</div></div>
        <div class="step-copy">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def scroll_to_results(anchor_id="match-results-anchor"):
    components.html(
        f"""
        <script>
        const anchor = window.parent.document.getElementById("{anchor_id}");
        if (anchor) {{ anchor.scrollIntoView({{ behavior: "smooth", block: "start" }}); }}
        </script>
        """,
        height=0, width=0,
    )


def render_page_header():
    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-title">Find Your Ideal Counselor</div>
            <div class="page-header-stats">
                <div class="page-header-stat">
                    <span class="page-header-stat-num">8</span>
                    <span class="page-header-stat-label">Match Factors</span>
                </div>
                <div class="page-header-stat">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#B588F7" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                    <span class="page-header-stat-label">Personalised</span>
                </div>
                <div class="page-header-stat">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#B588F7" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                    <span class="page-header-stat-label">Explainable AI</span>
                </div>
            </div>
            <p style="font-size:12px; color:#9C9790; margin:12px 0 0; line-height:1.55; display:flex; align-items:center; gap:6px; font-family:'Plus Jakarta Sans',sans-serif;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#C0B8B0" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                AI-generated estimates only — not a clinical assessment. Always consult a qualified mental health professional.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_disclaimer():
    st.markdown(
        """
        <div style="display:flex; gap:8px; align-items:flex-start; padding:10px 14px; margin-top:16px;
            background:rgba(245,158,11,0.04); border:1px solid rgba(245,158,11,0.2); border-radius:10px;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:1px;">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <span style="font-size:12px; color:#78716C; line-height:1.55;">
                <strong style="color:#92400E;">Note:</strong>
                Compatibility scores are AI-generated estimates, not clinical assessments — always consult a qualified mental health professional.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _match_badges(c: dict, primary: bool) -> str:
    feats = c.get("features") or {}
    badges = []
    issue = c.get("issue_match", 0)
    if issue >= 1.0:
        badges.append(("Issue Match", True))
    elif issue >= 0.6:
        badges.append(("Related Issue", None))
    if c.get("modality_match"):
        badges.append(("Modality Match", True))
    if feats.get("exp_issue_fit") or c.get("experience_years", 0) >= 8:
        badges.append(("Senior Counselor", True))
    if c.get("gender_match"):
        badges.append(("Gender Match", True))
    if feats.get("ethnicity_match"):
        badges.append(("Ethnicity Match", True))

    if primary:
        def chip(label, matched):
            if matched is True:
                return f'<span style="background:rgba(16,185,129,0.18);color:#6EE7B7;border:1px solid rgba(16,185,129,0.3);font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;">✓ {label}</span>'
            return f'<span style="background:rgba(245,158,11,0.18);color:#FCD34D;border:1px solid rgba(245,158,11,0.3);font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;">~ {label}</span>'
    else:
        def chip(label, matched):
            if matched is True:
                return f'<span style="background:rgba(16,185,129,0.1);color:#065F46;border:1px solid rgba(16,185,129,0.25);font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;">✓ {label}</span>'
            return f'<span style="background:rgba(245,158,11,0.1);color:#92400E;border:1px solid rgba(245,158,11,0.25);font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;">~ {label}</span>'

    return '<div style="display:flex;flex-wrap:wrap;gap:6px;padding:12px 0 4px;">' + "".join(chip(l, m) for l, m in badges) + "</div>"


def render_counselor_card(c: dict, score: float, is_primary=True, dismiss_key: str | None = None):
    langs = c.get("counselor_language") or "—"
    mods = c.get("counselor_modality") or "—"
    avail = c.get("availability") or "—"
    av = avatar_html(c['name'], c.get('image'), size=80, radius=16)
    dismiss_btn_html = f'<div class="dismiss-x" data-dismiss="{dismiss_key}">✕</div>' if dismiss_key else ""
    dismiss_btn_light = f'<div class="dismiss-x-light" data-dismiss="{dismiss_key}">✕</div>' if dismiss_key else ""

    if is_primary:
        st.markdown(
            f"""
            <div class="result-card primary">
                {dismiss_btn_html}
                <div class="card-header">
                    <div class="card-header-photo">{av}</div>
                    <div class="card-header-info">
                        <span class="result-card-badge badge-primary">Top Match</span>
                        <div class="counselor-name">{c['name']}</div>
                        <div class="compat-score">{score:.1f}%</div>
                        <div class="compat-label">Compatibility score</div>
                    </div>
                </div>
                {_match_badges(c, True)}
                <div class="info-row"><span class="info-key">Experience</span><span class="info-val">{c['experience_years']} yrs</span></div>
                <div class="info-row"><span class="info-key">Specialization</span><span class="info-val">{c['specialization']}</span></div>
                <div class="info-row"><span class="info-key">Modality</span><span class="info-val">{mods}</span></div>
                <div class="info-row"><span class="info-key">Language</span><span class="info-val">{langs}</span></div>
                <div class="info-row" style="border:none"><span class="info-key">Availability</span><span class="info-val">{avail}</span></div>
                <button class="card-view-btn">VIEW FULL PROFILE →</button>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="result-card">
                {dismiss_btn_light}
                <div class="card-header">
                    <div class="card-header-photo">{av}</div>
                    <div class="card-header-info">
                        <span class="result-card-badge badge-secondary">2nd Option</span>
                        <div class="counselor-name-secondary">{c['name']}</div>
                        <div class="compat-score-secondary">{score:.1f}%</div>
                        <div class="compat-label-secondary">Compatibility score</div>
                    </div>
                </div>
                {_match_badges(c, False)}
                <div class="info-row-secondary"><span class="info-key-secondary">Experience</span><span class="info-val-secondary">{c['experience_years']} yrs</span></div>
                <div class="info-row-secondary"><span class="info-key-secondary">Specialization</span><span class="info-val-secondary">{c['specialization']}</span></div>
                <div class="info-row-secondary"><span class="info-key-secondary">Modality</span><span class="info-val-secondary">{mods}</span></div>
                <div class="info-row-secondary"><span class="info-key-secondary">Language</span><span class="info-val-secondary">{langs}</span></div>
                <div class="info-row-secondary" style="border:none"><span class="info-key-secondary">Availability</span><span class="info-val-secondary">{avail}</span></div>
                <button class="card-view-btn">VIEW FULL PROFILE →</button>
            </div>
            """,
            unsafe_allow_html=True,
        )

    card_id = f"{int(c.get('counselor_id', 0))}_{'p' if is_primary else 's'}"
    if st.button("View Full Profile", key=f"vp_{card_id}", use_container_width=True, type="secondary"):
        show_profile_dialog(c, score)


# ── Profile dialog ─────────────────────────────────────────────────────────────


@st.dialog("Profile")
def show_profile_dialog(c: dict, score=None):
    name         = c.get("name", "Counselor")
    exp          = c.get("experience_years", "—")
    lang         = c.get("counselor_language", "—")
    about        = c.get("about_me") or ""
    ht1          = c.get("helpful_thought_1") or ""
    ht2          = c.get("helpful_thought_2") or ""
    ext          = c.get("expertise_tags") or ""
    modality_desc = c.get("modality_desc") or ""

    pills    = [t.strip() for t in ext.split(",") if t.strip()][:6] if ext.strip() else []
    thoughts = [t for t in [ht1, ht2] if t.strip()]
    av       = avatar_html(name, c.get("image"), size=84, radius=16)

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

    div[role="dialog"] {
        max-width: 730px !important;
        width: 730px !important;
    }

    .prof-header-band {
        background: linear-gradient(135deg, #F3F0FF 0%, #FFF8F3 100%);
        border-radius: 16px; padding: 20px 20px 16px; margin-bottom: 4px;
        border: 1px solid rgba(181,136,247,0.1);
    }
    .prof-header { display:flex; align-items:center; gap:18px; }
    .prof-name { font-family:'Fraunces',serif; font-size:23px; font-weight:600; color:#1C1917; margin:0 0 3px; line-height:1.2; }
    .prof-role { font-size:12px; color:#B588F7; font-weight:700; margin:0 0 8px; letter-spacing:0.03em; font-family:'Plus Jakarta Sans',sans-serif; }
    .prof-meta { display:flex; flex-wrap:wrap; column-gap:12px; row-gap:4px; }
    .prof-meta-item { font-size:12px; color:#6B6560; display:flex; align-items:center; gap:3px; }
    .prof-meta-score { font-size:18px; color:#B588F7; font-weight:700; }
    .prof-score-chip { display:inline-flex; align-items:center; background:#F5F3FF; color:#B588F7; font-size:11px; font-weight:700; letter-spacing:0.06em; padding:2px 10px; border-radius:20px; border:1px solid rgba(181,136,247,0.2); margin-bottom:6px; }
    .prof-rule { border:none; border-top:1px solid #EBEBEB; margin:14px 0 16px; }

    .prof-section { margin-bottom:12px; background:#FAFAFA; border-radius:12px; padding:14px 16px; border:1px solid rgba(0,0,0,0.04); }
    .prof-label { font-size:10.5px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:#B588F7; margin:0 0 10px; font-family:'Plus Jakarta Sans',sans-serif; }
    .prof-about { font-size:15px !important; color:#2D2D3F; line-height:1.8; margin:0; }

    .prof-pills { display:flex; flex-wrap:wrap; gap:6px; }
    .prof-pill {
        background: linear-gradient(135deg, #F5F3FF, #F0E8FF);
        color:#B588F7; font-size:12px; font-weight:600;
        padding:5px 14px; border-radius:20px;
        border:1px solid rgba(181,136,247,0.18);
        box-shadow: 0 1px 3px rgba(181,136,247,0.08);
        font-family:'Plus Jakarta Sans',sans-serif;
    }

    .prof-thoughts-wrap { display:flex; flex-direction:column; gap:8px; }
    .prof-thought {
        font-size:13px; color:#78350F; font-style:italic; line-height:1.7;
        padding: 10px 14px; margin: 0;
        border-left: 3px solid #F97316;
        background: rgba(249,115,22,0.06);
        border-radius: 0 10px 10px 0;
    }

    .prof-how { font-size:15px !important; color:#2D2D3F; line-height:1.8; margin:0; }

    div[data-testid="stExpander"] { background:#FFFFFF !important; border:1px solid #EBEBEB !important; border-radius:12px !important; box-shadow:none !important; margin-bottom:0 !important; }
    div[data-testid="stExpander"] summary { background:#FFFFFF !important; font-size:13px !important; font-weight:600 !important; color:#4A4A5A !important; text-transform:none !important; letter-spacing:0 !important; padding:12px 16px !important; border-radius:12px !important; }
    div[data-testid="stExpander"] summary:hover { background:#F5F3FF !important; color:#B588F7 !important; }
    div[data-testid="stExpander"] svg { color:#B588F7 !important; }
    div[data-testid="stDialog"] [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:first-child { margin-top:-16px !important; }

    div[data-testid="stDialog"] button[kind="primary"] {
        background: linear-gradient(135deg, #F97316 0%, #EA580C 100%) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(249,115,22,0.35) !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        border-radius: 14px !important;
        padding: 14px 28px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stDialog"] button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(249,115,22,0.45) !important;
        transform: translateY(-1px) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    score_item = f'<span class="prof-meta-score">✦ {score:.1f}%</span>' if score else ""
    _translate = '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#6B6560" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:3px;"><path d="M5 8l6 6"/><path d="M4 14l6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="M22 22l-5-10-5 10"/><path d="M14 18h6"/></svg>'
    age    = c.get("age", "")
    gender = c.get("gender", "")
    meta_html = (
        (f'<span class="prof-meta-item">👤 {gender}</span>' if gender else "")
        + (f'<span class="prof-meta-item">🎂 Age {age}</span>' if age else "")
        + f'<span class="prof-meta-item">💼 {exp} yrs exp</span>'
        + (f'<span class="prof-meta-item">{_translate}{lang}</span>' if lang and lang != "—" else "")
    )
    st.markdown(
        f'<div class="prof-header-band">'
        f'<div class="prof-header">{av}'
        f'<div style="padding-left:4px;">'
        f'<div style="display:flex;align-items:baseline;gap:10px;">'
        f'<div class="prof-name">{name}</div>{score_item}</div>'
        f'<div class="prof-role">Registered Counsellor (LKM)</div>'
        f'<div class="prof-meta">{meta_html}</div></div></div></div>'
        f'<div style="height:12px;"></div>',
        unsafe_allow_html=True,
    )

    left_col = ""
    right_col = ""

    if about.strip():
        left_col += (
            f'<div class="prof-section"><div class="prof-label">About</div>'
            f'<p class="prof-about">{about}</p></div>'
        )
    if modality_desc.strip():
        left_col += (
            f'<div class="prof-section"><div class="prof-label">How I work with you</div>'
            f'<p class="prof-how">{modality_desc}</p></div>'
        )

    if pills:
        pills_html = "".join(f'<span class="prof-pill">{p}</span>' for p in pills)
        right_col += (
            f'<div class="prof-section"><div class="prof-label">Areas of Expertise</div>'
            f'<div class="prof-pills">{pills_html}</div></div>'
        )
    if thoughts:
        rows = "".join(f'<div class="prof-thought">"{t}"</div>' for t in thoughts)
        right_col += (
            f'<div class="prof-section"><div class="prof-label">You might be thinking...</div>'
            f'<div class="prof-thoughts-wrap">{rows}</div></div>'
        )

    availability = c.get("availability")
    if availability:
        blocks = [b.strip() for b in str(availability).split(",") if b.strip()]
        if blocks:
            avail_html = "".join(f'<span class="prof-pill">🕒 {b}</span>' for b in blocks)
            right_col += (
                f'<div class="prof-section"><div class="prof-label">Availability</div>'
                f'<div class="prof-pills">{avail_html}</div></div>'
            )

    if left_col or right_col:
        st.markdown(
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:4px;">'
            f'<div>{left_col}</div><div>{right_col}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")

    counselor_id  = c.get("counselor_id")
    req_state_key = f"req_{counselor_id}"

    if req_state_key not in st.session_state:
        st.session_state[req_state_key] = False

    def toggle_req(val):
        st.session_state[req_state_key] = val

    already_sent_to = st.session_state.get("_global_sent_to")
    if already_sent_to:
        same = already_sent_to == name
        sent_title = "Request already sent" if same else "You already have a pending request"
        sent_body  = (f"We'll connect you with {name} soon." if same
                      else f"Please wait to hear back from {already_sent_to} before reaching out to another counselor.")
        st.markdown(
            f'<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);'
            f'border-radius:12px;padding:14px 18px;display:flex;align-items:center;gap:12px;margin-bottom:20px;">'
            f'<span style="font-size:22px;">✅</span>'
            f'<div>'
            f'<div style="font-size:13px;font-weight:600;color:#065F46;">{sent_title}</div>'
            f'<div style="font-size:12px;color:#6B6560;margin-top:2px;">{sent_body}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        st.write("")
        return

    if int(c.get("caseload") or 0) >= MAX_CASELOAD:
        st.markdown(
            f'<div style="background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.25);'
            f'border-radius:12px;padding:14px 18px;display:flex;align-items:center;gap:12px;margin-bottom:8px;">'
            f'<span style="font-size:22px;">🚫</span>'
            f'<div>'
            f'<div style="font-size:13px;font-weight:600;color:#B91C1C;">Fully booked</div>'
            f'<div style="font-size:12px;color:#6B6560;margin-top:2px;">{name} is at full capacity right now. '
            f'Please explore another counselor — you can still view this profile anytime.</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        st.write("")
        return

    if not st.session_state[req_state_key]:
        st.button(f"✉️ Get to know {name}", use_container_width=True, type="primary",
                  on_click=toggle_req, args=(True,))
    else:
        st.caption(
            f"Leave your details below. The clinic coordinator will connect you with {name} via email."
        )
        client_name  = st.text_input("Your Full Name")
        client_email = st.text_input("Your Email Address")
        st.caption(
            "🔒 Your details and questionnaire answers are used only to make and review your match. "
            "They are not shared or used for any other purpose."
        )
        st.write("")

        col1, col2 = st.columns(2)
        col1.button("Cancel", use_container_width=True, on_click=toggle_req, args=(False,))
        if col2.button("Send Request", use_container_width=True, type="primary"):
            if not client_name.strip() or not client_email.strip():
                st.error("Please fill in both your name and email.")
            elif check_pending_request(client_email.strip()):
                st.error(
                    "This email already has a pending request. "
                    "Please wait to hear back before sending another."
                )
            else:
                save_intro_request(
                    client_name.strip(), client_email.strip(),
                    int(counselor_id), float(score) if score else 0.0,
                    client_age=st.session_state.get("client_age"),
                    client_gender=st.session_state.get("client_gender"),
                    client_ethnicity=st.session_state.get("client_ethnicity"),
                    client_issue=st.session_state.get("client_issue"),
                    prev_exp=st.session_state.get("previous_exp"),
                    preferred_language=st.session_state.get("preferred_language"),
                    preferred_modality=st.session_state.get("preferred_modality"),
                    preferred_c_gender=st.session_state.get("preferred_c_gender"),
                )
                st.session_state["_global_sent_to"] = name
                st.session_state["_success_name"] = name
                st.rerun()


# ── Request success dialog ────────────────────────────────────────────────────
@st.dialog("Request Sent!")
def show_request_success_dialog(name: str):
    st.markdown(
        f"""
        <style>
        div[data-testid="stDialog"] button[kind="primary"] {{
            background: linear-gradient(135deg, #F97316 0%, #EA580C 100%) !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(249,115,22,0.30) !important;
            font-size: 15px !important; font-weight: 700 !important;
            border-radius: 12px !important; padding: 12px 28px !important;
        }}
        div[data-testid="stDialog"] button[kind="primary"]:hover {{
            box-shadow: 0 6px 20px rgba(249,115,22,0.45) !important;
            transform: translateY(-1px) !important;
        }}
        </style>
        <div style="text-align:center; padding:12px 0 20px;">
            <div style="width:68px;height:68px;background:linear-gradient(135deg,#F97316,#EA580C);
                border-radius:50%;display:flex;align-items:center;justify-content:center;
                margin:0 auto 18px;box-shadow:0 8px 24px rgba(249,115,22,0.35);">
                <span style="font-size:30px;line-height:1;">✉️</span>
            </div>
            <div style="font-family:'Fraunces',serif;font-size:22px;font-weight:600;color:#1C1917;margin-bottom:10px;">
                Your request is on its way!
            </div>
            <div style="font-size:13px;color:#6B6560;line-height:1.75;max-width:280px;margin:0 auto;font-family:'Plus Jakarta Sans',sans-serif;">
                We've received your request and will connect you with
                <strong style="color:#1C1917;">{name}</strong> via email within 1-2 business days.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Done", use_container_width=True, type="primary"):
        st.rerun()


# ── Match explanation ─────────────────────────────────────────────────────────
def _generate_explanation(c, client_issue) -> str:
    import random
    first     = c.get("name", "Your counselor").split()[0]
    spec      = c.get("specialization", client_issue)
    exp       = int(c.get("experience_years") or 0)
    modality  = c.get("counselor_modality", "")
    mod_match = c.get("modality_match") == 1
    eth_match = c.get("ethnicity_match") == 1
    ethnicity = c.get("ethnicity", "") if eth_match else ""

    exp_str    = f"{exp} years" if exp >= 8 else "several years"
    exact      = spec == client_issue
    issue_bold = f"<strong>{client_issue}</strong>"
    spec_bold  = f"<strong>{spec}</strong>"
    mod_bold   = f"<strong>{modality}</strong>"
    eth_bold   = f"<strong>{ethnicity}</strong>" if ethnicity else ""

    # Spec phrasing when not an exact match
    spec_phrase_A = f"{exp_str} working with {issue_bold}" if exact else f"{exp_str} in {spec_bold}, closely related to {issue_bold}"
    spec_phrase_B = f"exactly where {first}'s focus lies" if exact else f"closely related to {first}'s expertise in {spec_bold}"
    spec_phrase_C = f"specialises in {issue_bold}" if exact else f"specialises in {spec_bold}, which closely relates to {issue_bold}"

    templates = [
        # A — experience-led
        (
            f"For {issue_bold}, it helps to speak with someone who truly knows that area. "
            f"{first} has {spec_phrase_A}, so your challenges are already familiar to them."
            + (f" They also practise {mod_bold}, which matches the approach you prefer." if mod_match else "")
            + (f" Your shared {eth_bold} background may help conversations feel natural from the start." if eth_match and ethnicity else "")
        ),
        # B — built around you
        (
            f"You need support with {issue_bold}, and {spec_phrase_B}. "
            f"With {exp_str} of focused experience"
            + (f" and a {mod_bold} approach that fits your preference" if mod_match else "")
            + f", you can spend less time explaining and more time making progress."
            + (f" {first} also shares your {eth_bold} background, which can help build comfort early on." if eth_match and ethnicity else "")
        ),
        # C — strong match
        (
            f"Finding the right fit is not always easy. "
            f"{first} {spec_phrase_C}, brings {exp_str} of hands-on experience"
            + (f", and practises {mod_bold}, the approach you said you prefer" if mod_match else "")
            + f". Across what matters to you, {first} is a strong match."
            + (f" Your shared {eth_bold} background may also help you feel more at ease from the beginning." if eth_match and ethnicity else "")
        ),
    ]

    return random.choice(templates)


@st.dialog("Start over?")
def _start_over_dialog(reset_fn):
    st.markdown("""<style>
    div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"] > div:first-child button,
    div[data-testid="stModal"] div[data-testid="stHorizontalBlock"] > div:first-child button {
        background-color: #EF4444 !important;
        background-image: none !important;
        color: #FFFFFF !important;
        border: 1px solid #EF4444 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stDialog"] div[data-testid="stHorizontalBlock"] > div:first-child button:hover,
    div[data-testid="stModal"] div[data-testid="stHorizontalBlock"] > div:first-child button:hover {
        background-color: #DC2626 !important;
        border-color: #DC2626 !important;
    }
    </style>""", unsafe_allow_html=True)
    st.markdown("Your current matches will be cleared and you'll need to go through the questionnaire again.")
    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, start over", use_container_width=True, type="primary"):
            reset_fn()
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


# ── Quiz step fragments (partial rerun → no full-page flash on input change) ──
@st.fragment
def _step1_form(ref):
    render_step_progress(1)
    render_step_header(1, "Tell us about yourself", "A few quick details help us tailor your best match.")
    st.number_input("What is your age?", min_value=18, max_value=80, key="_age_ui")
    st.session_state.client_age = int(st.session_state._age_ui)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.radio("How do you identify?", ref["client_gender"], horizontal=True, key="_gender_ui")
    st.session_state.client_gender = st.session_state._gender_ui
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.selectbox("What is your cultural background or ethnicity?", ref["client_ethnicity"], key="_ethnicity_ui")
    st.session_state.client_ethnicity = st.session_state._ethnicity_ui
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    if col1.button("← Back", use_container_width=True):
        st.session_state.quiz_step = 0
        st.rerun()
    if col2.button("Next →", use_container_width=True, type="primary"):
        st.session_state.quiz_step = 2
        st.rerun()


@st.fragment
def _step2_form(ref):
    render_step_progress(2)
    render_step_header(2, "What brings you here?", "Share the main challenge you'd like support with today.")
    st.radio("Primary focus area", ref["client_issue"], horizontal=True, key="_issue_ui")
    st.session_state.client_issue = st.session_state._issue_ui
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.radio(
        "Have you ever tried counseling before?",
        ["No, this is my first time", "Yes, I have"],
        horizontal=True,
        key="_prev_exp_ui",
    )
    st.session_state.previous_exp = 1 if st.session_state._prev_exp_ui == "Yes, I have" else 0
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    if col1.button("← Back", use_container_width=True):
        st.session_state.quiz_step = 1
        st.rerun()
    if col2.button("Next →", use_container_width=True, type="primary"):
        st.session_state.quiz_step = 3
        st.rerun()


def _snapshot_match_inputs() -> dict:
    """Freeze the questionnaire answers into a plain dict. Read on the results
    page so reruns (e.g. opening a profile dialog) can't recompute the match
    with reverted widget state — which previously dropped the time filter."""
    return {
        "client_age":         st.session_state.get("client_age"),
        "client_gender":      st.session_state.get("client_gender"),
        "client_ethnicity":   st.session_state.get("client_ethnicity"),
        "client_issue":       st.session_state.get("client_issue"),
        "prev_exp":           int(st.session_state.get("previous_exp") or 0),
        "preferred_language": st.session_state.get("preferred_language"),
        "preferred_modality": st.session_state.get("preferred_modality"),
        "preferred_c_gender": st.session_state.get("preferred_c_gender"),
        "preferred_time":     st.session_state.get("preferred_time", "Any time"),
    }


@st.fragment
def _step3_form(ref):
    render_step_progress(3)
    render_step_header(3, "Your preferences", "Almost done — let us know what works best for you.")
    st.selectbox(
        "Preferred counseling approach (Modality)",
        ref["preferred_modality"],
        help=modality_help_text(ref["preferred_modality"]),
        key="preferred_modality",
    )
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.radio("Preferred language for sessions", ref["preferred_language"], horizontal=True, key="preferred_language")
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.radio("Preferred counselor gender", ref["preferred_counselor_gender"], horizontal=True, key="preferred_c_gender")
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.selectbox(
        "Preferred session time",
        ref.get("preferred_time", ["Any time"]),
        help="When you'd generally like sessions. 'Any time' won't filter on availability.",
        key="preferred_time",
    )
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    if col1.button("← Back", use_container_width=True):
        st.session_state.quiz_step = 2
        st.rerun()
    if col2.button("Find My Best Match ✨", use_container_width=True, type="primary"):
        st.session_state["_committed_match"] = _snapshot_match_inputs()
        st.session_state.quiz_step = 4
        st.rerun()


# ── Main page ─────────────────────────────────────────────────────────────────
def show_matching_page():
    inject_styles()

    if "_success_name" in st.session_state:
        _sname = st.session_state["_success_name"]
        del st.session_state["_success_name"]
        show_request_success_dialog(_sname)

    ref = get_reference_data()

    if "quiz_step" not in st.session_state:
        st.session_state.quiz_step = 0
    if "excluded_counselor_ids" not in st.session_state:
        st.session_state.excluded_counselor_ids = []

    if "client_age" not in st.session_state:          st.session_state.client_age = 25
    if "client_gender" not in st.session_state:       st.session_state.client_gender = ref["client_gender"][0] if ref["client_gender"] else ""
    if "client_ethnicity" not in st.session_state:    st.session_state.client_ethnicity = ref["client_ethnicity"][0] if ref["client_ethnicity"] else ""
    if "client_issue" not in st.session_state:        st.session_state.client_issue = ref["client_issue"][0] if ref["client_issue"] else ""
    if "previous_exp" not in st.session_state:        st.session_state.previous_exp = 0
    if "_age_ui" not in st.session_state:             st.session_state._age_ui = 25
    if "_gender_ui" not in st.session_state:          st.session_state._gender_ui = ref["client_gender"][0] if ref["client_gender"] else ""
    if "_ethnicity_ui" not in st.session_state:       st.session_state._ethnicity_ui = ref["client_ethnicity"][0] if ref["client_ethnicity"] else ""
    if "_issue_ui" not in st.session_state:           st.session_state._issue_ui = ref["client_issue"][0] if ref["client_issue"] else ""
    if "_prev_exp_ui" not in st.session_state:        st.session_state._prev_exp_ui = "No, this is my first time"
    if "preferred_modality" not in st.session_state:  st.session_state.preferred_modality = ref["preferred_modality"][0] if ref["preferred_modality"] else ""
    if "preferred_language" not in st.session_state:  st.session_state.preferred_language = ref["preferred_language"][0] if ref["preferred_language"] else ""
    if "preferred_c_gender" not in st.session_state:  st.session_state.preferred_c_gender = ref["preferred_counselor_gender"][0] if ref["preferred_counselor_gender"] else ""
    if "preferred_time" not in st.session_state:      st.session_state.preferred_time = ref["preferred_time"][0] if ref.get("preferred_time") else "Any time"

    render_page_header()

    components.html(
        """
        <script>
        (function() {
            var doc = window.parent.document;
            function applyRadioColor() {
                doc.querySelectorAll('[data-baseweb="radio"]').forEach(function(pill) {
                    if (pill.closest('[data-testid="stSidebar"]')) return;
                    var input = pill.querySelector('input[type="radio"]');
                    if (!input) return;
                    var outerRing = pill.children[0];
                    var innerDot  = outerRing ? outerRing.children[0] : null;
                    if (input.checked) {
                        if (outerRing) {
                            outerRing.style.setProperty('border-color', '#B588F7', 'important');
                            outerRing.style.setProperty('background-color', '#B588F7', 'important');
                        }
                        if (innerDot) innerDot.style.setProperty('background-color', '#FFFFFF', 'important');
                    } else {
                        if (outerRing) {
                            outerRing.style.removeProperty('border-color');
                            outerRing.style.removeProperty('background-color');
                        }
                        if (innerDot) innerDot.style.removeProperty('background-color');
                    }
                });
            }
            applyRadioColor();
            [150, 400, 800].forEach(function(t) { setTimeout(applyRadioColor, t); });
            new MutationObserver(applyRadioColor).observe(doc.body, { subtree: true, childList: true, attributes: true });
            setInterval(applyRadioColor, 300);
        })();
        </script>
        """,
        height=0, width=0,
    )

    # ── STEP 0: Welcome ──────────────────────────────────────────────────────
    if st.session_state.quiz_step == 0:
        st.markdown("<h3 style='color: #1C1917; text-align: center; margin-bottom: 10px; font-family: \"Fraunces\", serif; font-weight: 600;'>Let's find someone who truly gets you.</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B6560; margin-bottom: 30px; font-family: \"Plus Jakarta Sans\", sans-serif;'>Take a short, guided questionnaire so we can match you with the right counselor based on your unique needs and preferences.</p>", unsafe_allow_html=True)
        st.markdown(
            """
            <style>
            div[data-testid="stButton"] button[kind="primary"] {
                background: linear-gradient(to right, #B588F7 0%, #83ADF9 48%, #2E1065 52%, #2E1065 100%) !important;
                background-size: 210% 100% !important;
                background-position: right center !important;
                transition: background-position 0.4s ease-in-out, box-shadow 0.3s ease, transform 0.15s ease !important;
                border: none !important;
                font-size: 16px !important;
                letter-spacing: 0.03em !important;
                padding: 14px 28px !important;
                font-weight: 700 !important;
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                box-shadow: 0 4px 16px rgba(46,16,101,0.45) !important;
            }
            div[data-testid="stButton"] button[kind="primary"]:hover {
                background-position: left center !important;
                box-shadow: 0 6px 28px rgba(181,136,247,0.6) !important;
                transform: translateY(-1px) !important;
            }
            div[data-testid="stButton"] button[kind="primary"]:active {
                transform: scale(0.97) translateY(0) !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        _, col_btn, _ = st.columns([1, 2, 1])
        col_btn.button("Find My Counselor →", use_container_width=True, type="primary",
                       on_click=lambda: st.session_state.update(quiz_step=1))

        st.markdown(
            """
            <div style="text-align:center; margin-top:14px; margin-bottom:28px;">
                <span style="font-size:13px; color:#9090A8;">⏱ Takes about 2 minutes &nbsp;·&nbsp; 🔒 Free &amp; confidential</span>
            </div>
            <div style="border-top: 1px solid rgba(0,0,0,0.07); margin: 0 auto 28px; max-width: 480px;"></div>
            <div style="display:flex; justify-content:center; align-items:center; gap:0; max-width:480px; margin:0 auto 8px;">
                <div style="flex:1; text-align:center; padding:12px 8px;">
                    <div style="font-size:20px; margin-bottom:6px;">🧩</div>
                    <div style="font-size:13px; font-weight:600; color:#1C1917; margin-bottom:3px; font-family:'Plus Jakarta Sans',sans-serif;">3 Quick Steps</div>
                    <div style="font-size:12px; color:#8B8B9A; line-height:1.5;">Answer a few short questions about yourself</div>
                </div>
                <div style="width:1px; height:60px; background:rgba(0,0,0,0.08); flex-shrink:0;"></div>
                <div style="flex:1; text-align:center; padding:12px 8px;">
                    <div style="font-size:20px; margin-bottom:6px;">🤖</div>
                    <div style="font-size:13px; font-weight:600; color:#1C1917; margin-bottom:3px; font-family:'Plus Jakarta Sans',sans-serif;">AI-Powered Matching</div>
                    <div style="font-size:12px; color:#8B8B9A; line-height:1.5;">Our model ranks counselors by predicted fit</div>
                </div>
                <div style="width:1px; height:60px; background:rgba(0,0,0,0.08); flex-shrink:0;"></div>
                <div style="flex:1; text-align:center; padding:12px 8px;">
                    <div style="font-size:20px; margin-bottom:6px;">✨</div>
                    <div style="font-size:13px; font-weight:600; color:#1C1917; margin-bottom:3px; font-family:'Plus Jakarta Sans',sans-serif;">Personalised Results</div>
                    <div style="font-size:12px; color:#8B8B9A; line-height:1.5;">See why each counselor is right for you</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── STEP 1: Demographics ─────────────────────────────────────────────────
    elif st.session_state.quiz_step == 1:
        _step1_form(ref)

    # ── STEP 2: Clinical Needs ───────────────────────────────────────────────
    elif st.session_state.quiz_step == 2:
        _step2_form(ref)

    # ── STEP 3: Preferences ──────────────────────────────────────────────────
    elif st.session_state.quiz_step == 3:
        _step3_form(ref)

    # ── STEP 4: Results ──────────────────────────────────────────────────────
    elif st.session_state.quiz_step == 4:
        def _full_reset():
            for fk in ["client_age", "client_gender", "client_ethnicity", "client_issue",
                       "previous_exp", "preferred_modality", "preferred_language", "preferred_c_gender",
                       "preferred_time",
                       "_age_ui", "_gender_ui", "_ethnicity_ui", "_issue_ui", "_prev_exp_ui"]:
                st.session_state.pop(fk, None)
            st.session_state.quiz_step = 0
            st.session_state.excluded_counselor_ids = []
            st.session_state.pop("_committed_match", None)
            st.session_state.pop("_global_sent_to", None)
            st.session_state.pop("_success_name", None)
            for k in list(st.session_state.keys()):
                if k.startswith("match_") or k.startswith("shap_") or k.startswith("explanation_single_"):
                    del st.session_state[k]

        # Read the FROZEN inputs captured when "Find My Best Match" was clicked,
        # so reruns on this page (opening a profile, dismissing a card) never
        # recompute the match with reverted widget state.
        if "_committed_match" not in st.session_state:
            st.session_state["_committed_match"] = _snapshot_match_inputs()
        mi = st.session_state["_committed_match"]

        client_age         = mi["client_age"]
        client_gender      = mi["client_gender"]
        client_ethnicity   = mi["client_ethnicity"]
        client_issue       = mi["client_issue"]
        previous_exp       = mi["prev_exp"]
        preferred_language = mi["preferred_language"]
        preferred_modality = mi["preferred_modality"]
        preferred_c_gender = mi["preferred_c_gender"]
        preferred_time     = mi["preferred_time"]

        _match_payload = {
            "client_age": client_age,
            "client_gender": client_gender,
            "client_ethnicity": client_ethnicity,
            "client_issue": client_issue,
            "prev_exp": int(previous_exp),
            "preferred_language": preferred_language,
            "preferred_modality": preferred_modality,
            "preferred_c_gender": preferred_c_gender,
            "preferred_time": preferred_time,
        }
        _match_cache_key = "match_" + hashlib.md5(
            _json.dumps(sorted(_match_payload.items())).encode()
        ).hexdigest()

        if _match_cache_key not in st.session_state:
            with st.spinner("Analyzing compatibility factors to find your ideal match..."):
                st.session_state[_match_cache_key] = post_match({**_match_payload, "exclude_ids": []})

        result = st.session_state[_match_cache_key]

        if result.get("error"):
            st.warning(result["error"])
            st.markdown("</div>", unsafe_allow_html=True)
            return

        ranked_key = _match_cache_key + "_all"
        if ranked_key not in st.session_state:
            st.session_state[ranked_key] = result.get("matches") or (
                [result["top_match"]] + ([result["second_match"]] if result.get("second_match") else [])
            )

        excluded_set = set(st.session_state.excluded_counselor_ids)
        ranked_list = [c for c in st.session_state[ranked_key] if c["counselor_id"] not in excluded_set]

        if not ranked_list:
            st.warning("You've dismissed all available counselors.")
            if st.button("↺  Start Over", key="start_over_empty", use_container_width=False):
                _start_over_dialog(_full_reset)
            st.markdown("</div>", unsafe_allow_html=True)
            return

        best_c   = ranked_list[0]
        second_c = ranked_list[1] if len(ranked_list) > 1 else None
        best_features = best_c.get("features") or result.get("best_features", {})

        st.markdown('<div id="match-results-anchor"></div>', unsafe_allow_html=True)
        scroll_to_results()

        def _dismiss(idx):
            dismissed_id = ranked_list[idx]["counselor_id"]
            st.session_state.excluded_counselor_ids = (
                st.session_state.excluded_counselor_ids + [dismissed_id]
            )

        # ── Match Explanation + SHAP ──────────────────────────────────────────
        def _get_explanation(c):
            key = f"explanation_single_{c.get('counselor_id')}"
            if not isinstance(st.session_state.get(key), str):
                st.session_state[key] = _generate_explanation(c, client_issue)
            return st.session_state[key]

        counselor_name = best_c.get("name", "Your Top Match").upper()

        # Paired header row
        st.markdown('<p style="color:#B588F7; text-transform:uppercase; font-size:16px; letter-spacing:0.1em; font-family:\'Plus Jakarta Sans\', sans-serif; font-weight:700; margin:8px 0 24px;">YOUR MATCHES</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="large")
        with col1:
            render_counselor_card(best_c, best_c["compatibility_score"], is_primary=True, dismiss_key="dismiss_0")
            if st.button("__dismiss0__", key="dismiss_0", use_container_width=True):
                _dismiss(0)
                st.rerun()
        with col2:
            explanation = _get_explanation(best_c)
            if explanation:
                st.markdown(
                    f'<div class="ai-explanation-box" style="margin-bottom:16px;">'
                    f'<div class="ai-badge">✦ Why {counselor_name}?</div>'
                    f'<p style="font-size:15.5px;color:#2D2D3F;line-height:1.7;margin:0;">{explanation}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with st.expander("Technical details — SHAP feature contributions", expanded=False):
                _shap_cache_key = "shap_" + hashlib.md5(
                    _json.dumps(sorted(best_features.items())).encode()
                ).hexdigest()
                if _shap_cache_key not in st.session_state:
                    st.session_state[_shap_cache_key] = post_shap(best_features)
                shap_result = st.session_state[_shap_cache_key]
                if shap_result.get("error"):
                    st.info(shap_result["error"])
                else:
                    readable_names = {
                        "issue_match":        "Issue Similarity",
                        "modality_issue_fit": "Issue-Modality Fit",
                        "modality_match":     "Preferred Modality Match",
                        "gender_match":       "Preferred Gender Match",
                        "exp_issue_fit":      "Counselor Seniority",
                        "ethnicity_match":    "Ethnicity Match",
                        "prev_exp":           "Client Previous Experience",
                        "age_gap":            "Age Gap",
                    }
                    try:
                        names  = shap_result["feature_names"]
                        values = shap_result["shap_values"]
                        fvals  = shap_result["feature_values"]
                        order  = sorted(range(len(values)), key=lambda i: abs(values[i]), reverse=True)
                        max_abs = max(abs(v) for v in values) or 1.0

                        rows_html = ""
                        for i in order:
                            label = readable_names.get(names[i], names[i])
                            fval  = fvals[i]
                            sv    = values[i]
                            pct   = abs(sv) / max_abs * 100
                            color = "#10B981" if sv >= 0 else "#EF4444"
                            sign  = f"+{sv:.3f}" if sv >= 0 else f"{sv:.3f}"
                            fval_str = f"{fval:.2f}" if isinstance(fval, float) else str(fval)

                            rows_html += f"""
                            <div style="display:flex; align-items:center; gap:8px; padding:7px 0; border-bottom:1px solid #F3F0F8;">
                                <div style="flex:2; min-width:0; font-size:12.5px; color:#4A4A5A; text-align:right; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{label}</div>
                                <div style="width:32px; font-size:11px; color:#9090A8; text-align:right; flex-shrink:0;">{fval_str}</div>
                                <div style="flex:1.5; min-width:30px; position:relative; height:10px; background:#F3F0F8; border-radius:6px; overflow:hidden;">
                                    <div style="position:absolute; top:0; height:10px; width:{pct/2:.1f}%; background:{color}; border-radius:6px;
                                        {'left:50%' if sv >= 0 else f'right:50%'};"></div>
                                    <div style="position:absolute; top:0; left:50%; width:1px; height:10px; background:rgba(0,0,0,0.15);"></div>
                                </div>
                                <div style="width:48px; font-size:12.5px; font-weight:700; color:{color}; flex-shrink:0; text-align:right;">{sign}</div>
                            </div>"""

                        st.markdown(
                            f"""
                            <div style="font-size:11px; font-weight:600; color:#B588F7; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:12px; font-family:'Plus Jakarta Sans',sans-serif;">Feature contributions</div>
                            <div style="display:flex; align-items:center; gap:8px; padding:0 0 6px; border-bottom:2px solid #F0E8E6;">
                                <div style="flex:2; min-width:0; font-size:11px; color:#A0A0B8; text-align:right;">Feature</div>
                                <div style="width:32px; font-size:11px; color:#A0A0B8; text-align:right; flex-shrink:0;">Value</div>
                                <div style="flex:1.5; min-width:30px; font-size:11px; color:#A0A0B8; text-align:center;">Impact</div>
                                <div style="width:48px; font-size:11px; color:#A0A0B8; flex-shrink:0; text-align:right;">SHAP</div>
                            </div>
                            {rows_html}
                            <div style="display:flex; gap:16px; margin-top:12px; font-size:11px; color:#8B8B9A;">
                                <span><span style="display:inline-block;width:10px;height:10px;background:#10B981;border-radius:2px;margin-right:5px;vertical-align:middle;"></span>Increases match</span>
                                <span><span style="display:inline-block;width:10px;height:10px;background:#EF4444;border-radius:2px;margin-right:5px;vertical-align:middle;"></span>Decreases match</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    except Exception as exc:
                        st.info(f"Could not render feature contributions: {exc}")

        components.html(
            """
            <script>
            (function() {
                function run() {
                    var doc = window.parent.document;
                    doc.querySelectorAll('.card-view-btn').forEach(function(btn) {
                        if (btn._ready) return;
                        var container = btn.closest('[data-testid="stElementContainer"]');
                        if (!container) return;
                        var sibling = container.nextElementSibling;
                        while (sibling) {
                            var stBtn = sibling.querySelector('[data-testid="stButton"] button');
                            if (stBtn) {
                                btn._ready = true;
                                (function(b, nb) {
                                    b.addEventListener('click', function() { nb.click(); });
                                })(btn, stBtn);
                                break;
                            }
                            sibling = sibling.nextElementSibling;
                        }
                    });
                }
                // Run now, after short delays, and on every DOM mutation
                [0, 150, 400, 800].forEach(function(t) { setTimeout(run, t); });
                new MutationObserver(run).observe(
                    window.parent.document.body,
                    { subtree: true, childList: true }
                );
            })();
            </script>
            """,
            height=0, width=0,
        )

        # Wire X overlay buttons to hidden Streamlit dismiss buttons
        components.html("""
        <script>
        (function() {
            function wireDismiss() {
                var doc = window.parent.document;
                // Wire each .dismiss-x / .dismiss-x-light to its hidden Streamlit button
                // Find the button via its container's st-key-* class (reliable, no text matching)
                doc.querySelectorAll('[data-dismiss]').forEach(function(xBtn) {
                    if (xBtn._wired) return;
                    var key = xBtn.getAttribute('data-dismiss');
                    var container = doc.querySelector('.st-key-' + key);
                    if (!container) return;
                    var target = container.querySelector('button');
                    if (target) {
                        xBtn._wired = true;
                        xBtn.addEventListener('click', function(e) {
                            e.stopPropagation();
                            target.click();
                        });
                    }
                });
            }
            [0, 150, 400, 800].forEach(function(t) { setTimeout(wireDismiss, t); });
            new MutationObserver(wireDismiss).observe(
                window.parent.document.body, { subtree: true, childList: true }
            );
        })();
        </script>
        """, height=0, width=0)

        # ── 2nd option below ─────────────────────────────────────────────────
        if second_c:
            st.markdown(
                """
                <div style="display:flex; align-items:center; gap:16px; margin: 16px 0 32px;">
                    <div style="flex:1; height:1px; background:rgba(0,0,0,0.10);"></div>
                    <span style="font-size:11px; font-weight:600; color:#B0A9C0; letter-spacing:0.1em; text-transform:uppercase; white-space:nowrap;">Also consider</span>
                    <div style="flex:1; height:1px; background:rgba(0,0,0,0.10);"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            sec_col, _ = st.columns([1, 1], gap="large")
            with sec_col:
                render_counselor_card(second_c, second_c["compatibility_score"], is_primary=False, dismiss_key="dismiss_1")
                if st.button("__dismiss1__", key="dismiss_1", use_container_width=True):
                    _dismiss(1)
                    st.rerun()

        # ── Start Over ───────────────────────────────────────────────────────
        st.markdown("""
        <div style="height:32px;"></div>
        <div style="display:flex; align-items:center; gap:16px; margin-bottom:20px;">
            <div style="flex:1; height:1px; background:rgba(0,0,0,0.08);"></div>
            <span style="font-size:11px; color:#C0C0CC; letter-spacing:0.08em; text-transform:uppercase; white-space:nowrap;">Not happy with your results?</span>
            <div style="flex:1; height:1px; background:rgba(0,0,0,0.08);"></div>
        </div>
        """, unsafe_allow_html=True)
        _, center, _ = st.columns([2, 1, 2])
        with center:
            if st.button("↺  Start Over", key="start_over_bottom", use_container_width=True):
                _start_over_dialog(_full_reset)
        components.html("""
        <script>
        (function() {
            function styleStartOver() {
                var doc = window.parent.document;
                doc.querySelectorAll('button').forEach(function(btn) {
                    if (btn.innerText.trim().startsWith('↺')) {
                        btn.style.setProperty('background', 'transparent', 'important');
                        btn.style.setProperty('color', '#EF4444', 'important');
                        btn.style.setProperty('border', '1.5px solid rgba(239,68,68,0.45)', 'important');
                        btn.style.setProperty('border-radius', '50px', 'important');
                        btn.style.setProperty('font-size', '13px', 'important');
                        btn.style.setProperty('font-weight', '600', 'important');
                        btn.style.setProperty('letter-spacing', '0.04em', 'important');
                        btn.style.setProperty('box-shadow', 'none', 'important');
                        btn.onmouseenter = function() {
                            this.style.setProperty('background', 'rgba(239,68,68,0.07)', 'important');
                            this.style.setProperty('border-color', '#EF4444', 'important');
                        };
                        btn.onmouseleave = function() {
                            this.style.setProperty('background', 'transparent', 'important');
                            this.style.setProperty('border-color', 'rgba(239,68,68,0.45)', 'important');
                        };
                    }
                });
            }
            [0, 150, 400].forEach(function(t) { setTimeout(styleStartOver, t); });
            new MutationObserver(styleStartOver).observe(
                window.parent.document.body, { subtree: true, childList: true }
            );
        })();
        </script>
        """, height=0, width=0)

    st.markdown('</div>', unsafe_allow_html=True)
