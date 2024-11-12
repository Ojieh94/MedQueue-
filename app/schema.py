import enum
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

# Enum for User Roles
class UserRole(str, enum):
    SUPER_ADMIN = "super_admin"
    HOSPITAL_ADMIN = "hospital_admin"
    DOCTOR = "doctor"
    PATIENT = "patient"

# Enum for Appointment Status
class AppointmentStatus(str, enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELED = "canceled"
    IN_PROGRESS = "in_progress"

# Base Model for User
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    hashed_password: str
    confirm_password: str
    role: UserRole
    phone_number: str
    date_of_birth: datetime
    gender: str
    state_of_residence: str
    home_address: str

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id: int
    is_active: bool = False
    created_at: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)

# Base Model for Hospital

class Hospital(BaseModel):
    id: int
    name: str
    address: str
    phone_number: str
    admin_id: int

    model_config = ConfigDict(from_attributes=True)

# Base Model for Doctor
class Doctor(BaseModel):
    id: int
    user_id: int
    hospital_id: int
    role_id: str
    specialization: str
    years_of_experience: int
    is_available: bool = True

    model_config = ConfigDict(from_attributes=True)


# Base Model for Appointment

class AppointmentBase(BaseModel):
    hospital_id: int
    appointment_note: str
    scheduled_time: datetime
    doctor_id: int

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int
    patient: User
    hospital: Hospital
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    doctor_id: Doctor

    model_config = ConfigDict(from_attributes=True)

# Base Model for Medical Record

class MedicalRecord(BaseModel):
    id: int
    patient_id: int
    description: str
    record_date: datetime
    doctor_id: int

    model_config = ConfigDict(from_attributes=True)

# Base Model for Patient

class PatientCreate(BaseModel):
    hospital_card_id: str
    
class Patient(BaseModel):
    id: int
    user_id: int
    hospital_card_id: str
    medical_records: List[MedicalRecord]

    model_config = ConfigDict(from_attributes=True)
