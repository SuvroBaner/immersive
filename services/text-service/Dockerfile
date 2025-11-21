# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /app
RUN pip install --no-cache-dir poetry uv

# Install dependencies to a specific folder
COPY pyproject.toml .
# Generate requirements.txt for simplicity in the final image
RUN uv pip compile pyproject.toml -o requirements.txt

# Stage 2: Runtime (Security Hardened)
FROM python:3.10-slim

WORKDIR /app

# Create a non-root user for security
RUN useradd -m -u 1000 canvas_user
USER canvas_user

# Copy requirements and install
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --user

# Copy Application Code
COPY --chown=canvas_user:canvas_user app ./app

# Expose port (Documentation only)
EXPOSE 8000

# Add local bin to PATH
ENV PATH="/home/canvas_user/.local/bin:$PATH"

# Run Application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]