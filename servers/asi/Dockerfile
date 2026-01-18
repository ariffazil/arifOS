# Dockerfile for ASI Server (555/666)
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY arifos_core/ /app/arifos_core/

EXPOSE 9002

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:9002/health || exit 1

CMD ["python", "-m", "uvicorn", "arifos_core.servers.asi_server:app", "--host", "0.0.0.0", "--port", "9002"]
