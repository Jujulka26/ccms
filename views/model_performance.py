import pandas as pd
import streamlit as st
from utils.ui import render_hero, open_card, close_card, render_stat


def show_model_performance_page():
    render_hero(
        "Model performance",
        "A simple view of model metrics so you can compare performance without digging through raw output.",
        eyebrow="Analytics",
    )

    try:
        df = pd.read_csv("model_results.csv")

        metric_cols = ["Accuracy", "F1", "ROC-AUC"]
        df_scores = df.copy()
        df_scores["Overall"] = df_scores[metric_cols].mean(axis=1)

        top_model = df_scores.sort_values("Overall", ascending=False).iloc[0]
        stat_col1, stat_col2, stat_col3 = st.columns(3, gap="medium")
        with stat_col1:
            render_stat("Models compared", len(df))
        with stat_col2:
            render_stat("Best ROC-AUC", f"{df['ROC-AUC'].max() * 100:.1f}%")
        with stat_col3:
            render_stat("Best model", top_model["Model"])

        open_card("Model comparison", "Switch between table and chart view.")
        tabs = st.tabs(["Table", "Chart"])
        with tabs[0]:
            st.dataframe(df, use_container_width=True, hide_index=True)
        with tabs[1]:
            df_plot = df.set_index("Model")[["Accuracy", "F1", "ROC-AUC"]] * 100
            st.line_chart(df_plot)
        close_card()

        df_sorted = df_scores.sort_values("Overall", ascending=False)
        top_two = df_sorted.head(2)

        if top_two.iloc[0]["Overall"] - top_two.iloc[1]["Overall"] > 0.01:
            best = top_two.iloc[0]
            reason = "the highest overall average (Accuracy, F1, ROC-AUC)"
        else:
            best = top_two.iloc[0]
            reason = "overall strong performance across metrics"

        st.success(f"Best model: {best['Model']} based on {reason}.")

    except Exception:
        st.error("model_results.csv not found. Please run training first.")
