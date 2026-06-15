import streamlit as st

from frontend.utils.api import send_enquiry_email


def show_contactus_page():
    st.markdown(
        """
        <style>
        /* ── Info cards ───────────────────────────────────────────────── */
        .cu-info-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 28px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
            height: 100%;
            transition: box-shadow 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
        }
        .cu-info-card:hover {
            box-shadow: 0 8px 24px rgba(157,99,232,0.1);
            border-color: rgba(157,99,232,0.25);
            transform: translateY(-2px);
        }
        .cu-info-icon {
            font-size: 28px;
            margin-bottom: 12px;
            line-height: 1;
        }
        .cu-info-label {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #9D63E8;
            margin-bottom: 6px;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .cu-info-value {
            font-size: 15px;
            font-weight: 600;
            color: #1C1917;
            margin-bottom: 4px;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .cu-info-sub {
            font-size: 13px;
            color: #9C9790;
            margin: 0;
            line-height: 1.5;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* ── Form card ────────────────────────────────────────────────── */
        .cu-form-card {
            background: #FFFFFF;
            border-radius: 20px;
            padding: 36px 40px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
            margin-top: 8px;
        }
        .cu-form-title {
            font-family: 'Fraunces', serif;
            font-size: 24px;
            color: #1C1917;
            margin-bottom: 6px;
            font-weight: 600;
        }
        .cu-form-sub {
            font-size: 14px;
            color: #9C9790;
            margin-bottom: 24px;
            line-height: 1.6;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* ── Hours card ───────────────────────────────────────────────── */
        .cu-hours-card {
            background: linear-gradient(135deg, #9D63E8 0%, #5E8AEE 100%);
            border-radius: 20px;
            padding: 32px 36px;
            margin-top: 8px;
            position: relative;
            overflow: hidden;
        }
        .cu-hours-card::before {
            content: '';
            position: absolute;
            top: -40px; right: -40px;
            width: 200px; height: 200px;
            background: radial-gradient(circle, rgba(255,255,255,0.25) 0%, transparent 70%);
            pointer-events: none;
        }
        .cu-hours-title {
            font-family: 'Fraunces', serif;
            font-size: 20px;
            color: #2E1065;
            margin-bottom: 20px;
            font-weight: 600;
        }
        .cu-hours-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(46,16,101,0.12);
        }
        .cu-hours-row:last-child {
            border-bottom: none;
        }
        .cu-hours-day {
            font-size: 14px;
            color: rgba(46,16,101,0.65);
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .cu-hours-time {
            font-size: 14px;
            font-weight: 600;
            color: #2E1065;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .cu-hours-closed {
            font-size: 14px;
            font-weight: 600;
            color: rgba(239,68,68,0.75);
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* ── Divider ──────────────────────────────────────────────────── */
        .cu-divider {
            border: none;
            border-top: 1px solid rgba(0,0,0,0.07);
            margin: 32px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding:24px 0 20px; border-bottom:1px solid rgba(0,0,0,0.07); margin-bottom:24px;">
            <div style="font-family:'Fraunces',serif; font-size:clamp(22px,3vw,36px); color:#1C1917; margin:0 0 8px; letter-spacing:-0.4px; line-height:1.12; font-weight:500;">Contact Us</div>
            <p style="font-size:14px; color:#6B6560; margin:0; line-height:1.6; font-family:'Plus Jakarta Sans',sans-serif;">Have a question or need support? Reach out and we'll get back to you within 24-48 hours.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Contact info cards ────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(
            """
            <div class="cu-info-card">
                <div class="cu-info-icon">📧</div>
                <div class="cu-info-label">Email</div>
                <div class="cu-info-value">support@cc-match.com</div>
                <p class="cu-info-sub">We reply within 24-48 hours on business days.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="cu-info-card">
                <div class="cu-info-icon">📞</div>
                <div class="cu-info-label">Phone</div>
                <div class="cu-info-value">+60 12-345 6789</div>
                <p class="cu-info-sub">Available Mon - Fri, 9 AM to 5 PM.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="cu-info-card">
                <div class="cu-info-icon">📍</div>
                <div class="cu-info-label">Location</div>
                <div class="cu-info-value">Kuala Lumpur, Malaysia</div>
                <p class="cu-info-sub">In-person sessions available by appointment.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="cu-divider">', unsafe_allow_html=True)

    # ── Form + Hours ──────────────────────────────────────────────────────────
    form_col, hours_col = st.columns([3, 2], gap="large")

    with form_col:
        st.markdown(
            """
            <div class="cu-form-card">
                <div class="cu-form-title">Send us a message</div>
                <p class="cu-form-sub">Fill in the form below and our coordinator will get back to you.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

        with st.form("contact_form", clear_on_submit=True):
            name = st.text_input("Your name", placeholder="e.g. Ahmad Faiz")
            email = st.text_input("Your email", placeholder="e.g. ahmad@email.com")
            subject = st.selectbox(
                "Subject",
                ["General Enquiry", "Help with Matching", "Request Follow-up", "Technical Issue", "Other"],
            )
            message = st.text_area("Message", placeholder="Tell us how we can help you...", height=140)
            submitted = st.form_submit_button("Send Message", use_container_width=True, type="primary")

        if submitted:
            if not name.strip() or not email.strip() or not message.strip():
                st.error("Please fill in your name, email, and message before sending.")
            elif "@" not in email or "." not in email:
                st.error("Please enter a valid email address.")
            else:
                try:
                    send_enquiry_email(name.strip(), email.strip(), subject, message.strip())
                    st.success(f"Thank you, {name.strip()}! Your message has been sent. We'll get back to you within 24-48 hours.")
                except Exception:
                    st.error("Failed to send your message. Please try again or email us directly.")

    with hours_col:
        st.markdown(
            """
            <div class="cu-hours-card">
                <div class="cu-hours-title" style="position:relative;z-index:2;">Office Hours</div>
                <div class="cu-hours-row" style="position:relative;z-index:2;">
                    <span class="cu-hours-day">Monday</span>
                    <span class="cu-hours-time">9:00 AM - 5:00 PM</span>
                </div>
                <div class="cu-hours-row" style="position:relative;z-index:2;">
                    <span class="cu-hours-day">Tuesday</span>
                    <span class="cu-hours-time">9:00 AM - 5:00 PM</span>
                </div>
                <div class="cu-hours-row" style="position:relative;z-index:2;">
                    <span class="cu-hours-day">Wednesday</span>
                    <span class="cu-hours-time">9:00 AM - 5:00 PM</span>
                </div>
                <div class="cu-hours-row" style="position:relative;z-index:2;">
                    <span class="cu-hours-day">Thursday</span>
                    <span class="cu-hours-time">9:00 AM - 5:00 PM</span>
                </div>
                <div class="cu-hours-row" style="position:relative;z-index:2;">
                    <span class="cu-hours-day">Friday</span>
                    <span class="cu-hours-time">9:00 AM - 5:00 PM</span>
                </div>
                <div class="cu-hours-row" style="position:relative;z-index:2;">
                    <span class="cu-hours-day">Saturday</span>
                    <span class="cu-hours-closed">Closed</span>
                </div>
                <div class="cu-hours-row" style="position:relative;z-index:2;">
                    <span class="cu-hours-day">Sunday</span>
                    <span class="cu-hours-closed">Closed</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
