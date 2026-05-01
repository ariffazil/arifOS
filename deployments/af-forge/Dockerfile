# arifOS MCP Server — A-FORGE Production Dockerfile
# ═══════════════════════════════════════════════════════════════════════════════
#
# Build: docker build -t arifosmcp:a-forge -f deployments/a-forge/Dockerfile .
# Run:   docker run -p 3000:3000 -e ARIFOSMCP_TRANSPORT=http arifosmcp:a-forge

FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r arifos && useradd -r -g arifos arifos

# Copy and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e . 2>/dev/null || pip install --no-cache-dir fastmcp fastapi uvicorn starlette pydantic httpx && \
    pip install --no-cache-dir pytesseract Pillow

# Copy application code
COPY --chown=arifos:arifos arifosmcp/ ./arifosmcp/
COPY --chown=arifos:arifos core/ ./core/
COPY --chown=arifos:arifos static/ ./static/

# Copy startup script
COPY --chown=arifos:arifos deployments/af-forge/startup.sh /usr/local/bin/startup.sh
RUN chmod +x /usr/local/bin/startup.sh

# Build metadata (passed at build time)
ARG ARIFOS_BUILD_SHA=dev
ARG ARIFOS_BUILD_TIME=unknown
ARG ARIFOS_APP_VERSION=2026.04.26

ENV ARIFOS_BUILD_SHA=${ARIFOS_BUILD_SHA}
ENV ARIFOS_BUILD_TIME=${ARIFOS_BUILD_TIME}
ENV ARIFOS_APP_VERSION=${ARIFOS_APP_VERSION}
ENV PYTHONPATH=/tmp/pylibs:/app
ENV PYTHONUNBUFFERED=1

# Create required directories
RUN mkdir -p /app/VAULT999 /app/telemetry /app/data /tmp/pylibs && chown -R arifos:arifos /app /tmp/pylibs

# Switch to non-root user
USER arifos

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Default: HTTP/streamable-http for production
ENV ARIFOSMCP_TRANSPORT=http
ENV ARIFOSMCP_HOST=0.0.0.0
ENV ARIFOSMCP_PORT=8080

# Run the bootstrapper
ENTRYPOINT ["/usr/local/bin/startup.sh"]
