# arifOS ARIF Server (v52.4.0)
# The Architect (Nexus) - Mind & Heart
# DITEMPA BUKAN DIBERI

FROM python:3.12-slim

ARG VERSION=52.4.0

LABEL maintainer="arifOS Team"
LABEL version="${VERSION}"
LABEL description="arifOS ARIF Server - Mind & Heart"
LABEL role="ARIF"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ARIFOS_ENV=production
ENV ARIFOS_ROLE=ARIF
ENV ARIFOS_VERSION=${VERSION}
ENV PORT=8002

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy arifos core package
COPY pyproject.toml setup.py ./
COPY arifos/ ./arifos/

# Install arifos core with LLM support (heavy compute)
RUN pip install --no-cache-dir -e ".[api,litellm]"

# Copy ARIF server files
COPY deploy/AAA/ARIF/server.py ./server.py
COPY deploy/AAA/ARIF/requirements.txt ./requirements.txt

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
