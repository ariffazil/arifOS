# arifOS APEX Server (v52.4.0)
# The Summit (Judge) - Soul
# DITEMPA BUKAN DIBERI

FROM python:3.12-slim

ARG VERSION=52.4.0

LABEL maintainer="arifOS Team"
LABEL version="${VERSION}"
LABEL description="arifOS APEX Server - Constitutional Judge"
LABEL role="APEX"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ARIFOS_ENV=production
ENV ARIFOS_ROLE=APEX
ENV ARIFOS_VERSION=${VERSION}
ENV PORT=8003

WORKDIR /app

# Install system dependencies (minimal for isolation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy arifos core package
COPY pyproject.toml setup.py ./
COPY arifos/ ./arifos/

# Install arifos core (minimal, no litellm)
RUN pip install --no-cache-dir -e ".[api]"

# Copy APEX server files
COPY deploy/AAA/APEX/server.py ./server.py
COPY deploy/AAA/APEX/requirements.txt ./requirements.txt

# Create non-root user with high isolation
RUN useradd -m -u 1000 arifos && \
    chown -R arifos:arifos /app
USER arifos

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

# SSE transport for Railway (--transport sse)
CMD ["python", "server.py", "--transport", "sse"]
