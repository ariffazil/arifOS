# MEMORY_WRITE_POLICY.md — arifOS v38 Memory Write Policy Engine

**Status:** SEALED | **Version:** v38 | **Canon:** ARIFOS_MEMORY_STACK_v36.3O.md

---

## Overview

The Memory Write Policy Engine enforces **what may be remembered** based on governance verdicts. Memory in arifOS is evidence, not storage — every write must trace back to a floor check and pass constitutional gates.

**Core Philosophy:**

- VOID verdicts must NEVER become canonical memory
- Memory is evidence, not storage
- Every write must be auditable
- Recalled memory is *suggestion*, never *fact*

---

## 1. Core Invariants

| # | Invariant | Implementation |
|---|-----------|----------------|
| **INV-1** | VOID verdicts NEVER become canonical memory | `should_write()` rejects VOID → non-VOID band writes |
| **INV-2** | Authority boundary: humans seal law, AI proposes | `MemoryAuthorityCheck` enforces VAULT write restrictions |
| **INV-3** | Every write must be auditable (evidence chain) | `validate_evidence_chain()` required before write |
| **INV-4** | Recalled memory passes floor checks | `should_recall()` with confidence ceiling (0.85 max) |

---

## 2. Verdict → Band Routing

The policy engine routes memory writes based on APEX PRIME verdicts:

| Verdict | Target Bands | Description |
|---------|--------------|-------------|
| **SEAL** | LEDGER, ACTIVE | Canonical memory + session state |
| **SABAR** | LEDGER, ACTIVE | Canonical (with failure reason logged) |
| **PARTIAL** | PHOENIX, LEDGER | Queued for review + audit log |
| **VOID** | VOID only | Diagnostic ONLY, never canonical |
| **888_HOLD** | LEDGER | Log hold for audit trail |

### 2.1 Routing Logic

```python
VERDICT_BAND_ROUTING = {
    "SEAL": ["LEDGER", "ACTIVE"],      # Canonical + session
    "SABAR": ["LEDGER", "ACTIVE"],     # Canonical + session (with reason)
    "PARTIAL": ["PHOENIX", "LEDGER"],  # Queue for review + log
    "VOID": ["VOID"],                   # Diagnostic ONLY, never canonical
    "888_HOLD": ["LEDGER"],             # Log hold for audit
}
```

### 2.2 VOID Special Handling

VOID verdicts receive special treatment to prevent canonical contamination:

```python
if verdict == "VOID":
    if band_target != "VOID":
        return WriteDecision(
            allowed=False,
            reason="VOID verdicts can ONLY be written to Void band (never canonical)",
            ledger_entry={},
        )
```

---

## 3. Policy Decision Types

### 3.1 WriteDecision

Returned by `should_write()`:

```python
@dataclass
class WriteDecision:
    allowed: bool                    # Whether write is permitted
    reason: str                      # Human-readable explanation
    ledger_entry: Dict[str, Any]     # Complete entry for audit
    target_bands: List[str]          # Where to write
    requires_human_approval: bool    # True for VAULT writes
```

### 3.2 RecallDecision

Returned by `should_recall()`:

```python
@dataclass
class RecallDecision:
    allowed: bool                    # Whether recall is permitted
    reason: str                      # Human-readable explanation
    confidence_ceiling: float        # 0.0-1.0 trust level
    floor_warnings: List[str]        # Issues found during recall
```

### 3.3 RetentionDecision

Returned by `should_retain()`:

```python
@dataclass
class RetentionDecision:
    keep: bool                       # Whether to retain
    move_to_band: Optional[str]      # Band to move to (if any)
    reason: str                      # Human-readable explanation
    delete_after_days: Optional[int] # Days until deletion
```

### 3.4 EvidenceChainValidation

Returned by `validate_evidence_chain()`:

```python
@dataclass
class EvidenceChainValidation:
    valid: bool                      # Chain is complete
    missing_links: List[str]         # What's missing
    hash_verified: bool              # Hash matches content
    floor_check_present: bool        # Floor checks recorded
```

---

## 4. Evidence Chain Requirements

Every memory write must include a valid evidence chain:

### 4.1 Required Fields

| Field | Type | Purpose |
|-------|------|---------|
| `floor_checks` | `List[Dict]` | Floor check results from 888_JUDGE |
| `hash` or `evidence_hash` | `str` | SHA-256 linking to verdict |
| `timestamp` | `str` | ISO 8601 timestamp |
| `verdict` | `str` | APEX PRIME verdict |

### 4.2 Validation Example

```python
evidence_chain = {
    "floor_checks": [
        {"floor": "F1_Amanah", "score": 1.0, "passed": True},
        {"floor": "F2_Truth", "score": 0.99, "passed": True},
        # ... all 9 floors
    ],
    "timestamp": "2025-01-15T10:30:00Z",
    "verdict": "SEAL",
    "hash": "sha256..."
}

validation = policy.validate_evidence_chain(evidence_chain)
if not validation.valid:
    print(f"Missing: {validation.missing_links}")
```

### 4.3 Hash Computation

The evidence hash ties the memory write to its governance origin:

```python
def compute_evidence_hash(floor_checks, verdict, timestamp):
    evidence = {
        "floor_checks": floor_checks,
        "verdict": verdict,
        "timestamp": timestamp,
    }
    return hashlib.sha256(
        json.dumps(evidence, sort_keys=True).encode()
    ).hexdigest()
```

---

## 5. Recall Policy

Recalled memory is treated as **suggestion, not fact**. The policy engine applies confidence ceilings based on:

### 5.1 Confidence Factors

| Factor | Impact | Multiplier |
|--------|--------|------------|
| VOID band source | Blocked | 0.0 (rejected) |
| Non-SEAL/SABAR verdict | Reduced trust | 0.5 |
| Age > 30 days | Minor reduction | 0.8 |
| Age > 90 days | Further reduction | 0.7 |
| Missing evidence chain | Significant reduction | 0.6 |
| Missing floor checks | Moderate reduction | 0.7 |
| Topic mismatch | Minor reduction | 0.9 |
| Invalid timestamp | Minor reduction | 0.9 |

### 5.2 Maximum Confidence Ceiling

```python
MAX_RECALL_CONFIDENCE = 0.85
```

Even perfectly valid memories cap at 0.85 confidence. This enforces the principle: **recalled memory is suggestion, current floor checks are law**.

### 5.3 Recall Example

```python
memory_item = {
    "band": "LEDGER",
    "verdict": "SEAL",
    "timestamp": "2025-01-01T00:00:00Z",
    "evidence_chain": {...},
    "content": "Previous response about topic X"
}

decision = policy.should_recall(memory_item, current_context)
if decision.allowed:
    # Use with confidence_ceiling applied
    effective_confidence = min(decision.confidence_ceiling, 0.85)
    # Pass to current floor checks for validation
```

---

## 6. Retention Tiers

Memory lifecycle follows retention tiers:

| Tier | Duration | Bands | Purpose |
|------|----------|-------|---------|
| **HOT** | 7 days | ACTIVE | Session state, recent scars |
| **WARM** | 90 days | LEDGER, PHOENIX, WITNESS | Audit trail, pending proposals |
| **COLD** | Permanent | VAULT | Constitutional law |
| **VOID** | 90 days | VOID | Diagnostic (auto-delete) |

### 6.1 Retention Rules

```python
RETENTION_HOT_DAYS = 7       # Active Stream
RETENTION_WARM_DAYS = 90     # Ledger, Phoenix, Witness
RETENTION_COLD_DAYS = 365    # Archive (years)
RETENTION_VOID_DAYS = 90     # Void band (then auto-delete)
```

### 6.2 Band-Specific Rules

| Band | Tier | Behavior |
|------|------|----------|
| VAULT | COLD | **Never expires** — constitutional |
| LEDGER | WARM → COLD | Archive after 90 days |
| ACTIVE | HOT | Delete after 7 days |
| PHOENIX | WARM | Move to LEDGER when sealed/rejected |
| WITNESS | WARM | Rolling 90-day window |
| VOID | VOID | Auto-delete after 90 days |

---

## 7. Integration Points

### 7.1 Pipeline Stage Integration

| Stage | Integration | File |
|-------|-------------|------|
| 111_SENSE | Memory recall for cross-session context | `memory_sense.py` |
| 777_FORGE | Scar detection and pattern recognition | `memory_scars.py` |
| 888_JUDGE | Write policy enforcement | `memory_judge.py` |
| 999_SEAL | Ledger finalization and EUREKA receipts | `memory_seal.py` |

### 7.2 Integration Flow

```
User Query
    ↓
111_SENSE: should_recall() — load cross-session memory
    ↓
333_REASON → 777_FORGE: detect_patterns() — scar detection
    ↓
888_JUDGE: should_write() — verdict-based gating
    ↓
999_SEAL: finalize_to_ledger() — audit trail + EUREKA receipt
```

### 7.3 Example: Full Write Flow

```python
# 1. 888_JUDGE calls should_write()
decision = policy.should_write(
    verdict="SEAL",
    evidence_chain={
        "floor_checks": floor_results,
        "timestamp": now_iso,
        "verdict": "SEAL",
        "hash": computed_hash
    },
    band_target="LEDGER"
)

# 2. If allowed, route to bands
if decision.allowed:
    for band in decision.target_bands:
        router.route_write(
            verdict="SEAL",
            content=response_content,
            target_band=band,
            evidence_hash=decision.ledger_entry["hash"]
        )

# 3. Record in audit layer
audit.record_write(
    band=band,
    entry_id=entry_id,
    writer_id="888_JUDGE",
    verdict="SEAL",
    entry_hash=content_hash,
    evidence_hash=evidence_hash
)
```

---

## 8. Human Approval Gates

Certain operations require explicit human approval:

| Operation | Approval Required | Reason |
|-----------|-------------------|--------|
| VAULT writes | Always | Constitutional law |
| 888_HOLD verdicts | Always | High-stakes decision |
| Amendment sealing | Always | AI proposes, humans seal |
| Constitution modification | Always | Self-modification protection |

### 8.1 Approval Flow

```python
decision = policy.should_write(verdict="SEAL", evidence_chain=chain, band_target="VAULT")

if decision.requires_human_approval:
    # Queue for human review
    phoenix_proposal = create_proposal(decision)
    await human_seal(phoenix_proposal)
    # Only proceed after human approval
```

---

## 9. Strict Mode vs Lenient Mode

The policy engine supports two modes:

| Mode | Behavior | Use Case |
|------|----------|----------|
| **Strict** (default) | Reject on any policy violation | Production |
| **Lenient** | Warn but allow (with logging) | Development/testing |

```python
# Strict mode (default)
policy = MemoryWritePolicy(strict_mode=True)

# Lenient mode (development)
policy = MemoryWritePolicy(strict_mode=False)
```

---

## 10. Audit Trail

All policy decisions are logged:

```python
# Access policy decision log
log = policy.get_write_log()

# Each entry contains:
{
    "timestamp": "2025-01-15T10:30:00Z",
    "verdict": "SEAL",
    "bands": ["LEDGER", "ACTIVE"],
    "allowed": True,
    "reason": "Policy approved"
}
```

---

## 11. Error Handling

### 11.1 Policy Rejection Reasons

| Error | Reason | Resolution |
|-------|--------|------------|
| `Unknown verdict type` | Invalid verdict string | Use valid verdict (SEAL/SABAR/PARTIAL/VOID/HOLD) |
| `Evidence chain invalid` | Missing required fields | Include floor_checks, hash, timestamp, verdict |
| `VOID verdicts can ONLY be written to Void band` | VOID → non-VOID write | Route VOID to VOID band only |
| `Verdict X cannot write to Y` | Routing violation | Use allowed bands for verdict |

### 11.2 Example Error Handling

```python
decision = policy.should_write(verdict="VOID", evidence_chain=chain, band_target="LEDGER")

if not decision.allowed:
    # Handle rejection
    log_policy_violation(decision.reason)
    # Route to correct band
    if "VOID" in decision.reason:
        route_to_void(content)
```

---

## 12. File Reference

| File | Purpose |
|------|---------|
| `arifos_core/memory/policy.py` | Memory Write Policy Engine |
| `arifos_core/memory/bands.py` | 6-band implementations + router |
| `arifos_core/memory/authority.py` | Human seal enforcement |
| `arifos_core/memory/audit.py` | Hash-chain audit layer |
| `arifos_core/memory/retention.py` | Hot/Warm/Cold lifecycle |
| `arifos_core/integration/memory_sense.py` | 111_SENSE integration |
| `arifos_core/integration/memory_judge.py` | 888_JUDGE integration |
| `arifos_core/integration/memory_scars.py` | 777_FORGE scar detection |
| `arifos_core/integration/memory_seal.py` | 999_SEAL finalization |

---

## 13. Quick Reference

### Policy Check Cheat Sheet

```python
from arifos_core.memory.policy import MemoryWritePolicy

policy = MemoryWritePolicy()

# Check if write allowed
write_decision = policy.should_write(verdict, evidence_chain, band_target)

# Check if recall allowed
recall_decision = policy.should_recall(memory_item, current_context)

# Check retention status
retention_decision = policy.should_retain(memory_item, age_days)

# Validate evidence chain
validation = policy.validate_evidence_chain(evidence_chain)
```

### Key Constants

```python
RETENTION_HOT_DAYS = 7       # Active Stream
RETENTION_WARM_DAYS = 90     # Ledger, Phoenix, Witness
RETENTION_COLD_DAYS = 365    # Archive
RETENTION_VOID_DAYS = 90     # Void (auto-delete)
MAX_RECALL_CONFIDENCE = 0.85 # Confidence ceiling
```

---

**Version:** v38.0 | **Last Updated:** 2025-12-13
