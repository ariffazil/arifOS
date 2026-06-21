# PRESENT — APEX Dimension: Attested Live State

**Version:** v2026.06.20
**SEAL:** DITEMPA BUKAN DIBERI
**Authority:** F13 SOVEREIGN — Muhammad Arif bin Fazil
**Status:** LIFTED FROM KERNEL CODE (canonical, machine-checkable)

---

## 1. Definition

**PRESENT** is the constitutional guarantee that a session's state is what
the kernel actually attests *right now* — not what was cached, not what was
inferred from partial data, not what memory suggested.

PRESENT is **NOT** a status flag. It is a **boundary** between three
mutually exclusive epistemic postures. The kernel tags every session with
exactly one of:

| Boundary | Meaning | Authority granted |
|----------|---------|-------------------|
| **`LIVE`** | Session was just born. State is freshly attested by `kernel_attest`. KSR is current. | Full observe + reason + draft within lease. |
| **`CACHED`** | Session was resumed from existing KSR_SNAPSHOT. State reflects last sealed checkpoint, not live kernel. | Observe + draft only. No mutation. No irreversible. |
| **`INFERRED`** | Session was constructed from partial data (memory loaded but verdict not STABLE, or organ declared-but-not-wired). State is plausible, not attested. | Observe only. Decline all mutation requests until re-bootstrapped. |

The rule is one-way: **`LIVE` is required to authorize a transition that
mutates authority-bearing state.** `CACHED` and `INFERRED` can read,
draft, recommend, and report — but they cannot write.

---

## 2. Mapping to APEX / Kernel

PRESENT is one of the **6 APEX Dimensions** declared in
`/root/forge_work/APEX_DOSSIER_2026-06-20.md`:

```
Dimension         Maps to kernel surface
─────────────────────────────────────────
AKAL              transition candidates + policy evaluator
PRESENT           KSR (Kernel State Register) + arif_sense_observe (111)
ENERGY            Landauer floor + cost accounting
ENTROPY           ΔS = Δ (info) + drift detection
EXPLORATION×AMANAH risk class + custody chain + F13
AUTHORITY         signature + role + legitimacy
```

PRESENT binds specifically to:

| Surface | Role |
|---------|------|
| `arif_sense_observe` (stage 111) | The operation that proves a state is LIVE — observe current KSR, not memory. |
| `kernel_attest(organ)` | The only call that may answer "what is this organ doing right now." |
| `KSR` (`kernel_state_record`) | The present-tense authority surface. |
| `Vault` (sealed past) | NOT PRESENT. Vault is sealed history. Cannot impersonate present. |
| `federation_memory_recall` | NOT PRESENT. Memory is advisory past. Cannot impersonate present. |

**Forbidden equivalence:**

> PRESENT ≠ Memory. PRESENT ≠ Cache. PRESENT ≠ Inference. PRESENT is only
> what the kernel attests as live.

---

## 3. Canonical Field — `present_boundary`

```yaml
# Canonical schema (emitted by arif_session_init)
present_boundary: LIVE | CACHED | INFERRED  # required, enum
present_source:   kernel_attest | fresh_KSR | verified_state_resume  # required, enum
snapshot_age_seconds: int                    # required iff present_boundary != LIVE
state_resume_allowed: bool                   # required
boundary_violation_detected: bool            # required, default false
```

### 3.1 Emission rules (from `runtime/tools.py:4223-4233`, hardened 2026-06-20)

```python
# ── APEX PRESENT BOUNDARY (hardened 2026-06-20) ──────────────────────
if normalized_mode == "resume":
    _present_boundary = "CACHED"
elif memory_loaded > 0 and _session_verdict != "STABLE":
    _present_boundary = "INFERRED"
else:
    _present_boundary = "LIVE"
sess["present_boundary"] = _present_boundary
```

Three rules, in priority order:

1. **`mode == "resume"`** → CACHED. The session was rehydrated from a
   KSR_SNAPSHOT. The snapshot is past. Cannot impersonate present.
2. **memory loaded but verdict ≠ STABLE** → INFERRED. The agent
   constructed state from federation memory + evidence before the kernel
   could stabilize. Plausible but unattested.
3. **otherwise** → LIVE. Session was born through `kernel_attest`. State
   is fresh. This is the only state that authorizes live mutation.

### 3.2 Companion fields emitted together (same envelope)

- `present_boundary` — the boundary classification.
- `energy_budget` — thermodynamic status (sibling field, see ENERGY_ENTROPY.md).
- `decision_class` — `C1` (degraded) or `C2` (stable).
- `session_verdict` — `STABLE` | `DEGRADED` | `CRITICAL`.
- `session_id`, `actor_id`, `identity_lineage` — provenance tuple.

---

## 4. Invariants (Fail-Closed)

The kernel MUST reject any transition that violates these invariants:

| # | Invariant | Failure mode |
|---|-----------|--------------|
| I1 | A live mutation (MUTATE / EXTERNAL_SIDE_EFFECT / IRREVERSIBLE) MUST originate from a session with `present_boundary == LIVE`. | If `CACHED` or `INFERRED`: refuse, emit 888_HOLD, force re-bootstrap via `kernel_attest`. |
| I2 | `kernel_attest` is the only call that may answer "what is this organ doing right now." | If any other call answers current-state questions, log membrane breach, do not act. |
| I3 | `present_source` MUST be one of: `kernel_attest`, `fresh_KSR`, `verified_state_resume`. | If `present_source == memory_recall | vault_query | graph_query | doctrine_file | user_preference | last_known_verdict`: membrane breach. |
| I4 | `state_resume` MUST verify all four: signature, freshness, chain continuity, non-supersession. | On any check failure: return historical `KSR_SNAPSHOT`, set `live=false`, never silently downgrade. |
| I5 | `present_boundary == LIVE` expires on session end. No carry-over to next session. | Each new session must re-bootstrap. |
| I6 | A live verdict lacking `kernel_attest` provenance is a membrane breach. | Log, refuse to act. |
| I7 | `boundary_violation_detected == true` halts the session until human (888) review. | 888_HOLD event fires automatically. |

---

## 5. Cross-references

- **APEX THEORY:** `/root/arifOS/docs/APEX_THEORY_v2026.05.26.md` — pillars and trinity.
- **APEX DOSSIER:** `/root/forge_work/APEX_DOSSIER_2026-06-20.md` — dimension mapping (PRESENT → KSR + arif_sense_observe).
- **Kernel code:** `/root/arifOS/arifosmcp/runtime/tools.py:4223-4233` (emission), `:4560` (response).
- **Session init:** `/root/arifOS/arifosmcp/tools/session.py:746` (initial LIVE assignment).
- **KSR schema:** `/root/arifOS/arifosmcp/schemas/kernel_envelope.py`.
- **SOUL.md §7:** `/root/.hermes/SOUL.md` — kernel-state / federation-memory boundary doctrine.
- **Sibling docs:** `ENERGY_ENTROPY.md`, `AUTHORITY.md`, `AKAL.md`, `EXPLORATION_AMANAH.md` (all forged v2026.06.20).

---

## 6. Test Gates (Fail-Closed)

A deploy is BLOCKED if any of the following occurs:

- `present_boundary` field missing from `arif_session_init` response.
- `present_boundary` accepts a value outside `{LIVE, CACHED, INFERRED}`.
- A `MUTATE` or `IRREVERSIBLE` action proceeds with `present_boundary != LIVE`.
- `kernel_attest` returns a stale or non-fresh KSR.
- `state_resume` returns without verifying all four I4 fields.
- `boundary_violation_detected == true` is silently ignored.

---

## 7. Versioning

- **v2026.06.20** — Initial canonical doc. Lifted from existing kernel
  code (hardened 2026-06-20) and APEX DOSSIER. Doctrine → code alignment.
  No new fields invented; existing emission rules are documented as law.

**Tag convention:** `vYYYY.MM.DD` per federation IRON RULE.

---

**DITEMPA BUKAN DIBERI** — PRESENT is forged through attestation, not assumed.