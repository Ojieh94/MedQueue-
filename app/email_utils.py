import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))


def send_password_reset_email(to_email: str, first_name: str, token: str):
    subject = "Password Reset Request"
    reset_link = f"https://www.queuemedix.com/forgot-password?token={token}"

    body = f"""
    <html>
    <body>
        <p>Hello {first_name},</p>  <!-- 🔹 Inserts first name -->
        <p>You requested a password reset. Click the link below to reset your password:</p>
        <br>
        <a href="{reset_link}" style="background-color:#008CBA;color:white;padding:10px 15px;text-decoration:none;border-radius:5px;">Reset Password</a>
        <br>
        <br>
        <p>If you did not request this, please ignore this email.</p>
        <p>Thank you,</p>
        <br>
        <p>QueueMedix Team</p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        print("Password reset email sent successfully!")
        return True
    except Exception as e:
        print("Failed to send email:", e)
        return False
