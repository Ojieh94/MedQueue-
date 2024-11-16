from sqlalchemy.orm import Session
from app import models, schemas


def create_hospital(payload: schemas.HospitalCreate, db: Session):
    hospital = models.Hospital(**payload.model_dump())

    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


def get_hospital_by_email(db: Session, email: str):
    return db.query(models.Hospital).filter(models.Hospital.email == email).first()


def get_hospitals(db: Session, offset: int = 0, limit: int = 10):
    return db.query(models.Hospital).offset(offset).limit(limit).all()
