# --- Stage 1: Builder ---
    FROM python:3.10.13-slim AS builder

    WORKDIR /app
    
    # Install git and uv. Git is needed for any git-based dependencies (good practice).
    RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
    RUN pip install --no-cache-dir uv
    
    # Copy dependency files
    COPY pyproject.toml uv.lock* ./
    
    # Generate requirements.txt
    # Logic: Use 'uv export' if lockfile exists, otherwise 'uv compile'
    RUN if [ -f uv.lock ]; then \
        # 1. Export the dependencies (including hashes)
        uv export --format requirements-txt | \
        # 2. FILTER OUT the local editable requirement (e.g., -e file:///app)
        # egrep removes any line starting with -e or containing file://
        egrep -v '^-e|file://' > requirements.txt; \
        else \
        # FALLBACK: Compile from pyproject.toml
        uv pip compile pyproject.toml -o requirements.txt; \
        fi
    
    # --- Stage 2: Runtime ---
    FROM python:3.10.13-slim
    
    # Standard Python Envs for Production
    ENV PYTHONUNBUFFERED=1 \
        PYTHONDONTWRITEBYTECODE=1 \
        PATH="/home/canvas_user/.local/bin:$PATH"
    
    WORKDIR /app
    
    # Create non-root user (security best practice)
    RUN useradd -m -u 1000 canvas_user
    
    # 1. Install Dependencies
    # Copy requirements first to leverage Docker cache
    COPY --from=builder /app/requirements.txt .
    
    # Switch to user
    USER canvas_user
    
    # Install external dependencies listed in requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt --user
    
    # 2. Copy Application Code
    COPY --chown=canvas_user:canvas_user app ./app
    
    # Expose port
    EXPOSE 8000
    
    # Runtime Command
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers"]