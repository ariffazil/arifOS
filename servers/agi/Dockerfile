# arifOS AGI Server Dockerfile (v49.1)
# Trinity Architecture: Mind Layer (111 SENSE / 222 THINK / 333 ATLAS)
# Floors: F2 (Truth), F4 (Clarity), F7 (Humility), F10 (Ontology), F13 (Curiosity)
#
# Build: docker build -t arifos-agi:v49.1 -f servers/agi/Dockerfile .
# Run: docker run -p 9001:9001 arifos-agi:v49.1

FROM python:3.11.8-slim

# Labels
LABEL org.opencontainers.image.title="arifOS AGI Server"
LABEL org.opencontainers.image.description="Constitutional Mind Layer - Delta Kernel"
LABEL org.opencontainers.image.version="v49.1.0"
LABEL maintainer="Arif Fazil <arifbfazil@gmail.com>"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ARIFOS_MODE=AGI
ENV ARIFOS_VERSION=v49.1.0
ENV ARIFOS_FLOORS=F2,F4,F7,F10,F13

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
EXPOSE 9001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9001/health || exit 1

# Start server
CMD ["python", "-m", "arifos.servers.agi_server"]
