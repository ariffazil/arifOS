# arifOS Public Ambassador (Horizon)

> **FastMCP 2.x Compatible** deployment for Prefect Horizon

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER REQUEST                                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌─────────────────┐ ┌──────────┐ ┌─────────────────┐
│  ☁️ Horizon     │ │ 🔥 VPS   │ │ 💻 Local        │
│  (This Repo)    │ │ (Full)   │ │ (STDIO)         │
├─────────────────┤ ├──────────┤ ├─────────────────┤
│ 8 Tools         │ │ 11 Tools │ │ 11 Tools        │
│ FastMCP 2.12.3  │ │ FastMCP  │ │ FastMCP 3.1.1   │
│ Auto-scale      │ │ 3.1.1    │ │ Direct access   │
│ Public          │ │ Sovereign│ │ Development     │
│ Safe subset     │ │ Kernel   │ │                 │
└─────────────────┘ └──────────┘ └─────────────────┘
```

## Tool Comparison

| Tool | Horizon (8) | VPS (11) | Description |
|------|-------------|----------|-------------|
| `init_anchor` | ✅ | ✅ | Session initialization |
| `arifOS_kernel` | ✅ | ✅ | Metabolic router |
| `apex_soul` | ✅ | ✅ | Constitutional verdict |
| `agi_mind` | ✅ | ✅ | Reasoning engine |
| `asi_heart` | ✅ | ✅ | Safety critique |
| `physics_reality` | ✅ | ✅ | Reality grounding |
| `math_estimator` | ✅ | ✅ | Thermodynamic vitals |
| `architect_registry` | ✅ | ✅ | Tool discovery |
| `vault_ledger` | ❌ | ✅ | 999_VAULT (sovereign only) |
| `engineering_memory` | ❌ | ✅ | 555_MEMORY (sovereign only) |
| `code_engine` | ❌ | ✅ | Code execution (sovereign only) |

## Deploy to Horizon

1. Push this repo to GitHub
2. Go to https://horizon.prefect.io
3. Connect this repository
4. Set entrypoint: `server.py:mcp`
5. Deploy

## Why Separate Repos?

| Aspect | arifOS (VPS) | arifOS-horizon (This) |
|--------|--------------|----------------------|
| **FastMCP Version** | 3.1.1 | 2.12.3 (Horizon's) |
| **Entry Point** | Complex server | Minimal adapter |
| **Dependencies** | Heavy (ML, DB) | Light (HTTP only) |
| **Tools** | 11 (full) | 8 (public-safe) |
| **VAULT999** | Local PostgreSQL | ❌ Not available |
| **Memory** | Redis + Qdrant | ❌ Not available |

## Connecting to Sovereign Kernel

This Horizon deployment can proxy to your VPS:

```python
# Set in Horizon dashboard
ARIFOS_VPS_URL=https://arifosmcp.arif-fazil.com
ARIFOS_VPS_API_KEY=your_key
```

Or clients can use both:
```python
# Public for simple queries
client = Client("https://arifos.fastmcp.app")

# Sovereign for sensitive operations
sovereign = Client("https://arifosmcp.arif-fazil.com")
```

---

**arifOS Trinity**: 🔥 VPS | ☁️ Horizon | 💻 Local

*Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]
