from sqlalchemy.orm import Session
from app import models

"""
get doctor by id
"""

def get_doctor_by_id(doctor_id: int, db: Session) -> models.Doctor:
    return db.query(models.Doctor).filter(models.Doctor.id ==doctor_id).first()