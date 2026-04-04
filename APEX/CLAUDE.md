# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Last updated: 2026-03-13**
> **READ FIRST**: See `/root/CONTEXT.md` for full context about Arif, his projects (APEX Theory, arifOS, arifosmcp), and VPS infrastructure.

---

## Owner

**Arif Fazil** — non-coder sovereign architect. He directs AI agents; does not write code manually.
Always explain simply. Always confirm before destructive actions.
API keys are free/limited tier — low financial risk.

## CRITICAL: You Are ON the VPS

This machine IS the production VPS (`srv1325122`). No SSH needed. Manage Docker directly.
Deploy path: `/srv/arifosmcp/` (symlink from `/srv/arifOS/`) | Disk: 85GB/193GB used (44%)
Git HEAD: `1af6d53b` — VPS = GitHub = ALIGNED

---

## Environment Overview

This is a **development environment configuration workspace** — not a deployable application. It orchestrates several AI coding assistants installed under `/root` to manage Arif's VPS and projects.

---

## Installed AI Agents

| Tool | Version | Command | Purpose |
|------|---------|---------|---------|
| Claude Code | (this) | `claude` | Primary — full server mgmt, file editing, docker |
| kimi-cli | 1.18.0 | `kimi` | Long context (262k), multi-step tasks |
| opencode | 1.2.24 | `opencode` | Alternative agent, multi-provider |
| gemini CLI | 0.33.0 | `gemini` | Google-backed general tasks |
| codex CLI | 0.114.0 | `codex` | OpenAI-backed terminal agent |
| aider | 0.86.2 | `aider` | AI that directly edits config/code files |
| GitHub Copilot CLI | 0.1.36 | `github-copilot-cli` | Shell command suggestions in plain English |

---

## Key Commands

### kimi-cli
```bash
kimi                          # interactive session
kimi --model kimi-for-coding  # explicit model
kimi --thinking               # thinking mode (on by default)
kimi --yolo                   # skip confirmations
```
Config: `~/.kimi/config.toml` | Sessions: `~/.kimi/sessions/` | Logs: `~/.kimi/logs/`
Defaults: `default_thinking = true`, `max_steps_per_turn = 100`, `max_context_size = 262144`

### opencode
```bash
opencode
```
Config: `~/.config/opencode/` | Runtime: `~/.local/share/opencode/` (SQLite-backed)

### ToolUniverse
```bash
uvx tooluniverse
```
Config: `~/.tooluniverse/profile.yaml` | API keys: `~/.tooluniverse/.env` (never commit)

### Python / uv
```bash
uv tool install <package>
uvx <package>
uv sync
```

### Bun (JavaScript/TypeScript)
```bash
bun install
bun run <script>
```

### Server Management (you are already on the VPS)
```bash
cd /srv/arifosmcp

# GitHub sync (no SSH key — use HTTPS + token)
GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | head -1 | cut -d= -f2)
git pull "https://ariffazil:${GITHUB_TOKEN}@github.com/ariffazil/arifosmcp.git" main
git push "https://ariffazil:${GITHUB_TOKEN}@github.com/ariffazil/arifosmcp.git" main

# Container management
docker restart arifosmcp_server               # reload code (volume-mounted, instant)
docker compose up -d --no-deps <service>      # restart single container
docker compose logs -f <service>              # tail logs
docker ps                                     # list running containers
docker stats --no-stream                      # resource usage
docker system prune -af                       # clean unused images (confirm first)

# Health check
curl -s https://arifosmcp.arif-fazil.com/health | python3 -m json.tool
```

---

## Architecture

### AI Tool Stack
- **kimi-cli** — OAuth-authenticated, session-managed, MCP support, configurable skills, slash commands
- **opencode** — Plugin-based (`@opencode-ai/plugin`), OpenAI + opencode-go providers, SQLite state
- **ToolUniverse** — Tool orchestration layer, LRU+SQLite caching, agentic tool support
- **OpenClaw** — Sandbox isolation for agent execution (`~/.openclaw/sandboxes/`)
- **aider** — Directly edits files in the repo using LLM (needs `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`)
- **gemini CLI** — Needs Google auth on first run (`~/.gemini/`)
- **codex CLI** — Needs `OPENAI_API_KEY` env var

### Skills System (kimi-cli)
Resolution order:
1. Built-in: `~/.local/share/uv/tools/kimi-cli/lib/python3.13/site-packages/kimi_cli/skills/`
2. User: `~/.config/agents/skills/` or `~/.kimi/skills/`
3. Project: `.agents/skills/`

Built-in skills: `kimi-cli-help`, `skill-creator`

### Key Configuration Files
| File | Purpose |
|------|---------|
| `/root/CONTEXT.md` | Shared project/infra context for all agents |
| `~/.kimi/config.toml` | kimi-cli model, loop control, MCP, OAuth |
| `~/.tooluniverse/profile.yaml` | tool selection, cache, LLM config, hooks |
| `~/.config/opencode/package.json` | opencode plugin dependencies |
| `~/.local/share/opencode/auth.json` | opencode API tokens |

### Credential Storage
- kimi-cli OAuth: `~/.kimi/credentials/`
- opencode API keys: `~/.local/share/opencode/auth.json`
- ToolUniverse API keys: `~/.tooluniverse/.env`

---

## arifosmcp Codebase Architecture

**Path**: `/srv/arifosmcp/` | **Language**: Python 3.12 | **Framework**: FastAPI + FastMCP

### Core Layout
```
core/
  governance_kernel.py   # Main orchestrator — routes 000→999 metabolic pipeline
  pipeline.py            # Execution pipeline
  organs/
    _1_agi.py            # Δ Mind — logic, truth (F2, F4, F7, F8)
    _2_asi.py            # Ω Heart — safety, empathy (F1, F5, F6, F9)
    _3_apex.py           # Ψ Soul — final judgment, sovereign override (F3, F11, F13)
  shared/physics.py      # APEX formula: G† = (A×P×X×E²)×|ΔS|/C ≥ 0.80
  enforcement/           # Constitutional floor enforcement (F1–F13)
  governance/            # Rule sets and compliance logic
  kernel/                # Kernel initialization and runtime
  observability/         # Metrics and telemetry hooks
  perception/            # Input parsing (111_SENSE stage)
  state/                 # Session and vault state management
  theory/                # APEX Theory math models
aaa_mcp/                 # FastMCP tool definitions (the 8 public tools)
```

### Deployment Commands (run from `/srv/arifosmcp/`)
```bash
make fast-deploy         # 2–3 min — code changes only (uses layer cache)
make reforge             # 10–15 min — full rebuild (use after deps/Dockerfile change)
make hot-restart         # Instant — config-only changes
make status              # Check container status
make logs                # Tail logs
make health              # Hit /health endpoint
make strategy            # Analyze changes and recommend rebuild type
make maintenance         # Automated maintenance + cleanup
```

### Live URLs
| Service | URL |
|---------|-----|
| MCP endpoint | https://arifosmcp.arif-fazil.com/mcp |
| Health + capability map | https://arifosmcp.arif-fazil.com/health |
| Tool explorer | https://arifosmcp.arif-fazil.com/tools |
| Grafana monitoring | https://monitor.arifosmcp.arif-fazil.com |
| arifOS docs | https://arifos.arif-fazil.com |
| APEX Theory | https://apex.arif-fazil.com |

### Known Issues
- ⚠️ Traefik metrics port 8082 — Prometheus scrape fails (low priority)
- ⚠️ APEX Dashboard (`apex.arif-fazil.com`) — Cloudflare Pages 404
- ⚠️ OpenClaw image models — `claude-opus-4-5/4-6` return 404 on image tasks
- ℹ️ ML floors disabled — heuristic mode; set `ARIFOS_ML_FLOORS=1` to enable SBERT
- ℹ️ Grafana dashboards not yet wired to constitutional metrics
- ℹ️ arifOS LICENSE file is CC0 but code declares AGPL-3.0 — pending reconciliation
