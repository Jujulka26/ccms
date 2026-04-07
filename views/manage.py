import streamlit as st
from utils.db import add_counselor, delete_counselor, load_counselors, update_counselor
from utils.ui import render_hero, open_card, close_card, render_stat


GENDER_OPTIONS = ["Male", "Female"]
ETHNICITY_OPTIONS = ["Malay", "Chinese", "Indian", "Other"]
LANGUAGE_OPTIONS = ["English", "Malay", "Mandarin", "Tamil"]
SPECIALIZATION_OPTIONS = ["Anxiety", "Depression", "Stress", "Trauma"]
MODALITY_OPTIONS = ["CBT", "Humanistic", "Mindfulness", "REBT"]


def _option_index(options, value, default=0):
    if value is None:
        return default

    normalized = str(value).strip()
    if "," in normalized:
        normalized = normalized.split(",")[0].strip()

    return options.index(normalized) if normalized in options else default


@st.dialog("Add new counselor")
def render_add_counselor_dialog():
    with st.form("add_counselor_dialog_form"):
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            name = st.text_input("Name")
            age = st.number_input("Age", 20, 70, 30)
            gender = st.selectbox("Gender", GENDER_OPTIONS)
            ethnicity = st.selectbox("Ethnicity", ETHNICITY_OPTIONS)

        with col2:
            counselor_language = st.selectbox("Counselor language", LANGUAGE_OPTIONS, index=LANGUAGE_OPTIONS.index("Malay"))
            specialization = st.selectbox("Specialization", SPECIALIZATION_OPTIONS, index=SPECIALIZATION_OPTIONS.index("Stress"))
            counselor_modality = st.selectbox("Counselor modality", MODALITY_OPTIONS, index=MODALITY_OPTIONS.index("CBT"))
            experience_years = st.number_input("Years of Experience", 0, 30, 3)

        submitted = st.form_submit_button("Save counselor", use_container_width=True, type="primary")

    if submitted:
        add_counselor(name, age, gender, ethnicity, specialization, counselor_language, counselor_modality, experience_years)
        st.success("Counselor added successfully.")
        st.rerun()


@st.dialog("Edit counselor")
def render_edit_counselor_dialog():
    counselors_df = load_counselors()

    if counselors_df.empty:
        st.warning("No counselors found in database.")
        return

    counselor_options = counselors_df[["counselor_id", "name"]].copy()
    selected_id = st.selectbox(
        "Select counselor",
        counselor_options["counselor_id"].tolist(),
        format_func=lambda cid: f"ID {int(cid)} - {counselor_options.loc[counselor_options['counselor_id'] == cid, 'name'].iloc[0]}",
    )

    row = counselors_df.loc[counselors_df["counselor_id"] == selected_id].iloc[0]
    gender_index = _option_index(GENDER_OPTIONS, row.get("gender"))
    ethnicity_index = _option_index(ETHNICITY_OPTIONS, row.get("ethnicity"))
    language_index = _option_index(LANGUAGE_OPTIONS, row.get("counselor_language"))
    specialization_index = _option_index(SPECIALIZATION_OPTIONS, row.get("specialization"))
    modality_index = _option_index(MODALITY_OPTIONS, row.get("counselor_modality"))

    with st.form("edit_counselor_dialog_form"):
        edit_col1, edit_col2 = st.columns(2, gap="medium")

        with edit_col1:
            edit_name = st.text_input("Name", value=row["name"])
            edit_age = st.number_input("Age", 20, 70, int(row["age"]))
            edit_gender = st.selectbox("Gender", GENDER_OPTIONS, index=gender_index)
            edit_ethnicity = st.selectbox("Ethnicity", ETHNICITY_OPTIONS, index=ethnicity_index)

        with edit_col2:
            edit_language = st.selectbox("Counselor language", LANGUAGE_OPTIONS, index=language_index)
            edit_specialization = st.selectbox("Specialization", SPECIALIZATION_OPTIONS, index=specialization_index)
            edit_modality = st.selectbox("Counselor modality", MODALITY_OPTIONS, index=modality_index)
            edit_year_exp = st.number_input("Years of Experience", 0, 30, int(row["experience_years"]))

        submitted = st.form_submit_button("Update counselor", use_container_width=True, type="primary")

    if submitted:
        update_counselor(
            int(selected_id),
            edit_name,
            edit_age,
            edit_gender,
            edit_ethnicity,
            edit_specialization,
            edit_language,
            edit_modality,
            edit_year_exp,
        )
        st.success(f"Counselor {int(selected_id)} updated successfully.")
        st.rerun()


@st.dialog("Delete counselor")
def render_delete_counselor_dialog():
    counselors_df = load_counselors()

    if counselors_df.empty:
        st.warning("No counselors found in database.")
        return

    counselor_options = counselors_df[["counselor_id", "name"]].copy()
    selected_id = st.selectbox(
        "Select counselor to delete",
        counselor_options["counselor_id"].tolist(),
        format_func=lambda cid: f"ID {int(cid)} - {counselor_options.loc[counselor_options['counselor_id'] == cid, 'name'].iloc[0]}",
    )

    st.warning("This action cannot be undone.")
    confirm_delete = st.checkbox("I confirm this delete action")

    if st.button("Delete counselor", type="primary", use_container_width=True, disabled=not confirm_delete):
        delete_counselor(int(selected_id))
        st.success(f"Counselor {int(selected_id)} deleted successfully.")
        st.rerun()


def show_manage_page():
    counselors_df = load_counselors()

    render_hero(
        "Counselor Management",
        "Review counselor records, add new entries, and update existing profiles in one place.",
        eyebrow="Directory",
    )

    stat_col1, stat_col2, stat_col3 = st.columns(3, gap="medium")
    with stat_col1:
        render_stat("Total counselors", len(counselors_df))
    with stat_col2:
        st.markdown("##### Quick action")
        if st.button("Add counselor", use_container_width=True, type="primary"):
            render_add_counselor_dialog()
    with stat_col3:
        st.markdown("##### Manage record")
        edit_col, delete_col = st.columns(2, gap="small")
        with edit_col:
            if st.button("Edit", use_container_width=True, disabled=counselors_df.empty):
                render_edit_counselor_dialog()
        with delete_col:
            if st.button("Delete", use_container_width=True, disabled=counselors_df.empty):
                render_delete_counselor_dialog()

    open_card("Current directory", "Review counselors in the directory table.")

    if counselors_df.empty:
        st.warning("No counselors found in database.")
    else:
        st.dataframe(counselors_df, use_container_width=True, hide_index=True)

    close_card()

    if counselors_df.empty:
        return