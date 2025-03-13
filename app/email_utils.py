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


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Generic function to send emails via SMTP"""
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

        print(f"Email sent successfully: {subject}")
        return True
    except Exception as e:
        print(f"Failed to send email: {subject}. Error: {e}")
        return False

def send_password_reset_email(to_email: str, name: str, token: str):
    subject = "Password Reset"
    # reset_link = f"https://www.queuemedix.com/forgot-password?token={token}"

    body = f"""
    <html>
    <body>
        <p>Hello {name},</p>  <!-- 🔹 Inserts first name or hospital's name -->
        <p><b>Reset your password</b></p> 
        <p>We received a request to reset the password to your QueueMedix account.</p>
        <br>
        <p>Your OTP code: {token}</p>
        <p>Please note your OTP code will expire after 5 minutes.</p> 
        <p>If you didn't initiate this request, please send us an email to <a href= "mailto:queuemedix@gmail.com">queuemedix@gmail.com</a> so we can immediately look into this.</p>
        <br>
        <p>Best regards,</p>
        
        <p>Team QueueMedix</p>
    </body>
    </html>
    """
    return send_email(to_email, subject, body)
    

def send_successful_reset_email(to_email: str, name: str):
    subject = "Password Reset Successful"
    login_link = f"https://www.queuemedix.com/signin"

    body = f"""
    <html>
    <body>
        <p>Hello {name},</p>  <!-- 🔹 Inserts first name or hospital's name -->
        <p><b>Password Reset Successful</b></p> 
        <p>Your QueueMedix account password has been successfuly reset. Please click on the link below to login.</p>
        <br>
        <a href="{login_link}" style="background-color:blue;color:white;padding:10px 15px;text-decoration:none;border-radius:5px;">Login to your account</a>
        <br>
        <br>
        <p>If you didn't initiate this request, please send us an email to <a href= "mailto:queuemedix@gmail.com">queuemedix@gmail.com</a> so we can immediately look into this.</p>
        <br>
        <p>Best regards,</p>
        
        <p>Team QueueMedix</p>
    </body>
    </html>
    """
    return send_email(to_email, subject, body)