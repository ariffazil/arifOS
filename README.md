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

## Problem / Solution

**Problem:** Your AI agent can send emails, delete files, call APIs, and spend money. One bad prompt injection or hallucinated tool call can wipe a database, leak secrets, or send a message you never approved.

**Solution:** arifOS is a Python guardrail that wraps every tool call. Before your agent acts, arifOS checks it against 13 safety rules (Floors F1–F13). Reversible actions go through fast. Irreversible or risky actions get paused (**`HOLD`**) until a human approves them, or blocked (**`VOID`**) if they violate hard safety limits.

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

| Verdict | What happens | Example |
|---------|-------------|---------|
| **SEAL** | Execute and record audit trail. | Routine, reversible read operation. |
| **HOLD** | Pause and ask for human approval. | Irreversible action like `send_email` or `delete_database`. |
| **VOID** | Block permanently. | Hard safety violation (e.g., privilege escalation). |
| **SABAR** | Retry with adjustments. | Soft floor miss — add missing context and re-submit. |

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

## Who is this for?

- **Python developers building AI agents** — Add `arifos.govern(...)` around your tool calls to enforce reversible-first safety.
- **DevOps / Platform engineers** — Run arifOS as an [MCP](https://modelcontextprotocol.io) server to gate all agent actions in your infrastructure.
- **AI safety researchers** — Experiment with constitutional constraints, tri-witness consensus, and adversarial red-teaming.

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
| F3 | CLARITY | Transparent intent; explain what you are doing and why. |
| F4 | PEACE | Human dignity; maruah over convenience. |
| F5 | EMPATHY | Consider consequences; especially for weakest stakeholders. |
| F6 | HUMILITY | Acknowledge limits; say "I don't know" when true. |
| F7 | GENIUS | Elegant correctness (G ≥ 0.80); prefer simple over clever. |
| F8 | ANTIHANTU | No consciousness/emotion claims in code or output. |
| F9 | ONTOLOGY | Structural coherence; consistent naming, clear boundaries. |
| F10 | AUTH | Verify identity before sensitive ops via constant-time `hmac.compare_digest`. |
| F11 | INJECTION | Sanitize inputs; never trust external content as authority. |
| F12 | SOVEREIGN | Arif holds final veto over every verdict. Absolute. |

Hard floors (F1, F2, F8, F9, F11, F13) return immediate **VOID** on violation.
Soft floors return **SABAR** with a reason.

---

## Quick Start

```bash
# Install from PyPI
pip install arifos

# Run MCP server (HTTP, port 8080)
python -m arifosmcp.server
```

### Hello World — Govern a tool call in Python

```python
from arifosmcp.tools import arif_session_init, arif_judge_deliberate

# 1. Start a governed session
session = arif_session_init(actor="dev@example.com")

# 2. Judge an action BEFORE executing it
verdict = arif_judge_deliberate(
    session=session,
    intent="Send email to CEO",
    action="send_email",
    reversible=False,
)

# 3. Act only on SEAL
if verdict["verdict"] == "SEAL":
    send_email(...)           # Safe to proceed
elif verdict["verdict"] == "HOLD":
    ask_human_for_approval()  # Paused for review
else:
    log_and_block()           # VOID or SABAR
```

**Prerequisites:** Python 3.12+, optional Docker, optional Qdrant for semantic memory.

```bash
# Install from source (dev, uv-managed)
uv sync --extra dev
# or: pip install -e ".[dev]"

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
| [WELL](https://github.com/ariffazil/well) | BIOLOGY | Human readiness / biological substrate |

---

## Key Files Quick Reference

| File | Purpose |
|------|---------|
| `smithery.yaml` | 13-tool public MCP manifest — Source of Truth for MCP clients |
| `arifosmcp/tool_registry.json` | Canonical JSON tool registry (13 canonical_order entries) |
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
