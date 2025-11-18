"""
Base prompt fragments that can be reused across different providers.
"""

# This block defines the context, which is universal
CONTEXT_BLOCK = """
---
CONTEXT:
- Tone: {tone}
- Language: {language}
- Target Platform: {target_platform}
"""

# This block defines the seller inputs, which is also universal
SELLER_INPUTS_BLOCK = """
---
SELLER INPUTS:
- Item Name: {item_name}
- Materials: {materials}
- Inspiration: {inspiration}
- Category: {category}
"""

# We remove the full ECOMMERCE_COPYWRITER_TEMPLATE from here
# because its JSON instructions are provider-specific.