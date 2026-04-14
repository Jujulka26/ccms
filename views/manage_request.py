import streamlit as st
import pandas as pd
from utils.db import get_all_requests, update_request_status

def send_approval_email(name, email, counselor):
    """Placeholder function for sending an approval email"""
    # In a real application, this would integrate with an SMTP server or email API
    pass

@st.dialog("Confirm Approval")
def confirm_approve_dialog(request_id, client_name, client_email, counselor_name):
    st.write(f"Are you sure you want to approve the request for **{client_name}** to match with **{counselor_name}**?")
    st.write("An approval email will be sent to the client.")
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Approve", type="primary", use_container_width=True):
            update_request_status(request_id, 'Approved')
            send_approval_email(client_name, client_email, counselor_name)
            st.success("Request approved!")
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

@st.dialog("Confirm Rejection")
def confirm_reject_dialog(request_id, client_name):
    st.write(f"Are you sure you want to reject the request for **{client_name}**?")
    st.warning("This action cannot be undone.")
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Reject", type="primary", use_container_width=True):
            update_request_status(request_id, 'Rejected')
            st.success("Request rejected.")
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

def render():
    st.markdown(
        """
        <div style="position: relative; overflow: hidden; background-color: #FAFAFF; background-image: radial-gradient(at 0% 0%, #E0F2FE 0px, transparent 60%), radial-gradient(at 100% 100%, #BAE6FD 0px, transparent 60%), radial-gradient(at 100% 0%, #FFFFFF 0px, transparent 50%), url('data:image/svg+xml,%3Csvg width=\\'20\\' height=\\'20\\' xmlns=\\'http://www.w3.org/2000/svg\\'%3E%3Ccircle cx=\\'2\\' cy=\\'2\\' r=\\'2\\' fill=\\'%230EA5E9\\' fill-opacity=\\'0.08\\'/%3E%3C/svg%3E'); border-radius: 20px; padding: 48px 48px; margin-bottom: 32px; border: 1px solid rgba(14,165,233,0.15); box-shadow: 0 16px 32px -8px rgba(14,165,233,0.12), inset 0 1px 0 rgba(255,255,255,0.9); display: flex; align-items: center; justify-content: space-between; width: 100%; min-height: 236px;">
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
    
    # Fetch all requests from the database
    df_requests = get_all_requests()
    
    # Calculate statistics safely
    total_pending = len(df_requests[df_requests['status'] == 'Pending']) if df_requests is not None and not df_requests.empty else 0
    total_approved = len(df_requests[df_requests['status'] == 'Approved']) if df_requests is not None and not df_requests.empty else 0
    total_rejected = len(df_requests[df_requests['status'] == 'Rejected']) if df_requests is not None and not df_requests.empty else 0

    # Display Stat Cards
    st.markdown(
        f"""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 32px;">
            <div style="background: #FFFFFF; border-radius: 16px; padding: 24px 28px; border: 1px solid rgba(0,0,0,0.06); box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
                <div style="font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #0EA5E9; margin-bottom: 12px;">Pending</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 40px; line-height: 1; color: #1A1A2E; margin-bottom: 6px;">{total_pending}</div>
                <div style="font-size: 13px; color: #8B8B9A;">awaiting your review</div>
            </div>
            <div style="background: #FFFFFF; border-radius: 16px; padding: 24px 28px; border: 1px solid rgba(0,0,0,0.06); box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
                <div style="font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #10B981; margin-bottom: 12px;">Approved</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 40px; line-height: 1; color: #1A1A2E; margin-bottom: 6px;">{total_approved}</div>
                <div style="font-size: 13px; color: #8B8B9A;">successful matches</div>
            </div>
            <div style="background: #FFFFFF; border-radius: 16px; padding: 24px 28px; border: 1px solid rgba(0,0,0,0.06); box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
                <div style="font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #EF4444; margin-bottom: 12px;">Rejected</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 40px; line-height: 1; color: #1A1A2E; margin-bottom: 6px;">{total_rejected}</div>
                <div style="font-size: 13px; color: #8B8B9A;">declined requests</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<hr style='border: none; margin: 32px 0; border-bottom: 1px solid rgba(0,0,0,0.1);' />", unsafe_allow_html=True)
    
    if df_requests is None or df_requests.empty:
        st.info("No requests found in the database.")
        return
        
    # Create the three tabs
    tab_pending, tab_approved, tab_rejected = st.tabs(["Pending", "Approved", "Rejected"])
    
    df_pending = df_requests[df_requests['status'] == 'Pending']
    df_approved = df_requests[df_requests['status'] == 'Approved']
    df_rejected = df_requests[df_requests['status'] == 'Rejected']
    
    # --- PENDING TAB ---
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
                unsafe_allow_html=True
            )
        else:
            for index, row in df_pending.iterrows():
                # Display each request in a nice card-like container
                with st.container(border=True):
                    col_info, col_actions = st.columns([3, 1], vertical_alignment="center")
                    
                    with col_info:
                        score_str = f"{row['compatibility_score']:.2f}%" if pd.notnull(row['compatibility_score']) else "N/A"
                        st.markdown(
                            f"""
                            <div style="padding: 0px 8px 8px 8px; margin-top: -8px;">
                                <div style="font-size: 22px; font-weight: 600; color: #1A1A2E; margin-bottom: 12px;">{row['client_name']}</div>
                                <div style="font-size: 16px; color: #5A5A6E;">
                                    <div style="margin-bottom: 8px;">✉️ <strong style="color: #4A4A5C; margin-left: 4px;">Email:</strong> {row['client_email']}</div>
                                    <div style="margin-bottom: 8px;">🧑‍⚕️ <strong style="color: #4A4A5C; margin-left: 4px;">Requested Counselor:</strong> {row['counselor_name']}</div>
                                    <div style="margin-bottom: 4px;">🎯 <strong style="color: #4A4A5C; margin-left: 4px;">Match Score:</strong> <span style="background: rgba(16,185,129,0.15); color: #10B981; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 14px;">{score_str}</span></div>
                                </div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        
                    with col_actions:
                        if st.button("Approve", key=f"approve_{row['request_id']}", type="primary", use_container_width=True):
                            confirm_approve_dialog(row['request_id'], row['client_name'], row['client_email'], row['counselor_name'])
                            
                        if st.button("Reject", key=f"reject_{row['request_id']}", use_container_width=True):
                            confirm_reject_dialog(row['request_id'], row['client_name'])

    # --- APPROVED TAB ---
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
                unsafe_allow_html=True
            )
        else:
            # Drop the request_id from display for cleaner UI
            display_df = df_approved.drop(columns=['request_id'])
            # Rename columns for display
            display_df = display_df.rename(columns={
                'client_name': 'Client Name',
                'client_email': 'Client Email',
                'counselor_name': 'Counselor Name',
                'compatibility_score': 'Match Score',
                'status': 'Status'
            })
            st.dataframe(display_df, use_container_width=True, hide_index=True)

    # --- REJECTED TAB ---
    with tab_rejected:
        st.markdown("<h3 style='font-family: \"DM Serif Display\", serif; margin-top: 16px; margin-bottom: 8px; color: #EF4444;'>Rejected Requests</h3>", unsafe_allow_html=True)
        if df_rejected.empty:
            st.markdown(
                """
                <div style="background: #FFFFFF; border: 1px dashed rgba(0,0,0,0.1); border-radius: 12px; padding: 48px 20px; text-align: center; margin-top: 16px;">
                    <div style="font-size: 36px; margin-bottom: 12px; opacity: 0.7;">🚫</div>
                    <div style="font-size: 16px; font-weight: 600; color: #1A1A2E; margin-bottom: 4px;">No rejected requests</div>
                    <div style="font-size: 14px; color: #8B8B9A;">Rejected records will be stored here.</div>
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            display_df = df_rejected.drop(columns=['request_id'])
            display_df = display_df.rename(columns={
                'client_name': 'Client Name',
                'client_email': 'Client Email',
                'counselor_name': 'Counselor Name',
                'compatibility_score': 'Match Score',
                'status': 'Status'
            })
            st.dataframe(display_df, use_container_width=True, hide_index=True)
