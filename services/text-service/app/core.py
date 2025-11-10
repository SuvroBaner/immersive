"""
This is the "brain" of your service. It will handle the prompt engineering and the actual call to the Gemini API.

We'll use requests to download the image from the image_url and google-generative-ai to process it.

"""

import os
import requests
from PIL import Image
from io import BytesIO
import json
import time

import google.generativeai as genai

from requests.cookies import MockResponse

from .models import ContentRequest, ContentResponse, GeneratedContent

# load the API from the .env file
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

# --- MOCK MODE ---
# Set to True to return a mock response without calling the Gemini API (for testing purposes)
MOCK_MODE = True
MOCK_MODEL_NAME = "mock-gemini-pro"
MOCK_RESPONSE = {
    "title": "Handcrafted 'Rainy Day' Terracotta Pot with Delicate White Motifs",
    "description": "Capture the fresh, earthy feeling of a rainy day with this one-of-a-kind terracotta pot. Hand-shaped from natural clay... the seller, inspired by their garden, has adorned it with delicate white patterns reminiscent of raindrops...",
    "product_facts": [
        "Terracotta (or 'baked earth') is a porous clay, perfect for plant health.",
        "This item is handcrafted, meaning no two pieces are exactly alike.",
        "Sourced directly from a household artist."
    ],
    "blog_snippet_idea": "The Rise of Artisan Pottery: A Look at 'Crafts of India' Seller..."
}

# -------------------------

# Configure the Gemini API -

try:
    api_key = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key = api_key)
    # client = genai.Client() # in prod use this
except KeyError:
    print("Error: GOOGLE_API_KEY is not set in the environment variables")
    if not MOCK_MODE:
        raise

# This is the master prompt template.
# It's structured to guide the AI to return a JSON object.

PROMPT_TEMPLATE = """
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

def fetch_image_from_url(url: str) -> Image.Image:
    """ Downloads an image from a URL and returns it as a PIL Image object."""
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an error for bad responses.
        img = Image.open(BytesIO(response.content))
        return img
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image from URL {url}: {e}")
        raise

async def generate_content_from_gemini(request: ContentRequest) -> (GeneratedContent, str):
    """
    Generate content using the Gemini API
    Returns a tuple of (GeneratedContent, ai_model_name)
    """

    if MOCK_MODE:
        print("--- RUNNING IN MOCK MODE ----")
        time.sleep(0.5) # simulate latency
        return GeneratedContent(**MOCK_RESPONSE), MOCK_MODEL_NAME

    try:
        # 1. Initialize the model
        model_name = "gemini-2.5-flash"
        model = genai.GenerativeModel(model_name)

        # 2. Fetch the image from the URL
        print(f"Fetching image from: {request.image_url}")
        image = fetch_image_from_url(request.image_url)

        # 3. Create the text part of the prompt
        text_prompt = PROMPT_TEMPLATE.format(
            tone = request.config.tone,
            language = request.config.language,
            target_platform = request.config.target_platform,
            item_name = request.seller_inputs.item_name,
            materials = request.seller_inputs.materials,
            inspiration = request.seller_inputs.inspiration,
            category = request.seller_inputs.category
        )

        # 4. Define the generation config to force JSON output 
        generation_config = genai.GenerationConfig(
            response_mime_type = "application/json"
        )

        # 5. Generate content (image + text)
        print("Sending request to Gemini API ...")
        response = await model.generate_content_async(
            [text_prompt, image],
            generation_config = generation_config
        )

        # 6. Parse the JSON response -
        print("Parsing Gemini Response ...")
        response_json = json.loads(response.text)

        # 7. Validate with Pydantic and return
        return GeneratedContent(**response_json), model_name

    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        # In a real app, you'd raise a proper HTTPException
        raise