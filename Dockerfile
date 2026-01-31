# Dockerfile for arifOS Constitutional Monolith (v55.1-CODEBASE-AAA)
# Streamable HTTP MCP server + health/metrics endpoints
# Railway-compatible: uses codebase-mcp-sse entry point (FastMCP)

FROM python:3.12-slim

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
# Explicit runtime deps for FastMCP streamable HTTP
RUN uv pip install --system --no-cache fastapi uvicorn[standard] pydantic mcp sse-starlette httpx-sse

# Copy codebase (v55+ canonical module)
COPY codebase/ codebase/
# Copy static dashboard files
COPY codebase/mcp/static/ codebase/mcp/static/
# Copy constitutional theory bundle
COPY 000_THEORY/ 000_THEORY/
# Docs for runtime reference
COPY docs/ docs/
# Setup scripts
COPY setup/ setup/

# Install package in editable mode (includes both arifos and codebase)
RUN uv pip install --system -e .

# Set environment variables
ENV PYTHONPATH=/app
ENV ARIFOS_MODE=production
ENV ARIFOS_MCP_MODE=sse
ENV HOST=0.0.0.0
ENV PORT=8080

# Expose port
EXPOSE 8080

# Health check (matches railway.toml healthcheckPath)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run Codebase MCP streamable HTTP server
CMD ["codebase-mcp-sse"]
