"""
In this file, we will use Pydantic to translate the JSON specifications into a Python classes.

GenerateText Request Body

1. POST /v1/content/generate
This single endpoint takes all the seller's simple inputs and the URL of the newly-processed image, then returns the generated text.
Method: POST
Request Body: application/json
Request:
JSON
{
  "image_url": "https://s3.your-bucket.com/processed/user-123/img-a1b2c3d4.png",
  "seller_inputs": {
    "item_name": "Clay Pot",
    "materials": "Natural terracotta clay, white paint",
    "inspiration": "Made this during the rainy season, inspired by my garden",
    "category": "Pottery"
  },
  "config": {
    "tone": "evocative",
    "language": "en-IN",
    "target_platform": "web"
  }
}

Response (HTTP 200 OK): The response is the complete, structured content, ready for the frontend to display.
JSON
{
  "generated_content": {
    "title": "Handcrafted 'Rainy Day' Terracotta Pot with Delicate White Motifs",
    "description": "Capture the fresh, earthy feeling of a rainy day with this one-of-a-kind terracotta pot. Hand-shaped from natural clay... the seller, inspired by their garden, has adorned it with delicate white patterns reminiscent of raindrops...",
    "product_facts": [
      "Terracotta (or 'baked earth') is a porous clay, perfect for plant health.",
      "This item is handcrafted, meaning no two pieces are exactly alike.",
      "Sourced directly from a household artist."
    ],
    "blog_snippet_idea": "The Rise of Artisan Pottery: A Look at 'Crafts of India' Seller..."
  },
  "ai_model_used": "gemini-1.5-pro",
  "latency_ms": 8450
}

"""

from pydantic import BaseModel, Field
from typing import List, Optional

# ---- Request Models ----
# These models define the expected input

class SellerInputs(BaseModel):
    item_name: str = Field(..., description="The name of the item")
    materials: str = Field(..., description="The materials used to make the item")
    inspiration: str = Field(..., description="The inspiration for the item")
    category: str = Field(..., description="The category of the item")

class Config(BaseModel):
    tone: str = Field(..., description="The tone of the content")
    language: str = Field(..., description="The language of the content")
    target_platform: str = Field(..., description="The platform of the content")

class ContentRequest(BaseModel):
    image_url: str = Field(..., description="The URL of the image")
    seller_inputs: SellerInputs = Field(..., description="The inputs from the seller")
    config: Config = Field(..., description="The config for the content")


# ---- Response Models ----
# These models define the output

class GeneratedContent(BaseModel):
    title: str = Field(..., description="The title of the content")
    description: str = Field(..., description="The description of the content")
    product_facts: List[str] = Field(..., description="The product facts of the content")
    blog_snippet_idea: str = Field(..., description="The blog snippet idea of the content")

class ContentResponse(BaseModel):
    generated_content: GeneratedContent = Field(..., description="The generated content")
    ai_model_used: str = Field(..., description="The AI model used to generate the content")
    latency_ms: float = Field(..., description="The latency of the content generation in milliseconds")