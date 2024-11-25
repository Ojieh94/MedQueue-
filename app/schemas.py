from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import List, Optional

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
    PENDING = "pending"
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
    email: EmailStr
    role: UserRole
    phone_number: str
    date_of_birth: datetime
    gender: str
    country: str
    state_of_residence: str
    home_address: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    role: Optional[UserRole]
    phone_number: Optional[str]
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    country: Optional[str]
    state_of_residence: Optional[str]
    home_address: Optional[str]


class User(UserBase):
    id: int
    is_active: bool = False
    created_at: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)

# Base Model for Hospital
class HospitalBase(BaseModel):
    name: str
    address: str
    state: str
    email: EmailStr
    website: str
    license_number: str
    phone_number: str
    hospital_admin_id: str
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
    hospital_id: Optional[int]
    hospital_admin_id: str
    admin_type: AdminType

    model_config = ConfigDict(from_attributes=True)


class AdminCreate(UserCreate):
    hospital_id: Optional[int] # not all admins need hospital id
    hospital_admin_id: str
    admin_type: AdminType

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

class PatientUpdate(UserUpdate):
    pass


class Patient(BaseModel):
    id: int
    user_id: int
    hospital_card_id: str | None
    medical_records: List[MedicalRecord]

    model_config = ConfigDict(from_attributes=True)

# Response models
class PatientResponse(BaseModel):
    id: int
    hospital_card_id: str | None
    user: UserBase
    medical_records: List[MedicalRecord]

    model_config = ConfigDict(from_attributes=True)

# Base Model for Appointment
class AppointmentBase(BaseModel):
    appointment_note: str
    patient_id: int
    doctor_id: int
    hospital_id: int
    scheduled_time: datetime


class AppointmentCreate(AppointmentBase):
    pass

class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus

class Appointment(AppointmentBase):
    id: int
    patient: PatientResponse
    hospital: Hospital
    status: AppointmentStatus = AppointmentStatus.PENDING
    doctor: Doctor

    model_config = ConfigDict(from_attributes=True)

class DoctorResponse(BaseModel):
    role_id: str | None
    specialization: str
    years_of_experience: int
    is_available: bool = True
    user: UserBase

    model_config = ConfigDict(from_attributes=True)

class AdminResponse(BaseModel):
    admin_type: AdminType
    user: UserBase

    model_config = ConfigDict(from_attributes=True)


class EmailValidationRequest(BaseModel):
    email: EmailStr

class EmailValidationResponse(BaseModel):
    message: str


class DepartmentCreate(BaseModel):
    name: str
    hospital_id: int

class DepartmentUpdate(DepartmentCreate):
    hospital_id: Optional[int]

class Department(DepartmentCreate):
    id: int
    hospital: Hospital

    model_config = ConfigDict(from_attributes=True)