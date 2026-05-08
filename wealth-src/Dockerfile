# Use a multi-stage build or a single image with both runtimes
FROM python:3.12-slim-bookworm

# Install Node.js (needed for WEALTH CLI logic)
RUN apt-get update && apt-get install -y curl git && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy package.json and install Node dependencies
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Copy pyproject.toml and install Python dependencies
# Use UV_SKIP_WHEEL_FILENAME_CHECK to allow lock file version flexibility
COPY pyproject.toml ./
COPY uv.lock ./
RUN UV_SKIP_WHEEL_FILENAME_CHECK=1 uv sync --no-dev

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV NODE_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose canonical HTTP transport port
ENV PORT=8082
EXPOSE 8082

# Default command: Run the FastMCP server
# Use --transport sse if deploying to cloud, or keep default for stdio
# Canonical implementation is internal/monolith.py (AGENTS.md Tier A).
# server.py is a thin backward-compat wrapper.
ENTRYPOINT ["python", "internal/monolith.py"]
