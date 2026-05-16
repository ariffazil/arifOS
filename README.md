# arifOS — Constitutional AI Governance Kernel

> **Status:** SOVEREIGN KERNEL | **Organ:** MIND (Δ) | **Authority:** 888_JUDGE
> **PyPI:** `arifos` | **GHCR:** `ghcr.io/ariffazil/arifos`
> **MCP (canonical):** `https://arifos.arif-fazil.com/mcp`
> **MCP (short alias):** `https://mcp.arif-fazil.com/mcp`

## 🏛️ What this repo is

The central governance kernel of the arifOS federation. It defines the 13 Constitutional Floors (F1–F13) and hosts the canonical `arifosmcp` server — a FastMCP-powered governed runtime that exposes **13 canonical tools** to AI agents, every call passing through intent validation → constitutional floor checks → verdict before action.

**Every tool call is stateful, governed, and pipeline-aware.**

## 📦 Ownership

- **Owns**: Constitutional Law (F1–F13), `arifosmcp` core logic, VAULT999 ledger, `smithery.yaml` registry.
- **Does NOT own**: Frontend surfaces (AAA), Infrastructure orchestration (A-FORGE), Domain logic (GEOX/WELL).

## 🏗️ Current Structure

```
arifOS/
├── arifosmcp/              # Primary MCP runtime package (pip install target)
│   ├── server.py           # FastMCP + FastAPI entry point
│   ├── runtime/           # Dozens of runtime modules (tools, sessions, bridges)
│   ├── tools/             # Tool implementations
│   ├── schemas/           # Pydantic output schemas
│   ├── core/              # Governance kernel shims (floor, embodied_engine)
│   ├── Dockerfile         # Multi-stage production build (EXPOSE 8080)
│   └── MCP_TOOLS_README.md
├── core/                   # Root-level constitutional kernel
│   ├── floors.py           # F1–F13 enforcement (~924 lines)
│   ├── judgment.py         # Verdict engine
│   └── vault999/          # Append-only hash-chained ledger
├── VAULT999/               # Local vault ledger
├── tests/                  # Hundreds of test files (pytest, asyncio_mode=auto)
├── smithery.yaml           # Canonical 13-tool manifest (public registry)
├── pyproject.toml         # Root package charter
└── Makefile               # build, test, deploy targets
```

## 🧬 13 Canonical Tools (arif_noun_verb)

Sourced from `arifosmcp/tool_registry.json` (`canonical_order`):

| Stage | Tool | Purpose |
|-------|------|---------|
| 000 | `arif_session_init` | Bind actor identity, set safety state = HOLD |
| 111 | `arif_sense_observe` | Reality grounding (web, VPS vitals, atlas) |
| 222 | `arif_evidence_fetch` | External data oracle (GEOX, FRED, EIA) |
| 333 | `arif_mind_reason` | Structured reasoning + contradiction detection |
| 444 | `arif_kernel_route` | Routing + risk orthogonality (AGI/ASI/APEX lanes) |
| 444r | `arif_reply_compose` | Governed response assembly |
| 555 | `arif_memory_recall` | Semantic memory + skill registry |
| 666 | `arif_heart_critique` | Adversarial F5/F6/F9 pass |
| 666g | `arif_gateway_connect` | A2A mesh under F1–F13 |
| 777 | `arif_ops_measure` | Landauer cost + reversibility classification |
| 888 | `arif_judge_deliberate` | SEAL / HOLD / VOID / SABAR verdict |
| 999 | `arif_vault_seal` | Immutable Merkle-V3 ledger anchor |
| 010 | `arif_forge_execute` | Execution bridge (SEAL-gated only) |

> **Note:** `tool_registry.json` and this table agree on **13 constitutional tools**. The `/.well-known/mcp/server.json` `public_surface` field reads `canonical15` — this is intentional: the MCP surface exposes 15 tools (13 constitutional + `arif_ping` + `arif_selftest` probes). `smithery.yaml` also lists 13 because it tracks constitutional tools only.

## 🚀 Verified Commands

```bash
# Install from PyPI
pip install arifos

# Install from source (editable, with dev extras)
pip install -e ".[dev]"

# Run MCP server (HTTP + SSE)
python -m arifosmcp.server
# or via module:
python -m arifosmcp.runtime.__main__

# Run MCP server (stdio transport)
python -m arifosmcp.runtime.__main__ --mode stdio

# Test
pytest tests/ -q --tb=short

# Docker build (uses arifosmcp/Dockerfile)
docker build -f arifosmcp/Dockerfile -t ghcr.io/ariffazil/arifos:latest .
docker run -p 8080:8080 ghcr.io/ariffazil/arifos:latest
```

## 🔗 Federation Loop

- [AAA](https://github.com/ariffazil/AAA) — Body (session cockpit, A2A gateway)
- [A-FORGE](https://github.com/ariffazil/A-FORGE) — Forge (deployment, infrastructure)
- [GEOX](https://github.com/ariffazil/geox) — Field (geoscientific data)
- [WELL](https://github.com/ariffazil/well) — Substrate (human bio-telemetry)
- [WEALTH](https://github.com/ariffazil/wealth) — Capital (economic logic)

## 📌 Key Files

| File | Purpose |
|------|---------|
| `smithery.yaml` | 13-tool public manifest (Source of Truth for MCP clients) |
| `arifosmcp/tool_registry.json` | Canonical 13-tool JSON registry (`canonical_order` field) |
| `arifosmcp/MCP_TOOLS_README.md` | Full tool surface documentation |
| `core/floors.py` | F1–F13 constitutional enforcement |
| `VAULT999/` | Append-only hash-chained audit ledger |
| `arifosmcp/core/kernel/` | Backward-compat shims for test file imports |

## 🏥 Health Endpoints

- `GET /health` — Full system status (13 tools, ML floors, vault, graphiti)
- `GET /tools` — Live tool listing
- `GET /.well-known/mcp/server.json` — MCP server manifest

---

*Last Verified: 2026.05.16 | Commit: 656f31f3 | 999 SEAL ALIVE*
