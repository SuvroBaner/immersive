"""
This is the controller. It accepts your ImageJobRequest and returns the ImageJobResponse.

To start, it mocks the logic (generating a UUID and saying "Queued) so that we can test the interface.
"""

from turtle import mode
from fastapi import APIRouter, HTTPException, status
from app.schemas.job import ImageJobRequest, ImageJobResponse, JobStatus
from app.worker.tasks import process_image_job
from celery.result import AsyncResult
import uuid
from datetime import datetime
from app.worker.tasks import process_image_job

router = APIRouter()

@router.post("/jobs", response_model=ImageJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_image_job(payload: ImageJobRequest):
    """
    Submit a new image processing job.
    Returns a job ID immediately (non-blocking).
    """

    # 1. Generate a unique job ID
    job_id = str(uuid.uuid4())

    # 2. Send task to Celery Worker
    # .delay() is the magic method that pushes the task to Redis.
    # We convert the Pydantic model to a dict (JSON) so Celery can serialize it.
    #process_image_job.delay(job_id, payload.model_dump(mode = 'json'))

    process_image_job.apply_async(args=[job_id, payload.model_dump(mode='json')], task_id=job_id)

    # 3. Return the "ticket" to the user immediately
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
    Check Redis to see the real status of the background task.
    """

    # 1. Ask Redis about this Task ID
    task_result = AsyncResult(job_id)

    # 2. Map Celery Status to our API Status
    # Celery States: PENDING, STARTED, RETRY, FAILURE, SUCCESS
    celery_state = task_result.state

    api_status = JobStatus.PROCESSING
    result_url = None
    error_msg = None

    if celery_state == 'SUCCESS':
        api_status = JobStatus.COMPLETED
        # The return value from the worker function (the dict) is in .result
        output = task_result.result
        if isinstance(output, dict):
            result_url = output.get("result_url")

    elif celery_state == 'FAILURE':
        api_status = JobStatus.FAILED
        error_msg = str(task_result.result)

    elif celery_state == 'PENDING':
        api_status = JobStatus.QUEUED

    return ImageJobResponse(
        job_id = job_id,
        #status=JobStatus.PROCESSING, # Mocking that it's always working,
        status = api_status,
        created_at = datetime.now(), # ideally fetch this from db
        result_url = result_url,
        error = error_msg 
    )