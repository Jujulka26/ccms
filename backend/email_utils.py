import os
import resend

resend.api_key = os.environ.get("RESEND_API_KEY", "")

SENDER_EMAIL = "noreply@cc-match.com"


def send_approval_email(client_name: str, client_email: str, counselor_name: str):
    if not resend.api_key:
        raise RuntimeError("RESEND_API_KEY environment variable is not set.")

    body = f"""Hello {client_name},

Great news! Your request to match with our Licensed Counselor, {counselor_name}, has been reviewed and approved by the clinic coordinator.

Please wait for {counselor_name} to contact you directly via this email address to schedule your first introductory session.

If you have any immediate questions, feel free to reply to this email.

Warm regards,
Client-Counselor Matching System
"""
    resend.Emails.send({
        "from": f"CC Match <{SENDER_EMAIL}>",
        "to": client_email,
        "subject": "Counselor Match Request Approved!",
        "text": body,
    })
