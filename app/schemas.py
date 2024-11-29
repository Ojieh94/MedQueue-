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
    


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]


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
    registration_number: str
    ownership_type: OwnershipType
    owner_name: str
    accredited: bool = False


class HospitalCreate(HospitalBase):
    password: str


class HospitalUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]
    state: Optional[str]
    email: Optional[EmailStr]
    website: Optional[str]
    license_number: Optional[str]
    phone_number: Optional[str]
    registration_number: Optional[str]
    ownership_type: Optional[OwnershipType]
    owner_name: Optional[str]
    accredited: bool = False


class Hospital(HospitalBase):
    id: int

    model_config = ConfigDict(from_attributes=True)



# Base Model for Doctor
class DoctorBase(BaseModel):
    hospital_id: int
    role_id: str | None
    specialization: str
    phone_number: str
    date_of_birth: datetime
    gender: str
    country: str
    state_of_residence: str
    home_address: str
    years_of_experience: int
    is_available: bool = True

    
class DoctorUpdate(UserUpdate):
    hospital_id: Optional[int]
    role_id: Optional[str]
    specialization: Optional[str]
    phone_number: Optional[str]
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    country: Optional[str]
    state_of_residence: Optional[str]
    home_address: Optional[str]
    years_of_experience: Optional[int]

class Doctor(DoctorBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


# Base Model for Admin
class AdminBase(BaseModel):
    phone_number: str
    date_of_birth: datetime
    gender: str
    country: str
    state_of_residence: str
    home_address: str
    hospital_id: Optional[int]
    hospital_admin_id: str
    admin_type: AdminType

class Admin(AdminBase):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)


class AdminUpdate(UserUpdate):
    phone_number:Optional[str]
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    country: Optional[str]
    state_of_residence: Optional[str]
    home_address: Optional[str]
    hospital_id: Optional[int]
    admin_type: Optional[AdminType]



# Base Model for Medical Record
class MedicalRecordBase(BaseModel):
    patient_id: int
    description: str
    record_date: datetime
    doctor_id: int

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordUpdate(BaseModel):
    patient_id: Optional[int]
    description: Optional[str]
    record_date: Optional[datetime]
    doctor_id: Optional[int]

class MedicalRecord(MedicalRecordBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


# Base Model for Patient
class PatientBase(BaseModel):
    phone_number: str
    date_of_birth: datetime
    gender: str
    country: str
    state_of_residence: str
    home_address: str
    hospital_card_id: str | None


class PatientCreate(PatientBase):
    pass

class PatientUpdate(UserUpdate):
    phone_number: Optional[str]
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    country: Optional[str]
    state_of_residence: Optional[str]
    home_address: Optional[str]
    hospital_card_id: Optional[str]

class Patient(PatientBase):
    id: int
    user_id: int
    medical_records: List[MedicalRecord]

    model_config = ConfigDict(from_attributes=True)

# Patient Response models
class PatientResponse(PatientBase):
    id: int
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



# Response Models
class DoctorResponse(BaseModel):
    role_id: str | None
    specialization: str
    years_of_experience: int
    is_available: bool = True
    user: UserBase
    hospital: HospitalBase

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
