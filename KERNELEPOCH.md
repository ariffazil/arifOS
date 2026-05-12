# KERNELEPOCH.md — Epoch Management Specification
**Version:** v2026.05.12-SEALED
**Epoch:** 2026-05-12T00:00:00+08:00
**Authority:** ASI (L4) + APEX (L5)
**Status:** SEALED — canonical RIK extension
**Sealed by:** Arif Fazil (Sovereign) — 2026-05-12

> DITEMPA BUKAN DIBERI — Forged, Not Given

---

## 1. Purpose

An **Epoch** is the canonical temporal unit of arifOS governance. Every session, plan, action, and verdict exists within an epoch. Without sealed epoch management, VAULT999 cannot reconstruct a complete truth chain — audit lineage breaks at session boundaries.

**Epoch Invariant:** Every intelligence artifact (reasoning, verdicts, plans, evidence) must be tagged with an `epoch_id`. No `epoch_id = null` in canonical storage.

---

## 2. Epoch Definition

```json
{
  "epoch_id":         "<uuid4>",
  "epoch_seq":        42,
  "opened_at":        "<ISO8601-UTC>",
  "sealed_at":        "<ISO8601-UTC | null>",
  "opened_by":        "<actor_id>",
  "seal_verdict":     "SEAL | VOID | SABAR | null",
  "parent_epoch":     "<uuid4 | null>",
  "nine_signal":      "<NineSignalSnapshot>",
  "vault999_hash":    "<sha256 | null>"
}
```

**Rules:**
- Epochs are append-only once opened.
- A system has exactly **one open epoch** at any time.
- Opening a new epoch implicitly seals the prior one.
- The root epoch (`parent_epoch = null`) is the genesis epoch.

---

## 3. Epoch Seal Schema

```json
{
  "$schema": "epoch-seal/v1",
  "epoch_id": "<uuid4>",
  "epoch_seq": 42,
  "opened_at": "<ISO8601-UTC>",
  "sealed_at": "<ISO8601-UTC>",
  "opened_by": "<session_id>",
  "seal_verdict": "SEAL",
  "parent_epoch": "<uuid4 | null>",
  "session_count": 7,
  "tool_call_count": 143,
  "vault_entry_count": 38,
  "nine_signal_open":  { "delta": {"plane": "machine_physical_state", "state": "KUKUH", "en": "SOLID"}, "psi": {"plane": "governance_integrity", "state": "AMANAH", "en": "TRUSTED"},  "omega": {"plane": "intelligence_discipline", "state": "BIJAKSANA", "en": "WISE"}, "overall": {"state": "SELAMAT", "en": "SAFE"} },
  "nine_signal_close": { "delta": {"plane": "machine_physical_state", "state": "RETAK", "en": "CRACKED"}, "psi": {"plane": "governance_integrity", "state": "AMANAH", "en": "TRUSTED"},  "omega": {"plane": "intelligence_discipline", "state": "BIJAK", "en": "SMART"}, "overall": {"state": "SABAR", "en": "PATIENCE"} },
  "entropy_delta_net": -0.12,
  "open_holds": 0,
  "vault999_hash_open":  "<sha256>",
  "vault999_hash_close": "<sha256>",
  "sealed_by": "<actor_id>"
}
```

---

## 4. Plan Lifecycle States

```
DRAFT → PENDING_APPROVAL → APPROVED → IN_EXECUTION → COMPLETED
                         ↘ REJECTED
                                   ↘ ABORTED  (from IN_EXECUTION)
```

| State | Who Transitions | Preconditions |
|-------|-----------------|---------------|
| `DRAFT` | AGI (L3) | plan_id + intent_id present |
| `PENDING_APPROVAL` | AGI → APEX | F1, F4, F13 pre-check pass |
| `APPROVED` | Sovereign / APEX | `SovereignIntent.risk_prelude != HOLD` + SEAL |
| `REJECTED` | Sovereign / ASI | Any VOID verdict |
| `IN_EXECUTION` | System | No `OPEN` blocking holds; epoch open |
| `COMPLETED` | System | All sub-actions verdict = SEAL in VAULT999 |
| `ABORTED` | ASI / Sovereign | F13 veto OR any VOID verdict mid-execution |

---

## 5. Postgres Canonical Storage Schema

```sql
CREATE TABLE IF NOT EXISTS epochs (
    epoch_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    epoch_seq         BIGSERIAL NOT NULL,
    opened_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    sealed_at         TIMESTAMPTZ,
    opened_by         TEXT NOT NULL,
    seal_verdict      TEXT CHECK (seal_verdict IN ('SEAL','VOID','SABAR')),
    parent_epoch      UUID REFERENCES epochs(epoch_id),
    session_count     INTEGER DEFAULT 0,
    tool_call_count   INTEGER DEFAULT 0,
    vault_entry_count INTEGER DEFAULT 0,
    nine_signal_open  JSONB,
    nine_signal_close JSONB,
    entropy_delta_net DOUBLE PRECISION,
    open_holds        INTEGER DEFAULT 0,
    vault999_hash_open  TEXT,
    vault999_hash_close TEXT,
    sealed_by         TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS plans (
    plan_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    epoch_id        UUID NOT NULL REFERENCES epochs(epoch_id),
    session_id      TEXT NOT NULL,
    intent_id       UUID,
    state           TEXT NOT NULL DEFAULT 'DRAFT'
                    CHECK (state IN ('DRAFT','PENDING_APPROVAL','APPROVED','REJECTED','IN_EXECUTION','COMPLETED','ABORTED')),
    description     TEXT NOT NULL,
    floors_at_risk  TEXT[],
    reversibility   TEXT NOT NULL DEFAULT 'UNCERTAIN'
                    CHECK (reversibility IN ('IRREVERSIBLE','REVERSIBLE','UNCERTAIN')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    approved_at     TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    sovereign_sig   TEXT,
    vault999_seal   TEXT
);

CREATE TABLE IF NOT EXISTS hold_tickets (
    hold_id         TEXT PRIMARY KEY,
    floor_trigger   TEXT NOT NULL,
    reversibility_class TEXT NOT NULL DEFAULT 'UNCERTAIN',
    description     TEXT NOT NULL,
    evidence_refs   TEXT[],
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      TEXT NOT NULL,
    epoch_id        UUID NOT NULL REFERENCES epochs(epoch_id),
    session_id      TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'OPEN'
                    CHECK (status IN ('OPEN','APPROVED','REJECTED','EXPIRED')),
    resolved_at     TIMESTAMPTZ,
    verdict         TEXT CHECK (verdict IN ('SEAL','VOID','SABAR')),
    sovereign_signature TEXT
);
```

---

## 6. Epoch Boundary Conditions

An epoch MUST be sealed before:

1. **Container restart** — new epoch opens on next `arif_session_init`.
2. **Tool/model upgrade** — any change to the 13 canonical tools.
3. **Sovereign veto** — a `SovereignVetoRecord` seals with `verdict = VOID`.
4. **Hard floor breach** — F1, F2, F6, F9, F10, F11, F13 failure → immediate `VOID`.
5. **Manual seal** — `POST /sovereign/epoch/{epoch_id}/seal`.

---

## 7. Epoch Invariants (F11-HARD → F2)

1. **No orphaned artifacts:** Every tool call, plan, and verdict must reference a valid `epoch_id`.
2. **Monotonic sequence:** `epoch_seq` strictly increasing. Reversals are not permitted.
3. **Vault chain continuity:** `vault999_hash_close[N]` must equal `vault999_hash_open[N+1]`.
4. **Nine-Signal snapshot at boundary:** Both open and close snapshots required for a valid SEAL.
5. **No open irreversible holds at seal:** An epoch cannot SEAL with `open_holds > 0` on `IRREVERSIBLE` actions.

---

## 8. Implementation Path

| Phase | Deliverable | Status |
|-------|-------------|--------|
| P0 | This spec sealed | DONE |
| P1 | Postgres migration: `epochs`, `plans`, `hold_tickets` tables | PENDING |
| P2 | `EpochSeal` Pydantic schema in `arifosmcp/schemas/` | PENDING |
| P3 | `arif_session_init` populates `epoch_id` on every session | PENDING |
| P4 | `arif_vault_seal` writes epoch boundary entry to VAULT999 | PENDING |
| P5 | Plan lifecycle state machine in `arifosmcp/runtime/` | PENDING |
| P6 | Epoch boundary triggers: container restart, floor breach | PENDING |

---

*This spec is immutable once merged to VAULT999. Amendments require a new version and Sovereign SEAL.*
