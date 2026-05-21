<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-05-22
valid_from: 2026-05-22
valid_until: 2026-06-22
confidence: high
scope: /root/arifOS
epistemic_status: CLAIM
-->

# arifOS — Constitutional AI Governance Kernel

[![PyPI](https://img.shields.io/badge/PyPI-arifos-7C3AED?style=flat-square)](https://pypi.org/project/arifos/)
[![MCP](https://img.shields.io/badge/MCP-FastMCP_3.2-blue?style=flat-square)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/License-AGPL--3.0-green?style=flat-square)](./LICENSE)

> **In one sentence:** arifOS is the law layer — every AI tool call in this federation passes through it for validation, judgment, and audit before it can execute.

**Status:** SOVEREIGN KERNEL | **Organ:** MIND (Ω) | **Authority:** F13 SOVEREIGN (Arif)
**PyPI:** `pip install arifos` | **GHCR:** `ghcr.io/ariffazil/arifos`
**Live MCP:** `https://arifos.arif-fazil.com/mcp`

---

## What This Is

arifOS is a constitutional governance kernel for AI agents. It wraps every tool call, task execution, and agent action under 13 hard and soft constitutional invariants (Floors F1–F13). Think of it as the judge and auditor that sits between every AI agent and every action it wants to take.

Every request flows through a 13-stage metabolic pipeline:

```
User / Agent Intent
        ↓
000 INIT → 111 SENSE → 333 MIND → 444 KERNEL → 555 MEMORY
                                                      ↓
999 VAULT ← 888 JUDGE ← 777 OPS ← 666 HEART ← 010 FORGE
 (seal)     (verdict)    (cost)   (red-team)   (execute)
```

**HOLD** = stop and ask Arif. **VOID** = never. **SEAL** = approved and recorded.

---

## What It Owns vs. What It Doesn't

| Owns | Does NOT Own |
|------|--------------|
| Constitutional Law (F1–F13) | Frontend cockpit → [AAA](https://github.com/ariffazil/AAA) |
| 13 canonical MCP tools | Execution orchestration → [A-FORGE](https://github.com/ariffazil/A-FORGE) |
| VAULT999 immutable ledger | Earth-science interpretation → [GEOX](https://github.com/ariffazil/geox) |
| `smithery.yaml` public manifest | Economic modeling → [WEALTH](https://github.com/ariffazil/wealth) |
| A2A federation mesh routing | Human readiness → WELL |

---

## The 13 Constitutional Tools

Each tool owns one stage. Agents call them in sequence for governed workflows.

| Stage | Tool | What It Does |
|-------|------|-------------|
| 000 | `arif_session_init` | Bind actor identity; anchor session to constitution hash |
| 111 | `arif_sense_observe` | Ground reality — web search, VPS vitals, atlas, entropy_dS |
| 222 | `arif_evidence_fetch` | Pull external data with F-WEB receipts (prevents injection) |
| 333 | `arif_mind_reason` | Structured reasoning + contradiction detection (plan/verify) |
| 444 | `arif_kernel_route` | Route intent to AGI/ASI/APEX lane; risk and budget gates |
| 444r | `arif_reply_compose` | Assemble governed response with LLM compose |
| 555 | `arif_memory_recall` | Semantic memory via Qdrant + BGE-M3 embeddings |
| 666 | `arif_heart_critique` | Adversarial F5/F6/F9 critique pass + F-WEB injection scan |
| 666g | `arif_gateway_connect` | A2A agent mesh handshake under F1–F13 |
| 777 | `arif_ops_measure` | Landauer cost + reversibility classification |
| 888 | `arif_judge_deliberate` | Issue SEAL / HOLD / VOID / SABAR verdict |
| 999 | `arif_vault_seal` | Anchor to immutable Merkle-V3 ledger (append-only) |
| 010 | `arif_forge_execute` | Execute — only after 888_JUDGE SEAL; dry_run by default |

---

## The 13 Constitutional Floors (F1–F13)

Every tool call is checked against all 13 floors before execution:

| Floor | Name | Rule |
|-------|------|------|
| F1 | AMANAH | Reversible first. Irreversible requires explicit human ack. |
| F2 | TRUTH | ≥99% truth or declare uncertainty band (0.03–0.15). |
| F3 | WITNESS | Human-AI-Evidence tri-witness must align before output. |
| F4 | BALANCE | No winner-takes-all outcomes. |
| F5 | PEACE | Peace score ≥ 1.0; no silent harm. |
| F6 | DIGNITY | Human dignity preserved in every response. |
| F7 | HUMILITY | Uncertainty band declared on every substantive claim. |
| F8 | CONTINUITY | Session continuity preserved across turns. |
| F9 | ANTI-HANTU | No hallucination. Missing inputs → HOLD, not guess. |
| F10 | SUSTAINABILITY | No runaway resource consumption. |
| F11 | AUTH | Constant-time auth via `hmac.compare_digest`. No privilege escalation. |
| F12 | GUARD | Scan for external instruction overrides before every tool call. |
| F13 | SOVEREIGN | Arif holds final veto over every verdict. Absolute. |

Hard floors (F1, F2, F9, F11, F13) return immediate **VOID** on violation.
Soft floors return **SABAR** with a reason.

---

## Quick Start

```bash
# Install from PyPI
pip install arifos

# Install from source (dev, uv-managed)
uv sync --extra dev
# or: pip install -e ".[dev]"

# Run MCP server (HTTP, port 8080)
python -m arifosmcp.server

# Run MCP server (stdio — for Claude Desktop, Cursor, etc.)
python -m arifosmcp.__main__ --mode stdio

# Run tests
pytest tests/ -q --tb=short

# Docker
docker run -p 8080:8080 ghcr.io/ariffazil/arifos:latest
```

### Connect via Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "arifos": {
      "type": "http",
      "url": "https://arifos.arif-fazil.com/mcp"
    }
  }
}
```

### Connect via Cursor / Windsurf / any MCP client (stdio)

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "arifosmcp.__main__", "--mode", "stdio"]
    }
  }
}
```

---

## Repository Structure

```
arifOS/
├── arifosmcp/              # PRIMARY: pip-installable MCP runtime package
│   ├── server.py           # FastMCP + FastAPI entrypoint (port 8080)
│   ├── __main__.py         # CLI: stdio | http | streamable-http
│   ├── tools/              # 13 canonical tool implementations
│   ├── runtime/            # HTTP server, REST routes, JWT, A2A mesh, megaTools
│   ├── schemas/            # Pydantic output schemas (VerdictOutput, SealOutput, etc.)
│   ├── core/               # Floor enforcement shims
│   ├── memory/             # Qdrant + BGE-M3 semantic memory
│   ├── intelligence/       # 9-Sense federation hub, thinking sessions
│   ├── providers/          # LLM aggregation (SEA-LION → Ollama → rule fallback)
│   ├── smithery.yaml       # 13-tool public MCP manifest (Source of Truth)
│   └── Dockerfile          # Production image (EXPOSE 8080)
│
├── core/                   # ROOT: constitutional kernel (deepest law)
│   ├── floors.py           # F1–F13 enforcement (~947 lines)
│   ├── judgment.py         # Verdict engine (SEAL/HOLD/VOID/SABAR)
│   └── vault999/           # Append-only Merkle-V3 hash-chained ledger
│
├── VAULT999/               # Local vault ledger (append-only, never edit)
│
├── tests/                  # ~125 pytest modules (asyncio_mode=auto)
│   ├── constitutional/     # Floor compliance tests
│   ├── adversarial/        # Injection + jailbreak tests
│   └── integration/        # Full federation E2E
│
├── smithery.yaml           # PUBLIC MCP manifest (use this for tool discovery)
├── pyproject.toml          # Package charter (uv-managed, PyPI-publishable)
└── Makefile                # build, test, deploy, publish, health targets
```

---

## For Agentic Coders: How to Extend

### Add a new tool

1. Create `arifosmcp/tools/arif_<noun>_<verb>.py`
2. Define an `@mcp.tool` function that accepts a typed Pydantic model
3. Register in `arifosmcp/tool_registry.json` under `canonical_order`
4. Add entry to `smithery.yaml` under `tools`
5. Declare floor dependencies in the function docstring: `floors: [F1, F2, F9]`
6. Write tests in `tests/core/test_<toolname>.py`

### Understand the output contract

Every tool must return a dict matching:

```python
{
    "verdict": "SEAL | SABAR | HOLD | VOID",
    "payload": {},
    "floor_compliance": {"F1": True, "F2": True, ...},
    "epistemic_snapshot": {"confidence": 0.9, "uncertainty_band": 0.05},
    "audit_trail": {}
}
```

### Key invariant: floor enforcement

Every tool passes through `core/floors.py → FloorEnforcer.check()`.
Hard floors return immediate VOID. Soft floors return SABAR with `reason`.
Never bypass the floor enforcer. `FloorEnforcer` is the law.

### The 3-tier fallback for LLM reasoning

All reasoning tools use: **SEA-LION (primary) → Ollama (local fallback) → deterministic rule fallback**.
Deterministic fallbacks are guaranteed to return a valid verdict even when all LLMs are offline.

---

## Health Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Full status: tools, floors, vault, graphiti, memory |
| `GET /tools` | Live tool listing (MCP surface) |
| `GET /.well-known/mcp/server.json` | MCP server manifest |
| `GET /.well-known/agent.json` | A2A Agent Card (agent discovery) |
| `GET /ping` | Liveness check |

---

## Federation Map

| Repo | Role | Plain Purpose |
|------|------|---------------|
| **arifOS** | LAW | Decides what's allowed, held, or void |
| [AAA](https://github.com/ariffazil/AAA) | INTERFACE | Human cockpit + A2A agent gateway |
| [A-FORGE](https://github.com/ariffazil/A-FORGE) | EXECUTION | Runs governed agent workloads |
| [GEOX](https://github.com/ariffazil/geox) | FIELD | Earth-science evidence engine |
| [WEALTH](https://github.com/ariffazil/wealth) | CAPITAL | Financial / capital evidence engine |

---

## Key Files Quick Reference

| File | Purpose |
|------|---------|
| `smithery.yaml` | 13-tool public MCP manifest — Source of Truth for MCP clients |
| `arifosmcp/tool_registry.json` | Canonical JSON tool registry (15 entries including ping/selftest) |
| `core/floors.py` | F1–F13 constitutional enforcement (~947 lines) |
| `VAULT999/` | Append-only hash-chained audit ledger (never edit directly) |
| `arifosmcp/runtime/` | HTTP server, JWT, A2A mesh, REST routes |
| `pyproject.toml` | Package charter — version, deps, optional extras |

---

## TREE777 Wiki

The full federation knowledge base, architecture decisions, and agent documentation:
→ **https://wiki.arif-fazil.com**

---

*Last Verified: 2026-05-22 | 999 SEAL ALIVE*
**DITEMPA BUKAN DIBERI — Intelligence is forged, not given.**
