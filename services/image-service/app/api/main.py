"""
Create the App Entrypoint.

This is the glue that makes it runnable.
"""

from fastapi import FastAPI
from app.api.routes import router as job_router

app = FastAPI(
    title="Immersive Image Service",
    description="Async GPU Pipeline for Professional Image Correction",
    version="0.1.0"
)

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "image-service"}

# Resgiter the Jobs Router
app.include_router(job_router, prefix="/v1", tags=["Image Jobs"])