from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.oauth2 import get_current_user
from sqlalchemy.orm import Session
from app import schemas
from app.crud import doctors as doctor_crud, admins as admin_crud, hospitals as hos_crud
from app.database import get_db

router = APIRouter(
    tags=['Doctors']
)

@router.get('/doctors', status_code=200, response_model=List[schemas.DoctorResponse])
def get_all_doctors(db: Session = Depends(get_db), name: str = None, specialization: str = None,  offset: int = 0, limit: int = 10):
    # if current_user.admin_type != schemas.AdminType.SUPER_ADMIN:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super Admin privileges required")
     
    doctors = doctor_crud.get_doctors(db=db, name=name, specialization=specialization, offset=offset, limit=limit)

    return doctors


@router.get('/doctors/{doctor_id}', status_code=200, response_model=schemas.DoctorResponse)
def get_doctor_by_id(doctor_id: int, db: Session = Depends(get_db)):
    # Retrieve doctor by ID
    doctor = doctor_crud.get_doctor(db=db, doctor_id=doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    # Check if the current user is the doctor
    # current_doc = doctor_crud.get_doctor_by_user_id(
    #     db=db, user_id=current_user.id)
    # if current_doc and current_doc.id != doctor_id:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                         detail="Not authorized to perform this action")

    # # Retrieve admin data
    # current_admin = admin_crud.get_admin_by_user_id(db=db, user_id=current_user.id)
    # if current_admin is None:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="Admin privileges required")

    # # Check hospital authorization for non-super admin
    # if current_admin.admin_type != schemas.AdminType.SUPER_ADMIN:
    #     if current_admin.hospital_id != doctor.hospital_id:
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN, detail="You cannot perform this action")

    return doctor



@router.get('/doctors/availability/{hospital_id}', status_code=200, response_model=List[schemas.DoctorResponse])
def get_available_doctors(hospital_id: int, db: Session = Depends(get_db), offset: int = 0, limit: int = 10):
    # if current_user.admin_type != schemas.AdminType.SUPER_ADMIN:
    #     if current_user.hospital_id != hospital_id:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot check doctors of other hospitals")
    hospital = hos_crud.get_hospital_id(hospital_id, db)
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    
    doctors = doctor_crud.get_available_doctors(db=db, hospital_id=hospital_id, offset=offset, limit=limit)

    return doctors

@router.put('/doctors/{doctor_id}', status_code=200, response_model=schemas.DoctorResponse)
def update_doctor(doctor_id: int, doctor_payload: schemas.DoctorUpdate, db: Session = Depends(get_db), current_user: schemas.Doctor = Depends(get_current_user)):
    db_doctor = doctor_crud.get_doctor(db=db, doctor_id=doctor_id)
    if not db_doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    
    if current_user.id != doctor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You cannot perform this action")
    
    
    doctor = doctor_crud.update_doctor(db=db, doctor_id=doctor_id, doctor_payload=doctor_payload)

    return doctor


@router.delete('/doctors/{doctor_id}', status_code=200)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    doctor = doctor_crud.get_doctor(db=db, doctor_id=doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    # Authorization checks
    if current_user.role == schemas.UserRole.PATIENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Patients are not allowed to delete doctors.")

    if current_user.role == schemas.UserRole.DOCTOR:
        current_doctor = doctor_crud.get_doctor_by_user_id(
            db=db, user_id=current_user.id)
        if current_doctor.id != doctor_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Doctors can only delete their own records.")

    if current_user.role == schemas.UserRole.ADMIN:
        current_admin = admin_crud.get_admin_by_user_id(
            db=db, user_id=current_user.id)
        if current_admin.admin_type != schemas.AdminType.SUPER_ADMIN:
            if current_admin.hospital_id != doctor.hospital_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to delete this doctor."
                )

    # Delete the doctor
    doctor_crud.delete_doctor(db=db, doctor_id=doctor_id)

    return {"message": "Doctor deleted successfully"}
