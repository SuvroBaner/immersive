from typing import Dict, Type
from .base import AIModelProvider
from .providers.gemini import GeminiProvider

class ModelProviderFactory:
    """ Factory for creating AI model provider instances. """"

    _providers: Dict[str, Type[AIModelProvider]] = {
        "gemini": GeminiProvider,
    }

    @classmethod
    def get_provider(cls, provider_name: str) -> AIModelProvider:
        """
        Get an instance of the specified provider.

        Args:
            provider_name: Name of the provider to instantiate

        Returns:
            An instance of the specified provider

        Raises:
            ValueError: If the provider is not supported.

        """

        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            supported = ", ".join(cls._providers.keys())
            rasie ValueError(f"Unsupported provider: {provider_name}. Supported providers: {supported}")

        return provider_class()

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[AIModelProvider]) -> None:
        """ Register a new provider class. """
        cls._providers[name.lower()] = provider_class