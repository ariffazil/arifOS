# Repository Guidelines

## Project Structure & Module Organization
`arifosmcp/` is the main runtime package and contains server entrypoints, tool implementations, schemas, and runtime adapters. `core/` holds constitutional enforcement and vault logic. `tests/` contains the automated suite, with integration and floor-sensitive coverage. Support code lives in `scripts/`, deployment assets in `deploy/` and `infrastructure/`, frontend/docs packages in `static/` and `packages/`, and immutable audit material in `VAULT999/`.

## Build, Test, and Development Commands
- `uv sync --all-extras` installs the canonical Python environment.
- `uv run python -m arifosmcp.server` starts the local MCP/FastAPI server.
- `pytest tests/ -q --tb=short` runs the standard test suite.
- `pytest tests/ --cov=arifosmcp --cov=core --cov-report=html` generates coverage output.
- `uv run ruff check .` runs linting.
- `uv run mypy arifosmcp core` runs type checks.
- `make health` checks the local `/health` endpoint; `make sot-check` audits source-of-truth alignment.

## Coding Style & Naming Conventions
Target Python 3.12+ and keep line length to 100 characters, matching Ruff config in `pyproject.toml`. Use 4-space indentation, type hints on public functions, and Pydantic models for structured I/O. Prefer `snake_case` for modules, functions, and files, `PascalCase` for classes, and `UPPER_SNAKE_CASE` for constants. Follow existing tool naming like `arif_<domain>_<verb>`.

## Testing Guidelines
Place tests under `tests/` using `test_*.py` filenames; `pytest` is configured with `asyncio_mode = auto`, so async tests do not need manual loop plumbing. Add or update tests with every behavioral change, especially for routing, floor enforcement, or transport code. Cover both success and fail-secure paths for governance-sensitive logic.

## Commit & Pull Request Guidelines
Recent history uses concise conventional-style subjects such as `feat:`, `config:`, and `vault_seal:`. Keep commits scoped and imperative, for example `feat(runtime): add health parity check`. PRs should summarize the problem, the approach, test evidence, and any operational risk. Link issues when relevant and include screenshots only for changes under `static/` or other UI surfaces.

## Security & Configuration Tips
Do not commit secrets; use `.env.example` as the template and treat `secrets/` as local-only. Avoid manual edits inside `VAULT999/` and generated lockfiles unless the change is intentional and validated. High-stakes changes touching auth, ledger, or deployment paths should include explicit rollback notes.
