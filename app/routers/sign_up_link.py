from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import sign_up_link as link_gen

router = APIRouter(
    tags=["Unique Signup Link Generator"] #you can rename this with something better though
)

@router.post("/generate-signup-link/")
def generate_link(email: str, db: Session = Depends(get_db)):
    token = link_gen.create_signup_link(email, db)

    return {"signup_token": token}
