import streamlit as st

def show_faq_page():
    st.markdown(
        """
        <style>
        .faq-header {
            font-family: 'DM Serif Display', serif;
            font-size: 38px;
            color: #1A1A2E;
            margin-bottom: 16px;
        }
        .faq-subheader {
            font-size: 16px;
            color: #5A5A6E;
            margin-bottom: 32px;
        }
        
        /* ── Override Streamlit Expander (Accordion) styling ── */
        div[data-testid="stExpander"] {
            border: 1px solid #E5E2DC !important;
            border-radius: 14px !important;
            background: #FFFFFF !important;
            margin-bottom: 16px !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
            overflow: hidden;
            transition: all 0.2s ease-in-out;
        }
        div[data-testid="stExpander"]:hover {
            border-color: #8B5CF6 !important;
            box-shadow: 0 4px 12px rgba(139,92,246,0.08) !important;
        }
        
        /* Header of the expander */
        div[data-testid="stExpander"] summary {
            padding: 20px 24px !important;
            font-family: 'DM Sans', sans-serif !important;
        }
        
        /* The Question text inside the summary */
        div[data-testid="stExpander"] summary p {
            font-size: 17px !important;
            font-weight: 600 !important;
            color: #1A1A2E !important;
            margin: 0 !important;
        }

        /* The arrow icon */
        div[data-testid="stExpander"] summary svg {
            color: #8B5CF6 !important;
            width: 20px !important;
            height: 20px !important;
        }

        /* The container body containing the Answer */
        div[data-testid="stExpanderDetails"] {
            padding: 0 24px 24px 24px !important;
            border-top: none !important;
        }
        
        /* The Answer text */
        div[data-testid="stExpanderDetails"] p {
            font-size: 15px !important;
            color: #4A4A5A !important;
            line-height: 1.7 !important;
            margin: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="faq-header">Frequently Asked Questions</div>', unsafe_allow_html=True)
    st.markdown('<div class="faq-subheader">Learn more about how our matching works and what to expect from your counseling journey.</div>', unsafe_allow_html=True)

    faqs = [
        {
            "q": "How does the AI matching algorithm work?",
            "a": "Our system uses a Machine Learning model that evaluates 9 different compatibility factors, including your primary concerns, language preferences, counselor specializations, and therapy modalities. It calculates a 'Compatibility Score' to predict which counselor is best suited to support you."
        },
        {
            "q": "What happens after I request to get to know a counselor?",
            "a": "Once you submit your name and email, your request is logged securely in our system. Our clinic coordinator will review your match and reach out to you via email within 24-48 hours to schedule your first session or answer any preliminary questions."
        },
        {
            "q": "What is SHAP and why do you show 'Technical details'?",
            "a": "SHAP (SHapley Additive exPlanations) is an AI explainability tool. We expose this to show complete transparency in why the algorithm matched you with a specific counselor. It breaks down exactly which factors (like shared language or age gap) most strongly influenced your high compatibility score."
        },
        {
            "q": "Can I change my counselor if it's not a good fit?",
            "a": "Absolutely. A strong therapeutic alliance is the most important part of counseling. If after your first session you feel the connection isn't quite right, our coordinator can help you rematch with your second recommended option or another counselor entirely."
        },
        {
            "q": "What's the difference between CBT and Humanistic therapy?",
            "a": "Cognitive Behavioral Therapy (CBT) is highly structured and focuses on identifying and changing negative thought patterns and behaviors. Humanistic therapy is more open-ended and focuses on self-exploration, personal growth, and understanding your true feelings in a non-judgmental space."
        }
    ]

    for item in faqs:
        with st.expander(item["q"]):
            st.write(item["a"])
