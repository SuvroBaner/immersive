from typing import Dict, Type, Optional, Any
from .base import AIModelProvider
from .providers.gemini import GeminiProvider
from .providers.mock import MockProvider
from ..config import Settings # Import your new Settings

class ModelProviderFactory:
    """ 
    Factory for creating AI model provider instances.
    It extracts provider-specific config from the Settings object.
    """

    _providers: Dict[str, Type[AIModelProvider]] = {
        "gemini": GeminiProvider,
        "mock": MockProvider,
    }

    @classmethod
    def get_provider(cls, 
                     provider_name: str, 
                     settings: Settings, # Use the type-safe Settings object
                     **override_kwargs) -> AIModelProvider:
        """
        Get an instance of the specified provider, configuring it from settings.

        Args:
            provider_name: Name of the provider (e.g., "gemini")
            settings: The application settings object.
            **override_kwargs: Any kwargs passed here will override settings
                               (e.g., model_name="gemini-pro-1.5").
        Returns:
            An instance of the specified provider.
        """
        
        # 1. Handle Mock Mode (uses setting by default)
        if settings.mock_mode:
            return MockProvider()

        # 2. Find the provider class
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            supported = ", ".join(cls._providers.keys())
            raise ValueError(f"Unsupported provider: {provider_name}. Supported providers: {supported}")

        # 3. Get the provider-specific config block from settings
        provider_config = {}
        if settings.provider_settings:
            config_block = settings.provider_settings.get(provider_name.lower())
            
            if config_block:
                # Dump the Pydantic model to a dict of args
                provider_config = config_block.model_dump() 

        # 4. Apply any explicit overrides (e.g., from the request body)
        provider_config.update(override_kwargs)

        # 5. Filter out 'None' values so providers can use defaults
        final_kwargs = {k: v for k, v in provider_config.items() if v is not None}

        # 6. Instantiate the provider
        try:
            return provider_class(**final_kwargs)
        except TypeError as e:
            raise TypeError(
                f"Failed to instantiate {provider_class.__name__} with config {final_kwargs}. "
                f"Check __init__ signature. Original Error: {e}"
            )

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[AIModelProvider]) -> None:
        cls._providers[name.lower()] = provider_class

    @classmethod
    def list_providers(cls) -> list[str]:
        return list(cls._providers.keys())