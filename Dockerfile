# arifOS v49 Constitutional Governance API - Multi-Stage Build
#
# Build:
#   docker build -t arifos-api:v49 .
#
# Run:
#   docker run -p 8000:8000 arifos-api:v49
#
# Health check:
#   curl http://localhost:8000/health

###############################################################################
# Stage 1: Builder - Install dependencies and build artifacts
###############################################################################
FROM python:3.11.8-slim as builder

# Build arguments
ARG ARIFOS_VERSION=v49.0.0
ARG BUILD_DATE
ARG VCS_REF

# Labels (OCI annotations)
LABEL org.opencontainers.image.title="arifOS Constitutional API"
LABEL org.opencontainers.image.description="12-Floor Constitutional Governance System"
LABEL org.opencontainers.image.version="${ARIFOS_VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.source="https://github.com/ariffazil/arifOS"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.authors="Arif Fazil <arifbfazil@gmail.com>"
LABEL org.opencontainers.image.licenses="Constitutional License v49"

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better layer caching
COPY pyproject.toml README.md requirements.txt ./

# Install dependencies to a specific directory (no database for Railway)
RUN pip install --prefix=/install --no-warn-script-location -r requirements.txt

# Copy application source (v49 Structure)
COPY arifos/ ./arifos/
COPY 000_THEORY/ ./000_THEORY/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Install arifOS package
RUN pip install --prefix=/install --no-warn-script-location -e .

###############################################################################
# Stage 2: Runtime - Minimal production image
###############################################################################
FROM python:3.11.8-slim

# Build arguments
ARG ARIFOS_VERSION=v49.0.0
ARG BUILD_DATE
ARG VCS_REF

# Metadata
LABEL org.opencontainers.image.title="arifOS API Server" \
    org.opencontainers.image.description="Constitutional AI Governance Kernel" \
    org.opencontainers.image.version=$ARIFOS_VERSION \
    org.opencontainers.image.created=$BUILD_DATE \
    org.opencontainers.image.revision=$VCS_REF \
    org.opencontainers.image.licenses="Constitutional License v49" \
    maintainer="Arif Fazil <arif@arif-fazil.com>"

# Runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ARIFOS_ENV=production
ENV ARIFOS_VERSION=${ARIFOS_VERSION}
ENV PATH=/usr/local/lib/python3.11/site-packages:/usr/local/bin:$PATH
# Governance flags
ENV ARIFOS_ALLOW_LEGACY_SPEC=1
ENV ARIFOS_CONSTITUTIONAL_MODE=AAA
ENV ARIFOS_HUMAN_SOVEREIGN=Arif

# Create non-root user for security (F6 Amanah - Safety principle)
RUN groupadd --gid 1000 arifos && \
    useradd --uid 1000 --gid arifos --shell /bin/bash --create-home arifos && \
    mkdir -p /app /app/logs && \
    # Create Vault Structure for v47.1 Server
    mkdir -p /app/vault_999/CCC_CONSTITUTIONAL/LAYER_1_FOUNDATION && \
    mkdir -p /app/vault_999/CCC_CONSTITUTIONAL/LAYER_2_PERMANENT && \
    mkdir -p /app/vault_999/CCC_CONSTITUTIONAL/LAYER_3_PROCESSING/L2_active_state && \
    mkdir -p /app/vault_999/CCC_CONSTITUTIONAL/LAYER_3_PROCESSING/L3_phoenix_cooling && \
    mkdir -p /app/vault_999/CCC_CONSTITUTIONAL/LAYER_3_PROCESSING/L4_witness_observations && \
    mkdir -p /app/vault_999/CCC_CONSTITUTIONAL/LAYER_3_PROCESSING/L5_void_rejections && \
    mkdir -p /app/vault_999/BBB_MACHINE/LAYER_1_OPERATIONAL && \
    mkdir -p /app/vault_999/BBB_MACHINE/LAYER_2_WORKING && \
    mkdir -p /app/vault_999/BBB_MACHINE/LAYER_3_AUDIT && \
    mkdir -p /app/vault_999/INFRASTRUCTURE/cooling_ledger && \
    chown -R arifos:arifos /app

# Set work directory
WORKDIR /app

# Install curl in runtime for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from builder
COPY --from=builder --chown=arifos:arifos /install /usr/local

# Copy application code
COPY --chown=arifos:arifos arifos/ ./arifos/
COPY --chown=arifos:arifos 000_THEORY/ ./000_THEORY/
COPY --chown=arifos:arifos config/ ./config/
COPY --chown=arifos:arifos scripts/ ./scripts/
COPY --chown=arifos:arifos pyproject.toml README.md requirements.txt ./

# Install arifOS in editable mode
RUN pip install --no-cache-dir -e .

# Switch to non-root user (F6 Amanah - Security boundary)
USER arifos

# Expose API port
EXPOSE 8000

# Health check (F2 Truth - Verify system state)
# Railway overrides this with its own health check configuration
HEALTHCHECK --interval=10s --timeout=10s --start-period=45s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the Constitutional SSE server via Uvicorn
# Railway will override PORT via environment variable
# Use shell form to properly handle PORT variable
CMD ["/bin/sh", "-c", "exec uvicorn arifos.core.mcp.sse:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --log-level info"]
