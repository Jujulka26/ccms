import streamlit as st
from frontend.utils.api import login


def show_login_page():
    st.markdown(
        """
        <style>

        div[data-testid="stForm"] {
            background-color: #FFFFFF !important;
            border-radius: 20px !important;
            padding: 48px 40px !important;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06) !important;
            border: 1px solid rgba(0,0,0,0.06) !important;
            margin-top: 16px;
        }
        .login-title {
            font-family: 'Fraunces', serif;
            font-size: 32px;
            font-weight: 600;
            color: #1C1917;
            margin-bottom: 8px;
            text-align: center;
            line-height: 1.15;
        }
        .login-subtitle {
            font-size: 15px;
            color: #9C9790;
            line-height: 1.6;
            text-align: center;
            margin-bottom: 32px;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        with st.form("admin_login_card", clear_on_submit=False):
            st.markdown(
                """
                <div style="display:flex;justify-content:center;margin-bottom:20px;">
                    <div style="width:64px;height:64px;border-radius:18px;background:rgba(157,99,232,0.1);border:1px solid rgba(157,99,232,0.2);display:flex;align-items:center;justify-content:center;">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#9D63E8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                        </svg>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('<div class="login-title">Staff Login</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-subtitle">Authorised access only.</div>', unsafe_allow_html=True)

            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            st.markdown("##### ")

            submitted = st.form_submit_button("Sign in", use_container_width=True, type="primary")
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

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
