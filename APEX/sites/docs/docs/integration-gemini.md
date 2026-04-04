---
id: integration-gemini
title: Gemini CLI
sidebar_position: 2
description: Connect arifOS to Google Gemini CLI for terminal-based constitutional governance
---

# Gemini CLI Integration

Connect **arifOS** to [Gemini CLI](https://geminicli.com/) for terminal-based constitutional AI governance.

---

## Overview

Gemini CLI supports MCP servers through **STDIO transport**, allowing you to extend Gemini's capabilities with arifOS's 13 Constitutional Floors directly from your terminal.

:::tip Requirements
- **Gemini CLI** installed: `npm install -g @google/gemini-cli`
- **Python 3.12+** with `pip`
- **arifOS** package: `pip install arifos`
:::

---

## Quick Install

### Option 1: FastMCP CLI (Recommended)

If you have `fastmcp` installed globally:

```bash
fastmcp install gemini-cli arifos
```

### Option 2: Manual Configuration

Use Gemini CLI's built-in MCP management:

```bash
# Add arifOS server
gemini mcp add arifOS python -- -m arifos_aaa_mcp stdio

# Add with environment variables
gemini mcp add arifOS -e ARIFOS_GOVERNANCE_SECRET=your-secret \
  -e JINA_API_KEY=your-jina-key \
  python -- -m arifos_aaa_mcp stdio
```

### Option 3: With uv (Dependency Management)

For better dependency isolation:

```bash
gemini mcp add arifOS uv -- run --with arifos python -m arifos_aaa_mcp stdio
```

---

## Configuration with Environment Variables

Create a `.env` file:

```bash
# Required
ARIFOS_GOVERNANCE_SECRET=$(openssl rand -hex 32)

# Optional - Search API keys (recommended)
JINA_API_KEY=jina_...           # https://jina.ai (10M free tokens)
PERPLEXITY_API_KEY=pplx_...     # https://perplexity.ai
BRAVE_API_KEY=BSA...            # https://brave.com/search/api

# Optional - Enable ML floors for empathy scoring
ARIFOS_ML_FLOORS=1
```

Then install with env file:

```bash
gemini mcp add arifOS --env-file .env uv -- run --with arifos python -m arifos_aaa_mcp stdio
```

---

## Verify Installation

1. Check configured servers:
```bash
gemini mcp list
```

2. You should see:
```
arifOS
  Command: uv run --with arifos python -m arifos_aaa_mcp stdio
  Status: enabled
```

3. Start a Gemini session:
```bash
gemini
```

4. Ask Gemini to use arifOS tools:
> "Use arifOS to search for constitutional AI governance papers"

---

## Usage Examples

### Terminal-Based Constitutional Research

```bash
$ gemini

You: Search for the latest MCP protocol updates using arifOS

Gemini: I'll use arifOS to search for MCP protocol updates with constitutional
verification...

[Tool Call: search_reality]
Query: "MCP protocol updates 2025 Model Context Protocol"
Intent: research
Status: OK
Results: 5 papers found

F2 Truth Score: 0.97 (≥0.99 threshold not met - sources verified but 
confidence moderate)
F4 Clarity: Content reduces entropy
Verdict: SEAL with uncertainty marker

Here are the verified results...
```

### Risk-Classified File Operations

```bash
You: Use arifOS to inspect my project structure

Gemini: [Tool Call: inspect_file]
Path: ./my-project
Risk: LOW (read-only inspection)
Executing...

Found 47 files:
- README.md
- src/
  - main.py
  - utils.py
...
```

### Dangerous Operations Require Confirmation

```bash
You: Delete all log files in /var/log

Gemini: [Tool Call: eureka_forge]
Command: rm -rf /var/log/*
Risk: CRITICAL (destructive operation)

⚠️  888_HOLD TRIGGERED

This operation requires explicit human confirmation.
Confidence: 0.15 (low — destructive pattern detected)

Do you want to proceed? This action:
- Is IRREVERSIBLE
- Deletes system log files
- May impact debugging

Say "confirm destructive operation" to proceed, or cancel.
```

---

## Advanced Configuration

### Project-Specific Setup

For a specific project directory:

```bash
cd /path/to/my-project

# Install with project context
gemini mcp add arifOS --scope project \
  uv -- run --project . --with arifos \
  python -m arifos_aaa_mcp stdio
```

### With Additional Dependencies

```bash
# Add sentence-transformers for ML empathy scoring
gemini mcp add arifOS \
  uv -- run --with arifos --with sentence-transformers \
  python -m arifos_aaa_mcp stdio
```

### Python Version Control

```bash
# Use specific Python version
gemini mcp add arifOS \
  uv -- run --python 3.12 --with arifos \
  python -m arifos_aaa_mcp stdio
```

---

## Constitutional Guarantees

Every Gemini CLI session with arifOS enforces:

| Stage | Governance |
|-------|------------|
| **000 INIT** | `anchor_session` validates security clearance |
| **111-333 REASON** | `reason_mind` with F2 Truth grounding |
| **444 MEMORY** | `recall_memory` retrieves past context |
| **555-666 HEART** | `simulate_heart` checks stakeholder impact |
| **777 FORGE** | `eureka_forge` with risk classification |
| **888 JUDGE** | `apex_judge` issues final verdict |
| **999 SEAL** | `seal_vault` commits to immutable ledger |

---

## Troubleshooting

### "Command not found: gemini"

Install Gemini CLI:
```bash
npm install -g @google/gemini-cli
```

### "Server failed to start"

1. Check Python is in PATH:
```bash
which python
python --version  # Should be 3.12+
```

2. Verify arifOS installation:
```bash
pip show arifos
```

3. Try direct execution:
```bash
python -m arifos_aaa_mcp stdio
```

### Search returns "NO_API_KEY"

Add search provider keys:
```bash
gemini mcp remove arifOS

gemini mcp add arifOS \
  -e JINA_API_KEY=jina_... \
  -e PERPLEXITY_API_KEY=pplx_... \
  python -- -m arifos_aaa_mcp stdio
```

### Governance token errors

`ARIFOS_GOVERNANCE_SECRET` is required for `seal_vault` operations:

```bash
export ARIFOS_GOVERNANCE_SECRET=$(openssl rand -hex 32)
gemini mcp add arifOS -e ARIFOS_GOVERNANCE_SECRET=$ARIFOS_GOVERNANCE_SECRET \
  python -- -m arifos_aaa_mcp stdio
```

---

## Managing the Server

```bash
# List all MCP servers
gemini mcp list

# Disable arifOS temporarily
gemini mcp disable arifOS

# Re-enable
gemini mcp enable arifOS

# Remove completely
gemini mcp remove arifOS

# Update configuration
gemini mcp update arifOS --env KEY=value
```

---

## Best Practices

1. **Use a .env file** for API keys instead of inline
2. **Scope servers per project** for isolation
3. **Enable ARIFOS_ML_FLOORS=1** for better empathy scoring
4. **Set JINA_API_KEY** for superior search quality
5. **Never commit secrets** — add `.env` to `.gitignore`

---

## Next Steps

- [MCP Server Overview](/mcp-server) — Learn the 13 tools
- [Claude Desktop Integration](/integration-claude) — Desktop alternative
- [ChatGPT Integration](/integration-chatgpt) — Cloud-based option
- [Governance](/governance) — Constitutional Floors reference

---

*Ditempa Bukan Diberi — Forged, Not Given*
