# ── arifOS MCP Runtime — Lean Multi-Stage Build ──────────────────────────
# Target size: ~300-500MB (vs 6GB with heavy ML deps)
# Strategy: runtime deps only from requirements.txt (not full pyproject.toml)
# Code is volume-mounted at /usr/src/app in production — image provides env only.
#
# Build:  docker build -t arifos/arifosmcp:latest .
# Run:    docker compose up arifosmcp
# ─────────────────────────────────────────────────────────────────────────

# ── Stage 1: dependency installer ────────────────────────────────────────
FROM python:3.12-slim AS deps

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /install

# System packages needed to build Python wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast installs
RUN pip install uv

# Copy only dependency manifest (cached unless requirements.txt changes)
COPY requirements.txt .

# Install runtime deps into a separate prefix for clean copy
RUN uv pip install --system --no-cache -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/usr/src/app \
    VPS_MODE=1 \
    ARIFOS_DEPLOYMENT=vps

WORKDIR /usr/src/app

# Minimal runtime system packages only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from deps stage
COPY --from=deps /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy package source (overridden by volume mount in production)
# Copy arifosmcp package (build context is parent /arifOS/ directory)
COPY arifosmcp ./arifosmcp/

# Install the package itself (no deps — already installed above)
RUN pip install --no-deps -e ./arifosmcp/

# blake3 is required by core.organs._4_vault but not in requirements.txt
# Install it directly from PyPI
RUN pip install blake3==1.0.8

# Non-root user for security
RUN useradd -m -u 1000 arifos && chown -R arifos:arifos /usr/src/app
USER arifos

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uvicorn", "arifosmcp.runtime.server:app", "--host", "0.0.0.0", "--port", "8080"]
