from sqlalchemy.orm import Session
from typing import Optional, List
from app import models, schemas

"""
create department
list all available department
list department by id
update department
delete department
"""

def create_department(payload: schemas.DepartmentCreate, db: Session) -> models.Department:
    department = models.Department(**payload.model_dump())

    db.add(department)
    db.commit()
    db.refresh(department)
    return department

def list_departments(skip: int, limit: int, search: Optional[str], db: Session) -> List[models.Department]:
    query =  db.query(models.Department)
    
    if search:
        query = query.filter(models.Department.name.contains(search))
    
    return query.offset(skip).limit(limit).all()

def get_department_by_id(department_id: int, db: Session) -> models.Department:
    return db.query(models.Department).filter(models.Department.id == department_id).first()

def update_department(department_id: int, payload: schemas.DepartmentUpdate, db: Session) -> models.Department:
    department = get_department_by_id(department_id, db)

    if not department:
        return False
    
    updated_data = payload.model_dump(exclude_unset=True)

    for k, v in updated_data.items():
        setattr(department, k, v)
        
    db.commit()
    db.refresh(department)
    return department

def delete_department(department_id: int, db: Session):
    department = get_department_by_id(department_id, db)
    
    if not department:
        return False
    
    db.delete(department)
    db.commit()