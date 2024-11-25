from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.oauth2 import get_current_user
from sqlalchemy.orm import Session
from app import schemas
from app.crud import doctors as doctor_crud
from app.database import get_db

router = APIRouter(
    tags=['Doctors']
)

@router.get('/doctors', status_code=200, response_model=List[schemas.DoctorResponse])
def get_all_doctors(db: Session = Depends(get_db), name: str = None, specialization: str = None, current_user: schemas.User = Depends(get_current_user), offset: int = 0, limit: int = 10):
    doctors = doctor_crud.get_doctors(db=db, name=name, specialization=specialization, offset=offset, limit=limit)

    return doctors

