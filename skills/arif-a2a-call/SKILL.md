---
name: arif-a2a-call
description: A2A v1.0.0 client + 888 JUDGMENT integration for OPENCLAW. Use when candidate actions require ASI deliberation or A2A federation with APEX (formerly Hermes).
version: 2026.05.01
tags: [a2a, federation, judgment, apex, 888]
---

# arif-a2a-call — A2A Client for OPENCLAW

Use this skill when OPENCLAW needs 888 JUDGMENT or A2A federation with APEX (port 3002).

## Architecture

```
OPENCLAW
  ├── MCP ──── arifOS MCP ──── arif_judge_deliberate (888 JUDGMENT)
  └── A2A ──── APEX (direct) ──── 888 JUDGMENT (fallback/deliberation)
```

## Two-Step Judgment Path

### Step 1: Primary 888 — arifOS MCP (arif_judge_deliberate)

Use the arifOS MCP tool `arif_judge_deliberate` for constitutional judgment:

```
Tool: arif_judge_deliberate
  mode: judge
  candidate: <action text>
  session_id: <current session>
  actor_id: openclaw
```

Returns: SEAL / HOLD / VOID with floor compliance proof.

### Step 2: A2A Fallback — APEX (direct A2A)

If arifOS MCP is unavailable, route to APEX via A2A:

```bash
# Direct to APEX (port 3002)
curl -X POST http://localhost:3002/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer apex-prime-token-dev" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tasks/send",
    "params": {
      "message": {
        "parts": [{"kind": "text", "text": "<candidate_action>"}]
      }
    }
  }'
```

## Verdict Response Mapping

| Verdict | Meaning | OPENCLAW Action |
|---------|---------|-----------------|
| `SEAL` | Approved — all F1-F13 satisfied | Execute freely |
| `HOLD_888` | Paused — needs human confirmation | Pause, ask Arif |
| `VOID` | Forbidden — constitutional violation | Do not execute, announce |
| `pending-human-review` | AAA 888_JUDGE gate triggered | Wait for Arif verdict |

## A2A Endpoints

| Service | URL | Auth |
|---------|-----|------|
| APEX (direct) | `http://localhost:3002` | Bearer: `apex-prime-token-dev` |
| AAA Gateway | `http://localhost:3001` | Bearer: `aaa-a2a-token-dev` |

## Test Commands

```bash
# Test APEX directly
curl -X POST http://localhost:3002/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer hermes-agent-token-dev" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tasks/send","params":{"message":{"parts":[{"kind":"text","text":"write checkpoint after session seal"}]}}}'

# Test AAA Gateway
curl -X POST http://localhost:3001/a2a/message/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer aaa-a2a-token-dev" \
  -H "x-a2a-key: aaa-a2a-apikey-dev" \
  -d '{"jsonrpc":"2.0","id":1,"method":"message/send","params":{"skill":"status-query","message":{"parts":[{"kind":"text","text":"federation status"}]}}}'

# Check federation charter
curl http://localhost:3001/.well-known/arifos-federation.json
```

## When to Route to APEX via A2A

- arifOS MCP unavailable (network/timeout)
- Complex multi-agent deliberation required
- AAA gateway shows degraded health
- Explicit ASI deliberation requested by Arif

## Quick Reference

| Action | Endpoint | Method |
|--------|----------|--------|
| Send task to APEX | `/tasks` | POST |
| Get task status | `/tasks/{id}` | GET |
| Stream task | `/tasks/{id}/stream` | GET |
| Cancel task | `/tasks/{id}/cancel` | POST |
| Agent card | `/.well-known/agent-card.json` | GET |

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
