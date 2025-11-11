from typing import Dict, Type
from .base import AIModelProvider
from .providers.gemini import GeminiProvider
from .providers.mock import MockProvider

class ModelProviderFactory:
    """ Factory for creating AI model provider instances. """

    _providers: Dict[str, Type[AIModelProvider]] = {
        "gemini": GeminiProvider,
        "mock": MockProvider,
    }

    @classmethod
    def get_provider(cls, provider_name: str, mock_mode: bool = False, **kwargs) -> AIModelProvider:
        """
        Get an instance of the specified provider.

        Args:
            provider_name: Name of the provider to instantiate
            mock_mode: If True, returns MockProvider regardless of provider_name
            **kwargs: Optional arguments such as category, platform, etc.

        Returns:
            An instance of the specified provider

        Raises:
            ValueError: If the provider is not supported.

        """
        # If mock_mode is enabled, always return MockProvider
        if mock_mode:
            return MockProvider()

        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            supported = ", ".join(cls._providers.keys())
            raise ValueError(f"Unsupported provider: {provider_name}. Supported providers: {supported}")

        # Optionally pass kwargs to provider if it supports them
        try:
            return provider_class(**kwargs)
        except TypeError:
            # If provider doesn't accept these kwargs, just instantiate normally
            return provider_class()

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[AIModelProvider]) -> None:
        """ Register a new provider class. """
        cls._providers[name.lower()] = provider_class

    @classmethod
    def list_providers(cls) -> list[str]:
        """List all available provider names."""
        return list(cls._providers.keys())