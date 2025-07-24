from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.oauth2 import get_current_user
from sqlalchemy.orm import Session
from app import schemas, models
from app.crud import patients as patient_crud
from app.database import get_db

router = APIRouter(
    tags=['Patients']
)

"""
list all patient
list patient by id and hospital_card_number
update patient
delete patient
"""

@router.get("/patients", status_code=status.HTTP_200_OK, response_model=List[schemas.PatientResponse])
def get_all_patients(skip: int = 0, limit: int = 10, search: Optional[str] = "", db: Session = Depends(get_db)):
    
    patients = patient_crud.get_patients(skip, limit, search, db)
    return patients

@router.get('/patients/{patient_id}', status_code=status.HTTP_200_OK, response_model=schemas.PatientResponse)
def get_single_patient(patient_id: int, db: Session = Depends(get_db)):#, current_user: models.User = Depends(get_current_user)):

    patient = patient_crud.get_patient_by_id(patient_id, db)
    
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    #authorize the user
    ######## To be uncommented later
    # allowed_admins = {schemas.UserRole.ADMIN, schemas.UserRole.DOCTOR}

    # # Check if current user is an admin(endpoint is only accessible to super admins and hospital admins)
    # if current_user.role not in allowed_admins and current_user.id != patient.user_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized! Aborting..."
    #     )
    
    return patient

@router.get('/patients/cards/{patient_card_id}', status_code=status.HTTP_200_OK, response_model=schemas.PatientResponse)
def fetch_patient(patient_card_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    patient = patient_crud.get_patient_by_card_id(patient_card_id, db)
    
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    #authorize the user
    allowed_admins = {schemas.UserRole.ADMIN, schemas.UserRole.DOCTOR}

    # Check if current user is an admin(endpoint is only accessible to super admins and hospital admins)
    if current_user.role not in allowed_admins and current_user.id != patient.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized! Aborting..."
        )
    
    return patient

@router.put('/patients/{patient_id}', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.PatientResponse)
def update_patient(patient_id: int, patient_payload: schemas.PatientUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user), admin_user: models.Admin = Depends(get_current_user)):

    patient = patient_crud.get_patient_by_id(patient_id, db)
    
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    allowed_admins = {schemas.AdminType.SUPER_ADMIN, schemas.AdminType.HOSPITAL_ADMIN}

    # Check if current user is an admin(endpoint is only accessible to super admins and hospital admins)
    if admin_user.admin_type not in allowed_admins and current_user.id != patient.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized! Aborting..."
        )
    
    #update hospital
    updated_patient = patient_crud.update_patient(patient_id, patient_payload, db)
    return updated_patient

@router.delete('/patients/{patient_id}', status_code=status.HTTP_202_ACCEPTED)
def delete_patient(patient_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user),admin_users: models.Admin = Depends(get_current_user)):

    #patient availability check
    patient = patient_crud.get_patient_by_id(patient_id, db)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    
    # authorization block
    allowed_admins = {schemas.AdminType.SUPER_ADMIN, schemas.AdminType.HOSPITAL_ADMIN}

    # Check if current user is an admin(endpoint is only accessible to super admins and hospital admins)
    if admin_users.admin_type not in allowed_admins and current_user.id != patient.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized! Aborting..."
        )
    
    
    patient_crud.delete_patient(patient_id, db)

    return{"message": "Patient deleted successfully!"}


@router.delete('/patients/backend/{patient_id}', status_code=status.HTTP_202_ACCEPTED)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_crud.get_patient_by_id(patient_id, db)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    
    patient_crud.delete_patient(patient_id, db)

    return {"message": "Patient deleted successfully!"}