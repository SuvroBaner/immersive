"""
To store the Redis connection URL. 
We use pydantic-settings so we can easily swap the Redis URL in production later.
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Default to localhost for Development
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

settings = Settings()