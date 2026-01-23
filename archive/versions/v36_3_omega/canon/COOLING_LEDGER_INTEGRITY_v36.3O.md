# Cooling Ledger Integrity v36.3Omega

> **Binding Law:** This canon defines integrity guarantees, rotation rules, and failure modes for the Cooling Ledger (VAULT-999 L1).
> **Epoch:** v36.3Omega PHOENIX | **Sealed:** APEX PRIME
> **Motto:** "If L1 integrity fails, SEAL must fail."

---

## Source Files

| File | Location | Status |
|------|----------|--------|
| **COOLING_LEDGER_INTEGRITY_v36.3O.md** | `v36.3O/canon/` | **BINDING** |
| CCC_ARCHITECTURE_v36.3O.md | `v36.3O/canon/` | Cross-reference |
| vault999_final_seal_spec_v36.3O.json | `v36.3O/spec/` | Final Seal requirements |
| cooling_ledger_entry_spec_v36.3O.json | `v36.3O/spec/` | Entry schema |

---

## Section 1: Role of the Cooling Ledger

The Cooling Ledger is:

| Property | Description |
|----------|-------------|
| **Layer** | L1 (Evidence Layer) of VAULT-999 |
| **Structure** | Append-only log of high-stakes governance decisions |
| **Purpose** | GENIUS metrics, Phoenix-72 pressure, scar extraction |
| **Integrity** | Hash-chained entries with APEX signatures |

### Key Principle

> **If L1 integrity fails, SEAL must fail.**

The Cooling Ledger is the primary source of truth for what actually happened in governed interactions.

---

## Section 2: Entry Structure and Hash Chain

### 2.1 Required Entry Fields

Each Cooling Ledger entry MUST contain:

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO8601 | Time of verdict |
| `ledger_version` | enum | `v35Ic`, `v36Omega`, or `v36.3Omega` |
| `query_hash` | SHA-256 | Hash of governed input |
| `response_hash` | SHA-256 | Hash of governed output |
| `metrics` | object | Floor metrics and derived signals |
| `verdict` | enum | `SEAL`, `PARTIAL`, `HOLD_888`, `SABAR`, `VOID` |
| `previous_hash` | SHA-256 | Hash of previous entry (or genesis constant) |
| `entry_hash` | SHA-256 | Hash of this entry (excluding this field) |

See `cooling_ledger_entry_spec_v36.3O.json` for full machine-readable schema.

### 2.2 Hash-Chain Invariant

```
entry_hash_i = H(entry_i_without_entry_hash)
previous_hash_i = entry_hash_{i-1}

Where:
  H = SHA-256
  entry_i_without_entry_hash = entry_i with entry_hash field excluded
```

**Invariant:** Any violation of this chain MUST be treated as a critical governance failure.

### 2.3 Genesis Entry

The first entry in a ledger segment uses a well-defined genesis constant:

```
genesis_hash = "0x0000000000000000000000000000000000000000000000000000000000000000"
```

---

## Section 3: Rotation & Head State

The ledger is partitioned into segments (Hot → Warm → Cold) through rotation.

### 3.1 Hot Segment

| Property | Value |
|----------|-------|
| **Path** | `runtime/cooling_ledger.jsonl` (typical) |
| **Retention** | Up to 7 days OR up to 10,000 entries |
| **Trigger** | Time or entry count exceeds threshold |

**TODO(Arif):** Confirm canonical Hot segment thresholds for v36.3Omega.

### 3.2 Rotation Procedure

1. **Acquire** exclusive lock on the hot ledger file
2. **Flush** any buffered entries
3. **Compute** final `entry_hash` of the hot segment
4. **Update** `head_state.json` with:
   - `last_entry_hash`
   - `last_timestamp`
   - `segment_path`
   - `epoch`
5. **Move** hot JSONL file to Warm segment (timestamped + gzipped)
6. **Create** fresh hot ledger file (linking to prior `last_entry_hash`)

### 3.3 Chain Continuity Invariant

After rotation, the global chain remains unbroken when segments are concatenated in order.

---

## Section 4: Concurrency & Atomicity

### 4.1 Write Requirements

| Requirement | Specification |
|-------------|---------------|
| **Locking** | Use filesystem-level locking where available (e.g., `fcntl.flock` on POSIX) |
| **Atomicity** | Each append writes a single JSON line (one entry) |
| **Integrity** | Partial writes cannot create malformed entries |

### 4.2 Fallback for Unreliable Environments

If the environment cannot provide reliable locking, the ledger MUST:
- Prefer append-only single-writer processes, or
- Use a queue mechanism to serialize writes

---

## Section 5: Graceful Failure Modes

The Cooling Ledger is critical but must not cause unbounded cascading failures.

### 5.1 Failure Triggers

| Failure | Description |
|---------|-------------|
| Disk full | No space for new entries |
| Permission error | Cannot write to ledger file |
| File corruption | Hash chain broken or malformed entries |
| Lock timeout | Lock acquisition failure beyond safe timeout |

### 5.2 Failure Response

When any failure occurs, the current pipeline interaction MUST:

1. **Fall back to:**
   - `SABAR` for high-stakes interactions
   - `HOLD_888` if human confirmation available
2. **Log** an error in a separate, best-effort diagnostics channel

### 5.3 Forbidden Actions on Failure

The system MUST NOT:
- Fabricate ledger entries
- Return `SEAL` based on incomplete or unlogged evidence
- Silently skip ledger writes

**Invariant:** When ledger integrity is uncertain, the system prefers **pause/hold** over **false SEAL**.

---

## Section 6: Head State & Recovery

### 6.1 Head State Schema

`head_state.json` represents the latest known good ledger head:

| Field | Type | Description |
|-------|------|-------------|
| `last_entry_hash` | SHA-256 | Hash of most recent entry |
| `last_timestamp` | ISO8601 | Timestamp of most recent entry |
| `segment_path` | string | Path to segment containing the head |
| `epoch` | string | Epoch version |
| `chain_height` | integer | (Optional) Total entry count |
| `recovery_notes` | string | (Optional) Human-readable notes |

### 6.2 Recovery Protocol

On startup or recovery, the system SHOULD:

1. Read `head_state.json`
2. Validate the last segment up to `last_entry_hash`
3. If discrepancies are found:
   - Mark chain as **DEGRADED**
   - Allow reads with explicit warnings
   - **Disallow** new SEAL verdicts until resolved

---

## Section 7: Integration with Scars and Phoenix-72

### 7.1 Scar Extraction

Scar extraction routines MUST:
- Use Cooling Ledger entries as primary evidence
- Record `linked_ledger_hash` in scar records

### 7.2 Phoenix-72 Pressure

Phoenix-72 controllers MUST:
- Compute pressure using only entries that:
  - Pass structural validation
  - Are part of a verified chain segment

---

## Section 8: Runtime Implementation Mapping

### 8.1 Runtime Modules

| Component | Module | Purpose |
|-----------|--------|---------|
| Cooling Ledger | `arifos_core/memory/cooling_ledger.py` | `CoolingLedger`, `CoolingEntry` |
| Hash Chain | `arifos_core/ledger_hashing.py` | `hash_entry()`, `verify_chain()` |
| Head State | `arifos_core/memory/cooling_ledger.py` | `HeadState` (target) |

### 8.2 Test Coverage

| Test File | Coverage |
|-----------|----------|
| `tests/test_cooling_ledger.py` | Entry logging |
| `tests/test_cooling_ledger_integrity.py` | Hash chain verification |
| `tests/test_cooling_ledger_schema_compliance.py` | v35Ic schema |

---

## Section 9: PARADOX_HOTSPOTS

| Hotspot | Issue | Status |
|---------|-------|--------|
| **HS-LDG-001** | Hot segment thresholds (7 days, 10k entries) not canonized | TODO(Arif) |
| **HS-LDG-002** | Head state recovery protocol partial implementation | DELTA |
| **HS-LDG-003** | Concurrent write locking varies by platform | KNOWN |

---

## Section 10: Sign-Off

**Status:** SEALED
**Epoch:** v36.3Omega PHOENIX
**Last Verified:** 2025-12-12

*This canon is authoritative for Cooling Ledger implementations. For derived integrity checks in APEX PRIME, consult vault999_final_seal_spec_v36.3O.json.*

