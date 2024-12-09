from sqlalchemy.orm import Session
from sqlalchemy.sql import or_
from typing import Optional, List
from app import models, schemas

"""
creat hospital
list hospitals
get a single hospital by name
update hospital details
delete/remove hospital
"""

def create_hospital(payload: schemas.HospitalCreate, db: Session) -> models.Hospital:
    hospital = models.Hospital(**payload.model_dump())

    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


def get_hospital_by_email(db: Session, email: str) -> models.Hospital:
    return db.query(models.Hospital).filter(models.Hospital.email == email).first()

def get_hospital_id(hospital_id: int, db: Session) -> models.Hospital:
    return db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()


def get_hospitals(db: Session, offset: int = 0, limit: int = 10, search: Optional[str] = "") -> List[models.Hospital]:
    query =  db.query(models.Hospital)
    
    if search:
        query = query.filter(
            or_(models.Hospital.name.contains(search), models.Hospital.state.contains(search))
            )
    
    return query.offset(offset).limit(limit).all()

#get hospital doctors
def get_hospital_doctors(hospital_id: int, db: Session):
    return db.query(models.Doctor).filter(models.Doctor.hospital_id == hospital_id).all()

#get available doctors 
def get_hospital_available_doctors(hospital_id: int, db: Session):
    return db.query(models.Doctor).filter(models.Doctor.hospital_id == hospital_id, models.Doctor.is_available == True).all()

#get all appointments
def get_hospital_appointments(hospital_id: int, db: Session):
    return db.query(models.Appointment).filter(models.Appointment.hospital_id == hospital_id).all()

def get_hospital_by_name(name: str, db: Session) -> models.Hospital:
    return db.query(models.Hospital).filter(models.Hospital.name == name).first()

def update_hospital(hospital_id: int, payload: schemas.HospitalUpdate, db: Session) -> models.Hospital:
    hospital = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if not hospital:
        return False
    
    hospital_dict = payload.model_dump(exclude_unset=True)
    for k, v in hospital_dict.items():
        setattr(hospital, k, v)
    
    db.commit()
    db.refresh(hospital)

    return hospital

def delete_hospital(hospital_id: int, db: Session):
    hospital = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if not hospital:
        return False
    
    db.delete(hospital)
    db.commit()