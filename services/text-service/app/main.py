"""
    This files is the "glue". It creates the FastAPI app and the API endpoint, 
    then delegates to the appropriate provider through the factory.
"""

from unicodedata import category
from fastapi import FastAPI, HTTPException, Depends, Query
import time
from typing import Optional

from .models import ContentRequest, ContentResponse
from .core.factory import ModelProviderFactory
from .config import get_settings, Settings

app = FastAPI(
    title = "Immersive Text Generator API",
    description = "Generates product description using multimodal AI with multiple provider support",
    version = "1.0.0"
)

@app.get("/", tags = ["Health Chack"])
def read_root():
    """ A simple health check endpoint."""
    return {"status": "ok", "service": "text-service"}

@app.post("/v1/content/generate",
          response_model = ContentResponse,
          tags = ["Content Generation"])
async def create_product_content(
    request: ContentRequest,
    provider: Optional[str] = Query(None, description = "AI provider to use (gemini, openai, huggingface)"),
    settings: Settings = Depends(get_settings)):
    
    """
    Takes a product image URL and seller inputs, and returns AI-generated marketing content.

    - **request**: The content request containing image URL and seller inputs
    - **provider**: (Optional) The AI provider to use. If not specified, the default provider will be used.
    """
    start_time = time.time()

    try:
        # use specified provider or default from settings
        provider_name = provider or settings.default_provider

        # Get provider instance from factory. The factory will resolve API keys
        # based on provider and settings (including environment variables).
        ai_provider = ModelProviderFactory.get_provider(
            provider_name = provider_name,
            mock_mode = settings.mock_mode,
            settings = settings,
            category = request.seller_inputs.category if hasattr(request.seller_inputs, "category") else None,
            platform = request.config.target_platform if hasattr(request.config, "target_platform") else None
        )
        
        # Generate content using the selected provider
        generated_data, model_name = await ai_provider.generate_content(request)

        # Calculate latency
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        # Determine the actual provider used (mock if mock_mode is enabled)
        actual_provider = "mock" if settings.mock_mode else provider_name

        # Create response
        response = ContentResponse(
            generated_content = generated_data,
            ai_model_used = model_name,
            latency_ms = latency_ms,
            metadata = {
                "provider": actual_provider,
                "model": model_name
            }
        )

        return response

    except ValueError as e:
        # Handle provider-specific errors (like unsupported provider or missing API key)
        # The error message from providers already includes helpful suggestions
        raise HTTPException(
            status_code = 400,
            detail = str(e)
        )
    
    except Exception as e:
        # In a real app, you'd have more specific error handling
        print(f"An error occurred: {e}")
        raise HTTPException(
            status_code = 500,
            detail = f"An internal server error occurred: {e}"
        )

@app.get("/v1/providers", tags = ["Configuration"])
def list_providers(settings: Settings = Depends(get_settings)):
    """
    Returns a list of available AI providers and default provider
    """

    try:
        # Get list of registered providers from the factory
        providers = ModelProviderFactory.list_providers()
        
        # Check API key status (without exposing the actual key)
        import os
        api_key_in_settings = bool(getattr(settings, "GOOGLE_API_KEY", None) or getattr(settings, "google_api_key", None))
        api_key_in_env = bool(os.environ.get("GOOGLE_API_KEY"))

        return {
            "default_provider": settings.default_provider,
            "available_providers": providers,
            "provider_settings": settings.provider_settings,
            "mock_mode": settings.mock_mode,
            "api_key_configured": api_key_in_settings or api_key_in_env,
            "note": "When mock_mode is True, all requests will use MockProvider regardless of provider selection"
        }

    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = f"Error retrieving provider information: {str(e)}"
        )