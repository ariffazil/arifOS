# Cooling Ledger Cryptography Specification

**Version:** v42.0.0  
**Status:** Implemented  
**Task Reference:** Task 1.1: Cryptographic Binding for Cooling Ledger

> **Scope:** This upgrade strengthens auditability only. Constitutional thresholds and verdict semantics remain unchanged.

## 1. Purpose & Scope

This specification defines the cryptographic mechanisms for the arifOS cooling ledger, ensuring:

- **Tamper-evidence**: Any modification to past entries is detectable
- **Chain-of-custody**: Unbroken cryptographic link from genesis to head
- **Auditability**: Independent verification without trusting the system

**Scope:** Integrity and auditability. Excludes confidentiality & network transport.

## 2. Threat Model

### 2.1 Assumed Attacker Capabilities
- Read/write access to ledger files
- May have system access but NOT external anchors
- Cannot break SHA3-256 (collision resistance assumption)

### 2.2 Protected Against
| Attack | Detection Method |
|--------|-----------------|
| Entry modification | Hash chain break |
| Entry deletion | Index gap, Merkle mismatch |
| Entry reordering | prev_hash mismatch |
| Rollback/truncation | Merkle root mismatch, external anchor |
| Hash collision | Duplicate hash detection |
| Fork attempt | Fork ancestry detection |

### 2.3 Not Protected Against
- Full log rewrite with total system control
- Denial of service (log deletion)
- Real-time prevention (forensic only)
- Origin authenticity (no signatures in this phase)

## 3. Cryptographic Primitives

| Primitive | Algorithm | Notes |
|-----------|-----------|-------|
| Hash function | SHA3-256 | 256-bit output, collision-resistant |
| Serialization | JSON canonical | sorted keys, no whitespace |
| Genesis hash | `"0" * 64` | 64 hex zeros |

> **Note:** Uses SHA3-256 (not SHA-256) for backward compatibility with existing arifOS ledger. SHA3-256 provides equivalent security properties.

## 4. Data Structures

### 4.1 LedgerEntry

```python
@dataclass
class LedgerEntry:
    index: int           # Sequential, 0-based
    timestamp: str       # ISO 8601 UTC
    payload: Dict        # Decision data
    prev_hash: str       # SHA3-256 of previous entry (or GENESIS_HASH)
    hash: str            # SHA3-256 of this entry
```

### 4.2 Hash Computation

```
entry_hash = SHA3-256(
    f"{index}|{timestamp}|{canonical_json(payload)}|{prev_hash}"
)
```

### 4.3 Chain Structure

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Entry 0    │    │  Entry 1    │    │  Entry 2    │
│ prev: GEN   │───→│ prev: H(0)  │───→│ prev: H(1)  │
│ hash: H(0)  │    │ hash: H(1)  │    │ hash: H(2)  │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 5. Merkle Tree

- Leaves = entry hashes
- Internal nodes = `SHA3-256(left || right)`
- Odd leaves duplicated (Bitcoin-style)
- Root stored per batch for efficient verification

## 6. Verification Process

### 6.1 verify_integrity()

1. Check first entry links to GENESIS_HASH
2. For each entry: verify prev_hash == prev.entry_hash
3. Recompute each entry hash from content
4. Verify Merkle roots match stored values
5. Optionally check external anchors

### 6.2 detect_tampering()

Additional forensic checks:
- Duplicate hash detection
- Index continuity
- Timestamp monotonicity
- Fork ancestry analysis

## 7. Performance

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Append | O(1) | Single hash |
| Verify | O(n) | Linear scan |
| Merkle proof | O(log n) | Single entry |

Tested: 1,000 entries append+verify < 30s

## 8. Implementation

| File | Purpose |
|------|---------|
| `arifos_core/governance/ledger_cryptography.py` | CryptographicLedger class |
| `arifos_core/governance/merkle.py` | Merkle tree utilities |
| `tests/test_ledger_cryptography.py` | 21 test cases (16 spec scenarios) |

## 9. Audit & Compliance

- **Verification command**: `pytest tests/test_ledger_cryptography.py`
- **External anchoring**: Store Merkle roots in trusted external system
- **Incident response**: TamperReport provides human-readable anomaly details

## 10. References

- [RFC 6962](https://tools.ietf.org/html/rfc6962): Certificate Transparency
- [RFC 8785](https://tools.ietf.org/html/rfc8785): JSON Canonicalization
- Task 1.1: Cryptographic Binding for Cooling Ledger (spec PDF)
