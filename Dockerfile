# Dockerfile for arifOS Constitutional Kernel (v52.0.0 SEAL)

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
COPY pyproject.toml .
RUN pip install --no-cache-dir -r requirements.txt
# Ensure MCP and SSE support are installed
RUN pip install fastapi uvicorn pydantic mcp sse-starlette httpx-sse

# Copy codebase
COPY arifos/ arifos/
COPY 000_THEORY/ 000_THEORY/
COPY docs/ docs/
COPY setup/ setup/

# Install package
RUN pip install -e .

# Set environment variables
ENV PYTHONPATH=/app
ENV ARIFOS_MODE=production
ENV ARIFOS_MCP_MODE=bridge
ENV PORT=8000

# Expose port
EXPOSE 8000

# Run unified MCP SSE server
CMD ["sh", "-c", "python -m arifos.mcp trinity-sse"]