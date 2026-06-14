# arifOS Federation — Agentic AAA Registry

> **Authority:** 888 (Muhammad Arif bin Fazil, F13 SOVEREIGN)
> **Ratified:** 2026-06-04 | **Last updated:** 2026-06-14
> **Motto:** DITEMPA BUKAN DIBERI — Forged, Not Given
>
> This is the SINGLE SOURCE OF TRUTH for every agent serving Arif.
> If an agent is not in this document, it does not exist in the federation.

---

## CONSTITUTIONAL LANES (Updated 2026-06-14)

| Lane | Role | Authority | Agent Count |
|------|------|-----------|-------------|
| **AGI** (L3) | Tactical execution — proposes, drafts, codes, searches | Cannot self-approve critical decisions | 6 agents |
| **ASI** (L4) | Strategic judgment — critiques, evaluates, judges | Cannot provide new content beyond analytic judgment | 1 agent |

**APEX lane removed 2026-06-14:** The APEX authority resolution role (888 JUDGE + 999 SEAL) is now fully performed by arifOS kernel tools — `arif_judge_deliberate` (888) and `arif_vault_seal` (999). The legacy APEX Prime daemon (port 3002) remains active for backward compat but is no longer a separate constitutional lane. Deliberation is absorbed into AAA a2a-server and arifOS runtime.

**Iron law:** AGI proposes. ASI evaluates. Kernel adjudicates. No lane may act outside its role.

---

## AGENT REGISTRY (7 agents, verified 2026-06-14)

### L3 — AGI Lane (Tactical)

| # | Agent | Binary | Version | Model | Primary Role | Deny Rules | MCP Access |
|---|-------|--------|---------|-------|-------------|------------|------------|
| 1 | **Claude Code** | `claude` | 2.x | DeepSeek / per-provider | Primary executor | **0 deny** | arifOS + federation MCP |
| 2 | **OpenCode (333-AGI)** | `opencode` | 1.15+ | DeepSeek-V4-Pro | Forge agent (Ω, 333-THINK) | **0 deny** | arifOS + WEALTH + WELL + GEOX + 12+ MCP |
| 3 | **Continue CLI** | `cn` | 1.5+ | (per-provider) | Headless clerk, cn-organ gateway | 22 HARAM exclude | A-FORGE bridge, arifOS MCP |
| 4 | **Codex CLI** | `codex` | 0.136+ | OpenAI-compatible | OpenAI terminal | 0 deny | — |
| 5 | **Kimi** | `kimi` | 1.46+ | Moonshot / K2 | Moonshot terminal, complex reasoning | — | arifOS MCP |
| 6 | **Aider** | `aider` | latest | (configurable) | Pair programmer | — | — |

### L4 — ASI Lane (Strategic)

| # | Agent | Binary | Version | Model | Primary Role | Deny Rules | MCP Access |
|---|-------|--------|---------|-------|-------------|------------|------------|
| 7 | **Hermes ASI** | `hermes-asi-gateway` | systemd | MiniMax-M3 | Telegram relay + A2A bridge | — | A2A :18001, arifOS MCP |

---

## AA-HORIZON Bridge Agents

| Agent | Type | Port | Model | Role |
|-------|------|------|-------|------|
| **OpenClaw** | systemd | 18789 | ILMU-nano | A2A mesh gateway, Malaysian context brain |
| **cn-organ** | systemd | 18795 | Continue CLI | A2A gateway for headless Continue |
| **A-FORGE** | systemd | 7071 | TypeScript engine | Execution shell, federation probe |
| **AAA a2a-server** | systemd | 3001 | Node/Express | A2A gateway, governance adapter, React cockpit |

---

## AGENTIC FREEDOM AUDIT (Updated 2026-06-14)

| Agent | Hard Deny | Default Mode | Config File | Verified |
|-------|-----------|-------------|-------------|----------|
| Claude Code | **0** | `auto` | `~/.claude/settings.json` | ✅ 2026-06-14 |
| OpenCode | **0** | `forge` (default) | `~/.config/opencode/opencode.json` | ✅ 2026-06-14 |
| Continue CLI | **22** (HARAM only) | `ask` for remaining | `~/.continue/permissions.yaml` | ✅ 2026-06-14 |
| Codex CLI | **0** | `user` reviews | — | ✅ 2026-06-14 |
| Kimi | — | — | — | ✅ 2026-06-14 |
| Aider | — | — | — | ✅ 2026-06-14 |

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
| A-AUDIT | Observer | Composio audit logs — read only | Phase 1 ACTIVE |
| A-ARCHIVE | Witness | VAULT999 — read only | Phase 1 ACTIVE |

**Note 2026-06-14:** APEX lane removed from Hexagon. The 888 JUDGE and 999 SEAL roles are now kernel tools (`arif_judge_deliberate`, `arif_vault_seal`), not a separate agent lane. Hexagon composition: 4 active agents (333-AGI, 555-ASI, A-AUDIT, A-ARCHIVE).

**Organ-level Hexagon:**
| Organ | Scope | Write Gate |
|-------|-------|------------|
| GEOX | Read-only evidence ingest | None (never writes) |
| WEALTH | Read + draft, write blocked | F1 reversibility + F13 ack |
| WELL | Read-only | REFLECT_ONLY by design |
| A-FORGE | Read + write (via `arif_forge_execute`) | 888 JUDGE SEAL + VAULT999 receipt |

**Phase gates:**
| Phase | Status | What |
|-------|--------|------|
| 1 — Read-only reach | ✅ ACTIVE | Gmail/Drive/Docs/Sheets/Calendar reads |
| 2 — Per-organ sessions | ⏸️ Pending | Supabase + GitHub + AAA session manager |
| 3 — Trigger bus | ⏸️ Pending | Webhook endpoint + event router |
| 4 — Governed writes | ✅ ACTIVE | VAULT999 chain intact (61 seals), Supabase connected |
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
# Core federation health
systemctl is-active arifos arifosd wealth-organ well geox-mcp a-forge aaa-a2a
systemctl is-active hermes-asi-gateway openclaw-gateway cn-organ vault999-api vault999-writer

# Available CLIs
for agent in claude opencode cn codex kimi aider; do
  echo -n "$agent: " && which $agent 2>/dev/null && $agent --version 2>/dev/null | head -1 || echo "N/A"
done
```

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**

*7 registered agents. 0 credential blocks. 2 constitutional lanes (AGI + ASI). Kernel tools fill the authority role.*
*Last updated: 2026-06-14 (post-registry-audit — APEX absorbed, models updated, registry cross-referenced)*
