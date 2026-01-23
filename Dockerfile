# Dockerfile for arifOS Body API (v39/v51)

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
COPY pyproject.toml .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn pydantic mcp sse-starlette

# Copy codebase
COPY arifos/ arifos/
COPY 000_THEORY/ 000_THEORY/
COPY setup/ setup/

# Install package in editable mode
RUN pip install -e .

# Set environment variables
ENV PYTHONPATH=/app
ENV ARIFOS_MODE=production
ENV PORT=8000

# Expose the Body API port
EXPOSE 8000

# Run the Body API server (exec form with sh -c for $PORT expansion)
CMD ["sh", "-c", "uvicorn arifos.core.integration.api.app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
