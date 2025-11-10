"""
This is the abstract base class for the provider.
"""

from abc import ABC, abstractmethod
from ..models import ContentRequest, GeneratedContent
from typing import Tuple

class AIModelProvider(ABC):
    """ Abstract base class for AI model providers """

    @abstractmethod
    async def generate_content(self, request: ContentRequest) -> Tuple[GeneratedContent, str]:
        """
        Generate content based on the provided request.
        Returns a tuple of (GeneratedContent, model_name)
        """
        pass

    @abstractmethod
    def fetch_image(self, url: str):
        """ Fetch image from URL in the format required by the provided. """
        pass

