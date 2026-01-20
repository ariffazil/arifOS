# arifOS VAULT Server Dockerfile (v49.1)
# Trinity Architecture: Memory Layer (000 INIT / 999 VAULT)
# Floors: F1-F13 (All floors for root validation)
#
# Build: docker build -t arifos-vault:v49.1 -f servers/vault/Dockerfile .
# Run: docker run -p 9000:9000 arifos-vault:v49.1

FROM python:3.11.8-slim

# Labels
LABEL org.opencontainers.image.title="arifOS VAULT Server"
LABEL org.opencontainers.image.description="Constitutional Memory Layer - 000 INIT / 999 VAULT"
LABEL org.opencontainers.image.version="v49.1.0"
LABEL maintainer="Arif Fazil <arifbfazil@gmail.com>"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ARIFOS_MODE=VAULT
ENV ARIFOS_VERSION=v49.1.0
ENV ARIFOS_FLOORS=F1-F13

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

# Create vault directories
RUN mkdir -p /app/vault_999/AAA_MEMORY \
    /app/vault_999/BBB_LEDGER/LAYER_3_AUDIT \
    /app/vault_999/CCC_CONSTITUTIONAL/LAYER_1_FOUNDATION \
    /app/vault_999/CCC_CONSTITUTIONAL/LAYER_2_PERMANENT \
    /app/vault_999/CCC_CONSTITUTIONAL/LAYER_3_PROCESSING \
    /app/vault_999/INFRASTRUCTURE/cooling_ledger \
    && chown -R arifos:arifos /app/vault_999

# Switch to non-root
USER arifos

# Expose port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9000/health || exit 1

# Start server
CMD ["python", "-m", "arifos.servers.vault_server"]
