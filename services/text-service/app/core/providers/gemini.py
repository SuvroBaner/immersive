"""
Implement the Provider Class -

Gemini

"""

import os
import google.generativeai as genai
from PIL import Image
import json
from io import BytesIO
import requests
from typing import Tuple

from ..base import AIModelProvider
from ...models import ContentRequest, GeneratedContent
from ..prompts.provider_specific.gemini_templates import GEMINI_ECOMMERCE_TEMPLATE

class GeminiProvider(AIModelProvider):
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        genai.configure(api_key = self.api_key)
        self.model_name = "gemini-2.5-flash"
        self.model = genai.GenerativeModel(self.model_name)
        
        self.prompt_template = GEMINI_ECOMMERCE_TEMPLATE

    def fetch_image(self, url: str) -> Image.Image:
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))

    async def generate_content(self, request: ContentRequest) -> Tuple[GeneratedContent, str]:
        # Fetch image
        image = self.fetch_image(request.image_url)

        # Format Prompt
        text_prompt = self.prompt_template.format(
            tone = request.config.tone,
            language = request.config.language,
            target_platform = request.config.target_platform,
            item_name = request.seller_inputs.item_name,
            materials = request.seller_inputs.materials,
            inspiration = request.seller_inputs.inspiration,
            category = request.seller_inputs.category,
            image_url = request.image_url
        )

        # Generate Content
        generation_config = genai.GenerationConfig(
            response_mime_type = "application/json"
        )

        response = await self.model.generate_content_async(
            [text_prompt, image],
            generation_config = generation_config
        )

        # Parse response -
        response_json = json.loads(response.text)

        return GeneratedContent(**response_json), self.model_name