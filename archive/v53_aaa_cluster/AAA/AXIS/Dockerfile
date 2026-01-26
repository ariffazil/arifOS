# arifOS AXIS Server (v52.4.0)
# Authority & Memory (Spine) - Alpha & Omega
# DITEMPA BUKAN DIBERI

FROM python:3.12-slim

ARG VERSION=52.4.0

LABEL maintainer="arifOS Team"
LABEL version="${VERSION}"
LABEL description="arifOS AXIS Server - Authority & Memory"
LABEL role="AXIS"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ARIFOS_ENV=production
ENV ARIFOS_ROLE=AXIS
ENV ARIFOS_VERSION=${VERSION}
ENV PORT=8001

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy arifos core package
COPY pyproject.toml setup.py ./
COPY arifos/ ./arifos/

# Install arifos core
RUN pip install --no-cache-dir -e ".[api]"

# Copy AXIS server files
COPY deploy/AAA/AXIS/server.py ./server.py
COPY deploy/AAA/AXIS/requirements.txt ./requirements.txt

# Copy VAULT for session persistence
COPY VAULT999/ ./VAULT999/

# Create sessions directory
RUN mkdir -p /app/arifos/mcp/sessions

# VOLUME: Critical for Loop Bootstrap crash recovery
# Without this, open_sessions.json is lost on container restart
# Railway: Must configure persistent volume via dashboard/CLI
VOLUME ["/app/arifos/mcp/sessions", "/app/VAULT999"]

# Create non-root user
RUN useradd -m -u 1000 arifos && \
    chown -R arifos:arifos /app
USER arifos

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

# SSE transport for Railway (--transport sse)
CMD ["python", "server.py", "--transport", "sse"]
