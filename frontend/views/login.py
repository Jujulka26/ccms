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
            box-shadow: 0 4px 20px rgba(0,0,0,0.04) !important;
            border: 1px solid rgba(0,0,0,0.06) !important;
            margin-top: 16px;
        }
        .login-title {
            font-family: 'DM Serif Display', serif;
            font-size: 32px;
            font-weight: 700;
            color: #1A1A2E;
            margin-bottom: 8px;
            text-align: center;
            line-height: 1.2;
        }
        .login-subtitle {
            font-size: 15px;
            color: #5A5A6E;
            line-height: 1.6;
            text-align: center;
            margin-bottom: 32px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        with st.form("admin_login_card", clear_on_submit=False):
            st.markdown('<div class="login-title">Admin Login</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-subtitle">Sign in to manage directory and models.</div>', unsafe_allow_html=True)

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
