import math
import streamlit as st
import pandas as pd
from pathlib import Path
from frontend.utils.api import get_counselors, add_counselor, update_counselor, delete_counselor, get_reference_data

_IMG_DIR = Path(__file__).parent.parent / "assets" / "profile"


def _save_image(file, name: str) -> str:
    _IMG_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(file.name).suffix.lower()
    filename = name.strip().lower().replace(" ", "_") + ext
    (_IMG_DIR / filename).write_bytes(file.read())
    return filename


def inject_styles():
    st.markdown(
        """
        <style>

        .mg-stat-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 24px 28px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 1px 4px rgba(0,0,0,0.03);
        }
        .mg-stat-eyebrow {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #9D63E8;
            margin-bottom: 12px;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .mg-stat-value {
            font-family: 'Fraunces', serif;
            font-size: 40px;
            line-height: 1;
            color: #1C1917;
            margin-bottom: 6px;
            font-weight: 600;
        }
        .mg-stat-label {
            font-size: 13px;
            color: #9C9790;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .mg-action-label {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #9C9790;
            margin-bottom: 14px;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* ── Table card ───────────────────────────────────────────────── */
        .mg-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 18px 24px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
            margin-bottom: 20px;
        }
        .mg-card-title {
            font-family: 'Fraunces', serif;
            font-size: 20px;
            color: #1C1917;
            margin: 0 0 4px;
            font-weight: 600;
        }
        .mg-card-copy {
            font-size: 14px;
            color: #9C9790;
            margin: 0;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* ── st.container(border=True) styled as action card ─────────── */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #FFFFFF !important;
            border-radius: 16px !important;
            border: 1px solid rgba(0,0,0,0.06) !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.03) !important;
            padding: 8px 4px !important;
        }

        /* ── Button overrides (navy primary, ghost secondary) ─────────── */
        [data-testid="block-container"] div[data-testid="stButton"] button[kind="primary"],
        div[data-testid="stButton"] button[kind="primary"] {
            background: #2E1065 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(14,24,35,0.25) !important;
            transition: all 0.2s ease !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        [data-testid="block-container"] div[data-testid="stButton"] button[kind="primary"]:hover {
            background: #9D63E8 !important;
            box-shadow: 0 6px 18px rgba(157,99,232,0.35) !important;
            transform: translateY(-1px) !important;
        }
        [data-testid="block-container"] div[data-testid="stButton"] button[kind="secondary"] {
            border-radius: 10px !important;
            border: 1.5px solid #F0E8FF !important;
            background: #FFFFFF !important;
            color: #1C1917 !important;
            font-weight: 600 !important;
            transition: all 0.18s ease !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        [data-testid="block-container"] div[data-testid="stButton"] button[kind="secondary"]:hover {
            border-color: #9D63E8 !important;
            color: #9D63E8 !important;
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
MODALITY_OPTIONS = ["Cognitive", "Behavioral", "Humanistic", "Psychodynamic"]
TIME_BLOCK_OPTIONS = ["Weekday Morning", "Weekday Afternoon", "Weekday Evening", "Weekend"]


def _option_index(options, value, default=0):
    if value is None:
        return default
    normalized = str(value).strip()
    if "," in normalized:
        normalized = normalized.split(",")[0].strip()
    return options.index(normalized) if normalized in options else default


def safe_str(val):
    if val is None:
        return ""
    if isinstance(val, float) and math.isnan(val):
        return ""
    return str(val)


@st.dialog("Add new counselor", width="large")
def render_add_counselor_dialog():
    with st.form("add_counselor_dialog_form"):
        tab1, tab2 = st.tabs(["Basic Info", "Profile Details"])

        with tab1:
            col1, col2 = st.columns(2, gap="medium")
            with col1:
                name = st.text_input("Name")
                age = st.number_input("Age", 20, 70, 30)
                gender = st.selectbox("Gender", GENDER_OPTIONS)
                ethnicity = st.selectbox("Ethnicity", ETHNICITY_OPTIONS)
            with col2:
                counselor_language = st.multiselect("Language", LANGUAGE_OPTIONS, default=["Malay"], max_selections=2)
                specialization = st.selectbox("Specialization", SPECIALIZATION_OPTIONS, index=SPECIALIZATION_OPTIONS.index("Stress"))
                counselor_modality = st.multiselect("Modality", MODALITY_OPTIONS, default=["Cognitive"], max_selections=2)
                experience_years = st.number_input("Years of Experience", 0, 30, 3)
                availability = st.multiselect("Availability", TIME_BLOCK_OPTIONS, default=TIME_BLOCK_OPTIONS,
                                              help="General working times. Used to match clients by preferred time.")

        with tab2:
            profile_img = st.file_uploader("Profile Photo", type=["jpg", "jpeg", "png"])
            about_me = st.text_area("About Me", placeholder="I am a dedicated counseling professional...", height=80)
            modality_desc = st.text_area("Modality Description", placeholder="Describe what your counseling approach means in practice...", height=80)
            expertise_tags = st.text_input("Expertise Tags", placeholder="e.g., Anxiety, Overthinking, Self Growth")
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                helpful_thought_1 = st.text_input("Helpful Thought 1", placeholder="e.g., Am I doing enough?")
            with t_col2:
                helpful_thought_2 = st.text_input("Helpful Thought 2", placeholder="e.g., Why do I feel so alone?")

        submitted = st.form_submit_button("Save counselor", use_container_width=True, type="primary")

    if submitted:
        missing = []
        if not name.strip():                  missing.append("Name")
        if not counselor_language:            missing.append("Language")
        if not counselor_modality:            missing.append("Modality")
        if not about_me.strip():              missing.append("About Me")
        if not modality_desc.strip():         missing.append("Modality Description")
        if not expertise_tags.strip():        missing.append("Expertise Tags")
        if not helpful_thought_1.strip():     missing.append("Helpful Thought 1")
        if not helpful_thought_2.strip():     missing.append("Helpful Thought 2")
        if missing:
            st.error(f"Please fill in: {', '.join(missing)}")
        else:
            img_filename = _save_image(profile_img, name) if profile_img else None
            add_counselor({
                "name": name, "age": age, "gender": gender, "ethnicity": ethnicity,
                "specialization": specialization,
                "counselor_language": ", ".join(counselor_language),
                "counselor_modality": ", ".join(counselor_modality),
                "experience_years": experience_years,
                "availability": availability,
                "about_me": about_me, "expertise_tags": expertise_tags,
                "helpful_thought_1": helpful_thought_1, "helpful_thought_2": helpful_thought_2,
                "modality_desc": modality_desc, "image": img_filename,
            })
            get_counselors.clear()
            get_reference_data.clear()
            st.success("Counselor added successfully.")
            st.rerun()


@st.dialog("Edit counselor", width="large")
def render_edit_counselor_dialog():
    counselors = get_counselors()
    if not counselors:
        st.warning("No counselors found in database.")
        return

    counselors_df = pd.DataFrame(counselors)
    selected_id = st.selectbox(
        "Select counselor",
        counselors_df["counselor_id"].tolist(),
        format_func=lambda cid: f"ID {int(cid)} - {counselors_df.loc[counselors_df['counselor_id'] == cid, 'name'].iloc[0]}",
    )

    row = counselors_df.loc[counselors_df["counselor_id"] == selected_id].iloc[0]
    gender_index = _option_index(GENDER_OPTIONS, row.get("gender"))
    ethnicity_index = _option_index(ETHNICITY_OPTIONS, row.get("ethnicity"))
    specialization_index = _option_index(SPECIALIZATION_OPTIONS, row.get("specialization"))
    current_mods = [m.strip() for m in str(row.get("counselor_modality", "")).split(",") if m.strip() in MODALITY_OPTIONS]
    if not current_mods:
        current_mods = [MODALITY_OPTIONS[0]]

    with st.form("edit_counselor_dialog_form"):
        tab1, tab2 = st.tabs(["Basic Info", "Profile Details"])

        with tab1:
            edit_col1, edit_col2 = st.columns(2, gap="medium")
            with edit_col1:
                edit_name = st.text_input("Name", value=row["name"])
                edit_age = st.number_input("Age", 20, 70, int(row["age"]))
                edit_gender = st.selectbox("Gender", GENDER_OPTIONS, index=gender_index)
                edit_ethnicity = st.selectbox("Ethnicity", ETHNICITY_OPTIONS, index=ethnicity_index)
            with edit_col2:
                current_langs = [l.strip() for l in str(row.get("counselor_language", "")).split(",") if l.strip() in LANGUAGE_OPTIONS]
                if not current_langs:
                    current_langs = [LANGUAGE_OPTIONS[0]]
                edit_language = st.multiselect("Language", LANGUAGE_OPTIONS, default=current_langs, max_selections=2)
                edit_specialization = st.selectbox("Specialization", SPECIALIZATION_OPTIONS, index=specialization_index)
                edit_modality = st.multiselect("Modality", MODALITY_OPTIONS, default=current_mods, max_selections=2)
                edit_year_exp = st.number_input("Years of Experience", 0, 30, int(row["experience_years"]))
                current_avail = [b.strip() for b in str(row.get("availability") or "").split(",") if b.strip() in TIME_BLOCK_OPTIONS]
                edit_availability = st.multiselect("Availability", TIME_BLOCK_OPTIONS, default=current_avail,
                                                   help="General working times. Used to match clients by preferred time.")

        with tab2:
            current_img = safe_str(row.get("image"))
            if current_img:
                st.caption(f"Current photo: `{current_img}` — upload below to replace")
            edit_profile_img = st.file_uploader("Profile Photo", type=["jpg", "jpeg", "png"])
            edit_about_me = st.text_area("About Me", value=safe_str(row.get("about_me")), height=80)
            edit_modality_desc = st.text_area("Modality Description", value=safe_str(row.get("modality_desc")), height=80)
            edit_expertise_tags = st.text_input("Expertise Tags", value=safe_str(row.get("expertise_tags")))
            e_col1, e_col2 = st.columns(2)
            with e_col1:
                edit_thought_1 = st.text_input("Helpful Thought 1", value=safe_str(row.get("helpful_thought_1")))
            with e_col2:
                edit_thought_2 = st.text_input("Helpful Thought 2", value=safe_str(row.get("helpful_thought_2")))

        submitted = st.form_submit_button("Update counselor", use_container_width=True, type="primary")

    if submitted:
        missing = []
        if not edit_name.strip():             missing.append("Name")
        if not edit_language:                 missing.append("Language")
        if not edit_modality:                 missing.append("Modality")
        if not edit_about_me.strip():         missing.append("About Me")
        if not edit_modality_desc.strip():    missing.append("Modality Description")
        if not edit_expertise_tags.strip():   missing.append("Expertise Tags")
        if not edit_thought_1.strip():        missing.append("Helpful Thought 1")
        if not edit_thought_2.strip():        missing.append("Helpful Thought 2")
        if missing:
            st.error(f"Please fill in: {', '.join(missing)}")
        else:
            if edit_profile_img:
                img_filename = _save_image(edit_profile_img, edit_name)
            else:
                img_filename = safe_str(row.get("image")) or None
            update_counselor(int(selected_id), {
                "name": edit_name, "age": edit_age, "gender": edit_gender, "ethnicity": edit_ethnicity,
                "specialization": edit_specialization,
                "counselor_language": ", ".join(edit_language),
                "counselor_modality": ", ".join(edit_modality),
                "experience_years": edit_year_exp,
                "availability": edit_availability,
                "about_me": edit_about_me, "expertise_tags": edit_expertise_tags,
                "helpful_thought_1": edit_thought_1, "helpful_thought_2": edit_thought_2,
                "modality_desc": edit_modality_desc, "image": img_filename,
            })
            get_counselors.clear()
            get_reference_data.clear()
            st.success(f"Counselor {int(selected_id)} updated successfully.")
            st.rerun()


@st.dialog("Delete counselor")
def render_delete_counselor_dialog():
    counselors = get_counselors()
    if not counselors:
        st.warning("No counselors found in database.")
        return

    counselors_df = pd.DataFrame(counselors)
    selected_id = st.selectbox(
        "Select counselor to delete",
        counselors_df["counselor_id"].tolist(),
        format_func=lambda cid: f"ID {int(cid)} - {counselors_df.loc[counselors_df['counselor_id'] == cid, 'name'].iloc[0]}",
    )

    st.warning("This action cannot be undone.")
    confirm_delete = st.checkbox("I confirm this delete action")

    if st.button("Delete counselor", type="primary", use_container_width=True, disabled=not confirm_delete):
        delete_counselor(int(selected_id))
        get_counselors.clear()
        get_reference_data.clear()
        st.success(f"Counselor {int(selected_id)} deleted successfully.")
        st.rerun()


def show_manage_page():
    inject_styles()

    counselors = get_counselors()
    counselors_df = pd.DataFrame(counselors) if counselors else pd.DataFrame()

    st.markdown(
        """
        <div style="position: relative; overflow: hidden; background-color: #F5F3FF; background-image: radial-gradient(at 0% 0%, #F0E8FF 0px, transparent 55%), radial-gradient(at 100% 100%, #E8D5FD 0px, transparent 55%); border-radius: 20px; padding: 48px 48px; margin-bottom: 32px; border: 1px solid rgba(157,99,232,0.14); box-shadow: 0 16px 32px -8px rgba(157,99,232,0.1), inset 0 1px 0 rgba(255,255,255,0.9); display: flex; align-items: center; justify-content: space-between; width: 100%; min-height: 220px;">
            <div style="position: relative; z-index: 2; max-width: 65%;">
                <div style="color: #9D63E8; font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; background: rgba(157,99,232,0.1); border: 1px solid rgba(157,99,232,0.22); border-radius: 20px; padding: 4px 14px; margin-bottom: 20px; display: inline-block; font-family: 'Plus Jakarta Sans', sans-serif;">Directory</div>
                <div style="font-family: 'Fraunces', serif; font-size: 42px; color: #1C1917; margin-bottom: 16px; line-height: 1.1; letter-spacing: -0.5px; font-weight: 600;">Counselor Management</div>
                <p style="font-size: 16px; color: #6B6560; margin: 0; line-height: 1.65; max-width: 480px; font-family: 'Plus Jakarta Sans', sans-serif;">Review counselor records, add new entries, and update existing profiles in one place.</p>
            </div>
            <div style="font-size: 100px; line-height: 1; position: absolute; right: 20px; bottom: -15px; z-index: 1; opacity: 0.12; transform: rotate(-10deg); pointer-events: none;">
                🗂️
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
        with st.container(border=True):
            st.markdown('<div class="mg-action-label">Quick action</div>', unsafe_allow_html=True)
            if st.button("＋  Add counselor", use_container_width=True, type="primary"):
                render_add_counselor_dialog()

    with manage_col:
        with st.container(border=True):
            st.markdown('<div class="mg-action-label">Manage record</div>', unsafe_allow_html=True)
            edit_col, delete_col = st.columns(2, gap="small")
            with edit_col:
                if st.button("✎  Edit", use_container_width=True, disabled=counselors_df.empty):
                    render_edit_counselor_dialog()
            with delete_col:
                if st.button("✕  Delete", use_container_width=True, disabled=counselors_df.empty):
                    render_delete_counselor_dialog()

    st.markdown(
        """
        <hr style="margin: 32px 0 32px 0; border: none; border-top: 1px solid rgba(0,0,0,0.15);" />
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
        display_df = counselors_df.drop(columns=["about_me", "modality_desc", "helpful_thought_1", "helpful_thought_2"], errors="ignore")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
