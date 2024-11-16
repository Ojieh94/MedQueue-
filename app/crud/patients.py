from sqlalchemy.orm import Session
from app import models


def get_patient_by_email(db: Session, email: str):
    return db.query(models.Patient).join(models.User, models.Patient.user_id == models.User.id).filter(models.User.email == email).first()
