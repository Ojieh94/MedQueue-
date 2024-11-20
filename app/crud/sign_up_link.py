import secrets
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import SignupLink

def create_signup_link(email: str, db: Session) -> str:
    token = secrets.token_urlsafe(32)
    signup_link = SignupLink(token=token, email=email)
    db.add(signup_link)
    db.commit()
    return token

#background task for periodic cleanup
def delete_expired_tokens(db: Session):
    expired_time = datetime.now() - timedelta(hours=24)
    db.query(SignupLink).filter(SignupLink.created_at < expired_time).delete()
    db.commit()