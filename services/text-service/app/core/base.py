"""
This is the abstract base class for the provider.
"""

from abc import ABC, abstractmethod
from ..models import ContentRequest, GeneratedContent
from typing import Tuple

class AIModelProvider(ABC):
    """ Abstract base class for AI model providers """
    """
    Defines the single, public contract for content generation.
    """

    @abstractmethod
    async def generate_content(self, request: ContentRequest) -> Tuple[GeneratedContent, str]:
        """
        Generate content based on the provided request.
        Returns a tuple of (GeneratedContent, model_name)
        """
        pass

  # We remove fetch_image from the base class.
    # It is an internal implementation detail of any provider
    # that happens to get a URL, not a required part of the
    # public contract for all providers.

