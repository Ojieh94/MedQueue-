from fastapi import FastAPI
from sqlalchemy.orm import Session
from app.database import engine, Base

from app.routers import auth, hospitals, users

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(hospitals.router)
app.include_router(users.router)


@app.get('/')
def root():
    return {'message': 'Queue_Medix API!'}
