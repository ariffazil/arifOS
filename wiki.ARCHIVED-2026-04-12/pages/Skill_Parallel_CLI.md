---
type: Tool
tier: 20_RUNTIME
strand:
- tools
- research
- web
audience:
- researchers
- operators
- analysts
difficulty: intermediate
prerequisites:
- MCP_Tools
- Skill_MCP_Mcporter
tags:
- parallel
- parallel-cli
- deep-research
- web-search
- enrichment
- entity-discovery
- monitoring
- research
sources:
- Hermes official skill: official/research/parallel-cli
- Parallel docs: https://parallel.ai
last_sync: '2026-05-18'
confidence: 0.95
---

# Skill: Parallel CLI — Deep Research

**Parallel CLI** is the vendor-native research stack for deep web search, content extraction, enrichment, entity discovery (FindAll), and change monitoring. Designed for agents with JSON output, non-interactive flows, and async long-running jobs.

## Purpose

To give federation agents capabilities that Hermes native tools do not cover:
- **Deep research**: Multi-step async research with processor tiers (lite → ultra)
- **Enrichment**: Auto-add columns to CSV/JSON from web research
- **FindAll**: Web-scale entity discovery (e.g. "find all AI coding agent startups with enterprise offerings")
- **Monitoring**: Recurring change detection over pages or sources

## Specifications

- **Stage**: 111 (Sensing) + 222 (Fetch)
- **Layer**: WEB
- **Trinity**: Δ (Mind — deep research and synthesis)
- **Floors touched most directly**: F2 (Truth — citations from returned sources only), F4 (Guardrails — paid service quotas), F8 (Audit — all research jobs logged)

## Installation

```bash
# Standalone installer
curl -fsSL https://parallel.ai/install.sh | bash

# Or via pip
pip install "parallel-web-tools[cli]"

# Or via npm
npm install -g parallel-web-cli

# Or via Homebrew
brew install parallel-web/tap/parallel-cli
```

**Installed on**: `/root` (VPS host)  
**Binary**: `/root/.local/bin/parallel-cli`  
**Version**: 0.3.0  
**Auto-update**: Enabled

## Authentication

```bash
# Interactive (browser)
parallel-cli login

# Headless / SSH / container (device code flow)
parallel-cli login --device
# → Visit the URL and enter the user_code

# API key (CI/CD, agents)
export PARALLEL_API_KEY="your-key"
parallel-cli auth
```

**Auth status**: Pending device login for `parallel-cli` on this host.

## Core Capabilities

### 1. Search
```bash
# Structured web search
parallel-cli search "What is Anthropic's latest AI model?" --json
parallel-cli search "SEC filings for Apple" --include-domains sec.gov --json
parallel-cli search "bitcoin price" --after-date 2026-01-01 --max-results 10 --json

# One-shot vs agentic modes
parallel-cli search "latest browser benchmarks" --mode one-shot --json
parallel-cli search "AI coding agent enterprise reviews" --mode agentic --json
```

### 2. Extraction
```bash
# Pull clean content from URL
parallel-cli extract https://example.com --json
parallel-cli extract https://company.com --objective "Find pricing info" --json
parallel-cli extract https://example.com --full-content --json
parallel-cli fetch https://example.com --json
```

### 3. Deep Research (async)
```bash
# Synchronous
parallel-cli research run \
  "Compare leading AI coding agents by pricing, model support, and enterprise controls" \
  --processor core --json

# Async launch + poll
parallel-cli research run \
  "Compare leading AI coding agents" \
  --processor ultra --no-wait --json

parallel-cli research status trun_xxx --json
parallel-cli research poll trun_xxx --json
```

**Processor tiers:**
| Tier | Speed | Depth |
| :--- | :--- | :--- |
| lite | Fast | Shallow |
| base | Balanced | Moderate |
| core | Slower | Thorough |
| pro | Slow | Deep |
| ultra | Slowest | Maximum synthesis |

### 4. Enrichment
```bash
# Suggest columns
parallel-cli enrich suggest "Find CEO and annual revenue" --json

# Inline data
parallel-cli enrich run \
  --data '[{"company": "Anthropic"}, {"company": "Mistral"}]' \
  --intent "Find headquarters and employee count" \
  --json

# File-based
parallel-cli enrich run \
  --source-type csv --source companies.csv \
  --target enriched.csv \
  --source-columns '[{"name": "company", "description": "Company name"}]' \
  --intent "Find the CEO and annual revenue"
```

### 5. FindAll (Entity Discovery)
```bash
# Web-scale entity discovery
parallel-cli findall run "Find AI coding agent startups with enterprise offerings" --json
parallel-cli findall run "AI startups in healthcare" -n 25 --json

# Poll and retrieve results
parallel-cli findall status <run_id> --json
parallel-cli findall poll <run_id> --json
parallel-cli findall result <run_id> --json
parallel-cli findall schema <run_id> --json
```

### 6. Monitor (Change Detection)
```bash
parallel-cli monitor list --json
parallel-cli monitor get <monitor_id> --json
parallel-cli monitor events <monitor_id> --json
parallel-cli monitor delete <monitor_id> --json
```

## Context Chaining

```bash
# Launch first research job
parallel-cli research run "What are the top AI coding agents?" --json

# Follow-up reuses earlier context
parallel-cli research run \
  "What enterprise controls does the top-ranked one offer?" \
  --previous-interaction-id trun_xxx \
  --json
```

## Common Flags

| Flag | Purpose |
| :--- | :--- |
| `--json` | Machine-readable output (always use) |
| `--no-wait` | Async launch for long jobs |
| `--previous-interaction-id <id>` | Context chaining |
| `--max-results <n>` | Search result count |
| `--mode one-shot\|agentic` | Search behavior |
| `--include-domains` | Narrow trusted sources |
| `--exclude-domains` | Strip noisy domains |
| `--after-date YYYY-MM-DD` | Recency filter |

## Pitfalls

| Problem | Fix |
| :--- | :--- |
| Auth error (exit 3) | Run `parallel-cli login --device` or set `PARALLEL_API_KEY` |
| Large results overflow context | Save to `/tmp/*.json` with `-o` |
| Citing invented sources | Only cite URLs returned by CLI output |
| Choosing Parallel for simple lookups | Use Hermes native `web_search` instead |
| Omitting `--json` | Always add `--json` for agent parsing |

## Federation Context

- **Hermes**: Skill installed at `~/.hermes/skills/research/parallel-cli/`
- **A-FORGE / arifOS**: Can invoke via ShellTool or direct subprocess
- **Pricing**: Free tier available; paid tiers for higher volume
- **Overlap**: Brave Search (native) covers quick lookups; Parallel covers deep research, enrichment, and monitoring

## When to Use Parallel vs Native

| Task | Use | Tool |
| :--- | :--- | :--- |
| Quick fact lookup | Native | Hermes `web_search` |
| Deep multi-step research | Parallel | `parallel-cli research run` |
| CSV enrichment | Parallel | `parallel-cli enrich run` |
| Entity discovery at scale | Parallel | `parallel-cli findall run` |
| Change monitoring | Parallel | `parallel-cli monitor create` |
| Content extraction (rich) | Parallel | `parallel-cli extract` |

## Related

- [[Skill_MCP_Mcporter]] (MCP mesh CLI — can discover Parallel MCP if exposed)
- [[Skill_Inference_CLI]] (AI app gateway — complementary for generative tasks)
- [[MCP_Tools]] (Tool surface architecture)
