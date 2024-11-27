from fastapi import FastAPI
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from app.database import engine, Base, SessionLocal
from app.routers import admins, auth, hospitals, medical_records, users, doctors, sign_up_link as link_gen, email_validation, department, appointment
from app.crud import sign_up_link as link
from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]

app = FastAPI()

# origins = [
#     "http://localhost",
#     "http://localhost:3000",
#     "https://queue-medix.vercel.app"
# ]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"],  
    allow_headers=["*"]
    # allow_headers=["*", "Authorization"], 
)



Base.metadata.create_all(bind=engine)

# Function to schedule the cleanup task


def cleanup_job():
    db: Session = SessionLocal()
    try:
        link.delete_expired_tokens(db)
    finally:
        db.close()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=cleanup_job, trigger="interval", hours=24)
    scheduler.start()
    return scheduler

# Use asynccontextmanager for lifespan management


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the scheduler during app startup
    scheduler = start_scheduler()

    yield  # Wait for the app to shut down

    # Shutdown the scheduler gracefully
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

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
