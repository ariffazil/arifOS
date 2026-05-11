# AGENTS.md — GEOX / Physics9 Earth Witness

> **Constitutional Subsurface Reasoning Layer**
> DITEMPA BUKAN DIBERI — Forged, Not Given

This document is the canonical reference for AI coding agents working in this repository. It describes the project structure, build processes, development conventions, and governance constraints as they actually exist in the codebase.

---

## 1. Project Overview

**GEOX** (also referred to as **Physics9 Earth Witness**) is a governed AI orchestration platform for geoscience and subsurface intelligence. It acts as a *Judgment Engine* that sits above existing subsurface stacks, enforcing 13 constitutional floors (F1–F13) to separate observed data from inferred interpretation.

Every output must be physically grounded, geospatially verified, and audit-trail ready before it receives a verdict (`SEAL`, `PARTIAL`, `SABAR`, or `VOID`).

- **Live site:** https://geox.arif-fazil.com
- **MCP endpoint:** https://arifosmcp.arif-fazil.com/mcp
- **Health check:** https://geox.arif-fazil.com/health

---

## 2. Technology Stack

### Backend
- **Python 3.11+**
- **FastMCP 3.x** — MCP server framework
- **Pydantic 2.x** — Schema validation and contracts
- **Starlette + Uvicorn** — ASGI server for HTTP transport
- **pandas, numpy, pyproj, shapely, aiohttp** — Geoscience / geo-computation

### Frontend (`geox-gui/`)
- **React 19**, **TypeScript 5.x**, **Vite 5.x**
- **MapLibre GL 4** — 2D mapping
- **CesiumJS 1.114** — 3D globe / terrain
- **D3 7** — Well-log and data visualization
- **Zustand** — State management
- **Radix UI** — Headless accessible components
- **Tailwind CSS 3** — Styling

### Infrastructure
- **Docker + Docker Compose** — Containerization
- **Traefik** — Reverse proxy and TLS termination
- **Nginx (alpine)** — Static file serving for the frontend

---

## 3. Architecture & Code Organization

The codebase has two overlapping organizational schemes: the **legacy package layout** (`arifos/geox/`) and the **modern dimension-native layout** (`control_plane/`, `execution_plane/`, `services/`, `contracts/`, `geox/`).

### Modern Dimension-Native Layout (Canonical)

| Directory | Purpose |
|-----------|---------|
| `contracts/` | Pydantic schemas, enums, parity matrices, tool contracts |
| `control_plane/` | API routing, FastMCP canonical server (`fastmcp/server.py`), app manifests |
| `execution_plane/` | Calculation engines, VPS server (`vps/server.py`), dimensional kernels |
| `services/` | Evidence store, geo fabric, governance judge, witness engine (petrophysics) |
| `compatibility/` | Legacy adapters and backward-compatibility shims |
| `geox/core/` | Unified tool registry, AC-risk engine |
| `geox/dimensions/` | 7 canonical dimensions: `prospect/`, `well/`, `section/`, `earth_3d/`, `time_4d/`, `physics/`, `governance/` |
| `geox/apps/` | Micro-frontend manifests (`prospect-ui/`, `well-desk/`, `earth-volume/`, `judge-console/`) |
| `geox/shared/` | Shared schemas (`schemas/foundation.py`) and TypeScript contract packs |

### Legacy Package Layout (`arifos/geox/`)

Still actively used for core domain logic and tests:

| Layer | Key Files |
|-------|-----------|
| **THEORY** | `THEORY/contrast_taxonomy.py`, `contrast_governance.py`, `contrast_theory.py` |
| **ENGINE** | `ENGINE/contrast_space.py`, `anomaly_detector.py`, `transform_registry.py` |
| **TOOLS** | `tools/seismic/`, `tools/well_log_tool.py`, `tools/macrostrat_tool.py` |
| **GOVERNANCE** | `governance/floor_enforcer.py`, `audit_logger.py`, `verdict_renderer.py` |
| **Agent Core** | `geox_agent.py`, `geox_validator.py`, `geox_memory.py`, `geox_tools.py`, `geox_schemas.py` |

All MCP tools in this package are decorated with `@contrast_governed_tool`, which runs the full `THEORY → ENGINE → GOVERNANCE` pass before returning a verdict.

### Frontend Layout (`geox-gui/`)

```
geox-gui/src/
  components/
    LandingPage/        # Marketing landing page
    Layout/             # MainLayout, MainLayoutForge
    EarthWitness/       # 2D map (MapLibre) + 3D terrain (Cesium)
    LogDock/            # Well log viewer (Canvas/D3)
    SectionCanvas/      # Seismic section viewer
    ProspectUI/         # Prospect evaluation panel
    WellContextDesk/    # Well-context dashboard
    MalayBasinPilot/    # Live pilot dashboard
    VerdictConsole/     # Governance verdict display
    WitnessBadges/      # Constitutional floor badges
    ChronosHistory/     # Temporal audit trail
  store/                # Zustand slices
  types/                # Shared TypeScript types
```

**Governance constraint:** The `WitnessBadges` component must remain visible at all times in the cockpit layout. This is a constitutional requirement, not a stylistic choice.

---

## 4. Key Entry Points

| File | Role |
|------|------|
| `control_plane/fastmcp/server.py` | **Canonical FastMCP server** — primary MCP entrypoint for Smithery / Claude Desktop |
| `execution_plane/vps/server.py` | **Canonical VPS execution plane** — production HTTP server |
| `geox_unified_mcp_server.py` | Backward-compatible shim → `control_plane/fastmcp/server` |
| `geox_unified.py` | Backward-compatible shim → `execution_plane/vps/server` |
| `geox_mcp_server.py` | Legacy public entrypoint (re-exports from unified server) |
| `entrypoint.sh` | Docker container startup script (invokes `geox_unified.py`) |

When adding new tools or routes, prefer modifying the canonical servers inside `control_plane/` and `execution_plane/` rather than the root-level shims.

---

## 5. Build, Test & Lint Commands

### Python

```bash
# Install in editable mode
pip install -e ".[dev]"

# Run all tests
pytest tests/ -q

# Run a single test
pytest tests/ -k "test_name" -q

# With coverage (target: 65%)
pytest tests/ --cov=arifos.geox

# Lint
ruff check geox_mcp_server.py arifos/geox/

# Format
ruff format arifos/geox/

# Type check
mypy geox_mcp_server.py arifos/geox/
```

**Test configuration notes:**
- `asyncio_mode = auto` — async tests do not need decorators.
- Many seismic and governance files are excluded from coverage (see `pyproject.toml` `[tool.coverage.run] omit`).

### Frontend (`geox-gui/`)

```bash
cd geox-gui

# Development server
npm run dev

# Type check
npm run typecheck

# Lint
npm run lint

# Production build
npm run build
```

---

## 6. Development Conventions

### Python
- Start files with `from __future__ import annotations`.
- Use **Pydantic 2.x** `BaseModel` for all request/response schemas.
- Prefer `Enum`, `dataclass`, and explicit type hints.
- Decorate domain MCP tools with `@contrast_governed_tool` so they run through `THEORY → ENGINE → GOVERNANCE`.
- Verdict constants are defined in `arifos/geox/__init__.py`:
  - `GEOX_SEAL`, `GEOX_PARTIAL`, `GEOX_SABAR`, `GEOX_REVIEW`, `GEOX_HOLD`, `GEOX_BLOCK`, `GEOX_VOID`

### TypeScript / React
- Strict TypeScript is enabled (`strict: true`).
- Path alias `@/` maps to `src/`.
- Shared Python/TS contracts live in `geox/shared/contracts/` and are included in the TypeScript project.
- Cesium is excluded from Vite dependency optimization (`optimizeDeps.exclude: ['cesium']`).

### Code Style
- File headers and docstrings often use Unicode box-drawing characters (`═`, `╔`, `╗`, etc.) for visual separation.
- The phrase **DITEMPA BUKAN DIBERI** appears in headers as a project seal.

---

## 7. Testing Strategy

- **Unit tests:** `tests/unit/`
- **Physics solvers:** `tests/physics/` (porosity, saturation models)
- **Integration / E2E:** `test_e2e_mcp.py`, `test_end_to_end_mock.py`
- **Shared fixtures:** `tests/conftest.py`
  - `geo_request` — Standard `GeoRequest` for "Blok Selatan" in the Malay Basin.
  - `mock_agent` — `GeoXAgent` wired with `MockEarthNetTool` and `MockSeismicVLMTool`, in-memory memory store, no external APIs.

When writing new tests, use the existing fixtures to avoid real network calls. The `mock_agent` is the preferred way to test agent behavior without LLM dependencies.

---

## 8. Deployment Process

### VPS Deployment
```bash
# Deploy backend + frontend to production VPS
./deploy-vps.sh

# Force rebuild GUI assets
./deploy-vps.sh --force-rebuild
```

The script:
1. Builds Docker images locally (`geox-server`, `geox-gui`).
2. Transfers images to the VPS via `docker save | ssh ... docker load`.
3. Pulls latest code on the VPS and runs `docker compose up -d`.

### Docker Compose
- `docker-compose.yml` defines two services:
  - `geox` — Python MCP/HTTP server (port 8000, Traefik-routed).
  - `gui` — Nginx serving static frontend files.
- Traefik handles TLS, path prefixes (`/mcp`, `/health`, `/tools`), and load balancing.

### CI Pipeline (`.github/workflows/ci.yml`)
On every push and pull request:
1. **Security:** TruffleHog secret scan.
2. **Python:** Install editable package, run `pip-audit`, `ruff check`, `mypy`, `pytest`.
3. **Smoke test:** Start `geox_mcp_server.py` in HTTP mode and verify `/health` returns `200 OK` and `/mcp` is reachable.

---

## 9. Security & Governance Considerations

This is a **governance-first** project. Any code change that affects tool outputs, verdict logic, or data mutations must respect the constitutional floors:

| Floor | Rule | Effect on Code |
|-------|------|----------------|
| **F1 Amanah** | No irreversible action without a seal | Writes are blocked until verdict ≥ `PARTIAL` |
| **F2 Truth** | τ ≥ 0.99 — no ungrounded claims | Coordinates + CRS required on all geo inputs |
| **F4 Clarity** | Zero entropy — concise outputs | Keep decision text concise; units mandatory |
| **F7 Humility** | Confidence hard cap at Ω ≤ 0.90 | Uncertainty bands required on every estimate |
| **F9 Physics9** | Deterministic physical law adherence | Reject geometries / properties that violate physics |
| **F11 Authority** | Provenance mandatory | Every data source must declare its origin |
| **F13 Sovereign** | Human emergency override | Prospect gates and destructive ops require human confirmation |

A violation of any floor triggers an **`888_HOLD`** — a hard stop requiring explicit human ratification before execution continues.

**Important:** Do not rotate keys, modify production config, or bypass governance checks without explicit human approval.

---

## 10. Quick Reference

| Task | Command / Location |
|------|-------------------|
| Run canonical MCP server (stdio) | `python control_plane/fastmcp/server.py` |
| Run canonical MCP server (HTTP) | `python execution_plane/vps/server.py --host 0.0.0.0 --port 8000` |
| Run legacy entrypoint | `python geox_mcp_server.py` |
| Run frontend dev | `cd geox-gui && npm run dev` |
| Run tests | `pytest tests/ -q` |
| Run tests with coverage | `pytest tests/ --cov=arifos.geox` |
| Lint Python | `ruff check geox_mcp_server.py arifos/geox/` |
| Format Python | `ruff format arifos/geox/` |
| Type-check Python | `mypy geox_mcp_server.py arifos/geox/` |
| Lint frontend | `cd geox-gui && npm run lint` |
| Type-check frontend | `cd geox-gui && npm run typecheck` |
| Deploy to VPS | `./deploy-vps.sh` |
| Docker compose up | `docker compose up -d` |

---

*Last updated: 2026-04-14*
*Seal: DITEMPA BUKAN DIBERI*
