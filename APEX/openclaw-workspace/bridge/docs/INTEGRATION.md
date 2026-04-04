# OpenClaw + arifOS Integration Guide

## Overview

This bridge connects OpenClaw (gateway) to arifOS (constitutional kernel).

```
[User] → [OpenClaw Gateway] → [This Bridge] → [arifOS MCP]
                                    ↓
                              apex_judge
                              reason_mind
                              eureka_forge
                              seal_vault
```

## Setup

### 1. Prerequisites

- OpenClaw gateway running (port 3000)
- arifOS MCP server running (port 8088)
- Node.js 22+

### 2. Environment Variables

```bash
# Bridge configuration
ARIFOS_MCP_ENDPOINT=http://127.0.0.1:8088/mcp
OPENC LAW_GATEWAY_TOKEN=your-gateway-token

# Optional: Canon9 model selection
CANON9_MODEL_PRIMARY=qwen2.5:7b
CANON9_MODEL_FALLBACK=gpt-4
```

### 3. Install Bridge

```bash
cd openclaw-arifos-bridge
npm install
npm run build
```

### 4. Register with OpenClaw

Add to OpenClaw's extension config:

```json
{
  "extensions": [
    {
      "name": "arifos-governance",
      "path": "/path/to/openclaw-arifos-bridge/dist/index.js"
    }
  ]
}
```

## Tool Reference

### arifos_judge

Calls arifOS `apex_judge` for constitutional verdict.

**Input:**
```json
{
  "query": "User message here",
  "context": "Optional context",
  "session_id": "session-uuid"
}
```

**Output:**
```json
{
  "verdict": "SEAL|VOID|PARTIAL|SABAR|888_HOLD",
  "stage": "888",
  "reason": "Explanation",
  "confidence": 0.99
}
```

## Configuration

### canon9-models.json

Policy-driven model selection. Edit to change which LLM handles which query type.

### DIRECTIVE.md

Human-language output contract. Defines how responses should be formatted.

### TELEGRAM_FORMAT.md

Telegram-specific formatting rules.

## Health Checks

```bash
# Validate canon9 configuration
npm run healthcheck

# Check arifOS MCP connectivity
npm run check:arifos

# Full integration test
npm run test:integration
```

## Troubleshooting

### arifOS MCP not responding

```bash
curl http://127.0.0.1:8088/health
# Should return: {"status": "healthy", "tools_loaded": 13}
```

### OpenClaw gateway not responding

```bash
curl http://127.0.0.1:3000/health
# Should return gateway status
```

## Migration from AGI_ASI_bot

This bridge replaces the `AGI_ASI_bot` fork:

| Old (AGI_ASI_bot) | New (This Bridge) |
|-------------------|-------------------|
| `src/agents/tools/arifos-judge-tool.ts` | `src/tools/arifos-judge-tool.ts` |
| `canon9-models.json` | `config/canon9-models.json` |
| `scripts/canon9_healthcheck.ts` | `scripts/canon9_healthcheck.ts` |
| `DIRECTIVE.md` | `config/DIRECTIVE.md` |
| `TELEGRAM_FORMAT.md` | `config/TELEGRAM_FORMAT.md` |

All constitutional logic (13 Floors, ΔΩΨ, VAULT999) remains in arifOS.
