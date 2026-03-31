# Dockerfile — GEOX MCP Server
# DITEMPA BUKAN DIBERI
# Muhammad Arif bin Fazil | PETRONAS Exploration
#
# Multi-stage build for optimized production image
# Supports both STDIO (local) and HTTP (Prefect Horizon / remote) transport
#
# Build:
#   docker build -t geox-earth-witness .
#
# Run (STDIO):
#   docker run --rm geox-earth-witness
#
# Run (HTTP):
#   docker run --rm -p 8081:8081 geox-earth-witness --http --host 0.0.0.0 --port 8081
#
# Run (Prefect Horizon / cloud):
#   docker push your-registry/geox-earth-witness
#   # Then configure in Horizon UI

# ---------------------------------------------------------------------------
# Stage 1: Builder
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy and install dependencies
COPY pyproject.toml ./
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy source
COPY . .

# Install the package in editable mode
RUN uv pip install --system --no-cache -e .

# ---------------------------------------------------------------------------
# Stage 2: Production
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS production

# Security: run as non-root user
RUN useradd --create-home --shell /bin/bash geox \
    && chown -R geox:geox /home/geox

WORKDIR /home/geox

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /home/geox /home/geox

# Copy only the MCP server entrypoint
COPY --chown=geox:geox geox_mcp_server.py .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ARIFOS_ENV=production
ENV GEOSCIENCE_MODE=governed
ENV LOG_LEVEL=info

# Switch to non-root user
USER geox

# Expose port (for HTTP transport)
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8081/health')" || exit 1

# Default: HTTP transport for Prefect Horizon compatibility
ENTRYPOINT ["python", "geox_mcp_server.py"]
CMD ["--http", "--host", "0.0.0.0", "--port", "8081"]

# Alternative transports:
#   STDIO (local dev): docker run --rm geox-earth-witness python geox_mcp_server.py
#   HTTP custom port:  docker run --rm -p 9000:9000 geox-earth-witness --http --port 9000

# Labels
LABEL org.opencontainers.image.title="GEOX — Geological Intelligence Coprocessor"
LABEL org.opencontainers.image.description="Governed, agentic geological intelligence for arifOS"
LABEL org.opencontainers.image.version="0.4.0"
LABEL org.opencontainers.image.authors="Muhammad Arif bin Fazil <ariffazil@gmail.com>"
LABEL org.opencontainers.image.license="AGPL-3.0"
LABEL org.opencontainers.image.source="https://github.com/ariffazil/GEOX"
LABEL org.arifos.seal="DITEMPA BUKAN DIBERI"
