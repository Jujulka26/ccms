import time
import pandas as pd
import streamlit as st
from frontend.utils.api import (
    get_model_performance,
    trigger_retrain, get_retrain_status, get_model_history, deploy_version, discard_version,
)


def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

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
            font-family: 'Fraunces', serif;
            font-size: 36px;
            line-height: 1;
            color: #1C1917;
            margin-bottom: 6px;
            font-weight: 600;
        }
        .pm-stat-label {
            font-size: 13px;
            color: #9C9790;
            font-weight: 400;
            font-family: 'Plus Jakarta Sans', sans-serif;
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
            font-family: 'Fraunces', serif;
            font-size: 20px;
            color: #1C1917;
            margin: 0 0 4px;
            font-weight: 600;
        }
        .pm-card-copy {
            font-size: 14px;
            color: #6B6560;
            margin: 0;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        [data-testid="block-container"] div[data-testid="stTabs"] {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 4px 20px 24px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 1px 4px rgba(0,0,0,0.03);
            margin-bottom: 20px;
        }
        div[data-testid="stTabs"] button[role="tab"] {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            padding: 12px 18px !important;
            color: #9C9790 !important;
        }
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            font-weight: 700 !important;
            color: #1C1917 !important;
        }
        div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
            background-color: #C9636A !important;
            height: 3px !important;
            border-radius: 3px 3px 0 0 !important;
        }
        div[data-testid="stTabs"] [data-baseweb="tab-border"] {
            background-color: #F0ECE8 !important;
        }
        .pm-recommend {
            background: linear-gradient(135deg, rgba(201,99,106,0.06) 0%, #FFFFFF 100%);
            border: 1px solid rgba(201,99,106,0.22);
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
            color: #C9636A;
            background: rgba(201,99,106,0.1);
            border: 1px solid rgba(201,99,106,0.2);
            border-radius: 20px;
            padding: 4px 12px;
            margin-bottom: 14px;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .pm-recommend-title {
            font-family: 'Fraunces', serif;
            font-size: 22px;
            color: #1C1917;
            margin: 0 0 8px;
            font-weight: 600;
        }
        .pm-recommend-copy {
            font-size: 14px;
            color: #6B6560;
            line-height: 1.65;
            margin: 0;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .pm-note {
            background: rgba(245, 158, 11, 0.06);
            border-left: 3px solid #F59E0B;
            border-radius: 0 8px 8px 0;
            padding: 10px 16px;
            font-size: 13px;
            color: #6B6560;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_performance_metrics(data):
    model_count = data["model_count"]
    best_roc = data["best_roc_auc"] * 100
    deployed_model = data.get("deployed_model", "Tuned LightGBM")
    df = pd.DataFrame(data["models"])
    tuning_models = data.get("tuning_models", [])

    st.markdown(
        f"""
        <div class="pm-stat-grid">
            <div class="pm-stat-card">
                <div class="pm-stat-eyebrow" style="color:#C9636A;font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;">Models compared</div>
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
        '<div class="pm-note">Five baseline models were evaluated. '
        'LightGBM and CatBoost were selected for hyperparameter tuning. '
        'Tuned LightGBM was deployed based on best F1 and accuracy.</div>',
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["📊  Table", "📈  Chart"])
    with tabs[0]:
        st.dataframe(df, use_container_width=True, hide_index=True)
    with tabs[1]:
        df_plot = df.set_index("Model")[["Accuracy", "F1", "ROC-AUC"]] * 100
        st.line_chart(df_plot, use_container_width=True)

    if tuning_models:
        st.markdown('<hr style="margin: 32px 0 32px 0; border: none; border-top: 1px solid rgba(0,0,0,0.15);" />', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="pm-card">
                <div class="pm-card-title">Tuning comparison — LightGBM vs CatBoost</div>
                <p class="pm-card-copy">LightGBM and CatBoost were tuned with RandomizedSearchCV (50 iterations each). Tuned LightGBM is deployed as the active model.</p>
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

    st.markdown(
        f"""
        <div class="pm-recommend">
            <div class="pm-recommend-badge">&#10003; &nbsp;Deployed Model</div>
            <div class="pm-recommend-title">{deployed_model} is the active model</div>
            <p class="pm-recommend-copy">
                LightGBM and CatBoost were tuned with RandomizedSearchCV (50 iterations each).
                Tuned LightGBM is the active deployed model for client-counselor matching.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


_REQUIRED_COLUMNS = [
    "client_age", "client_ethnicity", "client_issue",
    "preferred_modality", "preferred_counselor_gender",
    "previous_counseling_experience",
    "counselor_age", "counselor_gender", "counselor_ethnicity",
    "counselor_modality", "specialization", "experience_years",
    "match_success",
]


def _template_csv_bytes() -> bytes:
    example = {
        "client_age": 29,
        "client_ethnicity": "Malay",
        "client_issue": "Anxiety",
        "preferred_modality": "Cognitive",
        "preferred_counselor_gender": "No preference",
        "previous_counseling_experience": 1,
        "counselor_age": 38,
        "counselor_gender": "Female",
        "counselor_ethnicity": "Malay",
        "counselor_modality": "Cognitive, Behavioral",
        "specialization": "Anxiety",
        "experience_years": 10,
        "match_success": 1,
    }
    return pd.DataFrame([example], columns=_REQUIRED_COLUMNS).to_csv(index=False).encode("utf-8")


def _render_model_management(data):
    st.markdown(
        """
        <div class="pm-card">
            <div class="pm-card-title">Train a new version</div>
            <p class="pm-card-copy">Upload a training dataset (CSV or Excel), then start training. Runs
            <strong>trainmodels.py → tunemodels.py</strong> on your data in the background — takes a few minutes.
            The active model is untouched until you choose to deploy the new version.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    retrain_result = st.session_state.get("retrain_result")

    # ── No active job, no result yet: upload dataset + start button ───────────
    if retrain_result is None:
        with st.expander("Required columns", expanded=False):
            st.markdown(
                "Your file must contain these columns (extra columns are ignored):\n\n"
                + "  ·  ".join(f"`{c}`" for c in _REQUIRED_COLUMNS)
            )
            st.download_button(
                "Download CSV template",
                data=_template_csv_bytes(),
                file_name="training_template.csv",
                mime="text/csv",
            )

        uploaded = st.file_uploader(
            "Upload training dataset",
            type=["csv", "xlsx", "xls"],
            help="The dataset the models will be trained on. Must contain the required columns above.",
        )

        st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

        if st.button("Start Training", type="primary", disabled=uploaded is None):
            result = trigger_retrain(uploaded.getvalue(), uploaded.name)
            if result:
                st.session_state["training_job_id"] = result["job_id"]
                st.rerun()

    # ── Training result panel ──────────────────────────────────────────────────
    else:
        version_id = retrain_result.get("version_id", "")
        old_m      = retrain_result.get("old_metrics", {})
        new_m      = retrain_result.get("new_metrics", {})
        rows       = retrain_result.get("rows", 0)
        rows_note  = f" Trained on <strong>{rows}</strong> rows." if rows else ""

        st.markdown(
            f'<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);'
            f'border-radius:12px;padding:16px 20px;margin-bottom:20px;">'
            f'<div style="font-size:12px;font-weight:600;color:#10B981;margin-bottom:6px;">TRAINING COMPLETE</div>'
            f'<div style="font-size:13px;color:#1C1917;">Version <code>{version_id}</code> is ready.{rows_note} '
            f'Save it to version history, or discard if the metrics are not good enough.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown("##### Metrics comparison")
        col_b, col_a = st.columns(2)
        with col_b:
            st.markdown("**Current active model**")
            if old_m:
                st.markdown(
                    f"Accuracy **{old_m.get('accuracy','—')}** &nbsp;·&nbsp; "
                    f"F1 **{old_m.get('f1','—')}** &nbsp;·&nbsp; "
                    f"ROC-AUC **{old_m.get('roc_auc','—')}**"
                )
            else:
                st.caption("No previous metrics on record.")
        with col_a:
            st.markdown("**New version**")
            if new_m:
                roc_delta = round(new_m.get("roc_auc", 0) - old_m.get("roc_auc", 0), 3) if old_m else 0
                sign      = "+" if roc_delta >= 0 else ""
                st.markdown(
                    f"Accuracy **{new_m.get('accuracy','—')}** &nbsp;·&nbsp; "
                    f"F1 **{new_m.get('f1','—')}** &nbsp;·&nbsp; "
                    f"ROC-AUC **{new_m.get('roc_auc','—')}** `{sign}{roc_delta}`"
                )
            else:
                st.caption("Could not read new metrics.")

        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        col_save, col_dis = st.columns(2)
        with col_save:
            if st.button("Save to history", type="primary", use_container_width=True):
                st.session_state.pop("retrain_result", None)
                st.rerun()
        with col_dis:
            if st.button("Discard", use_container_width=True):
                discard_version(version_id)
                st.session_state.pop("retrain_result", None)
                st.rerun()

        if retrain_result.get("output"):
            with st.expander("Pipeline output", expanded=False):
                st.code(retrain_result["output"], language="")

    # ── Model history ──────────────────────────────────────────────────────────
    st.markdown("<hr style='margin:32px 0 24px;border:none;border-top:1px solid rgba(0,0,0,0.08);'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="pm-card">
            <div class="pm-card-title">Version history</div>
            <p class="pm-card-copy">All trained versions are saved. Deploy any previous version to make it the active model.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hide the version that's currently pending review (not yet saved by the user)
    pending_vid = (retrain_result or {}).get("version_id")

    history = get_model_history()
    visible = [v for v in history if v.get("version_id") != pending_vid]
    if not visible:
        st.info("No saved versions yet. Train a new version above to start building history.")
    else:
        for v in visible:
            vid      = v.get("version_id", "")
            is_active = v.get("is_active", False)
            m        = v.get("metrics", {})
            rows     = v.get("rows", v.get("real_rows", 0))
            if v.get("mode") == "uploaded":
                mode_display = f"Uploaded · {rows} rows" if rows else "Uploaded"
            else:
                mode_display = "Synthetic"
            active_badge = (
                '<span style="background:#10B981;color:#fff;font-size:10px;font-weight:700;'
                'padding:2px 8px;border-radius:20px;margin-left:8px;">ACTIVE</span>'
                if is_active else ""
            )
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 3, 1], vertical_alignment="center")
                with c1:
                    st.markdown(
                        f'<div style="font-size:13px;font-weight:600;color:#1C1917;">'
                        f'{v.get("display_date", vid)}{active_badge}</div>'
                        f'<div style="font-size:12px;color:#8B8B9A;margin-top:2px;">{vid} · {mode_display}</div>',
                        unsafe_allow_html=True,
                    )
                with c2:
                    if m:
                        st.markdown(
                            f'<div style="font-size:13px;color:#6B6560;font-family:\'Plus Jakarta Sans\',sans-serif;">'
                            f'Acc <strong>{m.get("accuracy","—")}</strong> &nbsp;·&nbsp; '
                            f'F1 <strong>{m.get("f1","—")}</strong> &nbsp;·&nbsp; '
                            f'ROC-AUC <strong>{m.get("roc_auc","—")}</strong>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                with c3:
                    if not is_active:
                        if st.button("Deploy", key=f"deploy_{vid}", use_container_width=True, type="primary"):
                            with st.spinner(f"Deploying {vid}..."):
                                deploy_version(vid)
                            get_model_performance.clear()
                            st.success(f"{vid} deployed.")
                            st.rerun()
                    else:
                        st.markdown(
                            '<div style="text-align:center;font-size:12px;color:#10B981;font-weight:600;">Active</div>',
                            unsafe_allow_html=True,
                        )


def show_model_performance_page():
    inject_styles()

    st.markdown(
        """
        <div style="position: relative; overflow: hidden; background-color: #FFF9F7; background-image: radial-gradient(at 0% 0%, #FFEEE8 0px, transparent 60%), radial-gradient(at 100% 100%, #FFE4DC 0px, transparent 60%); border-radius: 20px; padding: 48px 48px; margin-bottom: 32px; border: 1px solid rgba(196,149,74,0.18); box-shadow: 0 16px 32px -8px rgba(196,149,74,0.1), inset 0 1px 0 rgba(255,255,255,0.9); min-height: 236px;">
            <div style="position: relative; z-index: 2; max-width: 65%;">
                <div style="color: #C4954A; font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; background: rgba(196,149,74,0.1); border: 1px solid rgba(196,149,74,0.22); border-radius: 20px; padding: 4px 14px; margin-bottom: 20px; display: inline-block; font-family: 'Plus Jakarta Sans', sans-serif;">Analytics</div>
                <div style="font-family: 'Fraunces', serif; font-size: 42px; font-weight: 600; color: #1C1917; margin-bottom: 16px; line-height: 1.15; letter-spacing: -0.5px;">Model Management</div>
                <p style="font-size: 16px; color: #6B6560; margin: 0; line-height: 1.65; max-width: 480px; font-family: 'Plus Jakarta Sans', sans-serif;">Accuracy, F1 and ROC-AUC across all models, plus model version management and retraining.</p>
            </div>
            <div style="font-size: 110px; line-height: 1; position: absolute; right: 28px; bottom: -20px; z-index: 1; opacity: 0.15; transform: rotate(-5deg); pointer-events: none;">
                📊
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Training progress lives at PAGE level — never inside a tab ────────────
    # st.empty() while-loop: only placeholders update, zero full-page blink.
    # Safe here because no tabs exist on this render path.
    job_id = st.session_state.get("training_job_id")
    if job_id:
        status_box = st.empty()
        prog_box   = st.empty()

        while True:
            status = get_retrain_status(job_id)

            if status is None:
                status_box.warning("Training job not found — the server may have restarted. Please start training again.")
                prog_box.empty()
                del st.session_state["training_job_id"]
                break

            state = status.get("status", "running")
            step  = status.get("step", "Working...")
            prog  = float(status.get("progress", 0.0))

            with status_box.container():
                st.markdown(
                    f'<div style="background:rgba(201,99,106,0.06);border:1px solid rgba(201,99,106,0.2);'
                    f'border-radius:12px;padding:16px 20px;margin-bottom:4px;">'
                    f'<div style="font-size:12px;font-weight:600;color:#C9636A;margin-bottom:6px;font-family:\'Plus Jakarta Sans\',sans-serif;letter-spacing:0.08em;">TRAINING IN PROGRESS</div>'
                    f'<div style="font-size:13px;color:#1C1917;font-family:\'Plus Jakarta Sans\',sans-serif;">{step}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            prog_box.progress(prog)

            if state == "running":
                time.sleep(3)
            elif state == "done":
                st.session_state["retrain_result"] = status["result"]
                del st.session_state["training_job_id"]
                status_box.empty()
                prog_box.empty()
                st.rerun()
                break
            elif state == "error":
                status_box.error(f"Training failed: {status.get('error', 'Unknown error')}")
                prog_box.empty()
                del st.session_state["training_job_id"]
                break

        return  # skip tabs entirely while training

    # ── Normal view: tabs ─────────────────────────────────────────────────────
    data = get_model_performance()

    tab_metrics, tab_management = st.tabs([
        "📊  Performance",
        "⚙️  Model Training",
    ])

    with tab_metrics:
        _render_performance_metrics(data)

    with tab_management:
        _render_model_management(data)
