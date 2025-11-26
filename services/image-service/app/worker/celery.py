"""
This is the heart of the async system. It tells the worker where to look for jobs.
"""

from time import timezone
from celery import Celery
from app.core.config import settings

# Initialize the Celery App
celery_app = Celery(
    "image_worker",
    broker = settings.CELERY_BROKER_URL,
    backend = settings.CELERY_RESULT_BACKEND,
    # Auto-discover tasks in the "app.worker.tasks" module
    include = ["app.worker.tasks"]
)

# Optional: Configure Celery for better robustness
celery_app.conf.update(
    task_serializer = "json",
    accept_content = ["json"],
    result_serializer = "json",
    timezone = "UTC",
    enable_utc = True,
)