# arifOS Federation — Agent Architecture (2026-05-18)

## Overview

Two Telegram agents, one machine, different roles. No chaos — but needs cleanup.

---

## Active Agents

| | OpenClaw | Hermes |
|---|---|---|
| Telegram | `@AGI_ASI_bot` | `@ASI_arifos_bot` |
| Token | `8149595687:*` | `8410138119:*` |
| Protocol | Webhook | Polling |
| Port | 18789 (gateway), 8787 (webhook) | 18001 (A2A bridge) |
| Tier | AGI — sovereign operator | ASI — life relay |
| Trigger | @mention only | ALL messages in AAA group |
| Workspace | `/root/.openclaw/workspace/` | `/root/HERMES/` |

---

## Process Map

```
hermes-a2a.py (18001)         — ✅ RUNNING
  └── Polls @ASI_arifos_bot
  └── Forwards to AAA (3001) → OpenClaw sidecar (18790)

openclaw-agent-card.py (18795) — ✅ RUNNING
  └── Serves agent card for OpenClaw

openclaw-a2a.py (18002)       — ❌ DISABLED (dead, not running)
openclaw (Node.js) (18789)    — ✅ RUNNING
openclaw webhook (8787)       — ✅ RUNNING

apex-prime (3002)            — ✅ RUNNING (Docker container)
aaa-a2a (3001)               — ✅ RUNNING (Docker container)
```

---

## Data Flow

```
TELEGRAM @AGI_ASI_bot
  → Caddy (openclaw.arif-fazil.com/webhook/telegram)
  → OpenClaw webhook (127.0.0.1:8787/telegram-webhook)
  → OpenClaw gateway (127.0.0.1:18789)
  → MiniMax/LLM inference
  → Telegram reply

TELEGRAM @ASI_arifos_bot
  → hermes-a2a.py (127.0.0.1:18001, polling)
  → AAA gateway (127.0.0.1:3001)
  → OpenClaw sidecar (127.0.0.1:18790) for inference
  → Telegram reply via Hermes HTTP API (3002)
```

**Key insight**: Hermes is NOT independently doing inference. It routes through AAA → OpenClaw sidecar (18790). OpenClaw is the actual inference engine for both.

---

## A2A Agent Cards

| Agent | URL | Status |
|---|---|---|
| OpenClaw | http://127.0.0.1:18795/.well-known/agent-card.json | ✅ Serving |
| Hermes | http://127.0.0.1:18001/.well-known/agent-card.json | ✅ Serving |
| openclaw-a2a | http://127.0.0.1:18002/.well-known/agent-card.json | ❌ Disabled |

---

## Agent Identity Anchors

| | OpenClaw | Hermes |
|---|---|---|
| Workspace ID file | `/root/.openclaw/workspace/IDENTITY.md` | `/root/HERMES/SOUL.md` |
| Identity name | `arifOS_bot` / `OPENCLAW` | `Hermes Agent` |
| Sibling reference | `Hermes — ASI-level` | `OPENCLAW — AGI-level` |
| Telegram handle | `@AGI_ASI_bot` | `@ASI_arifos_bot` |
| Mandatory output template | Not enforced | Telegram reply template in SOUL.md |
| Agent card URL | https://openclaw.arif-fazil.com/.well-known/agent-card.json | http://127.0.0.1:18001/.well-known/agent-card.json |

---

## Issues Fixed (2026-05-18)

1. **openclaw-a2a.py (port 18002)** — disabled, was not running, dead code
2. **gateway-relay.py** — disabled, superseded by hermes-a2a.py

---

## Issues Remaining

1. **Hermes identity confusion** — Hermes sometimes calls itself "OpenClaw" or vice versa. Root cause: workspace bootstrap loads sibling SOUL.md content, model can conflate.
2. **No mandatory identity header in output** — neither agent is forced to state "I am Hermes" before replies. The A2A agent cards exist but aren't referenced at inference time.
3. **Agent card template not enforced** — A2A spec says agent cards exist, but there's no requirement for the model to read its own card before replying.

---

## What A2A Agent Cards Actually Solve

The A2A Agent Card is a **discovery + capability** document, not a runtime identity anchor. It helps:
- Other agents discover capabilities (e.g., "which agent handles research?")
- External callers know which endpoint to hit
- Protocol compliance (A2A spec requires `.well-known/agent-card.json`)

It does NOT solve the "I am Hermes but said I was OpenClaw" problem at runtime.

**What actually solves identity confusion:**

1. **Hard identity anchors in system prompt** — each agent's SOUL.md should be forced-read at boot, with explicit "you are NOT [sibling]" rules
2. **Output template with agent signature** — Hermes already has this in SOUL.md but it's not enforced at the model level
3. **Never cross-pollinate SOUL content** — sibling identity info should not be in the primary SOUL of the other agent

---

## Recommended Fixes

### Fix 1: Strengthen OpenClaw SOUL.md identity section

Add explicit "you are NOT Hermes" boundary to OpenClaw's SOUL.md.

### Fix 2: Add agent signature to OpenClaw output template

OpenClaw doesn't have a mandatory Telegram output template. Add one similar to Hermes.

### Fix 3: Each agent reads its own agent card on boot

Add to both agents' boot sequence:
```
Read: http://127.0.0.1:18795/.well-known/agent-card.json  (OpenClaw)
Read: http://127.0.0.1:18001/.well-known/agent-card.json  (Hermes)
```

This establishes "I am the agent at port X" as a firstprinciple fact, not inference.

---

## TREE777 Compliance

- OpenClaw token: `8149595687:*` — ✅
- Hermes token: `8410138119:*` — ✅
- Different bots, different tokens, no collision — ✅ PASS