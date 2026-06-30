# arifOS — Entry Point

**Status:** SOVEREIGN KERNEL | **Organ:** MIND (Δ) | **Authority:** 888_JUDGE

## Quick Start
```bash
# Install
pip install -e .

# Start MCP server (HTTP + SSE — port 8088)
PYTHONPATH=/root/arifOS python3.12 -m arifOS.arifosmcp.server

# Start MCP server (stdio)
PYTHONPATH=/root/arifOS python3.12 -m arifOS.arifosmcp.server --transport stdio

# Health check
curl http://localhost:8088/health
```

## Critical Files
| File | Purpose |
|------|---------|
| `core/floors.py` | F1-F13 floor enforcement |
| `VAULT999/` | Append-only VAULT999 ledger |
| `APEX/ASF1/tool_registry.json` | 13-tool canonical registry |
| `arifosmcp/server.py` | FastMCP MCP server entry point |
| `arifosmcp/constitutional_map.py` | Pre-flight gates, risk tiers |
| `AGENTS.md` | Full agent onboarding |

## 13 Canonical Tools
```
arif_session_init    — 000_INIT  | Session bootstrap + identity
arif_sense_observe   — 111_OBSERVE | Reality grounding / vitals
arif_evidence_fetch  — 222_EVIDENCE | Verified external evidence
arif_mind_reason     — 333_REASON  | Symbolic reasoning / synthesis
arif_kernel_route    — 555_ROUTE   | Intent routing + delegation
arif_reply_compose  — 444_REPLY   | Governed response composition
arif_memory_recall   — 555m_MEMORY | Vector Postgres+Qdrant recall
arif_heart_critique  — 444_CRITIQUE | Ethical critique / consequence
arif_gateway_connect — 666_GATEWAY | Federated cross-agent bridge
arif_ops_measure     — 777_MEASURE | Machine health + thermodynamic cost
arif_judge_deliberate — 888_JUDGE | Constitutional arbitration
arif_vault_seal      — 999_SEAL    | Immutable VAULT999 ledger seal
arif_forge_execute   — 666_FORGE   | Build execution + artifact creation
```

## Federation
```
AAA (Body) ←→ arifOS (Kernel) ←→ A-FORGE (Forge)
```

See `AGENTS.md` for full agent onboarding context.

**999 SEAL ALIVE**