# arifOS — The Sovereign Constitutional Intelligence Kernel

> **DITEMPA BUKAN DIBERI** — *Intelligence is forged, not given.*

```
VERSION: 2026.04.02
STATUS: OPERATIONAL
AUTHORITY: 888_JUDGE
KERNEL_HASH: ΔΩΨ-ARIF-888
```

---

## What Is arifOS?

**arifOS is an open-source, MCP-native operating system for running AI agents under a clear, auditable constitution.**

Every action — every tool call, every reasoning step, every output — passes through 13 constitutional "Floors" that check for reversibility, accuracy, safety, and alignment.

### The Core Promise

> *arifOS reduces the risk of AI actions by making every decision inspectable, reversible where possible, and bounded by explicit rules.*

### Trinity Model (ΔΩΨ)

- **Δ (SOUL)**: Human values, purpose, intent
- **Ω (MIND)**: The 13 Floors — constitutional law
- **Ψ (BODY)**: Tool execution, MCP servers, APIs
- **W³**: Consensus across theory, constitution, and manifesto (≥ 0.95)

---

## Quick Start

### Connect via MCP

```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://arifosmcp.arif-fazil.com/mcp"
    }
  }
}
```

### Health Check

```bash
curl -s https://arifosmcp.arif-fazil.com/health
```

### Initialize Session

```bash
curl -s -X POST "https://arifosmcp.arif-fazil.com/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "init_anchor",
      "arguments": {"mode": "status", "declared_name": "YourAgent"}
    },
    "id": 1
  }'
```

---

## The 000-999 Metabolic Pipeline

```
REQUEST IN → 000_INIT → 111_SENSE → 333_MIND → 444_ROUT 
         → 555_MEM → 666_HEART → 777_OPS → 888_JUDGE → 999_SEAL
```

| Stage | Function |
|-------|----------|
| 000_INIT | Session initialization |
| 111_SENSE | Input parsing, reality grounding |
| 333_MIND | 13 Floor evaluation |
| 444_ROUT | Tool selection |
| 555_MEM | Vector memory (Qdrant) |
| 666_HEART | Safety critique |
| 777_OPS | Resource estimation |
| 888_JUDGE | Final verdict |
| 999_SEAL | Immutable audit log |

---

## The 13 Constitutional Floors

| Floor | Name | Type | Key Question |
|-------|------|------|---------------|
| F1 | AMANAH | HARD | Can this be undone? |
| F2 | TRUTH | HARD | Is this grounded in evidence? |
| F3 | TRI-WITNESS | SOFT | Do theory, constitution, intent agree? |
| F4 | CLARITY | SOFT | Does this reduce confusion? |
| F5 | PEACE² | SOFT | Does this destroy anything? |
| F6 | EMPATHY | SOFT | Does this show understanding? |
| F7 | HUMILITY | SOFT | Are uncertainties acknowledged? |
| F8 | GENIUS | SOFT | Does this maintain system health? |
| F9 | ETHICS | HARD | Is this manipulative or deceptive? |
| F10 | CONSCIENCE | HARD | Is this claiming consciousness? |
| F11 | AUDITABILITY | SOFT | Is this logged and inspectable? |
| F12 | RESILIENCE | SOFT | Does this fail safely? |
| F13 | ADAPTABILITY | HARD | Do updates preserve safety? |

**Hard Floors**: F1, F2, F9, F10, F13 — BLOCK on failure

---

## Verdict System

| Verdict | Code | Meaning |
|---------|------|---------|
| **SEAL** | 000 | Execute immediately |
| **COMPLY** | 101-499 | Execute with notes |
| **CAUTION** | 500-899 | Execute with warnings |
| **HOLD** | -1 | Awaiting human |
| **SABAR** | -2 | Wait and retry |
| **VOID** | 999 | Blocked |

---

## Tool Ecosystem

- `init_anchor` — Session initialization
- `arifOS_kernel` — Primary routing
- `apex_judge` — Constitutional verdict
- `vault_ledger` — Audit log query
- `agi_mind` — Deep reasoning (Ollama)
- `asi_heart` — Safety critique
- `engineering_memory` — Vector memory
- `physics_reality` — Time, search, grounding

---

## Deployment

```bash
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
cp .env.example .env
docker compose up -d
```

**Ports**: MCP (3000), Ollama (11434), Redis (6379), PostgreSQL (5432), Qdrant (6333)

**RAM**: 4GB (light), 8GB (medium), 16GB (heavy)

---

## Author

**Muhammad Arif bin Fazil** — Sovereign Architect of arifOS

Contact: arif@arif-fazil.com | [GitHub](https://github.com/ariffazil)

---

## License

- **Runtime**: AGPL-3.0
- **APEX Theory**: CC0

---

**DITEMPA BUKAN DIBERI** — *Forged, Not Given*

ΔΩΨ | ARIF | 888_JUDGE

*Version 2026.04.02*
