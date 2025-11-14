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
    mock_mode: bool = True # True
    
    # Generic API keys map, one place to define per-provider keys.
    # Can be overridden from env using API_KEYS__<PROVIDER>=value (see env_nested_delimiter below).
    api_keys: Dict[str, Optional[str]] = {
        "gemini": None,
        "openai": None,
        "huggingface": None
    }
    
    # Provider-specific settings
    # Add entries for multiple providers; each can have model_name and api_key.
    # You can override nested values via env using the delimiter below, e.g.:
    #   PROVIDER_SETTINGS__GEMINI__API_KEY=xxx
    #   PROVIDER_SETTINGS__OPENAI__MODEL_NAME=gpt-4o-mini
    provider_settings: Dict[str, Dict[str, Any]] = {
        "gemini": {
            "model_name": "models/gemini-2.5-flash",
            "api_key": None
        },
        "openai": {
            "model_name": "gpt-4o-mini",
            "api_key": None
        },
        "huggingface": {
            "model_name": "distilbert-base-uncased",
            "api_key": None
        }
    }
    
    model_config = SettingsConfigDict(
        # Prefer .env in project root (outside app). If not present, pydantic will still
        # read process environment variables. You can also place a copy in app/.env.
        env_file=str(_ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unexpected env vars safely
        case_sensitive=False,  # Allow case-insensitive env var matching
        env_nested_delimiter="__"  # Enable nested overrides for provider_settings and api_keys
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()