---
sidebar_position: 4
title: Cursor
description: Add arifOS governance to Cursor IDE
---

# Cursor Setup

Add arifOS constitutional governance to Cursor, the AI-first code editor.

## Prerequisites

- [Cursor](https://cursor.sh/) installed
- Cursor version 0.40+ (MCP support required)

## Configuration

### Step 1: Open MCP Settings

In Cursor:
1. Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Search for "MCP: Open Settings"
3. Or navigate to **Settings** → **MCP Servers**

### Step 2: Add arifOS Server

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://arifos.arif-fazil.com/mcp"
    }
  }
}
```

### Step 3: Reload Cursor

Reload the window or restart Cursor to apply changes.

## Verify Installation

1. Open a new chat with Cursor AI
2. Ask: "What MCP tools are available?"
3. You should see arifOS tools listed:
   - `init_000`
   - `agi_genius`
   - `asi_act`
   - `apex_judge`
   - `vault_999`
   - `trinity_loop`

## Using arifOS in Cursor

### Code Review with Governance

```
Review this function and verify your suggestions with arifOS before applying:

function processPayment(amount) {
  // ... code here
}
```

Cursor will:
1. Analyze the code
2. Use `agi_genius` to verify suggestions
3. Use `asi_act` to check for harmful changes
4. Only suggest changes that pass governance

### Fact-Checking Documentation

```
Verify this JSDoc comment is accurate:

/**
 * Sorts array in O(n) time using radix sort
 * @param {number[]} arr - Input array
 */
```

arifOS will check the O(n) claim against F2 (Truth).

### Safe Refactoring

```
Refactor this module, but use 888_HOLD for any changes affecting the database layer.
```

arifOS will pause and ask for confirmation before database-affecting changes.

## Local Server for Development

For faster response times during development:

```json
{
  "mcpServers": {
    "arifOS": {
      "command": "python",
      "args": ["-m", "codebase.mcp"]
    }
  }
}
```

Requires `pip install arifos` first.

## Project-Level Rules

Create `.cursorrules` with governance instructions:

```markdown
# Cursor Rules

## arifOS Integration

- Use arifOS tools for all code modifications
- 888_HOLD required for:
  - Changes to authentication code
  - Database schema modifications
  - API endpoint changes
  - Package version upgrades

## Floor Priorities

- F2 (Truth): All comments must be verifiable
- F6 (Empathy): Consider junior developers reading this code
- F4 (Clarity): Code should be clearer after changes
```

## Troubleshooting

### Tools Not Appearing

1. Check MCP settings JSON syntax
2. Ensure Cursor version supports MCP
3. Reload window (`Cmd+Shift+R` / `Ctrl+Shift+R`)

### Slow Responses

The cloud server adds ~50ms latency. For faster development:
1. Use local server mode
2. Or run arifOS on your local network

### Governance Too Strict

If you're getting too many VOIDs:
1. Check which floor is failing
2. Adjust your prompts to satisfy the floor
3. Or explicitly ask to override (will be logged)

## Best Practices

1. **Keep governance enabled** — It catches real issues
2. **Use project rules** — Customize for your codebase
3. **Trust 888_HOLD** — High-stakes operations need confirmation
4. **Review audit trail** — Check `/health` for governance logs

## Next Steps

- [Python Integration](/guides/python) — Direct API access
- [MCP Examples](/mcp/examples) — Request/response patterns
- [Floor Reference](/floors/reference) — Understanding verdicts
