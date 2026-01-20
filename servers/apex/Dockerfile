# arifOS APEX Server Dockerfile (v49.1)
# Trinity Architecture: Soul Layer (444 EVIDENCE / 777 EUREKA / 888 SEAL / 889 PROOF)
# Floors: F3 (Tri-Witness), F8 (Genius)
#
# Build: docker build -t arifos-apex:v49.1 -f servers/apex/Dockerfile .
# Run: docker run -p 9003:9003 arifos-apex:v49.1

FROM python:3.11.8-slim

# Labels
LABEL org.opencontainers.image.title="arifOS APEX Server"
LABEL org.opencontainers.image.description="Constitutional Soul Layer - Psi Kernel"
LABEL org.opencontainers.image.version="v49.1.0"
LABEL maintainer="Arif Fazil <arifbfazil@gmail.com>"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ARIFOS_MODE=APEX
ENV ARIFOS_VERSION=v49.1.0
ENV ARIFOS_FLOORS=F3,F8

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
EXPOSE 9003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9003/health || exit 1

# Start server
CMD ["python", "-m", "arifos.servers.apex_server"]
