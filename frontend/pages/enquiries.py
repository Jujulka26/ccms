import pandas as pd
import streamlit as st
from datetime import datetime

from frontend.utils.api import get_enquiries, update_enquiry_status


def render():
    st.markdown(
        """
        <div style="position: relative; overflow: hidden; background-color: #FFFBF5; background-image: radial-gradient(at 0% 0%, #FEF3C7 0px, transparent 60%), radial-gradient(at 100% 100%, #FDE68A 0px, transparent 60%); border-radius: 20px; padding: 48px 48px; margin-bottom: 32px; border: 1px solid rgba(245,158,11,0.2); box-shadow: 0 16px 32px -8px rgba(245,158,11,0.12), inset 0 1px 0 rgba(255,255,255,0.9); min-height: 200px;">
            <div style="position: relative; z-index: 2; max-width: 65%;">
                <div style="color: #D97706; font-size: 11px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.25); border-radius: 20px; padding: 4px 14px; margin-bottom: 20px; display: inline-block;">Inbox</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 42px; color: #1A1A2E; margin-bottom: 16px; line-height: 1.15; letter-spacing: -0.5px;">Enquiries</div>
                <p style="font-size: 16px; color: #4A4A5C; margin: 0; line-height: 1.65; max-width: 480px;">Messages submitted through the Contact Us form.</p>
            </div>
            <div style="font-size: 100px; line-height: 1; position: absolute; right: 24px; bottom: -18px; z-index: 1; opacity: 0.15; transform: rotate(-8deg); pointer-events: none;">✉️</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    enquiries = get_enquiries()
    df = pd.DataFrame(enquiries) if enquiries else pd.DataFrame()

    total = len(df)
    new_count = int((df["status"] == "New").sum()) if not df.empty else 0

    st.markdown(
        f"""
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 28px;">
            <div style="background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%); border-radius: 16px; padding: 24px 28px; border: 1px solid rgba(249,115,22,0.2);">
                <div style="font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #F97316; margin-bottom: 12px;">New</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 40px; line-height: 1; color: #1A1A2E;">{new_count}</div>
                <div style="font-size: 13px; color: #8B8B9A; margin-top: 6px;">awaiting a response</div>
            </div>
            <div style="background: #FFFFFF; border-radius: 16px; padding: 24px 28px; border: 1px solid rgba(0,0,0,0.06);">
                <div style="font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #8B5CF6; margin-bottom: 12px;">Total</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 40px; line-height: 1; color: #1A1A2E;">{total}</div>
                <div style="font-size: 13px; color: #8B8B9A; margin-top: 6px;">enquiries received</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("No enquiries yet. Submissions from the Contact Us page will appear here.")
        return

    for _, row in df.iterrows():
        is_new = row.get("status") == "New"
        created = row.get("created_at")
        when = created.strftime("%d %b %Y, %H:%M") if isinstance(created, datetime) else (str(created) if created else "")
        badge = (
            '<span style="background:#F97316;color:#fff;font-size:10px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:3px 10px;border-radius:20px;margin-left:10px;">New</span>'
            if is_new else
            '<span style="background:rgba(16,185,129,0.15);color:#10B981;font-size:10px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:3px 10px;border-radius:20px;margin-left:10px;">Handled</span>'
        )
        with st.container(border=True):
            col_msg, col_action = st.columns([4, 1], vertical_alignment="center")
            with col_msg:
                st.markdown(
                    f"""
                    <div style="padding: 0px 8px 8px 8px; margin-top: -8px;">
                        <div style="font-size: 18px; font-weight: 600; color: #1A1A2E; margin-bottom: 8px;">{row['subject'] or '(No subject)'}{badge}</div>
                        <div style="font-size: 14px; color: #5A5A6E; line-height: 1.7;">
                            <div>👤 <strong style="color:#4A4A5C;">{row['name']}</strong> &nbsp;·&nbsp; ✉️ {row['email']}</div>
                            <div style="margin-top: 8px; color: #4A4A5C;">{row['message']}</div>
                            <div style="margin-top: 8px; font-size: 12px; color: #9CA3AF;">{when}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_action:
                if is_new:
                    if st.button("Mark handled", key=f"handle_{row['enquiry_id']}", type="primary", use_container_width=True):
                        update_enquiry_status(row["enquiry_id"], "Handled")
                        get_enquiries.clear()
                        st.rerun()
                else:
                    if st.button("Reopen", key=f"reopen_{row['enquiry_id']}", use_container_width=True):
                        update_enquiry_status(row["enquiry_id"], "New")
                        get_enquiries.clear()
                        st.rerun()
