from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.crud.users import get_user_by_email
# from app.crud.password_reset import update_password, update_hospital_password
from app.oauth2 import authenticate_user, create_access_token, get_current_user, hash_password
from app.database import get_db
from app import models, schemas
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

    hashed_password = hash_password(payload.password)
    payload.password = hashed_password
    return create_hospital(db=db, payload=payload)


@router.post("/signup/patient", status_code=201, response_model=schemas.PatientResponse)
def patient_signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if the email already exists
    patient = get_user_by_email(db, email=payload.email)
    if patient:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate and hash password
    password_validation_result = validate_password(
        payload.password, payload.first_name, payload.last_name)

    if password_validation_result != "Password is valid":
        raise HTTPException(status_code=400, detail=password_validation_result)

    hashed_password = hash_password(payload.password)
    payload.password = hashed_password

    # Create user
    user = models.User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password=hashed_password,
        role=schemas.UserRole.PATIENT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    dummy_patient_data = schemas.PatientCreate()
    # Create patient record
    patient = models.Patient(
        **dummy_patient_data.model_dump(),
        user_id=user.id
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


##### DOCTOR SIGNUP SESSION #####
@router.post("/signup/doctor", status_code=201, response_model=schemas.DoctorResponse)
def doctor_signup(payload: schemas.DoctorUserCreate, token: str, db: Session = Depends(get_db)):

    # Validate the signup token
    signup_link = db.query(models.SignupLink).filter(models.SignupLink.token == token).first()
    if not signup_link:
        raise HTTPException(status_code=400, detail="Invalid signup token")
    
    if signup_link.is_used:
        raise HTTPException(status_code=400, detail="Signup token already used")

    # Check if token is expired (optional)
    if signup_link.created_at < datetime.now() - timedelta(hours=24):
        raise HTTPException(status_code=400, detail="Signup token has expired")

    # Check if the email associated with the token matches the payload
    if signup_link.email != payload.email:
        raise HTTPException(status_code=400, detail="Token email does not match")

    # Mark the token as used
    signup_link.is_used = True
    db.commit()

    # Check if the email already exists
    doctor = get_user_by_email(db, email=payload.email)
    if doctor:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate and hash password
    password_validation_result = validate_password(
        payload.password, payload.first_name, payload.last_name)

    if password_validation_result != "Password is valid":
        raise HTTPException(status_code=400, detail=password_validation_result)

    hashed_password = hash_password(payload.password)
    payload.password = hashed_password

    # Create user
    user = models.User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password=hashed_password,
        role=schemas.UserRole.DOCTOR,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    doctor_dummy_data = schemas.DoctorCreate()
    # Create Doctor record
    doctor = models.Doctor(
        **doctor_dummy_data.model_dump(),
        user_id=user.id,
        hospital_id=payload.hospital_id
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


### ADMIN SESSION
@router.post("/signup/admin", status_code=201, response_model=schemas.AdminBase)
def admin_signup(payload: schemas.UserCreate, token: str, db: Session = Depends(get_db)):

    # Validate the signup token
    signup_link = db.query(models.SignupLink).filter(models.SignupLink.token == token).first()
    if not signup_link:
        raise HTTPException(status_code=400, detail="Invalid signup token")
    
    if signup_link.is_used:
        raise HTTPException(status_code=400, detail="Signup token already used")

    # Check if token is expired (optional)
    if signup_link.created_at < datetime.now() - timedelta(hours=24):
        raise HTTPException(status_code=400, detail="Signup token has expired")

    # Check if the email associated with the token matches the payload
    if signup_link.email != payload.email:
        raise HTTPException(status_code=400, detail="Token email does not match")

    # Mark the token as used
    signup_link.is_used = True
    db.commit()

    # Check if the email already exists
    admin = get_user_by_email(db, email=payload.email)
    if admin:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate and hash password
    password_validation_result = validate_password(
        payload.password, payload.first_name, payload.last_name)

    if password_validation_result != "Password is valid":
        raise HTTPException(status_code=400, detail=password_validation_result)

    hashed_password = hash_password(payload.password)
    payload.password = hashed_password

    # Create user
    user = models.User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password=hashed_password,
        role=schemas.UserRole.ADMIN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    dummy_admin_payload = schemas.AdminCreate()
    # Create admin record
    admin = models.Admin(
        **dummy_admin_payload.model_dump(),
        user_id=user.id
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin


#### LOGIN ENDPOINT
@router.post("/login", status_code=200)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(
        db, email=form_data.username.lower(), password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = {"sub": user.email, "user_id": user.id}
    if hasattr(user, 'role'):
        token_data["user_role"] = user.role

    access_token = create_access_token(data=token_data)

    return {"access_token": access_token, "token_type": "bearer"}



