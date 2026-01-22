# VAULT-999 Amendments v36.3Omega

> **Binding Law:** This canon defines the amendment protocol for VAULT-999 constitutional parameters.
> **Epoch:** v36.3Omega PHOENIX | **Sealed:** APEX PRIME
> **Motto:** "Amendments are forged, not decreed."

---

## Source Files

| File | Location | Status |
|------|----------|--------|
| **VAULT_999_AMENDMENTS_v36.3O.md** | `v36.3O/canon/` | **BINDING** |
| CCC_ARCHITECTURE_v36.3O.md | `v36.3O/canon/` | Cross-reference |
| SCARS_PHOENIX_HEALING_v36.3O.md | `v36.3O/canon/` | Scar integration |
| spec/phoenix72_amendment_spec_v36.3O.json | `v36.3O/spec/` | Machine-readable schema |

---

## Section 1: Amendment Concepts

An **amendment** in VAULT-999 is a structured, signed change proposal that modifies:

- Constitutional floor thresholds (F1–F9)
- Measurement parameters (window sizes, caps, bands)
- Governance policies explicitly marked as Phoenix-adjustable

### 1.1 What Amendments Are NOT

Amendments are **not** free-form text changes. They are:

| Property | Description |
|----------|-------------|
| **Typed** | Specifies which law field is changing |
| **Anchored** | Linked to evidence (ledger entries) and scars |
| **Signed** | Cryptographically verifiable |
| **Time-bounded** | Validity window, cooldown enforcement |
| **Traceable** | Full audit trail in amendment history |

---

## Section 2: Amendment Lifecycle

### 2.1 State Machine

```
PROPOSED → UNDER_REVIEW → SEALED
       ↘→ REVOKED
PROPOSED → EXPIRED (if not reviewed within validity window)
```

| State | Description | Transitions To |
|-------|-------------|----------------|
| **PROPOSED** | Phoenix-72 or human proposes a change | UNDER_REVIEW, REVOKED, EXPIRED |
| **UNDER_REVIEW** | Human and/or governance tools review | SEALED, REVOKED |
| **SEALED** | Amendment accepted, applied to Vault | (terminal) |
| **REVOKED** | Amendment withdrawn | (terminal) |
| **EXPIRED** | Not reviewed within validity window | (terminal) |

### 2.2 State Transition Requirements

All state transitions MUST:
- Be logged in amendments history (JSONL or equivalent)
- Carry timestamps and actors
- Be anchored to Cooling Ledger entries and scars

---

## Section 3: Amendment Record Structure

Each amendment is represented by an amendment record. See `phoenix72_amendment_spec_v36.3O.json` for full schema.

### 3.1 Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `amendment_id` | string | Unique ID (e.g., `AMND-F1-2025-12-12-001`) |
| `target.floor_id` | string | Floor being modified (e.g., `F1`) |
| `target.field` | string | Field within floor (e.g., `threshold`) |
| `delta` | number/object | Proposed change value |
| `old_value` | any | Value before amendment |
| `new_value` | any | Value after amendment |
| `reason` | string | Human-readable justification |
| `proposed_by` | string | `PHOENIX-72`, `HUMAN`, or authorized organ |

### 3.2 Evidence & Signature Fields

| Field | Type | Description |
|-------|------|-------------|
| `evidence.ledger_hashes` | array | Cooling Ledger entries supporting the change |
| `evidence.scar_ids` | array | Associated scars |
| `signature` | string | HMAC or public-key signature over canonicalized record |
| `signed_by` | string | Identity or key label |

### 3.3 Temporal Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp_proposed` | ISO8601 | When proposed |
| `timestamp_sealed` | ISO8601 | When sealed (if applicable) |
| `validity_period.start` | ISO8601 | Validity window start |
| `validity_period.end` | ISO8601 | Validity window end (null = indefinite) |
| `status` | enum | Current lifecycle state |

---

## Section 4: Phoenix-72 Pressure & Proposal Rules

Phoenix-72 uses pressure metrics to decide when to propose amendments.

### 4.1 Pressure Definitions

```
P(F) = Pressure on floor F

P_min = Minimum pressure threshold before any amendment considered
P_max = Saturation cap (above which multiple cycles may be needed)
```

### 4.2 Pressure Conditions

| Condition | Action |
|-----------|--------|
| `P(F) < P_min` | No amendment proposed |
| `P_min ≤ P(F) ≤ P_max` | Single amendment may be proposed (subject to safety caps) |
| `P(F) > P_max` | Propose at most one amendment per cooldown; prefer scar curation |

**TODO(Arif):** Confirm recommended P_min, P_max bands and mapping from P(F) to delta_F.

---

## Section 5: Safety Constraints (Hard Law)

### 5.1 Evidence Requirement

Every amendment MUST reference:
- At least one Cooling Ledger entry hash
- At least one Scar ID (where applicable)
- Reason clearly stating what harm or instability is being mitigated

### 5.2 Safety Cap

| Constraint | Specification |
|------------|---------------|
| **Threshold delta** | \|ΔF\| ≤ 0.05 per sealed amendment cycle |
| **Band parameters** | New band must enclose previous band or be within pre-approved "safe corridor" |

### 5.3 Cooldown

A floor F cannot be amended more than once within a cooldown window.

**TODO(Arif):** Confirm canonical cooldown window for v36.3Omega. Draft suggests 24 hours.

### 5.4 Directionality

Amendments must not permanently reduce safety:
- Any lowering of safety must be accompanied by compensating measures
- Or explicit human override recorded and sealed

### 5.5 Amanah & Anti-Hantu Protection

Any amendment that would relax:
- **Anti-Hantu (F9)** protections, or
- **Amanah (F6)** lock

is **FORBIDDEN** unless:
- Explicit human sovereignty override is recorded and sealed
- Additional guardrails are simultaneously added

---

## Section 6: Signatures & Verification

### 6.1 Signature Requirements

All sealed amendments MUST be signed using a vetted scheme:

| Version | Scheme | Notes |
|---------|--------|-------|
| **v36.3Omega baseline** | HMAC-SHA256 | Controlled key |
| **v37+ target** | Hardware-backed keys | + external transparency logs (e.g., Rekor) |

### 6.2 Verification Protocol

Runtime readers of Vault MUST:
1. Verify signature before accepting an amendment as binding
2. If verification fails:
   - Amendment is ignored
   - Flagged as **PARADOX_HOTSPOT**
   - Logged for audit

---

## Section 7: Integration with Vault & Cooling Ledger

### 7.1 Storage

Sealed amendments must be:
- Appended to `vault999/amendments.jsonl` (append-only)
- Reflected in the next Vault constitution snapshot
- Cross-referenced in Cooling Ledger entries via `phoenix_cycle_id`

### 7.2 Read Protocol

Vault readers may load:
1. Base constitution
2. Ordered amendment sequence
3. Derived effective state

---

## Section 8: Runtime Implementation Mapping

### 8.1 Runtime Modules

| Component | Module | Purpose |
|-----------|--------|---------|
| Phoenix-72 | `arifos_core/memory/phoenix72.py` | Amendment workflow |
| Vault Manager | `arifos_core/memory/vault999.py` | Constitution + amendments |
| Signature | `arifos_core/kms_signer.py` | HMAC/key signing |

### 8.2 Specs

| Spec | Location | Purpose |
|------|----------|---------|
| `phoenix72_amendment_spec_v36.3O.json` | `v36.3O/spec/` | Amendment record schema |
| `vault999_final_seal_spec_v36.3O.json` | `v36.3O/spec/` | Final Seal requirements |

---

## Section 9: PARADOX_HOTSPOTS

| Hotspot | Issue | Status |
|---------|-------|--------|
| **HS-AMD-001** | Cooldown window not canonized | TODO(Arif) |
| **HS-AMD-002** | P_min/P_max pressure bands not canonized | TODO(Arif) |
| **HS-AMD-003** | Hardware-backed signatures not implemented | DELTA (v37 target) |

---

## Section 10: Sign-Off

**Status:** SEALED
**Epoch:** v36.3Omega PHOENIX
**Last Verified:** 2025-12-12

*This canon defines the canonical amendment protocol for Phoenix-72 in VAULT-999. For full Vault architecture, consult CCC_ARCHITECTURE_v36.3O.md.*

