# arifOS Federation — Agentic AAA Registry

> **Authority:** 888 (Muhammad Arif bin Fazil, F13 SOVEREIGN)
> **Ratified:** 2026-06-04
> **Motto:** DITEMPA BUKAN DIBERI — Forged, Not Given
>
> This is the SINGLE SOURCE OF TRUTH for every agent serving Arif.
> If an agent is not in this document, it does not exist in the federation.

---

## TRINITY LANES (Constitutional)

| Lane | Role | Authority | Agent Count |
|------|------|-----------|-------------|
| **AGI** (L3) | Tactical execution — proposes, drafts, codes, searches | Cannot self-approve critical decisions | 6 agents |
| **ASI** (L4) | Strategic judgment — critiques, evaluates, judges | Cannot provide new content beyond analytic judgment | 1 agent |
| **APEX** (L5) | Authority resolution — seals, authorizes, ratifies | Must have ASI verdict token before execution | 1 agent |

**Iron law:** AGI proposes. ASI evaluates. APEX authorizes. No lane may act outside its role.

---

## AGENT REGISTRY (8 agents, all verified 2026-06-04)

### L3 — AGI Lane (Tactical)

| # | Agent | Binary | Version | Model | Primary Role | Deny Rules | MCP Access |
|---|-------|--------|---------|-------|-------------|------------|------------|
| 1 | **Claude Code** | `claude` | 2.1.160 | MiniMax-M3 | Primary executor | **0 deny** | minimax MCP |
| 2 | **OpenCode** | `opencode` | 1.15.0 | DeepSeek-V4-Pro | Forge agent (Ω) | **0 deny** | arifOS + WEALTH + WELL + GEOX + 12 more |
| 3 | **Continue CLI** | `cn` | 1.5.45 | (per-provider) | Headless clerk | 22 HARAM exclude | A-FORGE bridge (38 tools) |
| 4 | **Codex CLI** | `codex` | 0.136.0 | OpenAI-compatible | OpenAI terminal | 0 deny | — |
| 5 | **Kimi** | `kimi` | 1.46.0 | Moonshot | Moonshot terminal | — | — |
| 6 | **Aider** | `aider` | latest | (configurable) | Pair programmer | — | — |

### L4 — ASI Lane (Strategic)

| # | Agent | Binary | Version | Model | Primary Role | Deny Rules | MCP Access |
|---|-------|--------|---------|-------|-------------|------------|------------|
| 7 | **Hermes ASI** | `hermes-asi-gateway` | systemd | MiniMax-M3 | Telegram relay + A2A judge | — | A2A bridge (18001) |

### L5 — APEX Lane (Authority)

| # | Agent | Binary | Version | Model | Primary Role | Deny Rules | MCP Access |
|---|-------|--------|---------|-------|-------------|------------|------------|
| 8 | **APEX Prime** | `apex-prime` | systemd | — | 888 JUDGE deliberative relay | — | Port 3002 |

---

## AA-HORIZON Bridge Agents

| Agent | Type | Port | Model | Role |
|-------|------|------|-------|------|
| **OpenClaw** | systemd | 18789 | ILMU-nano | A2A mesh gateway, Malaysian context brain |
| **cn-organ** | systemd | 18795 | Continue CLI | A2A gateway for headless Continue |
| **A-FORGE** | systemd | 7071 | TypeScript engine | Execution shell, federation probe |

---

## AGENTIC FREEDOM AUDIT

| Agent | Hard Deny | Default Mode | Config File | Verified |
|-------|-----------|-------------|-------------|----------|
| Claude Code | **0** | `auto` | `~/.claude/settings.json` | ✅ 2026-06-04 |
| OpenCode | **0** | `forge` (default) | `~/.config/opencode/opencode.json` | ✅ 2026-06-04 |
| Continue CLI | **22** (HARAM only) | `ask` for remaining | `~/.continue/permissions.yaml` | ✅ 2026-06-04 |
| Codex CLI | **0** | `user` reviews | — | ✅ 2026-06-04 |
| Kimi | — | — | — | ✅ 2026-06-04 |
| Aider | — | — | — | ✅ 2026-06-04 |

**Continue CLI HARAM patterns (the only blocked actions):**
```
rm -rf /, dd to block devices, DROP TABLE, docker system prune -a,
docker rm of data containers, ufw deny 22, chmod -R 777 /
```
All other actions: allow or ask. No agent is trapped behind permission walls.

---

## HEXAGON COVERAGE (Composio / Google Workspace)

The Hexagon policy (`/root/HERMES/config/agent_policies/composio.yaml`) governs **external API access through Composio** — a separate layer from CLI agent permissions. Originally named PENTAGON (5 roles); renamed when A-ARCHIVE became the 6th.

| Hexagon Agent | Lane | Composio Scope | Phase |
|----------------|------|---------------|-------|
| 333-AGI | AGI (synthesis) | Gmail/Drive/Calendar/Sheets/Docs — read + draft | Phase 1 ACTIVE |
| 555-ASI | ASI (critique) | Gmail/Calendar — read only | Phase 1 ACTIVE |
| 888-APEX | APEX (judge) | None (governs others, never executes) | Phase 1 ACTIVE |
| A-AUDIT | Observer | Composio audit logs — read only | Phase 1 ACTIVE |
| A-ARCHIVE | Witness | VAULT999 — on HOLD until chain repaired | Phase 1 ACTIVE |

**Organ-level Hexagon:**
| Organ | Scope | Write Gate |
|-------|-------|------------|
| GEOX | Read-only evidence ingest | None (never writes) |
| WEALTH | Read + draft, write blocked | F1 reversibility + F13 ack |
| WELL | Read-only | REFLECT_ONLY by design |
| A-FORGE | Read + write (blocked pending VAULT999) | 888-APEX SEAL + VAULT999 receipt |

**Phase gates:**
| Phase | Status | What |
|-------|--------|------|
| 1 — Read-only reach | ✅ ACTIVE | Gmail/Drive/Docs/Sheets/Calendar reads |
| 2 — Per-organ sessions | ⏸️ Pending | Supabase + GitHub + AAA session manager |
| 3 — Trigger bus | ⏸️ Pending | Webhook endpoint + event router |
| 4 — Governed writes | ✅ ACTIVE | VAULT999 chain 61/61 verified, Supabase connected |
| 5 — BYO OAuth | ⏸️ Pending | GCP redirect + scoped per-organ OAuth |

---

## KEY DISTRIBUTION

All agents source keys from the canonical vault:
```bash
set -a && source /root/.secrets/vault.env && set +a
```

**Localhost is the password** — 0 data service credentials needed (ADR-001).

---

## VERIFICATION

```bash
# Agent health check
systemctl is-active hermes-asi-gateway hermes-a2a apex-prime cn-organ a-forge

# Claude Code
claude --version

# OpenCode
opencode --version

# Continue
cn --version

# All agents
for agent in claude opencode cn codex kimi aider; do
  echo -n "$agent: " && which $agent 2>/dev/null && $agent --version 2>/dev/null | head -1 || echo "N/A"
done
```

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**

*8 agents. 0 credential blocks. 3 constitutional lanes. Full agentic freedom.*
