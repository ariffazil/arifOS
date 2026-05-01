# ── arifOS AAA MCP Server ──────────────────────────────────────────────
# Single process, single port. Runs FastMCP streamable-HTTP transport
# with REST endpoints (/health, /tools, /version) as custom routes.
# Hardened for Production (v2026.05.01-KANON)
# ───────────────────────────────────────────────────────────────────────

FROM python:3.12-slim AS build

# Build-time environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Deployment identity — set at docker build via --build-arg
ARG ARIFOS_BUILD_SHA=unknown
ARG ARIFOS_BUILD_TIME=unknown
ARG ARIFOS_BUILD_BRANCH=unknown
ENV DEPLOY_GIT_COMMIT=${ARIFOS_BUILD_SHA}
ENV DEPLOY_GIT_BRANCH=${ARIFOS_BUILD_BRANCH}
ENV DEPLOY_BUILD_TIME=${ARIFOS_BUILD_TIME}

WORKDIR /usr/src/app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Initialize git submodules (arifOS-model-registry)
#RUN git submodule update --init --recursive

# Install dependencies in build stage to keep runtime image clean
# NOTE: torch is NOT installed separately — sentence-transformers moved to optional deps.
# Embeddings are served by Ollama (bge-m3:latest) as an external service.
RUN python -m pip install --upgrade pip && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi && \
    pip install --no-cache-dir .

# Install WebMCP dependencies (F12/F11 constitutional web gateway)
RUN pip install --no-cache-dir itsdangerous prefab-ui fastapi uvicorn redis python-multipart psutil
RUN pip install --no-cache-dir "fastapi>=0.100.0"
# NOTE: fastmcp >=3.2.4 function_parsing.py is fragile.
# Do NOT patch it with sed — use a pinned version or upstream fix instead.
# If you hit "invalid syntax", rebuild with: docker build --no-cache .

# Remove pip-installed arifosmcp from site-packages to avoid conflict with /usr/src/app source
RUN rm -rf /usr/local/lib/python3.12/site-packages/arifosmcp*

# BGE-M3 model is served by Ollama (ollama_engine container).
# No local HuggingFace model baking required — eliminates ~750MB torch + ~570MB model from image.


FROM python:3.12-slim AS runtime

# Create non-root user (F11 Authority / F1 Law)
RUN groupadd -g 1000 arifos && \
    useradd -u 1000 -g arifos -m -s /bin/bash arifos

WORKDIR /app

# Build arguments for OCI labels (passed via --build-arg from build stage)
ARG ARIFOS_BUILD_SHA=unknown
ARG ARIFOS_BUILD_BRANCH=unknown
ARG ARIFOS_BUILD_TIME=unknown

# Environment configuration
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8080
ENV HOST=0.0.0.0
ENV AAA_MCP_TRANSPORT=http
# DEPLOY_GIT_COMMIT/BRANCH/TIME are what server.py reads — wire them from build-arg
ENV DEPLOY_GIT_COMMIT=${ARIFOS_BUILD_SHA}
ENV DEPLOY_GIT_BRANCH=${ARIFOS_BUILD_BRANCH}
ENV DEPLOY_BUILD_TIME=${ARIFOS_BUILD_TIME}

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Copy artifacts from build stage
COPY --from=build /usr/local /usr/local
COPY . .

# Setup dirs, fix ownership
RUN mkdir -p telemetry data memory static/dashboard && rm -rf VAULT999 && mkdir -p VAULT999
RUN mkdir -p /ms-playwright && chown -R arifos:arifos /app /ms-playwright

# ── Volume-mount override ──────────────────────────────────────────────
# A .pth file that inserts /app (volume mount) at sys.path position 0.
# This lets local dev / host-mounted code override the image-baked
# site-packages without requiring a rebuild.  The image ships with
# stale site-packages (from the build stage pip install); the volume
# mount at /app always has HEAD.  By prepending /app we guarantee the
# volume-mounted code is preferred over the image's built packages.
RUN echo -e "import sys, os\\n\\n# /app is the canonical volume mount\\napp_pth = '/app'\\nif app_pth not in sys.path:\\n    sys.path.insert(0, app_pth)" > "/usr/local/lib/python3.12/site-packages/arifos-app-override.pth"

# Install Playwright browser deterministically
#RUN python -m playwright install --with-deps chromium && \
#    chown -R arifos:arifos /ms-playwright

# Switch to non-root user for runtime (F11 Authority / F1 Law)
USER arifos

# Expose canonical MCP port
EXPOSE 8080

# Production Healthcheck (F12 Defense)
HEALTHCHECK --interval=20s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS --max-time 3 http://localhost:8080/health || exit 1

# Metadata Labels — OCI image spec for immutable provenance
# Uses ENV variables (DEPLOY_GIT_COMMIT, DEPLOY_BUILD_TIME) since those
# are populated from ARG at build time and correctly expand in LABEL.
LABEL io.modelcontextprotocol.server.name="io.github.ariffazil/arifosmcp" \
      io.modelcontextprotocol.server.version="${DEPLOY_GIT_COMMIT}" \
      io.modelcontextprotocol.server.description="Constitutional AI governance server with 13 canonical MCP capability tools. Diagnostics are internal runtime only." \
      org.opencontainers.image.revision="${DEPLOY_GIT_COMMIT}" \
      org.opencontainers.image.created="${DEPLOY_BUILD_TIME}" \
      org.opencontainers.image.source="https://github.com/ariffazil/arifOS" \
      org.opencontainers.image.licenses="MIT"

# Execute consolidated entrypoint
CMD ["uvicorn", "arifosmcp.runtime.server:app", "--host", "0.0.0.0", "--port", "8080"]
