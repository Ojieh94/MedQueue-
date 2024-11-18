from sqlalchemy.orm import Session
from app import models


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, offset: int = 0, limit: int = 10):
    return db.query(models.User).offset(offset).limit(limit).all()


def get_user(db: Session, user_id: int):
    return db.query(models.UserRole).filter(models.User.id == user_id).first()
