# Dockerfile for arifOS Constitutional Monolith (v53.1.0-CODEBASE)
# Single solid container for MCP SSE + Body API
# Railway-compatible: Uses codebase-mcp-sse entry point

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

# Copy codebase (v53+ canonical module)
COPY codebase/ codebase/
# Fix: Copy 000_THEORY which actually exists, not L1_THEORY
COPY 000_THEORY/ 000_THEORY/
# Docs are good to have
COPY docs/ docs/
# Setup scripts
COPY setup/ setup/

# Install package in editable mode (includes both arifos and codebase)
RUN uv pip install --system -e .

# Set environment variables
ENV PYTHONPATH=/app
ENV ARIFOS_MODE=production
ENV ARIFOS_MCP_MODE=bridge
# PORT is set by Railway dynamically

# Expose port
EXPOSE 8000

# Health check (matches railway.toml healthcheckPath)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run Codebase MCP SSE server
# Uses PORT env var from Railway (defaults to 8000 for local)
CMD ["sh", "-c", "codebase-mcp-sse"]
