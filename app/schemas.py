from enum import Enum
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

# Enum for User Roles


class UserRole(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"

# Enum for Admin Roles


class AdminType(str, Enum):
    SUPER_ADMIN = "super_admin"
    HOSPITAL_ADMIN = "hospital_admin"
    DEPARTMENT_ADMIN = "dept_admin"


# Enum for Appointment Status
class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELED = "canceled"
    IN_PROGRESS = "in_progress"

# Enum for Hospital Ownership type


class OwnershipType(str, Enum):
    PRIVATE = "private"
    GOVERNMENT = "government"
    NGO = "ngo"

# Base Model for User


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    role: UserRole
    phone_number: str
    date_of_birth: datetime
    gender: str
    country: str
    state_of_residence: str
    home_address: str


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class User(UserBase):
    id: int
    is_active: bool = False
    created_at: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)

# Base Model for Hospital


class HospitalBase(BaseModel):
    name: str
    address: str
    email: str
    website: str
    license_number: str
    phone_number: str
    hospital_admin_id: int
    registration_number: str
    ownership_type: OwnershipType
    owner_name: str
    accredited: bool = False


class HospitalCreate(HospitalBase):
    password: str


class HospitalUpdate(HospitalBase):
    pass


class Hospital(HospitalBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# Base Model for Doctor


class Doctor(BaseModel):
    id: int
    user_id: int
    hospital_id: int
    role_id: str | None
    specialization: str
    years_of_experience: int
    is_available: bool = True

    model_config = ConfigDict(from_attributes=True)


class DoctorCreate(UserCreate):
    hospital_id: int
    role_id: str | None
    specialization: str
    years_of_experience: int

# Base Model for Admin


class Admin(BaseModel):
    id: int
    user_id: int
    hospital_id: int
    hospital_admin_id: str
    admin_type: AdminType

    model_config = ConfigDict(from_attributes=True)


class AdminCreate(UserCreate):
    hospital_id: int
    hospital_admin_id: str
    admin_type: AdminType


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


class PatientCreate(UserCreate):
    hospital_card_id: str | None


class Patient(BaseModel):
    id: int
    user_id: int
    hospital_card_id: str
    medical_records: List[MedicalRecord]

    model_config = ConfigDict(from_attributes=True)
