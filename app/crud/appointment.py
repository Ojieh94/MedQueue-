from sqlalchemy import and_
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.routers.queue_sys import notify_queue_update

"""
create an appointment
list appointments
list patient appointment
get appointment by id
get appointment by hospital
get uncompleted appointment
cancel an appointment
check pending appointment
switch apointment status
"""

async def create_appointment(patient_id: int, payload: schemas.AppointmentCreate, db: Session):
    
    appointment = models.Appointment(**payload.model_dump(), patient_id=patient_id)
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    await notify_queue_update(hospital_id=appointment.hospital_id, db=db)


    return appointment 


def get_appointments(skip: int, limit: int, db: Session) -> List[models.Appointment]:
    query = db.query(models.Appointment).order_by(models.Appointment.scheduled_time)
    return query.offset(skip).limit(limit).all()

def get_patient_appointments(patient_id: int, skip: int, limit: int, db: Session) -> List[models.Appointment]:
    query = db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).order_by(models.Appointment.scheduled_time)
    return query.offset(skip).limit(limit).all()

def get_appointment_by_id(appointment_id: int, db: Session) -> models.Appointment:
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()


def get_appointment_by_hospital_id(hospital_id: int, skip: int, limit: int, db: Session) -> List[models.Appointment]:
    return db.query(models.Appointment).filter(models.Appointment.hospital_id == hospital_id).order_by(models.Appointment.scheduled_time).offset(skip).limit(limit).all()


def get_appointment_by_doctor_id(doctor_id: int, skip: int, limit: int, db: Session) -> List[models.Appointment]:
    return db.query(models.Appointment).filter(models.Appointment.doctor_id == doctor_id).order_by(models.Appointment.scheduled_time).offset(skip).limit(limit).all()

def get_hospital_appointment_by_schedule_time(hospital_id: int, scheduled_time: str, db: Session) -> models.Appointment:
    return db.query(models.Appointment).filter(models.Appointment.hospital_id == hospital_id, models.Appointment.scheduled_time == scheduled_time).first()

def get_uncompleted_appointments(db: Session) -> List[models.Appointment]:
    return db.query(models.Appointment).filter(models.Appointment.status != schemas.AppointmentStatus.COMPLETED).order_by(models.Appointment.scheduled_time).all()

async def cancel_appointment(appointment_id: int, db: Session):
    appointment = get_appointment_by_id(appointment_id, db)
    
    if not appointment:
        return False
    
    appointment.status = schemas.AppointmentStatus.CANCELED
    db.commit()
    db.refresh(appointment)

    await notify_queue_update(hospital_id=appointment.hospital_id, db=db)


    return appointment

def get_pending_appointments(db: Session) -> List[models.Appointment]:
    query = db.query(models.Appointment).filter(models.Appointment.status == schemas.AppointmentStatus.PENDING).order_by(models.Appointment.scheduled_time)
    return query.all()


def get_patient_pending_appointments(patient_id: int, db: Session) -> models.Appointment:
    query = db.query(models.Appointment).filter(
        and_(
            models.Appointment.patient_id == patient_id,
            models.Appointment.status != schemas.AppointmentStatus.COMPLETED,
            models.Appointment.status != schemas.AppointmentStatus.CANCELED
        )
    )
    return query.first()


async def switch_appointment_status(appointment_id: int, new_status: schemas.AppointmentStatusUpdate, db: Session) -> models.Appointment:
    appointment = get_appointment_by_id(appointment_id, db)
    
    if not appointment:
        return False
    
    appointment.status = new_status.status
    db.commit()
    db.refresh(appointment)

    await notify_queue_update(hospital_id=appointment.hospital_id, db=db)


    return appointment


async def delete_appointment(appointment_id: int, db: Session):
    appointment = get_appointment_by_id(appointment_id, db)
    
    if not appointment:
        return False
    
    db.delete(appointment)
    db.commit()

    await notify_queue_update(hospital_id=appointment.hospital_id, db=db)

    return True