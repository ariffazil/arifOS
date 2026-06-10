# CLAUDE.md — arifOS Constitutional Kernel

> **The law of the federation. arifOS structures decision; it does not decide.**
> **DITEMPA BUKAN DIBERI — Forged, Not Given.**

---

## 0. LOADING SEQUENCE (read in 30 seconds)

```bash
# 1. Know the canonical surface:
cat arifosmcp/CANONICAL_PATHS.md
cat arifosmcp/PUBLIC_SURFACE_CANON.md

# 2. Know what tools are registered:
cat arifosmcp/tool_registry.json | python3 -m json.tool | grep '"name"'

# 3. Verify health:
curl -s http://localhost:8088/health | python3 -m json.tool

# 4. Confirm floor status:
curl -s http://localhost:8088/mcp | python3 -m json.tool | grep -E 'floor|tool'
```

---

## 1. WHAT THIS REPO IS

**arifOS** is the constitutional MCP kernel. It enforces 13 floors (F1–F13), routes agent actions through a governed pipeline (000→999), and seals terminal outcomes to VAULT999.

```
Arif (F13 SOVEREIGN)
    ↓
arifOS (13 constitutional tools — arif_*)
    ├── arif_session_init      — start a governed session
    ├── arif_sense_observe     — search/ingest/observe reality
    ├── arif_evidence_fetch    — fetch + cite external evidence
    ├── arif_mind_reason       — multi-step reasoning + planning
    ├── arif_heart_critique    — ethical risk + empathy audit
    ├── arif_judge_deliberate  — render constitutional verdict
    ├── arif_forge_execute     — execute approved builds/deploys
    ├── arif_vault_seal        — seal to immutable ledger
    ├── arif_memory_recall     — search/store session memory
    ├── arif_kernel_route      — route intent to correct tool
    ├── arif_ops_measure       — health + vitals + cost
    ├── arif_reply_compose     — compose final response
    └── arif_gateway_connect   — bridge to federation organs
```

**Golden path:** `session_init → sense_observe/evidence_fetch → mind_reason → heart_critique → judge_deliberate → vault_seal`

---

## 2. BUILD, TEST, LINT

```bash
# Install
uv sync --all-extras

# Run server
uv run python -m arifosmcp.runtime.server   # port 8088

# Full test suite
uv run pytest tests/ -q --tb=short

# CI subset (fast, < 2 min)
uv run pytest tests/test_phase0_standalone.py tests/test_surface_lock.py tests/test_registry.py -q --tb=short

# Lint
ruff check core/ arifosmcp/ tests/ --line-length 100
mypy arifosmcp/runtime/ --ignore-missing-imports
```

---

## 3. KEY DIRECTORIES

| Path | What lives here |
|------|-----------------|
| `arifosmcp/tools/` | 13 canonical `arif_*` tool handlers |
| `arifosmcp/runtime/` | FastMCP ASGI server, tool registration, A2A bridge |
| `arifosmcp/schemas/` | Pydantic 2 models for all tool I/O |
| `core/` | Floor enforcement, VAULT999 ledger, judgment primitives |
| `tests/` | 168 pytest files — constitutional, adversarial, integration |
| `arifosmcp/tool_registry.json` | Machine-readable canonical tool surface |
| `arifosmcp/CANONICAL_PATHS.md` | Source of truth map for all key files |

---

## 4. CONSTITUTIONAL LAW (F1–F13)

| Floor | Rule (short) |
|-------|-------------|
| F1 AMANAH | Reversible first. Git commit before destructive ops. |
| F2 TRUTH | ≥99% truth or declare confidence band. |
| F7 HUMILITY | Gödel band [0.03–0.15]. No fake certainty. |
| F9 ANTI-HANTU | No hallucinated APIs, filenames, or endpoints. |
| F11 AUTH | Confirm before destructive/critical ops. |
| F13 SOVEREIGN | Arif's veto is absolute. No autonomous override. |

---

## 5. CONVENTIONS

- **Public names are `arif_*`**, never `arifos_*`. Legacy aliases exist; don't add new ones.
- **asyncio_mode = auto** — don't add `@pytest.mark.asyncio` unless the file already uses it.
- **New tools** → extend handler in `arifosmcp/tools/`, update `constitutional_map.py`, regenerate `tool_registry.json`, update `PUBLIC_SURFACE_CANON.md` and `CANONICAL_PATHS.md`.
- **Canonical paths beat docs** — trust `CANONICAL_PATHS.md` over any README.
- **888_HOLD before:** `rm -rf`, vault writes, force push, production deploy, secret rotation.

---

## 6. FORBIDDEN ACTIONS

- Issue SEAL/SABAR/VOID without Arif's approval (F13)
- Modify F1–F13 floors without explicit approval
- Force push / reset hard
- Drop databases or delete data directories
- Add new top-level directories without ADR entry in `ADR_001_BOUNDARIES.md`

---

*Companion: `/root/AGENTS.md` (federation-wide), `/root/CONTEXT.md` (live state)*
*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
