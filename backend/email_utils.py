import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SENDER_EMAIL = "saltysmilesofficial@gmail.com"


def send_approval_email(client_name: str, client_email: str, counselor_name: str):
    password = os.environ.get("EMAIL_PASSWORD", "")
    if not password:
        raise RuntimeError("EMAIL_PASSWORD environment variable is not set.")

    body = f"""Hello {client_name},

Great news! Your request to match with our Licensed Counselor, {counselor_name}, has been reviewed and approved by the clinic coordinator.

Please wait for {counselor_name} to contact you directly via this email address to schedule your first introductory session.

If you have any immediate questions, feel free to reply to this email.

Warm regards,
Client-Counselor Matching System
"""
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = client_email
    msg["Subject"] = "Counselor Match Request Approved!"
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SENDER_EMAIL, password)
    server.sendmail(SENDER_EMAIL, client_email, msg.as_string())
    server.quit()
