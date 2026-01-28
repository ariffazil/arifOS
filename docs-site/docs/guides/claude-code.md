---
sidebar_position: 3
title: Claude Code
description: Configure Claude Code CLI with arifOS governance
---

# Claude Code Setup

Configure Claude Code (the CLI tool) with arifOS constitutional governance.

## Overview

Claude Code is Anthropic's official CLI for Claude. It can connect to MCP servers for extended capabilities, including arifOS governance.

## Configuration

### Global Configuration

Create or edit `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://arifos.arif-fazil.com/mcp"
    }
  }
}
```

### Project-Level Configuration

For project-specific governance, create `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://arifos.arif-fazil.com/mcp"
    }
  }
}
```

## Using CLAUDE.md

For deeper integration, add governance instructions to your `CLAUDE.md` file:

```markdown
# CLAUDE.md

## Governance

This project uses arifOS constitutional governance. Before any action:

1. Check against TEACH principles (Truth, Empathy, Amanah, Clarity, Humility)
2. Use 888_HOLD for:
   - Database migrations
   - Production deployments
   - Credential handling
   - Mass file operations (>10 files)
   - Git history modification

## SABAR Protocol

If a floor fails:
1. STOP — Don't execute
2. ACKNOWLEDGE — State which floor failed
3. BREATHE — Pause
4. ADJUST — Propose alternative
5. RESUME — Only when all floors pass
```

## Verifying Integration

Start Claude Code and check for arifOS tools:

```bash
claude

# In the Claude Code session:
> What MCP tools are available?
```

You should see:
- `init_000` — System ignition
- `agi_genius` — Mind (truth, clarity)
- `asi_act` — Heart (empathy, safety)
- `apex_judge` — Soul (verdict)
- `vault_999` — Seal (ledger)
- `trinity_loop` — Full pipeline in one call

## Usage Patterns

### Automatic Governance

Claude Code will use arifOS tools when:
- You ask it to verify facts
- You request code changes affecting data
- You ask about high-stakes operations

### Manual Invocation

You can explicitly request governance:

```
> Use arifOS to verify this claim before proceeding: "React 18 uses a new reconciler algorithm"
```

### High-Stakes Operations

For operations that trigger 888_HOLD:

```
> I want to run a database migration

Claude will:
1. Call init_000 (detect: high-stakes operation)
2. Return 888_HOLD verdict
3. Ask for explicit confirmation
4. Only proceed after human approval
```

## Local Server Mode

For offline or low-latency usage:

```json
{
  "mcpServers": {
    "arifOS": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

This starts a local stdio server that Claude Code manages automatically.

## Troubleshooting

### MCP Tools Not Available

1. Check settings file location
2. Validate JSON syntax
3. Restart Claude Code session

### Connection Timeouts

The HTTP connection may timeout on slow networks. Options:

1. **Use local server** (recommended for development)
2. **Increase timeout** in configuration
3. **Check firewall** settings

### Floor Violations

If you see VOID verdicts frequently, check the `floor_summary`:

```json
{
  "verdict": "VOID",
  "floor_summary": {
    "failed": ["F2"],
    "reason": "Unverified claim stated as fact"
  }
}
```

This is the system working correctly — adjust your request to pass the floor.

## Best Practices

1. **Don't disable governance** — It's there to help
2. **Use CLAUDE.md** — Project-specific rules enhance governance
3. **Trust 888_HOLD** — When it pauses, there's a reason
4. **Review VOIDs** — They indicate potential issues

## Next Steps

- [Cursor Setup](/guides/cursor) — VS Code-based IDE
- [Python Integration](/guides/python) — Direct API access
- [MCP Tools Reference](/mcp/overview) — Detailed tool documentation
