# arifOS Trinity MCP Server
# Constitutional AI Governance Framework
# DITEMPA BUKAN DIBERI

FROM python:3.12-slim

# Build args
ARG VERSION=50.5.16
ARG BUILD_DATE

# Labels
LABEL maintainer="arifOS Team"
LABEL version="${VERSION}"
LABEL description="arifOS Trinity MCP Server - Constitutional AI Governance"

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ARIFOS_ENV=staging
ENV ARIFOS_VERSION=${VERSION}
ENV PORT=8000

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY pyproject.toml setup.py ./
COPY arifos/ ./arifos/

# Install dependencies
RUN pip install --no-cache-dir -e ".[api]"

# Copy remaining files
COPY VAULT999/ ./VAULT999/
COPY 000_THEORY/ ./000_THEORY/

# Create non-root user
RUN useradd -m -u 1000 arifos && \
    chown -R arifos:arifos /app
USER arifos

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Default command: SSE server for staging
CMD ["python", "-m", "arifos.mcp", "trinity-sse"]
