# Dockerfile for VAULT Server (000/999)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy arifOS packages (Phase 8.3: Add canonical validators + canon)
COPY arifos/ /app/arifos/
COPY arifos_core/ /app/arifos_core/
COPY 000_THEORY/ /app/000_THEORY/

# Create vault directory
RUN mkdir -p /app/vault_999/BBB_LEDGER/LAYER_3_AUDIT

# Expose port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:9000/health || exit 1

# Run VAULT server
CMD ["python", "-m", "uvicorn", "arifos_core.servers.vault_server:app", "--host", "0.0.0.0", "--port", "9000"]
