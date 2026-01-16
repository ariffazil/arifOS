# arifOS v45 FastAPI Server Dockerfile
#
# Build:
#   docker build -t arifos-api .
#
# Run:
#   docker run -p 8000:8000 arifos-api
#
# With Qdrant:
#   docker-compose up
#
# NOTE: Body API (arifos_core.api.app) is planned for L7_DEMOS/body_api/
#       This Dockerfile will be updated when Body API is implemented.

FROM python:3.11-slim

# Labels
LABEL maintainer="arifOS Project <arifbfazil@gmail.com>"
LABEL version="v45.0.0"
LABEL description="arifOS Constitutional Governance API (Sovereign Witness)"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ARIFOS_ENV=production
ENV ARIFOS_VERSION=v45.0.0

# Create non-root user for security
RUN groupadd --gid 1000 arifos && \
    useradd --uid 1000 --gid arifos --shell /bin/bash --create-home arifos

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml README.md ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi>=0.100.0 \
    uvicorn[standard]>=0.23.0 \
    pydantic>=2.0.0 \
    numpy>=1.20.0

# Copy application code
COPY arifos_core/ ./arifos_core/
COPY scripts/ ./scripts/
COPY L1_THEORY/ ./L1_THEORY/
COPY L2_GOVERNANCE/ ./L2_GOVERNANCE/
COPY spec/ ./spec/

# Install arifOS in editable mode
RUN pip install --no-cache-dir -e .

# Change ownership to non-root user
RUN chown -R arifos:arifos /app

# Switch to non-root user
USER arifos

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the server
CMD ["uvicorn", "arifos_core.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
