import streamlit as st
from utils.db import add_counselor, delete_counselor, load_counselors, update_counselor


def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

        /* ── Action cards row ─────────────────────────────────────────── */
        .mg-action-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }
        .mg-stat-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 24px 28px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }
        .mg-stat-eyebrow {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #8B5CF6;
            margin-bottom: 12px;
        }
        .mg-stat-value {
            font-family: 'DM Serif Display', serif;
            font-size: 40px;
            line-height: 1;
            color: #1A1A2E;
            margin-bottom: 6px;
        }
        .mg-stat-label {
            font-size: 13px;
            color: #8B8B9A;
        }
        .mg-action-label {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #8B8B9A;
            margin-bottom: 14px;
        }

        /* ── Table card ───────────────────────────────────────────────── */
        .mg-card {
            background: #FFFFFF;
            border-radius: 20px;
            padding: 32px 36px 28px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
            margin-bottom: 20px;
        }
        .mg-card-title {
            font-family: 'DM Serif Display', serif;
            font-size: 22px;
            color: #1A1A2E;
            margin: 0 0 4px;
        }
        .mg-card-copy {
            font-size: 14px;
            color: #8B8B9A;
            margin: 0 0 20px;
        }

        /* ── Button overrides (purple primary, ghost secondary) ───────── */
        /* Scope all button overrides to main content only — prevents leaking into sidebar */
        [data-testid="block-container"] div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(124,58,237,0.3) !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="block-container"] div[data-testid="stButton"] button[kind="primary"]:hover {
            box-shadow: 0 6px 18px rgba(124,58,237,0.4) !important;
            transform: translateY(-1px) !important;
        }
        [data-testid="block-container"] div[data-testid="stButton"] button[kind="secondary"] {
            border-radius: 10px !important;
            border: 1.5px solid #E5E2DC !important;
            background: #FFFFFF !important;
            color: #2D2D3F !important;
            font-weight: 600 !important;
            transition: all 0.18s ease !important;
        }
        [data-testid="block-container"] div[data-testid="stButton"] button[kind="secondary"]:hover {
            border-color: #8B5CF6 !important;
            color: #7C3AED !important;
        }
        [data-testid="block-container"] div[data-testid="stButton"] button:disabled {
            opacity: 0.4 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
    inject_styles()

    counselors_df = load_counselors()

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="app-hero">
            <div class="eyebrow">Directory</div>
            <div class="hero-title">Counselor Management</div>
            <p class="hero-copy">Review counselor records, add new entries, and update
            existing profiles in one place.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Stat + action cards ───────────────────────────────────────────────────
    stat_col, add_col, manage_col = st.columns(3, gap="medium")

    with stat_col:
        st.markdown(
            f"""
            <div class="mg-stat-card">
                <div class="mg-stat-eyebrow">Total counselors</div>
                <div class="mg-stat-value">{len(counselors_df)}</div>
                <div class="mg-stat-label">registered in directory</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with add_col:
        st.markdown('<div class="mg-stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="mg-action-label">Quick action</div>', unsafe_allow_html=True)
        if st.button("＋  Add counselor", use_container_width=True, type="primary"):
            render_add_counselor_dialog()
        st.markdown('</div>', unsafe_allow_html=True)

    with manage_col:
        st.markdown('<div class="mg-stat-card">', unsafe_allow_html=True)
        st.markdown('<div class="mg-action-label">Manage record</div>', unsafe_allow_html=True)
        edit_col, delete_col = st.columns(2, gap="small")
        with edit_col:
            if st.button("✎  Edit", use_container_width=True, disabled=counselors_df.empty):
                render_edit_counselor_dialog()
        with delete_col:
            if st.button("✕  Delete", use_container_width=True, disabled=counselors_df.empty):
                render_delete_counselor_dialog()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Directory table card ──────────────────────────────────────────────────
    st.markdown(
        """
        <div class="mg-card">
            <div class="mg-card-title">Current directory</div>
            <p class="mg-card-copy">Review all counselors registered in the system.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if counselors_df.empty:
        st.warning("No counselors found in the database.")
    else:
        st.dataframe(counselors_df, use_container_width=True, hide_index=True)

    if counselors_df.empty:
        return