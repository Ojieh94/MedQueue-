from sqlalchemy.orm import Session
from app import models


def get_admin(db: Session, admin_id: int):
    return db.query(models.Admin).filter(models.Admin.id == admin_id).first()


def get_admins(db: Session, offset: int = 0, limit: int = 10):
    return db.query(models.Admin).offset(offset).limit(limit).all()


def get_admin_by_email(db: Session, email: str):
    return db.query(models.Admin).join(models.User, models.Admin.user_id == models.User.id).filter(models.User.email == email).first()


def get_admin_by_user_id(db: Session, user_id: int):
    return db.query(models.Admin).filter(models.Admin.user_id == user_id).first()
