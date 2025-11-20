# Immersive Craft AI Platform

An AI-powered platform for household artists and craftspeople to professionally showcase and sell their creative items. This repository contains the backend microservices, starting with the **Immersive Text Generator** — a multimodal AI service that generates professional product descriptions from images and seller inputs.

---

## 🏗️ Architecture

The platform is built as a collection of microservices, with the `text-service` implementing a **provider factory pattern** that supports multiple AI providers:

- **Gemini** (Google) - Multimodal AI with vision capabilities
- **Mock** - For testing and development without API calls

The service uses a strategy pattern where each provider implements the same interface, allowing seamless switching between AI backends through configuration.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or `pip`
- A Google API key for Gemini (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository** (if not already done)

2. **Create and activate a virtual environment**

   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate  # On macOS/Linux
   # .venv\Scripts\Activate.ps1  # On Windows PowerShell
   ```

   Or using standard Python:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   # Using uv
   cd services/text-service
   uv pip install -e .
   
   # Or using pip
   pip install -e services/text-service/
   ```

4. **Configure environment variables**

   Create a `.env` file in `services/text-service/`:

   ```bash
   cd services/text-service
   nano .env  # or use your preferred editor
   ```

   Add your configuration:

   ```env
   # Default provider (gemini, mock)
   DEFAULT_PROVIDER=gemini
   
   # Enable mock mode for testing (set to true to bypass API calls)
   MOCK_MODE=false
   
   # Provider-specific settings
   # Note: Use double underscores (__) to nest settings
   PROVIDER_SETTINGS__GEMINI__API_KEY=your_google_api_key_here
   PROVIDER_SETTINGS__GEMINI__MODEL_NAME=gemini-2.5-flash
   ```

   **Important:** The nested configuration format (`PROVIDER_SETTINGS__GEMINI__API_KEY`) is required. This allows Pydantic to properly map environment variables to the nested `ProviderConfig` structure.

5. **Run the service**

   ```bash
   # From the project root
   uvicorn services.text-service.app.main:app --reload --port 8000
   
   # Or from services/text-service/
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`

   - **Interactive API Docs:** http://127.0.0.1:8000/docs
   - **Alternative Docs:** http://127.0.0.1:8000/redoc

---

## 📚 API Documentation

### Endpoints

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "text-service"
}
```

#### `GET /v1/providers`
List available AI providers and their configuration status.

**Response:**
```json
{
  "default_provider": "gemini",
  "mock_mode": false,
  "available_providers": ["gemini", "mock"],
  "configured_providers": {
    "gemini": {
      "model_name": "gemini-2.5-flash",
      "api_key_configured": true
    }
  }
}
```

#### `POST /v1/content/generate`
Generate product descriptions, titles, and marketing content from an image and seller inputs.

**Query Parameters:**
- `provider` (optional): Override the default provider (e.g., `?provider=gemini`)

**Request Body:**
```json
{
  "image_url": "https://example.com/product-image.jpg",
  "seller_inputs": {
    "item_name": "Handcrafted Clay Pot",
    "materials": "Natural terracotta clay, white paint",
    "inspiration": "Made during the rainy season, inspired by my garden",
    "category": "Pottery"
  },
  "config": {
    "tone": "evocative",
    "language": "en-IN",
    "target_platform": "web"
  }
}
```

**Response:**
```json
{
  "generated_content": {
    "title": "Handcrafted Clay Pot - Pottery Collection",
    "description": "This exquisite clay pot showcases the artistry...",
    "product_facts": [
      "Handcrafted pottery made with premium natural terracotta clay",
      "Unique design inspired by the rainy season garden",
      "One-of-a-kind piece, no two items are exactly alike"
    ],
    "blog_snippet_idea": "Discover the story behind this stunning clay pot..."
  },
  "ai_model_used": "gemini-2.5-flash",
  "latency_ms": 1250.5,
  "metadata": {
    "provider": "gemini"
  }
}
```

**Example cURL:**

```bash
curl -X POST "http://127.0.0.1:8000/v1/content/generate?provider=gemini" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://images.unsplash.com/photo-1604264726154-26480e76f4e1",
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
```

---

## ⚙️ Configuration

### Environment Variables

All configuration is managed through environment variables or a `.env` file in `services/text-service/`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_PROVIDER` | Default AI provider to use | `gemini` |
| `MOCK_MODE` | Enable mock mode (bypasses API calls) | `false` |
| `PROVIDER_SETTINGS__GEMINI__API_KEY` | Google Gemini API key | `None` |
| `PROVIDER_SETTINGS__GEMINI__MODEL_NAME` | Gemini model to use | `gemini-2.5-flash` |

### Mock Mode

Set `MOCK_MODE=true` in your `.env` file to enable mock mode. This bypasses all API calls and returns instantly generated sample content, useful for:
- Testing the API structure without consuming API credits
- Development when API keys are not available
- Integration testing

---

## 🏗️ Project Structure

```
immersive/
├── README.md
├── LICENSE
└── services/
    └── text-service/
        ├── app/
        │   ├── main.py              # FastAPI application and routes
        │   ├── models.py            # Pydantic request/response models
        │   ├── config.py            # Settings and configuration
        │   └── core/
        │       ├── base.py          # Abstract provider interface
        │       ├── factory.py       # Provider factory pattern
        │       ├── providers/
        │       │   ├── gemini.py    # Google Gemini implementation
        │       │   └── mock.py      # Mock provider for testing
        │       └── prompts/
        │           ├── base_templates.py
        │           └── provider_specific/
        │               └── gemini_templates.py
        ├── pyproject.toml           # Project dependencies
        ├── Dockerfile               # Container configuration
        └── .env                     # Environment variables (create this)
```

---

## 🔧 Development

### Adding a New Provider

1. Create a new provider class in `app/core/providers/` that inherits from `AIModelProvider`
2. Implement the `generate_content()` method
3. Register it in `app/core/factory.py`:

```python
_providers: Dict[str, Type[AIModelProvider]] = {
    "gemini": GeminiProvider,
    "mock": MockProvider,
    "your_provider": YourProvider,  # Add here
}
```

4. Update `app/config.py` to include default configuration in `provider_settings`
5. Add environment variable support following the `PROVIDER_SETTINGS__PROVIDER__KEY` pattern

### Running Tests

```bash
cd services/text-service
pytest
```

---

## 🐛 Troubleshooting

### `api_key_configured: false` in `/v1/providers`

This means your API key isn't being loaded. Ensure:
- Your `.env` file uses the nested format: `PROVIDER_SETTINGS__GEMINI__API_KEY=your_key`
- The `.env` file is in `services/text-service/` directory
- The service has been restarted after adding the key

### `model_name: null` in `/v1/providers`

Add the model name to your `.env`:
```env
PROVIDER_SETTINGS__GEMINI__MODEL_NAME=gemini-2.5-flash
```

### 500 Error on `/v1/content/generate`

Check the service logs for detailed error messages. Common issues:
- Invalid or missing API key
- Network issues fetching the image URL
- Provider-specific API errors

---

## 📝 License

See [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Support

For questions or issues, please open an issue in the repository.
