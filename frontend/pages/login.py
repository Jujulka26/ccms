import streamlit as st
from frontend.utils.api import login


def show_login_page():
    st.markdown(
        """
        <style>
        /* Soft branded backdrop glow behind the card for depth */
        .login-glow {
            position: fixed; top: -8%; left: 50%; transform: translateX(-50%);
            width: 680px; height: 460px; pointer-events: none; z-index: 0;
            background: radial-gradient(circle, rgba(157,99,232,0.16) 0%, rgba(94,138,238,0.05) 45%, transparent 72%);
        }

        /* ── Auth card ──────────────────────────────────────────────── */
        div[data-testid="stForm"] {
            background: #FFFFFF !important;
            border-radius: 24px !important;
            padding: 42px 40px 32px !important;
            box-shadow: 0 24px 60px rgba(46,16,101,0.14), 0 2px 8px rgba(0,0,0,0.04) !important;
            border: 1px solid rgba(157,99,232,0.10) !important;
            position: relative;
            overflow: hidden;
            margin-top: 28px;
        }
        /* Gradient lock badge */
        .login-badge {
            width: 62px; height: 62px; border-radius: 17px;
            background: linear-gradient(135deg, #9D63E8 0%, #5E8AEE 100%);
            box-shadow: 0 10px 24px rgba(157,99,232,0.38);
            display: flex; align-items: center; justify-content: center;
            margin: 4px auto 18px;
        }
        .login-eyebrow {
            font-size: 11px; font-weight: 700; letter-spacing: 0.14em;
            text-transform: uppercase; color: #9D63E8; text-align: center;
            margin-bottom: 8px; font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .login-title {
            font-family: 'Fraunces', serif;
            font-size: 30px; font-weight: 500; color: #1C1917;
            margin-bottom: 8px; text-align: center; line-height: 1.15;
            letter-spacing: -0.3px;
        }
        .login-subtitle {
            font-size: 14px; color: #6B6560; line-height: 1.6;
            text-align: center; margin-bottom: 28px;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* Sign in — brand gradient (covers the primaryFormSubmit kind) */
        div[data-testid="stForm"] button[kind*="primary"] {
            background: linear-gradient(135deg, #9D63E8 0%, #5E8AEE 100%) !important;
            border: none !important; color: #FFFFFF !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 700 !important; font-size: 15px !important;
            border-radius: 12px !important; padding: 13px !important;
            box-shadow: 0 6px 18px rgba(157,99,232,0.35) !important;
            transition: box-shadow 0.2s ease, transform 0.15s ease !important;
        }
        div[data-testid="stForm"] button[kind*="primary"]:hover {
            box-shadow: 0 9px 26px rgba(157,99,232,0.46) !important;
            transform: translateY(-1px) !important;
        }
        div[data-testid="stForm"] button[kind*="primary"]:active { transform: scale(0.98) !important; }

        /* Cancel — quiet ghost button, clearly secondary */
        div[data-testid="stForm"] button[kind*="secondary"] {
            background: transparent !important; border: none !important;
            color: #9C9790 !important; box-shadow: none !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important; font-size: 14px !important;
            padding: 9px !important;
        }
        div[data-testid="stForm"] button[kind*="secondary"]:hover {
            color: #6D28D9 !important; background: rgba(157,99,232,0.05) !important;
        }

        /* Security footer */
        .login-foot {
            display: flex; align-items: center; justify-content: center; gap: 6px;
            margin-top: 20px; font-size: 12px; color: #A29B94;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        </style>
        <div class="login-glow"></div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.3, 1])

    with col2:
        with st.form("admin_login_card", clear_on_submit=False):
            st.markdown(
                """
                <div class="login-badge">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF"
                         stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                        <circle cx="12" cy="16" r="1"/>
                    </svg>
                </div>
                <div class="login-eyebrow">CC Match &middot; Staff Portal</div>
                <div class="login-title">Welcome back</div>
                <div class="login-subtitle">Sign in to manage counselors, requests, and matching.</div>
                """,
                unsafe_allow_html=True,
            )

            email = st.text_input("Email", placeholder="you@ccmatch.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

            submitted = st.form_submit_button("Sign in", use_container_width=True, type="primary")
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

            st.markdown(
                """
                <div class="login-foot">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#A29B94"
                         stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                    Secure area &middot; authorised staff only
                </div>
                """,
                unsafe_allow_html=True,
            )

            if cancelled:
                st.session_state.role = None
                st.rerun()

            if submitted:
                if not email.strip() or not password.strip():
                    st.error("Please enter both email and password.")
                elif login(email.strip(), password.strip()):
                    st.session_state.role = "admin"
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
