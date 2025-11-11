"""
Base prompt templates that can be used across different providers.
"""

# Generic e-commerce template that works with most providers
ECOMMERCE_COPYWRITER_TEMPLATE = """
You are an expert e-commerce copywriter. Your task is to generate compelling product content
based on an image and a few inputs from the seller.

You must respond in a valid JSON format. Do NOT include any text outside of the JSON object.
The JSON object must match the following schema:

{{
    "title": "string",
    "description": "string",
    "product_facts": ["string", "string", "string"],
    "blog_snippet_idea": "string"
}}

---
CONTEXT:
- Tone: {tone}
- Language: {language}
- Target Platform: {target_platform}

SELLER INPUTS:
- Item Name: {item_name}
- Materials: {materials}
- Inspiration: {inspiration}
- Category: {category}

IMAGE:
- URL: {image_url}

Generate the content based on the seller inputs and attached image.
"""

# You can define different templates for different use cases
PRODUCT_DESCRIPTION_TEMPLATE = """
Create a compelling product description for the following item:
...
"""

BLOG_POST_TEMPLATE = """
Write a blog post about the following product:
...
"""