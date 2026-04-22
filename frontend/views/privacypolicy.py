import streamlit as st


def show_privacypolicy_page():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

        /* ── Hero ─────────────────────────────────────────────────────── */
        .pp-hero {
            position: relative;
            overflow: hidden;
            background-color: #FAFAFF;
            background-image:
                radial-gradient(at 0% 0%, #E9DFFF 0px, transparent 60%),
                radial-gradient(at 100% 100%, #F0E6FF 0px, transparent 60%);
            border-radius: 20px;
            padding: 48px 52px;
            margin-bottom: 32px;
            border: 1px solid rgba(124,58,237,0.15);
            box-shadow: 0 16px 32px -8px rgba(124,58,237,0.12), inset 0 1px 0 rgba(255,255,255,0.9);
        }
        .pp-eyebrow {
            color: #8B5CF6;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            background: rgba(167,139,250,0.12);
            border: 1px solid rgba(167,139,250,0.25);
            border-radius: 20px;
            padding: 4px 14px;
            margin-bottom: 20px;
            display: inline-block;
        }
        .pp-hero-title {
            font-family: 'DM Serif Display', serif;
            font-size: 42px;
            color: #1A1A2E;
            margin-bottom: 16px;
            line-height: 1.15;
            letter-spacing: -0.5px;
        }
        .pp-hero-copy {
            font-size: 15px;
            color: #4A4A5C;
            margin: 0;
            line-height: 1.65;
            max-width: 520px;
        }
        .pp-hero-emoji {
            font-size: 90px;
            line-height: 1;
            position: absolute;
            right: 48px;
            bottom: -10px;
            opacity: 0.18;
            transform: rotate(-8deg);
            pointer-events: none;
        }
        .pp-updated {
            display: inline-block;
            margin-top: 18px;
            font-size: 12px;
            color: #8B8B9A;
        }

        /* ── Section card ─────────────────────────────────────────────── */
        .pp-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 32px 36px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            margin-bottom: 20px;
        }
        .pp-card-title {
            font-family: 'DM Serif Display', serif;
            font-size: 20px;
            color: #1A1A2E;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .pp-card-body {
            font-size: 14px;
            color: #4A4A5C;
            line-height: 1.75;
            margin: 0;
        }
        .pp-card-body ul {
            margin: 10px 0 0 0;
            padding-left: 20px;
        }
        .pp-card-body li {
            margin-bottom: 6px;
        }

        /* ── Highlight note ───────────────────────────────────────────── */
        .pp-note {
            background: rgba(139,92,246,0.06);
            border-left: 4px solid #8B5CF6;
            border-radius: 0 12px 12px 0;
            padding: 16px 20px;
            margin-top: 14px;
            font-size: 14px;
            color: #4A4A5C;
            line-height: 1.65;
        }

        /* ── Footer banner ────────────────────────────────────────────── */
        .pp-footer {
            background: linear-gradient(135deg, #1A1A2E 0%, #2D1B6E 100%);
            border-radius: 20px;
            padding: 36px 44px;
            margin-top: 12px;
            position: relative;
            overflow: hidden;
            text-align: center;
        }
        .pp-footer::before {
            content: '';
            position: absolute;
            top: -50px; right: -50px;
            width: 200px; height: 200px;
            background: radial-gradient(circle, rgba(139,92,246,0.22) 0%, transparent 70%);
            pointer-events: none;
        }
        .pp-footer-title {
            font-family: 'DM Serif Display', serif;
            font-size: 22px;
            color: #FFFFFF;
            margin-bottom: 8px;
        }
        .pp-footer-body {
            font-size: 14px;
            color: rgba(255,255,255,0.6);
            margin: 0;
        }
        .pp-footer-email {
            color: #A78BFA;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="pp-hero">
            <div style="position: relative; z-index: 2;">
                <div class="pp-eyebrow">Privacy Policy</div>
                <div class="pp-hero-title">Your privacy matters to us.</div>
                <p class="pp-hero-copy">We are committed to protecting the personal information you share with us. This policy explains what we collect, how we use it, and your rights.</p>
                <span class="pp-updated">Last updated: April 2026</span>
            </div>
            <div class="pp-hero-emoji">🔒</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Sections ──────────────────────────────────────────────────────────────
    sections = [
        (
            "📋", "What Information We Collect",
            """When you use our platform, we may collect the following information:
            <ul>
                <li><strong>Personal details</strong> — your name and email address when you submit a counselor match request or contact us.</li>
                <li><strong>Questionnaire responses</strong> — your age, gender, ethnicity, primary concern, language preference, therapy modality preference, and counselor gender preference.</li>
                <li><strong>Usage data</strong> — general interaction data within the platform (no cookies or tracking scripts are used).</li>
            </ul>""",
            None,
        ),
        (
            "🎯", "How We Use Your Information",
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
            "🤝", "Who We Share Your Data With",
            """We treat your data with strict confidentiality. Your information is only shared with:
            <ul>
                <li><strong>Your matched counselor</strong> — only after your request is approved by our clinic coordinator.</li>
                <li><strong>Our clinic coordinator</strong> — to review and process your match request internally.</li>
            </ul>""",
            "We do <strong>not</strong> sell, rent, or share your personal information with any third parties outside of the above.",
        ),
        (
            "🗄️", "Data Storage & Security",
            """Your data is stored securely in our database hosted on a local server. We take reasonable steps to protect your information from unauthorised access, including:
            <ul>
                <li>Password-protected admin access with hashed credentials.</li>
                <li>Role-based access control — only authorised admins can view request records.</li>
                <li>No sensitive health data beyond your stated primary concern is stored.</li>
            </ul>""",
            None,
        ),
        (
            "📅", "How Long We Keep Your Data",
            """We retain your information only for as long as necessary:
            <ul>
                <li>Match request records are kept for administrative and counseling coordination purposes.</li>
                <li>Contact form enquiries are not stored in our database — they are delivered to our inbox only.</li>
            </ul>
            You may request deletion of your data at any time by contacting us directly.""",
            None,
        ),
        (
            "✅", "Your Rights",
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
            "🔄", "Changes to This Policy",
            """We may update this Privacy Policy from time to time to reflect changes in our practices or legal requirements. When we do, the "Last updated" date at the top of this page will be revised. We encourage you to review this page periodically.""",
            None,
        ),
    ]

    for icon, title, body, note in sections:
        note_html = f'<div class="pp-note">{note}</div>' if note else ""
        st.markdown(
            f"""
            <div class="pp-card">
                <div class="pp-card-title">{icon} {title}</div>
                <div class="pp-card-body">{body}{note_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="pp-footer">
            <div class="pp-footer-title">Questions about your privacy?</div>
            <p class="pp-footer-body">Contact us at <span class="pp-footer-email">saltysmilesofficial@gmail.com</span> and we will respond within 24–48 hours.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
