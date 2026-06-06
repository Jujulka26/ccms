import time
import pandas as pd
import streamlit as st
from frontend.utils.api import (
    get_model_performance, get_consented_outcomes,
    trigger_retrain, get_retrain_status, get_model_history, deploy_version, discard_version,
)


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


def _render_outcome_data():
    st.markdown(
        """
        <div class="pm-card">
            <div class="pm-card-title">Export outcome data</div>
            <p class="pm-card-copy">Downloads client + counselor features with finalised outcome labels (Successful / Unsuccessful only). Ongoing matches are excluded — they have no definitive label yet. No personal identifiers included.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    rows = get_consented_outcomes()
    if rows:
        df_export = pd.DataFrame(rows)
        csv_bytes = df_export.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download outcomes CSV",
            data=csv_bytes,
            file_name="match_outcomes.csv",
            mime="text/csv",
            type="primary",
        )
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        st.dataframe(df_export, use_container_width=True, hide_index=True)
    else:
        st.info("No finalised outcomes yet. Outcomes appear here once consented users are marked Successful or Unsuccessful.")


def _render_model_management(data):
    deployed_model = data.get("deployed_model", "Tuned LightGBM")

    st.markdown(
        """
        <div class="pm-card">
            <div class="pm-card-title">Train a new version</div>
            <p class="pm-card-copy">Runs <strong>datascript.py → trainmodels.py → tunemodels.py</strong>. Takes several minutes. The active model is untouched until you choose to deploy.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    retrain_result = st.session_state.get("retrain_result")

    # ── No active job, no result yet: show uploader + start button ─────────────
    if retrain_result is None:
        uploaded = st.file_uploader(
            "Upload real outcomes CSV (optional)",
            type="csv",
            help="Upload the CSV exported from the Outcome Data tab to include real match data in training. Leave empty to train on synthetic data only.",
        )

        real_data = []
        if uploaded is not None:
            try:
                df_upload = pd.read_csv(uploaded)
                real_data = df_upload.to_dict(orient="records")
                st.markdown(
                    f'<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);'
                    f'border-radius:10px;padding:10px 14px;margin-top:8px;font-size:13px;color:#065F46;">'
                    f'<strong>{len(real_data)}</strong> real outcome row{"s" if len(real_data) != 1 else ""} loaded — '
                    f'will be appended to synthetic data before training.</div>',
                    unsafe_allow_html=True,
                )
            except Exception:
                st.warning("Could not read the uploaded CSV. Training will use synthetic data only.")

        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

        if st.button("Start Training", type="primary"):
            result = trigger_retrain(real_data if real_data else None)
            if result:
                st.session_state["training_job_id"] = result["job_id"]
                st.rerun()

    # ── Training result panel ──────────────────────────────────────────────────
    else:
        version_id  = retrain_result.get("version_id", "")
        result_mode = retrain_result.get("mode", "synthetic")
        result_real = retrain_result.get("real_rows", 0)
        old_m       = retrain_result.get("old_metrics", {})
        new_m       = retrain_result.get("new_metrics", {})

        mode_label = f"Hybrid · {result_real} real rows" if result_mode == "hybrid" and result_real else "Synthetic"
        st.markdown(
            f'<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);'
            f'border-radius:12px;padding:16px 20px;margin-bottom:20px;">'
            f'<div style="font-size:12px;font-weight:600;color:#10B981;margin-bottom:6px;">TRAINING COMPLETE — {mode_label}</div>'
            f'<div style="font-size:13px;color:#1A1A2E;">Version <code>{version_id}</code> is ready. '
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
            mode_tag = "Hybrid" if v.get("mode") == "hybrid" else "Synthetic"
            rr       = v.get("real_rows", 0)
            mode_display = f"Hybrid · {rr} real rows" if mode_tag == "Hybrid" and rr else mode_tag
            active_badge = (
                '<span style="background:#10B981;color:#fff;font-size:10px;font-weight:700;'
                'padding:2px 8px;border-radius:20px;margin-left:8px;">ACTIVE</span>'
                if is_active else ""
            )
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 3, 1], vertical_alignment="center")
                with c1:
                    st.markdown(
                        f'<div style="font-size:13px;font-weight:600;color:#1A1A2E;">'
                        f'{v.get("display_date", vid)}{active_badge}</div>'
                        f'<div style="font-size:12px;color:#8B8B9A;margin-top:2px;">{vid} · {mode_display}</div>',
                        unsafe_allow_html=True,
                    )
                with c2:
                    if m:
                        st.markdown(
                            f'<div style="font-size:13px;color:#4A4A5C;">'
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
        <div style="position: relative; overflow: hidden; background-color: #FAFDFC; background-image: radial-gradient(at 0% 0%, #D1FAE5 0px, transparent 60%), radial-gradient(at 100% 100%, #ECFDF5 0px, transparent 60%); border-radius: 20px; padding: 48px 48px; margin-bottom: 32px; border: 1px solid rgba(16,185,129,0.2); box-shadow: 0 16px 32px -8px rgba(16,185,129,0.12), inset 0 1px 0 rgba(255,255,255,0.9); min-height: 236px;">
            <div style="position: relative; z-index: 2; max-width: 65%;">
                <div style="color: #10B981; font-size: 11px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.25); border-radius: 20px; padding: 4px 14px; margin-bottom: 20px; display: inline-block;">Analytics</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 42px; color: #1A1A2E; margin-bottom: 16px; line-height: 1.15; letter-spacing: -0.5px;">Model Management</div>
                <p style="font-size: 16px; color: #4A4A5C; margin: 0; line-height: 1.65; max-width: 480px;">Accuracy, F1 and ROC-AUC across all models — plus outcome data and model management.</p>
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
                    f'<div style="background:rgba(139,92,246,0.06);border:1px solid rgba(139,92,246,0.2);'
                    f'border-radius:12px;padding:16px 20px;margin-bottom:4px;">'
                    f'<div style="font-size:12px;font-weight:600;color:#8B5CF6;margin-bottom:6px;">TRAINING IN PROGRESS</div>'
                    f'<div style="font-size:13px;color:#1A1A2E;">{step}</div>'
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

    tab_metrics, tab_outcomes, tab_management = st.tabs([
        "📊  Performance",
        "📋  Outcome Data",
        "⚙️  Model Training",
    ])

    with tab_metrics:
        _render_performance_metrics(data)

    with tab_outcomes:
        _render_outcome_data()

    with tab_management:
        _render_model_management(data)
