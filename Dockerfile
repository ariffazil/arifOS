# Dockerfile for arifOS Constitutional MCP Server (v55.1-CODEBASE-AAA)
# Streamable HTTP transport + health/metrics endpoints
# Railway-compatible: uses codebase-mcp-sse entry point (FastMCP)

FROM python:3.12-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Layer 1: Install Python dependencies (cached unless requirements change)
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Layer 2: Copy project metadata + source
COPY pyproject.toml .
COPY codebase/ codebase/

# Layer 3: Install package (registers entry points like codebase-mcp-sse)
RUN uv pip install --system --no-deps -e .

# Layer 4: Copy constitutional data (changes less often than code)
COPY 000_THEORY/ 000_THEORY/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ARIFOS_MODE=production
ENV ARIFOS_MCP_MODE=sse
ENV HOST=0.0.0.0
ENV PORT=8080

# Expose port
EXPOSE 8080

# Health check (matches railway.toml healthcheckPath)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -sf http://localhost:8080/health || exit 1

# Run Codebase MCP Streamable HTTP server
CMD ["codebase-mcp-sse"]
