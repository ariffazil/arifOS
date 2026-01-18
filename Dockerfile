# arifOS v47 Constitutional Governance API - Multi-Stage Build
#
# Build:
#   docker build -t arifos-api:v47 .
#
# Run:
#   docker run -p 8000:8000 arifos-api:v47
#
# Health check:
#   curl http://localhost:8000/health

###############################################################################
# Stage 1: Builder - Install dependencies and build artifacts
###############################################################################
FROM python:3.11.8-slim as builder

# Build arguments
ARG ARIFOS_VERSION=v47.0.0
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
LABEL org.opencontainers.image.licenses="Constitutional License v46"

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
COPY pyproject.toml README.md requirements.txt . ./

# Install dependencies to a specific directory
RUN pip install --prefix=/install --no-warn-script-location -r requirements.txt

# Copy application source
COPY arifos_core/ ./arifos_core/
COPY L1_THEORY/ ./L1_THEORY/
COPY L2_PROTOCOLS/ ./L2_PROTOCOLS/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Install arifOS package
RUN pip install --prefix=/install --no-warn-script-location -e .

###############################################################################
# Stage 2: Runtime - Minimal production image
###############################################################################
FROM python:3.11.8-slim

# Build arguments
ARG ARIFOS_VERSION=v47.0.0
ARG BUILD_DATE
ARG VCS_REF

# Metadata
LABEL org.opencontainers.image.title="arifOS API Server" \
    org.opencontainers.image.description="Constitutional AI Governance Kernel" \
    org.opencontainers.image.version=$ARIFOS_VERSION \
    org.opencontainers.image.created=$BUILD_DATE \
    org.opencontainers.image.revision=$VCS_REF \
    org.opencontainers.image.licenses="Constitutional License v47" \
    maintainer="Arif Fazil <arif@arif-fazil.com>"

# Runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ARIFOS_ENV=production
ENV ARIFOS_VERSION=${ARIFOS_VERSION}
ENV PATH=/usr/local/lib/python3.11/site-packages:/usr/local/bin:$PATH

# Create non-root user for security (F6 Amanah - Safety principle)
RUN groupadd --gid 1000 arifos && \
    useradd --uid 1000 --gid arifos --shell /bin/bash --create-home arifos && \
    mkdir -p /app /app/ledger /app/sessions /app/logs && \
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
COPY --chown=arifos:arifos arifos_core/ ./arifos_core/
COPY --chown=arifos:arifos L1_THEORY/ ./L1_THEORY/
COPY --chown=arifos:arifos L2_PROTOCOLS/ ./L2_PROTOCOLS/
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
# Note: VOLUME directive is removed for Railway compatibility. Use persistent storage mounts.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the Constitutional SSE server (v49 unified entry point)
CMD ["python", "-m", "arifos.mcp", "sse"]
