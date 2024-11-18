from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.crud.users import get_user_by_email
from app.oauth2 import authenticate_user, create_access_token, pwd_context
from app.database import get_db
from app import models, oauth2, schemas
from app.crud.hospitals import get_hospital_by_email, create_hospital
from app.utils import validate_hospital_password, validate_password

router = APIRouter(
    tags=['Authentication']
)


@router.post('/signup/hospital', status_code=201, response_model=schemas.HospitalBase)
def hospital_signup(payload: schemas.HospitalCreate, db: Session = Depends(get_db)):
    hospital = get_hospital_by_email(db, email=payload.email)
    if hospital:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Email already registered')

    # Validate password
    password_validation_result = validate_hospital_password(
        payload.password, payload.name, payload.owner_name)

    if password_validation_result != "Password is valid":
        raise HTTPException(status_code=400, detail=password_validation_result)

    hashed_password = pwd_context.hash(payload.password)
    payload.password = hashed_password
    return create_hospital(db=db, payload=payload)


@router.post("/signup/patient", status_code=201, response_model=schemas.PatientResponse)
def patient_signup(payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    # Check if the email already exists
    patient = get_user_by_email(db, email=payload.email)
    if patient:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate and hash password
    password_validation_result = validate_password(
        payload.password, payload.first_name, payload.last_name)

    if password_validation_result != "Password is valid":
        raise HTTPException(status_code=400, detail=password_validation_result)

    hashed_password = pwd_context.hash(payload.password)
    payload.password = hashed_password

    # Create user
    user = models.User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password=hashed_password,
        role=schemas.UserRole.PATIENT,
        phone_number=payload.phone_number,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        country=payload.country,
        state_of_residence=payload.state_of_residence,
        home_address=payload.home_address,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create patient record
    patient = models.Patient(
        user_id=user.id,
        hospital_card_id=payload.hospital_card_id
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


@router.post("/signup/doctor", status_code=201, response_model=schemas.DoctorResponse)
def doctor_signup(payload: schemas.DoctorCreate, db: Session = Depends(get_db)):
    # Check if the email already exists
    doctor = get_user_by_email(db, email=payload.email)
    if doctor:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate and hash password
    password_validation_result = validate_password(
        payload.password, payload.first_name, payload.last_name)

    if password_validation_result != "Password is valid":
        raise HTTPException(status_code=400, detail=password_validation_result)

    hashed_password = pwd_context.hash(payload.password)
    payload.password = hashed_password

    # Create user
    user = models.User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password=hashed_password,
        role=schemas.UserRole.DOCTOR,
        phone_number=payload.phone_number,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        country=payload.country,
        state_of_residence=payload.state_of_residence,
        home_address=payload.home_address,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create doctor record
    doctor = models.Doctor(
        user_id=user.id,
        hospital_id=payload.hospital_id,
        role_id=payload.role_id,
        specialization=payload.specialization,
        years_of_experience=payload.years_of_experience
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


@router.post("/signup/admin", status_code=201, response_model=schemas.AdminResponse)
def admin_signup(payload: schemas.AdminCreate, db: Session = Depends(get_db)):
    # Check if the email already exists
    admin = get_user_by_email(db, email=payload.email)
    if admin:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate and hash password
    password_validation_result = validate_password(
        payload.password, payload.first_name, payload.last_name)

    if password_validation_result != "Password is valid":
        raise HTTPException(status_code=400, detail=password_validation_result)

    hashed_password = pwd_context.hash(payload.password)
    payload.password = hashed_password

    # Create user
    user = models.User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password=hashed_password,
        role=schemas.UserRole.ADMIN,
        phone_number=payload.phone_number,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        country=payload.country,
        state_of_residence=payload.state_of_residence,
        home_address=payload.home_address,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create admin record
    admin = models.Admin(
        user_id=user.id,
        hospital_id=payload.hospital_id,
        hospital_admin_id=payload.hospital_admin_id,
        admin_type=payload.admin_type
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin


@router.post("/login", status_code=200)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(
        db, credential=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
