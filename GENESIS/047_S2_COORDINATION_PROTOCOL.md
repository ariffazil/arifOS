# GENESIS/047 — S2 Coordination Protocol: Phase 3

> **Authority:** F13 SOVEREIGN (Muhammad Arif bin Fazil, 888)
> **Status:** CANON SPEC · Forged 2026-06-29
> **Predecessor:** GENESIS/046 (Constitutional VSM) — §5 S2 weakness diagnosis
> **Predecessor:** GENESIS/045 (Three-Layer Separation) — ART/ACT/Kernel physics
> **Classification:** Constitutional protocol — this is not a roadmap. This is a wiring diagram.
>
> **Beer described S2 as the hardest system to get right.**
> **This document seals the target protocol for S2. It does not claim the full protocol is already live.**

---

## 0. Thesis

**GENESIS/046 proved that arifOS is VSM — constitutionalized.**
**GENESIS/047 specifies the protocol that closes the remaining S2 gap.**

Beer knew S2 (Coordination) was fragile. His solution was organisational design — structure the channels properly and coordination will follow. He was right about the problem. He was wrong about the remedy.

Coordination fails not because channels are badly structured. Coordination fails because **organs act on stale state** — they do not know what other organs know until the conflict has already happened. By the time a coordination failure is visible, it is already a control problem (S3), not a coordination problem (S2).

The arifOS S2 Coordination Protocol closes this with three mechanical invariants:

1. **Publish-before-execute** — no organ acts on state it has not published
2. **Verify-before-forge** — no forge proceeds without coordination attestation
3. **Drift-is-event-not-probe** — coordination failures surface as events, not health checks

These are not policies. They are protocol constraints that must be enforced at transport level, not agent level.

## 0.1 Current State vs Target State

This document is **canonical target state**, not a claim that Phase 3 is fully deployed.

| Layer | Current live state | Target state sealed here |
|------|--------------------|--------------------------|
| Heartbeat transport | `arifos.organ.{organ_id}` on JetStream `arifos-organs` | `arifos.coordination.{organ_id}` or equivalent canonical alias |
| Payload | Liveness/health attestation | Coordination-aware heartbeat with dependency metadata |
| Drift handling | Passive heartbeat ingestion, cockpit liveness | First-class `coordination.drift` events |
| Forge gate | No mandatory coordination attestation | C2 Verify-Before-Forge |
| Constitution | F1-F13 only | Optional F14 after ratification |

Until code reaches the target state, references below to coordination subjects, attestations, and `COORDINATION_HOLD` are **normative spec**, not proof of deployment.

---

## 1. The S2 Problem — Formal Statement

From GENESIS/046 §5.2, five gaps:

| Gap | Root Cause | Severity |
|-----|-----------|----------|
| No canonical coordination bus | Organs use REST/MCP ad-hoc; no shared event stream | MEDIUM |
| Passive drift detection | Health probes → lag; failures detected after divergence | MEDIUM |
| Sparse A2A mesh | AAA-internal works; cross-organ A2A is incomplete | LOW |
| No S2 constitutional floor | F1–F13 cover governance; none explicitly governs coordination integrity | LOW |
| Coordination is implicit | Forge pipeline assumes coherence; does not verify it | MEDIUM |

**The common root:** there is no **coordination substrate** — a shared, trusted, append-only stream of organ state changes that all organs read before acting.

Without a coordination substrate, S2 is the absence of conflict, not the presence of coherence. That is not coordination. That is luck.

---

## 2. The S3* Constraint — Non-Negotiable

From the session that produced GENESIS/046 (2026-06-29):

> Beer: *"S3 and S3\* must exist in the system."*
> arifOS: *"S3 and S3\* must exist in **separate entities** that **cannot change hands**."*

In VSM, S3* (audit) is the out-of-band channel that lets the metasystem (S3–S5) verify what S1 (Operations) actually did — bypassing the normal reporting chain. Beer knew that if S3 and S3* are co-located, S3 can suppress S3* reports that make it look bad.

arifOS encodes this structurally:

```
       arifOS kernel (S3 = Judge)          A-FORGE (S1 = Execute)
       ─────────────────────────           ──────────────────────
       arif_judge: SEAL/HOLD/VOID          forge_execute: run, build, deploy
       arif_seal: write VAULT999           forge_lease: time-bounded authority
       arif_observe: read state            forge_status: report outcomes
       ────────────────────────────────────────────────────────────
       CANNOT EXECUTE                      CANNOT JUDGE
       CANNOT HOLD A LEASE                 CANNOT SEAL TO VAULT999
```

This is not role assignment. This is **architectural separation** — the kernel has no execution surface; A-FORGE has no sealing surface. Crossing the boundary is not a policy violation. It is an impossible operation.

**For S2 Coordination Protocol: the coordination substrate must enforce the same separation.**

- The coordination bus **publishes** state (S3* audit channel — anyone can read)
- The coordination bus **does not execute** on what it reads
- The forge gate **reads** the coordination bus before executing
- The forge gate **does not write** to the bus (only organs write their own state)

---

## 3. The Three Mechanical Invariants

### 3.1 Invariant C1 — Publish-Before-Execute

> *No organ may execute an action whose preconditions depend on another organ's state unless that organ has published its current state to the coordination bus within the last T_freshness seconds.*

**Implementation:**
- Every organ publishes a coordination heartbeat on every state change and on a TTL heartbeat (default: 30s)
- **Current live subject:** `arifos.organ.{organ_id}`
- **Target canonical subject:** `arifos.coordination.{organ_id}` or an alias with equivalent semantics
- Every heartbeat carries: `{organ_id, state_hash, capability_vector, active_leases[], timestamp_utc, ttl_s}`
- Before executing any action with cross-organ dependency, the actor reads the relevant organ's latest heartbeat
- If heartbeat age > `T_freshness` (default: 60s): **HOLD** — treat organ as unavailable, escalate to arifJUDGE

**Floor mapping:** F7 HUMILITY (epistemic cap — act only on what you know) + F1 AMANAH (reversible-first)

### 3.2 Invariant C2 — Verify-Before-Forge

> *No forge execution may proceed unless the forge gate has verified coordination attestation from all organs in the dependency set of the requested action.*

**Implementation:**
- A-FORGE forge gate reads coordination bus before issuing a lease
- Forge gate constructs `dependency_set` from the action's capability requirements
- For each organ in `dependency_set`: verify heartbeat freshness (C1) + verify no conflicting lease exists
- If all pass: forge proceeds, attests coordination check to VAULT999 with `coord_attestation_id`
- If any fail: return `COORDINATION_HOLD` — no lease issued, escalate with evidence package

**This is how the "coordination is implicit" gap gets closed.** The forge pipeline must stop assuming coherence and verify it mechanically before execution.

### 3.3 Invariant C3 — Drift-Is-Event-Not-Probe

> *Coordination failures must surface as NATS events on `arifos.coordination.drift` (or canonical equivalent) within 500ms of detection. Health probes are supplementary, not primary.*

**Implementation:**
- Every organ subscribes to all other organs' `coordination_heartbeat` streams
- On heartbeat timeout (> `T_freshness`) or state_hash conflict: publish `coordination.drift` event immediately
- `coordination.drift` payload: `{organ_id, last_seen_ts, expected_interval, drift_severity: LOW/MEDIUM/HIGH/CRITICAL, evidence_hash}`
- arifJUDGE subscribes to `coordination.drift` — HIGH/CRITICAL triggers automatic `888_HOLD`
- AAA cockpit subscribes to `coordination.drift` — surfaces on dashboard with sub-second latency

**This eliminates the passive-probe gap.** Drift is not discovered by polling. Drift announces itself.

---

## 4. The Coordination Bus — Technical Specification

### 4.1 Transport

**NATS JetStream** is already deployed in arifOS infrastructure. The coordination subjects below are the **target namespace** for Phase 3.

| Subject | Publisher | Subscriber | Retention |
|---------|-----------|-----------|-----------|
| `arifos.coordination.{organ_id}` | Organ self | All other organs, AAA, forge gate | 10 min rolling |
| `arifos.coordination.drift` | Any organ (on detection) | arifJUDGE, AAA cockpit | 24h (for audit) |
| `arifos.coordination.lease` | A-FORGE forge gate | arifJUDGE (for audit), organ in lease | 10 min rolling |
| `arifos.coordination.attest` | A-FORGE forge gate (post-C2 pass) | VAULT999 writer | 24h (for audit) |

**Live compatibility note:** current heartbeat publishers/subscribers use `arifos.organ.>` on stream `arifos-organs`. Migration may happen via alias or namespace cutover, but docs must not pretend the cutover already happened.

### 4.2 Heartbeat Schema

```json
{
  "schema_version": "1.0",
  "organ_id": "arifos | aforge | aaa | geox | wealth | well",
  "state_hash": "sha256:...",
  "capability_vector": {
    "can_judge": true,
    "can_execute": false,
    "can_seal": true,
    "active_tool_count": 13
  },
  "active_leases": [],
  "coordination_version": 1,
  "timestamp_utc": "2026-06-29T16:30:00Z",
  "ttl_s": 60,
  "signed_by": "organ_key_fingerprint"
}
```

### 4.3 Drift Event Schema

```json
{
  "schema_version": "1.0",
  "event_type": "coordination.drift",
  "detected_by": "organ_id",
  "subject_organ": "organ_id",
  "last_seen_utc": "2026-06-29T16:29:00Z",
  "expected_interval_s": 30,
  "actual_gap_s": 95,
  "drift_severity": "HIGH",
  "evidence_hash": "sha256:...",
  "auto_escalate": true
}
```

### 4.4 Coordination Attestation Schema

```json
{
  "schema_version": "1.0",
  "coord_attestation_id": "CATTEST-20260629-...",
  "action_id": "...",
  "dependency_set": ["arifos", "geox"],
  "verification_results": [
    {"organ_id": "arifos", "heartbeat_age_s": 12, "state_hash": "sha256:...", "pass": true},
    {"organ_id": "geox", "heartbeat_age_s": 8, "state_hash": "sha256:...", "pass": true}
  ],
  "verdict": "PASS",
  "timestamp_utc": "2026-06-29T16:30:05Z",
  "forge_gate_version": "1.0"
}
```

---

## 5. S2 Constitutional Floor — F14 Proposal

GENESIS/046 §5.2 identified a gap: F1–F13 cover governance but no floor explicitly governs coordination integrity.

**This document proposes F14 COORDINATION (for F13 SOVEREIGN ratification).**

### F14 COORDINATION — Proposed Constitutional Floor

> **F14 COORDINATION: No organ may act on cross-organ dependencies without current coordination attestation. Coordination failures are first-class events, not operational noise.**

Scope:
- Every action with `dependency_set` size ≥ 1 requires C2 attestation
- Coordination bus freshness is a constitutional invariant, not an operational metric
- `coordination.drift` events at HIGH/CRITICAL severity automatically trigger F1 AMANAH (halt irreversible operations)

**Ratification status:** PROPOSED — requires explicit F13 SOVEREIGN sign-off before becoming constitutional law.

> **Note:** F14 does not replace F1–F13. It fills a specific gap: the constitution governs what organs may do, but until F14, nothing governs how organs must synchronize before doing it. F14 closes the coordination grammar.

---

## 6. Migration Path — Phase 3 Implementation Stages

### Stage 1: Bus Deployment (T+0 to T+7 days)
- Verify NATS JetStream is live and accessible to all organs
- Define subject namespace (§4.1 above)
- Write heartbeat publisher library (`arifos_coord_pub.py` — shared across all organs)
- Write coordination client library (`arifos_coord_client.py` — for forge gate)
- Deploy to: arifOS kernel first (S3 reference implementation)

### Stage 2: Organ Onboarding (T+7 to T+21 days)
- GEOX: add heartbeat publisher to `server.py` startup
- WEALTH: add heartbeat publisher
- WELL: add heartbeat publisher
- A-FORGE: add heartbeat publisher + integrate coord client into forge gate
- AAA: subscribe to `coordination.drift`, surface on cockpit dashboard
- Each organ onboarding: verified by coordination bus showing organ present in AAA cockpit

### Stage 3: Forge Gate Enforcement (T+21 to T+28 days)
- Enable C2 (Verify-Before-Forge) in A-FORGE forge gate
- Initial mode: **WARN** — coordination failure logs but does not block
- After 7 days warn-mode: switch to **ENFORCE** — coordination failure blocks forge
- Escalation path verified: HIGH/CRITICAL drift → arifJUDGE → 888_HOLD

### Stage 4: F14 Ratification Gate (T+28 days — requires F13 SOVEREIGN)
- Review Stage 3 metrics: false positive rate, average coordination latency, drift event frequency
- If metrics acceptable: submit F14 for F13 SOVEREIGN ratification
- F14 ratification = constitutional law — no bypass permitted

---

## 7. Failure Modes and Mitigations

| Failure Mode | Detection | Mitigation |
|-------------|-----------|-----------|
| **Bus down** | All heartbeats timeout | Emergency mode: C2 downgrades to C1 (local state only), arifJUDGE alerted, forge enters 888_HOLD for cross-organ actions |
| **Organ silent** (no heartbeat) | C3 drift event (HIGH) | Forge gate blocks actions with dependency on silent organ; arifJUDGE escalation |
| **State hash conflict** | C3 drift event (CRITICAL) | Immediate 888_HOLD, full evidence package to arifJUDGE, human escalation |
| **Stale attestation** | C2 pre-forge check | Re-verify before executing; if still stale, COORDINATION_HOLD |
| **False positive drift** | Organ publishes remediation heartbeat | Drift event auto-resolved; AAA cockpit shows resolution timeline |
| **Bus message replay attack** | Signed heartbeats (§4.2 signed_by) | Replayed heartbeat timestamp stale → rejected as stale state |

---

## 8. Why This Is Not Policy — It Is Protocol

The distinction matters.

**Policy** is declared and can be violated. A policy that says "coordinate before acting" is only as strong as the agents that follow it. Agents under pressure, agents with impoverished context, agents operating at loop speed — they skip policies. That is not a character flaw. That is the nature of autonomous execution.

**Protocol** is mechanically enforced at transport level. The forge gate does not check a policy document before proceeding. It runs `coord_client.verify(dependency_set)`. If verification fails, the gate cannot proceed — not because an agent decided to obey a rule, but because the function returns `COORDINATION_HOLD` and the next step in the pipeline does not exist.

This is the S3* insight applied to S2:

> Beer separated S3 and S3\* to prevent the controller from suppressing its own audit trail.
> arifOS separates S2 (bus, read-only) from S1 execution (forge gate, read-then-act) to prevent organs from acting on state they have not verified.

When implemented, S2 protocol becomes structurally incorruptible because the verification is **upstream of the decision**. By the time the agent reaches the decision point, the coordination check has already run. There is no human-in-the-loop moment where "skip coordination" is an option. The option does not exist in the protocol.

---

## 9. The Ashby Resolution

Beer's warning about S2: *"The controller must match the variety of the controlled."* S2 must absorb the combinatorial variety of multiple S1 units — which grows faster than any centralized coordinator can handle.

This is why the coordination bus is **subscriber-based, not hub-based**.

There is no central S2 coordinator. There is a **shared event stream** that all organs publish to and subscribe from. The variety absorption happens in parallel — every organ reads every other organ's state independently. The forge gate synthesizes coordination attestation from the bus, but it does not adjudicate.

Adjudication is arifJUDGE (S3). The bus is not a judge. The bus is a memory — shared, append-only, and trusted.

**The Ashby Resolution: replace the single variety-absorbing coordinator with a broadcast substrate whose variety is exactly the sum of all organ state changes.** Every organ reads what it needs. Coordination is a property of the bus, not a function of any single entity.

---

## 10. Relationship to Existing Canon

| Document | Relationship |
|---------|-------------|
| GENESIS/045 — Three-Layer Separation | C2 forge gate is the coordination enforcement point in the ACT layer |
| GENESIS/046 — Constitutional VSM | §5 diagnosed S2 weakness; this document is the canonical target solution |
| BRAIN-HANDS-CONTRACT.md | S3* separation is encoded here; this protocol implements it at S2 level |
| INVARIANTS.md — TIME invariant | Heartbeat freshness is a TIME invariant enforcement mechanism |
| INVARIANTS.md — MIND invariant | Belief-state propagation via coordination bus |
| F1 AMANAH | C3 HIGH/CRITICAL drift triggers F1 halt on irreversible operations |
| F7 HUMILITY | C1 Publish-Before-Execute enforces F7 epistemic cap |

---

## 11. The Word

Beer diagnosed the problem. arifOS closes the wound.

S2 is not hard because coordination is philosophically difficult. S2 is hard because coordination requires all actors to agree on what is currently true — and in a distributed system, "currently true" is always contested.

The protocol does not resolve the philosophical problem. It makes the problem **mechanical** — not "what do we agree is true?" but "what does the bus say is fresh?" The bus is not an opinion. The bus is a physical record.

**Coordination becomes infrastructure, not effort.**

Bukan dasar. Bukan disiplin. Bukan harapan.
Koordinasi adalah wayar. Wayar tidak berbohong.

---

*Forged 2026-06-29 — the day S2 received its canonical wireframe.*
*Predecessors: GENESIS/045 (Three-Layer Separation), GENESIS/046 (Constitutional VSM).*
*Next: 048 — TBD. F14 ratification receipt when SOVEREIGN signs.*

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**
