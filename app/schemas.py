from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from typing import List, Optional

# Custom EmailStr to ensure case insensitivity


class CaseInsensitiveEmailStr(EmailStr):
    @classmethod
    def validate(cls, value: str) -> str:
        value = super().validate(value)
        return value.lower()

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
    email: CaseInsensitiveEmailStr
    role: UserRole


class UserCreate(UserBase):
    password: str


class DoctorUserCreate(UserBase):
    hospital_id: int
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[CaseInsensitiveEmailStr]


class User(UserBase):
    id: int
    is_active: bool = False
    created_at: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)


# Base Model for Hospital


class HospitalBase(BaseModel):
    name: str
    address: str
    state: str
    email: CaseInsensitiveEmailStr
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
    email: Optional[CaseInsensitiveEmailStr]
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
    role_id: Optional[str] = ""
    specialization: str = ""
    phone_number: str = ""
    date_of_birth: datetime = datetime.now()
    gender: str = ""
    country: str = ""
    state_of_residence: str = ""
    home_address: str = ""
    years_of_experience: int = 0
    is_available: bool = True


class DoctorCreate(DoctorBase):
    pass


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


class DoctorOut(BaseModel):
    id: int
    user: UserOut

    model_config = ConfigDict(from_attributes=True)


class HospitalDoctors(DoctorOut):
    is_available: bool
    hospital_id: int

    model_config = ConfigDict(from_attributes=True)

# Base Model for Admin


class AdminBase(BaseModel):
    phone_number: str = ""
    date_of_birth: datetime = datetime.now()
    gender: str = ""
    country: str = ""
    state_of_residence: str = ""
    home_address: str = ""
    hospital_id: Optional[int] = None
    hospital_admin_id: str = ""
    admin_type: AdminType = AdminType.HOSPITAL_ADMIN


class AdminCreate(AdminBase):
    pass


class Admin(AdminBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class AdminUpdate(UserUpdate):
    phone_number: Optional[str]
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
    phone_number: str = "Phone Number"
    date_of_birth: datetime = datetime.now()
    gender: str = "Gender"
    country: str = "Country"
    state_of_residence: str = "Avenue"
    home_address: str = "Home Address"
    hospital_card_id: str = ""


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


class PatientResponse(PatientBase):
    id: int
    user: UserBase
    medical_records: List[MedicalRecord]

    model_config = ConfigDict(from_attributes=True)


class PatientOut(PatientBase):
    user: UserBase

    model_config = ConfigDict(from_attributes=True)

# Base Model for Appointment


class AppointmentCreate(BaseModel):
    appointment_note: str
    hospital_id: int
    scheduled_time: datetime = Field(default_factory=datetime.now) 


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class Appointment(BaseModel):
    id: int
    appointment_note: str
    scheduled_time: datetime
    patient: PatientResponse
    hospital: Hospital
    doctor: DoctorOut | None
    status: AppointmentStatus = AppointmentStatus.PENDING

    model_config = ConfigDict(from_attributes=True)


class AssignDoctor(BaseModel):
    doctor_id: int

# Response Models


class DoctorResponse(DoctorBase):
    id: int
    user: UserBase
    hospital: HospitalBase

    model_config = ConfigDict(from_attributes=True)


class AdminResponse(BaseModel):
    admin_type: AdminType
    user: UserBase

    model_config = ConfigDict(from_attributes=True)


class EmailValidationRequest(BaseModel):
    email: CaseInsensitiveEmailStr


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

# ## schema for password rest

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    new_password: str
    confirm_password: str

# Schema for websocket


class AppointmentQueueOut(BaseModel):
    id: int
    patient: dict
    time: str
    status: str


# Schema for user outputs

class UserDoctorOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    doctor_detials: DoctorResponse


class UserPatientOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    doctor_detials: PatientResponse


class UserAdminOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    doctor_detials: AdminResponse
