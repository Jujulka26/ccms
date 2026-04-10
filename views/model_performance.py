import pandas as pd
import streamlit as st
from utils.ui import render_hero, open_card, close_card, render_stat


def show_model_performance_page():
    render_hero(
        "Model performance",
        "Compare and analyze model metrics at a glance. Track accuracy, F1 scores, and ROC-AUC to make informed decisions.",
        eyebrow="Analytics",
    )

    try:
        df = pd.read_csv("model_results.csv")

        metric_cols = ["Accuracy", "F1", "ROC-AUC"]
        df_scores = df.copy()
        df_scores["Overall"] = df_scores[metric_cols].mean(axis=1)

        top_model = df_scores.sort_values("Overall", ascending=False).iloc[0]
        
        # ── Key Metrics Section ───────────────────────────────────────
        st.markdown("<div style='margin-bottom: 28px;'><h3 style='font-family: DM Serif Display; font-size: 20px; color: #1A1A2E; margin: 0 0 16px 0;'>Key Metrics</h3></div>", unsafe_allow_html=True)
        
        stat_col1, stat_col2, stat_col3 = st.columns(3, gap="medium")
        with stat_col1:
            render_stat("Models compared", len(df))
        with stat_col2:
            render_stat("Best ROC-AUC", f"{df['ROC-AUC'].max() * 100:.1f}%")
        with stat_col3:
            render_stat("Best model", top_model["Model"])

        # ── Model Comparison Section ──────────────────────────────────
        st.markdown("<div style='margin: 32px 0 24px 0;'></div>", unsafe_allow_html=True)
        
        open_card("Model comparison", "Switch between detailed table and visual comparison.")
        
        tabs = st.tabs(["📊 Table", "📈 Chart"])
        
        with tabs[0]:
            st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        with tabs[1]:
            st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
            df_plot = df.set_index("Model")[["Accuracy", "F1", "ROC-AUC"]] * 100
            st.line_chart(df_plot, use_container_width=True)
        
        close_card()

        # ── Best Model Recommendation ──────────────────────────────────
        st.markdown("<div style='margin: 28px 0;'></div>", unsafe_allow_html=True)
        
        df_sorted = df_scores.sort_values("Overall", ascending=False)
        top_two = df_sorted.head(2)

        if top_two.iloc[0]["Overall"] - top_two.iloc[1]["Overall"] > 0.01:
            best = top_two.iloc[0]
            reason = "the highest overall average (Accuracy, F1, ROC-AUC)"
        else:
            best = top_two.iloc[0]
            reason = "overall strong performance across metrics"

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(255, 255, 255, 0.98) 100%); 
                        border: 1px solid rgba(16, 185, 129, 0.2); 
                        border-radius: 16px; 
                        padding: 24px; 
                        margin-top: 12px;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <span style="font-size: 20px;">✓</span>
                    <span style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #10B981;">Recommendation</span>
                </div>
                <p style="margin: 0; font-family: 'DM Serif Display', serif; font-size: 20px; color: #1A1A2E; font-weight: 700;">
                    {best['Model']} is your best choice
                </p>
                <p style="margin: 8px 0 0 0; font-size: 15px; color: #5A5A6E; line-height: 1.6;">
                    Based on {reason}.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    except Exception as e:
        st.error("❌ model_results.csv not found. Please run training first.")
