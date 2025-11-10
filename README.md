# Immersive Craft AI Platform

This project is an AI-powered platform for household artists and craftspeople to professionally showcase and sell their creative items.

This repository contains the backend microservices, starting with the Immersive Text Generator.

---

## 🚀 Local Development Setup

Follow these steps to set up and run the services locally. This guide assumes you have [uv](https://github.com/astral-sh/uv) installed.

### 1. Set Up The Virtual Environment

First, create and activate the virtual environment from the project root:

```bash
# 1. Create the virtual environment (named .venv)
uv venv

# 2. Activate it
# On macOS/Linux:
source .venv/bin/activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

Install all required packages for the `text-service` using `uv`:

```bash
uv pip install -r services/text-service/requirements.txt
```

### 3. Set Up Environment Variables

You must provide a Google API key for the service to run.

```bash
# 1. Copy the example file to a new .env file
cp services/text-service/.env.example services/text-service/.env

# 2. Open the new .env file and add your API key
nano services/text-service/.env
```

### 4. Run the Service

You can now run the `text-service` using `uvicorn`:

```bash
uvicorn services.text-service.app.main:app --reload
```

The API will be live at `http://127.0.0.1:8000`, and you can access the interactive documentation at `http://127.0.0.1:8000/docs`.

---

## Services

### 1. `/services/text-service`

* **Language:** Python (FastAPI)
* **Purpose:** A multimodal AI service that takes a product image and seller inputs to generate professional, immersive product descriptions, titles, and facts.
* **Endpoint:** `POST /v1/content/generate`