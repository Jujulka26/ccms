import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from utils.db import load_counselors
from utils.model import load_resources
from utils.ui import render_hero, open_card, close_card


ISSUE_SIMILARITY = {
    "Anxiety": {"Anxiety": 1.0, "Stress": 0.7, "Trauma": 0.5, "Depression": 0.6},
    "Stress": {"Stress": 1.0, "Anxiety": 0.7, "Trauma": 0.6, "Depression": 0.5},
    "Trauma": {"Trauma": 1.0, "Stress": 0.6, "Anxiety": 0.5, "Depression": 0.4},
    "Depression": {"Depression": 1.0, "Anxiety": 0.6, "Stress": 0.5, "Trauma": 0.4},
}


def issue_similarity_score(client_issue, counselor_specialization):
    return ISSUE_SIMILARITY.get(client_issue, {}).get(counselor_specialization, 0.0)


def previous_experience_value(previous_exp):
    try:
        return float(previous_exp)
    except (TypeError, ValueError):
        return 2.0


def experience_years_value(counselor):
    raw_years = counselor.get("experience_years")
    try:
        return float(raw_years)
    except (TypeError, ValueError):
        return 0.0


def engineer_features_from_df(df):
    """
    Engineer model features from a dataframe for model prediction.
    Expects columns: client_age, client_gender, client_ethnicity, client_issue, 
    previous_counseling_experience, preferred_language, preferred_modality, 
    preferred_counselor_gender, counselor_age, counselor_gender, counselor_ethnicity,
    counselor_language, counselor_modality, experience_years, specialization
    """
    rows = []
    for _, row in df.iterrows():
        try:
            client_age = float(row.get("client_age", 0))
            client_gender = row.get("client_gender", "")
            client_ethnicity = row.get("client_ethnicity", "")
            client_issue = row.get("client_issue", "")
            previous_exp = row.get("previous_counseling_experience", 2.0)
            preferred_language = row.get("preferred_language", "")
            preferred_modality = row.get("preferred_modality", "")
            preferred_c_gender = row.get("preferred_counselor_gender", "No preference")
            
            counselor_age = float(row.get("counselor_age", 0))
            counselor_gender = row.get("counselor_gender", "")
            counselor_ethnicity = row.get("counselor_ethnicity", "")
            counselor_languages = [v.strip() for v in str(row.get("counselor_language", "")).split(",") if v.strip()]
            counselor_modalities = [v.strip() for v in str(row.get("counselor_modality", "")).split(",") if v.strip()]
            exp_years = experience_years_value({"experience_years": row.get("experience_years", 0.0)})
            specialization = row.get("specialization", "")
            
            row_dict = {
                "issue_score": issue_similarity_score(client_issue, specialization),
                "modality_match": int(preferred_modality in counselor_modalities),
                "gender_match": 1 if preferred_c_gender == "No preference" else int(preferred_c_gender == counselor_gender),
                "ethnicity_match": int(client_ethnicity == counselor_ethnicity),
                "age_gap": abs(client_age - counselor_age),
                "client_age": client_age,
                "counselor_age": counselor_age,
                "exp_years": exp_years,
                "prev_exp": previous_experience_value(previous_exp),
            }
            rows.append(row_dict)
        except Exception:
            continue
    
    return pd.DataFrame(rows)


def get_shap_contributions(model_pipeline, background_data, x_row, feature_names):
    try:
        import shap
    except ImportError:
        return None, None, None, "SHAP is not installed. Run: pip install shap"

    try:
        background_df = background_data[feature_names].copy() if isinstance(background_data, pd.DataFrame) else pd.DataFrame(background_data, columns=feature_names)
        
        # Ensure background has sufficient samples for KernelExplainer
        if len(background_df) < 10:
            return None, None, None, "Insufficient background data for SHAP explanation (need at least 10 samples)"
        
        # Use up to 100 samples for stable baseline estimation
        if len(background_df) > 100:
            background_df = background_df.sample(100, random_state=42)

        def predict_positive_class(data):
            data_df = pd.DataFrame(data, columns=feature_names)
            return model_pipeline.predict_proba(data_df)[:, 1]

        explainer = shap.KernelExplainer(predict_positive_class, background_df.values, link="identity")
        shap_values = explainer.shap_values(x_row[feature_names].values, nsamples=200)

        # Ensure shap_values is properly extracted
        if isinstance(shap_values, list):
            row_contrib = np.array(shap_values[0])
        elif isinstance(shap_values, np.ndarray):
            if shap_values.ndim == 2:
                row_contrib = shap_values[0]  # Take first row if 2D
            else:
                row_contrib = shap_values  # Already 1D
        else:
            row_contrib = np.array(shap_values)

        expected = explainer.expected_value
        if isinstance(expected, list):
            base_value = float(expected[0])
        elif isinstance(expected, np.ndarray):
            base_value = float(expected[0]) if expected.size > 0 else 0.0
        else:
            base_value = float(expected)

        shap_df = pd.DataFrame({"feature": feature_names, "shap_value": row_contrib})
        shap_df["abs_shap"] = shap_df["shap_value"].abs()
        shap_df = shap_df.sort_values("abs_shap", ascending=False)
        return shap_df, row_contrib, base_value, None
    except Exception as exc:
        return None, None, None, f"Unable to generate SHAP explanation: {exc}"


def sorted_options(series):
    return sorted([value for value in series.dropna().unique().tolist() if str(value).strip()])


def modality_help_text(modality_options):
    descriptions = {
         "CBT": "Helps you change negative thoughts and behaviors.",
        "Humanistic": "Focuses on understanding your feelings in a supportive, non-judgmental way.",
        "Mindfulness": "Teaches you to stay calm and aware in the present moment.",
        "REBT": "Helps you challenge unhealthy beliefs and think more positively."
    }

    if not modality_options:
        return "Modality is the counseling approach used in sessions."

    parts = []
    for modality in modality_options:
        detail = descriptions.get(str(modality), "approach used in counseling sessions")
        parts.append(f"- {modality}: {detail}")

    return "Modality is the counseling approach/style:\n\n" + "\n".join(parts)


def scroll_to_results(anchor_id="match-results-anchor"):
    components.html(
        f"""
        <script>
        const anchor = window.parent.document.getElementById("{anchor_id}");
        if (anchor) {{
            anchor.scrollIntoView({{ behavior: "smooth", block: "start" }});
        }}
        </script>
        """,
        height=0,
        width=0,
    )


def show_matching_page():
    model, df_ref = load_resources()
    counselors = load_counselors()

    render_hero(
        "Client-Counselor Matching",
        "",
        eyebrow="Matching",
    )

    open_card(
        "Client profile",
        "Fill in details and preferences. The system compares all counselors and ranks the best fit.",
    )

    left, center, right = st.columns([1, 100, 1])
    with center:
        with st.form("client_form"):
            st.markdown("#### Client details")
            info_col1, info_col2 = st.columns(2, gap="medium")
            with info_col1:
                client_age = st.number_input("Client age", 18, 80, 25)
                client_gender = st.selectbox("Client gender", sorted_options(df_ref["client_gender"]))
                client_ethnicity = st.selectbox("Client ethnicity", sorted_options(df_ref["client_ethnicity"]))
            with info_col2:
                client_issue = st.selectbox("Presenting issue", sorted_options(df_ref["client_issue"]))
                previous_exp = st.selectbox(
                    "Previous counseling experience",
                    [0, 1],
                    format_func=lambda value: "Yes" if int(value) == 1 else "No",
                )

            st.markdown("#### Preferences")
            pref_col1, pref_col2 = st.columns(2, gap="medium")
            with pref_col1:
                preferred_language = st.selectbox("Preferred language", sorted_options(df_ref["preferred_language"]))
                modality_options = sorted_options(df_ref["preferred_modality"])
                preferred_modality = st.selectbox(
                    "Preferred modality",
                    modality_options,
                    help=modality_help_text(modality_options),
                )
            with pref_col2:
                preferred_c_gender = st.selectbox(
                    "Preferred counselor gender",
                    sorted_options(df_ref["preferred_counselor_gender"]),
                )

            submitted = st.form_submit_button("Find best counselor", use_container_width=True, type="primary")
    close_card()

    if not submitted:
        return

    if counselors.empty:
        st.error("No counselors in database.")
        return

    rows = []
    for _, counselor in counselors.iterrows():
        exp_years = experience_years_value(counselor)
        counselor_languages = [value.strip() for value in str(counselor.get("counselor_language", "")).split(",") if value.strip()]
        if preferred_language not in counselor_languages:
            continue
        counselor_modalities = [value.strip() for value in str(counselor.get("counselor_modality", "")).split(",") if value.strip()]
        counselor_age = counselor.get("age")
        counselor_gender = counselor.get("gender")
        counselor_ethnicity = counselor.get("ethnicity")
        rows.append(
            {
                "issue_score": issue_similarity_score(client_issue, counselor.specialization),
                "modality_match": int(preferred_modality in counselor_modalities),
                "gender_match": 1 if preferred_c_gender == "No preference" else int(preferred_c_gender == counselor_gender),
                "ethnicity_match": int(client_ethnicity == counselor_ethnicity),
                "age_gap": abs(float(client_age) - float(counselor_age)),
                "client_age": client_age,
                "counselor_age": counselor_age,
                "exp_years": exp_years,
                "prev_exp": previous_experience_value(previous_exp),
                "counselor_id": counselor.counselor_id,
            }
        )

    if not rows:
        st.warning(f"No counselors found who support {preferred_language}.")
        return

    input_df = pd.DataFrame(rows)
    feature_order = [
        'issue_score',
        'modality_match',
        'gender_match',
        'ethnicity_match',
        'age_gap',
        'client_age',
        'counselor_age',
        'exp_years',
        'prev_exp'
    ]
    X = input_df[feature_order]

    input_df["compatibility"] = model.predict_proba(X)[:, 1] * 100
    ranked = input_df.sort_values("compatibility", ascending=False)
    best = ranked.iloc[0]
    best_c = counselors[counselors.counselor_id == best.counselor_id].iloc[0]
    second = ranked.iloc[1] if len(ranked) > 1 else None
    second_c = counselors[counselors.counselor_id == second.counselor_id].iloc[0] if second is not None else None

    st.markdown('<div id="match-results-anchor"></div>', unsafe_allow_html=True)
    scroll_to_results()

    open_card("Top recommendation", "The best-ranked counselor based on the submitted profile.")
    metric_col1, metric_col2 = st.columns([1, 1], gap="medium")
    with metric_col1:
        st.metric("Compatibility", f"{best.compatibility:.1f}%")
        st.markdown(f"""
        **Top counselor name:** {best_c['name']}  
        **Age:** {best_c['age']}  
        **Gender:** {best_c['gender']}  
        **Specialization:** {best_c['specialization']}  
        **Language:** {best_c['counselor_language']}  
        **Modality:** {best_c['counselor_modality']}  
        **Experience Years:** {best_c['experience_years']}
        """)
    with metric_col2:
        second_score = f"{ranked.iloc[1].compatibility:.1f}%" if len(ranked) > 1 else "-"
        st.metric("Second option", second_score)
        if second_c is not None:
            st.markdown(f"""
        **Second option name:** {second_c['name']}  
        **Age:** {second_c['age']}  
        **Gender:** {second_c['gender']}  
        **Specialization:** {second_c['specialization']}  
        **Language:** {second_c['counselor_language']}  
        **Modality:** {second_c['counselor_modality']}  
        **Experience Years:** {second_c['experience_years']}
        """)
        else:
            st.caption("No second option available.")
    close_card()

    tabs = st.tabs(["All matches", "Why this match"])

    with tabs[0]:
        open_card("Match ranking", "A quick comparison of all available counselors.")
        ranked_view = ranked[["counselor_id", "compatibility"]].copy()
        ranked_view["compatibility"] = ranked_view["compatibility"].map(lambda value: f"{value:.1f}%")
        st.dataframe(ranked_view, use_container_width=True, hide_index=True)
        close_card()

    with tabs[1]:
        open_card("Explanation", "Simple summary first. Technical model details are optional below.")

        positive_points = []
        negative_points = []

        positive_points.append(f"Supports preferred language ({preferred_language})")

        if int(best.modality_match) == 1:
            positive_points.append(f"Modality matched ({preferred_modality})")
        else:
            negative_points.append(f"Modality not matched ({preferred_modality})")

        if float(best.issue_score) >= 0.99:
            positive_points.append(f"Specialization matched ({client_issue})")
        elif float(best.issue_score) >= 0.6:
            positive_points.append(f"Related specialization support ({client_issue})")
        else:
            negative_points.append(f"Specialization less aligned ({client_issue})")

        if preferred_c_gender != "No preference":
            if int(best.gender_match) == 1:
                positive_points.append(f"Preferred gender matched ({preferred_c_gender})")
            else:
                negative_points.append(f"Preferred gender not matched ({preferred_c_gender})")

        explain_col1, explain_col2 = st.columns([1, 1], gap="large")

        with explain_col1:
            st.markdown("**Quick summary**")
            if positive_points:
                for item in positive_points[:3]:
                    st.write(f"- {item}")
            else:
                st.write("- No strong positive driver detected.")

        with explain_col2:
            st.markdown("**Things to review**")
            if negative_points:
                for item in negative_points[:3]:
                    st.write(f"- {item}")
            else:
                st.write("- No major concern detected.")

        with st.expander("Technical details (optional)", expanded=False):
            best_index = ranked.index[0]
            x_best = X.loc[[best_index]]
            
            # Use training data (df_ref) as background for proper SHAP baseline
            df_ref_engineered = engineer_features_from_df(df_ref)
            if len(df_ref_engineered) > 0:
                background_data = df_ref_engineered
            else:
                background_data = X.sample(min(25, len(X)), random_state=42)
            
            shap_df, row_contrib, base_value, shap_error = get_shap_contributions(model, background_data, x_best, feature_order)

            if shap_error:
                st.info(shap_error)
            else:
                readable_names = {
                    "issue_score": "Issue Similarity",
                    "modality_match": "Preferred Modality Match",
                    "gender_match": "Preferred Gender Match",
                    "ethnicity_match": "Ethnicity Match",
                    "age_gap": "Age Gap",
                    "client_age": "Client Age",
                    "counselor_age": "Counselor Age",
                    "exp_years": "Counselor Experience (Years)",
                    "prev_exp": "Client Previous Experience",
                }

                shap_df["feature"] = shap_df["feature"].map(lambda value: readable_names.get(value, value))
                st.caption("Positive SHAP values increase the predicted compatibility. Negative values decrease it.")
                st.bar_chart(shap_df.set_index("feature")["shap_value"])
                st.dataframe(
                    shap_df[["feature", "shap_value"]].rename(columns={"shap_value": "contribution"}),
                    use_container_width=True,
                    hide_index=True,
                )

                st.markdown("#### Detailed SHAP charts")
                try:
                    import matplotlib.pyplot as plt
                    import shap

                    feature_labels = [readable_names.get(feature, feature) for feature in feature_order]
                    row_data = x_best.iloc[0][feature_order].values
                    explanation = shap.Explanation(
                        values=row_contrib,
                        base_values=base_value,
                        data=row_data,
                        feature_names=feature_labels,
                    )

                    fig_waterfall = plt.figure(figsize=(11, 5))
                    shap.plots.waterfall(explanation, max_display=10, show=False)
                    st.pyplot(fig_waterfall, clear_figure=True)

                    fig_force = plt.figure(figsize=(11, 3))
                    shap.force_plot(
                        base_value,
                        row_contrib,
                        row_data,
                        feature_names=feature_labels,
                        matplotlib=True,
                        show=False,
                    )
                    st.pyplot(fig_force, clear_figure=True)
                except Exception as exc:
                    st.info(f"Could not render SHAP waterfall/force chart: {exc}")

        close_card()
