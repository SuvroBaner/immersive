import os
from dotenv import load_dotenv
import google.generativeai as genai

def main():
    # Load environment variables
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found. Check your .env file.")
        return

    # Configure Gemini client
    genai.configure(api_key=api_key)

    print("🔍 Fetching available Gemini models...\n")

    # List available models
    models = [m for m in genai.list_models() if "generateContent" in m.supported_generation_methods]

    if not models:
        print("⚠️ No models supporting 'generateContent' found for your API key.")
        return

    # Display available models
    for m in models:
        print(f"✅ {m.name}")

    # Pick one model
    model_name = "models/gemini-2.5-flash"
    print(f"\n🚀 Using model: {model_name}")

    try:
        # Create model instance
        model = genai.GenerativeModel(model_name)

        # Generate a simple response
        response = model.generate_content("Say 'Hello, world!' in a poetic way in one line")
        print("\n🤖 Gemini response:\n")
        print(response.text)

    except Exception as e:
        print(f"\n❌ Error generating content: {e}")

if __name__ == "__main__":
    main()
