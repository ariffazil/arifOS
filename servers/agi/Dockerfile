# Dockerfile for AGI Server (111/222/333)
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy arifOS packages (Phase 8.3: Add canonical validators)
COPY arifos/ /app/arifos/
COPY arifos_core/ /app/arifos_core/

EXPOSE 9001

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:9001/health || exit 1

CMD ["python", "-m", "uvicorn", "arifos_core.servers.agi_server:app", "--host", "0.0.0.0", "--port", "9001"]
