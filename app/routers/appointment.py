from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.oauth2 import get_current_user
from sqlalchemy.orm import Session
from app import schemas, models
from app.crud import patients as pat_crud, appointment as apt_crud, hospitals as hp_crud, doctor as doc_crud
from app.database import get_db

"""
create an appointment
list appointments
list patient appointment
get appointment by id
get uncompleted appointment
cancel an appointment
check patient pending appointment
switch apointment status
"""

router = APIRouter(
    tags=['Appointments']
)

@router.post('/appointments/new_appointment', status_code=status.HTTP_201_CREATED, response_model=schemas.Appointment)
def create_appointment(patient_id: int, apt_payload: schemas.AppointmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    patient = pat_crud.get_patient_by_id(patient_id, db)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    # Check if the patient is already scheduled for an appointment
    existing_appointment = apt_crud.get_pending_appointments(patient_id, db)
    if existing_appointment:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Patient already has an uncompleted appointment")
    
    #check if the hospital exists
    hospital = hp_crud.get_hospital_id(apt_payload.hospital_id, db)
    if not hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    
    #check if the doctor exists
    doctor = doc_crud.get_doctor_by_id(apt_payload.doctor_id, db)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    
    #check doctor availability
    if not doctor.is_available:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The doctor you've chosen is not available at the moment! Please pick a different doctor or check back later.")
    
    # Create the appointment
    new_appointment = apt_crud.create_appointment(patient_id, apt_payload, db)
    db.commit()
    db.refresh(new_appointment)

    doctor.is_available = False
    db.commit()
    db.refresh(doctor)
    
    return new_appointment

@router.get('/appointments', status_code=status.HTTP_200_OK, response_model=List[schemas.Appointments])
def get_appointments(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    users = {schemas.UserRole.ADMIN, schemas.UserRole.DOCTOR}
    
    # Check if current user is an admin or a doctor(endpoint is only accessible to super admins, doctors and hospital admins)
    if current_user.role not in users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized! Aborting...."
        )
    
    appointments = apt_crud.get_appointments(skip, limit, db)
    return appointments

@router.get('/appointments/patient/{patient_id}', status_code=status.HTTP_200_OK, response_model=schemas.Appointment)
def get_patient_appointments(patient_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    patient = pat_crud.get_patient_by_id(patient_id, db)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    users = {schemas.UserRole.ADMIN, schemas.UserRole.DOCTOR}
    
    # Check if current user is an admin or a doctor(endpoint is only accessible to super admins, doctors, owner(patient) and hospital admins)
    if current_user.role not in users and current_user.id != patient.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized! Aborting...."
        )
    
    appointments = apt_crud.get_patient_appointments(patient_id, db)
    return appointments

@router.get('/appointments/{appointment_id}', status_code=status.HTTP_200_OK, response_model=schemas.Appointment)
def get_appointment_by_id(appointment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    appointment = apt_crud.get_appointment_by_id(appointment_id, db)

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    

    users = {schemas.UserRole.ADMIN, schemas.UserRole.DOCTOR}
    
    # Check if current user is an admin or a doctor(endpoint is only accessible to super admins, doctors and hospital admins)
    if current_user.role not in users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized! Aborting...."
        )
    
    appointment = apt_crud.get_appointment_by_id(appointment_id, db)

    return appointment

@router.get('/appointments/uncompleted', status_code=status.HTTP_200_OK, response_model=List[schemas.Appointment])
def get_uncompleted_appointments(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    users = {schemas.UserRole.ADMIN, schemas.UserRole.DOCTOR}
    
    # Check if current user is an admin or a doctor(endpoint is only accessible to super admins, doctors and hospital admins)
    if current_user.role not in users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized! Aborting...."
        )
    
    appointments = apt_crud.get_uncompleted_appointments(db)

    return appointments

@router.delete('/appointments/{appointment_id}/cancel', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Appointment)
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    appointment = apt_crud.get_appointment_by_id(appointment_id, db)

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    
    if current_user.id != appointment.patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized! Aborting..."
        )
    
    apt_crud.cancel_appointment(appointment_id, db)
    db.commit()

    doctor = doc_crud.get_doctor_by_id(appointment.doctor_id, db)
    doctor.is_available = True
    db.commit(doctor)
    db.refresh(doctor)

    return {"message": "Appointment has been deleted successfully!"}

@router.get('/appointments/pending_appointments', status_code=status.HTTP_200_OK, response_model=schemas.Appointment)
def get_pending_appointments(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    
    users = {schemas.UserRole.ADMIN, schemas.UserRole.DOCTOR}
    
    if current_user.role not in users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized! Aborting...."
        )
    
    appointments = apt_crud.get_pending_appointments(db)
    return appointments

#set appointment status
@router.put('/appointments/{appointment_id}/appointment_status', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Appointment)
def update_appointment_status(appointment_id: int, new_status: schemas.AppointmentStatusUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    appointment = apt_crud.get_appointment_by_id(appointment_id, db)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    
    #authorization check
    users = {schemas.UserRole.ADMIN, schemas.UserRole.DOCTOR}
    
    if current_user.role not in users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized! Aborting...."
        )
    
    apt_crud.switch_appointment_status(appointment_id, new_status, db)
    db.commit()

    return {"message": f"Appointment status has been updated to {new_status.status}"}