from fastapi import HTTPException
from app import schemas
from app.crud.hospitals import get_hospital_by_email
from app.crud.users import get_user_by_email
from sqlalchemy.orm import Session
from app.utils import validate_hospital_password, validate_password
from app.oauth2 import hash_password



def update_password(payload: schemas.PassReset, db: Session):

    user = get_user_by_email(payload.email, db)
    if not user:
        return None

    if payload.new_password != payload.confirm_password:
        return None

    new_password_hashed = hash_password(payload.new_password)

    # Check if password is same as old password
    if user.password == new_password_hashed:
        raise HTTPException(
            status_code=400, detail="Password cannot be the same as the current password")

    # Validate password
    password_validation_result = validate_password(
        payload.new_password, user.first_name, user.last_name)

    if password_validation_result != "Password is valid":
        raise HTTPException(status_code=400, detail=password_validation_result)

    user.password = new_password_hashed
    db.commit()
    db.refresh(user)
    return user


def update_hospital_password(payload: schemas.PassReset, db: Session):

    hospital = get_hospital_by_email(payload.email, db)
    if not hospital:
        return None

    if payload.new_password != payload.confirm_password:
        return None

    new_password_hashed = hash_password(payload.new_password)

    # Check if password is same as old password
    if hospital.password == new_password_hashed:
        raise HTTPException(
            status_code=400, detail="Password cannot be the same as the current password")

    # Validate password
    password_validation_result = validate_hospital_password(
        payload.new_password, hospital.name, hospital.owner_name)

    if password_validation_result != "Password is valid":
        raise HTTPException(status_code=400, detail=password_validation_result)

    hospital.password = new_password_hashed
    db.commit()
    db.refresh(hospital)
    return hospital
