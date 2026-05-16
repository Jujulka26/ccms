import pandas as pd
import streamlit as st
from frontend.utils.api import get_model_performance


def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

        .pm-stat-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 28px;
        }
        .pm-stat-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 24px 28px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }
        .pm-stat-eyebrow {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 12px;
        }
        .pm-stat-value {
            font-family: 'DM Serif Display', serif;
            font-size: 36px;
            line-height: 1;
            color: #1A1A2E;
            margin-bottom: 6px;
        }
        .pm-stat-label {
            font-size: 13px;
            color: #8B8B9A;
            font-weight: 400;
        }
        .pm-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 18px 24px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 2px 10px rgba(0,0,0,0.04);
            margin-bottom: 20px;
        }
        .pm-card-title {
            font-family: 'DM Serif Display', serif;
            font-size: 20px;
            color: #1A1A2E;
            margin: 0 0 4px;
        }
        .pm-card-copy {
            font-size: 14px;
            color: #5A5A6E;
            margin: 0;
        }
        [data-testid="block-container"] div[data-testid="stTabs"] {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 4px 20px 24px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
            margin-bottom: 20px;
        }
        div[data-testid="stTabs"] button[role="tab"] {
            font-family: 'DM Sans', sans-serif !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            padding: 12px 18px !important;
            color: #8B8B9A !important;
        }
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            font-weight: 700 !important;
            color: #1A1A2E !important;
        }
        div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
            background-color: #8B5CF6 !important;
            height: 3px !important;
            border-radius: 3px 3px 0 0 !important;
        }
        div[data-testid="stTabs"] [data-baseweb="tab-border"] {
            background-color: #F0EDE8 !important;
        }
        .pm-recommend {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, #FFFFFF 100%);
            border: 1px solid rgba(139, 92, 246, 0.25);
            border-radius: 16px;
            padding: 28px 32px;
            margin-top: 4px;
        }
        .pm-recommend-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #8B5CF6;
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 20px;
            padding: 4px 12px;
            margin-bottom: 14px;
        }
        .pm-recommend-title {
            font-family: 'DM Serif Display', serif;
            font-size: 22px;
            color: #1A1A2E;
            margin: 0 0 8px;
        }
        .pm-recommend-copy {
            font-size: 14px;
            color: #5A5A6E;
            line-height: 1.65;
            margin: 0;
        }
        .pm-note {
            background: rgba(245, 158, 11, 0.06);
            border-left: 3px solid #F59E0B;
            border-radius: 0 8px 8px 0;
            padding: 10px 16px;
            font-size: 13px;
            color: #5A5A6E;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_model_performance_page():
    inject_styles()

    st.markdown(
        """
        <div style="position: relative; overflow: hidden; background-color: #FAFDFC; background-image: radial-gradient(at 0% 0%, #D1FAE5 0px, transparent 60%), radial-gradient(at 100% 100%, #ECFDF5 0px, transparent 60%); border-radius: 20px; padding: 48px 48px; margin-bottom: 32px; border: 1px solid rgba(16,185,129,0.2); box-shadow: 0 16px 32px -8px rgba(16,185,129,0.12), inset 0 1px 0 rgba(255,255,255,0.9); min-height: 236px;">
            <div style="position: relative; z-index: 2; max-width: 65%;">
                <div style="color: #10B981; font-size: 11px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.25); border-radius: 20px; padding: 4px 14px; margin-bottom: 20px; display: inline-block;">Analytics</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 42px; color: #1A1A2E; margin-bottom: 16px; line-height: 1.15; letter-spacing: -0.5px;">Model Performance</div>
                <p style="font-size: 16px; color: #4A4A5C; margin: 0; line-height: 1.65; max-width: 480px;">Accuracy, F1 and ROC-AUC across all models at a glance.</p>
            </div>
            <div style="font-size: 110px; line-height: 1; position: absolute; right: 28px; bottom: -20px; z-index: 1; opacity: 0.15; transform: rotate(-5deg); pointer-events: none;">
                📊
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    data = get_model_performance()

    model_count = data["model_count"]
    best_roc = data["best_roc_auc"] * 100
    deployed_model = data.get("deployed_model", "Tuned LightGBM")
    df = pd.DataFrame(data["models"])
    tuning_models = data.get("tuning_models", [])

    st.markdown(
        f"""
        <div class="pm-stat-grid">
            <div class="pm-stat-card">
                <div class="pm-stat-eyebrow" style="color:#8B5CF6;">Models compared</div>
                <div class="pm-stat-value">{model_count}</div>
                <div class="pm-stat-label">evaluated at baseline</div>
            </div>
            <div class="pm-stat-card">
                <div class="pm-stat-eyebrow" style="color:#10B981;">Best ROC-AUC</div>
                <div class="pm-stat-value">{best_roc:.1f}%</div>
                <div class="pm-stat-label">after hyperparameter tuning</div>
            </div>
            <div class="pm-stat-card">
                <div class="pm-stat-eyebrow" style="color:#6366F1;">Deployed model</div>
                <div class="pm-stat-value" style="font-size:26px;padding-top:6px;">{deployed_model}</div>
                <div class="pm-stat-label">best after tuning — active in production</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<hr style="margin: 32px 0 32px 0; border: none; border-top: 1px solid rgba(0,0,0,0.15);" />', unsafe_allow_html=True)

    # ── Baseline comparison ──────────────────────────────────────────────────
    st.markdown(
        """
        <div class="pm-card">
            <div class="pm-card-title">Baseline model comparison</div>
            <p class="pm-card-copy">All candidate models evaluated at default settings before tuning.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="pm-note">Differences between top baseline models are within noise. '
        'LightGBM and CatBoost were selected for tuning. Tuned LightGBM achieved the best ROC-AUC '
        'and was chosen as the final deployed model.</div>',
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["📊  Table", "📈  Chart"])
    with tabs[0]:
        st.dataframe(df, use_container_width=True, hide_index=True)
    with tabs[1]:
        df_plot = df.set_index("Model")[["Accuracy", "F1", "ROC-AUC"]] * 100
        st.line_chart(df_plot, use_container_width=True)

    # ── Tuning comparison ────────────────────────────────────────────────────
    if tuning_models:
        st.markdown('<hr style="margin: 32px 0 32px 0; border: none; border-top: 1px solid rgba(0,0,0,0.15);" />', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="pm-card">
                <div class="pm-card-title">Tuning comparison — LightGBM vs CatBoost</div>
                <p class="pm-card-copy">LightGBM and CatBoost were the top two baseline models and were both tuned with RandomizedSearchCV (50 iterations). Tuned LightGBM achieved the best overall ROC-AUC and was selected as the deployed model.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        df_tuning = pd.DataFrame(tuning_models)

        tuning_tabs = st.tabs(["📊  Table", "📈  Chart"])
        with tuning_tabs[0]:
            st.dataframe(df_tuning, use_container_width=True, hide_index=True)
        with tuning_tabs[1]:
            df_tuning_plot = df_tuning.set_index("Model")[["Accuracy", "F1", "ROC-AUC"]] * 100
            st.bar_chart(df_tuning_plot, use_container_width=True)

    # ── Recommendation ───────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="pm-recommend">
            <div class="pm-recommend-badge">&#10003; &nbsp;Deployed Model</div>
            <div class="pm-recommend-title">{deployed_model} is the active model</div>
            <p class="pm-recommend-copy">
                LightGBM and CatBoost were the top two performers at baseline and were both tuned with
                RandomizedSearchCV. Tuned LightGBM achieved the highest ROC-AUC after tuning and was
                selected as the final deployed model for client-counselor matching.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
