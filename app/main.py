from fastapi import FastAPI
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from app.database import engine, Base, SessionLocal
from app.routers import (
    admins, auth, hospitals, medical_records, users, doctors,
    sign_up_link as link_gen, email_validation, department, appointment
)
from app.crud import sign_up_link as link
from fastapi.middleware.cors import CORSMiddleware


# Use asynccontextmanager for lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the scheduler during app startup
    scheduler = start_scheduler()
    yield  # Wait for the app to shut down
    # Shutdown the scheduler gracefully
    scheduler.shutdown()


# Initialize the FastAPI application with lifespan
app = FastAPI(lifespan=lifespan)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://queue-medix.vercel.app"],  # Deployed frontend
    allow_origin_regex=r"http://localhost:\d+",  # Local frontend with dynamic ports
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Database initialization
Base.metadata.create_all(bind=engine)


# Function to schedule the cleanup task
def cleanup_job():
    db: Session = SessionLocal()
    try:
        link.delete_expired_tokens(db)
    finally:
        db.close()


# Start the scheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=cleanup_job, trigger="interval", hours=24)
    scheduler.start()
    return scheduler


# Include routers
app.include_router(email_validation.router)
app.include_router(link_gen.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(hospitals.router)
app.include_router(doctors.router)
app.include_router(department.router)
app.include_router(appointment.router)
app.include_router(admins.router)
app.include_router(medical_records.router)


@app.get('/')
def root():
    return {'message': 'Queue_Medix API!'}
