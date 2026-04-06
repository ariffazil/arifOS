# arifOS MCP Server — Production Dockerfile
# ═══════════════════════════════════════════════════════════════════════════════
# 
# Build: docker build -t arifos-mcp:latest -f deployments/af-forge/Dockerfile .
# Run:   docker run -p 3000:3000 -e ARIFOS_MCP_TRANSPORT=http arifos-mcp:latest
#
# Multi-stage build for optimized production image

# ─── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY pyproject.toml ./
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --user \
    fastmcp>=2.0.0 \
    fastapi>=0.110.0 \
    httpx>=0.27.0 \
    pydantic>=2.0.0 \
    py-ecc>=7.0.0 \
    starlette>=0.37.0 \
    uvicorn>=0.29.0

# ─── Stage 2: Production ──────────────────────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

# Create non-root user for security
RUN groupadd -r arifos && useradd -r -g arifos arifos

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/arifos/.local
ENV PATH=/home/arifos/.local/bin:$PATH

# Copy application code
COPY --chown=arifos:arifos arifosmcp/ ./arifosmcp/
COPY --chown=arifos:arifos core/ ./core/
COPY --chown=arifos:arifos static/ ./static/
COPY --chown=arifos:arifos config/ ./config/
COPY --chown=arifos:arifos server.py ./

# Build metadata (passed at build time)
ARG ARIFOS_BUILD_SHA=dev
ARG ARIFOS_BUILD_TIME=unknown
ARG ARIFOS_APP_VERSION=2026.04.06

ENV ARIFOS_BUILD_SHA=${ARIFOS_BUILD_SHA}
ENV ARIFOS_BUILD_TIME=${ARIFOS_BUILD_TIME}
ENV ARIFOS_APP_VERSION=${ARIFOS_APP_VERSION}
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER arifos

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Expose port
EXPOSE 3000

# Default: stdio for local, override to http for production
ENV ARIFOS_MCP_TRANSPORT=http
ENV ARIFOS_MCP_HOST=0.0.0.0
ENV ARIFOS_MCP_PORT=3000

# Run the MCP server
CMD ["python", "-m", "arifosmcp.runtime.server"]
