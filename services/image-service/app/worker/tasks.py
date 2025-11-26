"""
Here, first we will create a "Mock" task. It won't do image processing yet; it will just sleep for 5 seconds
to simulate a heavy GPU load. This proves that your API returns immediately while the worker runs slowly.
"""

from app.worker.celery import celery_app
import time
from app.schemas.job import JobStatus
import logging

# Setup logger
logger = logging.getLogger(__name__)

@celery_app.task(bind = True, name = "process_image_job")
def process_image_job(self, job_id: str, job_config: dict):
    """
    Simulates a heavy GPU image processing task.
    """
    logger.info(f"🚀 Starting Job {job_id}")

    # 1. Update status to PROCESSING (Mocking DB update for now)
    # In real life, you'd update Redis or Postgres here

    # 2. Simulate Work (The "Heavy" Lifting)
    time.sleep(10) # sleep for 10 seconds

    logger.info(f"✅ Finished Job {job_id}")

    # 3. Return result -
    return{
        "job_id": job_id,
        "status": JobStatus.COMPLETED,
        "result_url": "https://example.com/processed_image.png"
    }