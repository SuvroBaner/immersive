"""
    This files is the "glue". It creates the FastAPI app and the API endpoint, then calls your core.py logic.
"""

from fastapi import FastAPI, HTTPException
import time

from .models import ContentRequest, ContentResponse
from .core import generate_content_from_gemini

app = FastAPI(
    title = "Immersive Text Generator API",
    description = "Generates product description using multimodal AI.",
    version = "1.0.0"
)

@app.get("/", tags = ["Health Chack"])
def read_root():
    """ A simple health check endpoint."""
    return {"status": "ok", "service": "text-service"}

@app.post("/v1/content/generate",
          response_model = ContentResponse,
          tags = ["Content Generation"])

async def create_product_content(request: ContentRequest):
    """
    Takes a product image URL and seller inputs, and returns AI-generated marketing content.
    """
    start_time = time.time()

    try:
        generated_data, model_name = await generate_content_from_gemini(request)

        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        response = ContentResponse(
            generated_content = generated_data,
            ai_model_used = model_name,
            latency_ms = latency_ms
        )

        return response

    except Exception as e:
        # In a real app, you'd have more specific error handling
        print(f"An error occurred: {e}")
        raise HTTPException(
            status_code = 500,
            detail = f"An internal server error occurred: {e}"
        )