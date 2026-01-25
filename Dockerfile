# Dockerfile for arifOS Constitutional Monolith (v52.0.0-SEAL)
# Single solid container for MCP SSE + Body API

FROM python:3.11-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
COPY pyproject.toml .
# Use uv for faster installs
RUN uv pip install --system --no-cache -r requirements.txt
RUN uv pip install --system --no-cache fastapi uvicorn pydantic mcp sse-starlette httpx-sse

# Copy codebase
COPY arifos/ arifos/
COPY 000_THEORY/ 000_THEORY/
COPY docs/ docs/
COPY setup/ setup/

# Install package in editable mode
RUN uv pip install --system -e .

# Set environment variables
ENV PYTHONPATH=/app
ENV ARIFOS_MODE=production
ENV ARIFOS_MCP_MODE=bridge
ENV PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run Unified MCP SSE server
# This serves both the Body API and the MCP SSE protocol
CMD ["uv", "run", "python", "-m", "arifos.mcp.sse"]