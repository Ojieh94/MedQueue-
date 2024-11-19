from fastapi import FastAPI, Lifespan
from app.database import engine, Base
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from app.routers import auth, hospitals, users, sign_up_link as link_gen
from app.crud import sign_up_link as link
from app.database import SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Function to schedule the cleanup task
def schedule_cleanup():
    def cleanup_job():
        db: Session = SessionLocal()
        try:
            link.delete_expired_tokens(db)
        finally:
            db.close()

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=cleanup_job, trigger="interval", hours=24)
    scheduler.start()
    return scheduler

# Call this function during app startup
@app.lifespan
def app_lifespan(app: FastAPI) -> Lifespan:
    # Start the scheduler
    scheduler = schedule_cleanup()

    # Startup phase
    yield

    # Shutdown phase
    scheduler.shutdown()


app.include_router(link_gen.router)
app.include_router(auth.router)
app.include_router(hospitals.router)
app.include_router(users.router)


@app.get('/')
def root():
    return {'message': 'Queue_Medix API!'}
