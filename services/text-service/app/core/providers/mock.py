"""
Mock Provider for testing and simulation.

This provider returns simulated content without making any API calls.
Useful for development, testing, and when API keys are not available.
"""

from typing import Tuple
from PIL import Image
from io import BytesIO
import requests

from ..base import AIModelProvider
from ...models import ContentRequest, GeneratedContent


class MockProvider(AIModelProvider):
    """Mock provider that simulates AI content generation without API calls."""
    
    def __init__(self):
        """Initialize the mock provider. No API key required."""
        self.model_name = "mock-model-v1.0"
    
    def fetch_image(self, url: str) -> Image.Image:
        """
        Fetch image from URL (or create a mock image).
        In mock mode, we still fetch the image to validate the URL works.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            # If image fetch fails, create a simple mock image
            # This allows the mock to work even with invalid URLs
            return Image.new('RGB', (800, 600), color='lightgray')
    
    async def generate_content(self, request: ContentRequest) -> Tuple[GeneratedContent, str]:
        """
        Generate mock content based on the request.
        Returns realistic-looking content without calling any AI API.
        """
        # Fetch image (or use mock)
        image = self.fetch_image(request.image_url)
        
        # Generate mock content based on seller inputs
        mock_content = self._generate_mock_content(request)
        
        return mock_content, self.model_name
    
    def _generate_mock_content(self, request: ContentRequest) -> GeneratedContent:
        """Generate realistic mock content from request data."""
        
        # Extract information from request
        item_name = request.seller_inputs.item_name
        materials = request.seller_inputs.materials
        inspiration = request.seller_inputs.inspiration
        category = request.seller_inputs.category
        tone = request.config.tone
        language = request.config.language
        platform = request.config.target_platform
        
        # Generate mock title
        title = f"Handcrafted {item_name} - {category} Collection"
        
        # Generate mock description
        description = f"""This exquisite {item_name.lower()} showcases the artistry and craftsmanship that goes into every piece. 
        
Crafted with care using {materials.lower()}, this item represents a unique blend of tradition and contemporary design. 
        
The inspiration behind this piece comes from {inspiration.lower()}, which is reflected in its distinctive character and charm. Perfect for those who appreciate handmade quality and authentic craftsmanship.
        
Whether displayed in your home or given as a gift, this {category.lower()} piece tells a story of passion, creativity, and dedication to the art of making."""
        
        # Generate mock product facts
        product_facts = [
            f"Handcrafted {category.lower()} made with premium {materials.split(',')[0].strip().lower()}",
            f"Unique design inspired by {inspiration.lower()}",
            f"One-of-a-kind piece, no two items are exactly alike",
            f"Perfect for {platform} showcasing and presentation"
        ]
        
        # Generate mock blog snippet
        blog_snippet = f"Discover the story behind this stunning {item_name.lower()}. Learn how {inspiration.lower()} inspired the creation of this beautiful {category.lower()} piece, and explore the craftsmanship that makes each item unique."
        
        return GeneratedContent(
            title=title,
            description=description,
            product_facts=product_facts,
            blog_snippet_idea=blog_snippet
        )

