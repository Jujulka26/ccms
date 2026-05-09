import base64
import hashlib
import json as _json
import os
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import time
import google.generativeai as genai

from frontend.utils.api import get_reference_data, post_match, post_shap, save_intro_request
from frontend.utils.avatar import avatar_html

# ── Custom CSS ────────────────────────────────────────────────────────────────
def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
        .stApp { background: #F7F5F0; }

        .hero-wrap {
            background-color: #FAFAFF;
            background-image:
                radial-gradient(at 0% 0%, #E9DFFF 0px, transparent 60%),
                radial-gradient(at 100% 100%, #F0E6FF 0px, transparent 60%);
            border-radius: 20px;
            padding: 56px 52px 48px;
            margin-bottom: 32px;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(124,58,237,0.15);
            box-shadow: 0 16px 32px -8px rgba(124,58,237,0.12), inset 0 1px 0 rgba(255,255,255,0.9);
        }
        .hero-eyebrow {
            display: inline-block;
            font-size: 11px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase;
            color: #8B5CF6; background: rgba(167,139,250,0.12); border: 1px solid rgba(167,139,250,0.25);
            border-radius: 20px; padding: 4px 14px; margin-bottom: 20px;
        }
        .hero-title { font-family: 'DM Serif Display', serif; font-size: 42px; line-height: 1.15; color: #1A1A2E; margin: 0 0 16px; letter-spacing: -0.5px; }
        .hero-subtitle { font-size: 16px; color: #4A4A5C; max-width: 480px; line-height: 1.65; margin: 0; }
        .hero-stats { display: flex; gap: 40px; margin-top: 40px; padding-top: 32px; border-top: 1px solid rgba(0,0,0,0.08); }
        .hero-stat-num { font-family: 'DM Serif Display', serif; font-size: 28px; color: #1A1A2E; line-height: 1; }
        .hero-stat-label { font-size: 12px; color: #8B8B9A; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.06em; }
        .hero-content { display: flex; align-items: center; position: relative; z-index: 2; }
        .hero-text { flex: 1; min-width: 0; max-width: 60%; }
        .hero-image-wrap { position: absolute; bottom: -48px; right: -20px; width: 50%; height: 130%; pointer-events: none; z-index: 1; }
        .hero-img { width: 100%; height: 100%; object-fit: contain; object-position: right center; opacity: 0.9; mix-blend-mode: multiply; -webkit-mask-image: linear-gradient(to right, transparent 0%, rgba(0,0,0,0.5) 30%, black 60%); mask-image: linear-gradient(to right, transparent 0%, rgba(0,0,0,0.5) 30%, black 60%); }

        .form-card {
            background: radial-gradient(1200px 300px at -10% -30%, rgba(139,92,246,0.08) 0%, transparent 60%), radial-gradient(900px 260px at 110% 120%, rgba(109,40,217,0.06) 0%, transparent 55%), #FFFFFF;
            border-radius: 24px; padding: 28px 36px 24px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 12px 32px -16px rgba(31,31,60,0.10), 0 1px 3px rgba(0,0,0,0.03);
            margin-bottom: 24px;
        }
        .step-header { display: flex; align-items: center; gap: 14px; margin-bottom: 6px; }
        .step-chip { width: 34px; height: 34px; border-radius: 50%; background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%); color: #FFFFFF; font-family: 'DM Sans', sans-serif; font-weight: 700; font-size: 14px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(124,58,237,0.35); flex-shrink: 0; }
        .step-title { font-family: 'DM Serif Display', serif; font-size: 24px; color: #1A1A2E; line-height: 1.2; }
        .step-copy { font-size: 14px; color: #5A5A6E; margin: 4px 0 16px 48px; line-height: 1.55; }
        .section-label { font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #8B5CF6; margin: 0 0 20px; }
        .section-divider { border: none; border-top: 1px solid #E5E5E5; margin: 0px 0 20px 0 !important; position: relative; z-index: 10; }

        [data-testid="block-container"] [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
        [data-testid="stRadio"] > div, [role="radiogroup"] { margin-bottom: 0 !important; padding-bottom: 0 !important; }

        div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] > div > div {
            border-radius: 10px !important; border: 1.5px solid #E5E2DC !important; background: #FAFAF8 !important;
            font-family: 'DM Sans', sans-serif !important; font-size: 14px !important; transition: border-color 0.2s;
        }
        div[data-testid="stNumberInput"] input:focus, div[data-testid="stSelectbox"] > div > div:focus-within {
            border-color: #8B5CF6 !important; box-shadow: 0 0 0 3px rgba(139,92,246,0.1) !important;
        }
        label[data-testid="stWidgetLabel"] p, label[data-testid="stWidgetLabel"] div, label[data-testid="stWidgetLabel"] span {
            font-size: 18px !important; font-weight: 600 !important; color: #1A1A2E !important; margin-bottom: 10px !important;
        }

        [data-testid="block-container"] [data-baseweb="radio"] > div:first-child,
        [data-testid="block-container"] [data-baseweb="radio"] input[type="radio"],
        [data-testid="block-container"] [role="radiogroup"] > label > div:first-child {
            position: absolute !important; width: 1px !important; height: 1px !important; opacity: 0 !important; pointer-events: none !important; overflow: hidden !important;
        }
        [data-testid="block-container"] [data-baseweb="radio"] { padding: 9px 22px !important; background: #F7F5F0 !important; border: 1.5px solid #E5E2DC !important; border-radius: 30px !important; cursor: pointer !important; transition: background 0.18s ease, border-color 0.18s ease !important; margin-right: 2px !important; }
        [data-testid="block-container"] [data-baseweb="radio"]:hover { border-color: #8B5CF6 !important; background: rgba(139,92,246,0.06) !important; }
        [data-testid="block-container"] [data-baseweb="radio"]:has(input:checked) { background: rgba(249,115,22,0.08) !important; border-color: #F97316 !important; }
        [data-testid="block-container"] [data-baseweb="radio"]:has(input:checked) p { font-weight: 700 !important; }
        [data-testid="block-container"] [data-baseweb="radio"] p { font-size: 14px !important; margin: 0 !important; color: #4A4A5A !important; font-weight: 500 !important; }

        [data-testid="block-container"] div[data-testid="stButton"] button { border-radius: 12px !important; font-family: 'DM Sans', sans-serif !important; font-size: 15px !important; font-weight: 600 !important; padding: 10px 24px !important; transition: all 0.2s; width: 100% !important; }
        [data-testid="block-container"] div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%) !important; color: #FFFFFF !important; border: none !important; box-shadow: 0 4px 14px rgba(124,58,237,0.35); }
        [data-testid="block-container"] div[data-testid="stButton"] button[kind="primary"]:hover { box-shadow: 0 6px 20px rgba(124,58,237,0.45) !important; transform: translateY(-1px); }

        .result-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px; }
        .result-card { position: relative; background: #FFFFFF; border-radius: 20px; padding: 28px 28px 0; border: 1px solid rgba(0,0,0,0.06); margin-bottom: 0px; overflow: hidden; }
        .dismiss-x { position: absolute; top: 12px; right: 12px; width: 28px; height: 28px; border-radius: 50%; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.18); color: rgba(255,255,255,0.5); font-size: 13px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.18s ease; line-height: 1; z-index: 10; }
        .dismiss-x:hover { background: rgba(239,68,68,0.18); border-color: rgba(239,68,68,0.5); color: #EF4444; }
        .dismiss-x-light { position: absolute; top: 12px; right: 12px; width: 28px; height: 28px; border-radius: 50%; background: rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.1); color: #B0B0C0; font-size: 13px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.18s ease; line-height: 1; z-index: 10; }
        .dismiss-x-light:hover { background: rgba(239,68,68,0.08); border-color: rgba(239,68,68,0.35); color: #EF4444; }
        .st-key-dismiss_0, .st-key-dismiss_1 { display: none !important; }
        [class*="st-key-vp_"] { display: none !important; }
        .result-card.primary { background: #1A1A2E; border-color: transparent; }
        .card-view-btn { display: block; width: calc(100% + 56px); margin: 24px -28px 0; padding: 14px 28px; background: transparent; border: none; border-top: 1px solid rgba(0,0,0,0.07); color: #7C3AED; font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; cursor: pointer; text-align: center; font-family: 'DM Sans', sans-serif; transition: background 0.15s, color 0.15s; }
        .result-card.primary .card-view-btn { border-top-color: rgba(255,255,255,0.08); color: rgba(255,255,255,0.55); }
        .card-view-btn:hover { background: rgba(124,58,237,0.07); color: #5B21B6; }
        .result-card.primary .card-view-btn:hover { background: rgba(255,255,255,0.06); color: #FFFFFF; }
        .result-card-badge { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; border-radius: 20px; padding: 4px 12px; display: inline-block; margin-bottom: 0; align-self: flex-start; }
        .badge-primary { background: rgba(139,92,246,0.2); color: #A78BFA; }
        .badge-secondary { background: #F0EDE8; color: #8B8B9A; }
        .card-header { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; }
        .card-header-photo { flex-shrink: 0; }
        .card-header-info { flex: 1; min-width: 0; display: flex; flex-direction: column; align-items: flex-start; gap: 6px; }
        .compat-score { font-family: 'DM Serif Display', serif; font-size: 32px; line-height: 1; color: #FFFFFF; margin: 0; padding-left: 10px; }
        .compat-score-secondary { font-family: 'DM Serif Display', serif; font-size: 32px; line-height: 1; color: #1A1A2E; margin: 0; padding-left: 10px; }
        .compat-label { font-size: 10px; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.08em; margin: 0; padding-left: 10px; }
        .compat-label-secondary { font-size: 10px; color: #A0A0B0; text-transform: uppercase; letter-spacing: 0.08em; margin: 0; padding-left: 10px; }
        .counselor-name { font-size: 18px; font-weight: 700; color: #FFFFFF; margin: 0; padding-left: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
        .counselor-name-secondary { font-size: 18px; font-weight: 700; color: #1A1A2E; margin: 0; padding-left: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
        .info-row { display: flex; justify-content: space-between; align-items: center; padding: 11px 0; border-bottom: 1px solid rgba(255,255,255,0.07); }
        .info-row-secondary { display: flex; justify-content: space-between; align-items: center; padding: 11px 0; border-bottom: 1px solid #F0EDE8; }
        .info-key { font-size: 12px; color: rgba(255,255,255,0.4); }
        .info-key-secondary { font-size: 12px; color: #A0A0B0; }
        .info-val { font-size: 13px; color: rgba(255,255,255,0.85); font-weight: 500; }
        .info-val-secondary { font-size: 13px; color: #2D2D3F; font-weight: 500; }

        .explain-card { background: #FFFFFF; border-radius: 20px; padding: 32px 36px; border: 1px solid rgba(0,0,0,0.06); margin-bottom: 24px; }
        .explain-title { font-family: 'DM Serif Display', serif; font-size: 22px; color: #1A1A2E; margin: 0 0 24px; }
        .point-row-wrap { display: flex; flex-direction: column; gap: 12px; margin-top: 12px; }
        .point-row { display: flex; align-items: center; gap: 14px; padding: 14px 18px; border-radius: 14px; font-size: 14.5px; font-weight: 500; transition: all 0.2s ease; }
        .point-row-green { background: rgba(16,185,129,0.06); border: 1px solid rgba(16,185,129,0.15); color: #065F46; }
        .point-row-amber { background: rgba(245,158,11,0.06); border: 1px solid rgba(245,158,11,0.15); color: #92400E; }
        .icon-circle { display: flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; flex-shrink: 0; }
        .icon-circle.green { background: #10B981; color: #fff; }
        .icon-circle.amber { background: #F59E0B; color: #fff; }

        .ai-explanation-box { background: linear-gradient(135deg, #F8F5FF 0%, #FDF9FF 100%); border: 1px solid rgba(139,92,246,0.15); border-left: 3px solid #8B5CF6; border-radius: 0 16px 16px 0; padding: 24px 28px; margin-top: 4px; }
        .ai-explanation-box-alt { background: #FAFAF8; border: 1px solid rgba(0,0,0,0.06); border-left: 3px solid #A0A0B0; border-radius: 0 16px 16px 0; padding: 20px 24px; margin-top: 4px; }
        .ai-badge { display: inline-flex; align-items: center; gap: 6px; background: linear-gradient(135deg, #8B5CF6, #6D28D9); color: #fff; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; padding: 4px 12px; border-radius: 20px; margin-bottom: 14px; }
        .ai-badge-alt { display: inline-flex; align-items: center; gap: 6px; background: #6B7280; color: #fff; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; padding: 4px 12px; border-radius: 20px; margin-bottom: 12px; }
        .ai-explanation-text { font-size: 15.5px; color: #2D2D3F; line-height: 1.85; font-weight: 400; margin: 0; font-style: italic; }
        .ai-explanation-text-alt { font-size: 14.5px; color: #4A4A5A; line-height: 1.8; font-weight: 400; margin: 0; font-style: italic; }

        div[data-testid="stTabs"] button { font-family: 'DM Sans', sans-serif !important; font-size: 14px !important; font-weight: 500 !important; }

        [data-testid="block-container"] div[data-testid="stButton"] button:not([kind="primary"]) {
            background: transparent !important;
            border: 1.5px solid rgba(109,40,217,0.25) !important;
            color: #6D28D9 !important;
            border-radius: 12px !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            letter-spacing: 0.03em !important;
            padding: 10px 20px !important;
            transition: all 0.2s ease !important;
            box-shadow: none !important;
        }
        [data-testid="block-container"] div[data-testid="stButton"] button:not([kind="primary"]):hover {
            background: rgba(109,40,217,0.06) !important;
            border-color: #6D28D9 !important;
            color: #5B21B6 !important;
        }

        div[data-testid="stExpander"] {
            background: #FFFFFF;
            border: 1px solid rgba(109,40,217,0.15) !important;
            border-radius: 16px !important;
            overflow: hidden;
            margin-bottom: 24px;
            box-shadow: none !important;
        }
        div[data-testid="stExpander"] summary {
            padding: 12px 20px !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            letter-spacing: 0.07em !important;
            text-transform: uppercase !important;
            color: #6D28D9 !important;
            background: linear-gradient(135deg, #F8F5FF 0%, #FDF9FF 100%) !important;
            border-radius: 16px !important;
            border-bottom: 1px solid rgba(109,40,217,0.10);
            list-style: none;
        }
        div[data-testid="stExpander"] summary:hover {
            background: linear-gradient(135deg, #F0EBFF 0%, #F8F5FF 100%) !important;
            color: #5B21B6 !important;
        }
        div[data-testid="stExpander"] summary svg { color: #8B5CF6 !important; }
        div[data-testid="stExpander"] > details > div[data-testid="stExpanderDetails"] {
            padding: 24px !important;
            background: #FFFFFF;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sorted_options(lst):
    return sorted([v for v in lst if str(v).strip()])


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
    nodes_html = ""
    for i, name in enumerate(step_names, 1):
        if i < step:
            circle_bg = "linear-gradient(135deg,#8B5CF6 0%,#6D28D9 100%)"
            circle_color = "#FFFFFF"; circle_border = "none"; shadow = "0 4px 12px rgba(124,58,237,0.30)"
            label_color = "#6D28D9"; weight = "600"; inner = "✓"
        elif i == step:
            circle_bg = "linear-gradient(135deg,#8B5CF6 0%,#6D28D9 100%)"
            circle_color = "#FFFFFF"; circle_border = "none"; shadow = "0 6px 16px rgba(124,58,237,0.40), 0 0 0 4px rgba(139,92,246,0.15)"
            label_color = "#1A1A2E"; weight = "700"; inner = str(i)
        else:
            circle_bg = "#FFFFFF"; circle_color = "#B0A9A0"; circle_border = "1.5px solid #E5E0D8"
            shadow = "none"; label_color = "#B0A9A0"; weight = "500"; inner = str(i)
        nodes_html += (
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:8px;z-index:2;background:transparent;">'
            f'<div style="width:34px;height:34px;border-radius:50%;background:{circle_bg};color:{circle_color};'
            f'border:{circle_border};display:flex;align-items:center;justify-content:center;'
            f'font-family:\'DM Sans\',sans-serif;font-weight:700;font-size:13px;box-shadow:{shadow};">{inner}</div>'
            f'<span style="font-size:11.5px;color:{label_color};font-weight:{weight};letter-spacing:0.02em;">{name}</span>'
            f'</div>'
        )
    fill_pct = max(0, min(100, int((step - 1) / (total - 1) * 100))) if total > 1 else 0
    st.markdown(
        f"""
        <div style="position:relative;padding:4px 8px 8px;margin-bottom:30px;">
            <div style="position:absolute;left:calc(8px + 17px);right:calc(8px + 17px);top:calc(4px + 17px);height:2px;background:#EDE8E3;border-radius:2px;z-index:1;"></div>
            <div style="position:absolute;left:calc(8px + 17px);top:calc(4px + 17px);width:calc((100% - 16px - 34px) * {fill_pct} / 100);height:2px;background:linear-gradient(90deg,#8B5CF6,#6D28D9);border-radius:2px;z-index:1;"></div>
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


def render_hero_new():
    if "hero_img_2_b64" not in st.session_state:
        try:
            with open(os.path.join("assets", "ccmatchlogo.png"), "rb") as f:
                st.session_state["hero_img_2_b64"] = base64.b64encode(f.read()).decode()
        except FileNotFoundError:
            st.session_state["hero_img_2_b64"] = None
    b64 = st.session_state["hero_img_2_b64"]
    img_tag = f'<img src="data:image/png;base64,{b64}" class="hero-img" alt="" />' if b64 else ""
    st.markdown(
        f"""
        <div class="hero-wrap">
            <div class="hero-content">
                <div class="hero-text">
                    <div class="hero-eyebrow">AI-Powered Matching</div>
                    <h1 class="hero-title">Find Your<br><em>Ideal Counselor</em></h1>
                    <p class="hero-subtitle">Our model analyses compatibility across specialization, language, modality and personal fit — ranked by predicted outcome.</p>
                </div>
                <div class="hero-image-wrap">{img_tag}</div>
            </div>
            <div class="hero-stats">
                <div><div class="hero-stat-num">9</div><div class="hero-stat-label">Match factors</div></div>
                <div><div class="hero-stat-num">ML</div><div class="hero-stat-label">Powered</div></div>
                <div><div class="hero-stat-num">SHAP</div><div class="hero-stat-label">Explainability</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_counselor_card(c: dict, score: float, is_primary=True, dismiss_key: str | None = None):
    langs = c.get("counselor_language") or "—"
    mods = c.get("counselor_modality") or "—"
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
                <div class="info-row"><span class="info-key">Experience</span><span class="info-val">{c['experience_years']} yrs</span></div>
                <div class="info-row"><span class="info-key">Specialization</span><span class="info-val">{c['specialization']}</span></div>
                <div class="info-row"><span class="info-key">Modality</span><span class="info-val">{mods}</span></div>
                <div class="info-row" style="border:none"><span class="info-key">Language</span><span class="info-val">{langs}</span></div>
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
                <div class="info-row-secondary"><span class="info-key-secondary">Experience</span><span class="info-val-secondary">{c['experience_years']} yrs</span></div>
                <div class="info-row-secondary"><span class="info-key-secondary">Specialization</span><span class="info-val-secondary">{c['specialization']}</span></div>
                <div class="info-row-secondary"><span class="info-key-secondary">Modality</span><span class="info-val-secondary">{mods}</span></div>
                <div class="info-row-secondary" style="border:none"><span class="info-key-secondary">Language</span><span class="info-val-secondary">{langs}</span></div>
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
    spec         = c.get("specialization", "")
    modality     = c.get("counselor_modality", "—")
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
    .prof-header { display:flex; align-items:center; gap:20px; margin-bottom:16px; }
    .prof-name { font-family:'DM Serif Display',serif; font-size:22px; color:#1A1A2E; margin:0 0 3px; line-height:1.2; }
    .prof-role { font-size:12px; color:#8B5CF6; font-weight:600; margin:0 0 7px; }
    .prof-meta { display:flex; flex-wrap:wrap; column-gap:14px; row-gap:3px; }
    .prof-meta-item { font-size:12.5px; color:#5A5A6E; }
    .prof-meta-score { font-size:18px; color:#7C3AED; font-weight:700; }
    .prof-score-chip { display:inline-flex; align-items:center; background:#F3F0FF; color:#6D28D9; font-size:11px; font-weight:700; letter-spacing:0.06em; padding:2px 10px; border-radius:20px; border:1px solid rgba(109,40,217,0.2); margin-bottom:6px; }
    .prof-rule { border:none; border-top:1px solid #EBEBEB; margin:14px 0 16px; }
    .prof-label { font-size:11px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:#8B5CF6; margin:0 0 8px; }
    .prof-section { margin-bottom:18px; }
    .prof-about { font-size:12.5px; color:#2D2D3F; line-height:1.75; margin:0; }
    .prof-pills { display:flex; flex-wrap:wrap; gap:6px; }
    .prof-pill { background:#F3F0FF; color:#6D28D9; font-size:12px; font-weight:600; padding:4px 12px; border-radius:20px; border:1px solid rgba(109,40,217,0.15); }
    .prof-thought { font-size:13.5px; color:#4A4A5A; font-style:italic; line-height:1.65; padding-left:12px; border-left:2px solid #D8D0F5; margin-bottom:8px; }
    .prof-thought:last-child { margin-bottom:0; }
    div[data-testid="stExpander"] { background:#FFFFFF !important; border:1px solid #EBEBEB !important; border-radius:12px !important; box-shadow:none !important; margin-bottom:0 !important; }
    div[data-testid="stExpander"] summary { background:#FFFFFF !important; font-size:13px !important; font-weight:600 !important; color:#4A4A5A !important; text-transform:none !important; letter-spacing:0 !important; padding:12px 16px !important; border-radius:12px !important; }
    div[data-testid="stExpander"] summary:hover { background:#F7F5FF !important; color:#6D28D9 !important; }
    div[data-testid="stExpander"] svg { color:#8B5CF6 !important; }
    div[data-testid="stDialog"] [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:first-child { margin-top:-16px !important; }
    </style>
    """, unsafe_allow_html=True)

    score_item = f'<span class="prof-meta-score">✦ {score:.1f}%</span>' if score else ""
    _translate = '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#5A5A6E" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:3px;"><path d="M5 8l6 6"/><path d="M4 14l6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="M22 22l-5-10-5 10"/><path d="M14 18h6"/></svg>'
    meta_html = (
        f'<span class="prof-meta-item">💼 {exp} yrs exp</span>'
        + (f'<span class="prof-meta-item">{_translate}{lang}</span>' if lang and lang != "—" else "")
    )
    st.markdown(
        f'<div class="prof-header">{av}'
        f'<div style="padding-left:6px;">'
        f'<div style="display:flex;align-items:baseline;gap:10px;">'
        f'<div class="prof-name">{name}</div>{score_item}</div>'
        f'<div class="prof-role">Licensed Counselor</div>'
        f'<div class="prof-meta">{meta_html}</div></div></div>'
        f'<hr class="prof-rule">',
        unsafe_allow_html=True,
    )

    if about.strip():
        st.markdown(
            f'<div class="prof-section"><div class="prof-label">About</div>'
            f'<p class="prof-about">{about}</p></div>',
            unsafe_allow_html=True,
        )

    if pills:
        pills_html = "".join(f'<span class="prof-pill">{p}</span>' for p in pills)
        st.markdown(
            f'<div class="prof-section"><div class="prof-label">Areas of Expertise</div>'
            f'<div class="prof-pills">{pills_html}</div></div>',
            unsafe_allow_html=True,
        )

    if thoughts:
        rows = "".join(f'<div class="prof-thought">"{t}"</div>' for t in thoughts)
        st.markdown(
            f'<div class="prof-section"><div class="prof-label">You might be thinking...</div>{rows}</div>',
            unsafe_allow_html=True,
        )

    if modality_desc.strip():
        st.markdown(
            f'<div class="prof-section"><div class="prof-label">How I work with you</div>'
            f'<p class="prof-about">{modality_desc}</p></div>',
            unsafe_allow_html=True,
        )

    st.write("")

    req_state_key = f"req_{c.get('counselor_id')}"
    if req_state_key not in st.session_state:
        st.session_state[req_state_key] = False

    def toggle_req(val):
        st.session_state[req_state_key] = val

    if not st.session_state[req_state_key]:
        st.button(f"✉️ Get to know {name}", use_container_width=True, type="primary",
                  on_click=toggle_req, args=(True,))
    else:
        st.caption(
            f"Leave your details below. The clinic coordinator will connect you with {name} via email."
        )
        client_name  = st.text_input("Your Full Name")
        client_email = st.text_input("Your Email Address")
        st.write("")

        col1, col2 = st.columns(2)
        col1.button("Cancel", use_container_width=True, on_click=toggle_req, args=(False,))
        if col2.button("Send Request", use_container_width=True, type="primary"):
            if not client_name.strip() or not client_email.strip():
                st.error("Please fill in both your name and email.")
            else:
                save_intro_request(
                    client_name.strip(), client_email.strip(),
                    int(c.get("counselor_id")), float(score) if score else 0.0,
                )
                st.success(f"Request sent! We will connect you with {name} soon.")
                time.sleep(2)
                st.session_state.quiz_step = 0
                st.session_state[req_state_key] = False
                st.rerun()


# ── Gemini match explanation ──────────────────────────────────────────────────
def _counselor_summary(c) -> str:
    gender = c.get("gender", "").lower()
    pronoun = "she/her" if gender in ["female", "woman"] else ("he/him" if gender in ["male", "man"] else "they/them")
    modality_match = "Yes" if c.get("modality_match") == 1 else "No"
    gender_match = "Yes" if c.get("gender_match") == 1 else "No"
    return (
        f"- Name: {c.get('name')}, {pronoun}, {c.get('experience_years')} years experience\n"
        f"- Specialization: {c.get('specialization')}\n"
        f"- Session modality: {c.get('counselor_modality')} (matches client preference: {modality_match})\n"
        f"- Language: {c.get('counselor_language')}\n"
        f"- About: {c.get('about_me') or 'N/A'}\n"
        f"- Gender preference matched: {gender_match}"
    )


def get_gemini_explanation(c, client_issue, preferred_language, preferred_modality, preferred_c_gender, client_age, previous_exp) -> str | None:
    """Generate a single counselor explanation. Cache by counselor_id externally."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    prev_text = "has previously tried counseling" if previous_exp else "is new to counseling"
    gender_pref_text = (
        f"prefers a {preferred_c_gender} counselor"
        if preferred_c_gender not in ["No preference", ""]
        else "has no gender preference"
    )

    prompt = f"""You are a warm, empathetic counseling match assistant for a mental health platform in Malaysia.

A client is seeking support for: {client_issue}
Client profile:
- Age: {client_age}, {prev_text}, {gender_pref_text}
- Preferred language: {preferred_language}
- Preferred session modality: {preferred_modality}

Matched counselor:
{_counselor_summary(c)}

Write a warm, personal 3-4 sentence paragraph explaining why this counselor is a good match for the client. Speak directly to the client using "you"/"your". Do not mention numbers or scores. If there is a mismatch (modality or gender), acknowledge it briefly in a reassuring way.

Respond with plain text only. No JSON, no markdown."""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return None



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


# ── Main page ─────────────────────────────────────────────────────────────────
def show_matching_page():
    inject_styles()

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
    if "preferred_modality" not in st.session_state:  st.session_state.preferred_modality = ref["preferred_modality"][0] if ref["preferred_modality"] else ""
    if "preferred_language" not in st.session_state:  st.session_state.preferred_language = ref["preferred_language"][0] if ref["preferred_language"] else ""
    if "preferred_c_gender" not in st.session_state:  st.session_state.preferred_c_gender = ref["preferred_counselor_gender"][0] if ref["preferred_counselor_gender"] else ""

    render_hero_new()
    st.markdown('<div class="form-card">', unsafe_allow_html=True)

    components.html(
        """
        <script>
        (function() {
            var doc = window.parent.document;
            function applyOrange() {
                doc.querySelectorAll('[data-baseweb="radio"]').forEach(function(pill) {
                    if (pill.closest('[data-testid="stSidebar"]')) return;
                    var input = pill.querySelector('input[type="radio"]');
                    if (!input) return;
                    var outerRing = pill.children[0];
                    var innerDot  = outerRing ? outerRing.children[0] : null;
                    if (input.checked) {
                        if (outerRing) {
                            outerRing.style.setProperty('border-color', '#F97316', 'important');
                            outerRing.style.setProperty('background-color', '#F97316', 'important');
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
            applyOrange();
            [150, 400, 800].forEach(function(t) { setTimeout(applyOrange, t); });
            new MutationObserver(applyOrange).observe(doc.body, { subtree: true, childList: true, attributes: true });
            setInterval(applyOrange, 300);
        })();
        </script>
        """,
        height=0, width=0,
    )

    # ── STEP 0: Welcome ──────────────────────────────────────────────────────
    if st.session_state.quiz_step == 0:
        st.markdown("<h3 style='color: #1A1A2E; text-align: center; margin-bottom: 10px; font-family: \"DM Serif Display\", serif;'>Let's find someone who truly gets you.</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #5A5A6E; margin-bottom: 30px;'>Take a short, guided questionnaire so we can match you with the right counselor based on your unique needs and preferences.</p>", unsafe_allow_html=True)
        st.markdown(
            """
            <style>
            div[data-testid="stButton"] button[kind="primary"] {
                background-image: radial-gradient(134.26% 244.64% at 42.92% -80.36%, #B301B3 25.45%, #381DBD 100%) !important;
                background-size: 100% 100% !important;
                border: 1px solid #8043C8 !important;
                transition: background-size 150ms ease-in-out, box-shadow 150ms ease-in-out, transform 100ms ease !important;
                font-size: 16px !important;
                letter-spacing: 0.03em !important;
                padding: 14px 28px !important;
                font-weight: 700 !important;
            }
            div[data-testid="stButton"] button[kind="primary"]:hover {
                background-size: 100% 200% !important;
                box-shadow: 0px 0px 8px 0px rgba(180,40,180,0.35), 0px 0px 24px 0px rgba(102,43,223,0.35) !important;
            }
            div[data-testid="stButton"] button[kind="primary"]:active {
                transform: scale(0.95) !important;
                box-shadow: 0px 0px 11.7px 0px rgba(180,40,180,0.50), 0px 0px 28.8px 0px rgba(102,43,223,0.50) !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        _, col_btn, _ = st.columns([1, 2, 1])
        col_btn.button("Find My Counselor →", use_container_width=True, type="primary",
                       on_click=lambda: st.session_state.update(quiz_step=1))

    # ── STEP 1: Demographics ─────────────────────────────────────────────────
    elif st.session_state.quiz_step == 1:
        render_step_progress(1)
        render_step_header(1, "Tell us about yourself", "A few quick details help us tailor your best match.")
        st.number_input("What is your age?", min_value=18, max_value=80, key="client_age")
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.radio("How do you identify?", ref["client_gender"], horizontal=True, key="client_gender")
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.selectbox("What is your cultural background or ethnicity?", ref["client_ethnicity"], key="client_ethnicity")
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        col1.button("← Back", use_container_width=True,
                    on_click=lambda: st.session_state.update(quiz_step=0))
        col2.button("Next →", use_container_width=True, type="primary",
                    on_click=lambda: st.session_state.update(quiz_step=2))

    # ── STEP 2: Clinical Needs ───────────────────────────────────────────────
    elif st.session_state.quiz_step == 2:
        render_step_progress(2)
        render_step_header(2, "What brings you here?", "Share the main challenge you'd like support with today.")
        st.radio("Primary focus area", ref["client_issue"], horizontal=True, key="client_issue")
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.radio(
            "Have you ever tried counseling before?",
            [0, 1],
            format_func=lambda v: "Yes, I have" if int(v) == 1 else "No, this is my first time",
            horizontal=True,
            key="previous_exp",
        )
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        col1.button("← Back", use_container_width=True,
                    on_click=lambda: st.session_state.update(quiz_step=1))
        col2.button("Next →", use_container_width=True, type="primary",
                    on_click=lambda: st.session_state.update(quiz_step=3))

    # ── STEP 3: Preferences ──────────────────────────────────────────────────
    elif st.session_state.quiz_step == 3:
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
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        col1.button("← Back", use_container_width=True,
                    on_click=lambda: st.session_state.update(quiz_step=2))
        col2.button("Find My Best Match ✨", use_container_width=True, type="primary",
                    on_click=lambda: st.session_state.update(quiz_step=4))

    # ── STEP 4: Results ──────────────────────────────────────────────────────
    elif st.session_state.quiz_step == 4:
        def _full_reset():
            st.session_state.quiz_step = 0
            st.session_state.excluded_counselor_ids = []
            # Clear all match caches so dismissed counselors re-enter the pool
            for k in list(st.session_state.keys()):
                if k.startswith("match_") or k.startswith("gemini_single_"):
                    del st.session_state[k]

        client_age = st.session_state.client_age
        client_gender = st.session_state.client_gender
        client_ethnicity = st.session_state.client_ethnicity
        client_issue = st.session_state.client_issue
        previous_exp = st.session_state.previous_exp
        preferred_language = st.session_state.preferred_language
        preferred_modality = st.session_state.preferred_modality
        preferred_c_gender = st.session_state.preferred_c_gender

        # Cache key based on quiz answers only — exclude_ids filtered locally so
        # dismissals are instant (no new API call needed)
        _match_payload = {
            "client_age": client_age,
            "client_gender": client_gender,
            "client_ethnicity": client_ethnicity,
            "client_issue": client_issue,
            "previous_exp": int(previous_exp),
            "preferred_language": preferred_language,
            "preferred_modality": preferred_modality,
            "preferred_c_gender": preferred_c_gender,
        }
        _match_cache_key = "match_" + hashlib.md5(
            _json.dumps(sorted(_match_payload.items())).encode()
        ).hexdigest()

        if _match_cache_key not in st.session_state:
            with st.spinner("Analyzing compatibility factors to find your ideal match..."):
                pass
            st.session_state[_match_cache_key] = post_match({**_match_payload, "exclude_ids": []})

        result = st.session_state[_match_cache_key]

        if result.get("error"):
            st.warning(result["error"])
            st.markdown("</div>", unsafe_allow_html=True)
            return

        # Store the full ranked list once; dismissals filter it locally — no API re-call
        ranked_key = _match_cache_key + "_all"
        if ranked_key not in st.session_state:
            st.session_state[ranked_key] = result.get("matches") or (
                [result["top_match"]] + ([result["second_match"]] if result.get("second_match") else [])
            )

        # Filter out dismissed counselors on every render (instant, no API call)
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
        best_features = result.get("best_features", {})

        if not best_c:
            st.error("No counselors available for matching.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        st.markdown('<div id="match-results-anchor"></div>', unsafe_allow_html=True)
        scroll_to_results()

        st.markdown('<p class="explain-title" style="color:#6D28D9; text-transform:uppercase; font-size:16px; letter-spacing:0.1em; font-family:\'DM Sans\', sans-serif; font-weight:600; margin-top:8px;">YOUR MATCHES</p>', unsafe_allow_html=True)


        def _dismiss(idx):
            dismissed_id = ranked_list[idx]["counselor_id"]
            st.session_state.excluded_counselor_ids = (
                st.session_state.excluded_counselor_ids + [dismissed_id]
            )

        col1, col2 = st.columns(2, gap="large")
        with col1:
            render_counselor_card(best_c, best_c["compatibility_score"], is_primary=True, dismiss_key="dismiss_0")
            # Hidden Streamlit button wired to X via JS
            if st.button("__dismiss0__", key="dismiss_0", use_container_width=True):
                _dismiss(0)
                st.rerun()
        with col2:
            if second_c:
                render_counselor_card(second_c, second_c["compatibility_score"], is_primary=False, dismiss_key="dismiss_1")
                if st.button("__dismiss1__", key="dismiss_1", use_container_width=True):
                    _dismiss(1)
                    st.rerun()
            else:
                st.markdown(
                    """
                    <div style="
                        background: linear-gradient(160deg, #F8F5FF 0%, #FDFCFF 100%);
                        border-radius: 20px;
                        padding: 44px 32px;
                        border: 1.5px solid rgba(139,92,246,0.35);
                        min-height: 370px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        text-align: center;
                    ">
                        <div style="font-size: 36px; margin-bottom: 24px; opacity: 0.3; line-height:1;">❝</div>
                        <p style="font-family: 'DM Serif Display', serif; font-size: 18px; color: #3D1D8A; font-style: italic; line-height: 1.7; margin: 0 0 14px; max-width: 260px;">
                            You deserve to feel heard, supported, and understood. Reaching out takes courage.
                        </p>
                        <p style="font-size: 11.5px; color: #B0A9C0; letter-spacing: 0.07em; text-transform: uppercase; margin: 0 0 24px;">— A reminder for you</p>
                        <div style="width: 40px; height: 1px; background: rgba(139,92,246,0.2); margin-bottom: 24px;"></div>
                        <p style="font-size: 11px; color: #E8637A; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 600; margin: 0;">
                            No more counselors available.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

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

        st.write("")

        # ── Match Explanation (Gemini AI) — generate only for visible 2, cache by ID ──
        def _get_explanation(c):
            key = f"gemini_single_{c.get('counselor_id')}"
            if key not in st.session_state:
                st.session_state[key] = get_gemini_explanation(
                    c, client_issue, preferred_language, preferred_modality,
                    preferred_c_gender, client_age, int(previous_exp),
                )
            return st.session_state[key]

        with st.spinner("Generating your personalised match insight..."):
            explanation = _get_explanation(best_c)
        explanation_2 = None
        if second_c:
            with st.spinner("Generating insight for your 2nd option..."):
                explanation_2 = _get_explanation(second_c)

        st.markdown('<div class="explain-card">', unsafe_allow_html=True)
        st.markdown('<p class="explain-title" style="color:#6D28D9; text-transform:uppercase; font-size:16px; letter-spacing:0.1em; font-family:\'DM Sans\', sans-serif; font-weight:600; margin-top:8px;">WHY THIS MATCH ?</p>', unsafe_allow_html=True)

        if explanation:
            st.markdown(
                f'<div class="ai-explanation-box">'
                f'<div class="ai-badge">✦ AI Insight</div>'
                f'<p class="ai-explanation-text">{explanation}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            # Fallback to static bullets when Gemini is unavailable
            positive_points, negative_points = [], []
            positive_points.append(f"Supports your preferred language ({preferred_language})")
            if best_c["modality_match"] == 1:
                positive_points.append(f"Modality matches your preference ({preferred_modality})")
            else:
                negative_points.append(f"Modality does not match ({preferred_modality})")
            if best_c["issue_score"] >= 0.99:
                positive_points.append(f"Direct specialization in {client_issue}")
            elif best_c["issue_score"] >= 0.6:
                positive_points.append(f"Related experience with {client_issue}")
            else:
                negative_points.append(f"Specialization less aligned with {client_issue}")
            if preferred_c_gender != "No preference":
                if best_c["gender_match"] == 1:
                    positive_points.append(f"Preferred gender matched ({preferred_c_gender})")
                else:
                    negative_points.append(f"Preferred gender not matched ({preferred_c_gender})")

            exp_col1, exp_col2 = st.columns(2, gap="large")
            with exp_col1:
                st.markdown("<p style='font-size:15px; font-weight:600; color:#10B981; margin-bottom:0;'>Strengths</p>", unsafe_allow_html=True)
                st.markdown('<div class="point-row-wrap">', unsafe_allow_html=True)
                for item in positive_points[:4]:
                    st.markdown(
                        f'<div class="point-row point-row-green"><div class="icon-circle green"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg></div><span>{item}</span></div>',
                        unsafe_allow_html=True,
                    )
                st.markdown('</div>', unsafe_allow_html=True)
            with exp_col2:
                st.markdown("<p style='font-size:15px; font-weight:600; color:#F59E0B; margin-bottom:0;'>Things to note</p>", unsafe_allow_html=True)
                st.markdown('<div class="point-row-wrap">', unsafe_allow_html=True)
                if negative_points:
                    for item in negative_points[:4]:
                        st.markdown(
                            f'<div class="point-row point-row-amber"><div class="icon-circle amber"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg></div><span>{item}</span></div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        '<div class="point-row point-row-green"><div class="icon-circle green"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg></div><span>No major concerns detected</span></div>',
                        unsafe_allow_html=True,
                    )
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── SHAP expander ─────────────────────────────────────────────────────
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
                    "issue_score": "Issue Similarity", "modality_match": "Preferred Modality Match",
                    "gender_match": "Preferred Gender Match", "ethnicity_match": "Ethnicity Match",
                    "age_gap": "Age Gap", "client_age": "Client Age", "counselor_age": "Counselor Age",
                    "exp_years": "Counselor Experience (Years)", "prev_exp": "Client Previous Experience",
                }
                try:
                    import matplotlib.pyplot as plt
                    import shap
                    feature_labels = [readable_names.get(f, f) for f in shap_result["feature_names"]]
                    explanation = shap.Explanation(
                        values=np.array(shap_result["shap_values"]),
                        base_values=shap_result["base_value"],
                        data=np.array(shap_result["feature_values"]),
                        feature_names=feature_labels,
                    )
                    fig_wf = plt.figure(figsize=(11, 5))
                    shap.plots.waterfall(explanation, max_display=10, show=False)
                    st.pyplot(fig_wf, clear_figure=True)
                except Exception as exc:
                    st.info(f"Could not render SHAP charts: {exc}")

        # ── Second Match Explanation ──────────────────────────────────────────
        if second_c and explanation_2:
            st.markdown('<div class="explain-card">', unsafe_allow_html=True)
            st.markdown('<p class="explain-title" style="color:#6B7280; text-transform:uppercase; font-size:16px; letter-spacing:0.1em; font-family:\'DM Sans\', sans-serif; font-weight:600; margin-top:8px;">WHY THE 2ND OPTION ?</p>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="ai-explanation-box-alt">'
                f'<div class="ai-badge-alt">✦ AI Insight</div>'
                f'<p class="ai-explanation-text-alt">{explanation_2}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

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
