# Cooling Ledger (v42)

**Version:** v42.0 | **Status:** DRAFT | **Last Updated:** 2025-12-16
**Source:** Merged from v38Omega Cooling Ledger

---

## 1. Purpose

The Cooling Ledger is the append-only audit trail of arifOS providing:

1. **Hash-chain integrity** - Each entry links to previous via SHA3-256
2. **Evidence traceability** - Every entry traces back to floor checks
3. **Crash recovery** - HeadState tracking for fast chain verification
4. **Hot/Warm rotation** - 7-day hot segment with archive rotation

**Core Principle:** DITEMPA BUKAN DIBERI - Truth must cool before it rules.

---

## 2. Ledger Entry Schema

```python
@dataclass
class LedgerEntry:
    ledger_version: str         # "v42"
    timestamp: str              # ISO-8601 UTC
    query_hash: str             # SHA-256 of input
    response_hash: str          # SHA-256 of output
    metrics: Dict[str, Any]     # Floor metrics snapshot
    verdict: str                # SEAL | SABAR | PARTIAL | VOID | 888_HOLD
    class: str                  # "CLASS_A" | "CLASS_B"
    floor_warnings: List[str]   # Floor check warnings
    prev_hash: Optional[str]    # Chain link
    entry_hash: str             # Self-hash (SHA3-256)
```

---

## 3. Hash-Chain Integrity

Every entry contains:
- `prev_hash`: SHA3-256 of previous entry (null for first)
- `entry_hash`: SHA3-256 of current entry content

```python
def _compute_hash(entry: Dict[str, Any]) -> str:
    excluded = {"hash", "entry_hash", "kms_signature", "kms_key_id"}
    data = {k: v for k, v in entry.items() if k not in excluded}
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha3_256(canonical.encode("utf-8")).hexdigest()
```

---

## 4. HeadState (Crash Recovery)

```python
@dataclass
class HeadState:
    last_entry_hash: Optional[str]  # For fast chain verification
    entry_count: int                # Total entries
    last_timestamp: Optional[str]   # Most recent timestamp
    epoch: str                      # "v42"
```

On startup, compare `HeadState.last_entry_hash` with actual last entry for quick integrity check.

---

## 5. Fail-Open Hardening

```python
class LedgerConfig:
    fail_behavior: str = "SABAR_HOLD_WITH_LOG"
    # Options:
    # - SABAR_HOLD_WITH_LOG: Return failure (caller triggers SABAR/HOLD)
    # - SILENT_FAIL: Log warning and return failure
    # - RAISE: Raise exception
```

**Rule:** Never silently return success if write failed.

---

## 6. Verdict => Band Routing

| Verdict | Target Bands | Canonical? |
|---------|--------------|------------|
| SEAL | LEDGER, ACTIVE | YES |
| SABAR | LEDGER, ACTIVE | YES (with reason) |
| PARTIAL | PHOENIX, LEDGER | PENDING |
| VOID | VOID only | NO |
| 888_HOLD | LEDGER | PENDING |
| SUNSET | PHOENIX | Re-trial |

---

**DITEMPA BUKAN DIBERI** - Forged, not given; truth must cool before it rules.
