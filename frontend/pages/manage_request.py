import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from frontend.utils.api import get_requests, get_counselors, approve_request, close_request, send_approval_email


_ICON_PATHS = {
    "mail":        '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "user-check":  '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><polyline points="16 11 18 13 22 9"/>',
    "target":      '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "tag":         '<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/>',
    "user":        '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "heart":       '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    "inbox":       '<polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>',
    "check-circle":'<path d="M21.801 10A10 10 0 1 1 17 3.335"/><path d="m9 11 3 3L22 4"/>',
    "archive":     '<rect width="20" height="5" x="2" y="3" rx="1"/><path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8"/><path d="M10 12h4"/>',
    "clipboard":   '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>',
}


def _icon(name, color="#9D63E8", size=15, stroke=2):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
        f'style="flex-shrink:0;">{_ICON_PATHS[name]}</svg>'
    )


def _row(icon_name, label, value_html, color="#9D63E8"):
    return (
        '<div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">'
        '<div style="display:flex; align-items:center; gap:8px; min-width:165px; flex-shrink:0;'
        ' font-size:13px; color:#8A857E; font-weight:600;">'
        f'{_icon(icon_name, color)}<span>{label}</span></div>'
        f'<div style="font-size:14px; color:#1C1917;">{value_html}</div>'
        '</div>'
    )


def _client_context_html(row) -> str:
    """Compact summary of the client's questionnaire answers, shown so the
    coordinator can sanity-check the match before approving."""
    rows_html = ""
    if row.get("client_issue"):
        rows_html += _row("tag", "Issue", row["client_issue"])
    demo = " / ".join(
        str(x) for x in [row.get("client_age"), row.get("client_gender"), row.get("client_ethnicity")]
        if x not in (None, "")
    )
    if demo:
        rows_html += _row("user", "Client", demo)
    prefs = []
    if row.get("preferred_modality"):  prefs.append(str(row["preferred_modality"]))
    if row.get("preferred_language"):  prefs.append(str(row["preferred_language"]))
    if row.get("preferred_c_gender"):  prefs.append(f"{row['preferred_c_gender']} counselor")
    if row.get("prev_exp") is not None:
        prefs.append("has prior counseling" if row.get("prev_exp") else "first time")
    if prefs:
        rows_html += _row("heart", "Prefers", ", ".join(prefs))
    if not rows_html:
        return ""
    return (
        '<div style="margin-top:14px; padding-top:14px; border-top:1px dashed rgba(0,0,0,0.10);">'
        + rows_html + "</div>"
    )


@st.dialog("Confirm Approval")
def confirm_approve_dialog(request_id, client_name, client_email, counselor_name):
    st.write(f"Are you sure you want to approve the request for **{client_name}** to match with **{counselor_name}**?")
    st.write("An approval email will be sent to the client.")
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Approve", type="primary", use_container_width=True):
            approve_request(request_id)
            send_approval_email(request_id, client_name, client_email, counselor_name)
            get_requests.clear()
            get_counselors.clear()  # caseload changed → refresh directory + matching
            st.success("Request approved!")
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


def render():
    st.markdown(
        """
        <style>
        /* Approve button: solid navy, matching the Counselor Management buttons */
        [class*="st-key-approve_"] button {
            background: #2E1065 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(14,24,35,0.25) !important;
            transition: all 0.2s ease !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        [class*="st-key-approve_"] button:hover {
            background: #9D63E8 !important;
            box-shadow: 0 6px 18px rgba(157,99,232,0.35) !important;
            transform: translateY(-1px) !important;
        }
        </style>
        <div style="position: relative; overflow: hidden; background-color: #F5F3FF; background-image: radial-gradient(at 0% 0%, #F0E8FF 0px, transparent 60%), radial-gradient(at 100% 100%, #E8D5FD 0px, transparent 60%); border-radius: 20px; padding: 48px 48px; margin-bottom: 32px; border: 1px solid rgba(157,99,232,0.15); box-shadow: 0 16px 32px -8px rgba(157,99,232,0.1), inset 0 1px 0 rgba(255,255,255,0.9); display: flex; align-items: center; justify-content: space-between; width: 100%; min-height: 220px;">
            <div style="position: relative; z-index: 2; max-width: 65%;">
                <div style="color: #9D63E8; font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; background: rgba(157,99,232,0.1); border: 1px solid rgba(157,99,232,0.22); border-radius: 20px; padding: 4px 14px; margin-bottom: 20px; display: inline-block; font-family: 'Plus Jakarta Sans', sans-serif;">Approvals</div>
                <div style="font-family: 'Fraunces', serif; font-size: 42px; color: #1C1917; margin-bottom: 16px; line-height: 1.1; letter-spacing: -0.5px; font-weight: 500;">Review Requests</div>
                <p style="font-size: 16px; color: #6B6560; margin: 0; line-height: 1.65; max-width: 480px; font-family: 'Plus Jakarta Sans', sans-serif;">Review and manage client-counselor matching requests below.</p>
            </div>
            <div style="position: absolute; right: 36px; bottom: 24px; z-index: 1; opacity: 0.12; transform: rotate(8deg); pointer-events: none;">
                <svg width="118" height="118" viewBox="0 0 24 24" fill="none" stroke="#9D63E8" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
                    <rect width="8" height="4" x="8" y="2" rx="1" ry="1"/>
                    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
                    <path d="M9 12h6"/><path d="M9 16h4"/>
                </svg>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    requests_data = get_requests()
    df_requests = pd.DataFrame(requests_data) if requests_data else pd.DataFrame()

    cutoff = datetime.now() - timedelta(hours=24)

    def is_new(created_at):
        if created_at is None:
            return False
        dt = created_at if isinstance(created_at, datetime) else datetime.fromisoformat(str(created_at))
        return dt.replace(tzinfo=None) >= cutoff

    total_pending = len(df_requests[df_requests["status"] == "Pending"]) if not df_requests.empty else 0
    total_approved = len(df_requests[df_requests["status"] == "Approved"]) if not df_requests.empty else 0
    total_new = (
        sum(is_new(row["created_at"]) for _, row in df_requests[df_requests["status"] == "Pending"].iterrows())
        if not df_requests.empty and "created_at" in df_requests.columns
        else 0
    )

    st.markdown(
        f"""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 32px;">
            <div style="background: linear-gradient(135deg, #F5F3FF 0%, #F0E8FF 100%); border-radius: 16px; padding: 24px 28px; border: 1px solid rgba(157,99,232,0.2);">
                <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #9D63E8; margin-bottom: 12px; font-family: 'Plus Jakarta Sans', sans-serif;">New</div>
                <div style="font-family: 'Fraunces', serif; font-size: 40px; line-height: 1; color: #1C1917; margin-bottom: 6px; font-weight: 600;">{total_new}</div>
                <div style="font-size: 13px; color: #9C9790; font-family: 'Plus Jakarta Sans', sans-serif;">received in last 24h</div>
            </div>
            <div style="background: #FFFFFF; border-radius: 16px; padding: 24px 28px; border: 1px solid rgba(0,0,0,0.06);">
                <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #9D63E8; margin-bottom: 12px; font-family: 'Plus Jakarta Sans', sans-serif;">Pending</div>
                <div style="font-family: 'Fraunces', serif; font-size: 40px; line-height: 1; color: #1C1917; margin-bottom: 6px; font-weight: 600;">{total_pending}</div>
                <div style="font-size: 13px; color: #9C9790; font-family: 'Plus Jakarta Sans', sans-serif;">awaiting your review</div>
            </div>
            <div style="background: #FFFFFF; border-radius: 16px; padding: 24px 28px; border: 1px solid rgba(0,0,0,0.06);">
                <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #4A8C6A; margin-bottom: 12px; font-family: 'Plus Jakarta Sans', sans-serif;">Approved</div>
                <div style="font-family: 'Fraunces', serif; font-size: 40px; line-height: 1; color: #1C1917; margin-bottom: 6px; font-weight: 600;">{total_approved}</div>
                <div style="font-size: 13px; color: #9C9790; font-family: 'Plus Jakarta Sans', sans-serif;">matched clients</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr style='border: none; margin: 32px 0; border-bottom: 1px solid rgba(0,0,0,0.1);' />", unsafe_allow_html=True)

    if df_requests.empty:
        st.info("No requests found in the database.")
        return

    tab_pending, tab_approved, tab_closed = st.tabs(["Pending", "Approved", "Closed"])

    df_pending  = df_requests[df_requests["status"] == "Pending"]
    df_approved = df_requests[df_requests["status"] == "Approved"]
    df_closed   = df_requests[df_requests["status"] == "Closed"]

    with tab_pending:
        st.markdown("<h3 style='font-family: \"Fraunces\", serif; margin-top: 16px; margin-bottom: 8px; color: #1C1917; font-weight: 600;'>Pending Approvals</h3>", unsafe_allow_html=True)
        if df_pending.empty:
            empty_icon = _icon("inbox", "#C0B8AE", 38, 1.5)
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px dashed rgba(0,0,0,0.1); border-radius: 12px; padding: 48px 20px; text-align: center; margin-top: 16px;">
                    <div style="display:flex; justify-content:center; margin-bottom: 14px;">{empty_icon}</div>
                    <div style="font-size: 16px; font-weight: 600; color: #1C1917; margin-bottom: 4px;">You're all caught up!</div>
                    <div style="font-size: 14px; color: #8B8B9A;">There are no pending requests waiting for your approval at this time.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for _, row in df_pending.iterrows():
                with st.container(border=True):
                    col_info, col_actions = st.columns([3, 1], vertical_alignment="center")
                    with col_info:
                        score_str = f"{row['compatibility_score']:.2f}%" if pd.notnull(row.get("compatibility_score")) else "N/A"
                        new_badge = '<span style="background: #F97316; color: #FFFFFF; font-size: 10px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; padding: 3px 10px; border-radius: 20px; margin-left: 10px; vertical-align: middle;">New</span>' if is_new(row.get("created_at")) else ""
                        score_badge = f'<span style="background: rgba(5,150,105,0.12); color: #059669; padding: 3px 11px; border-radius: 20px; font-weight: 700; font-size: 13px;">{score_str}</span>'
                        info_html = (
                            _row("mail", "Email", row["client_email"])
                            + _row("user-check", "Requested Counselor", row["counselor_name"])
                            + _row("target", "Match Score", score_badge)
                            + _client_context_html(row)
                        )
                        st.markdown(
                            f"""
                            <div style="padding: 0px 8px 8px 8px; margin-top: -8px;">
                                <div style="font-size: 22px; font-weight: 600; color: #1C1917; margin-bottom: 16px;">{row['client_name']}{new_badge}</div>
                                {info_html}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with col_actions:
                        if st.button("Approve", key=f"approve_{row['request_id']}", type="primary", use_container_width=True):
                            confirm_approve_dialog(row["request_id"], row["client_name"], row["client_email"], row["counselor_name"])

    with tab_approved:
        st.markdown("<h3 style='font-family: \"Fraunces\", serif; margin-top: 16px; margin-bottom: 8px; color: #4A8C6A; font-weight: 600;'>Approved Requests</h3>", unsafe_allow_html=True)
        if df_approved.empty:
            empty_icon = _icon("check-circle", "#C0B8AE", 38, 1.5)
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px dashed rgba(0,0,0,0.1); border-radius: 12px; padding: 48px 20px; text-align: center; margin-top: 16px;">
                    <div style="display:flex; justify-content:center; margin-bottom: 14px;">{empty_icon}</div>
                    <div style="font-size: 16px; font-weight: 600; color: #1C1917; margin-bottom: 4px;">No active approved matches</div>
                    <div style="font-size: 14px; color: #8B8B9A;">Approved matches awaiting an outcome will appear here.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for _, row in df_approved.iterrows():
                with st.container(border=True):
                    col_info, col_action = st.columns([3, 1], vertical_alignment="center")
                    with col_info:
                        score_str = f"{row['compatibility_score']:.2f}%" if pd.notnull(row.get("compatibility_score")) else "N/A"
                        score_badge = f'<span style="background: rgba(5,150,105,0.12); color: #059669; padding: 3px 11px; border-radius: 20px; font-weight: 700; font-size: 13px;">{score_str}</span>'
                        info_html = (
                            _row("mail", "Email", row["client_email"])
                            + _row("user-check", "Counselor", row["counselor_name"])
                            + _row("target", "Match Score", score_badge)
                            + _client_context_html(row)
                        )
                        st.markdown(
                            f"""
                            <div style="padding: 0px 8px 8px 8px; margin-top: -8px;">
                                <div style="font-size: 20px; font-weight: 600; color: #1C1917; margin-bottom: 14px;">{row['client_name']}</div>
                                {info_html}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with col_action:
                        if st.button("✓ Close case", key=f"close_{row['request_id']}", use_container_width=True,
                                     help="Mark this engagement as finished. Frees one slot in the counselor's caseload."):
                            close_request(row["request_id"])
                            get_requests.clear()
                            get_counselors.clear()  # caseload changed → refresh directory + matching
                            st.rerun()

    with tab_closed:
        st.markdown("<h3 style='font-family: \"Fraunces\", serif; margin-top: 16px; margin-bottom: 8px; color: #6B6560; font-weight: 600;'>Closed Matches</h3>", unsafe_allow_html=True)
        if df_closed.empty:
            empty_icon = _icon("archive", "#C0B8AE", 38, 1.5)
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px dashed rgba(0,0,0,0.1); border-radius: 12px; padding: 48px 20px; text-align: center; margin-top: 16px;">
                    <div style="display:flex; justify-content:center; margin-bottom: 14px;">{empty_icon}</div>
                    <div style="font-size: 16px; font-weight: 600; color: #1C1917; margin-bottom: 4px;">No closed matches yet</div>
                    <div style="font-size: 14px; color: #8B8B9A;">Matches you close will be archived here.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for _, row in df_closed.iterrows():
                score_str = f"{row['compatibility_score']:.2f}%" if pd.notnull(row.get("compatibility_score")) else "N/A"
                score_badge = f'<span style="background: rgba(5,150,105,0.12); color: #059669; padding: 3px 11px; border-radius: 20px; font-weight: 700; font-size: 13px;">{score_str}</span>'
                info_html = (
                    _row("mail", "Email", row["client_email"])
                    + _row("user-check", "Counselor", row["counselor_name"])
                    + _row("target", "Match Score", score_badge)
                )
                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style="padding: 0px 8px 8px 8px; margin-top: -8px; opacity: 0.85;">
                            <div style="font-size: 20px; font-weight: 600; color: #1C1917; margin-bottom: 14px;">{row['client_name']}
                                <span style="background: rgba(107,101,96,0.1); color: #6B6560; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; padding: 3px 10px; border-radius: 20px; margin-left: 8px; vertical-align: middle;">Closed</span>
                            </div>
                            {info_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
