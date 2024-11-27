from sqlalchemy.orm import Session

from app import models, schemas


def create_record(db: Session, payload: schemas.MedicalRecordCreate) -> models.MedicalRecord:
    medical_record = models.MedicalRecord(**payload.model_dump())

    db.add(medical_record)
    db.commit()
    db.refresh(medical_record)
    return medical_record


def get_record(db: Session, record_id: int) -> models.MedicalRecord:
    return db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()


def get_patient_record(db: Session, patient_id: int) -> models.MedicalRecord:
    return db.query(models.MedicalRecord).filter(models.MedicalRecord.patient_id == patient_id).first()

def update_record(db: Session, record_id: int, record_payload: schemas.MedicalRecordUpdate) -> models.MedicalRecord:
    record = get_record(db=db,record_id=record_id)
    if not record:
        return None
    
    record_update = record_payload.model_dump(exclude_unset=True)
    for k, v in record_update.items():
        setattr(k, v, record)

    db.commit()
    db.refresh(record)
    return record
    

def delete_record(db: Session, record_id: int):
    record = get_record(db, record_id=record_id)
    if not record:
        return None
    
    db.delete(record)
    db.commit()