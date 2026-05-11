# arifOS — Roadmap: Next Horizon (180-Day)

> **Roadmap Name:** ARIFOS_NEXT_HORIZON_2026
> **Strategic Verdict:** APPROVED FOR PLANNING
> **Execution Verdict:** HOLD until repo contracts and schemas are frozen
> **First Move:** Create `FEDERATION_CONTRACT.md`, then make every repo obey it.
> **Seal:** DITEMPA BUKAN DIBERI

---

## North Star

> arifOS Federation vNext: a deterministic, evidence-bound, MCP-native governed intelligence stack where agents may reason, but only verified contracts may execute.

---

## Prime Rule

**Stop building more organs. Forge the contracts between organs.**

One repo, one authority. One contract, many implementations. One verdict chain, no hidden execution.

---

## The 10 Non-Negotiable Invariants

1. arifOS judges.
2. AAA identifies.
3. GEOX witnesses earth.
4. WEALTH witnesses capital.
5. A-FORGE executes only after verdict.
6. VAULT999 records.
7. ARIF may veto.
8. No agent self-authorizes.
9. No hidden irreversible action.
10. No evidence, no SEAL.

---

## Horizon 0 — Days 0–14: Canon Lock 🧊

**Goal:** Remove ambiguity before adding intelligence.

### arifOS Deliverables

| Deliverable | Output |
|-------------|--------|
| `FEDERATION_CONTRACT.md` | Defines organ boundaries, authority levels, handoff protocols |
| `/constitution/floors.yaml` | Machine-readable F1–F13 policy |
| `/constitution/invariants.yaml` | Runtime invariants (no self-approval, no hidden irreversible action) |
| `/schemas/verdict.schema.json` | Canonical SEAL / HOLD / VOID / PARTIAL object |
| `/schemas/evidence.schema.json` | Evidence witness object accepted by judge |
| `/schemas/trace.schema.json` | Trace, receipt, chain_id, actor_id schema |
| `/tests/golden/seal_cases.json` | Golden tests: every SEAL case |
| `/tests/golden/hold_cases.json` | Golden tests: every HOLD case |
| `/tests/golden/void_cases.json` | Golden tests: every VOID case |

### Gate
No new tools until contracts are frozen.

---

## Horizon 1 — Days 15–45: Security + Session Spine 🔐

**Goal:** Make AAA the hard boundary for identity and scope.

### arifOS Deliverables

| Deliverable | Output |
|-------------|--------|
| `judge.verify(payload)` → SEAL/HOLD/VOID | Deterministic verdict API |
| JSON Schema 2020-12 tool outputs | Every tool returns typed output |
| Evidence witness enforcement | Reject claims without witness object |
| Human authority preservation | F13 veto must never be callable by agent |

### Cross-Repo Coordination
- Consume `agent_card.schema.json` from AAA
- Consume `session.schema.json` from AAA
- Consume `delegation.schema.json` from AAA

---

## Horizon 2 — Days 46–90: Deterministic Judge ⚖️

**Goal:** Shift from LLM-evaluated governance to machine-checkable governance.

### arifOS Deliverables

| Deliverable | Output |
|-------------|--------|
| `/formal/z3_floor_checks.py` | Z3 / Python formal policy checks for F1–F13 |
| `/formal/ltl_trace_rules.md` | LTL trace rules for verdict chain validity |
| `judge.verify(payload)` hardened | Deterministic SEAL/HOLD/VOID with zero LLM in critical path |
| Golden test suite | arifOS must reject at least 20 known-bad cases deterministically |

### First Invariants to Prove

1. No irreversible execution without explicit human acknowledgement.
2. No SEAL without trace_id and evidence witness.
3. No domain claim without GEOX/WEALTH/WELL evidence where relevant.
4. No execution if actor scope does not include requested tool.
5. No agent may self-approve, self-seal, or claim F13 authority.
6. HOLD must be returned when evidence is incomplete.
7. VOID must be returned on schema mismatch or authority breach.

---

## Horizon 3 — Days 91–135: Semantic Federation 🌍💰

**Goal:** Make earth evidence and capital evidence interoperable.

### arifOS Deliverables

| Deliverable | Output |
|-------------|--------|
| `tri_witness.schema.json` | Cross-domain evidence aggregation schema |
| Shared semantic memory contract | arifOS coordinates GEOX + WEALTH evidence fusion |
| Causal reasoning integration | Consume causal analysis output before verdict |

### Cross-Domain Use Case
> "Given a subsurface uncertainty, produce a capital-risk witness without approving capital action."

Pipeline: GEOX detects uncertainty → arifOS requests evidence → WEALTH calculates EMV/downside/option value → arifOS judges → A-FORGE may only execute report generation → VAULT999 seals trace.

---

## Horizon 4 — Days 136–180: Self-Healing + Public Release 🛠️

**Goal:** Recovery agents may repair infrastructure, but never expand authority.

### arifOS Deliverables

| Deliverable | Output |
|-------------|--------|
| Auditor agent read-only mode | arifOS monitors self-healing actions |
| Recovery playbook review | arifOS must SEAL reversible recovery, HOLD irreversible |
| MCP registry readiness | Publish arifOS as MCP resource server |
| Release tag `vNext-Horizon-0` | All repos tagged |

---

## What to Build Next

Not another agent. Build the federation spine:

```
Identity → Evidence → Formal Verdict → Sandboxed Execution → Immutable Seal
```

## What to Avoid

- More overlapping dashboards.
- More untyped tools.
- More prompt-only governance.
- More agent autonomy language without execution contracts.
- More repo duplication.

## What Wins

- Deterministic checks.
- Typed schemas.
- Scoped authority.
- Evidence contracts.
- Cross-domain semantic memory.
- Causal reasoning.
- Human veto preserved.

---

*DITEMPA BUKAN DIBERI — Governance is forged, not given.*

*SEALED: 2026-05-10 | arifOS Constitutional Kernel — Next Horizon APPROVED FOR PLANNING*
