"""
This is the controller. It accepts your ImageJobRequest and returns the ImageJobResponse.

To start, it mocks the logic (generating a UUID and saying "Queued) so that we can test the interface.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.job import ImageJobRequest, ImageJobResponse, JobStatus
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/jobs", response_model=ImageJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_image_job(payload: ImageJobRequest):
    """
    Submit a new image processing job.
    Returns a job ID immediately (non-blocking).
    """

    # 1. Generate a unique job ID
    job_id = str(uuid.uuid4())

    # 2. TODO: Send task to Celery queue (we will do this in the next step)
    # task = process_image.delay(job_id, payload.model_dump())

    # 3. Return the "ticket" to the user
    return ImageJobResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        created_at=datetime.now(),
        queue_position=1 # TODO: Mock value for now
    )

@router.get("/jobs/{job_id}", response_model=ImageJobResponse)
async def get_job_status(job_id: str):
    """
    Poll the status of a specific job.
    """

    # TODO: Fetch the real status from Redis

    return ImageJobResponse(
        job_id=job_id,
        status=JobStatus.PROCESSING, # Mocking that it's always working
        created_at=datetime.now()
    )