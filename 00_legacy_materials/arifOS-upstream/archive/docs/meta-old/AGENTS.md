# AGENTS.md — arifOS Development Guide

**Project:** arifOS — Constitutional AI Governance System (Python MCP Server)
**Python:** >=3.12 (runtime) | tooling targets py310+ | **Version:** 2026.2.27
**Motto:** *Ditempa Bukan Diberi* — Forged, Not Given

This file is the PRIMARY guidance document for agentic coding tools in this repository.
Goal: safe, reversible, test-backed changes that respect architecture and governance boundaries.

---

## Source of Truth Hierarchy
- **PRIMARY:** `AGENTS.md` (this file), `pyproject.toml`, and repository code.
- **SECONDARY:** `.github/copilot-instructions.md` (derivative; key content integrated below).
- **TERTIARY:** Sealed receipts in `VAULT999/`, `spec/v46/*`, `ARIFOS_SKILLS_REGISTRY.md`.
- Cursor rules status: no `.cursorrules` or `.cursor/rules/` present.

---

## Repository Layout
```
core/           Pure governance/kernel logic (7-Organ Sovereign Stack) — NO transport imports
arifosmcp.transport/        Transport and MCP adapter layer — NO decision logic
arifosmcp.intelligence/      Console / 9-Sense Federation Hub
tests/          Unit, integration, and constitutional tests
spec/           Canonical governance specs (v46 floors, stages, traceability)
VAULT999/       Immutable sealed receipts (append-only)
```

---

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install uv && uv pip install -e ".[dev]"
# Fallback (no uv):
pip install -e ".[dev]"
```

---

## Build, Lint, and Typecheck
```bash
black . --line-length 100               # Format
ruff check . --line-length 100          # Lint
ruff check . --line-length 100 --fix    # Lint with auto-fix
mypy .                                  # Type check (strict on core/ modules)
```
- Ruff excludes `tests/**` and `archive/**` (see `pyproject.toml`).
- MyPy applies stricter overrides to `core.governance_kernel`, `core.judgment`, `core.pipeline`, `core.organs.*`.

---

## Test Commands
```bash
pytest tests/ -v                                              # All tests
pytest tests/test_file.py -v                                  # Single file
pytest tests/test_file.py::TestClassName -v                   # Single class
pytest tests/test_file.py::TestClassName::test_method -v      # Single method
pytest tests/test_file.py::test_function_name -v              # Single function
pytest -m constitutional -v                                   # Constitutional floor tests
pytest -m integration -v                                      # Integration tests
pytest -m "not slow" -v                                       # Skip slow tests
pytest tests/test_mcp_quick.py -v                             # Quick MCP smoke test
```
**Async policy:** `asyncio_mode = "auto"` — do NOT add `@pytest.mark.asyncio` decorators.
**Auto-set env in conftest:** `ARIFOS_PHYSICS_DISABLED=1`, `ARIFOS_ALLOW_LEGACY_SPEC=1`, `AAA_MCP_OUTPUT_MODE=debug`.

---

## Run the Server
```bash
python -m arifosmcp.transport              # stdio (default)
python -m arifosmcp.transport sse          # SSE transport
python -m arifosmcp.transport http         # Streamable HTTP
python -m arifosmcp.transport.selftest     # Self-test
arifos serve --profile strict --metrics
arifos deploy --target docker --stack trinity2
arifos health --endpoint http://localhost:8888/health
```

---

## Environment Variables
| Variable | Purpose |
|----------|---------|
| `ARIF_SECRET` / `ARIF_JWT_SECRET` | Authentication for SSE/HTTP transports |
| `BRAVE_API_KEY` / `OPENAI_API_KEY` | External search tools |
| `DATABASE_URL` / `REDIS_URL` | VAULT999 persistence and session cache |
| `AAA_MCP_TRANSPORT` | Override transport: `stdio` / `sse` / `http` |
| `AAA_MCP_OUTPUT_MODE` | `user` or `debug` |
| `ARIFOS_PHYSICS_DISABLED` | Set `1` to skip thermodynamic calculations |
| `ARIFOS_ALLOW_LEGACY_SPEC` | Set `1` to bypass spec version gating in tests |

Copy `.env.docker.example` to `.env.docker` and fill in keys before deploying.

---

## Code Style Guidelines

### Import Order
1. Standard library (`os`, `hashlib`, `typing`, etc.)
2. Third-party (`pydantic`, `fastmcp`, `numpy`, etc.)
3. Local packages (`core.*`, `arifosmcp.transport.*`, `arifosmcp.intelligence.*`)

Do not shadow the external SDK name `mcp` with any local module.
Use `try/except ImportError` for optional dependencies (lazy imports).

### Formatting and Types
- **Line length:** 100 characters (Black + Ruff)
- **Type hints:** Required on all function signatures in production code
- **Data models:** Pydantic v2 `BaseModel` for I/O contracts
- **Enums:** `class Verdict(str, Enum)` pattern
- **Async:** All I/O-bound functions MUST be `async def`

### Naming Conventions
| Type | Convention | Example |
|------|-----------|---------|
| Modules | `snake_case` | `governance_kernel.py` |
| Classes | `PascalCase` | `GovernanceKernel` |
| Functions/Variables | `snake_case` | `compute_uncertainty` |
| Constants | `UPPER_SNAKE_CASE` | `UNCERTAINTY_THRESHOLD` |
| Private helpers | `_prefix` | `_generate_session_id` |
| Organ modules | `_N_name.py` | `_0_init.py`, `_1_agi.py` |

### Error Handling
- **MCP tools** catch all exceptions and return structured dicts:
  ```python
  except Exception as e:
      return {"verdict": "VOID", "error": str(e), "stage": "222_REASON"}
  ```
- **`core/` kernel functions** may raise exceptions for internal errors.
- Never swallow errors silently.

### Decorator Order
`@mcp.tool()` must be OUTER, `@constitutional_floor()` must be INNER:
```python
@mcp.tool(name="reason", description="...")
@constitutional_floor("F2", "F4", "F7")
async def reason(query: str) -> dict: ...
```

### Module Hygiene
- Every non-trivial module must have a module docstring.
- Use section delimiters: `# ═══════════════════════════════════════════════════════`
- Define `__all__` exports explicitly.
- STDIO mode: NEVER use `print()` or write to `stdout`. Use `sys.stderr` or the logger.

---

## Architecture Constraints
1. **`core/` is pure:** No imports from `fastmcp`, `starlette`, `fastapi`, `uvicorn`, or any transport/HTTP library.
2. **`arifosmcp.transport/` is transport only:** No governance decision logic. Calls `core/` functions.
3. **Do NOT shadow `mcp`:** External SDK is `mcp`. No local module may use that name.
4. **SessionState is copy-on-write:** Never mutate session state in place.
5. **Separation of powers:** Architect (Δ) ≠ Engineer (Ω) ≠ Auditor (Ψ) ≠ KIMI (Κ).

---

## Testing Requirements
- All new functionality MUST have tests.
- Place tests in the appropriate `tests/` subtree.
- Run focused single tests first, then the broader suite to confirm no regressions.

---

## MCP Tools Reference
9 governance tools: `anchor` (000), `reason` (222), `integrate` (333), `respond` (444),
`validate` (555), `align` (666), `forge` (777), `audit` (888), `seal` (999).
Additional: `search`, `fetch`. Confirm current list in `arifosmcp.transport/server.py` before edits.

---

## OpenCode Session Lifecycle (Mandatory)
1. **Session Open:** Restore prior sealed state from VAULT999 (latest 999 receipt).
2. **000 INIT:** Run stage `000` immediately after vault restore — before any implementation.
3. **Execution Window:** Work through governed stages with explicit receipts.
4. **Session Close:** Run `999 SEAL` before handoff, with continuity notes for the next `000`.

**Hard rule:** No session starts directly at 222/333/444. Must follow: `VAULT999 restore → 000 INIT → governed execution`.
**Canonical stage spine:** `000 → 444 → 666 → 888 → 999`.

---

## 888 HOLD — Mandatory Human Confirmation
Stop and await explicit human approval when any trigger below is met:

**Original triggers:** database-destructive ops, production deployments, mass file changes (>10 files),
credential/secret handling, git history modification, bypassing constitutional failures.

**v41.2 Expanded triggers:**
- **H-USER-CORRECTION:** User corrects or disputes a constitutional claim
- **H-SOURCE-CONFLICT:** Conflicting evidence across source tiers (PRIMARY vs SECONDARY vs TERTIARY)
- **H-NO-PRIMARY:** Constitutional claim made without reading spec JSON
- **H-GREP-CONTRADICTS:** Search results contradict spec/canon patterns
- **H-RUSHED-FIX:** Proposing fixes based on <5 minutes of audit

**Action sequence:**
1. Declare: `888 HOLD — [trigger type] detected`
2. List conflicts: PRIMARY vs SECONDARY vs TERTIARY sources
3. Re-read PRIMARY: verify against spec JSON or SEALED canon
4. Await: `"Ready to proceed after verification"` — wait for explicit human approval

---

## Floor Violations Quick Reference
| Floor | Code Smell | Fix |
|-------|------------|-----|
| F1 | Mutates input, hidden side effects | Pure functions, explicit returns |
| F2 | Fabricated data, fake metrics | Empty/null when unknown |
| F3 | Contract mismatch, type lies | Use canonical interfaces |
| F4 | Magic numbers, obscure logic | Named constants, clear params |
| F5 | Destructive defaults, no backup | Safe defaults, preserve state |
| F6 | Only happy path, cryptic errors | Handle edge cases, clear messages |
| F7 | False confidence, fake computation | Admit uncertainty, cap confidence |
| F8 | Bypasses governance, invents patterns | Use established systems |
| F9 | Deceptive naming, hidden behavior | Honest names, transparent logic |
| F10–F13 | See `spec/v46/constitutional_floors.json` | Symbolic Guard, Command Auth, Injection Defense |

---

## Output Format for Governed Stages
```
[STAGE NNN] Stage Name
Status: [IN_PROGRESS | COMPLETE]
Floor Scores: F1=X F2=X ... F9=X
Verdict: [SEAL | PARTIAL | SABAR | VOID | 888_HOLD]
```

---

## v46 Alignment (from `.github/copilot-instructions.md`)
- Canonical sources: `AGENTS.md`, `spec/v46/*`, `L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md`.
- 12 constitutional floors in `spec/v46/constitutional_floors.json` (F1–F12: Truth through Injection Defense).
- Drift check: `rg --hidden -n "v45" .agent .codex .claude .kimi .cursor .gemini .github`
- Skills sync: `python scripts/sync_skills.py --check`
- Human veto power is ABSOLUTE. AI role is to propose, not decide.

---

## Practical Agent Workflow
1. Read target files and nearby tests first.
2. Implement the smallest safe change that solves the request.
3. Run a focused single test, then the broader suite to confirm no regressions.
4. Report what changed and what was actually verified — never fabricate steps.

*Last Updated: 2026-02-23*
