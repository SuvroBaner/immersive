import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict, Any, Optional
from functools import lru_cache

# Directories
# - _APP_DIR: directory where this config.py file is located (app directory)
# - _ROOT_DIR: project root assumed to be the parent of app
_APP_DIR = Path(__file__).parent.resolve()
_ROOT_DIR = _APP_DIR.parent

class Settings(BaseSettings):
    """Application settings."""
    
    # Default provider
    default_provider: str = "gemini"
    
    # Mock mode for testing
    mock_mode: bool = False # True
    
    # API Keys - pydantic_settings automatically maps GOOGLE_API_KEY env var to this field
    # It converts env var names to lowercase, so GOOGLE_API_KEY -> google_api_key
    google_api_key: Optional[str] = None
    
    # Provider-specific settings
    provider_settings: Dict[str, Dict[str, Any]] = {
        "gemini": {
            "model_name": "gemini-2.5-flash"
        },
    }
    
    model_config = SettingsConfigDict(
        # Prefer .env in project root (outside app). If not present, pydantic will still
        # read process environment variables. You can also place a copy in app/.env.
        env_file=str(_ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unexpected env vars safely
        case_sensitive=False  # Allow case-insensitive env var matching
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()