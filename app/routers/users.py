from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.crud import admins as admin_crud
from app.oauth2 import get_current_user
from sqlalchemy.orm import Session
import app.schemas as schemas
from app.crud import users as user_crud, doctors as doc_crud, patients as pat_crud
from app.database import get_db


router = APIRouter(
    tags=['User']
)


@router.get('/users', status_code=200, response_model=List[schemas.UserBase])
def get_all_users(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user), offset: int = 0, limit: int = 10):

    # Check if current user is an admin
    admin_user = admin_crud.get_admin_by_user_id(
        db=db, user_id=current_user.id)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    # Check if current user is super admin(endpoint is also accessible to super admins)
    if admin_user.admin_type != schemas.AdminType.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Accessible to only super admins")

    users = user_crud.get_users(db=db, offset=offset, limit=limit)
    return users


@router.get('/user/{user_id}', status_code=200)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    user = user_crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # # Check if current user is an admin
    # admin_user = admin_crud.get_admin_by_user_id(
    #     db=db, user_id=current_user.id)
    # if not admin_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    # # Check if current user is super admin(endpoint is only accessible to super admins)
    # if admin_user.admin_type != schemas.AdminType.SUPER_ADMIN:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                         detail="Accessible to only super admins")

    if user.role == schemas.UserRole.DOCTOR:
        doctor = doc_crud.get_doctor_by_user_id(db=db, user_id=user.id)
        return schemas.UserDoctorOut(
            id=user.id,
            doctor_id=doctor.id,
            email=user.email,
            role=user.role,
            first_name=user.first_name,
            last_name=user.last_name,
            specialization=doctor.specialization,
            hospital_id=doctor.hospital_id,
            is_active=user.is_active,
            created_at=user.created_at        
        )

    elif user.role == schemas.UserRole.PATIENT:
        patient = pat_crud.get_patient_by_user_id(db=db, user_id=user.id)
        return schemas.UserPatientOut(
            id=user.id,
            patient_id=patient.id,
            email=user.email,
            role=user.role,
            first_name=user.first_name,
            last_name = user.last_name,
            is_active=user.is_active,
            created_at=user.created_at
        )

    elif user.role == schemas.UserRole.ADMIN:
        admin = admin_crud.get_admin_by_user_id(db=db, user_id=user.id)
        return schemas.UserAdminOut(
            id=user.id,
            admin_id=admin.id,
            email=user.email,
            role=user.role,
            first_name=user.first_name,
            last_name=user.last_name,   
            admin_type=admin.admin_type,
            hospital_id=admin.hospital_id,
            is_active=user.is_active,
            created_at=user.created_at
        )

    raise HTTPException(status_code=400, detail="Invalid user role")
        


@router.get('/user/email/{email}', status_code=200, response_model=schemas.UserBase)
def get_user_by_email(email: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    user = user_crud.get_user_by_email(db=db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if current user is an admin
    admin_user = admin_crud.get_admin_by_user_id(
        db=db, user_id=current_user.id)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    # Check if current user is super admin(endpoint is only accessible to super admins)
    if admin_user.admin_type != schemas.AdminType.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Accessible to only super admins")
    return user

@router.delete("/users/{user_id}", status_code=200)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    user = user_crud.get_user(user_id=user_id, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check if current user is an admin
    admin_user = admin_crud.get_admin_by_user_id(
        db=db, user_id=current_user.id)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    # Check if current user is super admin(endpoint is only accessible to super admins)
    if admin_user.admin_type != schemas.AdminType.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Accessible to only super admins")
    
    user_crud.delete_user(db=db, user_id=user_id)

    return {"Message": "User successfully deleted"}

