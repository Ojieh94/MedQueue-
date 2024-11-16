from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.oauth2 import get_current_user
from sqlalchemy.orm import Session
import app.schemas as schemas
from app.crud.hospitals import get_hospitals
from app.database import get_db

router = APIRouter(
    tags=['Hospital']
)


@router.get("/hospitals", status_code=200, response_model=List[schemas.HospitalBase])
def get_all_hospitals(db: Session = Depends(get_db), offset: int = 0, limit: int = 10):
    hospitals = get_hospitals(
        db,
        offset=offset,
        limit=limit
    )
    return hospitals
