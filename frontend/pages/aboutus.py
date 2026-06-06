import streamlit as st


def show_aboutus_page():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

        /* ── Section title ────────────────────────────────────────────── */
        .au-section-title {
            font-family: 'DM Serif Display', serif;
            font-size: 28px;
            color: #1A1A2E;
            margin: 0 0 8px;
        }
        .au-section-sub {
            font-size: 15px;
            color: #8B8B9A;
            margin: 0 0 28px;
            line-height: 1.6;
        }

        /* ── Value cards ──────────────────────────────────────────────── */
        .au-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 28px 28px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            height: 100%;
            transition: box-shadow 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
        }
        .au-card:hover {
            box-shadow: 0 8px 24px rgba(124,58,237,0.1);
            border-color: rgba(139,92,246,0.3);
            transform: translateY(-2px);
        }
        .au-card-icon {
            font-size: 32px;
            margin-bottom: 14px;
            line-height: 1;
        }
        .au-card-title {
            font-family: 'DM Serif Display', serif;
            font-size: 18px;
            color: #1A1A2E;
            margin-bottom: 8px;
        }
        .au-card-body {
            font-size: 14px;
            color: #5A5A6E;
            line-height: 1.7;
            margin: 0;
        }

        /* ── How it works steps ───────────────────────────────────────── */
        .au-step {
            display: flex;
            gap: 20px;
            align-items: flex-start;
            margin-bottom: 24px;
        }
        .au-step-num {
            flex-shrink: 0;
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%);
            color: #FFFFFF;
            font-size: 15px;
            font-weight: 700;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .au-step-content-title {
            font-size: 15px;
            font-weight: 600;
            color: #1A1A2E;
            margin-bottom: 4px;
        }
        .au-step-content-body {
            font-size: 14px;
            color: #5A5A6E;
            line-height: 1.65;
            margin: 0;
        }

        /* ── Mission banner ───────────────────────────────────────────── */
        .au-mission {
            background: linear-gradient(135deg, #1A1A2E 0%, #2D1B6E 100%);
            border-radius: 20px;
            padding: 44px 48px;
            margin: 32px 0;
            position: relative;
            overflow: hidden;
        }
        .au-mission::before {
            content: '';
            position: absolute;
            top: -60px; right: -60px;
            width: 260px; height: 260px;
            background: radial-gradient(circle, rgba(139,92,246,0.22) 0%, transparent 70%);
            pointer-events: none;
        }
        .au-mission-label {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #A78BFA;
            margin-bottom: 14px;
        }
        .au-mission-text {
            font-family: 'DM Serif Display', serif;
            font-size: 26px;
            color: #FFFFFF;
            line-height: 1.45;
            margin: 0;
            max-width: 680px;
        }

        /* ── Divider ──────────────────────────────────────────────────── */
        .au-divider {
            border: none;
            border-top: 1px solid rgba(0,0,0,0.08);
            margin: 36px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding:24px 0 20px; border-bottom:1px solid rgba(0,0,0,0.07); margin-bottom:24px;">
            <div style="font-family:'DM Serif Display',serif; font-size:clamp(22px,3vw,34px); color:#1A1A2E; margin:0 0 8px; letter-spacing:-0.3px; line-height:1.15;">About Us</div>
            <p style="font-size:14px; color:#6B6B80; margin:0; line-height:1.6;">Learn about the mission and values behind CC Match.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Mission banner ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="au-mission">
            <div class="au-mission-label">Our Mission</div>
            <p class="au-mission-text">"To bridge the gap between individuals seeking mental health support and the counselors best equipped to help them — with transparency, empathy, and intelligent technology."</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── What we stand for ─────────────────────────────────────────────────────
    st.markdown('<div class="au-section-title">What we stand for</div>', unsafe_allow_html=True)
    st.markdown('<p class="au-section-sub">Our core values guide every decision we make in building this platform.</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(
            """
            <div class="au-card">
                <div class="au-card-icon">🔍</div>
                <div class="au-card-title">Transparency</div>
                <p class="au-card-body">We explain every match. You can always see exactly which factors drove your compatibility score — no black boxes, no guessing.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="au-card">
                <div class="au-card-icon">💜</div>
                <div class="au-card-title">Empathy First</div>
                <p class="au-card-body">Technology supports the process, but people are at the heart of it. Your comfort, safety, and wellbeing come before everything else.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="au-card">
                <div class="au-card-icon">🔒</div>
                <div class="au-card-title">Privacy & Trust</div>
                <p class="au-card-body">Your information is handled with care. We only collect what is needed to find your match and never share it without your consent.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="au-divider">', unsafe_allow_html=True)

    # ── How it works ──────────────────────────────────────────────────────────
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="au-section-title">How it works</div>', unsafe_allow_html=True)
        st.markdown('<p class="au-section-sub">A simple, guided process from start to your first session.</p>', unsafe_allow_html=True)

        steps = [
            ("Answer a short questionnaire", "Tell us about yourself — your concerns, preferences, language, and therapy style. It takes under 2 minutes."),
            ("Our AI finds your best match", "The model evaluates 8 compatibility factors across our counselor directory and calculates a personalised score for each."),
            ("Review your top matches", "See your top recommended counselors with full profiles and a clear breakdown of why each one was suggested."),
            ("Send a request", "Express interest in a counselor directly from the platform. Our team will be in touch within 24–48 hours to get you started."),
        ]

        for i, (title, body) in enumerate(steps, 1):
            st.markdown(
                f"""
                <div class="au-step">
                    <div class="au-step-num">{i}</div>
                    <div>
                        <div class="au-step-content-title">{title}</div>
                        <p class="au-step-content-body">{body}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown('<div class="au-section-title">About the technology</div>', unsafe_allow_html=True)
        st.markdown('<p class="au-section-sub">Responsible AI built for real-world mental health care.</p>', unsafe_allow_html=True)

        tech_cards = [
            ("🤖", "Machine Learning Matching", "Our model is trained on compatibility data across demographics, clinical needs, therapy modalities, and language preferences to find the most suitable counselor for you."),
            ("📊", "SHAP Explainability", "We use SHAP (SHapley Additive exPlanations) to break down every match score so you can see exactly which factors mattered most — fully transparent AI."),
            ("💬", "AI Mental Health Chatbot", "Before or after your match, our chatbot is here to listen, offer coping strategies, and guide you toward the support you need."),
        ]

        for icon, title, body in tech_cards:
            st.markdown(
                f"""
                <div class="au-card" style="margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
                        <span style="font-size: 22px;">{icon}</span>
                        <div class="au-card-title" style="margin: 0;">{title}</div>
                    </div>
                    <p class="au-card-body">{body}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="au-divider">', unsafe_allow_html=True)

    # ── Footer note ───────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align: center; padding: 8px 0 24px;">
            <div style="font-family: 'DM Serif Display', serif; font-size: 20px; color: #1A1A2E; margin-bottom: 8px;">Ready to find your match?</div>
            <p style="font-size: 14px; color: #8B8B9A; margin: 0;">Head to <strong style="color: #7C3AED;">Find a Counselor</strong> in the sidebar to get started.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
