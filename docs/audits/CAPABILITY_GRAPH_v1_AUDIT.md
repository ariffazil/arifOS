# CAPABILITY_GRAPH_v1 — Self-Audit Report

> **SOT-MANIFEST**
> owner: Arif
> last_verified: 2026-06-24
> valid_from: 2026-06-24
> valid_until: 2026-07-24
> confidence: high
> scope: /root/arifOS/docs/architecture/CAPABILITY_GRAPH_v1.md
> epistemic_status: AUDIT_VERDICT

---

## 1. Premise Correction Accepted

**Arif (F13) issued a correction:**

> arifOS is not yet an AGI substrate. It is a governance kernel.
> To become a real AGI substrate, it needs the missing runtime body around the constitutional brain.

This audit evaluates the CAPABILITY_GRAPH_v1 spec against that corrected premise.

**Verdict:** The spec is materially sound, but **scoped too narrowly**. It is not a full AGI-substrate specification. It is the specification for **Layer 4 (Action Bus) + Layer 1 (Identity/Authority)** of the larger substrate. It must be explicitly repositioned, and the missing layers must be specified separately.

---

## 2. Mapping the Spec Against the Six Missing Layers

### 2.1 Layer 1 — Embodied Memory (M0-M3)

| Sub-layer | Coverage in CAPABILITY_GRAPH_v1 | Verdict |
|-----------|----------------------------------|---------|
| M0 session memory | `session_token`, `session_geometry`, `verdict_geometry` | Partial |
| M1 user/operator memory | `allowed_actor_ids`, `forbidden_actor_ids` | Partial |
| M2 project/world model memory | Not addressed | Missing |
| M3 constitutional precedent memory | VAULT999 receipts mentioned, but not queryable precedent graph | Partial |

**Finding:** The spec treats memory as **session-bound authority state**, not as **structured, queryable, precedent-bearing memory**. There is no `precedent_id`, no `case_pattern`, no `analogical_lookup` mechanism. The kernel cannot yet ask: *"Have we seen this pattern before? What did we decide?"*

---

### 2.2 Layer 2 — Real Action Bus

| Required Component | Coverage | Verdict |
|--------------------|----------|---------|
| `authority_check` | `authority.tier`, `min_ceiling`, `allowed_actor_ids` | Strong |
| `blast_radius_check` | Implied by `reversibility.class` and `ack_required` | Partial |
| `reversibility_check` | `reversibility.class` | Strong |
| `evidence_check` | Not explicitly modeled | Missing |
| `human_dignity_check` | `witnesses.human`, `forbidden_actor_ids` | Partial |
| `rollback_plan` | Not addressed | Missing |

**Finding:** The action bus is the strongest part of the spec. It defines tool leases implicitly through `session_token` + `CapabilityNode`. But it lacks explicit **evidence requirements** and **rollback planning**. A high-impact action should carry a `rollback_plan_id` before execution.

---

### 2.3 Layer 3 — Persistent Identity and Authority

| Required Component | Coverage | Verdict |
|--------------------|----------|---------|
| `ACTOR_ID` | `actor_id`, `registered_by`, `allowed_actor_ids` | Strong |
| `ROLE` | `authority.tier`, `min_ceiling` | Partial |
| `AUTHORITY_SCOPE` | `geometry` fields + `modes` | Partial |
| `LEASE_DURATION` | `session_token` expiry implied, not explicit | Partial |
| `PERMITTED_ACTIONS` | `allowed_sessions`, `modes` | Partial |
| `FORBIDDEN_ACTIONS` | `forbidden_actor_ids` | Partial |
| `REVOCATION_PATH` | Not addressed | Missing |

**Finding:** Identity is well-started but incomplete. There is no explicit `lease_id`, `lease_expiry`, or `revoke` path. The `arif_surface_register` tool can approve, but there is no `arif_surface_revoke` or `arif_lease_revoke` tool.

---

### 2.4 Layer 4 — Learning Loop

| Required Component | Coverage | Verdict |
|--------------------|----------|---------|
| `observe outcome` | VAULT999 receipts | Partial |
| `compare expected vs actual` | Not addressed | Missing |
| `detect error` | `arif_self_correct` | Partial |
| `update local policy` | Not addressed | Missing |
| `store precedent` | Not addressed | Missing |
| `escalate if constitutional change needed` | Not addressed | Missing |

**Finding:** `arif_self_correct` is a self-correction gate, not a learning loop. There is no mechanism to update policy based on outcomes, or to promote/demote a case to constitutional precedent. Bounded learning is missing.

---

### 2.5 Layer 5 — World Model with Uncertainty

| Required Component | Coverage | Verdict |
|--------------------|----------|---------|
| `facts` | Not addressed | Missing |
| `beliefs` / confidence | Not addressed | Missing |
| `unknowns` | Not addressed | Missing |
| `risks` | Implied by `reversibility.class` | Partial |
| `actors` | `organ`, `actor_id` | Partial |
| `resources` | Not addressed | Missing |
| `time` / `jurisdictions` | Not addressed | Missing |
| `domain organs (GEOX/WEALTH/WELL)` | Listed as organ owners | Partial |

**Finding:** The spec knows *which organ* owns a tool, but it does not model the world state those organs represent. A mining decision cannot yet be evaluated as geology + capital + law + ecology + dignity + time. The world model is absent.

---

### 2.6 Layer 6 — Refusal Engine with Teeth

| Required Component | Coverage | Verdict |
|--------------------|----------|---------|
| `floor_violation → lock` | Implied by verdict loop | Partial |
| `authority_missing → deny` | `authority.tier`, `min_ceiling` | Strong |
| `irreversible + no human confirmation → 888_HOLD` | `ack_required`, `witnesses.human` | Strong |
| `human_dignity_risk → escalate` | `forbidden_actor_ids` only | Partial |
| `low confidence + high blast_radius → no execution` | Not addressed | Missing |

**Finding:** Refusal is the second-strongest part. `KERNEL_DENY` envelope is good. But the spec does not model **confidence × blast_radius** as a refusal condition. It also does not define a dignity-risk classification beyond actor allowlists.

---

## 3. Critical Gaps Summary

| # | Gap | Risk if ignored |
|---|-----|-----------------|
| 1 | No precedent memory (M3) | Kernel re-judges every case; cannot stabilize |
| 2 | No evidence requirements per action | Model can petition without grounding |
| 3 | No rollback plan enforcement | High-impact actions become irreversible by default |
| 4 | No lease revocation path | Compromised sessions cannot be killed cleanly |
| 5 | No bounded learning loop | System cannot adapt from outcomes |
| 6 | No world model / uncertainty registry | Cannot synthesize multi-domain reality |
| 7 | No confidence × blast_radius refusal | Overconfident low-evidence actions slip through |

---

## 4. What the Spec Actually Is

The CAPABILITY_GRAPH_v1 spec is correctly described as:

> **The canonical syscall membrane for MCP tools.**

It governs:
- Which tools exist.
- Who can invoke them.
- What verdict loop is required.
- How refusal is expressed.

It does **not** govern:
- What the system knows.
- How it learns.
- How it models the world.
- How it remembers precedent.

Therefore the spec should be **renamed/repositioned** as:

```text
CAPABILITY_GRAPH_v1 = Layer 1 (Identity/Authority) + Layer 4 (Action Bus)
                      of the arifOS AGI Substrate Architecture
```

---

## 5. Recommended Corrections

### 5.1 Immediate: Amend CAPABILITY_GRAPH_v1.md

Add a new section near the top:

```markdown
## 0. Scope Boundary

This document specifies the **capability surface and action bus** of arifOS.
It is one layer of the larger AGI substrate architecture.
It intentionally does NOT specify:
- embodied memory (M0-M3)
- world model / uncertainty registry
- bounded learning loop
- multi-domain synthesis (GEOX/WEALTH/WELL/AAA/VAULT)

Those layers are specified in `AGI_SUBSTRATE_v1.md`.
```

### 5.2 Short-term: Close the 7 critical gaps

1. **Precedent memory (M3)** — add `arif_precedent_lookup` tool + `PrecedentNode` schema.
2. **Evidence requirements** — add `evidence_required` field to `CapabilityNode`.
3. **Rollback plans** — add `rollback_plan_id` requirement for EXECUTE_HIGH_IMPACT+.
4. **Lease revocation** — add `arif_lease_revoke` tool.
5. **Bounded learning** — add `arif_learn_outcome` tool (tactics only; constitutional changes escalate).
6. **World model registry** — add `WorldModelNode` + `UncertaintyClaim` schemas.
7. **Confidence × blast_radius gate** — add `confidence_threshold` and `blast_radius` fields to action requests.

### 5.3 Medium-term: Forge AGI_SUBSTRATE_v1.md

Create the full architecture document that situates CAPABILITY_GRAPH_v1 as one layer among seven:

```text
arifOS_AGI_Substrate
├── 00 Kernel
├── 01 Identity Layer
├── 02 Memory Layer
├── 03 Cognition Layer
├── 04 Action Bus  ← CAPABILITY_GRAPH_v1 lives here
├── 05 Organs
└── 06 Learning Layer
```

---

## 6. Final Verdict

| Aspect | Rating |
|--------|--------|
| Correctness within scope | ✅ Strong |
| Completeness as AGI substrate | ⚠️ Insufficient |
| Readiness for implementation | ✅ Can proceed, but scope must be bounded |
| Alignment with F13 premise correction | ✅ After repositioning |

**Decision:** **ACCEPT with scope correction.** Do not throw the spec away. It is a necessary layer. But it must be explicitly framed as the Action Bus + Identity layer, not the whole AGI substrate. The missing layers must be forged next.

---

## 7. Next Action Options

Pick one:

1. **A — Amend CAPABILITY_GRAPH_v1.md** with a clear scope boundary and the 7 gap closures.
2. **B — Forge AGI_SUBSTRATE_v1.md** first, then amend CAPABILITY_GRAPH_v1.md to fit inside it.
3. **C — Implement the 7 gap closures** directly in code (`CapabilityNode` schema, new tools, migration).

Recommended order: **B, then A, then C.** Architecture before code.

---

*DITEMPA BUKAN DIBERI — Intelligence is forged, not given.*
