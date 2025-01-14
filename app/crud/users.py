from typing import List, Optional
from fastapi import Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app import models, schemas
from app.crud.hospitals import get_hospital_by_email

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

def get_user(db: Session, user_id: int) -> models.User:
    return db.query(models.User).filter(models.User.id == user_id).first()

def delete_user(db: Session, user_id: int):
    user = get_user(db=db, user_id=user_id)
    if not user:
        False

    db.delete(user)
    db.commit()

#getting all hospital and user's email address
def confirm_emails(email: str, db: Session):
    user_email = get_user_by_email(db=db, email=email)
    hospital_email = get_hospital_by_email(db=db, email=email)

    if user_email:
        return user_email.email
    elif hospital_email:
        return hospital_email.email
    else:
        return None


# def password_reset_email(email: str, db: Session):
#     email_check = confirm_emails(email, db)

#     email = db.query(models.PasswordResetToken).filter(models.PasswordResetToken.email == email_check).first()

#     if not email:
#         return None
    
#     return email