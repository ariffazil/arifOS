---
agent: arifOS + OpenClaw
workspace: /root/waw
motto: DITEMPA BUKAN DIBERI
authority: 888_JUDGE
---

# arifOS Agent Skills — Unified Stack

> **Constitutional AI Governance + Agent Runtime**
> 
> This document registers the atomic competencies available to AI agents
> operating within the arifOS ecosystem, including OpenClaw runtime.

---

## 🦞 OpenClaw Runtime (VPS)

### Core Configuration

```yaml
workspace: /root/waw
model: minimax/MiniMax-M2.7
fallbacks: NONE
embeddings: ollama/bge-m3
gateway: 127.0.0.1:18789
telegram: @AGI_ASI_bot
```

### Constitutional Commands

| Command | Floor | Purpose |
| :--- | :--- | :--- |
| `/seal` | F1, F3, F4, F7, F10 | Archive session to immutable package |
| `/new` | F1, F3, F7 | Start fresh session with auto-seal |
| `/status` | F4 | Show governance state |
| `/doctor` | F2 | Health diagnostic |
| `/memory` | F5 | Vector memory status |

### Seal Package Structure

```text
~/.openclaw/sealed/SEAL-YYYYMMDD-HHMMSS-xxxx/
├── transcript.jsonl   — Full conversation
├── manifest.json      — Constitutional metadata
├── audit.log          — Witness trail
└── seal.txt           — Human certificate
```

---

## 🤖 arifOS MCP Canonical Tools (v2)

### GOVERNANCE (Ψ Soul)

- `arifos_init` — Constitutional session ignition (000)
- `arifos_route` — Metabolic lane routing (444)
- `arifos_judge` — Sovereign verdict rendering (888)
- `arifos_vault` — Immutable Merkle-hashed recording (999)

### INTELLIGENCE (Δ Mind / Ω Heart)

- `arifos_mind` — First-principles reasoning & synthesis (333)
- `arifos_memory` — Governed recall & engineering context (555)
- `arifos_heart` — Safety, empathy, & consequence modeling (666)

### MACHINE (Δ Mind)

- `arifos_sense` — Reality grounding & physics sensing (111)
- `arifos_ops` — Capacity & thermodynamic estimation (777)
- `arifos_vps_monitor` — Hardened read-only telemetry (111)

### EXECUTION (Δ Mind)

- `arifos_forge` — Signed manifest bridge to A-FORGE (010)

---

## 🔗 Resource URIs

| URI | Content |
| :--- | :--- |
| `arifos://agents/skills` | This document |
| `arifos://status/vitals` | System health |
| `arifos://governance/floors` | F1-F13 thresholds |
| `arifos://contracts/tools` | Tool risk contracts |

---

## 🌐 Canonical Links

- **Human**: <https://arif-fazil.com>
- **Theory**: <https://arifos.arif-fazil.com>
- **Runtime**: <https://arifosmcp.arif-fazil.com>
- **Code**: <https://github.com/ariffazil/arifOS>

---

**DITEMPA BUKAN DIBERI — Forged, Not Given**
