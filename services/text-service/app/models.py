"""
In this file, we will use Pydantic to translate the JSON specifications into a Python classes.

GenerateText Request Body

1. POST /v1/content/generate
This single endpoint takes all the seller's simple inputs and the URL of the newly-processed image, then returns the generated text.
Method: POST
Request Body

curl -X 'POST' \
  'http://127.0.0.1:8000/v1/content/generate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "image_url": "https://images.unsplash.com/photo-1604264726154-26480e76f4e1?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y2xheSUyMHBvdHxlbnwwfHwwfHx8MA%3D%3D&fm=jpg&q=60&w=3000",
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
}'

Response (HTTP 200 OK): The response is the complete, structured content, ready for the frontend to display.

{
  "generated_content": {
    "title": "Handcrafted Clay Pot - Pottery Collection",
    "description": "This exquisite clay pot showcases the artistry and craftsmanship that goes into every piece. \n        \nCrafted with care using natural terracotta clay, white paint, this item represents a unique blend of tradition and contemporary design. \n        \nThe inspiration behind this piece comes from made this during the rainy season, inspired by my garden, which is reflected in its distinctive character and charm. Perfect for those who appreciate handmade quality and authentic craftsmanship.\n        \nWhether displayed in your home or given as a gift, this pottery piece tells a story of passion, creativity, and dedication to the art of making.",
    "product_facts": [
      "Handcrafted pottery made with premium natural terracotta clay",
      "Unique design inspired by made this during the rainy season, inspired by my garden",
      "One-of-a-kind piece, no two items are exactly alike",
      "Perfect for web showcasing and presentation"
    ],
    "blog_snippet_idea": "Discover the story behind this stunning clay pot. Learn how made this during the rainy season, inspired by my garden inspired the creation of this beautiful pottery piece, and explore the craftsmanship that makes each item unique."
  },
  "ai_model_used": "mock-model-v1.0",
  "latency_ms": 605.3879261016846,
  "metadata": {
    "provider": "mock",
    "model": "mock-model-v1.0"
  }
}

"""

from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict

# ---- Request Models ----
# These models define the expected input

class SellerInputs(BaseModel):
    item_name: str = Field("Clay Pot", description="The name of the item")
    materials: str = Field("Natural terracotta clay, white paint", description="The materials used to make the item")
    inspiration: str = Field("Made this during the rainy season, inspired by my garden", description="The inspiration for the item")
    category: str = Field("Pottery", description="The category of the item")

class Config(BaseModel):
    tone: str = Field("evocative", description="The tone of the content")
    language: str = Field("en-IN", description="The language of the content")
    target_platform: str = Field("web", description="The platform of the content")

class ContentRequest(BaseModel):
    image_url: str = Field(
      "https://images.unsplash.com/photo-1604264726154-26480e76f4e1?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y2xheSUyMHBvdHxlbnwwfHwwfHx8MA%3D%3D&fm=jpg&q=60&w=3000",
      description="The URL of the image")
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
    metadata: Optional[Dict[str, Any]] = None