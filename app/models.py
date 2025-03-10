from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.schemas import AdminType, OwnershipType, UserRole, AppointmentStatus
from app.database import Base

# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    doctor = relationship("Doctor", back_populates="user",
                          cascade="all, delete", uselist=False)
    patient = relationship("Patient", back_populates="user",
                           cascade="all, delete", uselist=False)
    admin = relationship("Admin", back_populates="user",
                         cascade="all, delete", uselist=False)
    
# Hospital Model
class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String(255), nullable=False)
    state = Column(String(20), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    website = Column(String)
    license_number = Column(String, nullable=False)
    phone_number = Column(String(15), nullable=True)
    registration_number = Column(String, nullable=False)
    ownership_type = Column(Enum(OwnershipType), nullable=False)
    owner_name = Column(String)
    accredited = Column(Boolean, default=False)

    # Relationships
    admin = relationship("Admin", back_populates="hospital")
    appointments = relationship("Appointment", back_populates="hospital")
    departments = relationship("Department", back_populates="hospital")
    doctor = relationship("Doctor", back_populates="hospital")


# Doctor Model
class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    phone_number = Column(String(15), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String, nullable=False)
    country = Column(String, nullable=False)
    state_of_residence = Column(String, nullable=False)
    home_address = Column(String(255), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    role_id = Column(String(20), nullable=True)
    specialization = Column(String, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    years_of_experience = Column(Integer, nullable=False)

    # Relationships
    user = relationship("User", back_populates="doctor")
    hospital = relationship("Hospital", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")
    medical_records = relationship("MedicalRecord", back_populates="doctor")


# Patient Model
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    hospital_card_id = Column(String(20), nullable=True)
    phone_number = Column(String(15), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String, nullable=False)
    country = Column(String, nullable=False)
    state_of_residence = Column(String, nullable=False)
    home_address = Column(String(255), nullable=False)

    # Relationships
    medical_records = relationship("MedicalRecord", back_populates="patient")
    user = relationship("User", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")


# Admin Model
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    hospital_admin_id = Column(String, nullable=False)
    admin_type = Column(Enum(AdminType), nullable=False)
    phone_number = Column(String(15), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String, nullable=False)
    country = Column(String, nullable=False)
    state_of_residence = Column(String, nullable=False)
    home_address = Column(String(255), nullable=False)

    # Relationships
    user = relationship("User", back_populates="admin")
    hospital = relationship("Hospital", back_populates="admin")

# Appointment Model


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    appointment_note = Column(Text, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus),
                    default=AppointmentStatus.PENDING, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    hospital = relationship("Hospital", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")


# Medical Record Model
class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    description = Column(Text, nullable=False)
    record_date = Column(DateTime, server_default=func.now())
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)

    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")

# Hospital Departments
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    name = Column(String, unique=True, index=True, nullable=False)

    # Relationships
    hospital = relationship("Hospital", back_populates="departments")

# Signup Link - Table to store generated tokens for admins/doctors signup links.
class SignupLink(Base):
    __tablename__ = "signup_links"
    token = Column(String, primary_key=True, unique=True, index=True)
    email = Column(String, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    message_text = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now())

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
