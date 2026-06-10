import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from frontend.utils.api import get_requests, get_counselors, approve_request, close_request, send_approval_email


def _client_context_html(row) -> str:
    """Compact summary of the client's questionnaire answers, shown so the
    coordinator can sanity-check the match before approving."""
    parts = []
    if row.get("client_issue"):
        parts.append(f"🧩 <strong style='color:#6B6560;'>Issue:</strong> {row['client_issue']}")
    demo = " / ".join(
        str(x) for x in [row.get("client_age"), row.get("client_gender"), row.get("client_ethnicity")]
        if x not in (None, "")
    )
    if demo:
        parts.append(f"👤 {demo}")
    prefs = []
    if row.get("preferred_modality"):  prefs.append(str(row["preferred_modality"]))
    if row.get("preferred_language"):  prefs.append(str(row["preferred_language"]))
    if row.get("preferred_c_gender"):  prefs.append(f"{row['preferred_c_gender']} counselor")
    if row.get("prev_exp") is not None:
        prefs.append("has prior counseling" if row.get("prev_exp") else "first time")
    if prefs:
        parts.append("💡 <strong style='color:#6B6560;'>Prefers:</strong> " + ", ".join(prefs))
    if not parts:
        return ""
    return (
        '<div style="margin-top:10px;padding-top:10px;border-top:1px dashed rgba(0,0,0,0.08);'
        'font-size:13px;color:#6B6B80;line-height:1.8;">' + "<br>".join(parts) + "</div>"
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
        </style>
        <div style="position: relative; overflow: hidden; background-color: #F5F3FF; background-image: radial-gradient(at 0% 0%, #F0E8FF 0px, transparent 60%), radial-gradient(at 100% 100%, #E8D5FD 0px, transparent 60%); border-radius: 20px; padding: 48px 48px; margin-bottom: 32px; border: 1px solid rgba(181,136,247,0.15); box-shadow: 0 16px 32px -8px rgba(181,136,247,0.1), inset 0 1px 0 rgba(255,255,255,0.9); display: flex; align-items: center; justify-content: space-between; width: 100%; min-height: 220px;">
            <div style="position: relative; z-index: 2; max-width: 65%;">
                <div style="color: #B588F7; font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; background: rgba(181,136,247,0.1); border: 1px solid rgba(181,136,247,0.22); border-radius: 20px; padding: 4px 14px; margin-bottom: 20px; display: inline-block; font-family: 'Plus Jakarta Sans', sans-serif;">Approvals</div>
                <div style="font-family: 'Fraunces', serif; font-size: 42px; color: #1C1917; margin-bottom: 16px; line-height: 1.1; letter-spacing: -0.5px; font-weight: 600;">Review Requests</div>
                <p style="font-size: 16px; color: #6B6560; margin: 0; line-height: 1.65; max-width: 480px; font-family: 'Plus Jakarta Sans', sans-serif;">Review and manage client-counselor matching requests below.</p>
            </div>
            <div style="font-size: 100px; line-height: 1; position: absolute; right: 20px; bottom: -15px; z-index: 1; opacity: 0.12; transform: rotate(10deg); pointer-events: none;">
                📝
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
            <div style="background: linear-gradient(135deg, #F5F3FF 0%, #F0E8FF 100%); border-radius: 16px; padding: 24px 28px; border: 1px solid rgba(181,136,247,0.2);">
                <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #B588F7; margin-bottom: 12px; font-family: 'Plus Jakarta Sans', sans-serif;">New</div>
                <div style="font-family: 'Fraunces', serif; font-size: 40px; line-height: 1; color: #1C1917; margin-bottom: 6px; font-weight: 600;">{total_new}</div>
                <div style="font-size: 13px; color: #9C9790; font-family: 'Plus Jakarta Sans', sans-serif;">received in last 24h</div>
            </div>
            <div style="background: #FFFFFF; border-radius: 16px; padding: 24px 28px; border: 1px solid rgba(0,0,0,0.06);">
                <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #B588F7; margin-bottom: 12px; font-family: 'Plus Jakarta Sans', sans-serif;">Pending</div>
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
            st.markdown(
                """
                <div style="background: #FFFFFF; border: 1px dashed rgba(0,0,0,0.1); border-radius: 12px; padding: 48px 20px; text-align: center; margin-top: 16px;">
                    <div style="font-size: 36px; margin-bottom: 12px; opacity: 0.7;">⏳</div>
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
                        st.markdown(
                            f"""
                            <div style="padding: 0px 8px 8px 8px; margin-top: -8px;">
                                <div style="font-size: 22px; font-weight: 600; color: #1C1917; margin-bottom: 12px;">{row['client_name']}{new_badge}</div>
                                <div style="font-size: 16px; color: #6B6560;">
                                    <div style="margin-bottom: 8px;">✉️ <strong style="color: #6B6560; margin-left: 4px;">Email:</strong> {row['client_email']}</div>
                                    <div style="margin-bottom: 8px;">🧑‍⚕️ <strong style="color: #6B6560; margin-left: 4px;">Requested Counselor:</strong> {row['counselor_name']}</div>
                                    <div style="margin-bottom: 4px;">🎯 <strong style="color: #6B6560; margin-left: 4px;">Match Score:</strong> <span style="background: rgba(16,185,129,0.15); color: #10B981; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 14px;">{score_str}</span></div>
                                </div>
                                {_client_context_html(row)}
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
            st.markdown(
                """
                <div style="background: #FFFFFF; border: 1px dashed rgba(0,0,0,0.1); border-radius: 12px; padding: 48px 20px; text-align: center; margin-top: 16px;">
                    <div style="font-size: 36px; margin-bottom: 12px; opacity: 0.7;">✅</div>
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
                        st.markdown(
                            f"""
                            <div style="padding: 0px 8px 8px 8px; margin-top: -8px;">
                                <div style="font-size: 20px; font-weight: 600; color: #1C1917; margin-bottom: 10px;">{row['client_name']}</div>
                                <div style="font-size: 15px; color: #6B6560;">
                                    <div style="margin-bottom: 6px;">✉️ <strong style="color: #6B6560; margin-left: 4px;">Email:</strong> {row['client_email']}</div>
                                    <div style="margin-bottom: 6px;">🧑‍⚕️ <strong style="color: #6B6560; margin-left: 4px;">Counselor:</strong> {row['counselor_name']}</div>
                                    <div>🎯 <strong style="color: #6B6560; margin-left: 4px;">Match Score:</strong> <span style="background: rgba(16,185,129,0.15); color: #10B981; padding: 3px 10px; border-radius: 12px; font-weight: 600; font-size: 13px;">{score_str}</span></div>
                                </div>
                                {_client_context_html(row)}
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
            st.markdown(
                """
                <div style="background: #FFFFFF; border: 1px dashed rgba(0,0,0,0.1); border-radius: 12px; padding: 48px 20px; text-align: center; margin-top: 16px;">
                    <div style="font-size: 36px; margin-bottom: 12px; opacity: 0.7;">🗂️</div>
                    <div style="font-size: 16px; font-weight: 600; color: #1C1917; margin-bottom: 4px;">No closed matches yet</div>
                    <div style="font-size: 14px; color: #8B8B9A;">Matches you close will be archived here.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for _, row in df_closed.iterrows():
                score_str = f"{row['compatibility_score']:.2f}%" if pd.notnull(row.get("compatibility_score")) else "N/A"
                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style="padding: 0px 8px 8px 8px; margin-top: -8px; opacity: 0.85;">
                            <div style="font-size: 20px; font-weight: 600; color: #1C1917; margin-bottom: 10px;">{row['client_name']}
                                <span style="background: rgba(107,101,96,0.1); color: #6B6560; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; padding: 3px 10px; border-radius: 20px; margin-left: 8px; vertical-align: middle;">Closed</span>
                            </div>
                            <div style="font-size: 15px; color: #6B6560;">
                                <div style="margin-bottom: 6px;">✉️ <strong style="color: #6B6560; margin-left: 4px;">Email:</strong> {row['client_email']}</div>
                                <div style="margin-bottom: 6px;">🧑‍⚕️ <strong style="color: #6B6560; margin-left: 4px;">Counselor:</strong> {row['counselor_name']}</div>
                                <div>🎯 <strong style="color: #6B6560; margin-left: 4px;">Match Score:</strong> <span style="background: rgba(16,185,129,0.15); color: #10B981; padding: 3px 10px; border-radius: 12px; font-weight: 600; font-size: 13px;">{score_str}</span></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
