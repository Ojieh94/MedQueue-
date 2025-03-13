import string
from fastapi import HTTPException
from app import schemas
from app.crud.hospitals import get_hospital_by_email
from app.crud.users import get_user_by_email
from sqlalchemy.orm import Session
from app.utils import validate_hospital_password, validate_password
from app.oauth2 import hash_password, verify_password
import secrets
from app.models import PasswordResetToken
from datetime import datetime,timedelta



def update_password(payload: schemas.PasswordResetConfirm, db: Session):

    user = get_user_by_email(db=db, email=payload.email)
    hospital = get_hospital_by_email(db=db, email=payload.email)
    if not user and not hospital:
        raise HTTPException(
            status_code=404, detail="Not found"
        )

    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=400, detail="Passwords do not match."
        )

    new_password_hashed = hash_password(payload.new_password)

    # update user's password
    if user:
        if  verify_password(payload.new_password, user.password):
            raise HTTPException(status_code=400, detail="For security reasons, new password cannot be the same as the old password.")

        # Validate password
        user_password_validation_result = validate_password(payload.new_password, user.first_name, user.last_name)

        if user_password_validation_result != "Password is valid":
            raise HTTPException(status_code=400, detail=user_password_validation_result)

        user.password = new_password_hashed
        db.commit()
        db.refresh(user)
        return user
    
    #updating hospital's passsword
    if hospital:
        if verify_password(payload.new_password, hospital.password):
            raise HTTPException(status_code=400, detail="For Security reasons, new password cannot be the same as the old password.")

        #validate password
        hospital_password_validation_result = validate_hospital_password(payload.new_password, hospital.name, hospital.owner_name)

        if hospital_password_validation_result != "Password is valid":
            raise HTTPException(status_code=400, detail=hospital_password_validation_result)
        
        hospital.password = new_password_hashed
        db.commit()
        db.refresh(hospital)
        return hospital
   

def generate_otp(length: int = 6) -> str:
    characters = string.digits  # Digits-only OTP
    return ''.join(secrets.choice(characters) for _ in range(length))

def create_password_reset_token(email: str, db: Session) -> str:    
    otp = generate_otp()
    reset_token = PasswordResetToken(
        token=otp,
        email=email,
        expires_at=datetime.now() + timedelta(minutes=5)  # Expires in 5 minutes
    )
    db.add(reset_token)
    db.commit()
    return otp

#background task for periodic cleanup
def delete_expired_tokens(db: Session):
    expired_time = datetime.now() - timedelta(hours=24)
    db.query(PasswordResetToken).filter(PasswordResetToken.created_at < expired_time).delete()
    db.commit()