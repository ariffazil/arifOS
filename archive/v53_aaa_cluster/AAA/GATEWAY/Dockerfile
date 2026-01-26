# arifOS AAA Gateway (v52.4.0)
# The Router - Circuit Breaker & Auth
# DITEMPA BUKAN DIBERI

FROM python:3.12-slim

ARG VERSION=52.4.0

LABEL maintainer="arifOS Team"
LABEL version="${VERSION}"
LABEL role="GATEWAY"

ENV PYTHONUNBUFFERED=1
ENV PYTHONTDONTWRITEBYTECODE=1
ENV ARIFOS_ENV=production
ENV ARIFOS_ROLE=GATEWAY
ENV PORT=9000

# Set internal service URLs (Defaults for Railway Private Networking)
ENV AXIS_URL=http://axis:8001
ENV ARIF_URL=http://arif:8002
ENV APEX_URL=http://apex:8003

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy arifos core package
COPY pyproject.toml setup.py ./
COPY arifos/ ./arifos/

# Install arifos core + api deps
RUN pip install --no-cache-dir -e ".[api]"
RUN pip install --no-cache-dir httpx

# Copy Gateway server
COPY deploy/AAA/GATEWAY/server.py ./server.py

# Create non-root user
RUN useradd -m -u 1000 arifos && \
    chown -R arifos:arifos /app
USER arifos

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

CMD ["python", "server.py"]
