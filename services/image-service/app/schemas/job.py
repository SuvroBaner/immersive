"""
The shared Contract (Schemas)
Shared unerstanding of what a "job" looks like. This allows the API to validate input and the worker
to know exactly what to process without code duplication.
"""

from optparse import Option
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from typing import List, Optional
from datetime import datetime

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ImageJobRequest(BaseModel):
    image_url: HttpUrl = Field(..., description="The URL of the image to process")
    # The user can choose specific strategies to apply
    steps: List[str] = Field(default=["perspective", "crop", "shadows", "upscale"])
    webhook_url: Optional[HttpUrl] = None

class ImageJobResponse(BaseModel):
    job_id: str = Field(..., description="The unique identifier for the job")
    status: JobStatus
    created_at: datetime

    # OUTPUTS (populated when status is COMPLETED)
    result_url: Optional[HttpUrl] = None

    # ERRORS (populated when status is FAILED)
    error: Optional[str] = None

    # METADATA
    queue_position: Optional[int] = None