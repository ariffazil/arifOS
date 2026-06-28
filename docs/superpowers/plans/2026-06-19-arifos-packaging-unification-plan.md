# Implementation Plan — arifOS Packaging Unification

**Spec:** `docs/superpowers/specs/2026-06-19-arifos-packaging-unification-design.md`
**Date:** 2026-06-19
**Phases:** 4 (Phase 3 gated on kernel restart, Phase 4 gated on F13 per-action)

---

## Phase 1 — Dependency Floor Alignment

> Safe to execute now. No code changes. pyproject.toml + package.json edits only.
> Recommended: restart arifOS kernel first (WELL signal AMBER due to kernel 502).

### 1.1 — Delete stale well/src/pyproject.toml

- [ ] Delete `C:\ariffazil\well\src\pyproject.toml`
  - Verify `well\src\` still contains source code (only the pyproject.toml goes)
  - `afwell v0.1.0` with `fastmcp>=2.12.3` is incompatible with 3.x API

### 1.2 — Update well/pyproject.toml

File: `C:\ariffazil\well\pyproject.toml`

- [ ] `fastmcp[tasks]>=3.3.1,<4.0` → `fastmcp[tasks]==3.4.2`
- [ ] Audit: does this file contain `sentence-transformers` or `scikit-learn`?
  - If yes: add a comment `# TODO Phase 2: move to arifos[ml] extra` — do NOT move yet

### 1.3 — Update wealth/pyproject.toml

File: `C:\ariffazil\wealth\pyproject.toml`

- [ ] `fastmcp[tasks]>=3.3.1,<4` → `fastmcp[tasks]==3.4.2`
- [ ] `pydantic>=2.0.0` → `pydantic>=2.13.4`
- [ ] `numpy>=1.26.0` → `numpy>=2.4.6`
- [ ] `scipy>=1.10.0` → `scipy>=1.17.1`
- [ ] `asyncpg>=0.29.0` → `asyncpg>=0.31.0`
- [ ] `uvicorn[standard]>=0.30.0` → `uvicorn[standard]>=0.49.0`
- [ ] `fastapi>=0.115.0` → `fastapi>=0.136.1`
- [ ] `starlette>=0.40.0` — already correct, leave as-is
- [ ] `httpx>=0.25.0` → `httpx>=0.28.1`
- [ ] `anyio>=4.0.0` → `anyio>=4.13.0`
- [ ] Pin all currently unpinned deps (add `>=` floors from canonical matrix):
  - `pydantic-ai>=0.0.1` (check latest stable on PyPI first)
  - `langgraph>=0.2.0`
  - `duckdb>=0.10.0`
  - `polars>=1.0.0`
  - `pyarrow>=17.0.0`
  - `networkx>=3.3`
  - `pyportfolioopt>=1.5.5`
  - `pandera>=0.19.0`
  - `opentelemetry-api>=1.42.1`
  - `opentelemetry-sdk>=1.42.1`
  - (all others in wealth deps currently listed without versions)

### 1.4 — Update geox/pyproject.toml

File: `C:\ariffazil\geox\pyproject.toml`

- [ ] `fastmcp[tasks]>=3.4.2,<4.0` → `fastmcp[tasks]==3.4.2`
- [ ] All other deps already at or above canonical floors — verify, no change expected

### 1.5 — JS: Update AAA a2a-server

File: `C:\ariffazil\AAA\a2a-server\package.json`

- [ ] `"express": "^4.21.0"` → `"express": "^5.2.1"`
- [ ] After change: review server.js for express 5 breaking changes:
  - Error handler signatures `(err, req, res, next)` — verify still works
  - `req.query` parsing — verify no qs-dependent logic

### 1.6 — JS: Update AAA a2a-gateway

File: `C:\ariffazil\AAA\services\a2a-gateway\package.json`

- [ ] `"express": "^4.18.0"` → `"express": "^5.2.1"`
- [ ] Same express 5 review as 1.5

### 1.7 — JS: Update @arifos/mcp package

File: `C:\ariffazil\arifOS\arifosmcp\packages\npm\arifos-mcp\package.json`

- [ ] `"@modelcontextprotocol/sdk": "^1.0.0"` → `"^1.9.0"`
- [ ] `"typescript": "^5.3.0"` (devDependencies) → `"^6.0.3"`

### 1.8 — JS: Update A-FORGE package

File: `C:\ariffazil\A-FORGE\package.json`

- [ ] `"@supabase/supabase-js": "^2.107.0"` → `"^2.108.0"`

### 1.9 — Verify Phase 1

- [ ] `cd C:\ariffazil\wealth && pip install -e . --dry-run` — confirm no resolution errors
- [ ] `cd C:\ariffazil\well && pip install -e . --dry-run`
- [ ] `cd C:\ariffazil\geox && pip install -e . --dry-run`
- [ ] `cd C:\ariffazil\AAA\a2a-server && npm install` — confirm express 5 resolves
- [ ] `cd C:\ariffazil\AAA\services\a2a-gateway && npm install`
- [ ] Commit: `chore: align federation dependency floors — canonical matrix 2026-06-19`

---

## Phase 2 — Package Consolidation

> pyproject.toml structural changes only. No Python module code changes.
> Execute after Phase 1 is committed and green.

### 2.1 — Delete root pyproject.toml

- [ ] Delete `C:\ariffazil\arifOS\pyproject.toml` (the root wrapper — redundant)
  - Back it up first: `copy pyproject.toml pyproject.toml.bak`

### 2.2 — Promote arifosmcp/pyproject.toml to root

- [ ] Copy `C:\ariffazil\arifOS\arifosmcp\pyproject.toml` → `C:\ariffazil\arifOS\pyproject.toml`
- [ ] This becomes the single canonical pyproject.toml

### 2.3 — Apply new extras gating

Edit `C:\ariffazil\arifOS\pyproject.toml`:

**Remove from `[project.dependencies]` (move to extras):**
- [ ] `sentence-transformers` → `[ml]`
- [ ] `scikit-learn` → `[ml]`
- [ ] `qdrant-client` → `[vectors]`
- [ ] `chromadb` → `[vectors]`
- [ ] `lancedb` → `[vectors]`
- [ ] `playwright` → `[browser]`
- [ ] `beautifulsoup4` → `[browser]`
- [ ] `torch` → `[heavy]`
- [ ] `transformers` → `[heavy]`
- [ ] `opentelemetry-api` → `[observe]`
- [ ] `opentelemetry-sdk` → `[observe]`
- [ ] `pymupdf` → `[io]`
- [ ] `pdfplumber` → `[io]`
- [ ] `python-docx` → `[io]`
- [ ] `openpyxl` → `[io]`
- [ ] `pillow` → `[io]`
- [ ] `blake3` → `[io]`
- [ ] `pynacl` → `[io]`
- [ ] `tavily-python` → `[search]`
- [ ] `exa-py` → `[search]`
- [ ] `firecrawl-py` → `[search]`
- [ ] `trafilatura` → `[search]`
- [ ] `readability-lxml` → `[search]`
- [ ] `markdownify` → `[search]`
- [ ] `html2text` → `[search]`
- [ ] `bleach` → `[search]`
- [ ] `defusedxml` → `[search]`
- [ ] `tldextract` → `[search]`
- [ ] `google-api-python-client` → `[google]`
- [ ] `google-auth-httplib2` → `[google]`
- [ ] `google-auth-oauthlib` → `[google]`
- [ ] `google-genai` → `[google]`
- [ ] `sqlalchemy` → `[db]`
- [ ] `alembic` → `[db]`
- [ ] `psycopg2-binary` → `[db]`
- [ ] `lasio`, `welly`, `striplog`, `segyio`, `statsmodels`, `scipy`, `matplotlib`, `pyproj` → `[geox]`
- [ ] `supabase`, `numpy-financial`, `psycopg[binary]`, `yfinance`, wealth stack → `[wealth]`

**Add new `[project.optional-dependencies]` groups:**
- [ ] Add `[io]` group
- [ ] Add `[search]` group
- [ ] Add `[google]` group
- [ ] Add `[db]` group
- [ ] Add `[geox]` group (include `setuptools<70`)
- [ ] Add `[wealth]` group (all wealth-domain deps)
- [ ] Add `[well]` group (empty — kernel only)
- [ ] Add `[aaa]` group (`nats-py>=2.29.3`)
- [ ] Update `[full]` to include all domain extras

**Update `[project.scripts]`:**
- [ ] Add `aaa-mcp = "arifos.runtime.__main__:main"` (legacy alias)
- [ ] Keep `arifos-mcp = "arifos.runtime.__main__:main"` (transition alias)

**Update `[tool.setuptools.packages.find]`:**
- [ ] Change `include = ["arifosmcp*", ...]` → `include = ["arifos*", ...]`
  - This prepares for Phase 3 rename (no effect until the folder is renamed)

### 2.4 — Delete arifosmcp/pyproject.toml

- [ ] Delete `C:\ariffazil\arifOS\arifosmcp\pyproject.toml`
  - Root pyproject.toml is now the only one

### 2.5 — Verify Phase 2

- [ ] `pip install -e ".[dev]" --dry-run` from arifOS root — confirm light install resolves
- [ ] `pip install -e ".[full]" --dry-run` — confirm full install resolves without conflicts
- [ ] `pip install -e ".[geox]" --dry-run` — confirm setuptools<70 constraint not broken
- [ ] Commit: `chore: consolidate to single pyproject.toml with full domain extras gating`

---

## Phase 3 — Module Rename

> Code change. **GATE: do not start until arifOS kernel is confirmed UP.**
>
> Pre-execution checklist:
> 1. Restart arifOS at arifos.arif-fazil.com
> 2. Run `well_attest_to_kernel` — WELL must return GREEN
> 3. Only then proceed with steps below

### 3.1 — Rename the Python package directory

- [ ] `git mv arifosmcp arifos` from `C:\ariffazil\arifOS\`

### 3.2 — Bulk replace all arifosmcp references

- [ ] Run replacement across `*.py`:
  `grep -rl "arifosmcp" --include="*.py" . | xargs sed -i 's/arifosmcp/arifos/g'`
- [ ] Run replacement across `*.toml`:
  `grep -rl "arifosmcp" --include="*.toml" . | xargs sed -i 's/arifosmcp/arifos/g'`
- [ ] Run replacement across `*.json`:
  `grep -rl "arifosmcp" --include="*.json" . | xargs sed -i 's/arifosmcp/arifos/g'`
- [ ] Run replacement across `*.md`:
  `grep -rl "arifosmcp" --include="*.md" . | xargs sed -i 's/arifosmcp/arifos/g'`
- [ ] Run replacement across `*.yaml` / `*.yml`:
  `grep -rl "arifosmcp" --include="*.yaml" --include="*.yml" . | xargs sed -i 's/arifosmcp/arifos/g'`

### 3.3 — Update MCP server configs

- [ ] `C:\Users\User\.claude\mcp.json` — update `python -m arifosmcp.runtime stdio` → `python -m arifos.runtime stdio`
- [ ] `C:\Users\User\AppData\Roaming\Antigravity\User\mcp.json` — same
- [ ] `C:\Users\User\.gemini\antigravity\mcp_config.json` — same
- [ ] `C:\Users\User\.gemini\settings.json` — check for arifosmcp references

### 3.4 — Update CLAUDE.md

- [ ] `C:\Users\User\.claude\CLAUDE.md` — update `python -m arifosmcp.runtime stdio` reference
- [ ] Project CLAUDE.md if present in arifOS/

### 3.5 — Post-rename verification (must all pass)

- [ ] `grep -r "arifosmcp" --include="*.py" --include="*.toml" --include="*.json" --include="*.md" --include="*.yaml" .`
  → **must return zero results**
- [ ] `python -m arifos.runtime stdio` — must respond without error
- [ ] `pytest -m "not integration"` from arifOS root — must be green
- [ ] `arifos --help` (if installed) — must respond

### 3.6 — Commit

- [ ] Commit: `feat!: rename module arifosmcp → arifos — MCP is transport, not identity`

---

## Phase 4 — PyPI Cleanup

> 888_HOLD — F13 confirmation required before each numbered action.
> Each action is independent and irreversible.

### 4.1 — Publish new arifos version (do this FIRST)

- [ ] **[F13 CONFIRM]** Build: `python -m build` from arifOS root
- [ ] Test install from dist: `pip install dist/arifos-2026.06.19-py3-none-any.whl`
- [ ] Confirm `arifos --help` works from fresh install
- [ ] `twine upload dist/arifos-2026.06.19*` — publish to PyPI

### 4.2 — Yank the epoch release

- [ ] **[F13 CONFIRM]** Yank `arifos==1!2026.6.11`:
  `twine yank arifos 1!2026.6.11`
- [ ] Verify: `pip install arifos` now resolves to `2026.06.19`

### 4.3 — Publish arifosmcp redirect stub

- [ ] **[F13 CONFIRM]** Prepare redirect stub in `arifosmcp/`
  - Minimal `pyproject.toml` with `install_requires = ["arifos>=2026.06.19"]`
  - `description = "Deprecated: merged into arifos. pip install arifos"`
- [ ] Publish: `twine upload dist/arifosmcp-2026.06.19*`

### 4.4 — Update federation registry

- [ ] **[F13 CONFIRM]** Update `smithery.yaml` — package name `arifosmcp` → `arifos`
- [ ] Update any other registry entries (Claude.ai MCP directory, etc.)

---

## Rollback Notes

- **Phase 1:** All changes are pyproject.toml edits — revert with git
- **Phase 2:** `pyproject.toml.bak` preserved; restore and delete new root pyproject.toml
- **Phase 3:** `git revert` on the rename commit; MCP configs must be manually restored
- **Phase 4:** Cannot un-yank from PyPI; plan accordingly
