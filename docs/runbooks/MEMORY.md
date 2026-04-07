# MEMORY.md

## Full Agent Loop (Permanent)

All agents must follow: REASON → PLAN → ACT → OBSERVE → REFLECT → REPEAT → MEMORY → PERSIST

## Platform Rules
- **NEVER modify openclaw.json directly** — always use `gateway` tool:
  - `config.get` — read config (returns { raw: JSON5, hash: SHA256 })
  - `config.patch` — deep-merge partial update

## Current Session
- **Telegram Bot**: Plugin enabled, awaiting bot token
- **VPS Access**: `srv1325122.hstgr.cloud` / `vps.arif-fazil.com`
- **APEX-CONTRAST Protocol**: Created at `/workspace/skills/APEX-CONTRAST-PROTOCOL.md`

## Pending Tasks
- **Supabase** — still pending (network issue from sandbox)
- **Telegram groups** — blocked, needs configuration (streaming, dmPolicy, groupPolicy)
- **VPS deployment** — arifOS deploy.skill needs cleanup, heartbeat stale

## AGI_META_INIT_SEAL Architecture
| Component | Function |
|-----------|----------|
| **SELF-KNOWLEDGE** | Defines AGI_bot identity (creator, model, tools, roles) |
| **000_INIT** | Session anchoring — loads constitutional context (Ω₀=0.04, 13 floors) |
| **999_SEAL** | Audit log — reads previous seal for self-improvement loop |

### 13 Constitutional Floors (F1-F13)
- F1: AMANAH — Reversibility
- F2: TRUTH — Evidence required
- F3: TRI_WITNESS — W³ ≥ 0.95
- F4: CLARITY — Entropy ↓

### Architecture Flow
```
User message → OpenClaw Gateway → arifOS MCP Server → apex_judge + tools
```