from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.schema import UserRole, AppointmentStatus
from app.database import Base

# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    phone_number = Column(String(15), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String, nullable=False)
    country = Column(String, nullable=False)
    state_of_residence = Column(String, nullable=False)
    home_address = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    hospital = relationship("Hospital", back_populates="admin", uselist=False)
    doctor = relationship("Doctor", back_populates="user", uselist=False)
    patient = relationship("Patient", back_populates="user", uselist=False)
    appointments = relationship("Appointment", back_populates="user")

# Hospital Model
class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String(255), nullable=False)
    phone_number = Column(String(15), nullable=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    admin = relationship("User", back_populates="hospital")
    appointments = relationship("Appointment", back_populates="hospital")

# Doctor Model
class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    role_id = Column(String(20), nullable=True)
    specialization = Column(String, nullable=True)
    is_available= Column(Boolean, default=True, nullable=False)
    years_of_experience = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="doctor")
    hospital = relationship("Hospital", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")
    medical_records = relationship("MedicalRecord", back_populates="doctor")

# Patient Model
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hospital_card_id = Column(String(20), nullable=True)
    
    
    # Relationships
    medical_records = relationship("MedicalRecord", back_populates="patient")
    user = relationship("User", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")

# Appointment Model
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    appointment_note = Column(Text, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    hospital = relationship("Hospital", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    user = relationship("User", back_populates="appointments")

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
