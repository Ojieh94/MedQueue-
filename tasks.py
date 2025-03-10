from app.celery_config import celery_app

@celery_app.task
def send_notification(user_id: int, message: str):
    print(f"New message for User {user_id}: {message}")