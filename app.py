import streamlit as st
from frontend.pages.manage import show_manage_page
from frontend.pages.matching import show_matching_page
from frontend.pages.model_performance import show_model_performance_page
from frontend.pages.login import show_login_page
from frontend.pages.chatbot import show_chatbot_page
from frontend.pages.manage_request import render as show_manage_request_page
from frontend.pages.enquiries import render as show_enquiries_page
from frontend.pages.aboutus import show_aboutus_page
from frontend.pages.contactus import show_contactus_page
from frontend.pages.counselors import show_counselors_page


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
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        .stApp {
            background: #F5F3FF;
        }

        [data-stale="true"] { opacity: 0 !important; transition: none !important; }

        .block-container {
            max-width: 1200px;
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
            border: 1.5px solid #F0E8FF !important;
            background: #F5F3FF !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 14px !important;
            transition: border-color 0.2s;
        }
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stNumberInput"] input:focus,
        div[data-testid="stSelectbox"] > div > div:focus-within {
            border-color: #B588F7 !important;
            box-shadow: 0 0 0 3px rgba(181,136,247,0.12) !important;
        }

        div[data-testid="stModal"] > div > div {
            border-radius: 20px !important;
        }

        /* ── Sidebar styling ──────────────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #B588F7 0%, #83ADF9 100%);
            border-right: 1px solid rgba(181,136,247,0.2);
        }

        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown div,
        section[data-testid="stSidebar"] .stRadio p,
        section[data-testid="stSidebar"] strong {
            color: rgba(46,16,101,0.9);
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* ── Nav radio group ─────────────────────────────────────────── */
        section[data-testid="stSidebar"] [data-testid="stElementContainer"][width="fit-content"],
        section[data-testid="stSidebar"] [data-testid="stRadio"],
        section[data-testid="stSidebar"] [role="radiogroup"] {
            width: 100% !important;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] {
            display: flex !important;
            flex-direction: column !important;
            align-items: stretch !important;
            gap: 4px !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child {
            display: none !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"] {
            padding: 11px 16px !important;
            background: rgba(255,255,255,0.35) !important;
            border: 1px solid rgba(255,255,255,0.5) !important;
            border-radius: 10px !important;
            transition: background 0.18s ease, border-color 0.18s ease !important;
            margin-bottom: 0 !important;
            width: 100% !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
        }
        section[data-testid="stSidebar"] [data-baseweb="radio"]:hover {
            background: rgba(255,255,255,0.5) !important;
            border-color: rgba(255,255,255,0.7) !important;
        }
        section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) {
            background: rgba(255,255,255,0.92) !important;
            border-color: #2E1065 !important;
            box-shadow: 0 2px 12px rgba(255,255,255,0.4) !important;
        }
        section[data-testid="stSidebar"] [data-baseweb="radio"] p,
        section[data-testid="stSidebar"] [data-baseweb="radio"] span {
            font-size: 14px !important;
            font-weight: 600 !important;
            margin: 0 !important;
            color: rgba(46,16,101,0.85) !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) p,
        section[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) span {
            color: #2E1065 !important;
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
        [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
        }
        [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.sidebar-spacer),
        [data-testid="stSidebarUserContent"] .element-container:has(.sidebar-spacer) {
            flex: 1 !important;
            min-height: 0 !important;
        }
        .sidebar-spacer {
            display: block;
            width: 100%;
        }

        /* ── Primary buttons ─────────────────────────────────────────── */
        button[kind="primary"] {
            background: linear-gradient(to right, #B588F7 0%, #83ADF9 48%, #2E1065 52%, #2E1065 100%) !important;
            background-size: 210% 100% !important;
            background-position: right center !important;
            transition: background-position 0.4s ease-in-out, box-shadow 0.3s ease, transform 0.15s ease !important;
            border: none !important;
            color: #FFFFFF !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 16px rgba(46,16,101,0.45) !important;
        }
        button[kind="primary"]:hover {
            background-position: left center !important;
            box-shadow: 0 6px 24px rgba(181,136,247,0.55) !important;
            transform: translateY(-1px) !important;
        }
        button[kind="primary"]:active {
            transform: scale(0.97) translateY(0) !important;
        }

        /* ── Logout / Back to home — destructive ghost button ───────────── */
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background-color: rgba(255,255,255,0.82) !important;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23C41A16' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4'/%3E%3Cpolyline points='16 17 21 12 16 7'/%3E%3Cline x1='21' y1='12' x2='9' y2='12'/%3E%3C/svg%3E") !important;
            background-repeat: no-repeat !important;
            background-position: 14px center !important;
            background-size: 15px 15px !important;
            color: #C41A16 !important;
            border: 1.5px solid rgba(196,26,22,0.6) !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease !important;
            padding: 8px 0 8px 14px !important;
            margin-bottom: 16px !important;
        }
        section[data-testid="stSidebar"] button[kind="secondary"]:hover {
            background-color: #FFFFFF !important;
            border-color: #C41A16 !important;
            color: #B91C1C !important;
        }

        /* ── Sidebar collapse/expand buttons ─────────────────────────── */
        button[aria-label="Collapse sidebar"],
        section[data-testid="stSidebar"] button[data-testid="baseButton-headerNoPadding"] {
            background: rgba(255,255,255,0.5) !important;
            color: #2E1065 !important;
            border: 1.5px solid rgba(255,255,255,0.7) !important;
            border-radius: 8px !important;
            opacity: 1 !important;
        }
        button[aria-label="Collapse sidebar"]:hover,
        section[data-testid="stSidebar"] button[data-testid="baseButton-headerNoPadding"]:hover {
            background: rgba(255,255,255,0.7) !important;
            border-color: rgba(255,255,255,0.9) !important;
        }

        button[data-testid="collapsedControl"],
        button[aria-label="Expand sidebar"] {
            background: #B588F7 !important;
            color: #FFFFFF !important;
            border-radius: 0 10px 10px 0 !important;
            border: none !important;
            box-shadow: 2px 0 14px rgba(181,136,247,0.45) !important;
            opacity: 1 !important;
        }
        button[data-testid="collapsedControl"]:hover,
        button[aria-label="Expand sidebar"]:hover {
            background: #B588F7 !important;
            box-shadow: 2px 0 18px rgba(181,136,247,0.7) !important;
        }
        button[aria-label="Collapse sidebar"] svg {
            fill: #2E1065 !important;
            color: #2E1065 !important;
        }
        button[data-testid="collapsedControl"] svg,
        button[aria-label="Expand sidebar"] svg {
            fill: #FFFFFF !important;
            color: #FFFFFF !important;
        }

        /* ── Sidebar divider ──────────────────────────────────────────── */
        section[data-testid="stSidebar"] hr {
            border-bottom: 1px solid rgba(46,16,101,0.15);
            margin: 20px 0;
        }

        /* ── Landing page ─────────────────────────────────────────────── */
        .land-cta-btn {
            display: inline-block;
            background: #8B5CF6;
            color: #FFFFFF !important;
            font-size: 15px;
            font-weight: 700;
            padding: 16px 40px;
            border-radius: 50px;
            text-decoration: none !important;
            transition: background 0.2s, box-shadow 0.2s, transform 0.15s;
            box-shadow: 0 4px 20px rgba(181,136,247,0.45);
            font-family: 'Plus Jakarta Sans', sans-serif;
            letter-spacing: 0.01em;
        }
        .land-cta-btn:hover {
            background: #B588F7;
            box-shadow: 0 8px 28px rgba(181,136,247,0.7);
            transform: translateY(-2px);
        }

        .land-band {
            padding: 80px clamp(24px, 8vw, 120px);
        }
        .land-inner {
            max-width: 1080px;
            margin: 0 auto;
        }

        /* Hero band */
        .land-hero-band {
            background: #0F0E1A;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .land-hero-band::before {
            content: '';
            position: absolute;
            top: -100px; right: -60px;
            width: 560px; height: 560px;
            background: radial-gradient(circle, rgba(131,173,249,0.22) 0%, transparent 55%);
            pointer-events: none;
        }
        .land-hero-band::after {
            content: '';
            position: absolute;
            bottom: -80px; left: -40px;
            width: 400px; height: 400px;
            background: radial-gradient(circle, rgba(0,168,120,0.14) 0%, transparent 55%);
            pointer-events: none;
        }
        .land-hero-eyebrow {
            display: inline-block;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: rgba(181,136,247,0.9);
            background: rgba(181,136,247,0.12);
            border: 1px solid rgba(181,136,247,0.3);
            border-radius: 20px;
            padding: 5px 16px;
            margin-bottom: 28px;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .land-hero-title {
            font-family: 'Fraunces', serif;
            font-size: 60px;
            line-height: 1.06;
            color: #FFFFFF;
            margin: 0 auto 24px;
            letter-spacing: -1.5px;
            max-width: 740px;
            font-weight: 600;
        }
        .land-hero-copy {
            font-size: 18px;
            color: rgba(255,255,255,0.55);
            max-width: 500px;
            line-height: 1.72;
            margin: 0 auto 44px !important;
            text-align: center !important;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* Steps band */
        .land-steps-band {
            background: #F5F3FF;
        }
        .land-band-label {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #B588F7;
            text-align: center;
            margin-bottom: 12px;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .land-band-title {
            font-family: 'Fraunces', serif;
            font-size: 38px;
            color: #1C1917;
            text-align: center;
            margin: 0 0 48px;
            font-weight: 600;
        }
        .land-steps {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }
        .land-step {
            padding: 36px 32px;
            background: #FFFFFF;
            border-radius: 18px;
            box-shadow: 0 2px 16px rgba(181,136,247,0.06);
            border: 1px solid rgba(181,136,247,0.08);
        }
        .land-step-num {
            font-family: 'Fraunces', serif;
            font-size: 48px;
            line-height: 1;
            margin-bottom: 20px;
            font-weight: 300;
        }
        .land-step-num.n1 { color: #D4B8FC; }
        .land-step-num.n2 { color: #B588F7; }
        .land-step-num.n3 { color: #83ADF9; }
        .land-step-title {
            font-size: 16px;
            font-weight: 700;
            color: #1C1917;
            margin-bottom: 10px;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .land-step-copy {
            font-size: 14px;
            color: #6B6560;
            line-height: 1.72;
            margin: 0;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* Why band */
        .land-why-band {
            background: #FFFFFF;
        }
        .land-why-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 40px;
        }
        .land-why-icon {
            width: 48px;
            height: 48px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            margin-bottom: 20px;
            line-height: 1;
        }
        .land-why-icon.rose { background: rgba(181,136,247,0.12); }
        .land-why-icon.gold { background: rgba(59,130,246,0.12); }
        .land-why-icon.sage { background: rgba(5,150,105,0.1); }
        .land-why-title {
            font-size: 16px;
            font-weight: 700;
            color: #1C1917;
            margin-bottom: 10px;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .land-why-copy {
            font-size: 14px;
            color: #6B6560;
            line-height: 1.72;
            margin: 0;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* CTA band */
        .land-cta-band {
            background: #0F0E1A;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .land-cta-band::before {
            content: '';
            position: absolute;
            top: -80px; right: -80px;
            width: 360px; height: 360px;
            background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 60%);
            pointer-events: none;
        }
        .land-cta-title {
            font-family: 'Fraunces', serif;
            font-size: 40px;
            color: #FFFFFF;
            margin: 0 0 14px;
            font-weight: 600;
        }
        .land-cta-copy {
            font-size: 16px;
            color: rgba(255,255,255,0.55);
            margin: 0 0 36px;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* Staff link */
        .land-staff-link {
            background: #F5F3FF;
            text-align: center;
            padding: 18px 0 20px;
            border-top: 1px solid rgba(0,0,0,0.06);
        }
        .land-staff-link a {
            font-size: 12px;
            color: #9C9790 !important;
            text-decoration: none !important;
            letter-spacing: 0.04em;
            transition: color 0.2s;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .land-staff-link a:hover { color: #B588F7 !important; }

        @media (max-width: 768px) {
            .land-hero-title { font-size: 36px; }
            .land-band-title { font-size: 28px; }
            .land-steps, .land-why-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Client-Counselor Matching System", layout="wide")
inject_app_styles()


if "role" not in st.session_state:
    st.markdown(
        """
        <style>
        .stApp { background: #FFFFFF !important; }
        section[data-testid="stMain"] .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <!-- ── Hero ──────────────────────────────────────────────────────── -->
        <div class="land-hero-band land-band">
            <div class="land-inner" style="position:relative;z-index:2;">
                <div class="land-hero-eyebrow">✦ AI-Powered Counselor Matching</div>
                <div class="land-hero-title">Find the right counselor,<br>matched just for you</div>
                <p class="land-hero-copy">Answer a few questions. Our model does the rest — surfacing your best-fit counselor from our verified directory.</p>
                <a href="/?login=client" target="_self" class="land-cta-btn">Find your counselor &rarr;</a>
            </div>
        </div>

        <!-- ── How it works ───────────────────────────────────────────────── -->
        <div class="land-steps-band land-band">
            <div class="land-inner">
                <div class="land-band-label">How it works</div>
                <div class="land-band-title">Three simple steps</div>
                <div class="land-steps">
                    <div class="land-step">
                        <div class="land-step-num n1">01</div>
                        <div class="land-step-title">Share your preferences</div>
                        <p class="land-step-copy">Tell us about yourself — your age, concerns, preferred language, and what you're looking for in a counselor.</p>
                    </div>
                    <div class="land-step">
                        <div class="land-step-num n2">02</div>
                        <div class="land-step-title">Get AI-matched</div>
                        <p class="land-step-copy">Our model analyses compatibility across multiple dimensions to surface your best-fit counselors from our directory.</p>
                    </div>
                    <div class="land-step">
                        <div class="land-step-num n3">03</div>
                        <div class="land-step-title">Connect by email</div>
                        <p class="land-step-copy">Submit an intro request and your counselor will reach out to arrange your first session. No account needed.</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- ── Why us ─────────────────────────────────────────────────────── -->
        <div class="land-why-band land-band">
            <div class="land-inner">
                <div class="land-band-label">Why us</div>
                <div class="land-band-title">Built around you</div>
                <div class="land-why-grid">
                    <div>
                        <div class="land-why-icon rose">✦</div>
                        <div class="land-why-title">Personalised Matching</div>
                        <p class="land-why-copy">Not a random list — every recommendation is scored for compatibility with your specific profile, concerns, and preferences.</p>
                    </div>
                    <div>
                        <div class="land-why-icon gold">◎</div>
                        <div class="land-why-title">Full Transparency</div>
                        <p class="land-why-copy">We don't just show you a match — we explain exactly why each counselor is suitable for you, so you can make an informed choice.</p>
                    </div>
                    <div>
                        <div class="land-why-icon sage">⬡</div>
                        <div class="land-why-title">No Account Needed</div>
                        <p class="land-why-copy">No sign-up, no password, no tracking. Just answer a few questions and get matched instantly — your privacy is respected.</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- ── CTA ────────────────────────────────────────────────────────── -->
        <div class="land-cta-band land-band">
            <div class="land-inner" style="position:relative;z-index:2;">
                <div class="land-cta-title">Ready to find your counselor?</div>
                <p class="land-cta-copy">It only takes a few minutes. No account required.</p>
                <a href="/?login=client" target="_self" class="land-cta-btn">Get matched now &rarr;</a>
            </div>
        </div>

        <!-- ── Staff link ──────────────────────────────────────────────────── -->
        <div class="land-staff-link">
            <a href="/?login=admin" target="_self">Staff access &rarr;</a>
        </div>
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


def _dialog_styles():
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


@st.dialog("Confirm logout")
def _logout_dialog():
    _dialog_styles()
    st.markdown("Are you sure you want to log out?")
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Log out", use_container_width=True):
            del st.session_state["role"]
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Go back to home?")
def _back_dialog():
    _dialog_styles()
    st.markdown("You'll need to start the matching process again.")
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go back", use_container_width=True):
            del st.session_state["role"]
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


# ── Sidebar brand wordmark ────────────────────────────────────────────────────
st.sidebar.markdown(
    """
    <div style="padding: 4px 2px 20px; border-bottom: 1px solid rgba(46,16,101,0.15); margin-bottom: 20px;">
        <div style="font-family: 'Fraunces', serif; font-size: 20px; font-weight: 600; color: #2E1065; letter-spacing: -0.3px; line-height: 1;">CC Match</div>
        <div style="font-size: 11px; color: rgba(46,16,101,0.55); margin-top: 3px; font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: 0.03em;">Counselor Matching System</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if role == "admin":
    st.sidebar.markdown(
        '<div style="font-size: 10px; font-weight: 700; letter-spacing: 0.12em; color: rgba(167,139,250,0.9); text-transform: uppercase; margin-bottom: 10px; font-family: \'Plus Jakarta Sans\', sans-serif;">Admin</div>',
        unsafe_allow_html=True,
    )
    page = st.sidebar.radio("Navigation", ["Match a Client", "Counselor Management", "Our Counselors", "Review Requests", "Enquiries", "Model Management"], label_visibility="collapsed")
else:
    st.sidebar.markdown(
        '<div style="font-size: 10px; font-weight: 700; letter-spacing: 0.12em; color: rgba(167,139,250,0.9); text-transform: uppercase; margin-bottom: 10px; font-family: \'Plus Jakarta Sans\', sans-serif;">Navigation</div>',
        unsafe_allow_html=True,
    )
    page = st.sidebar.radio("Navigation", ["Find a Counselor", "Our Counselors", "Chat with Mira", "About Us", "Contact Us"], label_visibility="collapsed")

st.sidebar.markdown('<div class="sidebar-spacer" style="flex-grow: 1; min-height: 50px;"></div>', unsafe_allow_html=True)

st.sidebar.markdown("---")

if role == "admin":
    st.sidebar.markdown(
        '<div style="font-size: 13px; color: rgba(255,255,255,0.45); margin-bottom: 12px; padding: 0 2px; font-family: \'Plus Jakarta Sans\', sans-serif;">Signed in as <strong style="color:rgba(255,255,255,0.85)">Admin</strong></div>',
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Log out", use_container_width=True):
        _logout_dialog()
else:
    if st.sidebar.button("Exit", use_container_width=True):
        _back_dialog()


if page in ["Match a Client", "Find a Counselor"]:
    show_matching_page()
elif page == "Counselor Management":
    show_manage_page()
elif page == "Review Requests":
    show_manage_request_page()
elif page == "Enquiries":
    show_enquiries_page()
elif page == "Model Management":
    show_model_performance_page()
elif page == "Our Counselors":
    show_counselors_page()
elif page == "Chat with Mira":
    show_chatbot_page()
elif page == "About Us":
    show_aboutus_page()
elif page == "Contact Us":
    show_contactus_page()
