"""
Implement the Provider Class - Gemini (simplified & non-blocking)
"""

import os
import google.generativeai as genai
import httpx # for async network calls
from PIL import Image
import json
from io import BytesIO
import requests
from typing import Tuple, Optional, Type

from ..base import AIModelProvider
from ...models import ContentRequest, GeneratedContent
from ..prompts.provider_specific.gemini_templates import GEMINI_ECOMMERCE_TEMPLATE

class GeminiProvider(AIModelProvider):
    """
    Concrete Strategy for Google Gemini API.

    This provider is non-blocking and configurable.
    """

    def __init__(self, 
                 api_key: Optional[str] = None,
                 model_name: str = "gemini-2.5-flash"): # make the model configurable
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Optional API key. If not provided, will try to get from:
                    1. GOOGLE_API_KEY environment variable
                    2. Settings.google_api_key (from .env file)

            model_name: The specific Gemini model to use
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found. Please set it as an environment variable."
            )

        ## genai.configure is global
        genai.configure(api_key = self.api_key)

        self.model_name = model_name
        self.model = genai.GenerativeModel(self.model_name)
        self.prompt_template = GEMINI_ECOMMERCE_TEMPLATE

        # Create a persistent async HTTP client
        self._http_client = httpx.AsyncClient(timeout = 10.0)

    async def _fetch_image_async(self, url: str) -> Image.Image:
        """
        Fetches an image from a URL asynchronously.
        """
        try:
            response = await self._http_client.get(url)
            response.raise_for_status() # Raise an exception for 4xx/5xx responses

            # Image.open is a sync operation, but it's very fast
            # as it's just reading from in-memory bytes.
            return Image.open(BytesIO(response.content))

        except httpx.RequestError as e:
            print(f"Error fetching image from {url}: {e}")
            # You might want to raise a custom exception here
            raise


    async def generate_content(self, request: ContentRequest) -> Tuple[GeneratedContent, str]:
        """
        The main implementation of the AIModelProvider Strategy.
        """

        try:
            # 1. Fetch Image (non-blocking)
            image = await self._fetch_image_async(request.image_url)

            # 2. Format Prompt (simplified)
            # .model_dump() to pass all fields at once
            prompt_data = {
                **request.config.model_dump(),
                **request.seller_inputs.model_dump(),
                "image_url": request.image_url
            }
            text_prompt = self.prompt_template.format(**prompt_data)

            # 3. Generate Content
            generation_config = genai.GenerationConfig(
                response_mime_type = "application/json"
            )

            response = await self.model.generate_content_async(
                [text_prompt, image],
                generation_config = generation_config
            )

            # 4. Parse response
            # The SDK's .text attribute is already a JSON string
            response_json = json.loads(response.text)

            return GeneratedContent(**response_json), self.model_name

        except (httpx.RequestError, json.JSONDecodeError, TypeError) as e:
            # Catch potential errors and provide a clear log
            print(f"Error in GeminiProvider: {e}")
            # You should raise a specific internal error here 
            raise Exception("Failed to generate content from Gemini")