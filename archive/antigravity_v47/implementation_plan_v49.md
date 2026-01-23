# arifOS v49 Single-Body Consolidation Plan

## Problem Statement
The repo still ships multiple overlapping runtimes (`arifos/` vs `arifos_core/`/`arifos_clip/`/`arifos_eval/`/`arifos_orchestrator/`), legacy canon/data trees, and stray build artifacts. Packaging (`pyproject.toml`) currently publishes all trees, Docker/Procfile still copy legacy paths, and tests/coverage are split across root and `tests/`. v49 canon (000_THEORY + AAA_MCP + arifos) needs a single body with archived legacy kept out of the build surface.

## Proposed Changes

### Component 1: Repository layout + archive strategy
#### [NEW] archive_local/ (gitignored) + archive_local/README.md
- Create a gitignored landing zone for legacy trees, session exhaust, and one-off outputs; document contents and retention rules (keep `archive/` for versioned history).
#### [MODIFY] .gitignore
- Add `archive_local/**`, `.venv/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.vs/`, `htmlcov/`, `coverage.xml`, `v49 staging*/`, stray completion/final docs, and other sandbox outputs so they never reappear in the index.
#### [MOVE] Legacy/duplicate trees into archive_local/
- Park `arifos_core/`, `arifos_clip/`, `arifos_eval/`, `arifos_ledger/`, `arifos_orchestrator/`, `runtime/`, `cooling_ledger/`, `ledger/`, `logs/`, `sessions/`, `WISDOM/`, `v49 staging (delete after forge)/`, `UNTRACKED_MANIFEST_2026-01-17.json`, and stray completion/final docs. Drop a short pointer README in each moved root (or in `archive_local/README.md`) explaining canonical replacements.

### Component 2: Canonical package + build boundaries
#### [MODIFY] pyproject.toml
- Narrow package discovery to `arifos*` (and scripts), drop legacy packages from `include`, adjust `tool.setuptools.package-data` and extras accordingly, and remove `--cov=arifos_core` from pytest defaults. Ensure scripts/entrypoints point at `arifos` modules (not `arifos_core`).
#### [MODIFY] pytest.ini and mypy.ini
- Point `testpaths` at `tests/` only, remove `mypy_path` shims for legacy packages, and exclude `archive_local/**` so static analysis ignores parked code.
#### [MODIFY] Dockerfile / docker-compose.yml / Procfile
- Copy/mount only canonical trees (`arifos/`, `AAA_MCP/`, `000_THEORY/`, `config/`, `setup/`, `servers/`, `scripts/`), add missing mounts from `IMPLEMENTATION_GAPS.md` (e.g., `000_THEORY` canon path), and align CMD/entrypoints with the canonical servers.

### Component 3: Canonical code migration + compatibility
#### [MODIFY] arifos/ (ingest legacy runtime surface)
- Identify high-traffic modules still only in `arifos_core/` (e.g., `mcp/orthogonal_executor.py`, enforcement metrics, memory/ledger helpers) and either port them into `arifos/` or provide thin proxies in `arifos_core/__init__.py` that re-export `arifos` equivalents before archiving the tree.
#### ✅ [COMPLETE] Component 4: MCP Metabolizer (Encoder → Metabolizer → Decoder)
- **Status**: Implemented and tested (2026-01-18)
- **Location**: `arifos/orchestrator/metabolizer.py` (405 lines, canonical) + `arifos_core/orchestrator/metabolizer.py` (working mirror)
- **Integration**: Wired into `mcp_gateway.py`'s `_handle_tools_call()` for human-optimized output
- **Features**: Phase 9 support (Phoenix-72 cooling, zkPC receipts, EUREKA sieve memory bands)
- **Tests**: 9 tests, 91% coverage, all passing (`tests/test_metabolizer.py`)
- **Architecture**: Encoder (JSON normalization) → Metabolizer (user profile strategy) → Decoder (human-readable rendering)
- **Discovery**: Architect identified missing 4th MCP component (Server/Transport/Client/Metabolizer). This fills the gap between raw server JSON and human presentation.
- **Consolidation Gap**: Tests currently import from `arifos_core.orchestrator.metabolizer` due to `arifos/__init__.py` having deep spec file dependencies (enforcement.metrics → genius_metrics → manifest verification). The canonical `arifos/orchestrator/metabolizer.py` is identical but unusable until `arifos/__init__.py` refactored to make enforcement imports optional.
- **TODO**: Refactor `arifos/__init__.py` to wrap all enforcement/memory/system imports in try/except, allowing `arifos.orchestrator` subpackage to work independently during development.
#### [MODIFY] arifos/orchestrator/mcp_gateway.py (+ metabolizer/pipeline)
- Implement the blueprint in `docs/blueprints/aaa_mcp_gateway_blueprint.md`: solid JSON-RPC validation, multi-transport handlers (stdio/http/sse), dynamic routing by provider, and real server calls instead of mocks. Ensure it consumes the canonical validators (per `IMPLEMENTATION_GAPS.md` #1) and parallel AGI||ASI execution path.
#### [MODIFY] Scripts/configs referencing arifos_core
- Update `scripts/*.py`, `config/*.json`, and guide files to import `arifos` equivalents; add compatibility warnings where removal is planned.

### Component 4: Tests + QA surface
#### [MOVE] Root-level tests into tests/
- Move `test_constitutional_floors.py`, `test_mcp_fixes.py`, `test_cloud_deployment.py` under `tests/` (e.g., `tests/legacy/`), fix imports to `arifos`, and drop duplicate test exclusions.
#### [NEW] Smoke/integration tests
- Add minimal smoke covering the MCP gateway (JSON-RPC round-trip, provider routing), package import sanity (`import arifos`), and a packaging test ensuring `pip install -e .` does not expose archived modules.

### Component 5: Documentation + manifest alignment
#### [MODIFY] README.md, 000_THEORY/MANIFEST.md, AGENTS.md, DOCUMENTATION_INDEX.md
- Document the v49 single-body layout, the archive_local policy, and canonical entrypoints (AAA_MCP gateway, Trinity servers). Update MANIFEST progress tables to reflect the consolidation and Docker fixes.
#### [NEW] docs/REPO_STRUCTURE_v49.md (or similar)
- One-page map of canonical vs archived paths, agent workspace folders, and how to reach archived content if needed.

### Component 6: Housekeeping + onboarding
#### [MODIFY] setup/on_workspace_open.py and load-env.ps1
- Ensure they skip `archive_local/**`, hint users to run cleanup, and auto-create the archive directory on first run.
#### [NEW] scripts/archive_sweep.py (optional)
- Script to relocate known legacy paths into `archive_local/` and summarize what moved (dry-run + apply modes).

## Verification Plan
- `pip install -e .` (packages only `arifos*`, no legacy modules pulled in).
- `pytest -q` (after moving tests); targeted: `pytest tests/test_mcp_fixes.py tests/test_constitutional_floors.py` and new MCP gateway smoke.
- `rg "arifos_core" --glob '!archive_local/**'` to confirm no live imports depend on archived paths.
- `python -m arifos.orchestrator.mcp_gateway` smoke run (stdio loop) plus `python scripts/cleanup_sessions.py --status` to ensure session utilities survive package changes.
- `docker build -t arifos-api .` (ensures Dockerfile uses canonical tree and mounts `000_THEORY` correctly).
