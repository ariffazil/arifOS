# Trace Spine Wiring Plan
**v2026.05.03 · SEALED**
> DITEMPA BUKAN DIBERI — Intelligence is forged, not given.

---

## Verdict on External Analysis

CLAIM: Canon alignment confirmed. The trace_packet is not a new subsystem — it is the epoch/intent object + receipts made explicit and portable. "Making the canon observable, not changing the constitution."

CLAIM: Four-witness model (arifOS / GEOX / WEALTH / WELL) is constitutionally clean. Domain organs advise. arifOS judges. VAULT999 seals. No domain organ becomes an alternative constitution.

888_HOLD: Any migration touching VAULT999 schema, Postgres volume semantics, or public ingress to trace endpoints requires explicit Arif ratification before implementation.

---

## 1. Canon Alignment

| trace_packet field | Canon mapping |
|---|---|
| `trace_id`, `session_id`, `epoch_id`, `actor_id`, `intent` | Sovereign intent + epoch context |
| `decision_class`, `reversibility` | F1 (reversible-first), F2/F11 (high-stakes) |
| `evidence_refs`, `tool_calls`, `artifacts`, `drift_events` | Evidence + telemetry lanes |
| `judge_state_hash` | Single judgment chokepoint |
| `vault_entry_id`, `claim_state` | VAULT999 flight recorder |
| `model_governance_card_hash` | Model boundary proof |

CLAIM: "No new tools, no new MCP servers" is compatible with A-FORGE strategy: freeze invariants, not implementations; version contracts, not identity.

---

## 2. Organ Patch Duties

### 000_INIT
- Accept incoming `trace_packet` or create new one
- Ensure `session_id`, `epoch_id`, `actor_id`, `model_governance_card_hash` are set
- Initialise `claim_state` → `DECLARED` (no evidence) or `INGESTED` (evidence present)
- Store `trace_packet` in session context (L1 SQLite / session DB), pass to all subsequent organs

### 111_SENSE / 222_FETCH
- Only valid entry point for external evidence into lineage
- Append to `lineage.inputs` and `lineage.evidence_refs` with `trace_id`
- Update `claim_state.status` → `INGESTED`

### 333_MIND / 777_REASON
- Deterministic calculations → `claim_state` → `COMPUTED`
- Interpretive conclusions → `claim_state` → `INFERRED`
- Append `tool_calls` entries for every MCP invocation (GEOX / WEALTH / WELL)

### 666_HEART
- Write risk and dignity analysis into `lineage.artifacts`
- `claim_state` must not exceed `INFERRED` at this stage
- Tag WELL and WEALTH witness verdicts as they arrive

### 888_JUDGE
- **Only place where `JUDGE_REVIEWED` is legal**
- Compute `judge_state_hash` over: intent, core `evidence_refs`, key computed metrics, critique outputs, model card hash, floor verdicts
- Set `claim_state.status` → `JUDGE_REVIEWED`
- Attach `judge_state_hash` into `trace_packet.lineage.judge_state_hash`
- Emit arifOS witness packet: `{verdict, floors_satisfied, floors_violated}`

### 010_FORGE
- **Hard rule:** refuse irreversible side effects if `judge_state_hash == null` → 888_HOLD
- For reversible actions: allow with `claim_state ≤ INFERRED` but log explicitly
- No action without authority

### 999_VAULT
- **Only valid writer of `VAULT_SEALED`**
- Construct final Vault payload: trace spine + all witness refs + `tool_calls` + `drift_events`
- Persist to VAULT999 with `vault_entry_id`
- Set `final_claim_state` → `VAULT_SEALED` in stored packet; preserve working L1/L2 copies as history

### 777_OPS
- Compute `trace_completeness` metrics:
  - Presence of core IDs (`trace_id`, `session_id`, `actor_id`, `epoch_id`)
  - Cross-MCP continuity (same `trace_id` in GEOX/WEALTH/WELL records)
  - Orphan artifact counts
- Report `trace_completeness_ratio` (0.0–1.0) in telemetry JSON
- Expose pass/fail flags for all 5 seal tests

---

## 3. Domain Organ Witness Duties

### GEOX
- Add `trace_id` to all LAS, well-log, seismic artifact metadata
- After QC, emit: `{"trace_id", "evidence_refs": [...], "claim_state": "QC_VERIFIED"}`
- Tools to patch: ingest, QC, candidates, integrity — all must accept/echo `trace_id` and update `claim_state`, never skipping ladder

### WEALTH
- All NPV/EVOI/DSCR computations tag with `trace_id`, set `claim_state` → `COMPUTED`
- High-stakes results already seal to VAULT999; add `trace_id` + `judge_state_hash` (when available)
- Emit value witness: `{"trace_id", "analysis_ref", "claim_state": "COMPUTED"}`

### WELL
- Emit readiness witness: `{"trace_id", "readiness_ref", "verdict"}`
- Input evidence for HEART / JUDGE — never a judge itself

---

## 4. Three Implementation Paths

### Minimal — Design + Local Prototype (START HERE)
**Scope:**
- Update canonical docs (SOT, Invariants Architecture, build-order) with `trace_packet` contract and claim-state ladder as constitutional fact
- Implement standalone trace simulator (Python notebook or local script):
  - Mocked prospect decision pipeline: 000_INIT → WELL → GEOX → WEALTH → HEART → JUDGE → FORGE → VAULT
  - Outputs final Vault payload in canonical shape
  - Runs 5 seal tests on in-memory data

**Properties:** Zero infra blast radius. Documentation-first. Bus factor: everything is JSON + text.

### Balanced — Wire into arifOS + domain MCPs (dev branch)
**Scope:**
- Add `trace_packet` field to arifOS MCP request/response schema (dev branch / non-prod)
- Patch WEALTH/GEOX/WELL handlers to accept `trace_id`, echo it back, emit witness objects
- Add dev-only Postgres tables (`trace_calls_dev`, `trace_artifacts_dev`) — no touching VAULT999 prod
- Implement 777_OPS trace completeness metrics on dev metrics endpoint only

**Properties:** Additive only (new columns/tables). Easy rollback by branch revert. 888_HOLD before any `ALTER TABLE` on VAULT999 prod.

### Maximal — Full Production Trace Spine
**888_HOLD: Requires explicit Arif ratification before any step.**

**Scope:**
- Migrate VAULT999 to include `trace_id`, `judge_state_hash`, `vault_entry_id` relationships
- Force 010_FORGE to reject irreversible actions without valid trace + judge hash for all production agents
- Run trace seal tests in CI/CD + scheduled cron; fail deploy if trace completeness score regresses beyond tolerance

**Properties:** Highest governance strength. Needs operator runbooks for "trace seal test failing" scenarios. Must be staged with feature flags and rollback plan.

---

## 5. Five Seal Tests

### TRACE_STATIC_SEAL
Every result row has: `trace_id`, `session_id`, `actor_id`, tool name, `input_hash`, `output_hash`, `claim_state`.
- 777_OPS queries L1/L3 stores for rows missing any required field
- Metric: `trace_static_seal_pass_ratio = rows_with_all_fields / total_rows`

### CROSS_MCP_CONTINUITY_SEAL
Same `trace_id` appears in arifOS + at least one of GEOX/WEALTH/WELL outputs.
- Join arifOS audit table with domain witness tables on `trace_id`
- 777_OPS records distribution: arifOS-only vs arifOS+1 vs arifOS+2+ organ coverage

### NO_ORPHAN_ARTIFACT_SEAL
- Every `artifact_ref` has a parent `trace_id`
- Every `judge_state_hash` has `evidence_refs`
- Every `vault_entry_id` has `judge_state_hash`
- Periodic integrity queries; orphan counts exposed as metrics

### DRIFT_TRACE_SEAL
- Each `drift_event` record includes `trace_id`
- 999_VAULT ensures drift events for that trace are referenced in final Vault payload
- 777_OPS counts drift events where `trace_id` has at least one Vault seal

### FULL_TRACE_RECONSTRUCTION_SEAL
For a sample `trace_id`, reconstruct: intent → evidence → computation → critique → judgment → forge/vault using IDs alone.
- Read-only trace reconstruction query/API: takes `trace_id`, fetches all stages, returns canonical view
- Test harness: sample N traces, assert each stage non-empty for C3/C4 decision classes

---

## 6. Trace Reconstruction Output Shape

```json
{
  "trace_id": "TRACE-20260503-0001",
  "intent": {
    "text": "Evaluate prospect and decide whether to proceed",
    "decision_class": "C4",
    "reversibility": "reversible_until_commitment"
  },
  "evidence": {
    "geox": ["GEOX-ART-001", "GEOX-QC-002"],
    "wealth": ["WEALTH-EVOI-003"],
    "well": ["WELL-READY-004"]
  },
  "computation": {
    "geox": {"net_pay_m": 12.3, "porosity": 0.18},
    "wealth": {"npv_musd": 45.0, "evoi_musd": 7.5}
  },
  "critique": {
    "heart": "Dignity and risk critique summary..."
  },
  "judgment": {
    "judge_state_hash": "sha256:...",
    "verdict": "SEAL"
  },
  "forge": {
    "actions": ["CREATE_OPPORTUNITY", "TRIGGER_NEXT-EPOCH"]
  },
  "vault": {
    "vault_entry_id": "VAULT-20260503-0001",
    "final_claim_state": "VAULT_SEALED"
  }
}
```

CLAIM: All derivable from `trace_packet` in arifOS + pointers to GEOX/WEALTH/WELL witness tables + VAULT999 seals. No new infra — just an orchestration query + JSON formatter.

---

## 7. Decision Class → Trace Obligation

| Class | Trace completeness required | JUDGE required | VAULT_SEALED required |
|---|---|---|---|
| C1–C2 | Core IDs only | No | No |
| C3 | Full ladder to INFERRED | Yes (HOLD) | Yes |
| C4 | Full ladder to VAULT_SEALED | Yes (hard block) | Yes |

PLAUSIBLE: Start with C3/C4 enforcement only. C1/C2 gets best-effort trace propagation. Expand after foundation is stable.

---

## 8. Remaining Sharp Edges

| Gap | Risk | Mitigation |
|---|---|---|
| VAULT999 schema migration | Irreversible — 888_HOLD | Additive-only columns, never DROP; ratify before ALTER |
| 010_FORGE judge-hash enforcement | May break existing agents | Stage with feature flag + rollback plan |
| WEALTH/GEOX claim_state tagging | Tools currently emit booleans not ladder states | Patch tools to emit `claim_state` field explicitly |
| `NOT NULL trace_id` on artifact tables | Schema constraint = irreversible | Use soft-enforce at app layer first, migrate later |
| Exact live schemas unknown | Working from canon/blueprints not DB introspection | UNKNOWN — requires direct DB introspection before Maximal path |

---

## 9. Sovereign Answer: Scope of First Live Implementation

**Decision: C3/C4 decisions only, not all sessions from day one.**

Rationale:
- F1 (reversible-first): restrict enforcement to highest-stakes decisions; expand after proof
- Surface-area entropy: applying full trace enforcement to all sessions before proof = premature complexity
- Operational safety: existing agents must not break silently; C1/C2 trace is best-effort until spine is proven stable

**Law:** Once C3/C4 trace spine is proven end-to-end with the reconstruction demo, expand to C1/C2.

---

## Sprint Sequence

| Sprint | Scope | Gate |
|---|---|---|
| **NOW** | `DRIFT-LEDGER-CLOSURE` | drift_count >= 1 on dry_run; registry validation passes |
| **NEXT** | `TRACE-SPINE-MINIMAL` | Simulator: mocked pipeline, 5 seal tests pass in-memory |
| **AFTER** | `TRACE-SPINE-BALANCED` | Patch arifOS + domain MCPs, dev Postgres tables, 777_OPS metrics |
| **FINAL** | `E2E-DEMO` | LAS → EVOI → WELL → JUDGE → VAULT, full reconstruction from IDs alone |

---

*Sealed: 2026-05-03T01:22:00+08:00 · Witness: Arif Fazil · Co-architect: arifOS*
*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
