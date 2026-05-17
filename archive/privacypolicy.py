import streamlit as st


def show_privacypolicy_page():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

        .pp-title {
            font-family: 'DM Serif Display', serif;
            font-size: 38px; color: #1A1A2E;
            margin: 0 0 14px; line-height: 1.15; letter-spacing: -0.5px;
        }
        .pp-intro {
            font-size: 15px; color: #5A5A6E;
            line-height: 1.7; margin: 0 0 10px; max-width: 640px;
        }
        .pp-meta {
            font-size: 12px; color: #ABABBB; margin: 0;
        }
        .pp-divider {
            border: none; border-top: 1px solid rgba(0,0,0,0.08); margin: 28px 0 32px;
        }

        .pp-card {
            background: #FFFFFF;
            border-radius: 16px; padding: 28px 32px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
            margin-bottom: 16px;
        }
        .pp-card-header {
            display: flex; align-items: center; gap: 14px; margin-bottom: 14px;
        }
        .pp-card-num {
            flex-shrink: 0;
            width: 30px; height: 30px;
            background: rgba(139,92,246,0.1);
            color: #7C3AED; font-size: 13px; font-weight: 700;
            border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
        }
        .pp-card-title {
            font-family: 'DM Serif Display', serif;
            font-size: 19px; color: #1A1A2E; margin: 0;
        }
        .pp-card-body {
            font-size: 14px; color: #4A4A5C; line-height: 1.8; margin: 0;
        }
        .pp-card-body ul {
            margin: 10px 0 0; padding-left: 20px;
        }
        .pp-card-body li { margin-bottom: 8px; }

        .pp-note {
            background: rgba(139,92,246,0.05);
            border-left: 3px solid #8B5CF6;
            border-radius: 0 8px 8px 0;
            padding: 14px 18px; margin-top: 16px;
            font-size: 14px; color: #4A4A5C; line-height: 1.65;
        }

        .pp-contact-box {
            background: #FAFAFF;
            border: 1px solid rgba(139,92,246,0.15);
            border-radius: 16px; padding: 32px 36px;
            margin-top: 8px; text-align: center;
        }
        .pp-contact-title {
            font-family: 'DM Serif Display', serif;
            font-size: 22px; color: #1A1A2E; margin-bottom: 10px;
        }
        .pp-contact-body {
            font-size: 14px; color: #5A5A6E; margin: 0; line-height: 1.6;
        }
        .pp-contact-email { color: #7C3AED; font-weight: 600; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Clean page header ─────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="pp-title">Privacy Policy</div>
        <p class="pp-intro">We are committed to protecting the personal information you share with us. This policy explains what we collect, how we use it, and your rights as a user of this platform.</p>
        <p class="pp-meta">Last updated: April 2026</p>
        <hr class="pp-divider">
        """,
        unsafe_allow_html=True,
    )

    # ── Sections ──────────────────────────────────────────────────────────────
    sections = [
        (
            "What Information We Collect",
            """When you use our platform, we may collect the following information:
            <ul>
                <li><strong>Personal details</strong> — your name and email address when you submit a counselor match request or contact us.</li>
                <li><strong>Questionnaire responses</strong> — your age, gender, ethnicity, primary concern, language preference, therapy modality preference, and counselor gender preference.</li>
                <li><strong>Usage data</strong> — general interaction data within the platform (no cookies or tracking scripts are used).</li>
            </ul>""",
            None,
        ),
        (
            "How We Use Your Information",
            """Your information is used solely for the following purposes:
            <ul>
                <li>To generate a personalised counselor compatibility score and recommend suitable matches.</li>
                <li>To process and manage your counselor match request.</li>
                <li>To send you email notifications regarding your request status (approved or rejected).</li>
                <li>To respond to enquiries you submit via our Contact Us page.</li>
            </ul>""",
            "We do <strong>not</strong> use your data for advertising, profiling beyond matching, or any commercial purposes.",
        ),
        (
            "Who We Share Your Data With",
            """We treat your data with strict confidentiality. Your information is only shared with:
            <ul>
                <li><strong>Your matched counselor</strong> — only after your request is approved by our clinic coordinator.</li>
                <li><strong>Our clinic coordinator</strong> — to review and process your match request internally.</li>
            </ul>""",
            "We do <strong>not</strong> sell, rent, or share your personal information with any third parties outside of the above.",
        ),
        (
            "Data Storage & Security",
            """Your data is stored securely in our database hosted on a local server. We take reasonable steps to protect your information from unauthorised access, including:
            <ul>
                <li>Password-protected admin access with hashed credentials.</li>
                <li>Role-based access control — only authorised admins can view request records.</li>
                <li>No sensitive health data beyond your stated primary concern is stored.</li>
            </ul>""",
            None,
        ),
        (
            "How Long We Keep Your Data",
            """We retain your information only for as long as necessary:
            <ul>
                <li>Match request records are kept for administrative and counseling coordination purposes.</li>
                <li>Contact form enquiries are not stored in our database — they are delivered to our inbox only.</li>
            </ul>
            You may request deletion of your data at any time by contacting us directly.""",
            None,
        ),
        (
            "Your Rights",
            """As a user of this platform, you have the right to:
            <ul>
                <li><strong>Access</strong> — request a copy of the personal data we hold about you.</li>
                <li><strong>Correction</strong> — ask us to correct inaccurate or incomplete information.</li>
                <li><strong>Deletion</strong> — request that your personal data be removed from our system.</li>
                <li><strong>Withdraw consent</strong> — stop using the platform at any time. Your data will not be used further once you withdraw.</li>
            </ul>""",
            "To exercise any of these rights, please reach out via our <strong>Contact Us</strong> page or email us directly.",
        ),
        (
            "Changes to This Policy",
            """We may update this Privacy Policy from time to time to reflect changes in our practices or legal requirements. When we do, the "Last updated" date at the top of this page will be revised. We encourage you to review this page periodically.""",
            None,
        ),
    ]

    for i, (title, body, note) in enumerate(sections, 1):
        note_html = f'<div class="pp-note">{note}</div>' if note else ""
        st.markdown(
            f"""
            <div class="pp-card">
                <div class="pp-card-header">
                    <div class="pp-card-num">{i}</div>
                    <div class="pp-card-title">{title}</div>
                </div>
                <div class="pp-card-body">{body}{note_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Contact note ──────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="pp-contact-box">
            <div class="pp-contact-title">Questions about your privacy?</div>
            <p class="pp-contact-body">Contact us at <span class="pp-contact-email">support@cc-match.com</span><br>and we will respond within 24–48 hours.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
