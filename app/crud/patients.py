from sqlalchemy.orm import Session
from sqlalchemy.sql import or_
from typing import Optional, List
from app import models, schemas

"""
list all patient
list patient by id and hospital_card_number
update patient
delete patient
"""
def get_patient_by_email(db: Session, email: str):
    return db.query(models.Patient).join(models.User, models.Patient.user_id == models.User.id).filter(models.User.email == email).first()

def get_patients(skip: int, limit: int, search: Optional[str], db: Session) -> List[models.Patient]:
    query =  db.query(models.Patient).join(models.User, models.Patient.user_id == models.User.id)
    
    if search:
        query = query.filter(
            or_(models.User.last_name.contains(search), models.Patient.hospital_card_id.contains(search))
            )
    
    return query.offset(skip).limit(limit).all()


def get_patient_by_id(patient_id: int, db: Session) -> Optional[models.Patient]:
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patient_by_card_id(hospital_card_id: str, db: Session) -> models.Patient:
    return db.query(models.Patient).filter(models.Patient.hospital_card_id == hospital_card_id).first()

def update_patient(patient_id: int, patient_payload: schemas.PatientUpdate, db: Session) -> models.Patient:
    patient = get_patient_by_id(patient_id, db)
    if not patient:
        return False
    
    patient_update = patient_payload.model_dump(exclude_unset=True)
    for k, v in patient_update.items():
        setattr(k, v, patient)
    
    db.commit()
    db.refresh(patient)
    return patient

def delete_patient(patient_id: int, db: Session):
    patient = get_patient_by_id(patient_id, db)
    if not patient:
        return False
    
    db.delete(patient)
    db.commit()
