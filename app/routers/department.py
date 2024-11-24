from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.oauth2 import get_current_user
from sqlalchemy.orm import Session
from app import schemas, models
from app.crud import department as dpt_crud
from app.database import get_db

router = APIRouter(
    tags=['Departments']
)

"""
create department
list all available department
list department by id
update department
delete department
"""

@router.post('/departments/add', status_code=status.HTTP_201_CREATED, response_model=schemas.Department)
def add_department(payload: schemas.DepartmentCreate, db: Session = Depends(get_db), admin_user: models.Admin = Depends(get_current_user)):

    #authorization checks
    allowed_admins = {schemas.AdminType.DEPARTMENT_ADMIN, schemas.AdminType.HOSPITAL_ADMIN}
    if admin_user.admin_type not in allowed_admins:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to create department")
    
    department = dpt_crud.create_department(payload, db)
    return department

@router.get('/departments', status_code=status.HTTP_200_OK, response_model=List[schemas.Department])
def list_departments(skip: int = 0, limit: int = 10, search: Optional[str] = "", db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user), admin_user: models.Admin = Depends(get_current_user)):
    departments = dpt_crud.list_departments(skip, limit, search, db)
    
    return departments

@router.get('/departments/{department_id}', status_code=status.HTTP_200_OK, response_model=schemas.Department)
def get_department(department_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user), admin_user: models.Admin = Depends(get_current_user)):
    department = dpt_crud.get_department_by_id(department_id, db)
    
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    
    return department

@router.put('/departments/{department_id}', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Department)
def update_department(department_id: int, payload: schemas.DepartmentUpdate, db: Session = Depends(get_db), admin_user: models.Admin = Depends(get_current_user)):

    department = dpt_crud.get_department_by_id(department_id, db)

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )
    
    #authorization check
    allowed_users = {schemas.AdminType.HOSPITAL_ADMIN, schemas.AdminType.DEPARTMENT_ADMIN}

    if admin_user.admin_type not in allowed_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update department"
        )
    
    updated_department = dpt_crud.update_department(department_id, payload, db)
    return updated_department

@router.delete('/departments/{department_id}', status_code=status.HTTP_202_ACCEPTED)
def delete_department(department_id: int, db: Session = Depends(get_db), admin_user: models.Admin = Depends(get_current_user)):

    department = dpt_crud.get_department_by_id(department_id, db)
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )
    
    #authorization check
    allowed_admins = {schemas.AdminType.SUPER_ADMIN, schemas.AdminType.HOSPITAL_ADMIN}
    if admin_user.admin_type not in allowed_admins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to delete department"
        )
    
    dpt_crud.delete_department(department_id, db)

    return {"message": "Department deleted successfully!"}