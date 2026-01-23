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
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn pydantic

# Copy codebase
COPY arifos/ arifos/
COPY 000_THEORY/ 000_THEORY/
COPY setup/ setup/

# Set environment variables
ENV PYTHONPATH=/app
ENV ARIFOS_MODE=production

# Expose the Body API port
EXPOSE 8000

# Run the Body API server
CMD ["python", "-m", "arifos.api.server"]
