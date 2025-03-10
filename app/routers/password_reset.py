from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.schemas import PasswordReset, PasswordResetConfirm
from app.crud.users import confirm_emails
from app.database import get_db
from app.crud.password_reset import create_password_reset_token, update_password
from app.models import PasswordResetToken
from app import email_utils


router = APIRouter(
    tags=["Reset Password"]
)

@router.post("/generate_password_reset_token", status_code=status.HTTP_201_CREATED)
def generate_password_reset_token(payload: PasswordReset, db:Session=Depends(get_db)):
    user = confirm_emails(payload.email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_password_reset_token(payload.email, db)

    # Send the token via email instead of returning it
    email_sent = email_utils.send_password_reset_email(payload.email, user.first_name, token)
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send password reset email")

    return {"message": "Password reset email sent successfully!"}

@router.put('/password_reset', status_code=status.HTTP_202_ACCEPTED)
def password_reset(token: str, payload: PasswordResetConfirm, db: Session = Depends(get_db)):

    user = confirm_emails(payload.email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    confirm_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
    if not confirm_token:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    if confirm_token.is_used:
        raise HTTPException(status_code=400, detail="Token already used")

    # Check if token is expired (optional)
    if confirm_token.created_at < datetime.now() - timedelta(hours=24):
        raise HTTPException(status_code=400, detail="Token has expired")

    # Check if the email associated with the token matches the payload
    if confirm_token.email != payload.email:
        raise HTTPException(status_code=400, detail="Token email does not match")


    #updating password
    update_password(payload, db)

    # Mark the token as used
    confirm_token.is_used = True
    db.commit()
    
    return {"message": "Password updated successfully"}
