import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from frontend.utils.api import get_requests, approve_request, send_approval_email


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
            st.success("Request approved!")
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


def render():
    st.markdown(
        """
        <div style="position: relative; overflow: hidden; background-color: #FAFAFF; background-image: radial-gradient(at 0% 0%, #E0F2FE 0px, transparent 60%), radial-gradient(at 100% 100%, #BAE6FD 0px, transparent 60%), radial-gradient(at 100% 0%, #FFFFFF 0px, transparent 50%); border-radius: 20px; padding: 48px 48px; margin-bottom: 32px; border: 1px solid rgba(14,165,233,0.15); box-shadow: 0 16px 32px -8px rgba(14,165,233,0.12), inset 0 1px 0 rgba(255,255,255,0.9); display: flex; align-items: center; justify-content: space-between; width: 100%; min-height: 236px;">
            <div style="position: relative; z-index: 2; max-width: 65%;">
                <div style="color: #0EA5E9; font-size: 11px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; background: rgba(14,165,233,0.12); border: 1px solid rgba(14,165,233,0.25); border-radius: 20px; padding: 4px 14px; margin-bottom: 20px; display: inline-block;">Approvals</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 42px; color: #1A1A2E; margin-bottom: 16px; line-height: 1.15; letter-spacing: -0.5px;">Review Requests</div>
                <p style="font-size: 16px; color: #4A4A5C; margin: 0; line-height: 1.65; max-width: 480px;">Review and manage client-counselor matching requests below.</p>
            </div>
            <div style="font-size: 100px; line-height: 1; position: absolute; right: 20px; bottom: -15px; z-index: 1; opacity: 0.15; transform: rotate(10deg); pointer-events: none;">
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
            <div style="background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%); border-radius: 16px; padding: 24px 28px; border: 1px solid rgba(249,115,22,0.2);">
                <div style="font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #F97316; margin-bottom: 12px;">New</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 40px; line-height: 1; color: #1A1A2E; margin-bottom: 6px;">{total_new}</div>
                <div style="font-size: 13px; color: #8B8B9A;">received in last 24h</div>
            </div>
            <div style="background: #FFFFFF; border-radius: 16px; padding: 24px 28px; border: 1px solid rgba(0,0,0,0.06);">
                <div style="font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #0EA5E9; margin-bottom: 12px;">Pending</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 40px; line-height: 1; color: #1A1A2E; margin-bottom: 6px;">{total_pending}</div>
                <div style="font-size: 13px; color: #8B8B9A;">awaiting your review</div>
            </div>
            <div style="background: #FFFFFF; border-radius: 16px; padding: 24px 28px; border: 1px solid rgba(0,0,0,0.06);">
                <div style="font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #10B981; margin-bottom: 12px;">Approved</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 40px; line-height: 1; color: #1A1A2E; margin-bottom: 6px;">{total_approved}</div>
                <div style="font-size: 13px; color: #8B8B9A;">successful matches</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr style='border: none; margin: 32px 0; border-bottom: 1px solid rgba(0,0,0,0.1);' />", unsafe_allow_html=True)

    if df_requests.empty:
        st.info("No requests found in the database.")
        return

    tab_pending, tab_approved = st.tabs(["Pending", "Approved"])

    df_pending = df_requests[df_requests["status"] == "Pending"]
    df_approved = df_requests[df_requests["status"] == "Approved"]

    with tab_pending:
        st.markdown("<h3 style='font-family: \"DM Serif Display\", serif; margin-top: 16px; margin-bottom: 8px; color: #1A1A2E;'>Pending Approvals</h3>", unsafe_allow_html=True)
        if df_pending.empty:
            st.markdown(
                """
                <div style="background: #FFFFFF; border: 1px dashed rgba(0,0,0,0.1); border-radius: 12px; padding: 48px 20px; text-align: center; margin-top: 16px;">
                    <div style="font-size: 36px; margin-bottom: 12px; opacity: 0.7;">⏳</div>
                    <div style="font-size: 16px; font-weight: 600; color: #1A1A2E; margin-bottom: 4px;">You're all caught up!</div>
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
                                <div style="font-size: 22px; font-weight: 600; color: #1A1A2E; margin-bottom: 12px;">{row['client_name']}{new_badge}</div>
                                <div style="font-size: 16px; color: #5A5A6E;">
                                    <div style="margin-bottom: 8px;">✉️ <strong style="color: #4A4A5C; margin-left: 4px;">Email:</strong> {row['client_email']}</div>
                                    <div style="margin-bottom: 8px;">🧑‍⚕️ <strong style="color: #4A4A5C; margin-left: 4px;">Requested Counselor:</strong> {row['counselor_name']}</div>
                                    <div style="margin-bottom: 4px;">🎯 <strong style="color: #4A4A5C; margin-left: 4px;">Match Score:</strong> <span style="background: rgba(16,185,129,0.15); color: #10B981; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 14px;">{score_str}</span></div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with col_actions:
                        if st.button("Approve", key=f"approve_{row['request_id']}", type="primary", use_container_width=True):
                            confirm_approve_dialog(row["request_id"], row["client_name"], row["client_email"], row["counselor_name"])

    with tab_approved:
        st.markdown("<h3 style='font-family: \"DM Serif Display\", serif; margin-top: 16px; margin-bottom: 8px; color: #10B981;'>Approved Requests</h3>", unsafe_allow_html=True)
        if df_approved.empty:
            st.markdown(
                """
                <div style="background: #FFFFFF; border: 1px dashed rgba(0,0,0,0.1); border-radius: 12px; padding: 48px 20px; text-align: center; margin-top: 16px;">
                    <div style="font-size: 36px; margin-bottom: 12px; opacity: 0.7;">✅</div>
                    <div style="font-size: 16px; font-weight: 600; color: #1A1A2E; margin-bottom: 4px;">No approved requests</div>
                    <div style="font-size: 14px; color: #8B8B9A;">Approved matches will appear in this history log.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            display_df = df_approved.drop(columns=["request_id"], errors="ignore")
            display_df = display_df.rename(columns={
                "client_name": "Client Name", "client_email": "Client Email",
                "counselor_name": "Counselor Name", "compatibility_score": "Match Score", "status": "Status",
            })
            st.dataframe(display_df, use_container_width=True, hide_index=True)
