from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app import models


def get_user_by_email(db: Session, email: str) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, offset: int = 0, limit: int = 10, search: Optional[str] = "") -> List[models.User]:
    query = db.query(models.User)

    if search:
        query = query.filter(
            or_(models.User.name.contains(search),
                models.User.state.contains(search))
        )

    return query.offset(offset).limit(limit).all()


def get_hospitals(db: Session, offset: int = 0, limit: int = 10, search: Optional[str] = "") -> List[models.Hospital]:
    query = db.query(models.Hospital)

    if search:
        query = query.filter(
            or_(models.Hospital.name.contains(search),
                models.Hospital.state.contains(search))
        )

    return query.offset(offset).limit(limit).all()

def get_user(db: Session, user_id: int) -> models.User:
    return db.query(models.UserRole).filter(models.User.id == user_id).first()

def delete_user(db: Session, user_id: int):
    user = get_user(db=db, user_id=user_id)
    if not user:
        False

    db.delete(user)
    db.commit()
