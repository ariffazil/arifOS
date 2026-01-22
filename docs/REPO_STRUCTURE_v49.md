# arifOS v49 Repository Structure (Single-Body)

## Canonical (shipped)
- `000_THEORY/` — Canon law + manifest for v49.
- `AAA_MCP/` — Blueprint + configs for the MCP transport gateway.
- `arifos/` — Single runtime body (AGI·ASI·APEX, MCP, enforcement, ledger).
- `config/`, `setup/`, `scripts/`, `servers/` — Deployment + tooling.
- `docs/` — Design notes, blueprints, and operational guides.
- `tests/` — All tests (move stray root tests here).
- `vault_999/` — Canonical ledger artifacts (sealed).
- Agent workspaces: `.agent/`, `.antigravity/`, `.claude/`, `.codex/`, `.kimi/`, `.gemini/` (keep as-is; document, don't package).

## Archived / sandbox (not shipped)
- `archive/` — Versioned historical artifacts (keep tracked).
- `archive_local/` — Gitignored parking lot for legacy trees and exhaust (keep `README.md` tracked).
  - Move here: `arifos_core/`, `arifos_clip/`, `arifos_eval/`, `arifos_ledger/`, `arifos_orchestrator/`, `runtime/`, `cooling_ledger/`, `ledger/`, `logs/`, `sessions/`, `WISDOM/`, `v49 staging*/`, `UNTRACKED_MANIFEST_*.json`, coverage artifacts.

## Compatibility + shims
- Packaging targets `arifos` only (pyproject narrowed); legacy imports may need thin shims/aliases while downstreams migrate off `arifos_core`.
- Docker/compose/Procfile should mount `000_THEORY/` + `arifos/` and use canonical entrypoints.

## Hygiene defaults
- Ignore caches (`.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`, `.vs/`, `htmlcov/`, `coverage.xml`) and leave them in `archive_local/` if needed.
- Treat `archive_local/` as sandbox-only; never commit its contents (except the README).

## Quick Verification
- `pip install -e .` (packages only `arifos` modules)
- `pytest -q` or targeted `pytest tests/legacy/test_mcp_fixes.py` (legacy MCP smoke)
- `rg "arifos_core" --glob '!archive_local/**'` to find remaining legacy imports before archiving
- `docker build -t arifos-api .` to validate canonical Dockerfile once mounts are updated
