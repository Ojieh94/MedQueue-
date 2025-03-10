import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Load Redis URL from environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://:localpassword@redis:6379/0")

# Initialize Celery
celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)
