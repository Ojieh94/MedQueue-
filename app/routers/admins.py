from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.oauth2 import get_current_user
from sqlalchemy.orm import Session
from app import schemas
from app.crud import doctors as doctor_crud, admins as admin_crud
from app.database import get_db

router = APIRouter(
    tags=['Admins']
)


@router.get('/admins', status_code=200, response_model=List[schemas.AdminResponse])
def get_all_admins(db: Session = Depends(get_db), current_user: schemas.Admin = Depends(get_current_user), offset: int = 0, limit: int = 10):
    if current_user.admin_type == schemas.AdminType.DEPARTMENT_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Super Admin and Hospital Admin privileges only")
    
    admins = admin_crud.get_admins(db=db, offset=offset, limit=limit)

    return admins

@router.get('/admin/{admin_id}', status_code=200, response_model=schemas.AdminResponse)
def get_admin_by_id(admin_id: int, db: Session = Depends(get_db), current_user: schemas.Admin = Depends(get_current_user)):
    admin = admin_crud.get_admin(db=db, admin_id=admin_id)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
     
    if current_user.admin_type == schemas.AdminType.DEPARTMENT_ADMIN:
        if current_user.id != admin_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Super Admin and Hospital Admin can delete other admins")
        
    if current_user.admin_type == schemas.AdminType.HOSPITAL_ADMIN:
        if admin.hospital_id != current_user.hospital_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view admins for your hospital")
        
    return admin
    

@router.put('/admins/{admin_id}', status_code=200, response_model=schemas.AdminResponse)
def update_admin(admin_id: int, admin_payload: schemas.AdminUpdate, db: Session = Depends(get_db), current_user: schemas.Admin = Depends(get_current_user)):
    admin = admin_crud.get_admin(db=db, admin_id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    
    if current_user.id != admin_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized to perform this action")
    
    admin = admin_crud.update_admin(db=db, admin_id=admin_id, admin_payload=admin_payload)

    return admin


@router.delete('/admins/{admin_id}', status_code=200)
def delete_admin(admin_id: int, db: Session = Depends(get_db), current_user: schemas.Admin = Depends(get_current_user)):
    admin = admin_crud.get_admin(db=db, admin_id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    
    if current_user.admin_type == schemas.AdminType.DEPARTMENT_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Super Admin and Hospital Admin privileges only")
    
    if current_user.admin_type == schemas.AdminType.HOSPITAL_ADMIN:
        if current_user.hospital_id != admin.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete admins that belong to your hospital")
      
    admin_crud.delete_admin(db=db, admin_id=admin_id)

    return {"message": "Admin deleted successfully"}

