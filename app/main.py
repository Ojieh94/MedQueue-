import os
import redis
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, Depends, WebSocketDisconnect
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from datetime import datetime

# Import database and models
from app.database import engine, Base, SessionLocal, get_db
from app.models import Message
from app.websocket_manager import manager
from tasks import send_notification

# Import routers
from app.routers import (
    admins, auth, hospitals, medical_records, queue_sys, users, doctors,
    sign_up_link as link_gen, email_validation, department, appointment, patients, password_reset, message
)
from app.crud import sign_up_link as link
from app.crud import password_reset as reset_token

# Import middleware
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Function to schedule the cleanup task


def cleanup_job():
    db: Session = SessionLocal()
    try:
        link.delete_expired_tokens(db)
        reset_token.delete_expired_tokens(db)
    except Exception as e:
        print(f"Error deleting tokens from database: {e}")
    finally:
        db.close()

# Start the scheduler


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=cleanup_job, trigger="interval", hours=24)
    scheduler.start()
    return scheduler

# Use asynccontextmanager for lifespan management


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()

# Initialize the FastAPI application
app = FastAPI(lifespan=lifespan)

# Add origins
origins = [
    "http://localhost",
    "https://queue-medix.vercel.app",
    "https://www.queuemedix.com",
    "https://queuemedix.com",
]

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Read Redis credentials from environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


@app.get("/redis-test")
def test_redis():
    redis_client.set("message", "Hello from Redis!")
    return {"redis_message": redis_client.get("message")}

# WebSocket for chat functionality


@app.websocket("/chat/{sender_id}/{receiver_id}")
async def chat_endpoint(websocket: WebSocket, sender_id: int, receiver_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            # Store message in database
            message = Message(sender_id=sender_id, receiver_id=receiver_id,
                              message_text=data, timestamp=datetime.now())
            db.add(message)
            db.commit()

            # Send the message to all connected clients
            await manager.send_message(f"User {sender_id}: {data}")

            # Trigger notification in the background
            send_notification.delay(receiver_id, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Database initialization
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(message.router)
app.include_router(password_reset.router)
app.include_router(email_validation.router)
app.include_router(link_gen.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(hospitals.router)
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(department.router)
app.include_router(appointment.router)
app.include_router(admins.router)
app.include_router(medical_records.router)
app.include_router(queue_sys.router)


@app.get('/')
def root():
    return {'message': 'Queue_Medix API!'}
