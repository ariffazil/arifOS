# arifOS ASI Server Dockerfile (v49.1)
# Trinity Architecture: Heart Layer (555 EMPATHY / 666 ACT)
# Floors: F1 (Amanah), F5 (Peace), F6 (Empathy), F9 (C_dark), F11 (Auth), F12 (Injection)
#
# Build: docker build -t arifos-asi:v49.1 -f servers/asi/Dockerfile .
# Run: docker run -p 9002:9002 arifos-asi:v49.1

FROM python:3.11.8-slim

# Labels
LABEL org.opencontainers.image.title="arifOS ASI Server"
LABEL org.opencontainers.image.description="Constitutional Heart Layer - Omega Kernel"
LABEL org.opencontainers.image.version="v49.1.0"
LABEL maintainer="Arif Fazil <arifbfazil@gmail.com>"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ARIFOS_MODE=ASI
ENV ARIFOS_VERSION=v49.1.0
ENV ARIFOS_FLOORS=F1,F5,F6,F9,F11,F12

# Create non-root user (F6 Amanah - Security)
RUN groupadd --gid 1000 arifos && \
    useradd --uid 1000 --gid arifos --shell /bin/bash --create-home arifos

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy arifOS codebase
COPY --chown=arifos:arifos arifos/ ./arifos/
COPY --chown=arifos:arifos 000_THEORY/ ./000_THEORY/
COPY --chown=arifos:arifos pyproject.toml README.md ./

# Install arifOS
RUN pip install --no-cache-dir -e .

# Switch to non-root
USER arifos

# Expose port
EXPOSE 9002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9002/health || exit 1

# Start server
CMD ["python", "-m", "arifos.servers.asi_server"]
