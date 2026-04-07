import streamlit as st

from views.manage import show_manage_page
from views.matching import show_matching_page
from views.model_performance import show_model_performance_page
from utils.db import verify_admin_credentials


def inject_app_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

        :root {
            --bg-1: #f7f9fc;
            --bg-2: #eef3f9;
            --surface-strong: #ffffff;
            --border: #dce4ee;
            --text-main: #132033;
            --text-muted: #5b6b7f;
            --accent: #234e70;
            --accent-soft: #d9e7f4;
            --shadow: 0 18px 50px rgba(18, 32, 51, 0.09);
        }

        html, body, [class*="css"]  {
            font-family: 'Manrope', sans-serif;
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(35, 78, 112, 0.08), transparent 28%),
                radial-gradient(circle at top right, rgba(64, 120, 173, 0.08), transparent 24%),
                linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 100%);
        }
        .block-container {
            max-width: 1200px;
            padding-top: 1.5rem;
            padding-bottom: 1.8rem;
        }
        .app-hero, .soft-card, .stat-card {
            background: var(--surface-strong);
            border: 1px solid var(--border);
            border-radius: 16px;
            box-shadow: 0 10px 28px rgba(18, 32, 51, 0.06);
        }
        .app-hero {
            padding: 1.1rem 1.2rem;
            margin-bottom: 1.15rem;
        }
        .soft-card {
            padding: 0.9rem 1rem 0.25rem 1rem;
            margin-bottom: 1rem;
        }
        .stat-card {
            padding: 0.75rem 0.9rem;
            text-align: center;
            margin-bottom: 1rem;
        }
        .eyebrow {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            margin-bottom: 0.25rem;
        }
        .hero-title {
            font-size: 1.72rem;
            font-weight: 800;
            color: var(--text-main);
            margin-bottom: 0.3rem;
            line-height: 1.1;
        }
        .hero-copy, .card-copy {
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-bottom: 0;
            line-height: 1.55;
        }
        .card-title {
            font-size: 1rem;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 0.25rem;
        }
        .landing-card {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 16px;
            box-shadow: 0 10px 28px rgba(18, 32, 51, 0.06);
            padding: 1rem 1rem 0.95rem 1rem;
            height: 100%;
        }
        .landing-card.admin {
            background: linear-gradient(180deg, rgba(35, 78, 112, 0.04), rgba(255, 255, 255, 0.98));
        }
        .landing-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.28rem 0.62rem;
            border-radius: 999px;
            background: var(--accent-soft);
            color: var(--accent);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 0.7rem;
        }
        .landing-title {
            font-size: 1.08rem;
            font-weight: 800;
            color: var(--text-main);
            margin-bottom: 0.35rem;
        }
        .landing-meta {
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-bottom: 0.8rem;
            line-height: 1.5;
        }
        .stat-label {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 0.1rem;
        }
        .stat-value {
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--text-main);
        }
        div[data-testid="stDataFrame"] {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid var(--border);
        }
        div[data-testid="stForm"] {
            border: none;
            background: transparent;
            padding: 0;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.45rem;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 0.35rem 0.8rem;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #17212f 0%, #223246 100%);
        }
        section[data-testid="stSidebar"] * {
            color: #f8fafc !important;
        }
        section[data-testid="stSidebar"] .stButton button {
            border: 1px solid rgba(255, 255, 255, 0.22);
        }
        .stExpander {
            border-radius: 12px;
            border: 1px solid var(--border);
            background: #ffffff;
        }
        .stButton > button {
            border-radius: 12px;
            font-weight: 700;
        }
        @media (max-width: 768px) {
            .hero-title {
                font-size: 1.5rem;
            }
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


@st.dialog("Sign in as Admin")
def render_admin_login_dialog():
    with st.form("admin_login_form"):
        email = st.text_input("email")
        password = st.text_input("Password", type="password")

        submit_col, cancel_col = st.columns(2)
        with submit_col:
            submitted = st.form_submit_button("Sign in", use_container_width=True, type="primary")
        with cancel_col:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

    if cancelled:
        st.session_state.admin_login_open = False
        st.rerun()

    if submitted:
        if verify_admin_credentials(email, password):
            st.session_state.role = "admin"
            st.session_state.admin_login_open = False
            st.rerun()
        st.error("Invalid email or password.")


st.set_page_config(page_title="Client-Counselor Matching System", layout="wide")
inject_app_styles()


if "show_form" not in st.session_state:
    st.session_state.show_form = False

if "admin_login_open" not in st.session_state:
    st.session_state.admin_login_open = False


if "role" not in st.session_state:
    st.markdown(
        """
        <style>
        div.stButton > button {
            min-height: 50px;
            font-size: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    render_hero(
        "Client-Counselor Matching System",
        "Choose a path to continue.",
        eyebrow="Welcome",
    )

    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        st.markdown(
            """
            <div class="landing-card">
                <div class="landing-badge">Client</div>
                <div class="landing-title">Find a counselor</div>
                <div class="landing-meta">Get matched in a few simple steps.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Continue as Client", use_container_width=True, type="primary"):
            st.session_state.admin_login_open = False
            st.session_state.role = "client"
            st.rerun()

    with right_col:
        st.markdown(
            """
            <div class="landing-card admin">
                <div class="landing-badge">Admin</div>
                <div class="landing-title">Manage directory and models</div>
                <div class="landing-meta">Sign in to manage records and review performance.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Admin", use_container_width=True):
            st.session_state.admin_login_open = True
            st.rerun()

    if st.session_state.admin_login_open:
        render_admin_login_dialog()
        st.stop()

    st.stop()


role = st.session_state.role

if role == "admin":
    page = st.sidebar.radio("Navigation", ["Client-Counselor Matching", "Counselor Management", "Model Performance"])
else:
    page = "Client-Counselor Matching"

st.sidebar.markdown(f"**Signed in as:** {role.title()}")

if st.sidebar.button("Logout"):
    st.session_state.admin_login_open = False
    del st.session_state["role"]
    st.rerun()


if page == "Client-Counselor Matching":
    show_matching_page()
elif page == "Counselor Management":
    show_manage_page()
elif page == "Model Performance":
    show_model_performance_page()
