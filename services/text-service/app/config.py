import os
from pydantic import BaseSettings
from typing import Dict, Any, Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""
    
    # Default provider
    default_provider: str = "gemini"
    
    # Mock mode for testing
    mock_mode: bool = False
    
    # Provider-specific settings
    provider_settings: Dict[str, Dict[str, Any]] = {
        "gemini": {
            "model_name": "gemini-2.5-flash"
        },
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()