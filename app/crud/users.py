from typing import List, Optional
from fastapi import Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app import models, schemas
from app.crud.hospitals import get_hospital_by_email
from app.oauth2 import pwd_context, verify_password
from app.utils import validate_hospital_password, validate_password

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


def update_password(payload: schemas.PassReset, db: Session):
    user = get_user_by_email(payload.email, db)
    if not user:
        return None

    if payload.new_password != payload.confirm_password:
        return None
    
    # checking if the user is trying to re-use the same password
    if verify_password(payload.new_password, user.password):
        raise HTTPException(status_code=400,
                            detail="This is your previous password. Please use something stronger")
    
    # Validate password
    password_validation_result = validate_password(
        payload.new_password, user.first_name, user.last_name)

    if password_validation_result != "Password is valid":
        raise HTTPException(status_code=400, detail=password_validation_result)

    hashed_password = pwd_context.hash(password=payload.new_password)
    user.password = hashed_password
    db.commit()
    db.refresh(user)
    return user


def update_hospital_password(payload: schemas.PassReset, db: Session):
    hospital = get_hospital_by_email(payload.email, db)
    if not hospital:
        return None

    if payload.new_password != payload.confirm_password:
        return None

    # checking if the user is trying to re-use the same password
    if verify_password(payload.new_password, hospital.password):
        raise HTTPException(status_code=400,
                            detail="This is your previous password. Please use something stronger")
    
    # Validate password
    password_validation_result = validate_hospital_password(
        payload.new_password, hospital.name, hospital.owner_name)

    if password_validation_result != "Password is valid":
        raise HTTPException(status_code=400, detail=password_validation_result)

    hashed_password = pwd_context.hash(password=payload.new_password)
    hospital.password = hashed_password
    db.commit()
    db.refresh(hospital)
    return hospital
