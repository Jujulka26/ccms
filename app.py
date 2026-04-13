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
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        
        /* Apply font to text components but prevent icon override */
        section[data-testid="stSidebar"] .stMarkdown p, 
        section[data-testid="stSidebar"] .stMarkdown div, 
        section[data-testid="stSidebar"] .stRadio p, 
        section[data-testid="stSidebar"] strong {
            color: rgba(255,255,255,0.95);
            font-family: 'DM Sans', sans-serif;
        }

        /* ── Nav radio group spacing ──────────────────────────────────── */
        section[data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 6px;
            display: flex;
            flex-direction: column;
        }

        /* Hide the radio bullet — Streamlit renders this as label[data-baseweb="radio"]
           NOT div[role="radio"], so we target the correct element here */
        section[data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child {
            display: none !important;
        }

        /* Style each nav item as a clean row */
        section[data-testid="stSidebar"] [data-baseweb="radio"] {
            padding: 11px 16px !important;
            background: rgba(255,255,255,0.04) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-radius: 10px !important;
            transition: background 0.18s ease, border-color 0.18s ease !important;
            margin-bottom: 0 !important;
            width: 100% !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
        }
        section[data-testid="stSidebar"] [data-baseweb="radio"]:hover {
            background: rgba(255,255,255,0.09) !important;
            border-color: rgba(139,92,246,0.45) !important;
        }
        /* Active nav item — :has(input:checked) targets the selected radio */
        section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) {
            background: rgba(139,92,246,0.18) !important;
            border-color: rgba(139,92,246,0.65) !important;
            box-shadow: 0 2px 10px rgba(139,92,246,0.15) !important;
        }
        section[data-testid="stSidebar"] [data-baseweb="radio"] p,
        section[data-testid="stSidebar"] [data-baseweb="radio"] span {
            font-size: 14px !important;
            font-weight: 600 !important;
            margin: 0 !important;
            color: rgba(255,255,255,0.9) !important;
        }
        section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) p,
        section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) span {
            color: #FFFFFF !important;
        }

        /* ── Pin footer to bottom of sidebar ─────────────────────────── */
        [data-testid="stSidebarUserContent"] {
            display: flex !important;
            flex-direction: column !important;
            height: 100% !important;
        }
        [data-testid="stSidebarUserContent"] > div {
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
            min-height: 0 !important;
        }
        /* Make every stVerticalBlock in the sidebar a flex column */
        [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
        }
        /* The spacer element's Streamlit wrapper grows to fill remaining space */
        [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.sidebar-spacer),
        [data-testid="stSidebarUserContent"] .element-container:has(.sidebar-spacer) {
            flex: 1 !important;
            min-height: 0 !important;
        }
        .sidebar-spacer {
            display: block;
            width: 100%;
        }

        /* ── Logout — destructive ghost button ────────────────────────── */
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background: transparent !important;
            color: rgba(239,68,68,0.85) !important;
            border: 1.5px solid rgba(239,68,68,0.35) !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease !important;
            padding: 8px 0 !important;
            margin-bottom: 16px !important;
        }
        section[data-testid="stSidebar"] button[kind="secondary"]:hover {
            background: rgba(239,68,68,0.1) !important;
            border-color: rgba(239,68,68,0.65) !important;
            color: #EF4444 !important;
        }

        /* ── Sidebar collapse (<<) button inside sidebar ──────────────── */
        button[aria-label="Collapse sidebar"],
        section[data-testid="stSidebar"] button[data-testid="baseButton-headerNoPadding"] {
            background: rgba(139,92,246,0.25) !important;
            color: #FFFFFF !important;
            border: 1.5px solid rgba(139,92,246,0.5) !important;
            border-radius: 8px !important;
            opacity: 1 !important;
        }
        button[aria-label="Collapse sidebar"]:hover,
        section[data-testid="stSidebar"] button[data-testid="baseButton-headerNoPadding"]:hover {
            background: rgba(139,92,246,0.45) !important;
            border-color: #8B5CF6 !important;
        }

        /* ── Sidebar expand (>>) button shown when sidebar is closed ───── */
        button[data-testid="collapsedControl"],
        button[aria-label="Expand sidebar"] {
            background: #8B5CF6 !important;
            color: #FFFFFF !important;
            border-radius: 0 10px 10px 0 !important;
            border: none !important;
            box-shadow: 2px 0 14px rgba(139,92,246,0.4) !important;
            opacity: 1 !important;
        }
        button[data-testid="collapsedControl"]:hover,
        button[aria-label="Expand sidebar"]:hover {
            background: #7C3AED !important;
            box-shadow: 2px 0 18px rgba(139,92,246,0.55) !important;
        }
        button[data-testid="collapsedControl"] svg,
        button[aria-label="Collapse sidebar"] svg,
        button[aria-label="Expand sidebar"] svg {
            fill: #FFFFFF !important;
            color: #FFFFFF !important;
        }

        /* ── Sidebar divider ──────────────────────────────────────────── */
        section[data-testid="stSidebar"] hr {
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin: 20px 0;
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


@st.dialog("Confirm logout")
def _logout_dialog():
    st.markdown("Are you sure you want to log out?")
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Log out", type="primary", use_container_width=True):
            del st.session_state["role"]
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


if role == "admin":
    st.sidebar.markdown(
        '<div style="font-size: 11px; font-weight: 600; letter-spacing: 0.12em; color: #A78BFA; text-transform: uppercase; margin-bottom: 12px;">Admin Navigation</div>',
        unsafe_allow_html=True
    )
    page = st.sidebar.radio("Navigation", ["Client-Counselor Matching", "Counselor Management", "Model Performance"], label_visibility="collapsed")
else:
    page = "Client-Counselor Matching"

# Invisible spacer — pushes the footer to the bottom of the sidebar
st.sidebar.markdown('<div class="sidebar-spacer" style="flex-grow: 1; min-height: 50px;"></div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown(
    f'<div style="font-size: 13px; color: rgba(255,255,255,0.55); margin-bottom: 12px; padding: 0 2px;">Signed in as <strong style="color:rgba(255,255,255,0.9)">{role.title()}</strong></div>',
    unsafe_allow_html=True
)

if st.sidebar.button("Log out", use_container_width=True):
    _logout_dialog()


if page == "Client-Counselor Matching":
    show_matching_page()
elif page == "Counselor Management":
    show_manage_page()
elif page == "Model Performance":
    show_model_performance_page()