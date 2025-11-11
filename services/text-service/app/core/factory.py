from typing import Dict, Type, Optional, Any
import os
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
    def _resolve_api_key(cls, provider_name: str, settings: Optional[Any]) -> Optional[str]:
        """
        Resolve API key for a given provider in a generalized way:
        1) Provider-specific key in settings.provider_settings[provider].api_key
        2) Provider-specific field on settings (e.g., google_api_key)
        3) Upper-cased env var pattern: <PROVIDER>_API_KEY (e.g., GEMINI_API_KEY)
        4) Well-known aliases (e.g., GOOGLE_API_KEY for gemini)
        """
        provider = (provider_name or "").lower()
        # 1) Provider-specific api_key in provider_settings
        if settings and hasattr(settings, "provider_settings"):
            try:
                ps = settings.provider_settings.get(provider, {})
                if isinstance(ps, dict):
                    key = ps.get("api_key")
                    if key:
                        return key
            except Exception:
                pass

        # 2) Provider-specific field on settings
        if settings:
            candidate_attr = f"{provider}_api_key"
            key = getattr(settings, candidate_attr, None)
            if key:
                return key
            # 2b) Generic api_keys map
            try:
                from typing import Mapping
                api_keys = getattr(settings, "api_keys", None)
                if isinstance(api_keys, dict):
                    key = api_keys.get(provider)
                    if key:
                        return key
            except Exception:
                pass

        # 3) Generic env var pattern
        env_var = f"{provider.upper()}_API_KEY"
        key = os.environ.get(env_var)
        if key:
            return key

        # 4) Well-known alias for Gemini (Google)
        if provider == "gemini":
            key = os.environ.get("GOOGLE_API_KEY")
            if not key and settings:
                key = getattr(settings, "google_api_key", None)
            if key:
                return key

        return None

    @classmethod
    def get_provider(cls, provider_name: str, mock_mode: bool = False, settings: Optional[Any] = None, **kwargs) -> AIModelProvider:
        """
        Get an instance of the specified provider.

        Args:
            provider_name: Name of the provider to instantiate
            mock_mode: If True, returns MockProvider regardless of provider_name
            settings: Optional settings object for resolving API keys and config
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

        # Resolve API key generically and pass if the provider supports it
        api_key = cls._resolve_api_key(provider_name, settings)
        if api_key and provider_name.lower() in {"gemini"}:
            kwargs["api_key"] = api_key

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