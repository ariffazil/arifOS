# arifOS Skills

> DITEMPA BUKAN DIBERI — Forged, Not Given.

This directory contains arifOS-specific agent skills that teach AI coding assistants (Cursor, Claude Code, OpenClaw, etc.) how to work with the arifOS constitutional AI kernel and its federation components.

## Available Skills

| Skill | Description | Status |
|-------|-------------|--------|
| `langfuse-arifos/` | Instrument arifOS tool calls with Langfuse v3 tracing | ✅ active |
| `langfuse/` (upstream) | [Langfuse official skill](https://github.com/langfuse/skills) — use for Langfuse docs and CLI | upstream |

## Installation

### Clone into your agent's skills directory

```bash
# Clone this repo
git clone https://github.com/ariffazil/arifOS.git /path/to/arifOS-workspace

# Symlink the skill into your agent's skills directory
ln -s /path/to/arifOS-workspace/arifOS/skills/langfuse-arifos \
   /path/to/your-agent/skills/langfuse-arifos
```

### Or use the skills CLI

```bash
npx skills add langfuse/skills --skill "langfuse"
```

## Quick Start

Once installed, AI agents can:

1. **Instrument arifOS tool calls** with Langfuse v3 spans
2. **Query Langfuse traces** via CLI/API for arifOS operations
3. **Add new tools to tracing** using the instrumentation reference
4. **Verify tracing wiring** by checking the Langfuse dashboard

## Federation Skills Map

```
arifOS (governance kernel)
├── tools.py          → arifOS tool handlers
├── telemetry.py     → Langfuse + Prometheus instrumentation
├── vault999        → immutable ledger
├── 000–999 pipeline → constitutional tool chain
│
├── A-FORGE          → execution bridge (TypeScript)
├── GEOX             → earth intelligence (Python)
├── WEALTH           → capital intelligence (Python)
└── skills/
    └── langfuse-arifos/  ← THIS — arifOS-specific Langfuse wiring
```

## Key Files

```
skills/langfuse-arifos/
├── SKILL.md         ← main skill entry point
└── references/
    └── instrumentation.md  ← how to wire new tools to Langfuse
```

## Environment Variables

```bash
# arifOS → Langfuse (cloud Japan region)
LANGFUSE_PUBLIC_KEY=pk-lf-YOUR_PUBLIC_KEY
LANGFUSE_SECRET_KEY=sk-lf-YOUR_SECRET_KEY
LANGFUSE_HOST=https://jp.cloud.langfuse.com

# arifOS → self-hosted Langfuse (internal Docker network)
# LANGFUSE_HOST=http://langfuse-web:3000
```

## Documentation

- **arifOS Observatory**: https://arifos.arif-fazil.com/observatory/
- **Langfuse Docs**: https://langfuse.com/docs
- **arifOS GitHub**: https://github.com/ariffazil/arifOS
