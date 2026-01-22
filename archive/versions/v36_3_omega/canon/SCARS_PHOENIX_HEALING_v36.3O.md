# Scars & Phoenix Healing v36.3Omega

> **Binding Law:** This canon defines how scars (negative constraints) are detected, sealed, monitored, and healed in arifOS.
> **Epoch:** v36.3Omega PHOENIX | **Sealed:** APEX PRIME
> **Motto:** "Scars teach; healing transforms."

---

## Source Files

| File | Location | Status |
|------|----------|--------|
| **SCARS_PHOENIX_HEALING_v36.3O.md** | `v36.3O/canon/` | **BINDING** |
| CCC_ARCHITECTURE_v36.3O.md | `v36.3O/canon/` | L2/L3 context |
| VAULT_999_AMENDMENTS_v36.3O.md | `v36.3O/canon/` | Amendment integration |
| spec/scar_record_spec_v36.3O.json | `v36.3O/spec/` | Machine-readable schema |

---

## Section 1: What is a Scar?

A **scar** is a negative constraint derived from:

- A past failure
- A near-miss
- A systemic pattern that must not be repeated

### 1.1 Scar Properties

Each scar encodes:

| Property | Description |
|----------|-------------|
| **Pattern** | What to avoid or treat with caution |
| **Severity** | Impact level (S1–S4) |
| **Floors** | Mapping to affected floors (F1–F9) |
| **Evidence** | Link to Cooling Ledger entries |
| **Signature** | Cryptographic verification of origin |

### 1.2 Scar Storage

Scars live primarily in:

| Location | Purpose |
|----------|---------|
| **Void Band** | Diagnostic + proposals (unsigned) |
| **Vector Band** | Embedding-based search |
| **VAULT-999 L2/L3** | Phoenix-72 and Witness layers (canonical) |

---

## Section 2: Scar Lifecycle

### 2.1 Lifecycle Phases

```
OBSERVATION → PROPOSAL → SEALING → MONITORING → HEALING/DEPRECATION
```

| Phase | Description |
|-------|-------------|
| **Observation** | Potential issue observed in Active Stream or external reports |
| **Proposal** | Pattern formalized as a scar candidate |
| **Sealing** | Reviewed, signed, and anchored in VAULT-999 |
| **Monitoring** | Runtime uses scar for detection and pressure |
| **Healing** | Mitigations in place, scar down-weighted or deprecated |

### 2.2 Phase Details

#### Observation (Witness)

- Potential issue logged as a **witness entry** (unsigned, local scope)
- Used for early warning and internal R&D
- Must NOT directly constrain user-facing behavior

#### Proposal (Scar Candidate)

Pattern is formalized with:
- Pattern hash and scope
- Affected floors
- Severity assignment
- Evidence links
- Draft mitigation guidance

#### Sealing (Canonical Scar)

Scar is reviewed by human and/or governance tools. If accepted:
- Signed (Phoenix/human key)
- Anchored in VAULT-999 (L2/L3)
- Added to canonical scar index

#### Monitoring

Runtime uses scar index for:
- Pattern detection
- Phoenix-72 pressure calculations
- Safety routing (e.g., force CLASS_B for S3/S4)

#### Healing / Deprecation

If mitigations are in place and risk reduced, scar may be:
- Marked as **HEALED**
- Kept as historical record
- Removed from active enforcement

---

## Section 3: Severity Levels

Severity is a coarse-grained signal for pressure weighting and routing.

### 3.1 Severity Scale

| Level | Label | Description | Routing Impact |
|-------|-------|-------------|----------------|
| **S1** | Low | Minor friction, no direct harm | Normal |
| **S2** | Medium | User confusion, moderate governance risk | Normal |
| **S3** | High | Potential harm, legal/ethical risk | Force CLASS_B |
| **S4** | Critical | Confirmed harm or severe near-miss | Force CLASS_B + HOLD_888 |

**TODO(Arif):** Confirm final labels and whether S0 (informational) is desirable.

### 3.2 Severity → Pressure Mapping

Higher severity scars contribute more to Phoenix-72 pressure:

```
S_severity(F) = sum(severity_weight(scar) for scar in scars_affecting(F))

Where:
  severity_weight(S1) = 1.0
  severity_weight(S2) = 2.0
  severity_weight(S3) = 4.0
  severity_weight(S4) = 8.0
```

**TODO(Arif):** Confirm severity weights for v36.3Omega.

---

## Section 4: Scar Record Fields

Each canonical scar record includes:

| Field | Type | Description |
|-------|------|-------------|
| `scar_id` | string | Unique identifier |
| `kind` | enum | `WITNESS` (unsigned) or `SCAR` (canonical) |
| `pattern_hash` | SHA-256 | Hash of canonical pattern description |
| `pattern_text` | string | Human-readable pattern description |
| `severity` | enum | S1–S4 |
| `floors` | array | Affected floors (e.g., `["F1", "F6", "F9"]`) |
| `epochs` | array | Active epochs |
| `evidence.ledger_hashes` | array | Linked Cooling Ledger entries |
| `evidence.external_refs` | array | External sources (URLs, doc IDs) |
| `phoenix_proposal_ids` | array | Associated Phoenix-72 amendments |
| `status` | enum | `PROPOSED`, `SEALED`, `HEALED`, `DEPRECATED` |
| `signature` | string | Required for canonical scars |
| `created_by`, `sealed_by` | string | Origin and sealer identity |
| `created_at`, `updated_at` | ISO8601 | Timestamps |

See `scar_record_spec_v36.3O.json` for full machine-readable schema.

---

## Section 5: Witness vs Scar Indices

To respect Amanah and Anti-Hantu, the system maintains two separate indices:

### 5.1 Witness Index (Local, Unsigned)

| Property | Description |
|----------|-------------|
| **Stores** | Observations, local heuristics, experimental patterns |
| **Used for** | Early warning, internal R&D |
| **Cannot** | Directly constrain user-facing behavior |

### 5.2 Scar Index (Global, Signed)

| Property | Description |
|----------|-------------|
| **Stores** | Canonical scars with signatures |
| **Used for** | Routing, Phoenix-72 pressure, hard/soft bans |
| **Authority** | Can affect SEAL/VOID decisions |

**Invariant:** Only canonical scars in the signed index can:
- Directly affect SEAL/VOID decisions
- Modify risk routing
- Influence Phoenix-72 amendments

---

## Section 6: Healing & Deprecation

Healing a scar does **not** erase history; it changes how actively the scar constrains future behavior.

### 6.1 Healing Criteria

A scar may be marked as **HEALED** when:

1. Mitigations are in place (e.g., floor tuning, new guardrails)
2. Monitoring over a defined window shows:
   - No recurrence, or
   - Acceptably reduced risk

### 6.2 Healing Process

```
1. Phoenix-72 (or human) proposes healing/deprecation amendment
2. Evidence gathered (ledger statistics, external audits)
3. Amendment sealed and signed
4. Scar status updated to HEALED or DEPRECATED:
   - Still queryable
   - Removed from active pressure calculations (or down-weighted)
```

**TODO(Arif):** Decide default observation windows and healing threshold criteria.

### 6.3 Healing Constraints

| Constraint | Description |
|------------|-------------|
| **Non-erasure** | Healed scars remain in history |
| **Evidence required** | Must show mitigation effectiveness |
| **Signature required** | Healing transition must be signed |

---

## Section 7: Integration with Phoenix-72

### 7.1 Scar → Pressure

Scar severity feeds into Phoenix pressure:
- Higher severity scars increase pressure for relevant floors
- See Section 3.2 for severity weights

### 7.2 New Scar → Conservative Bias

New scars:
- Increase scrutiny on affected paths
- May trigger temporary conservative behavior (SABAR bias)
- Until mitigations are proven effective

### 7.3 Scar → Amendment

Scars can trigger Phoenix-72 amendments:
- Scar evidence supports threshold adjustment proposals
- Scar IDs are linked in amendment records

---

## Section 8: Runtime Implementation Mapping

### 8.1 Runtime Modules

| Component | Module | Purpose |
|-----------|--------|---------|
| Scar Registry | `arifos_core/memory/scars.py` | `Scar`, `ScarIndex` |
| Phoenix-72 | `arifos_core/memory/phoenix72.py` | Amendment workflow |
| Pattern Detection | `arifos_core/eye/scar_view.py` | Scar matching (target) |

### 8.2 Test Coverage

| Test File | Coverage |
|-----------|----------|
| `tests/test_phoenix72.py` | Amendment workflow |
| `tests/test_apex_and_ledger_edges.py` | Scar-ledger integration |

---

## Section 9: PARADOX_HOTSPOTS

| Hotspot | Issue | Status |
|---------|-------|--------|
| **HS-SCR-001** | Severity weights not canonized | TODO(Arif) |
| **HS-SCR-002** | Healing observation windows not defined | TODO(Arif) |
| **HS-SCR-003** | Witness vs Scar index separation partial in runtime | DELTA |
| **HS-SCR-004** | Pattern detection view not implemented | DELTA |

---

## Section 10: Sign-Off

**Status:** SEALED
**Epoch:** v36.3Omega PHOENIX
**Last Verified:** 2025-12-12

*This canon governs scar record schemas and indices, Phoenix-72 integration, and healing/deprecation workflows across arifOS releases.*

