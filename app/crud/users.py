from sqlalchemy.orm import Session
from app import models


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_all_users(db: Session, offset: int = 0, limit: int = 10):
    return db.query(models.User).offset(offset).limit(limit).all()
