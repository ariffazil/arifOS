# arifOS MCP Server — AF-FORGE Production Dockerfile
# ═══════════════════════════════════════════════════════════════════════════════
# 
# Build: docker build -t arifosmcp:af-forge -f deployments/af-forge/Dockerfile .
# Run:   docker run -p 3000:3000 -e ARIFOSMCP_TRANSPORT=http arifosmcp:af-forge

FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r arifos && useradd -r -g arifos arifos

# Copy and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e . 2>/dev/null || pip install --no-cache-dir fastmcp fastapi uvicorn starlette pydantic httpx

# Copy application code
COPY --chown=arifos:arifos arifosmcp/ ./arifosmcp/
COPY --chown=arifos:arifos core/ ./core/
COPY --chown=arifos:arifos static/ ./static/

# Build metadata (passed at build time)
ARG ARIFOS_BUILD_SHA=dev
ARG ARIFOS_BUILD_TIME=unknown
ARG ARIFOS_APP_VERSION=2026.04.06

ENV ARIFOS_BUILD_SHA=${ARIFOS_BUILD_SHA}
ENV ARIFOS_BUILD_TIME=${ARIFOS_BUILD_TIME}
ENV ARIFOS_APP_VERSION=${ARIFOS_APP_VERSION}
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create required directories
RUN mkdir -p /app/VAULT999 /app/telemetry /app/data && chown -R arifos:arifos /app

# Switch to non-root user
USER arifos

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Expose port
EXPOSE 3000

# Default: HTTP/streamable-http for production
ENV ARIFOSMCP_TRANSPORT=http
ENV ARIFOSMCP_HOST=0.0.0.0
ENV ARIFOSMCP_PORT=3000

# Run the MCP server
CMD ["python", "-m", "arifosmcp.runtime.__main__"]
