import re
from sqlalchemy.orm import Session
from app.models import SignupLink
from datetime import datetime, timedelta

from app.crud.hospitals import get_hospital_by_email
from app.crud.users import get_user_by_email


def validate_password(password: str, first_name: str, last_name: str) -> str:
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if first_name.lower() in password.lower() or last_name.lower() in password.lower():
        return "Password cannot be the same as your name"
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one digit"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Password must contain at least one special character"
    if ' ' in password:
        return "Password must not contain spaces"
    return "Password is valid"


def validate_hospital_password(password: str, name: str, owner_name: str) -> str:
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if name.lower() in password.lower() or owner_name.lower() in password.lower():
        return "Password cannot be the same as your name"
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one digit"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Password must contain at least one special character"
    if ' ' in password:
        return "Password must not contain spaces"
    return "Password is valid"

# To get current user for authentication
def get_hospital_or_user(db: Session, email: str):
    user = get_hospital_by_email(db, email)
    if not user:
        user = get_user_by_email(db, email)
    return user

def validate_signup_token(token: str, db: Session) -> bool:
    signup_link = db.query(SignupLink).filter(SignupLink.token == token).first()
    if not signup_link:
        return False
    if signup_link.is_used:
        return False
    # Check if the token is expired (e.g., valid for 24 hours)
    if signup_link.created_at < datetime.now() - timedelta(hours=24):
        return False
    return True

def remaining_time(created_at: datetime) -> str:
    time_diff = created_at - datetime.now()
    days, remainder = divmod(time_diff.days, 86400)
    hours, remainder = divmod(time_diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"

