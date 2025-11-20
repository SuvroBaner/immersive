"""
Mock Provider for testing and simulation.

This provider returns simulated content instantly without making any API calls.
It is lightweight and has no external network dependencies.
"""

from typing import Tuple
import asyncio  # Used to simulate a small delay

from ..base import AIModelProvider
from ...models import ContentRequest, GeneratedContent


class MockProvider(AIModelProvider):
    """Mock provider that simulates AI content generation without API calls."""
    
    def __init__(self, **kwargs):
        """Initialize the mock provider. No API key required."""
        # We accept **kwargs to harmlessly ignore any config
        # passed from the factory (like api_key or model_name)
        self.model_name = "mock-model-v1.0"
    
    async def generate_content(self, request: ContentRequest) -> Tuple[GeneratedContent, str]:
        """
        Generate mock content based on the request.
        Returns realistic-looking content without calling any AI API.
        """
        
        # Simulate a small amount of non-blocking I/O (e.g., 50ms)
        # This makes the mock behave more like a real network call
        # in logs and performance traces.
        await asyncio.sleep(0.05) 
        
        # Generate and return the mock content
        mock_content = self._generate_mock_content(request)
        
        return mock_content, self.model_name
    
    def _generate_mock_content(self, request: ContentRequest) -> GeneratedContent:
        """Generate realistic mock content from request data."""
        
        # This helper function is synchronous and CPU-bound, which is perfect.
        item_name = request.seller_inputs.item_name
        materials = request.seller_inputs.materials
        inspiration = request.seller_inputs.inspiration
        
        title = f"[Mock] Handcrafted {item_name}"
        
        description = f"This is a mock description for a {item_name}." \
                      f" It is made of {materials} and was inspired by {inspiration}." \
                      f" The request config was: tone={request.config.tone}, lang={request.config.language}."
        
        product_facts = [
            f"Fact 1: Made of {materials.split(',')[0].strip()}",
            "Fact 2: This is mock data",
            "Fact 3: Generated instantly"
        ]
        
        blog_snippet = f"Blog snippet idea for {item_name}."
        
        return GeneratedContent(
            title=title,
            description=description,
            product_facts=product_facts,
            blog_snippet_idea=blog_snippet
        )