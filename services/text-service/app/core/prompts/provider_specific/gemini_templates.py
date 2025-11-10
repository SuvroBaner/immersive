"""Templates optimized for Gemini models."""

# Import from base templates 
from ..base_templates import ECOMMERCE_COPYWRITER_TEMPLATE

# Gemini works well with structured prompts
GEMINI_ECOMMERCE_TEMPLATE = ECOMMERCE_COPYWRITER_TEMPLATE + """
Additional instructions for Gemini:
- Be concise and factual
- Focus on visual details from the image
- Structure the description with short paragraphs
"""

# Gemini-specific template that leverages its multimodal capabilities
GEMINI_VISUAL_ANALYSIS_TEMPLATE = """
Analyze the following product image in detail:
1. First describe what you see in the image
2. Note any unique visual characteristics
3. Identify materials, colors, and textures
4. Suggest how these visual elements could be highlighted in marketing
5. Format your response as JSON with the following structure:
{
    "visual_description": "string",
    "unique_features": ["string", "string"],
    "materials_detected": ["string", "string"],
    "marketing_angles": ["string", "string"]
}
"""