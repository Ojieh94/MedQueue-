from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
# from app.oauth2 import get_current_user
from sqlalchemy.orm import Session
from app import schemas
from app.crud import patients as pat_crud, appointment as apt_crud, hospitals as hp_crud, doctors as doc_crud
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

@router.put('/appointments/{appointment_id}/assign_doctor', status_code=status.HTTP_202_ACCEPTED)
def assign_doctor(appointment_id: int, payload: schemas.AssignDoctor, db: Session = Depends(get_db)):
    
    appointment = apt_crud.get_appointment_by_id(appointment_id, db)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    
    # Check if the doctor is available
    doctor = doc_crud.get_doctor(db, payload.doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    
    if not doctor.is_available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Doctor has already been assigned")
    
    # Assign doctor to the appointment
    appointment.doctor_id = payload.doctor_id
    db.commit()
    db.refresh(appointment)

    #change doctor availability status
    doctor.is_available = False
    db.commit()
    db.refresh(doctor)

    return {"message": "doctor assigned successfully!"}

@router.post('/appointments/new_appointment', status_code=status.HTTP_201_CREATED)
def create_appointment(patient_id: int, apt_payload: schemas.AppointmentCreate, db: Session = Depends(get_db)):

    patient = pat_crud.get_patient_by_id(patient_id, db)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    
    # Check if the patient is already scheduled for an appointment
    existing_appointment = apt_crud.get_patient_pending_appointments(patient_id, db)
    if existing_appointment:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Patient already has a pending appointment")
    
    #check if the hospital exists
    hospital = hp_crud.get_hospital_id(apt_payload.hospital_id, db)
    if not hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    
    # Create the appointment
    apt_crud.create_appointment(patient_id, apt_payload, db)
    
    return {"message": "appointment created successfully!"}

@router.get('/appointments', status_code=status.HTTP_200_OK, response_model=List[schemas.Appointment])
def get_appointments(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    appointments = apt_crud.get_appointments(skip, limit, db)
    return appointments

@router.get('/appointments/patient/{patient_id}', status_code=status.HTTP_200_OK, response_model=List[schemas.Appointment])
def get_patient_appointments(patient_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):

    patient = pat_crud.get_patient_by_id(patient_id, db)
    
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")


    # authorized_users = {schemas.UserRole.ADMIN, schemas.UserRole.DOCTOR}
    
    # # Check if current user is an admin or a doctor(endpoint is only accessible to super admins, doctors, owner(patient) and hospital admins)
    # if patient.user_id != current_user.id and current_user.role not in authorized_users:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Unauthorized! Aborting...."
    #     )
    
    appointments = apt_crud.get_patient_appointments(patient_id, skip, limit, db)
    return appointments

@router.get('/appointments/uncompleted', status_code=status.HTTP_200_OK, response_model=List[schemas.Appointment])
def get_uncompleted_appointments(db: Session = Depends(get_db)):

    appointments = apt_crud.get_uncompleted_appointments(db)

    return appointments

@router.get('/appointments/pending_appointments', status_code=status.HTTP_200_OK, response_model=List[schemas.Appointment])
def get_pending_appointments(db: Session = Depends(get_db)):

    
    appointments = apt_crud.get_pending_appointments(db)
    return appointments

@router.get('/appointments/{appointment_id}', status_code=status.HTTP_200_OK, response_model=schemas.Appointment)
def get_appointment_by_id(appointment_id: int, db: Session = Depends(get_db)):

    appointment = apt_crud.get_appointment_by_id(appointment_id, db)

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    

    appointment = apt_crud.get_appointment_by_id(appointment_id, db)

    return appointment


@router.delete('/appointments/{appointment_id}/cancel', status_code=status.HTTP_202_ACCEPTED)
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):

    appointment = apt_crud.get_appointment_by_id(appointment_id, db)

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    
 
    if appointment.status == schemas.AppointmentStatus.CANCELED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Appointment is already canceled")
    
    apt_crud.cancel_appointment(appointment_id, db)
    db.commit()

    doctor = doc_crud.get_doctor(db=db, doctor_id=appointment.doctor_id)
    doctor.is_available = True
    db.commit()
    db.refresh(doctor)

    return {"message": "Appointment has been cancelled successfully!"}


#set appointment status
@router.put('/appointments/{appointment_id}/appointment_status', status_code=status.HTTP_202_ACCEPTED)
def update_appointment_status(appointment_id: int, new_status: schemas.AppointmentStatusUpdate, db: Session = Depends(get_db)):

    appointment = apt_crud.get_appointment_by_id(appointment_id, db)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    
    
    apt_crud.switch_appointment_status(appointment_id, new_status, db)
    db.commit()

    return {"message": f"Appointment status has been updated to {new_status.status}"}