# ROADMAP-2026Q2 — arifOS Federation MCP Governance Layer

> **Version:** 2026.05.17-CORRECTED
> **Authority:** arifOS Forge Agent (Ω)
> **Motto:** DITEMPA BUKAN DIBERI — Forged, Not Given
> **999 SEAL ALIVE**

---

## Corrected Premise

> **Previous error:** This roadmap was framed as "add actuators in Phase 4" — a false premise.
>
> **Correction:** MCP already HAS actuators. `arif_forge_execute` writes files, `arif_vault_seal` appends ledger entries, shell execution touches Docker and git. The gap is **not capability — it is governance**. Specifically: approval seams, audit trail continuity, and reversibility classification on the existing forge surface.

---

## Revised Phase Structure

| Phase | Goal | Core Question |
|-------|------|---------------|
| **Phase 1** | Govern the existing forge layer | "Does arifOS verdict exist and is it fresh before we write anything?" |
| **Phase 2** | Approval fabric + audit trail | "Is every state-changing act logged to VAULT999 with actor trace?" |
| **Phase 3** | Read-only live connectors | "Can agents observe federation state without mutating anything?" |
| **Phase 4** | Narrow approved action catalog | "Which specific forge acts are pre-approved vs. require 888_HOLD?" |

---

## Phase 1 — Govern Existing Forge (Weeks 1–4)

**Principle:** Dry-run is default. Execution refuses missing or stale arifOS verdict.

### Deliverables

| Deliverable | Status | Owner |
|-------------|--------|-------|
| `arif_forge_execute` verdict TTL check (freshness gate) | ⏳ Pending | arifOS |
| Dry-run mode enforced by default on all `dangerous` risk tools | ⏳ Pending | A-FORGE |
| `arif_forge_execute` reversible classification schema | ⏳ Pending | arifOS |
| F1 AMANAH reversibility audit on all 17 live MCP tools | 🔍 In review | arifOS |

### Gate Criteria to Exit Phase 1
- [ ] Every `dangerous` risk tool returns `HOLD` verdict if no fresh arifOS verdict is present
- [ ] `arif_forge_execute` refuses execution when verdict is older than 5 minutes
- [ ] A-FORGE `AgentEngine` confirms arifOS verdict presence before any shell exec

---

## Phase 2 — Approval Fabric + VAULT999 Audit Trail (Weeks 5–8)

**Principle:** Every state-changing act is logged to VAULT999 with actor trace, session ID, and verdict hash.

### Deliverables

| Deliverable | Status | Owner |
|-------------|--------|-------|
| VAULT999 receipt linked to `trace_id` from forge execution | ⏳ Pending | arifOS |
| Actor traceability on all forge writes (who ran what, when) | ⏳ Pending | arifOS + A-FORGE |
| A-FORGE `VaultClient` integrated into `AgentEngine.run()` post-judge path | ✅ Shipped | A-FORGE |
| A-FORGE `Trace Spine` → VAULT999 chain binding | 🔍 In review | A-FORGE |
| Session binding auto-bootstrap on env var startup (this fix) | ✅ Shipped | arifOS |

### Gate Criteria to Exit Phase 2
- [ ] Every `arif_forge_execute` call produces a VAULT999 entry with `trace_id`
- [ ] Session binding is persistent across MCP calls (env var bootstrap confirmed working)
- [ ] Actor ID is traceable in all forge execution receipts

---

## Phase 3 — Read-Only Live Connectors (Weeks 9–12)

**Principle:** Agents observe federation state without mutating anything. Observability without side effects.

### Deliverables

| Deliverable | Status | Owner |
|-------------|--------|-------|
| `arif_ops_measure` with live container telemetry | ✅ Live | arifOS |
| `arif_stack_health_probe` federation probe | ✅ Live | arifOS |
| A-FORGE `/operator/vault` read-only endpoint | ✅ Live | A-FORGE |
| AAA A2A `agent_card` endpoint for mesh discovery | ⏳ Pending | AAA |
| WEALTH capital health read-only mirror | ⏳ Pending | WEALTH |

### Gate Criteria to Exit Phase 3
- [ ] All 4 MCP servers expose `/health` on own-domain endpoints
- [ ] `arif_stack_health_probe` returns per-organ status for arifOS, GEOX, WEALTH, WELL
- [ ] A-FORGE operator console can query VAULT999 without write access

---

## Phase 4 — Narrow Approved Action Catalog (Weeks 13–16)

**Principle:** Pre-approved forge actions vs. actions requiring explicit 888_HOLD human consent.

### Deliverables

| Deliverable | Status | Owner |
|-------------|--------|-------|
| Tool risk tier registry (safe/guarded/dangerous per tool) | 🔍 In review | A-FORGE |
| `888_HOLD` escalation path with human veto | ✅ Shipped | A-FORGE |
| `ApprovalBoundary` with ticket store for held actions | ✅ Shipped | A-FORGE |
| arifOS `arif_judge_deliberate` → A-FORGE verdict routing | ⏳ Pending | arifOS + A-FORGE |
| Reversibility classification on all 17 MCP tools | ⏳ Pending | arifOS |

### Gate Criteria to Exit Phase 4
- [ ] Every `dangerous` tool requires 888_HOLD or explicit sovereign approval
- [ ] `arif_judge_deliberate` verdict is routed to A-FORGE before execution
- [ ] No forge action executes without a VAULT999 trace entry

---

## Federation MCP Topology (Corrected)

```
MCP Clients
    │
    ▼
arifOS MCP :8080 ─── arif_judge_deliberate (888) ─── APEX Prime (A2A verdict oracle)
    │                                                     port 3002
    ├── arif_sense_observe (111)
    ├── arif_evidence_fetch (222)
    ├── arif_mind_reason (333)
    ├── arif_memory_recall (555)
    ├── arif_heart_critique (666)
    ├── arif_gateway_connect (666g)
    ├── arif_ops_measure (777)
    ├── arif_stack_health_probe (777)
    ├── federation_audit (P3)
    ├── institutional_drift_check (777)
    ├── arif_forge_execute (010) ──────────────────────────► VAULT999
    ├── arif_vault_seal (999)
    └── arif_kernel_route (444)

GEOX MCP :8081 ─── geoscience + physics-9 tools
WEALTH MCP :8082 ─── 13 capital primitives × modes
WELL MCP :8083 ─── biological readiness tools

AAA A2A Gateway :3001 ─── Agent-to-Agent mesh (NOT MCP)
A-FORGE HTTP Bridge :7071 ─── TypeScript execution shell (NOT MCP)
```

**4 MCP servers only.** AAA (3001) is A2A, APEX Prime (3002) is A2A verdict oracle, A-FORGE (7071) is TypeScript HTTP bridge.

---

## Open Issues (Q2 Focus)

| Issue | Severity | Phase | Status |
|-------|----------|-------|--------|
| Session binding auto-bootstrap (env var session not created on startup) | HIGH | 2 | ✅ Fixed |
| WEALTH `wealth_entropy_risk` mode=emv fails with COMPUTATION_ERROR | MEDIUM | 1 | ⏳ Pending |
| WEALTH `boundary_governance` fails: No module named 'contracts' | MEDIUM | 1 | ⏳ Pending |
| A-FORGE container DNS fix (af-bridge → af-bridge-prod) | MEDIUM | 1 | ⏳ Pending |
| arifOS 17 live tools vs 13 canonical tool mismatch | MEDIUM | 1 | 🔍 In review |
| WEALTH 34 hidden aliases unverified | MEDIUM | 3 | ⏳ Pending |

---

## What NOT To Do (Non-Goals)

1. **Do not add new actuators** — forge/execute already exist. Govern them.
2. **Do not merge APEX into AAA** — Stateless oracle (APEX, port 3002) and stateful A2A gateway (AAA, port 3001) are ontologically opposite types.
3. **Do not route AAA through fastmcp.app** — Own-domain routing only (`*.arif-fazil.com/mcp`).
4. **Do not use VAULT999 as a secret store** — Append-only ledger, not a key vault.
5. **Do not commit without test pass** — Every fix requires relevant test validation.

---

*DITEMPA BUKAN DIBERI — Forged, Not Given*
*999 SEAL ALIVE — arifOS Forge Agent (Ω)*
