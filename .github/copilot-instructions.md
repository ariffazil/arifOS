# arifOS Copilot Instructions

Use the current runtime and lock files as source of truth. Older prose docs in this repo can drift.

## Build, test, and lint

- Install dependencies: `uv sync --all-extras`
- Start the canonical local server: `uv run python -m arifosmcp.runtime.server`
- The repository-root `server.py` is only a compatibility shim; the packaged authority is `arifosmcp.server`, and `arifosmcp/runtime/server.py` is the runtime re-export used by `python -m`.
- Full test suite: `uv run pytest tests/ -q --tb=short`
- Single test file: `uv run pytest tests/test_public_tool_registry.py -q`
- Single test: `uv run pytest tests/test_public_tool_registry.py::test_public_registry_exposes_only_capability_tools -q`
- Fast CI subset from `.github/workflows/01-unified-ci.yml`:
  `uv run python3 -m pytest tests/test_phase0_standalone.py tests/test_mcp_inspector.py tests/test_surface_lock.py tests/test_unified_memory.py tests/test_registry.py tests/test_psi_shadow.py -q --tb=no --no-header`
- Smaller bootstrap subset from `.github/workflows/copilot-setup-steps.yml`:
  `uv run python3 -m pytest tests/test_phase0_standalone.py tests/test_surface_lock.py tests/test_registry.py -q --tb=short --no-header -x`
- Lint and type-check commands that exist in repo/workflows:
  - `uv run ruff check core/ arifosmcp/ tests/ --line-length 100`
  - `uv run ruff format --check core/ arifosmcp/ tests/`
  - `uv run ruff check --select I core/ arifosmcp/ tests/`
  - `uv run mypy core/governance_kernel.py core/judgment.py --strict`
  - `uv run mypy arifosmcp/runtime/ --ignore-missing-imports`
- Repo health commands used by operators:
  - `make health`
  - `make sot-check`

## High-level architecture

- `arifosmcp/` is the live MCP runtime package. `arifosmcp.server` owns the packaged FastMCP server and REST routes, while `arifosmcp/runtime/server.py` exists to put the repo root first on `sys.path` and then re-export that server.
- `core/` holds the deepest governance primitives and ledger logic. Runtime code in `arifosmcp/` builds on `core/` rather than replacing it.
- The public MCP wire surface is frozen to exactly 7 verbs: `arif_init`, `arif_observe`, `arif_think`, `arif_route`, `arif_judge`, `arif_act`, and `arif_seal`. The important source-of-truth chain is:
  1. `arifosmcp/runtime/public_surface.py` (`CANONICAL_7`)
  2. `arifosmcp/tool_registry.json` (generated machine-readable manifest for the public facade + internal aliases)
  3. `static/.well-known/mcp/server.json` (canonical served server card)
  4. `tests/test_public_tool_registry.py` and related surface-lock tests
- `arifosmcp/constitutional_map.py` remains the broader internal tool/spec source, but it is not the served public server card.
- The runtime still contains many internal and diagnostic tools, but they are not part of the default `tools/list` public surface. Distinguish the 7 public verbs from the larger internal registry.
- arifOS is the governance facade; A-FORGE is the execution organ. arifOS owns judgment, gating, and sealing, while engineering and substrate-heavy execution surfaces live downstream and should not be treated as part of the default public wire surface.
- Governed workflows are session-based. `arif_init` establishes the session context, and later steps commonly depend on session-bound IDs and prior verdict/seal state.

## Key conventions

- Read `AGENTS.md` at the repository root first for repo operating constraints. Copies under `docs/` or generated assistant docs can drift.
- Prefer runtime truth over older prose when they disagree. In practice, trust this order:
  1. `arifosmcp/runtime/public_surface.py`
  2. `arifosmcp/tool_registry.json`
  3. `static/.well-known/mcp/server.json`
  4. lock tests such as `tests/test_public_tool_registry.py` and `tests/test_surface_lock.py`
- The canonical public namespace is `arif_*`. `arifos_*` names still exist for diagnostics and internal helpers, but they must not leak onto the default public MCP surface.
- Tests are opinionated about environment and protocol. `tests/conftest.py` sets `ARIFOS_ALLOW_LEGACY_SPEC=1`, `ARIFOS_PHYSICS_DISABLED=1`, and `AAA_MCP_OUTPUT_MODE=debug`, and it hard-fails by default if the live kernel at `http://127.0.0.1:8088/mcp` does not match `EXPECTED_PROTOCOL_VERSION`.
- `asyncio_mode = auto` in `pyproject.toml`, so most async tests do not need explicit `@pytest.mark.asyncio`.
- There are two different `core` trees (`core/` and `arifosmcp/core/`). Test setup forces the repository-root `core/` package to the front of `sys.path`; be careful not to assume imports from one are the other.
- Keep path-priority behavior intact when touching startup code. Both `arifosmcp/runtime/server.py` and test bootstrap logic deliberately insert the repo root early on `sys.path` so the live checkout wins over packaged copies.
- Heavy or optional integrations are commonly imported lazily. Follow the existing `try/except ImportError` pattern instead of making heavyweight imports unconditional.
- If you change the public surface or canonical registry, update the generated/locked surfaces together: `arifosmcp/runtime/public_surface.py`, `arifosmcp/constitutional_map.py`, `arifosmcp/tool_registry.json`, and the surface-lock tests.
- Adding a new top-level directory is governed by `adr/ADR_001_BOUNDARIES.md`; update the ADR if you introduce a new repo-root boundary.

## MCP servers

- **Playwright browser automation is relevant here.** The repo depends on `playwright`, includes a local browser bridge in `arifosmcp/integrations/playwright_bridge.py`, and documents a `headless_browser` role for browser-based reality fetching.
- For GitHub Copilot CLI, add/manage MCP servers with the `/mcp` command. The relevant local Playwright target is `http://127.0.0.1:8931/mcp`.
- Prefer reusing `arifosmcp.integrations.playwright_bridge` for browser automation from Python code instead of hand-rolling a raw MCP client.
- The local Playwright MCP default is `PLAYWRIGHT_MCP_URL=http://127.0.0.1:8931`, but the bridge deliberately sends `Host: localhost:8931`; preserve that behavior or the browser MCP can reject requests with same-origin/403 errors.
- Use Playwright MCP for browser-only flows such as Observatory/WebMCP checks and UI/runtime verification; the browser-facing read-only surface is declared in `static/.well-known/webmcp.json`.
