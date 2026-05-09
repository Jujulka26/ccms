import os
import resend

resend.api_key = os.environ.get("RESEND_API_KEY", "")

SENDER_EMAIL = "noreply@cc-match.com"
SUPPORT_EMAIL = "support@cc-match.com"


def send_approval_email(client_name: str, client_email: str, counselor_name: str):
    if not resend.api_key:
        raise RuntimeError("RESEND_API_KEY environment variable is not set.")

    body = f"""Hello {client_name},

Great news! Your request to match with our Licensed Counselor, {counselor_name}, has been reviewed and approved by the clinic coordinator.

Please wait for {counselor_name} to contact you directly via this email address to schedule your first introductory session.

If you have any immediate questions, please contact us at {SUPPORT_EMAIL}.

Warm regards,
Client-Counselor Matching System
"""
    resend.Emails.send({
        "from": f"CC Match <{SENDER_EMAIL}>",
        "to": client_email,
        "subject": "Counselor Match Request Approved!",
        "text": body,
    })


def send_enquiry_email(name: str, email: str, subject: str, message: str):
    if not resend.api_key:
        raise RuntimeError("RESEND_API_KEY environment variable is not set.")

    body = f"""New enquiry received via the Client-Counselor Matching System.

Name    : {name}
Email   : {email}
Subject : {subject}

Message:
{message}

---
Reply directly to this email to respond to {name}."""

    resend.Emails.send({
        "from": f"CC Match <{SENDER_EMAIL}>",
        "to": SUPPORT_EMAIL,
        "reply_to": email,
        "subject": f"[Client Enquiry] {subject} — from {name}",
        "text": body,
    })
