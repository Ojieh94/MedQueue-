from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.oauth2 import get_current_user
from sqlalchemy.orm import Session
from app import schemas, models
from app.crud import hospitals as hospital_crud, admins as admin_crud
from app.database import get_db

router = APIRouter(
    tags=['Hospitals']
)

"""
list hospitals
get a single hospital by name
update hospital details
delete/remove hospital
"""

@router.get("/hospitals", status_code=status.HTTP_200_OK, response_model=List[schemas.Hospital])
def get_all_hospitals(db: Session = Depends(get_db), offset: int = 0, limit: int = 10, search: Optional[str] = "Hospital name"):
    hospitals = hospital_crud.get_hospitals(
        db,
        offset=offset,
        limit=limit,
        search=search
    )
    return hospitals

@router.get('/hospitals/{hospital_id}', status_code=status.HTTP_200_OK, response_model=schemas.Hospital)
def get_single_hospital(hospital_id: int, db: Session = Depends(get_db)):

    hospital = hospital_crud.get_hospital_id(hospital_id, db)
    if not hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    
    return hospital

@router.put('/hospitals/{hospital_id}', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Hospital)
def update_hospital(hospital_id: int, payload: schemas.HospitalUpdate, db: Session = Depends(get_db), current_user: models.Hospital = Depends(get_current_user), admin_user: models.User = Depends(get_current_user)):

    #hospital availability check
    hospital = hospital_crud.get_hospital_id(hospital_id, db)
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found"
        )
    
    # authorization check
    user = admin_crud.get_admin_by_user_id(db, admin_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found"
        )
    
    allowed_admins = {schemas.AdminType.SUPER_ADMIN, schemas.AdminType.HOSPITAL_ADMIN}

    # Check if current user is an admin(endpoint is only accessible to super admins and hospital admins)

    is_authorized = (user.admin_type in allowed_admins or current_user.id == hospital.id)

    if not is_authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized the access this resource."
        )
    
    #update hospital
    updated_hospital = hospital_crud.update_hospital(hospital_id, payload, db)
    return updated_hospital

@router.delete('/hospitals/{hospital_id}', status_code=status.HTTP_202_ACCEPTED)
def delete_hospital(hospital_id: int, db: Session = Depends(get_db), current_user: models.Hospital = Depends(get_current_user), admin_user: models.User = Depends(get_current_user)):

    #hospital availability check
    hospital = hospital_crud.get_hospital_id(hospital_id, db)
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found"
        )
    
    # authorization check
    user = admin_crud.get_admin_by_user_id(db, admin_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found"
        )
    
    allowed_admins = {schemas.AdminType.SUPER_ADMIN, schemas.AdminType.HOSPITAL_ADMIN}

    # Check if current user is an admin(endpoint is only accessible to super admins and hospital admins)

    is_authorized = (user.admin_type in allowed_admins or current_user.id == hospital.id)

    if not is_authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized the access this resource."
        )
    
    hospital_crud.delete_hospital(hospital_id, db)

    return{"message": "Hospital deleted successfully!"}