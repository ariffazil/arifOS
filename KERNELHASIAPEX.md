# KERNELHASIAPEX.md — Sovereign Interface Specification
**Version:** v2026.05.12-SEALED
**Epoch:** 2026-05-12T00:00:00+08:00
**Authority:** APEX (L5) + Sovereign (L6)
**Status:** SEALED — canonical RIK extension
**Sealed by:** Arif Fazil (Sovereign) — 2026-05-12

> DITEMPA BUKAN DIBERI — Forged, Not Given

---

## 1. Purpose

The Sovereign Interface (SI) is the mandatory surface through which the human Sovereign (L6) maintains veto authority over all AGI/ASI/APEX actions. Without a sealed SI, F13 (SOVEREIGN) cannot be enforced at runtime — any action can proceed without human oversight.

**SI Invariant:** No AGI/ASI/APEX execution involving irreversible operations, epoch transitions, or cross-agent orchestration may proceed without the SI being reachable and responsive.

---

## 2. Schemas

### 2.1 SovereignIntent

```json
{
  "$schema": "sovereign-intent/v1",
  "intent_id": "<uuid4>",
  "epoch_id": "<epoch-uuid>",
  "session_id": "<session-uuid>",
  "actor_id": "sovereign",
  "description": "<human-readable intent>",
  "constraints": ["<floor-id>", "..."],
  "floors_at_risk": ["F1", "F13"],
  "risk_prelude": "HOLD | PROCEED | ESCALATE",
  "created_at": "<ISO8601-UTC>",
  "expires_at": "<ISO8601-UTC | null>"
}
```

**Rules:**
- `intent_id` is immutable once created.
- `expires_at: null` means the intent persists until explicitly resolved.
- `risk_prelude` is advisory — does not replace the Judge verdict.

### 2.2 888HoldTicket

```json
{
  "$schema": "888-hold-ticket/v1",
  "hold_id": "888-H<NNN>",
  "floor_trigger": "F<N>",
  "reversibility_class": "IRREVERSIBLE | REVERSIBLE | UNCERTAIN",
  "description": "<what is being held and why>",
  "evidence_refs": ["<artifact-ref>"],
  "created_at": "<ISO8601-UTC>",
  "created_by": "<actor_id>",
  "epoch_id": "<epoch-uuid>",
  "session_id": "<session-uuid>",
  "status": "OPEN | APPROVED | REJECTED | EXPIRED",
  "resolved_at": "<ISO8601-UTC | null>",
  "verdict": "SEAL | VOID | SABAR | null",
  "sovereign_signature": "<hmac-sha256 | null>"
}
```

**Rules:**
- `hold_id` follows sequential schema: `888-H001`, `888-H002`, etc., scoped per epoch.
- `OPEN` tickets block execution of the held action. The kernel must return `HOLD` until resolved.
- `IRREVERSIBLE` tickets require `sovereign_signature` for approval.
- All tickets are written to VAULT999 on creation and resolution — append-only.

### 2.3 SovereignVetoRecord

```json
{
  "$schema": "sovereign-veto/v1",
  "veto_id": "<uuid4>",
  "epoch_id": "<epoch-uuid>",
  "target": "plan_id | hold_id | session_id",
  "reason": "<human-readable>",
  "floors_cited": ["F13"],
  "issued_at": "<ISO8601-UTC>",
  "sovereign_signature": "<hmac-sha256>"
}
```

**Rules:**
- A veto is absolute (F13-HARD). No override path exists.
- Veto is written to VAULT999 immediately and propagated to all active sessions.
- Vetoed plans/sessions enter `VOID` state permanently.

---

## 3. API Contract

### 3.1 Veto Endpoint

```
POST /sovereign/veto/{epoch_id}
Authorization: Bearer <sovereign-token>

{ "target": "<plan_id|hold_id|session_id>", "reason": "<string>", "floors_cited": ["F13"] }

200: { "veto_id": "<uuid4>", "verdict": "VOID", "sealed_to_vault": true }
403: { "error": "SOVEREIGN_AUTH_REQUIRED", "floor": "F13" }
```

### 3.2 Plan Approval Endpoint

```
POST /sovereign/approve/{plan_id}
Authorization: Bearer <sovereign-token>

{ "epoch_id": "<uuid>", "ack_irreversible": true, "constraints": [] }

200: { "plan_id": "<uuid>", "verdict": "SEAL", "new_state": "APPROVED", "sealed_to_vault": true }
```

### 3.3 Hold Queue Endpoint

```
GET /sovereign/holds?status=OPEN&epoch_id=<uuid>
Authorization: Bearer <sovereign-token>

200: { "holds": [<888HoldTicket>, "..."], "open_count": <int>, "epoch_id": "<uuid>" }
```

### 3.4 Nine-Signal Dashboard Endpoint

```
GET /sovereign/signal
Authorization: Bearer <sovereign-token>

200: {
  "epoch_id": "<uuid>",
  "timestamp": "<ISO8601-UTC>",
  "nine_signal": {
    "delta": { "state": "KUKUH|RETAK|LEBUR", "en": "SOLID|CRACKED|DISSOLVED", "evidence": "<string>" },
    "psi":   { "state": "AMANAH|GANTUNG|KHIANAT", "en": "TRUSTED|PENDING|BETRAYED", "evidence": "<string>" },
    "omega": { "state": "BIJAKSANA|BIJAK|SESAT", "en": "WISE|SMART|LOST", "evidence": "<string>" }
  },
  "open_holds": <int>,
  "pending_approvals": <int>,
  "vault999_health": "healthy|degraded|offline"
}
```

---

## 4. Nine-Signal Dashboard Contract (HORIZON-v2026.04.18)

| Plane | BM States | EN States | Palette |
|-------|-----------|-----------|---------|
| Δ DELTA (Infrastructure) | KUKUH / RETAK / LEBUR | SOLID / CRACKED / DISSOLVED | teal / amber / red |
| Ψ PSI (Governance) | AMANAH / GANTUNG / KHIANAT | TRUSTED / PENDING / BETRAYED | teal / amber / red |
| Ω OMEGA (Intelligence) | BIJAKSANA / BIJAK / SESAT | WISE / SMART / LOST | teal / amber / red |

**Signal derivation rules:**

- **Δ DELTA:** KUKUH if `dS > -0.1` AND `verdict == SEAL`; LEBUR if `dS ≤ -0.5` OR `verdict == VOID`; RETAK otherwise.
- **Ψ PSI:** AMANAH if `psi_le > 0.9` OR `tau ≥ 0.99`; KHIANAT if `psi_le < 0.7`; GANTUNG otherwise.
- **Ω OMEGA:** BIJAKSANA if `echoDebt < 0.2` AND `psi_le > 0.85`; SESAT if `echoDebt ≥ 0.7`; BIJAK otherwise.

**Accessibility:** WCAG AA contrast ratio ≥ 4.5:1 for all signal colors.

---

## 5. SI Invariants (F13-HARD)

1. **Reachability:** SI must be reachable before any irreversible operation. If unreachable → `HOLD`.
2. **Veto Propagation:** A `SovereignVetoRecord` must propagate to all active sessions within 10 seconds.
3. **Hold Queue Drain:** `OPEN` tickets with `reversibility_class = IRREVERSIBLE` are hard blockers.
4. **No Self-Approval:** AGI/ASI/APEX cannot approve their own hold tickets.
5. **Audit Trail:** Every SI interaction is written to VAULT999 with sovereign session binding.

---

## 6. Implementation Path

| Phase | Deliverable | Status |
|-------|-------------|--------|
| P0 | This spec sealed | DONE |
| P1 | `/sovereign/holds` GET endpoint | PENDING |
| P2 | `888HoldTicket` Pydantic schema in `arifosmcp/schemas/` | PENDING |
| P3 | Vault writer: `hold_ticket` record type in VAULT999 | PENDING |
| P4 | `/sovereign/veto` POST endpoint + F13 guard | PENDING |
| P5 | `/sovereign/approve` POST + F1 ack gate | PENDING |
| P6 | `/sovereign/signal` Nine-Signal GET endpoint | PENDING |

---

*This spec is immutable once merged to VAULT999. Amendments require a new version and Sovereign SEAL.*
