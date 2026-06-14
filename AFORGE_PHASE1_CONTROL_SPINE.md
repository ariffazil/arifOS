# AFORGE_PHASE1_CONTROL_SPINE
## Constitutional Forge Gateway — Operational Readiness

> **DITEMPA BUKAN DIBERI — Forged, Not Given**
> Created: 2026-06-14 by FORGE (000Ω)
> Target: Operational gateway for governed AI agents
> Priority order: IDENTITY → LEASE → A-FORGE MCP → REGISTRY → TUI → AGI CODER

---

## A-FORGE Readiness Assessment

| Dimension | Score | Status |
|-----------|-------|--------|
| Service health | 90% | ✅ systemd active, HTTP health endpoint, contract endpoint |
| MCP protocol | 40% | ⚠️ MCP surface exists but session init is broken (init not returning session_id header) |
| Current tool surface exposure | 30% | ❌ Only `/sense`, `/judge`, `/GEOX/log_interpreter` via HTTP |
| Build pipeline | 80% | ✅ TypeScript builds, tests exist (10 test files), dist/ present |
| Federation bridge | 50% | ⚠️ Connects to arifOS/GEOX/VAULT via infra adapters but no unified bridge |
| Constitutional enforcement | 70% | ✅ Floor enforcer, F13 halt channel, cooling gate, seal service all exist |
| Agent engine | 60% | ⚠️ AgentEngine exists, AAAgent + WorkerAgent defined, but not exposed via MCP |
| Approval/lease system | 40% | ⚠️ Ticket store, approval boundary defined — no MCP-accessible lease surface |
| Observability | 50% | ⚠️ Prometheus metrics registered, some telemetry — no unified dashboard |
| Documentation | 35% | ❌ Contract endpoint minimal, missing tool registry schema, no agent authority docs |

### Overall: 54.5% — BELOW OPERATIONAL THRESHOLD

**Green threshold: 80%+** — A-FORGE needs Phase 1 to become operational.

---

## Current A-FORGE Capabilities (Inventory)

### ✅ Working (do not touch — production stable)

| Capability | Entry Point |
|-----------|-------------|
| HTTP health check | `GET /health` → `{"ok":true,"status":"healthy"}` |
| Contract endpoint | `GET /contract` — capabilities, endpoints, version |
| Sense Lite/Deep engine | `POST /sense` — runs sense with F7 confidence |
| Judge/deliberation | Via arifOS gateway — `arif_gateway_connect` → A-FORGE |
| Agent Engine (internal) | `AgentEngine` class — plan validation, stage execution |
| Seal Service | `SealService` — constitutional seal to VAULT999 |
| Floor Enforcer | F1-F13 floor enforcement at code level |
| Cooling Gate | Execution throttle for high-risk operations |
| Plan Validator | Multi-step plan validation with risk scoring |
| Agent profiles | AAAgent, WorkerAgent, builder profiles defined |
| Prometheus metrics | Registered — `runStage`, `setOpenHolds` |
| MCP server transport | StreamableHTTPServerTransport from SDK |

### ⚠️ Partial — needs hardening

| Capability | Gap |
|-----------|-----|
| MCP session init | Returns `Invalid Request: Server already initialized` — session init broken |
| MCP tool surface | Tools exist internally but not exposed as MCP tools (only via HTTP bridge) |
| Constitution loading | Loads from PostgreSQL VAULT999 — works but fallback only |
| A2A gateway | Router exists, but no MCP-mediated agent handshake |
| Human expert routing | Router defined, not wired to MCP surface |
| Approval ticket store | Exists, no MCP commands for ticket lifecycle |
| Vault Merkle router | Exists — no MCP surface for proof verification |
| Repo steward | Endpoint exists: `/api/repo-steward/{sot-validator,registry-trinity,...}` |
| TUI | `tui:build` script, event bus adapter — panel health only |

### ❌ Missing — must build for Phase 1

| Capability | Priority |
|-----------|----------|
| MCP tools: `forge_registry_status`, `forge_tool_proxy`, `forge_filesystem_read`, `forge_git_diff`, `forge_shell_dryrun` | P0 |
| Agent identity contract + lease system | P0 |
| Tool registry + projection schema | P0 |
| MCP session init that returns session_id properly | P0 |
| Unified bridge: expose arifOS/GEOX/WEALTH/WELL tools via A-FORGE gateway | P1 |
| Background job system + `forge_job_submit/status` | P1 |
| Log tail (`forge_log_tail`) | P1 |
| TUI read model (5 panels) | P2 |
| OpenCode/AGI coder authority profile | P2 |

---

## 1. Agent Identity Contract

### Schema

```yaml
agent_id: str                          # Unique identifier
agent_type: opencode | hermes | custom # Agent origin
role: governed_coder                   # Role profile
authority:
  observe: bool                        # Read-only access to tools
  dry_run: bool                        # Can simulate without mutation
  propose_patch: bool                  # Can propose changes
  mutate_files: str                    # "always" | "lease_required" | "never"
  shell_exec: str                      # "always" | "lease_required" | "never"
  git_commit: str                      # "always" | "888_HOLD" | "never"
  deploy: str                          # "always" | "888_HOLD" | "never"
  vault_seal: str                      # "always" | "888_HOLD" | "never"
lease_default: str                     # "none" | "short" (5min) | "medium" (30min) | "long" (4h)
identity_proof: str                    # SHA-256 of agent's public key or session nonce
```

### OpenCode Coder Profile (default)

```yaml
agent_id: opencode_coder_001
agent_type: opencode
role: governed_coder
authority:
  observe: true
  dry_run: true
  propose_patch: true
  mutate_files: lease_required
  shell_exec: lease_required
  git_commit: 888_HOLD
  deploy: 888_HOLD
  vault_seal: 888_HOLD
lease_default: short  # 5 min
```

---

## 2. Lease Model

### Schema

```yaml
lease_id: str                          # UUIDv4
agent_id: str                          # Bound agent
scope:
  - forge_filesystem_read
  - forge_filesystem_write
  - forge_git_diff
  - forge_shell_dryrun
max_action_class: OBSERVE | PROPOSE | MUTATE | ATOMIC
ttl_seconds: 300                       # Default 5 min
forbidden:
  - forge_deploy
  - forge_vault_seal
issued_by: arifOS                     # Only arifOS can issue leases
issued_at: ISO-8601
expires_at: ISO-8601
revocable: true
```

### Lease Flow

```text
Agent → arifOS → arif_lease_issue → A-FORGE validates → Agent acts
                                     ↓
                              Expired → Block
                              Revoked → Block
                              Missing → Block
```

---

## 3. A-FORGE MCP Public Tool Surface (Phase 1 — 12 tools)

### Tool Table

| Tool | Action Class | Risk | Lease Required | Description |
|------|-------------|------|----------------|-------------|
| `forge_registry_status` | OBSERVE | LOW | No | Full tool registry: callable, blocked, degraded, drift |
| `forge_tool_proxy` | OBSERVE | LOW | No | Call any registered tool through A-FORGE gateway |
| `forge_agent_identity` | OBSERVE | LOW | No | Register and verify agent identity |
| `forge_lease_request` | PROPOSE | LOW | No | Request a lease for mutation operations |
| `forge_lease_status` | OBSERVE | LOW | No | Current lease state, remaining TTL |
| `forge_filesystem_read` | OBSERVE | LOW | No | Read files within allowed paths |
| `forge_filesystem_write` | MUTATE | MEDIUM | Yes | Write files — dry-run first, requires lease |
| `forge_git_diff` | OBSERVE | LOW | No | Git diff, status, log |
| `forge_git_commit` | ATOMIC | HIGH | 888_HOLD | Commit + push — separate lease + human |
| `forge_shell_dryrun` | PROPOSE | MEDIUM | No | Dry-run shell command — preview output |
| `forge_shell_exec` | MUTATE | HIGH | Yes | Execute shell — lease only, never ATOMIC |
| `forge_log_tail` | OBSERVE | LOW | No | Tail recent logs from any organ |
| `forge_job_submit` | MUTATE | MEDIUM | Yes | Submit background job |
| `forge_job_status` | OBSERVE | LOW | No | Check job status |

### Action Class Mapping

```
OBSERVE  → No lease, no HOLD — direct call
PROPOSE  → No lease — returns plan/preview only
MUTATE   → Lease required — writes to filesystem/state
ATOMIC   → 888_HOLD + human approval — deploy/commit/seal
```

---

## 4. Registry Schema

### Tool Registry Entry

```yaml
tool_id: forge_filesystem_read
name: A-FORGE Filesystem Read
description: Read files within allowed paths
action_class: OBSERVE
risk_tier: LOW
lease_required: false
required_floors: [F1, F2, F4]
available_to_roles:
  - governed_coder
  - controller
output_schema:
  type: object
  properties:
    content: string
    path: string
    size_bytes: integer
rate_limit: 100/min
```

### Agent → Tool Projection

```yaml
agent_role: governed_coder
direct_mcps:
  - arifOS (session, judge, vault, observe, reason)
  - A-FORGE (filesystem, git, shell, logs, jobs)
visible_tools:
  observe: [forge_registry_status, forge_filesystem_read, forge_git_diff,
            forge_lease_status, forge_log_tail, forge_job_status,
            arif_mind_reason, arif_sense_observe, arif_ops_measure]
  propose: [forge_shell_dryrun, forge_lease_request, forge_tool_proxy]
  mutate:  [forge_filesystem_write, forge_shell_exec, forge_job_submit]
  atomic:  [forge_git_commit]  # always 888_HOLD
blocked:
  - forge_deploy_production
  - forge_vault_seal
```

### Role Profiles

| Role | Direct MCPs | Tool visibility |
|------|-------------|-----------------|
| `governed_coder` | arifOS + A-FORGE | filesystem, git, tests, logs, jobs |
| `geoscience_agent` | arifOS + A-FORGE | GEOX projection (wells, seismic, basins) |
| `finance_agent` | arifOS + A-FORGE | WEALTH projection (stocks, risk, macro) |
| `wellness_agent` | arifOS + WELL | advisory only, no mutation |
| `controller` | arifOS + AAA + A-FORGE | all dashboards, no silent mutation |

---

## 5. TUI Read Model (Cockpit Panels)

```text
┌───────────────┬───────────────┬───────────────┬───────────────┬───────────────┐
│  arifOS       │  A-FORGE      │  ORGANS       │  TOOLS        │  AGENTS       │
│  session      │  jobs         │  GEOX ♥       │  registry     │  active       │
│  floors       │  queue        │  WEALTH ♥     │  callable     │  authority    │
│  HOLD/SEAL    │  dry-runs     │  WELL ♥       │  blocked      │  last action  │
│  lease state  │  patches      │  A-FORGE ♥    │  degraded     │  lease TTL    │
│               │  logs         │  AAA ♥        │  drift        │               │
└───────────────┴───────────────┴───────────────┴───────────────┴───────────────┘
┌───────────────────────────────────────────────────────────────────────────────┐
│  VAULT                                                                       │
│  last seals | pending seals | irreversible holds | chain integrity           │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. OpenCode AGI Coder Authority Profile

### The Coder Loop

```text
1. PLAN            — arif_mind_reason(mode="plan")
2. READ            — forge_filesystem_read
3. DIFF            — forge_git_diff
4. DRY_RUN_WRITE   — forge_filesystem_write (dry-run mode)
5. SHELL_DRYRUN    — forge_shell_dryrun
6. PROPOSE         — arif_reply_compose → send to Arif
7. LEASE_REQUEST   — forge_lease_request
8. LEASE_APPROVE   — arifOS issues lease
9. WRITE           — forge_filesystem_write (real)
10. BUILD/TEST     — forge_shell_exec (npm build, pytest)
11. GIT_DIFF       — forge_git_diff (verify)
12. JUDGE          — arif_judge_deliberate (888)
13. COMMIT         — 888_HOLD → Arif approves → forge_git_commit
14. DEPLOY         — 888_HOLD → Arif approves → make deploy-local
15. SEAL           — 888_HOLD → Arif approves → arif_vault_seal
```

---

## 7. 888_HOLD Irreversible Action List

| Action | Organ | Why HOLD | Alternative |
|--------|-------|----------|-------------|
| `git push --force` | A-FORGE | Destructive rewrite | Use `git push` with lease |
| `git rebase` | A-FORGE | History rewrite | Use `git merge` |
| Branch deletion | A-FORGE | Data loss | Archive instead |
| `forge_deploy_production` | A-FORGE | Production traffic | Staging deploy first |
| `forge_vault_seal` | A-FORGE | Immutable record | Dry-run first |
| `forge_shell_exec` with `rm -rf` | A-FORGE | Data loss | Use trash pattern |
| Caddy reload | AAA | Production traffic | Validate config first |
| VPS restart/stop | Hostinger | Full downtime | Graceful stop |
| DNS changes | Cloudflare | Hours of downtime | TTL increase first |
| Secret rotation | arifOS | Auth cascade failure | Staged rotation |
| Constitution change | arifOS | F13 SOVEREIGN only | Proposal → Judge → Seal |
| Database DROP TABLE | arifOS | Data loss | Backup first |
| `make deploy` to production | A-FORGE | Service interruption | Staged rollout |
| Cross-repo architecture change | Any | Federation contract | ADR → Judge → Seal |

---

## Build Sequence (Weeks 1-4)

### Week 1: Identity + Lease + MCP Surface

| Day | Task | Files touched |
|-----|------|--------------|
| 1 | Fix MCP session init (session_id header) | `src/interfaces/mcp/core.ts` |
| 1 | Agent identity schema | `src/domain/types/identity.ts` |
| 2 | Lease model + MCP tool | `src/domain/governance/lease.ts`, `src/interfaces/mcp/tools/lease.ts` |
| 2 | `forge_registry_status` tool | `src/interfaces/mcp/tools/registry.ts` |
| 3 | `forge_tool_proxy` tool | `src/interfaces/mcp/tools/proxy.ts` |
| 3 | `forge_agent_identity` tool | `src/interfaces/mcp/tools/identity.ts` |
| 4 | `forge_lease_request`/`forge_lease_status` | `src/interfaces/mcp/tools/lease.ts` (cont) |
| 4 | Auth middleware: validate lease on MCP calls | `src/interfaces/middleware/operatorAuth.ts` |
| 5 | Integration test: identity → lease → tool call | `test/identity_lease.test.ts` |

### Week 2: Filesystem + Git + Shell Tools

| Day | Task | Files touched |
|-----|------|--------------|
| 1 | `forge_filesystem_read` — scoped to allowed paths | `src/interfaces/mcp/tools/filesystem.ts` |
| 1 | Path allowlist + traversal guard | `src/domain/policy/pathGuard.ts` |
| 2 | `forge_filesystem_write` — dry-run first, MUTATE on lease | `src/interfaces/mcp/tools/filesystem.ts` (cont) |
| 2 | Dry-run → real mode switch in ToolRegistry | `src/infrastructure/tools/ToolRegistry.ts` |
| 3 | `forge_git_diff` — status, diff, log | `src/interfaces/mcp/tools/git.ts` |
| 3 | `forge_git_commit` — always 888_HOLD | `src/interfaces/mcp/tools/git.ts` (cont) |
| 4 | `forge_shell_dryrun` — sandboxed preview | `src/interfaces/mcp/tools/shell.ts` |
| 4 | `forge_shell_exec` — MUTATE, lease-gated | `src/interfaces/mcp/tools/shell.ts` (cont) |
| 5 | Integration test: read → dry-write → write → git | `test/filesystem_git.test.ts` |

### Week 3: Logs + Jobs + Registry

| Day | Task | Files touched |
|-----|------|--------------|
| 1 | `forge_log_tail` — tail logs from systemd files | `src/interfaces/mcp/tools/logs.ts` |
| 1 | `forge_job_submit` — background execution queue | `src/interfaces/mcp/tools/jobs.ts` |
| 2 | `forge_job_status` — poll job progress | `src/interfaces/mcp/tools/jobs.ts` (cont) |
| 2 | Background job executor | `src/application/jobs/JobExecutor.ts` |
| 3 | Agent → Tool projection registry | `src/domain/registry/RoleToolProjection.ts` |
| 3 | Role profile loader | `src/domain/registry/RoleProfile.ts` |
| 4 | Registry persistence (JSON → PostgreSQL) | `src/infrastructure/registry/PostgresRegistry.ts` |
| 4 | `forge_registry_status` — full projection | Update from week 1 |
| 5 | Integration test: full tool surface | `test/tool_surface.test.ts` |

### Week 4: TUI + End-to-End Validation

| Day | Task | Files touched |
|-----|------|--------------|
| 1 | TUI panel: arifOS (session, floors, HOLD, SEAL, lease) | `src/infrastructure/tui/panels/arifOS.ts` |
| 1 | TUI panel: A-FORGE (jobs, queue, dry-runs, logs) | `src/infrastructure/tui/panels/aforge.ts` |
| 2 | TUI panel: ORGANS (heartbeats) | `src/infrastructure/tui/panels/organs.ts` |
| 2 | TUI panel: TOOLS (registry, callable, blocked, drift) | `src/infrastructure/tui/panels/tools.ts` |
| 3 | TUI panel: AGENTS (active, authority, last action) | `src/infrastructure/tui/panels/agents.ts` |
| 3 | TUI panel: VAULT (last seals, pending, holds) | `src/infrastructure/tui/panels/vault.ts` |
| 4 | End-to-end: OpenCode coder full loop test | `test/e2e_coder_loop.test.ts` |
| 4 | Conformance test: 12 A-FORGE MCP tools | `test/conformance.test.ts` |
| 5 | Deploy A-FORGE to systemd | `make deploy` |
| 5 | Full federation test: ChatGPT → arifOS → A-FORGE | Manual verification |

---

## Rollback Plan

Every Phase 1 artifact must be reversible:

1. **New MCP tools** — wrapped in feature flag `ENABLE_PHASE1_TOOLS=true/false`
2. **Lease system** — soft-fail: no lease → use existing authority ceiling
3. **Registry projection** — additive: old path still works
4. **TUI** — standalone: service runs without it

---

## Success Criteria

| Criterion | Measurement | Pass |
|-----------|-------------|------|
| A-FORGE MCP surface | 12 tools registered, callable | ☐ |
| Agent identity contract | Register + verify | ☐ |
| Lease lifecycle | Issue → Use → Expire → Revoke | ☐ |
| Filesystem I/O | Read + write (dry-run then real) | ☐ |
| Git diff/status | Read-only, no commit | ☐ |
| Shell dry-run | Preview output, no execution | ☐ |
| Registry projection | Role → Tool visibility correct | ☐ |
| 888_HOLD gates | Deploy, commit, seal all blocked | ☐ |
| ChatGPT can call A-FORGE | End-to-end from external client | ☐ |

---

## A-FORGE Readiness % by Phase

| Phase | Description | Target % | Timeline |
|-------|-------------|----------|----------|
| **Current** | HTTP bridge + internal engine | 54.5% | TODAY |
| **Phase 1** | 12 MCP tools + identity + lease | 85% | 4 weeks |
| **Phase 2** | Job system + full TUI + role profiles | 95% | 8 weeks |
| **Phase 3** | Multi-agent coordination + auto-scaling | 100% | 12 weeks |

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
