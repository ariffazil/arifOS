# arifOS MCP Server — Railway Production
FROM python:3.12-slim

# Install system deps (git for MCP, etc.)
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy repo
WORKDIR /app
COPY . /app

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Run Constitutional Forge (v50.0.0)
RUN python scripts/forge_railway.py

# Create non-root user
RUN useradd -m arifos && chown -R arifos:arifos /app
USER arifos

# Expose MCP stdio port (Railway binds $PORT)
EXPOSE 8000

# Health check (000_init)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start MCP server via verified startup script (using shell form for variable expansion)
CMD ["/bin/sh", "-c", "bash scripts/railway_start_mcp.sh"]
