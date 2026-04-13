import pandas as pd
import streamlit as st


def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

        /* ── Stat cards ───────────────────────────────────────────────── */
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

        /* ── Section Header / Subtle Card ─────────────────────────────── */
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
            text-shadow: none;
            margin: 0 0 4px;
        }
        .pm-card-copy {
            font-size: 14px;
            color: #5A5A6E;
            margin: 0;
        }

        /* ── Tab section card + styling ───────────────────────────────── */
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

        /* ── Recommendation banner ────────────────────────────────────── */
        .pm-recommend {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, #FFFFFF 100%);
            border: 1px solid rgba(245, 158, 11, 0.25);
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
            color: #F59E0B;
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.2);
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
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_model_performance_page():
    inject_styles()

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="app-hero">
            <div class="eyebrow">Analytics</div>
            <div class="hero-title">Model Performance</div>
            <p class="hero-copy">Compare and analyse model metrics at a glance. Track accuracy,
            F1 scores and ROC-AUC to make informed decisions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        df = pd.read_csv("model_results.csv")

        metric_cols = ["Accuracy", "F1", "ROC-AUC"]
        df_scores = df.copy()
        df_scores["Overall"] = df_scores[metric_cols].mean(axis=1)
        top_model = df_scores.sort_values("Overall", ascending=False).iloc[0]

        best_roc = df["ROC-AUC"].max() * 100
        model_count = len(df)
        best_name = top_model["Model"]

        # ── Stat cards ────────────────────────────────────────────────────────
        st.markdown(
            f"""
            <div class="pm-stat-grid">
                <div class="pm-stat-card">
                    <div class="pm-stat-eyebrow" style="color:#8B5CF6;">Models compared</div>
                    <div class="pm-stat-value">{model_count}</div>
                    <div class="pm-stat-label">evaluated in this run</div>
                </div>
                <div class="pm-stat-card">
                    <div class="pm-stat-eyebrow" style="color:#10B981;">Best ROC-AUC</div>
                    <div class="pm-stat-value">{best_roc:.1f}%</div>
                    <div class="pm-stat-label">highest discrimination score</div>
                </div>
                <div class="pm-stat-card">
                    <div class="pm-stat-eyebrow" style="color:#F59E0B;">Top model</div>
                    <div class="pm-stat-value" style="font-size:26px;padding-top:6px;">{best_name}</div>
                    <div class="pm-stat-label">best overall average</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # ── Model comparison section ──────────────────────────────────────────
        st.markdown(
            """
            <div class="pm-card">
                <div class="pm-card-title">Model comparison</div>
                <p class="pm-card-copy">Switch between the detailed table and visual comparison chart.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tabs = st.tabs(["📊  Table", "📈  Chart"])
        with tabs[0]:
            st.dataframe(df, use_container_width=True, hide_index=True)
        with tabs[1]:
            df_plot = df.set_index("Model")[["Accuracy", "F1", "ROC-AUC"]] * 100
            st.line_chart(df_plot, use_container_width=True)

        # ── Recommendation banner ─────────────────────────────────────────────
        df_sorted = df_scores.sort_values("Overall", ascending=False)
        top_two = df_sorted.head(2)

        if top_two.iloc[0]["Overall"] - top_two.iloc[1]["Overall"] > 0.01:
            reason = "the highest overall average across Accuracy, F1 and ROC-AUC"
        else:
            reason = "overall strong and consistent performance across all metrics"

        st.markdown(
            f"""
            <div class="pm-recommend">
                <div class="pm-recommend-badge">✓ &nbsp;Recommendation</div>
                <div class="pm-recommend-title">{best_name} is your best choice</div>
                <p class="pm-recommend-copy">Based on {reason}.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    except Exception:
        st.error("model_results.csv not found. Please run training first.")
