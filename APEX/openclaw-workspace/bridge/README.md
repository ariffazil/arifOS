# openclaw-arifos-bridge

**Integration layer between OpenClaw gateway and arifOS constitutional kernel.**

## Boundary Rules

| Layer | Ownership | Contents |
|-------|-----------|----------|
| **OpenClaw** | Upstream | Gateway runtime, channel adapters, generic platform |
| **This Bridge** | You | Adapter glue, config, prompts, healthchecks |
| **arifOS** | You | Constitutional kernel, AAA MCP, 13 Floors, VAULT999 |

## Architecture

```
WhatsApp/Telegram/Discord → OpenClaw Gateway → Bridge Adapter → arifOS MCP
                                                    ↓
                                              apex_judge
                                              eureka_forge
                                              seal_vault
```

## Structure

```
├── src/
│   ├── tools/
│   │   └── arifos-judge-tool.ts      # Wraps arifOS apex_judge MCP
│   ├── adapters/
│   │   └── message-to-mcp.ts         # OpenClaw msg → MCP tool call
│   └── prompts/
│       └── agent-alignment.md        # OpenClaw-specific prompts
├── config/
│   ├── canon9-models.json            # Policy model selection
│   ├── DIRECTIVE.md                  # Human output contract
│   └── TELEGRAM_FORMAT.md            # Channel formatting
├── scripts/
│   ├── canon9-healthcheck.ts         # Deployment validation
│   └── workspace-sync.sh             # OpenClaw workspace sync
├── state/
│   └── tri-witness/                  # Deployment audit logs
└── docs/
    └── INTEGRATION.md                # Operator guide
```

## MCP Boundary

This bridge **only** calls arifOS canonical tools:
- `anchor_session` (000)
- `reason_mind` (222)
- `recall_memory` (444)
- `simulate_heart` (555)
- `critique_thought` (666)
- `apex_judge` (888) ← Primary verdict tool
- `eureka_forge` (777)
- `seal_vault` (999)

**No constitutional logic here.** All governance happens in arifOS.

## Status

Scaffolded: 2026-02-27
Migration from: AGI_ASI_bot (89 commits decomposed)
