import streamlit as st

from views.manage import show_manage_page
from views.matching import show_matching_page
from views.model_performance import show_model_performance_page
from views.login import show_login_page


if "login" in st.query_params:
    target = st.query_params["login"]
    del st.query_params["login"]
    
    if target == "client":
        st.session_state.role = "client"
    elif target == "admin":
        st.session_state.role = "admin_login"
        
    st.rerun()


def inject_app_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        .stApp {
            background: #F7F5F0;
        }

        .block-container {
            max-width: 1200px;
        }

        /* ── Strip default link formatting so it looks like a card ── */
        a.clickable-card-link {
            text-decoration: none !important;
            color: inherit !important;
            display: block; /* Makes the whole area clickable */
            height: 100%;
        }

        /* ── Hero section ─────────────────────────────────────────────── */
        .app-hero {
            background: #1A1A2E;
            border-radius: 20px;
            padding: 56px 52px 48px;
            margin-bottom: 32px;
            position: relative;
            overflow: hidden;
        }
        .app-hero::before {
            content: '';
            position: absolute;
            top: -80px; right: -80px;
            width: 320px; height: 320px;
            background: radial-gradient(circle, rgba(139,92,246,0.18) 0%, transparent 70%);
            pointer-events: none;
        }
        .app-hero::after {
            content: '';
            position: absolute;
            bottom: -60px; left: 40px;
            width: 220px; height: 220px;
            background: radial-gradient(circle, rgba(16,185,129,0.12) 0%, transparent 70%);
            pointer-events: none;
        }
        .eyebrow {
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
        .hero-copy {
            font-size: 16px;
            color: rgba(255,255,255,0.55);
            max-width: 480px;
            line-height: 1.65;
            margin: 0;
        }

        /* ── Card sections ────────────────────────────────────────────── */
        .landing-card {
            background: #FFFFFF;
            border-radius: 20px;
            padding: 36px 40px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            height: 100%;
            min-height: 240px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.3s ease;
        }
        .landing-card.admin {
            background: linear-gradient(135deg, rgba(139,92,246,0.08) 0%, rgba(255,255,255,0.95) 100%);
        }
        
        .landing-badge {
            display: inline-block;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            border-radius: 20px;
            padding: 4px 12px;
            margin-bottom: 20px;
            background: rgba(139,92,246,0.15);
            color: #8B5CF6;
        }
        .landing-badge.admin {
            background: rgba(16,185,129,0.15);
            color: #10B981;
        }
        .landing-title {
            font-family: 'DM Serif Display', serif;
            font-size: 26px;
            font-weight: 700;
            color: #1A1A2E;
            margin-bottom: 12px;
            line-height: 1.2;
        }
        .landing-meta {
            color: #5A5A6E;
            font-size: 15px;
            margin-bottom: 0;
            line-height: 1.6;
        }
        
        .landing-action {
            font-size: 15px;
            font-weight: 600;
            color: #8B5CF6;
            margin-top: 24px;
            display: flex;
            align-items: center;
        }
        .landing-card.admin .landing-action {
            color: #10B981;
        }

        /* ── Hover effects mapped directly to the link wrapper ── */
        a.clickable-card-link:hover .landing-card {
            box-shadow: 0 12px 24px rgba(0,0,0,0.12);
            transform: translateY(-2px);
            border-color: #8B5CF6;
        }
        a.clickable-card-link:hover .landing-card.admin {
            border-color: #10B981;
        }

        /* ── Form styling ─────────────────────────────────────────────── */
        div[data-testid="stForm"] {
            border: none;
            background: transparent;
            padding: 0;
        }
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] > div > div {
            border-radius: 10px !important;
            border: 1.5px solid #E5E2DC !important;
            background: #FAFAF8 !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 14px !important;
            transition: border-color 0.2s;
        }
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stNumberInput"] input:focus,
        div[data-testid="stSelectbox"] > div > div:focus-within {
            border-color: #8B5CF6 !important;
            box-shadow: 0 0 0 3px rgba(139,92,246,0.1) !important;
        }

        div[data-testid="stModal"] > div > div {
            border-radius: 20px !important;
        }

        /* ── Sidebar styling ──────────────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1A1A2E 0%, #2D2D45 100%);
        }
        section[data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }

        @media (max-width: 768px) {
            .hero-title { font-size: 32px; }
            .landing-title { font-size: 22px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title, copy, eyebrow="Client-Counselor Matching System"):
    st.markdown(
        f"""
        <div class="app-hero">
            <div class="eyebrow">{eyebrow}</div>
            <div class="hero-title">{title}</div>
            <p class="hero-copy">{copy}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Client-Counselor Matching System", layout="wide")
inject_app_styles()


if "role" not in st.session_state:
    render_hero(
        "Client-Counselor Matching System",
        "Choose a path to continue.",
        eyebrow="Welcome",
    )

    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        st.markdown(
            """
            <a href="/?login=client" target="_self" class="clickable-card-link">
                <div class="landing-card">
                    <div>
                        <div class="landing-badge">Client</div>
                        <div class="landing-title">Find a counselor</div>
                        <div class="landing-meta">Get matched in a few simple steps.</div>
                    </div>
                    <div class="landing-action">Continue as Client &rarr;</div>
                </div>
            </a>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(
            """
            <a href="/?login=admin" target="_self" class="clickable-card-link">
                <div class="landing-card admin">
                    <div>
                        <div class="landing-badge admin">Admin</div>
                        <div class="landing-title">Manage directory and models</div>
                        <div class="landing-meta">Sign in to manage records and review performance.</div>
                    </div>
                    <div class="landing-action">Sign in as Admin &rarr;</div>
                </div>
            </a>
            """,
            unsafe_allow_html=True,
        )

    st.stop()


if st.session_state.get("role") == "admin_login":
    show_login_page()
    st.stop()


role = st.session_state.get("role")

if role is None:
    del st.session_state["role"]
    st.rerun()

if role == "admin":
    page = st.sidebar.radio("Navigation", ["Client-Counselor Matching", "Counselor Management", "Model Performance"])
else:
    page = "Client-Counselor Matching"

st.sidebar.markdown(f"**Signed in as:** {role.title()}")

if st.sidebar.button("Logout"):
    del st.session_state["role"]
    st.rerun()


if page == "Client-Counselor Matching":
    show_matching_page()
elif page == "Counselor Management":
    show_manage_page()
elif page == "Model Performance":
    show_model_performance_page()