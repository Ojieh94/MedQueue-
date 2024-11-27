import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.oauth2 import get_current_user
from sqlalchemy.orm import Session
from app import schemas, models
from app.crud import medical_records as record_crud, doctors as doc_crud, patients as pat_crud
from app.database import get_db

router = APIRouter(
    tags=['Medical_records']
)



@router.get('/medical_record/{record_id}', status_code=200, response_model=schemas.MedicalRecordBase)
def get_medical_record_by_id(record_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    record = record_crud.get_record(db=db, record_id=record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found")
    
    if current_user.role == schemas.UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Records can only be viewed by assigned doctors or owner")
    
    if current_user.role == schemas.UserRole.DOCTOR:
        current_doctor = doc_crud.get_doctor_by_user_id(db=db, user_id=current_user.id)

        if current_doctor.id != record.doctor_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only assigned doctors can view record")
        
    if current_user.role == schemas.UserRole.PATIENT:
        current_patient = pat_crud.get_patient_by_user_id(db=db, user_id=current_user.id)

        if current_patient.id != record.patient_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot view another patients record")
        
    return record


@router.post('/medical_record', status_code=201, response_model=schemas.MedicalRecordBase)
def create_medical_record(payload: schemas.MedicalRecordCreate, db: Session = Depends(get_db), current_user: schemas.Admin = Depends(get_current_user)):
    record = record_crud.create_record(db=db, payload=payload)

    if current_user.admin_type is not schemas.AdminType.HOSPITAL_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Hospital Admin can create records")
    
    return record


@router.put('/medical_record/{record_id}', status_code=200, response_model=schemas.MedicalRecordBase)
def update_record(record_id: int, payload: schemas.MedicalRecordUpdate, db: Session = Depends(get_db), current_user: schemas.Doctor = Depends(get_current_user)):
    record = record_crud.get_record(db=db, record_id=record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    
    if current_user.id != record.doctor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only assigned doctors can perform this action")
    
    record = record_crud.update_record(db=db, record_id=record_id, record_payload=payload)

    return record


@router.delete('/medical_record/{record_id}', status_code=200)
def delete_medical_record(record_id: int, db: Session = Depends(get_db), current_user: schemas.Admin = Depends(get_current_user)):
    record = record_crud.get_record(db=db, record_id=record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    if current_user.admin_type is not schemas.AdminType.HOSPITAL_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only Hospital Admin can create records")

    record_crud.delete_record(db=db, record_id=record_id)

    return {"message": "Record deleted successfully"}
