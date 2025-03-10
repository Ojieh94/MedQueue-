from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import Message
from app.database import get_db

router = APIRouter(
    tags=["Message Bot"]
)

@router.get("/chat/history/{user_id}/{other_user_id}")
def get_chat_history(user_id: int, other_user_id: int, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp).all()
    
    return messages

"""
We’ll use Redis and Celery for notifications.
check celery_config.py file, tasks.py file
"""
