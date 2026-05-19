# arifOS VPS RUNBOOK - Sovereign Operating Manual

<!--
SOT-MANIFEST
owner: Arif
last_verified: 2026-05-19
valid_from: 2026-05-19
valid_until: 2026-06-19
confidence: high
scope: /root
epistemic_status: CLAIM
-->

> **Authority:** F13 SOVEREIGN — human veto absolute
>
> **DITEMPA BUKAN DIBERI** — Intelligence is forged, not given.

This machine is the arifOS federation VPS. `/root` is not a monorepo. Every
agent must resolve the target repo or service before editing, deploying, or
claiming success.

## Landing Sequence

1. Read `/root/AGENTS.md`.
2. Read `/root/CONTEXT.md`.
3. Read this runbook.
4. Resolve the target repo or service.
5. Inspect live state before touching files:
   - `df -h /`
   - `free -h`
   - `uptime`
   - `docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'`
   - `systemctl is-active docker caddy arif-agent-worker hermes-a2a hermes-asi-gateway openclaw-gateway`

## Agent Usage Doctrine

| Role | Primary Agent | Use | Boundary |
|---|---|---|---|
| Machine operator | Codex | Surgical patches, tests, Docker/systemd checks, git diff discipline | Must verify before reporting done |
| Auditor | Gemini | Claim tagging, 888_HOLD risk review, governance checks | Read/audit first, execute only when bounded |
| Background orchestrator | OpenClaw | A2A, long-running research, delegated tool orchestration | Not final authority for host changes |
| Relay | Hermes | Telegram/human gateway, briefings, lightweight routing | Not direct root machine manager |
| Fast executor | Claude/Kimi | Bounded refactors or generated patches | No broad root/autopilot execution |
| GitHub interface | Copilot CLI | PRs, issues, GitHub-side automation | Not primary VPS operator |
| Experiment lab | OpenCode | Prototypes and model/tool experiments | No production path writes without Codex/Gemini review |

## Non-Negotiable Rules

1. No agent may declare `999_SEAL`. Only Arif or arifOS constitutional tooling can seal.
2. Every real change must produce:
   - exact changed files
   - `git diff --stat` or config diff summary
   - relevant tests or syntax checks
   - live health check when a service is affected
3. No destructive action without explicit approval:
   - `rm -rf`
   - `docker system prune -a`
   - database `DROP`, `TRUNCATE`, broad `DELETE`
   - branch deletion, force-push, history rewrite
   - volume removal
4. No plaintext secrets in agent configs. Use environment references or protected secret stores.
5. Production deploys require build/test pass, health probe, and rollback note.
6. Public ingress, auth, users/groups, firewall, `.env`, and secret rotation are `888_HOLD` unless Arif explicitly authorizes the exact action.

## Current Agent Hardening Baseline

Claude:
- No blanket auto-permission prompt skipping.
- Avoid `Bash(*)`, `Write(*)`, and `KillShell(*)` unless a session explicitly opts in.

Kimi:
- `default_yolo = false`.
- The global wrapper must not auto-inject `--afk`; AFK must be explicit via `KIMI_FORCE_AFK=1`.

OpenCode:
- MCP filesystem must be scoped to federation work roots, not all `/root`.
- Tokens in headers must come from environment variables.
- Experimental models and plugins are allowed only outside production paths unless Codex/Gemini review is complete.

Copilot:
- GitHub-side and PR work only by default.
- Use `~/.copilot/mcp-config.json` for federation MCP config.

Hermes:
- Relay and Telegram gateway.
- May route to OpenClaw or summarize state.
- Must not be treated as final deploy/seal authority.

OpenClaw:
- Background orchestrator and A2A gateway.
- Good for long-running research, delegated tool orchestration, and agent cards.
- Must not be sole authority for public deploys, secrets, or host mutation.

## Emergency Procedure

Prefer graceful service control over process-name killing.

Inspect:

```bash
systemctl is-active hermes-a2a hermes-asi-gateway openclaw-gateway arif-agent-worker
ps -eo pid,ppid,cmd --sort=cmd | rg -i 'codex|claude|gemini|opencode|copilot|kimi|openclaw|hermes'
```

Pause gateways, if needed:

```bash
systemctl stop hermes-a2a.service hermes-asi-gateway.service openclaw-gateway.service
```

Restart gateways:

```bash
systemctl restart hermes-a2a.service hermes-asi-gateway.service openclaw-gateway.service
```

Avoid broad `pkill`. If a single process must be stopped, identify the PID and use `kill <PID>`.

## Health Checks

Core host:

```bash
df -h /
free -h
uptime
systemctl --failed --no-pager
```

Docker federation:

```bash
docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'
curl -fsS http://127.0.0.1:8080/health
curl -fsS http://127.0.0.1:8081/health
curl -fsS http://127.0.0.1:8082/health
curl -fsS http://127.0.0.1:8083/health
curl -fsS http://127.0.0.1:3001/health || true
curl -fsS http://127.0.0.1:18789/health
```

Hermes/OpenClaw:

```bash
systemctl --no-pager --full status hermes-a2a.service hermes-asi-gateway.service openclaw-gateway.service
curl -fsS http://127.0.0.1:18789/health
curl -fsS http://127.0.0.1:18795/.well-known/agent-card.json
```

Note: Hermes A2A currently listens on `18001` but does not expose `/health`.

## Repo Status Sweep

```bash
for repo in arifOS A-FORGE AAA geox WEALTH WELL HERMES arif-sites; do
  if [ -d "/root/$repo/.git" ]; then
    echo "=== $repo ==="
    git -C "/root/$repo" status --short
    git -C "/root/$repo" log --oneline -1
  fi
done
```

## Seal Procedure

Agents may prepare a seal packet. They may not self-seal.

Seal packet must include:
- objective
- files changed
- commands run
- test/health evidence
- dirty workspace status
- remaining `888_HOLD` items
- rollback path

Arif or arifOS decides whether the packet becomes `999_SEAL`.
