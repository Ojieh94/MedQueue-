from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app import models, schemas


def get_doctors(db: Session, name: str = None, specialization: str = None, offset: int = 0, limit: int = 10) -> List[models.Doctor]:
    query = db.query(models.Doctor).join(models.User).filter(models.User.role == schemas.UserRole.DOCTOR)

    if name:
        query = query.filter(or_(models.User.first_name.ilike(f"%{name}%"), models.User.last_name.ilike(f"%{name}%"), (models.User.first_name + "" + models.User.last_name).ilike(f"%{name}%")
                                 )
                             )
        
    if specialization:
        query = query.filter(models.Doctor.specialization.ilike(f"%{specialization}%"))


    return query.offset(offset).limit(limit).all()

def get_doctor(db: Session, doctor_id: int) -> models.Doctor:
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()

def get_doctor_by_email(db: Session, email: str) -> models.Doctor:
    return db.query(models.Doctor).join(models.User, models.Doctor.user_id == models.User.id).filter(models.User.email == email).first()

def get_available_doctors(db: Session, offset: int = 0, limit: int = 10) -> List[models.Doctor]:
    return db.query(models.Doctor).filter(models.Doctor.is_available == True).offset(offset).limit(limit).all()

def change_doctor_availability_status(db: Session, doctor_id: int) -> models.Doctor:
    doctor = get_doctor(db=db, doctor_id=doctor_id)
    if not doctor:
        return False
    
    doctor.is_available = not doctor.is_available

    return doctor


def get_doctors_by_specialization(db: Session, specialization:str, offset: int = 0, limit: int = 10, search: Optional[str] = "") -> List[models.Doctor]:
    query = db.query(models.Doctor.specialization == specialization)

    if search:
        query = query.filter(
            models.Doctor.specialization.ilike(f"%{search}%"))

    return query.offset(offset).limit(limit).all()

