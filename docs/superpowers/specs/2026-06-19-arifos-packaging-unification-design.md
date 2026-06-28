# arifOS Packaging Unification Design

**Date:** 2026-06-19
**Status:** APPROVED — ready for implementation
**Scope:** Dependency floor alignment across all federation organs + package consolidation + module rename
**Author:** Arif Fazil (F13 Sovereign) + Claude Code

---

## Problem Statement

The arifOS federation currently has two overlapping Python packages (`arifos` + `arifosmcp`) with split
identities, divergent dependency floors across organs, and heavy mandatory dependencies that punish
lightweight installs. This violates constitutional principles of clarity (ΔS), humility (Ω₀), and
ontological purity (F10).

**Root causes:**
- Two pyproject.toml files publishing the same kernel under different names
- Organs (WEALTH, WELL) drifted to old dependency floors (numpy 1.26, pydantic 2.0, fastmcp 3.3.1)
- Heavy deps (torch, transformers, playwright, chromadb) are mandatory instead of optional
- `arifosmcp` name on PyPI contradicts `arifos` identity — MCP is transport, not identity
- Epoch prefix `1!` on PyPI makes version ordering unreliable
- Domain organ deps (io, search, geoscience, wealth stack) have no home in extras

---

## Decisions Made

| Decision | Choice | Rationale |
|---|---|---|
| Rename scope | Full rename — PyPI name + Python module | `arifosmcp` is transport naming, not identity |
| Package count | One package (`arifos`) with extras gating | Dual-package creates split identity and install chaos |
| Heavy deps | Move to optional extras | 4–6 GB mandatory install tax violates ΔS |
| `well/src/pyproject.toml` | Delete — stale, fastmcp 2.x | Incompatible with fastmcp 3.x API surface |
| PyPI epoch | Yank `1!2026.6.11`, republish clean | Epoch was accidental; must clean before further publishes |
| Domain deps | Each organ domain gets its own extras group | GEOX, WEALTH, WELL, AAA all covered explicitly |

---

## Canonical Dependency Floor Matrix

Single source of truth. All organs pin against these floors from 2026-06-19 onward.

### Python Kernel Floors (mandatory in all installs)

| Package | Canonical Floor | Pin Strategy | Change |
|---|---|---|---|
| `fastmcp[tasks]` | `==3.4.2` | Exact pin | WEALTH/WELL `3.3.1→3.4.2` |
| `pydantic` | `>=2.13.4` | Floor | WEALTH `2.0→2.13.4` |
| `httpx` | `>=0.28.1` | Floor | arifos root + WEALTH `0.25→0.28.1` |
| `uvicorn[standard]` | `>=0.49.0` | Floor | WEALTH `0.30→0.49` |
| `fastapi` | `>=0.136.1` | Floor | WEALTH `0.115→0.136.1` |
| `starlette` | `>=0.40.0` | Floor | arifos root relaxed from `1.0` (overly aggressive) |
| `anyio` | `>=4.13.0` | Floor | arifosmcp/WEALTH `4.0→4.13` |
| `asyncpg` | `>=0.31.0` | Floor | WEALTH `0.29→0.31` |
| `python-dotenv` | `>=1.2.2` | Floor | Unchanged |
| `cryptography` | `>=49.0.0` | Floor — security critical | arifosmcp `44→49` |
| `numpy` | `>=2.4.6` | Floor (not `==`) | WEALTH `1.26→2.4.6`; exact pin removed |
| `redis` | `>=5.0.0` | Floor | Session persistence backend |
| `prometheus-client` | `>=0.25.0` | Floor | Unchanged |
| `pydantic-settings` | `>=2.7.0` | Floor | Unchanged |
| `structlog` | `>=24.4.0` | Floor | Unchanged |
| `rich` | `>=15.0.0` | Floor | Unchanged |
| `psutil` | `>=7.2.2` | Floor | Unchanged |

> **GEOX-specific constraint — do NOT propagate to other organs:**
> `"setuptools<70"` — welly requires pkg_resources; setuptools 70+ removed it.

### JS/npm Floors

| Package | Canonical | Change |
|---|---|---|
| `express` | `^5.2.1` | AAA a2a-server `^4.21→^5`, a2a-gateway `^4.18→^5` |
| `@modelcontextprotocol/sdk` | `^1.9.0` | `@arifos/mcp` `^1.0→^1.9` |
| `typescript` | `^6.0.3` | `@arifos/mcp` `^5.3→^6.0.3` |
| `@supabase/supabase-js` | `^2.108.0` | A-FORGE `^2.107→^2.108` |
| `zod` | intentionally split | A-FORGE `^3.24.4` / AAA React UI `^4.4.3` — separate deploy runtimes, no shared install conflict |

---

## New `arifos` Package Structure

### Directory Layout

```
arifOS/
  pyproject.toml              <- single canonical (promoted from arifosmcp/)
  arifos/                     <- renamed from arifosmcp/
    __init__.py
    runtime/
    kernel/
    floors/
    vault/
    tools/
    intelligence/
    schemas/
    adapters/
    ...
```

### pyproject.toml — Full Dependency Tier Map

```toml
[project]
name = "arifos"
# arifos is the constitutional AGI kernel substrate.
# arifosmcp is deprecated — install arifos instead.

[project.scripts]
arifos     = "arifos.runtime.__main__:main"
arifos-mcp = "arifos.runtime.__main__:main"   # transition alias
aaa-mcp    = "arifos.runtime.__main__:main"   # legacy alias, remove in next major
aclip-cai  = "arifos.intelligence.cli:main"

# ─── LIGHT TIER — kernel only (~200 MB) ───────────────────────────────────────
# Mandatory for any arifos install. Constitutional floors + MCP transport only.
[project.dependencies]
"fastmcp[tasks]"    = "==3.4.2"
pydantic            = ">=2.13.4"
pydantic-settings   = ">=2.7.0"
httpx               = ">=0.28.1"
"uvicorn[standard]" = ">=0.49.0"
fastapi             = ">=0.136.1"
starlette           = ">=0.40.0"
anyio               = ">=4.13.0"
asyncpg             = ">=0.31.0"
cryptography        = ">=49.0.0"
python-dotenv       = ">=1.2.2"
rich                = ">=15.0.0"
psutil              = ">=7.2.2"
numpy               = ">=2.4.6"
redis               = ">=5.0.0"
prometheus-client   = ">=0.25.0"
structlog           = ">=24.4.0"

# ─── OPTIONAL EXTRAS ──────────────────────────────────────────────────────────
[project.optional-dependencies]

# ML floors — SBERT embeddings for F5/F6/F9 constitutional enforcement
ml = [
    "sentence-transformers>=5.5.1",
    "scikit-learn>=1.9.0",
]

# Vector stores — semantic memory backend
vectors = [
    "qdrant-client>=1.18.0",
    "chromadb>=0.5.0",
    "lancedb>=0.5.0",
]

# Browser + web scrape
browser = [
    "playwright>=1.49.0",
    "beautifulsoup4>=4.12.0",
    "duckduckgo-search>=6.3.0",
]

# Heavy ML — torch/transformers; only for full federation training nodes
heavy = [
    "torch>=2.12.0",
    "transformers>=5.12.0",
]

# Observability — OpenTelemetry traces + metrics export
observe = [
    "opentelemetry-api>=1.42.1",
    "opentelemetry-sdk>=1.42.1",
    "opentelemetry-exporter-otlp>=1.25.0",
]

# IO — document parsing, image processing, cryptographic hashing
io = [
    "pymupdf>=1.25.0",
    "pdfplumber>=0.11.0",
    "python-docx>=1.1.2",
    "openpyxl>=3.1.5",
    "pillow>=11.0.0",
    "blake3>=1.0.0",
    "pynacl>=1.6.2",
]

# Search + web intelligence — content fetch, extraction, sanitisation
search = [
    "tavily-python>=0.5.0",
    "exa-py>=2.14.0",
    "firecrawl-py>=1.3.0",
    "trafilatura>=1.12.0",
    "readability-lxml>=0.8.1",
    "markdownify>=0.13.1",
    "html2text>=2024.2.26",
    "bleach>=6.4.0",
    "defusedxml>=0.7.1",
    "tldextract>=5.3.1",
]

# Google Workspace — Calendar, Drive, Gmail integrations
google = [
    "google-api-python-client>=2.160.0",
    "google-auth-httplib2>=0.2.0",
    "google-auth-oauthlib>=1.4.0",
    "google-genai>=0.1.0",
]

# DB — relational ORM + migrations (beyond asyncpg raw drivers)
db = [
    "sqlalchemy>=2.0.36",
    "alembic>=1.14.0",
    "psycopg2-binary>=2.9.12",
]

# GEOX domain — Earth intelligence / geoscience substrate
# NOTE: includes setuptools<70 (welly constraint — do NOT remove)
geox = [
    "lasio>=0.32",
    "welly>=0.5.2",
    "striplog>=0.9.2",
    "segyio>=1.9.14",
    "statsmodels>=0.14.6",
    "scikit-learn>=1.9.0",
    "scipy>=1.17.1",
    "matplotlib>=3.11.0",
    "pyproj>=3.7.2",
    "setuptools<70",
]

# WEALTH domain — capital intelligence / valuation substrate
wealth = [
    "supabase>=2.10.0",
    "numpy-financial>=1.0.0",
    "psycopg[binary]>=3.1.0",
    "yfinance>=0.2.0",
    "duckdb>=0.10.0",
    "polars>=1.0.0",
    "pyarrow>=17.0.0",
    "networkx>=3.3",
    "pyportfolioopt>=1.5.5",
    "pandera>=0.19.0",
    "quantlib>=1.42.1",
    "riskfolio-lib>=7.3.0",
    "pymc>=6.0.1",
    "arviz>=1.2.0",
    "mesa>=3.5.1",
    "pydantic-ai>=0.0.1",
    "langgraph>=0.2.0",
]

# WELL domain — human substrate / biological governance
# WELL uses only the kernel + its own FastMCP tools; no additional Python deps needed.
well = []

# AAA domain — A2A messaging backbone
aaa = [
    "nats-py>=2.29.3",
]

# LLM adapters (optional bridges)
openai    = ["openai>=1.60.0"]
anthropic = ["anthropic>=0.40.0"]

# Dev tools
dev = [
    "pytest>=9.0.3",
    "pytest-asyncio>=1.3.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.15.13",
    "mypy>=2.1.0",
    "hypothesis>=6.120.0",
]

# Full federation node — all capability surfaces
full = [
    "arifos[ml,vectors,browser,heavy,observe,io,search,google,db,geox,wealth,aaa,openai,anthropic]",
]
```

### Install Paths by Organ

| Organ | Install command | Rationale |
|---|---|---|
| WELL | `pip install arifos` | kernel only — WELL tools are pure MCP |
| GEOX | `pip install arifos[geox,io]` | geoscience stack + document I/O |
| WEALTH | `pip install arifos[wealth,db,observe]` | valuation stack + ORM + telemetry |
| AAA | `pip install arifos[aaa]` | A2A NATS messaging |
| arifOS federation node | `pip install arifos[full]` | everything |
| `uvx` quick start | `uvx arifos` | kernel only, sovereign |
| Constitutional floors only | `pip install arifos[ml]` | F5/F6/F9 SBERT enforcement |

---

## Migration Phases

### Phase 1 — Dependency Floor Alignment

**Safe — no code changes, no renames, pyproject.toml edits only.**
**Execute now. arifOS kernel restart recommended first (WELL signal: AMBER).**

**Python organ changes:**

| File | Change |
|---|---|
| `well/pyproject.toml` | `fastmcp>=3.3.1,<4.0` → `fastmcp[tasks]==3.4.2`; audit for sentence-transformers (move to extras note only) |
| `wealth/pyproject.toml` | numpy `1.26→2.4.6`, scipy `1.10→1.17.1`, pydantic `2.0→2.13.4`, fastmcp `3.3.1→3.4.2`, asyncpg `0.29→0.31`, uvicorn `0.30→0.49`, fastapi `0.115→0.136.1`; pin all unpinned deps with canonical floors |
| `geox/pyproject.toml` | fastmcp `>=3.4.2,<4.0` → `==3.4.2` (exact pin) |
| `well/src/pyproject.toml` | **DELETE** — stale `afwell` package, fastmcp 2.x, incompatible API |

**JS organ changes:**

| File | Change |
|---|---|
| `AAA/a2a-server/package.json` | `express ^4.21 → ^5.2.1` (see express 5 note below) |
| `AAA/services/a2a-gateway/package.json` | `express ^4.18 → ^5.2.1` |
| `arifOS/arifosmcp/packages/npm/arifos-mcp/package.json` | `@modelcontextprotocol/sdk ^1.0→^1.9`, `typescript ^5.3→^6.0.3` |
| `A-FORGE/package.json` | `@supabase/supabase-js ^2.107→^2.108` |

> **Express 5 migration note:** Express 5 changed error middleware behaviour and `req.query` no longer uses `qs` by default. After upgrading AAA a2a-server and a2a-gateway, verify: (1) any `(err, req, res, next)` error handler signatures still work, (2) query string parsing is equivalent. Both services are simple — no complex middleware chains expected.

**Commit message:** `chore: align federation dependency floors — canonical matrix 2026-06-19`

---

### Phase 2 — Package Consolidation

**pyproject.toml structural change only — no Python code changes.**

1. Delete `C:\ariffazil\arifOS\pyproject.toml` (root wrapper, redundant)
2. Promote `C:\ariffazil\arifOS\arifosmcp\pyproject.toml` → `C:\ariffazil\arifOS\pyproject.toml`
3. Replace `[dependencies]` and `[optional-dependencies]` with the full tier map above
4. Update `[tool.setuptools.packages.find]` to target `arifos/` (prep for Phase 3 rename)
5. Add `aaa-mcp` to `[project.scripts]` alongside `arifos-mcp` (legacy alias)

**Deps moving from mandatory → extras (these must leave the mandatory list):**

| Package | Moves to |
|---|---|
| `sentence-transformers` | `[ml]` |
| `scikit-learn` | `[ml]` |
| `qdrant-client`, `chromadb`, `lancedb` | `[vectors]` |
| `playwright`, `beautifulsoup4` | `[browser]` |
| `torch`, `transformers` | `[heavy]` |
| `opentelemetry-api`, `opentelemetry-sdk` | `[observe]` |
| `pymupdf`, `pdfplumber`, `python-docx`, `openpyxl`, `pillow`, `blake3`, `pynacl` | `[io]` |
| `tavily-python`, `exa-py`, `firecrawl-py`, `trafilatura`, `readability-lxml`, `markdownify`, `html2text`, `bleach`, `defusedxml`, `tldextract` | `[search]` |
| `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, `google-genai` | `[google]` |
| `sqlalchemy`, `alembic`, `psycopg2-binary` | `[db]` |
| `lasio`, `welly`, `striplog`, `segyio`, `statsmodels`, `scipy`, `matplotlib`, `pyproj` | `[geox]` |
| `supabase`, `numpy-financial`, `psycopg[binary]`, `yfinance`, `duckdb`, `polars`, etc. | `[wealth]` |

**Commit message:** `chore: consolidate to single pyproject.toml with full domain extras gating`

---

### Phase 3 — Module Rename

**Code change. Execute only after arifOS kernel is confirmed UP.**

**Pre-execution gate (do not skip):**
```
1. Restart arifOS at arifos.arif-fazil.com
2. Run well_attest_to_kernel to reseal WELL identity
3. Confirm WELL returns GREEN before proceeding
```

**Steps:**
1. `git mv arifosmcp/ arifos/` — rename the Python package directory
2. Bulk replace all `arifosmcp` → `arifos` in Python source (`*.py`, `*.toml`, `*.json`, `*.md`)
3. Update Claude Code MCP config: `python -m arifosmcp.runtime stdio` → `python -m arifos.runtime stdio`
4. Update organ `mcp.json` configs that reference `arifosmcp` entrypoint
   - `C:\Users\User\.claude\mcp.json`
   - `C:\Users\User\AppData\Roaming\Antigravity\User\mcp.json`
   - `C:\Users\User\.gemini\antigravity\mcp_config.json`
5. Update `CLAUDE.md` references (global + project-level)
6. Update `README.md` and all docs

**Post-rename verification (must all pass before commit):**
```bash
grep -r "arifosmcp" --include="*.py" --include="*.toml" --include="*.json" .
# must return zero results

python -m arifos.runtime stdio   # must respond
pytest -m "not integration"       # must be green
```

**Commit message:** `feat!: rename module arifosmcp → arifos — MCP is transport, not identity`

---

### Phase 4 — PyPI Cleanup

**888_HOLD — explicit F13 confirmation required per action.**

Each action below is irreversible. Confirm individually before execution:

1. **Yank** `arifos==1!2026.6.11` from PyPI (epoch was accidental)
2. **Publish** `arifos==2026.06.19` with new module structure (confirm installable first)
3. **Publish redirect stub** for `arifosmcp`:
   ```
   Deprecated: this package has been merged into `arifos`.
   pip install arifos
   ```
4. **Update smithery.yaml** and federation registry entries to reflect `arifos` canonical name

---

## Organ Coverage Summary

| Organ | Language | Domain | Install path after Phase 2 | Key dep changes |
|---|---|---|---|---|
| arifOS kernel | Python | Constitutional substrate | `pip install arifos` | Consolidates arifosmcp |
| WELL | Python | Human substrate governance | `pip install arifos` | fastmcp `3.3.1→3.4.2` |
| WEALTH | Python | Capital intelligence | `pip install arifos[wealth,db,observe]` | 7 floor bumps; 15 deps pinned |
| GEOX | Python | Earth intelligence | `pip install arifos[geox,io]` | fastmcp exact pin; scipy/matplotlib explicit |
| AAA | JS (React + Node) | A2A control plane | `npm i` (no Python) | express `^4→^5`; zod stays split |
| A-FORGE | JS (Node) | Agent runtime | `npm i` (no Python) | supabase `^2.107→^2.108` |

---

## What This Does NOT Cover (Future Sessions)

The AGI/ASI kernel architecture layers — agent identity model (Darjat/Malu), multi-agent
orchestration (Hermes/OpenClaw), task graph engine, closed-loop learning — are intentionally
deferred. Many may already exist under different names in `arifosmcp/` (ConstitutionKernel,
FloorEvaluator, SessionRegistry, VAULT999). A post-rename codebase audit will determine what
exists vs. what genuinely needs to be built before committing to a new design session.

---

## Non-Goals

- Do not add new functionality in any phase
- Do not refactor internal `arifos/` module structure beyond the rename
- Do not change the MCP protocol surface (tools, schemas, tool names)
- Do not remove GEOX's `setuptools<70` constraint — intentional welly workaround
- Do not upgrade AAA React zod `^4.x` — it is in a separate runtime, not a conflict

---

## Risk Register

| Risk | Phase | Mitigation |
|---|---|---|
| WEALTH breaks on numpy 2.x API changes | 1 | `pytest -m "not integration"` in `wealth/` after Phase 1 |
| express 5 breaking changes in AAA a2a services | 1 | Verify error handler signatures + query parsing after upgrade |
| WEALTH unpinned deps (`pydantic-ai`, `langgraph`, etc.) resolve to incompatible versions | 1 | Pin explicitly to canonical floors in `wealth/pyproject.toml` |
| Import rename misses a file | 3 | `grep -r "arifosmcp"` must return zero before commit |
| PyPI yank blocks existing users pinned to `1!2026.6.11` | 4 | Publish new version first; yank only after confirmed installable |
| Phase 3 executed while kernel is down | 3 | Pre-execution gate: kernel must be UP, WELL must return GREEN |
| `arifos-mcp` / `aaa-mcp` aliases removed prematurely | 3 | Keep both as transition aliases; remove only in next calendar major |
