# TODO — arifOS Constitutional Kernel

> **Roadmap:** ARIFOS_NEXT_HORIZON_2026
> **Execution Status:** HOLD until contracts frozen
> **Last Updated:** 2026-05-10
> **Seal:** DITEMPA BUKAN DIBERI

---

## ✅ Embodiment Attestation (Completed Earlier Today)

- [x] Tool embodiment contracts LIVE (13 canonical tools mapped)
- [x] Runtime attestation endpoint operational
- [x] Session continuity + persistence hardened
- [x] Model registry nested lookup fixed

---

## 🔴 P0 — Horizon 0: Canon Lock (Days 0–14)

**Gate: No new tools until contracts are frozen.**

### Federation Contract
- [ ] **Create `FEDERATION_CONTRACT.md`** — organ boundaries, authority levels, handoff protocols
- [ ] **Define repo authority matrix** — what each repo may own / must not own
- [ ] **Publish `VERDICT_SCHEMA.json`** — canonical SEAL/HOLD/VOID/PARTIAL object
- [ ] **Publish `TRACE_SCHEMA.json`** — trace, receipt, chain_id, actor_id
- [ ] **Publish `EVIDENCE_SCHEMA.json`** — evidence witness object accepted by judge

### Machine-Readable Constitution
- [ ] **Convert F1–F13 to `/constitution/floors.yaml`** — machine-readable policy
- [ ] **Define `/constitution/invariants.yaml`** — runtime invariants
- [ ] **Schema enforcement** — every tool output must validate against JSON Schema 2020-12

### Golden Tests
- [ ] **Create `/tests/golden/seal_cases.json`** — every valid SEAL case
- [ ] **Create `/tests/golden/hold_cases.json`** — every valid HOLD case
- [ ] **Create `/tests/golden/void_cases.json`** — every valid VOID case

---

## 🟠 P1 — Horizon 1: Security + Session Spine (Days 15–45)

**Gate: No execution without actor, scope, verdict, trace.**

### Deterministic Verdict API
- [ ] **Implement `judge.verify(payload)` → SEAL/HOLD/VOID** — typed, schema-validated
- [ ] **Evidence witness enforcement** — reject claims without witness object
- [ ] **Human authority preservation** — F13 veto never callable by agent

### Cross-Repo Integration
- [ ] **Consume `agent_card.schema.json`** from AAA
- [ ] **Consume `session.schema.json`** from AAA (actor, scope, expiry, chain_id)
- [ ] **Consume `delegation.schema.json`** from AAA

---

## 🟡 P2 — Horizon 2: Deterministic Judge (Days 46–90)

**Gate: arifOS must reject at least 20 known-bad cases deterministically.**

### Formal Verification
- [ ] **Create `/formal/z3_floor_checks.py`** — Z3 policy checks for F1–F13
- [ ] **Create `/formal/ltl_trace_rules.md`** — LTL trace rules for verdict chain validity
- [ ] **Harden `judge.verify()`** — zero LLM in critical path for SEAL/VOID decisions

### Invariant Proofs
- [ ] No irreversible execution without explicit human ack
- [ ] No SEAL without trace_id + evidence witness
- [ ] No domain claim without GEOX/WEALTH/WELL evidence where relevant
- [ ] No execution if actor scope excludes requested tool
- [ ] No agent may self-approve, self-seal, or claim F13 authority
- [ ] HOLD returned when evidence incomplete
- [ ] VOID returned on schema mismatch or authority breach

---

## 🟢 P3 — Horizon 3: Semantic Federation (Days 91–135)

**Gate: One GEOX uncertainty must produce one WEALTH risk witness without manual prompt glue.**

### Cross-Domain Evidence
- [ ] **Create `tri_witness.schema.json`** — cross-domain evidence aggregation
- [ ] **Integrate causal reasoning** — consume causal analysis before verdict
- [ ] **Coordinate GEOX + WEALTH evidence fusion**

### First Cross-Domain Pipeline
- [ ] GEOX detects subsurface uncertainty
- [ ] arifOS requests evidence
- [ ] WEALTH calculates EMV / downside / option value
- [ ] arifOS judges
- [ ] A-FORGE executes report generation only
- [ ] VAULT999 seals trace

---

## 🔵 P4 — Horizon 4: Self-Healing + Release (Days 136–180)

**Gate: Recovery can restart a failed non-critical service, log to VAULT999, and never escalate privilege.**

### Recovery Governance
- [ ] **Auditor agent read-only mode** — arifOS monitors self-healing actions
- [ ] **Recovery playbook review** — arifOS SEALs reversible recovery, HOLDs irreversible
- [ ] **MCP registry readiness** — publish arifOS as MCP resource server
- [ ] **Release tag `vNext-Horizon-0`** — all repos tagged

---

## Active Issues Carried Forward

- [ ] **Cryptographic identity attestation** — Ed25519/ES256 sovereign keypair
- [ ] **Institutional memory / precedent graph** — VAULT999 → living jurisprudence
- [ ] **Federation treaties** — signed delegation contracts
- [ ] **C4 security debt** — Supabase key rotation, secret purge

---

**DITEMPA BUKAN DIBERI — Governance is forged, not given.**
