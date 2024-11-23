from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import database, schemas
from app.crud import users as user_crud
from app.oauth2 import create_email_validation_token, verify_email_validation_token

router = APIRouter(
    tags=["Email Validation"]
)

@router.post("/generate-email-token", status_code=status.HTTP_201_CREATED)
def generate_email_token(email: schemas.EmailValidationRequest, db: Session = Depends(database.get_db)):
    # Find the user by email
    user = user_crud.get_user_by_email(db=db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    # Generate the email validation token
    token = create_email_validation_token(email)
    
    return {"email": email, "token": token}

@router.get("/validate-email", status_code=status.HTTP_200_OK, response_model=schemas.EmailValidationResponse)
def validate_email(token: str, db: Session = Depends(database.get_db)):
    email = verify_email_validation_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )
    
    # Find and activate the user
    user = user_crud.get_user_by_email(db=db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    # Update user's active status
    user.is_active = True
    db.commit()
    db.refresh(user)

    return {"message": "Email validated and account activated"}

