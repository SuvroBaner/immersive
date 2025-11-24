from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict, Optional
from functools import lru_cache

# --- Path Setup ---
# _APP_DIR = app/
# _ROOT_DIR = services/text-service/
_APP_DIR = Path(__file__).parent.resolve()
_ROOT_DIR = _APP_DIR.parent

# --- Type-Safe Provider Configuration ---

class ProviderConfig(BaseSettings):
    """A type-safe model for a single provider's settings. 
    Keys are loaded via Pydantic, e.g., PROVIDER_SETTINGS__GEMINI__API_KEY.
    """
    
    api_key: Optional[str] = Field(default=None)
    model_name: Optional[str] = None

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore"
    )

class Settings(BaseSettings):
    """
    Application settings, loaded from .env and environment variables.
    """
    
    # --- Core Settings ---
    default_provider: str = Field(default="gemini")
    mock_mode: bool = Field(default=False)
    
    # --- Nested Provider-Specific Settings ---
    provider_settings: Dict[str, ProviderConfig] = Field(
        default_factory=lambda: {
            "gemini": ProviderConfig(
                # API key is now loaded solely by Pydantic from env/file.
                # We set it to None as a default, letting the environment override it.
                api_key=None,
                model_name="gemini-2.5-flash"
            ),
            "openai": ProviderConfig(
                api_key=None,
                model_name="gpt-4o-mini"
            ),
        }
    )

    model_config = SettingsConfigDict(
        # Load from .env in the `services/text-service/` directory
        env_file=str(_ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_nested_delimiter="__" # For PROVIDER_SETTINGS__GEMINI__...
    )

@lru_cache()
def get_settings() -> Settings:
    """
    Get the cached, singleton-like settings instance.
    This is the function you'll import elsewhere in your app.
    """
    return Settings()