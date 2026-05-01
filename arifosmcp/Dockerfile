# ── arifOS MCP Runtime — Lean Multi-Stage Build ──────────────────────────
# Package truth: /app/arifosmcp/ is the Python package
# PYTHONPATH=/app only — no multi-path chaos
#
# Build:  docker build -t ghcr.io/ariffazil/arifos:latest -f arifosmcp/Dockerfile .
# Run:    docker run --rm ghcr.io/ariffazil/arifos:latest python -m arifosmcp.runtime.__main__
# ─────────────────────────────────────────────────────────────────────────

# ── Stage 1: dependency installer ────────────────────────────────────────
FROM python:3.12-slim AS deps

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /install

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    VPS_MODE=1 \
    ARIFOS_DEPLOYMENT=vps

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from deps stage
COPY --from=deps /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy package source as /app/arifosmcp (not nested under a subfolder)
COPY arifosmcp /app/arifosmcp
COPY core /app/core
COPY pyproject.toml /app/

# Install runtime-only deps not in requirements.txt
RUN pip install blake3==1.0.8 "fastapi>=0.100.0" "langfuse>=2.0.0"

# Non-root user
RUN useradd -m -u 1000 arifos && chown -R arifos:arifos /app
USER arifos

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "arifosmcp.runtime.__main__"]
