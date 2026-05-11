# arifOS Copilot Instructions

## Build, test, and lint

- Preferred setup is `uv sync --all-extras`. Pip fallback is `pip install -e ".[dev]"`.
- Run the canonical local server with `python -m arifosmcp.runtime.server`. The root `server.py` is only a compatibility shim.
- Docker build/run path:
  - `docker build -t arifos:latest .`
  - `docker run -p 8080:8080 arifos:latest`
  - The production command in the image is `uvicorn arifosmcp.runtime.server:app --host 0.0.0.0 --port 8080`.
- Full tests: `pytest tests/ -q --tb=short`
- Single file: `pytest tests/test_public_tool_registry.py -q`
- Single test: `pytest tests/test_public_tool_registry.py::test_public_registry_matches_runtime -q`
- CI subset used by `01-unified-ci.yml`: `uv run python3 -m pytest tests/test_phase0_standalone.py tests/test_mcp_inspector.py tests/test_surface_lock.py tests/test_unified_memory.py tests/test_registry.py tests/test_psi_shadow.py -q --tb=no --no-header`
- Lint/type-check commands that exist in repo/workflows:
  - `ruff check core/ arifosmcp/ tests/ --line-length 100`
  - `ruff format --check core/ arifosmcp/ tests/`
  - `ruff check --select I core/ arifosmcp/ tests/`
  - `mypy core/governance_kernel.py core/judgment.py --strict`
  - `mypy arifosmcp/runtime/ --ignore-missing-imports`

## High-level architecture

- `arifosmcp/` is the live runtime package. Treat `arifosmcp.server` as the canonical server entrypoint and `arifosmcp/runtime/server.py` as the packaged re-export used by Docker and local `python -m` startup.
- `core/` contains the deepest governance primitives: floor enforcement, judgment, shared types, physics, and the `vault999` ledger. Runtime code in `arifosmcp/` builds on these primitives.
- `arifos/` is a secondary/legacy SDK-style package that still exists for compatibility. Do not change it expecting the public MCP runtime to change unless the call path clearly reaches it.
- The public MCP surface is locked to 13 canonical `arif_*` tools. The important chain is:
  1. `arifosmcp/constitutional_map.py` defines the canonical tool set.
  2. `arifosmcp/tool_registry.json` is the generated machine-readable registry.
  3. `arifosmcp/runtime/tools.py` contains the canonical handler registrations.
  4. `PUBLIC_SURFACE_CANON.md` and `CANONICAL_PATHS.md` document the intended public surface and source-of-truth map.
- Golden path for governed workflows is `arif_session_init -> arif_sense_observe / arif_evidence_fetch -> arif_mind_reason -> arif_heart_critique -> arif_judge_deliberate -> arif_vault_seal`. `arif_forge_execute` is the execution surface and should be treated as downstream of judgment.

## Key conventions

- Public names are `arif_*`, not `arifos_*`. Legacy names still exist in the tree, but new integrations and edits should follow the canonical 13-tool surface.
- This repo contains stale and archived guidance. Prefer these files when they disagree with older docs:
  1. `CANONICAL_PATHS.md`
  2. `PUBLIC_SURFACE_CANON.md`
  3. `arifosmcp/tool_registry.json`
  4. `arifosmcp/runtime/tools.py`
- `arifosmcp.server` deliberately rewrites `sys.path` early so the project root and live checkout win over packaged copies. Preserve that path-priority behavior when touching startup code or Docker import behavior.
- Multi-step governed flows are session-bound. `arif_session_init` establishes the session, and later tools commonly require `session_id` and `actor_id`.
- Tests depend on `tests/conftest.py` defaults: `ARIFOS_ALLOW_LEGACY_SPEC=1`, `ARIFOS_PHYSICS_DISABLED=1`, and `AAA_MCP_OUTPUT_MODE=debug`. Async pytest mode is `auto`, so most async tests do not need explicit `@pytest.mark.asyncio`.
- Optional or heavy integrations are usually imported lazily. Follow the existing `try/except ImportError` pattern instead of making heavyweight imports unconditional.
- Changes to canonical boundaries are expected to stay synchronized. If you change the public tool surface or canonical paths, also update the registry/docs/tests that lock them (`PUBLIC_SURFACE_CANON.md`, `CANONICAL_PATHS.md`, and `tests/test_public_tool_registry.py` / `tests/test_surface_lock.py`).
- Adding a new top-level directory is a governed change: `ADR_001_BOUNDARIES.md` requires an ADR entry and a `CANONICAL_PATHS.md` update.
