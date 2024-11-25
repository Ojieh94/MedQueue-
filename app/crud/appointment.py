from sqlalchemy.orm import Session
from typing import List
from app import models, schemas

"""
create an appointment
list appointments
list patient appointment
get appointment by id
get uncompleted appointment
cancel an appointment
check pending appointment
switch apointment status
"""

def create_appointment(patient_id: int, payload: schemas.AppointmentCreate, db: Session) -> models.Appointment:
    
    appointment = models.Appointment(**payload.model_dump(), patient_id=patient_id)
    db.add(appointment)
    db.commit()
    db.refresh(appointment)


def get_appointments(skip: int, limit: int, db: Session) -> List[models.Appointment]:
    query = db.query(models.Appointment).order_by(models.Appointment.scheduled_time)
    return query.offset(skip).limit(limit).all()

def get_patient_appointments(patient_id: int, skip: int, limit: int, db: Session) -> List[models.Appointment]:
    query = db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).order_by(models.Appointment.scheduled_time)
    return query.offset(skip).limit(limit).all()

def get_appointment_by_id(appointment_id: int, db: Session) -> models.Appointment:
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

def get_uncompleted_appointments(db: Session) -> List[models.Appointment]:
    query = db.query(models.Appointment).filter(models.Appointment.status != schemas.AppointmentStatus.COMPLETED).order_by(models.Appointment.scheduled_time)
    return query.all()

def cancel_appointment(appointment_id: int, db: Session):
    appointment = get_appointment_by_id(appointment_id, db)
    
    if not appointment:
        return False
    
    appointment.status = schemas.AppointmentStatus.CANCELED
    db.commit()
    db.refresh(appointment)
    return appointment

def get_pending_appointments(db: Session) -> List[models.Appointment]:
    query = db.query(models.Appointment).filter(models.Appointment.status == schemas.AppointmentStatus.PENDING).order_by(models.Appointment.scheduled_time)
    return query.all()

def switch_appointment_status(appointment_id: int, new_status: schemas.AppointmentStatusUpdate, db: Session) -> models.Appointment:
    appointment = get_appointment_by_id(appointment_id, db)
    
    if not appointment:
        return False
    
    appointment.status = new_status.status
    db.commit()
    db.refresh(appointment)
    return appointment