import streamlit as st
from frontend.views.manage import show_manage_page
from frontend.views.matching import show_matching_page
from frontend.views.model_performance import show_model_performance_page
from frontend.views.login import show_login_page
from frontend.views.chatbot import show_chatbot_page
from frontend.views.manage_request import render as show_manage_request_page
from frontend.views.aboutus import show_aboutus_page
from frontend.views.contactus import show_contactus_page
from frontend.views.privacypolicy import show_privacypolicy_page
from frontend.views.counselors import show_counselors_page


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

        [data-stale="true"] { opacity: 0 !important; transition: none !important; }

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

        /* ── Nav radio group — fill full sidebar width ────────────────── */
        /* Streamlit gives the radio stElementContainer width="fit-content" (confirmed via DOM).
           All other sidebar elements get width="100%". Target it directly. */
        section[data-testid="stSidebar"] [data-testid="stElementContainer"][width="fit-content"],
        section[data-testid="stSidebar"] [data-testid="stRadio"],
        section[data-testid="stSidebar"] [role="radiogroup"] {
            width: 100% !important;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] {
            display: flex !important;
            flex-direction: column !important;
            align-items: stretch !important;
            gap: 6px !important;
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

        /* ── Landing page ─────────────────────────────────────────────── */

        /* Shared button */
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
            box-shadow: 0 4px 20px rgba(139,92,246,0.4);
        }
        .land-cta-btn:hover {
            background: #7C3AED;
            box-shadow: 0 8px 28px rgba(139,92,246,0.55);
            transform: translateY(-1px);
        }

        /* Full-bleed band wrapper */
        .land-band {
            padding: 80px clamp(24px, 8vw, 120px);
        }
        /* Inner max-width centering */
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
            top: -120px; right: -80px;
            width: 500px; height: 500px;
            background: radial-gradient(circle, rgba(139,92,246,0.2) 0%, transparent 60%);
            pointer-events: none;
        }
        .land-hero-band::after {
            content: '';
            position: absolute;
            bottom: -80px; left: -40px;
            width: 350px; height: 350px;
            background: radial-gradient(circle, rgba(16,185,129,0.1) 0%, transparent 60%);
            pointer-events: none;
        }
        .land-hero-eyebrow {
            display: inline-block;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #A78BFA;
            background: rgba(167,139,250,0.12);
            border: 1px solid rgba(167,139,250,0.25);
            border-radius: 20px;
            padding: 5px 16px;
            margin-bottom: 28px;
        }
        .land-hero-title {
            font-family: 'DM Serif Display', serif;
            font-size: 58px;
            line-height: 1.08;
            color: #FFFFFF;
            margin: 0 auto 24px;
            letter-spacing: -1.5px;
            max-width: 720px;
        }
        .land-hero-copy {
            font-size: 18px;
            color: rgba(255,255,255,0.52);
            max-width: 500px;
            line-height: 1.72;
            margin: 0 auto 44px;
            text-align: center;
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
            color: #8B5CF6;
            text-align: center;
            margin-bottom: 12px;
        }
        .land-band-title {
            font-family: 'DM Serif Display', serif;
            font-size: 36px;
            color: #1A1A2E;
            text-align: center;
            margin: 0 0 48px;
        }
        .land-steps {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }
        .land-step {
            padding: 36px 32px;
            background: #FFFFFF;
            border-radius: 16px;
            box-shadow: 0 2px 12px rgba(139,92,246,0.06);
        }
        .land-step-num {
            font-family: 'DM Serif Display', serif;
            font-size: 44px;
            line-height: 1;
            margin-bottom: 20px;
        }
        .land-step-num.n1 { color: #C4B5FD; }
        .land-step-num.n2 { color: #8B5CF6; }
        .land-step-num.n3 { color: #5B21B6; }
        .land-step-title {
            font-size: 16px;
            font-weight: 700;
            color: #1A1A2E;
            margin-bottom: 10px;
        }
        .land-step-copy {
            font-size: 14px;
            color: #5A5A6E;
            line-height: 1.7;
            margin: 0;
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
        .land-why-icon.purple { background: rgba(139,92,246,0.12); }
        .land-why-icon.green  { background: rgba(16,185,129,0.12); }
        .land-why-icon.blue   { background: rgba(59,130,246,0.12); }
        .land-why-title {
            font-size: 16px;
            font-weight: 700;
            color: #1A1A2E;
            margin-bottom: 10px;
        }
        .land-why-copy {
            font-size: 14px;
            color: #5A5A6E;
            line-height: 1.72;
            margin: 0;
        }

        /* CTA band */
        .land-cta-band {
            background: linear-gradient(135deg, #0F0E1A 0%, #1E1048 100%);
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .land-cta-band::before {
            content: '';
            position: absolute;
            top: -80px; right: -80px;
            width: 360px; height: 360px;
            background: radial-gradient(circle, rgba(139,92,246,0.22) 0%, transparent 60%);
            pointer-events: none;
        }
        .land-cta-title {
            font-family: 'DM Serif Display', serif;
            font-size: 38px;
            color: #FFFFFF;
            margin: 0 0 14px;
        }
        .land-cta-copy {
            font-size: 16px;
            color: rgba(255,255,255,0.48);
            margin: 0 0 36px;
        }

        /* Staff link */
        .land-staff-link {
            background: #FFFFFF;
            text-align: center;
            padding: 18px 0 20px;
            border-top: 1px solid rgba(0,0,0,0.06);
        }
        .land-staff-link a {
            font-size: 12px;
            color: #C4C4D0 !important;
            text-decoration: none !important;
            letter-spacing: 0.04em;
            transition: color 0.2s;
        }
        .land-staff-link a:hover { color: #8B5CF6 !important; }

        @media (max-width: 768px) {
            .hero-title { font-size: 32px; }
            .landing-title { font-size: 22px; }
            .land-hero-title { font-size: 36px; }
            .land-steps, .land-why-grid { grid-template-columns: 1fr; }
            .land-step:first-child, .land-step:last-child { border-radius: 16px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Client-Counselor Matching System", layout="wide")
inject_app_styles()


if "role" not in st.session_state:
    # Override Streamlit container so sections bleed edge-to-edge
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
                <div class="land-hero-eyebrow">AI-Powered Counselor Matching</div>
                <div class="land-hero-title">Find the right counselor,<br>matched just for you</div>
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
                        <div class="land-why-icon purple">✦</div>
                        <div class="land-why-title">Personalised Matching</div>
                        <p class="land-why-copy">Not a random list — every recommendation is scored for compatibility with your specific profile, concerns, and preferences.</p>
                    </div>
                    <div>
                        <div class="land-why-icon green">◎</div>
                        <div class="land-why-title">Full Transparency</div>
                        <p class="land-why-copy">We don't just show you a match — we explain exactly why each counselor is suitable for you, so you can make an informed choice.</p>
                    </div>
                    <div>
                        <div class="land-why-icon blue">⬡</div>
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


if role == "admin":
    st.sidebar.markdown(
        '<div style="font-size: 11px; font-weight: 600; letter-spacing: 0.12em; color: #A78BFA; text-transform: uppercase; margin-bottom: 12px;">Admin Navigation</div>',
        unsafe_allow_html=True
    )
    page = st.sidebar.radio("Navigation", ["Match a Client", "Counselor Management", "Our Counselors", "Review Requests", "Model Management"], label_visibility="collapsed")
else:
    st.sidebar.markdown(
        '<div style="font-size: 11px; font-weight: 600; letter-spacing: 0.12em; color: #A78BFA; text-transform: uppercase; margin-bottom: 12px;">Client Navigation</div>',
        unsafe_allow_html=True
    )
    page = st.sidebar.radio("Navigation", ["Find a Counselor", "Our Counselors", "Chat with Mira", "About Us", "Contact Us"], label_visibility="collapsed")

# Invisible spacer — pushes the footer to the bottom of the sidebar
st.sidebar.markdown('<div class="sidebar-spacer" style="flex-grow: 1; min-height: 50px;"></div>', unsafe_allow_html=True)

st.sidebar.markdown("---")

if role == "admin":
    st.sidebar.markdown(
        f'<div style="font-size: 13px; color: rgba(255,255,255,0.55); margin-bottom: 12px; padding: 0 2px;">Signed in as <strong style="color:rgba(255,255,255,0.9)">Admin</strong></div>',
        unsafe_allow_html=True
    )
    if st.sidebar.button("Log out", use_container_width=True):
        _logout_dialog()
else:
    if st.sidebar.button("← Back to home", use_container_width=True):
        _back_dialog()


if page in ["Match a Client", "Find a Counselor"]:
    show_matching_page()
elif page == "Counselor Management":
    show_manage_page()
elif page == "Review Requests":
    show_manage_request_page()
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
