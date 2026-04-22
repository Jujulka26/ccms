import base64
import os
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import time

from frontend.utils.api import get_reference_data, post_match, post_shap, save_intro_request

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
        [data-testid="block-container"] [data-baseweb="radio"]:has(input:checked) { background: rgba(139,92,246,0.12) !important; border-color: #8B5CF6 !important; }
        [data-testid="block-container"] [data-baseweb="radio"]:has(input:checked) p { color: #6D28D9 !important; font-weight: 700 !important; }
        [data-testid="block-container"] [data-baseweb="radio"] p { font-size: 14px !important; margin: 0 !important; color: #4A4A5A !important; font-weight: 500 !important; }

        div[data-testid="stButton"] button { border-radius: 12px !important; font-family: 'DM Sans', sans-serif !important; font-size: 15px !important; font-weight: 600 !important; padding: 10px 24px !important; transition: all 0.2s; width: 100% !important; }
        div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%) !important; color: #FFFFFF !important; border: none !important; box-shadow: 0 4px 14px rgba(124,58,237,0.35); }
        div[data-testid="stButton"] button[kind="primary"]:hover { box-shadow: 0 6px 20px rgba(124,58,237,0.45) !important; transform: translateY(-1px); }

        .result-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px; }
        .result-card { position: relative; background: #FFFFFF; border-radius: 20px; padding: 28px; border: 1px solid rgba(0,0,0,0.06); margin-bottom: 0px; }
        .result-card.primary { background: #1A1A2E; border-color: transparent; }
        .result-card-badge { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; border-radius: 20px; padding: 3px 10px; display: inline-block; margin-bottom: 18px; }
        .badge-primary { background: rgba(139,92,246,0.2); color: #A78BFA; }
        .badge-secondary { background: #F0EDE8; color: #8B8B9A; }
        .profile-btn { position: absolute; top: 28px; right: 28px; font-size: 10px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; text-decoration: none !important; padding: 5px 12px; border-radius: 20px; transition: all 0.2s ease; box-shadow: none !important; cursor: pointer; }
        .compat-score { font-family: 'DM Serif Display', serif; font-size: 52px; line-height: 1; color: #FFFFFF; margin-bottom: 4px; }
        .compat-score-secondary { font-family: 'DM Serif Display', serif; font-size: 52px; line-height: 1; color: #1A1A2E; margin-bottom: 4px; }
        .compat-label { font-size: 12px; color: rgba(255,255,255,0.45); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 24px; }
        .compat-label-secondary { font-size: 12px; color: #A0A0B0; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 24px; }
        .counselor-name { font-size: 20px; font-weight: 600; color: #FFFFFF; margin-bottom: 16px; }
        .counselor-name-secondary { font-size: 20px; font-weight: 600; color: #1A1A2E; margin-bottom: 16px; }
        .info-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.07); }
        .info-row-secondary { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #F0EDE8; }
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

        div[data-testid="stTabs"] button { font-family: 'DM Sans', sans-serif !important; font-size: 14px !important; font-weight: 500 !important; }
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


def render_counselor_card(c: dict, score: float, is_primary=True):
    langs = c.get("counselor_language") or "—"
    mods = c.get("counselor_modality") or "—"
    if is_primary:
        st.markdown(
            f"""
            <div class="result-card primary">
                <span class="result-card-badge badge-primary">Top Match</span>
                <div class="compat-score">{score:.1f}%</div>
                <div class="compat-label">Compatibility score</div>
                <div class="counselor-name">{c['name']}</div>
                <div class="info-row"><span class="info-key">Experience</span><span class="info-val">{c['experience_years']} yrs</span></div>
                <div class="info-row"><span class="info-key">Specialization</span><span class="info-val">{c['specialization']}</span></div>
                <div class="info-row"><span class="info-key">Modality</span><span class="info-val">{mods}</span></div>
                <div class="info-row" style="border:none"><span class="info-key">Language</span><span class="info-val">{langs}</span></div>
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
                <div class="info-row-secondary"><span class="info-key-secondary">Experience</span><span class="info-val-secondary">{c['experience_years']} yrs</span></div>
                <div class="info-row-secondary"><span class="info-key-secondary">Specialization</span><span class="info-val-secondary">{c['specialization']}</span></div>
                <div class="info-row-secondary"><span class="info-key-secondary">Modality</span><span class="info-val-secondary">{mods}</span></div>
                <div class="info-row-secondary" style="border:none"><span class="info-key-secondary">Language</span><span class="info-val-secondary">{langs}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    card_id = f"{int(c.get('counselor_id', 0))}_{'p' if is_primary else 's'}"
    if st.button("View Full Profile", key=f"vp_{card_id}", use_container_width=True, type="primary" if is_primary else "secondary"):
        show_profile_dialog(c, score)


# ── Profile dialog ─────────────────────────────────────────────────────────────
_EXPERTISE_MAP = {
    "Anxiety":    ["Anxiety Management", "Panic Attacks", "Worry Reduction", "Stress Relief", "Cognitive Reframing"],
    "Depression": ["Low Mood Support", "Motivation Building", "Emotional Regulation", "Self-Esteem", "Behavioral Activation"],
    "Stress":     ["Work-Life Balance", "Stress Coping", "Burnout Recovery", "Mindfulness", "Relaxation Techniques"],
    "Trauma":     ["Trauma Processing", "PTSD Support", "Emotional Healing", "Resilience Building", "Safety Planning"],
}
_MODALITY_TAGS = {
    "CBT": ["Cognitive Restructuring", "Thought Records"],
    "Mindfulness": ["Present-Moment Awareness", "Breathing Techniques"],
    "Humanistic": ["Person-Centered Growth", "Empathetic Support"],
    "REBT": ["Belief Challenging", "Rational Thinking"],
}
_MODALITY_DESC = {
    "CBT": "Cognitive Behavioral Therapy (CBT) helps you identify and change unhelpful thought patterns and behaviors. Through structured sessions, you'll learn to reframe negative thoughts and build healthier coping strategies.",
    "Mindfulness": "Mindfulness-Based approaches teach you to observe your thoughts and feelings without judgment. You'll develop present-moment awareness and breathing techniques that reduce stress and increase emotional clarity.",
    "Humanistic": "Humanistic counseling is a person-centered approach that focuses on your unique strengths and potential. Sessions are warm, empathetic, and non-judgmental — built around understanding your personal experience.",
    "REBT": "Rational Emotive Behavior Therapy (REBT) helps you challenge irrational beliefs and replace them with healthier, rational thinking patterns, leading to more positive emotional outcomes.",
}


def _expertise_tags(spec, modality):
    tags = list(_EXPERTISE_MAP.get(spec, []))
    for tag in _MODALITY_TAGS.get(modality, []):
        if tag not in tags:
            tags.append(tag)
    return tags[:6]


def _helpful_thoughts(spec):
    defaults = {
        "Anxiety":    ["Am I doing enough?", "What if things go wrong?"],
        "Depression": ["Why do I feel so empty?", "Will I ever feel better?"],
        "Stress":     ["I can't keep up with everything.", "Why do I feel so overwhelmed?"],
        "Trauma":     ["Why do I keep reliving this?", "Will I ever feel safe again?"],
    }
    return defaults.get(spec, ["How do I move forward?", "Is it okay to ask for help?"])


@st.dialog("Counselor Profile")
def show_profile_dialog(c: dict, score=None):
    name = c.get("name", "Counselor")
    spec = c.get("specialization", "")
    modality = c.get("counselor_modality", "")
    exp = c.get("experience_years", "—")
    lang = c.get("counselor_language", "—")
    about = c.get("about_me") or ""
    ht1 = c.get("helpful_thought_1") or ""
    ht2 = c.get("helpful_thought_2") or ""
    ext = c.get("expertise_tags") or ""

    pills = [t.strip() for t in ext.split(",") if t.strip()][:6] if ext.strip() else _expertise_tags(spec, modality)
    thoughts = [t for t in [ht1, ht2] if t.strip()] or _helpful_thoughts(spec)

    avatar_url = f"https://api.dicebear.com/7.x/avataaars/svg?seed={name.replace(' ', '')}&backgroundColor=b6e3f4,c0aede,d1d4f9"
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:24px;margin-bottom:20px;">
            <img src="{avatar_url}" width="90" height="90" style="border-radius:16px;border:2px solid #EDE8E3;flex-shrink:0;" />
            <div style="flex:1;">
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:4px;">
                    <span style="font-family:'DM Serif Display',serif;font-size:22px;color:#1A1A2E;">{name}</span>
                </div>
                <div style="font-size:13px;color:#8B5CF6;font-weight:600;margin-bottom:8px;">Licensed Counselor</div>
                <div style="display:flex;gap:16px;flex-wrap:wrap;">
                    <span style="font-size:12px;color:#5A5A6E;">&#128188; {exp} yrs exp</span>
                    <span style="font-size:12px;color:#5A5A6E;">&#128172; {lang}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    if about.strip():
        st.markdown('<p style="font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#8B5CF6;margin:0 0 8px;">About Me</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:14px;color:#2D2D3F;line-height:1.7;margin-bottom:16px;">{about}</p>', unsafe_allow_html=True)

    st.markdown('<p style="font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#8B5CF6;margin:0 0 10px;">Areas of Expertise</p>', unsafe_allow_html=True)
    pill_html = "".join(
        f'<span style="display:inline-block;background:#F3F0FF;color:#6D28D9;font-size:12px;font-weight:600;padding:4px 12px;border-radius:20px;margin:0 6px 6px 0;">{p}</span>'
        for p in pills
    )
    st.markdown(f'<div style="margin-bottom:16px;">{pill_html}</div>', unsafe_allow_html=True)

    thought_items = "".join(
        f'<div style="display:flex;gap:8px;align-items:flex-start;margin-bottom:8px;">'
        f'<span style="color:#8B5CF6;font-size:14px;flex-shrink:0;">&#10024;</span>'
        f'<span style="font-size:14px;color:#2D2D3F;font-style:italic;font-weight:500;">"{t}"</span>'
        f'</div>'
        for t in thoughts
    )
    st.markdown(
        f"""
        <div style="background:#F8F5FF;border:1px solid #E9E1FF;border-radius:14px;padding:20px 22px;margin-bottom:16px;">
            <p style="font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#8B5CF6;margin:0 0 12px;">Thoughts I can help you with</p>
            {thought_items}
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("What approaches do I use?"):
        desc = _MODALITY_DESC.get(modality, f"This counselor uses {modality} as their primary approach.")
        st.markdown(f'<p style="font-size:14px;color:#2D2D3F;line-height:1.7;">{desc}</p>', unsafe_allow_html=True)

    st.write("")

    req_state_key = f"req_{c.get('counselor_id')}"
    if req_state_key not in st.session_state:
        st.session_state[req_state_key] = False

    def toggle_req(val):
        st.session_state[req_state_key] = val

    if not st.session_state[req_state_key]:
        st.button(f"✉️ Get to know {name}", use_container_width=True, type="primary", on_click=toggle_req, args=(True,))
    else:
        st.markdown(
            f"""
            <div style="border:1px solid #E5E2DC;border-radius:14px;padding:20px;background:#F7F5F0;margin-bottom:12px;">
                <p style="font-size:14px;color:#4A4A5A;margin-bottom:16px;">
                    <b>Leave your details below.</b> The clinic coordinator will review your match and connect you with {name} via email.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        client_name = st.text_input("Your Full Name")
        client_email = st.text_input("Your Email Address")

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


# ── Main page ─────────────────────────────────────────────────────────────────
def show_matching_page():
    inject_styles()

    ref = get_reference_data()

    if "quiz_step" not in st.session_state:
        st.session_state.quiz_step = 0

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
        _, col2 = st.columns([1, 1])
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
        st.progress(100)

        client_age = st.session_state.client_age
        client_gender = st.session_state.client_gender
        client_ethnicity = st.session_state.client_ethnicity
        client_issue = st.session_state.client_issue
        previous_exp = st.session_state.previous_exp
        preferred_language = st.session_state.preferred_language
        preferred_modality = st.session_state.preferred_modality
        preferred_c_gender = st.session_state.preferred_c_gender

        _, btn_col = st.columns([3, 1])
        btn_col.button("↺ Start Over", use_container_width=True,
                       on_click=lambda: st.session_state.update(quiz_step=0))

        with st.spinner("Analyzing compatibility factors to find your ideal match..."):
            time.sleep(1.2)

        result = post_match({
            "client_age": client_age,
            "client_gender": client_gender,
            "client_ethnicity": client_ethnicity,
            "client_issue": client_issue,
            "previous_exp": int(previous_exp),
            "preferred_language": preferred_language,
            "preferred_modality": preferred_modality,
            "preferred_c_gender": preferred_c_gender,
        })

        if result.get("error"):
            st.warning(result["error"])
            st.markdown("</div>", unsafe_allow_html=True)
            return

        best_c = result["top_match"]
        second_c = result.get("second_match")
        best_features = result.get("best_features", {})

        if not best_c:
            st.error("No counselors available for matching.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        st.markdown('<div id="match-results-anchor"></div>', unsafe_allow_html=True)
        scroll_to_results()

        st.markdown('<p class="explain-title" style="color:#6D28D9; text-transform:uppercase; font-size:16px; letter-spacing:0.1em; font-family:\'DM Sans\', sans-serif; font-weight:600; margin-top:8px;">YOUR MATCHES</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        with col1:
            render_counselor_card(best_c, best_c["compatibility_score"], is_primary=True)
        with col2:
            if second_c:
                render_counselor_card(second_c, second_c["compatibility_score"], is_primary=False)
            else:
                st.info("No second match available.")

        components.html(
            """
            <script>
            function sp(el, prop, val) { el.style.setProperty(prop, val, 'important'); }
            function styleVPButtons() {
                var doc = window.parent.document;
                var cols = doc.querySelectorAll('[data-testid="column"]');
                cols.forEach(function(col) {
                    var card = col.querySelector('.result-card');
                    if (!card) return;
                    var isPrimary = card.classList.contains('primary');
                    var bg = isPrimary ? '#22223D' : '#FAFAF8';
                    var color = isPrimary ? '#A78BFA' : '#6D28D9';
                    var hoverBg = isPrimary ? '#2A2A4A' : '#F0EDE8';
                    var hoverColor = isPrimary ? '#C4B5FD' : '#5B21B6';
                    col.querySelectorAll('[data-testid="element-container"]').forEach(function(ec) {
                        sp(ec, 'margin-top', '0'); sp(ec, 'padding-top', '0'); sp(ec, 'margin-bottom', '0'); sp(ec, 'padding-bottom', '0');
                    });
                    col.querySelectorAll('[data-testid="stVerticalBlock"]').forEach(function(vb) { sp(vb, 'gap', '0'); });
                    col.querySelectorAll('[data-testid="stButton"]').forEach(function(wrapper) {
                        sp(wrapper, 'width', '100%'); sp(wrapper, 'margin', '0'); sp(wrapper, 'padding', '0');
                        var btn = wrapper.querySelector('button');
                        if (!btn) return;
                        sp(btn, 'background', bg); sp(btn, 'color', color); sp(btn, 'border-radius', '14px');
                        sp(btn, 'border', 'none'); sp(btn, 'width', '100%'); sp(btn, 'padding', '13px 24px');
                        sp(btn, 'font-size', '12px'); sp(btn, 'font-weight', '600'); sp(btn, 'letter-spacing', '0.05em');
                        sp(btn, 'text-transform', 'uppercase'); sp(btn, 'box-shadow', 'none'); sp(btn, 'transform', 'none');
                        btn.onmouseenter = function() { sp(btn, 'background', hoverBg); sp(btn, 'color', hoverColor); };
                        btn.onmouseleave = function() { sp(btn, 'background', bg); sp(btn, 'color', color); };
                    });
                });
            }
            styleVPButtons(); setTimeout(styleVPButtons, 150); setTimeout(styleVPButtons, 500);
            </script>
            """,
            height=0, width=0,
        )

        st.write("")

        # ── Match Explanation ─────────────────────────────────────────────────
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

        st.markdown('<div class="explain-card">', unsafe_allow_html=True)
        st.markdown('<p class="explain-title" style="color:#6D28D9; text-transform:uppercase; font-size:16px; letter-spacing:0.1em; font-family:\'DM Sans\', sans-serif; font-weight:600; margin-top:8px;">WHY THIS MATCH ?</p>', unsafe_allow_html=True)
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
            shap_result = post_shap(best_features)
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

    st.markdown('</div>', unsafe_allow_html=True)
