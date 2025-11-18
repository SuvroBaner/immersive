"""
This file is the "glue". It creates the FastAPI app and the API endpoint, 
then delegates to the appropriate provider through the factory.
"""

from fastapi import FastAPI, HTTPException, Depends, Query
import time
from typing import Optional, Dict, Any

from .models import ContentRequest, ContentResponse
from .core.factory import ModelProviderFactory
from .config import get_settings, Settings

app = FastAPI(
    title="Immersive Text Generator API",
    description="Generates product descriptions using multimodal AI with multiple provider support.",
    version="1.0.0"
)

@app.get("/", tags=["Health Check"])
def read_root():
    """ A simple health check endpoint."""
    return {"status": "ok", "service": "text-service"}

@app.post("/v1/content/generate",
          response_model=ContentResponse,
          tags=["Content Generation"])
async def create_product_content(
    request: ContentRequest,
    provider: Optional[str] = Query(None, description="AI provider to use (e.g., gemini). Overrides default."),
    settings: Settings = Depends(get_settings)
):
    """
    Takes a product image URL and seller inputs, and returns AI-generated marketing content.
    """
    start_time = time.time()

    try:
        # 1. Determine which provider to use
        provider_name = provider or settings.default_provider

        # 2. Get provider instance from factory.
        # Our new factory handles mock_mode and config loading internally,
        # so this call is now extremely simple.
        ai_provider = ModelProviderFactory.get_provider(
            provider_name=provider_name,
            settings=settings
        )
        
        # 3. Generate content using the selected provider
        generated_data, model_name = await ai_provider.generate_content(request)

        # 4. Calculate latency
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        # 5. Create response
        actual_provider = "mock" if settings.mock_mode else provider_name
        
        response = ContentResponse(
            generated_content=generated_data,
            ai_model_used=model_name,
            latency_ms=latency_ms,
            metadata={
                "provider": actual_provider
                # model_name is already in ai_model_used, so no need to repeat
            }
        )

        return response

    except ValueError as e:
        # Raised by the factory for unsupported providers
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        # Raised by the provider (e.g., API error, image fetch failed)
        print(f"An internal error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An internal server error occurred."
        )

@app.get("/v1/providers", tags=["Configuration"])
def list_providers(settings: Settings = Depends(get_settings)):
    """
    Returns a list of available AI providers and their configured state.
    """
    
    available_providers = ModelProviderFactory.list_providers()
    
    # Create a "safe" dictionary to report on configured providers
    # without leaking sensitive keys.
    configured_providers: Dict[str, Any] = {}
    
    for name, config in settings.provider_settings.items():
        if name in available_providers:
            configured_providers[name] = {
                "model_name": config.model_name,
                "api_key_configured": bool(config.api_key) # True if set, False if None
            }

    return {
        "default_provider": settings.default_provider,
        "mock_mode": settings.mock_mode,
        "available_providers": available_providers,
        "configured_providers": configured_providers
    }