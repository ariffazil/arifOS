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
|---------|-------|---------|
| `/seal` | F1, F3, F4, F7, F10 | Archive session to immutable package |
| `/new` | F1, F3, F7 | Start fresh session with auto-seal |
| `/status` | F4 | Show governance state |
| `/doctor` | F2 | Health diagnostic |
| `/memory` | F5 | Vector memory status |

### Seal Package Structure
```
~/.openclaw/sealed/SEAL-YYYYMMDD-HHMMSS-xxxx/
├── transcript.jsonl   — Full conversation
├── manifest.json      — Constitutional metadata
├── audit.log          — Witness trail
└── seal.txt           — Human certificate
```

---

## 🤖 arifOS MCP Mega-Tools

### 111 SENSE — Fact Acquisition
- `search_reality` — Evidence-grounded search
- `physics_reality` — Earth-witness fact mapping

### 333 MIND — Reasoning
- `agi_mind` — First-principles reasoning
- `agi_reflect` — Self-critique and synthesis

### 444 ROUTER — Orchestration
- `arifOS_kernel` — Metabolic loop routing

### 555 MEMORY — Engineering
- `agentzero_engineer` — Governed code execution
- `engineering_memory` — Vector memory operations

### 666 HEART — Safety
- `asi_heart` — Empathy and consequence modeling
- `asi_critique` — Safety critique

### 888 JUDGE — Verdict
- `init_anchor` — Constitutional session ignition
- `apex_judge` — Final verdict rendering
- `vault_ledger` — Permanent decision recording

---

## 🔗 Resource URIs

| URI | Content |
|-----|---------|
| `arifos://agents/skills` | This document |
| `arifos://status/vitals` | System health |
| `arifos://governance/floors` | F1-F13 thresholds |
| `arifos://contracts/tools` | Tool risk contracts |

---

## 🌐 Canonical Links

- **Human**: https://arif-fazil.com
- **Theory**: https://arifos.arif-fazil.com
- **Runtime**: https://arifosmcp.arif-fazil.com
- **Code**: https://github.com/ariffazil/arifOS

---

**DITEMPA BUKAN DIBERI — Forged, Not Given**
