# ── arifOS MCP Runtime — Lean Multi-Stage Build ──────────────────────────
# Package truth: /app/arifosmcp/ is the Python package
# PYTHONPATH=/app only — no multi-path chaos
#
# Build:  docker build \
#           --build-arg ARIFOS_BUILD_SHA=$(git rev-parse --short HEAD) \
#           --build-arg ARIFOS_BUILD_BRANCH=$(git rev-parse --abbrev-ref HEAD) \
#           --build-arg ARIFOS_BUILD_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
#           -t ghcr.io/ariffazil/arifos:latest \
#           -f arifosmcp/Dockerfile .
# Run:    docker run --rm ghcr.io/ariffazil/arifos:latest python -m arifosmcp.runtime.__main__
#
# Git metadata is baked in at build time and exposed via:
#   ENV DEPLOY_GIT_COMMIT, DEPLOY_GIT_BRANCH, DEPLOY_BUILD_TIME
#   LABEL io.modelcontextprotocol.server.version, org.opencontainers.image.revision
# ─────────────────────────────────────────────────────────────────────────

# ── Stage 1: dependency installer ────────────────────────────────────────
FROM python:3.12-slim AS deps

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /install

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip pip install uv

COPY arifosmcp/requirements-lean.txt requirements-lean.txt

# ── Lean runtime: heuristic-only, no ML packages ─────────────────────────
# Semantic floors use fast heuristic fallback. Full ML (torch, SBERT) can be
# installed at runtime if needed. numpy>=2.0 for generic compatibility.
RUN --mount=type=cache,target=/root/.cache/pip \
    uv pip install --system -r requirements-lean.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Build-time git metadata — set via --build-arg at docker build
ARG ARIFOS_BUILD_SHA=unknown
ARG ARIFOS_BUILD_BRANCH=unknown
ARG ARIFOS_BUILD_TIME=unknown

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    VPS_MODE=1 \
    ARIFOS_DEPLOYMENT=vps

# Embed git metadata as runtime env vars (server.py reads DEPLOY_GIT_*)
ENV DEPLOY_GIT_COMMIT=${ARIFOS_BUILD_SHA}
ENV DEPLOY_GIT_BRANCH=${ARIFOS_BUILD_BRANCH}
ENV DEPLOY_BUILD_TIME=${ARIFOS_BUILD_TIME}

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from deps stage
COPY --from=deps /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=deps /usr/local/bin /usr/local/bin

# Verify aiohttp is installed (uv --system may skip if already present but version differs)
# Use pip as fallback since uv may not own all packages in --system mode
RUN uv pip install --system aiohttp 2>/dev/null || pip install --break-system-packages aiohttp 2>/dev/null || true

# Copy package source as /app/arifosmcp (not nested under a subfolder)
COPY arifosmcp /app/arifosmcp
COPY core /app/core
COPY pyproject.toml /app/

# Install runtime-only deps — heuristic-only build (no torch/sentence-transformers).
# ML semantic floors use fast heuristic fallback. Full ML packages (torch, SBERT)
# can be installed at runtime if needed. langfuse SDK goes to system Python.
RUN --mount=type=cache,target=/root/.cache/pip pip install blake3==1.0.8 "fastapi>=0.100.0" "langfuse>=2.0.0"

# Non-root user
RUN useradd -m -u 1000 arifos && chown -R arifos:arifos /app
USER arifos

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# OCI metadata labels — immutable provenance baked at build time
LABEL io.modelcontextprotocol.server.name="io.github.ariffazil/arifosmcp" \
      io.modelcontextprotocol.server.version="${ARIFOS_BUILD_SHA}" \
      io.modelcontextprotocol.server.description="Constitutional AI governance server with 13 canonical MCP capability tools. Diagnostics are internal runtime only." \
      org.opencontainers.image.revision="${ARIFOS_BUILD_SHA}" \
      org.opencontainers.image.created="${ARIFOS_BUILD_TIME}" \
      org.opencontainers.image.source="https://github.com/ariffazil/arifOS" \
      org.opencontainers.image.licenses="MIT"

CMD ["python", "-m", "arifosmcp.runtime.__main__"]
