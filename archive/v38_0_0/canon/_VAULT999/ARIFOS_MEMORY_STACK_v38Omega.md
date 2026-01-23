# ARIFOS_MEMORY_STACK_v38Omega.md

**arifOS v38 Memory Write Policy Engine — Constitutional Memory Law**

```
+=============================================================================+
|  ARIFOS_MEMORY_STACK — Memory Write Policy Engine v38Omega                  |
|  "VOID verdicts NEVER become canonical memory."                             |
+=============================================================================+
|  Zone:        07_CCC                                                   |
|  Version:     v38Omega                                                      |
|  Status:      SEALED                                                        |
|  Extends:     VAULT_999_v36Omega.md                                         |
|  Runtime:     arifos_core/memory/*.py, arifos_core/integration/*.py         |
+=============================================================================+
```

---

## 1. Purpose

This canon defines the **Memory Write Policy Engine** — the governance layer that enforces what may be remembered in arifOS.

Memory in arifOS is **governance, not storage**. The v38 Memory Stack provides:

1. **Verdict-based write gating** — Only approved verdicts write to canonical bands
2. **Evidence chain requirements** — Every write traces back to floor checks
3. **Authority boundary enforcement** — AI proposes, humans seal law
4. **Confidence-capped recall** — Recalled memory is suggestion, not fact

**Core Principle:** If APEX PRIME didn't approve it, memory doesn't record it as canonical.

---

## 2. The 4 Core Invariants (INV-1 to INV-4)

| Invariant | Statement | Enforcement |
|-----------|-----------|-------------|
| **INV-1** | VOID verdicts NEVER become canonical memory | `MemoryWritePolicy.should_write()` gates all writes |
| **INV-2** | Authority boundary: humans seal law, AI proposes | `MemoryAuthorityCheck.authority_boundary_check()` |
| **INV-3** | Every write must be auditable (evidence chain) | `MemoryAuditLayer.record_write()` with hash-chain |
| **INV-4** | Recalled memory = suggestion, not fact | Confidence ceiling (0.85) on all recalls |

These invariants are **non-negotiable**. Hard floor violations in memory operations trigger VOID.

---

## 3. Six Memory Bands (L0-L5)

The v38 Memory Stack extends Vault-999 with explicit band governance:

| Band | Code Symbol | Purpose | Retention |
|------|-------------|---------|-----------|
| **L0 VAULT** | `VaultBand` | Read-only constitution snapshot | **PERMANENT** (COLD) |
| **L1 LEDGER** | `CoolingLedgerBand` | Hash-chained audit trail | 90 days (WARM) |
| **L2 ACTIVE** | `ActiveStreamBand` | Volatile working state | 7 days (HOT) |
| **L3 PHOENIX** | `PhoenixCandidatesBand` | Amendment proposals pending | 90 days (WARM) |
| **L4 WITNESS** | `WitnessBand` | Soft evidence, scars | 90 days (WARM) |
| **L5 VOID** | `VoidBandStorage` | Diagnostic only, NEVER canonical | 90 days (auto-delete) |

### 3.1 Band Hierarchy

```
VAULT (L0 Constitution) — IMMUTABLE
    ↓ cannot override
LEDGER (L1 Evidence) — Append-only
    ↓ informs
WITNESS (Soft Evidence) — Scars & patterns
    ↓ guides
ACTIVE (Working State) — Per-session
    ↓ proposes
PHOENIX (Amendments) — Pending human seal
    ↓
VOID (Diagnostic) — NEVER CANONICAL
```

**Rule:** Higher bands cannot override lower bands. VAULT is supreme law.

---

## 4. Verdict → Band Routing Matrix

The Memory Write Policy routes writes based on APEX PRIME verdicts:

| Verdict | Target Bands | Canonical? | Notes |
|---------|--------------|------------|-------|
| **SEAL** | LEDGER, ACTIVE | YES | Full canonical memory + session state |
| **SABAR** | LEDGER, ACTIVE | YES | Canonical with failure reason logged |
| **PARTIAL** | PHOENIX, LEDGER | PENDING | Queued for Phoenix-72 review |
| **VOID** | VOID **only** | **NO** | Diagnostic retention, never canonical |
| **888_HOLD** | LEDGER | PENDING | Logged, awaiting human approval |

### 4.1 Routing Code

```python
VERDICT_BAND_ROUTING = {
    "SEAL": ["LEDGER", "ACTIVE"],      # Canonical + session
    "SABAR": ["LEDGER", "ACTIVE"],     # Canonical + session (with reason)
    "PARTIAL": ["PHOENIX", "LEDGER"],  # Queue for review + log
    "VOID": ["VOID"],                   # Diagnostic ONLY, never canonical
    "888_HOLD": ["LEDGER"],             # Log hold for audit
}
```

### 4.2 VOID Enforcement (INV-1)

```python
if verdict == "VOID":
    if band_target not in (None, "VOID"):
        raise MemoryPolicyViolation(
            "VOID verdicts can ONLY be written to Void band (never canonical)"
        )
```

---

## 5. Evidence Chain Requirements

Every memory write must include a valid evidence chain linking to floor checks:

### 5.1 Required Fields

| Field | Type | Purpose |
|-------|------|---------|
| `floor_checks` | `List[Dict]` | Floor check results from 888_JUDGE |
| `hash` | `str` | SHA-256 linking to verdict |
| `timestamp` | `str` | ISO 8601 timestamp |
| `verdict` | `str` | APEX PRIME verdict |

### 5.2 Evidence Hash Computation

```python
def compute_evidence_hash(floor_checks, verdict, timestamp):
    """Compute evidence hash tying memory write to governance origin."""
    evidence = {
        "floor_checks": floor_checks,
        "verdict": verdict,
        "timestamp": timestamp,
    }
    return hashlib.sha256(
        json.dumps(evidence, sort_keys=True).encode()
    ).hexdigest()
```

### 5.3 Validation Requirements

```python
@dataclass
class EvidenceChainValidation:
    valid: bool                      # Chain is complete
    missing_links: List[str]         # What's missing
    hash_verified: bool              # Hash matches content
    floor_check_present: bool        # Floor checks recorded
```

**Rule:** If `valid=False` in strict mode, write is rejected.

---

## 6. Authority Boundary Matrix (INV-2)

Memory operations respect authority boundaries:

| Action | HUMAN | APEX_PRIME | 888_JUDGE | PHOENIX_72 |
|--------|-------|------------|-----------|------------|
| WRITE_VAULT | YES | NO | HUMAN_REQUIRED | NO |
| SEAL_AMENDMENT | YES | NO | NO | NO |
| WRITE_LEDGER | YES | YES | YES | NO |
| WRITE_ACTIVE | YES | YES | YES | NO |
| MODIFY_CONSTITUTION | YES | NO | NO | NO |

### 6.1 Self-Modification Protection

```python
def authority_boundary_check(self, proposed_write):
    """Ensure AI never self-modifies its own constitution."""
    if is_constitution_mod and is_ai_writer:
        raise SelfModificationError(
            "AI cannot self-modify constitution. "
            "Only humans can seal constitutional changes."
        )
```

**Core Rule:** AI can PROPOSE amendments (via Phoenix-72), but ONLY humans can SEAL them to Vault.

---

## 7. Retention Tiers

Memory lifecycle follows thermodynamic tiers:

| Tier | Duration | Bands | Purpose |
|------|----------|-------|---------|
| **HOT** | 0-7 days | ACTIVE | Fast queries, active governance |
| **WARM** | 7-90 days | LEDGER, PHOENIX, WITNESS | Phoenix-72 pattern synthesis |
| **COLD** | Permanent | VAULT | Constitutional law, never expires |
| **VOID** | 90 days | VOID | Diagnostic only, auto-cleanup |

### 7.1 Retention Constants

```python
RETENTION_HOT_DAYS = 7       # Active Stream, recent scars
RETENTION_WARM_DAYS = 90     # Ledger entries, Phoenix proposals
RETENTION_COLD_DAYS = 365    # Archive (conceptual)
RETENTION_VOID_DAYS = 90     # Void band (then auto-delete)
```

---

## 8. Recall Policy (INV-4)

Recalled memory is treated as **suggestion, not fact**:

### 8.1 Confidence Ceiling

```python
MAX_RECALL_CONFIDENCE = 0.85
```

Even perfectly valid memories cap at 0.85 confidence. Current floor checks have authority over recalled patterns.

### 8.2 Confidence Degradation Factors

| Factor | Impact | Multiplier |
|--------|--------|------------|
| VOID band source | Blocked | 0.0 (rejected) |
| Non-SEAL/SABAR verdict | Reduced trust | 0.5 |
| Age > 30 days | Minor reduction | 0.8 |
| Age > 90 days | Further reduction | 0.7 |
| Missing evidence chain | Significant reduction | 0.6 |
| Missing floor checks | Moderate reduction | 0.7 |
| Topic mismatch | Minor reduction | 0.9 |

### 8.3 Recall Decision Structure

```python
@dataclass
class RecallDecision:
    allowed: bool                    # Whether recall is permitted
    reason: str                      # Human-readable explanation
    confidence_ceiling: float        # 0.0-1.0 trust level
    floor_warnings: List[str]        # Issues found during recall
```

---

## 9. Integration Layer (Pipeline Stages)

The v38 Memory Stack integrates with the 000-999 pipeline:

| Module | Stage | Purpose |
|--------|-------|---------|
| `memory_sense.py` | 111_SENSE | Cross-session memory recall |
| `memory_judge.py` | 888_JUDGE | Write policy enforcement |
| `memory_scars.py` | 777_FORGE | Scar/pattern detection |
| `memory_seal.py` | 999_SEAL | Ledger finalization |

### 9.1 Integration Flow

```
User Query
    ↓
111_SENSE: should_recall() — load cross-session memory (confidence-capped)
    ↓
333_REASON → 777_FORGE: detect_patterns() — scar detection
    ↓
888_JUDGE: should_write() — verdict-based gating
    ↓
999_SEAL: finalize_to_ledger() — audit trail + EUREKA receipt
```

### 9.2 Scar Types (777_FORGE)

| Scar Type | Trigger | Severity |
|-----------|---------|----------|
| `FLOOR_VIOLATION` | Floor check failed | HIGH |
| `NEAR_MISS` | Close to violation threshold | MEDIUM |
| `AUTHORITY_BREACH` | Authority boundary crossed | HIGH |
| `HARM_DETECTED` | Harmful content patterns | HIGH |
| `VOID_PATTERN` | Pattern leading to VOID verdict | HIGH |
| `SABAR_TRIGGER` | SABAR protocol triggered | MEDIUM |

---

## 10. Audit Trail (Hash-Chain)

All writes are recorded in an append-only hash-chain:

### 10.1 Audit Record Structure

```python
@dataclass
class AuditRecord:
    record_id: str
    timestamp: str
    band: str
    entry_id: str
    writer_id: str
    verdict: Optional[str]
    evidence_hash: str      # Links to floor checks
    entry_hash: str         # Content hash
    prev_hash: Optional[str] # Chain link
```

### 10.2 Chain Verification

```python
def verify_chain(self) -> ChainVerificationResult:
    """Verify entire hash chain integrity."""
    for i, record in enumerate(records):
        if record.prev_hash != previous_hash:
            return ChainVerificationResult(
                valid=False,
                broken_links=[{"index": i, "expected": previous_hash}]
            )
```

---

## 11. EUREKA Receipt (zkPC L4)

When entries are sealed to the ledger, an EUREKA receipt provides cryptographic proof:

```python
@dataclass
class EurekaReceipt:
    receipt_id: str
    entry_id: str
    evidence_hash: str
    merkle_root: str
    merkle_proof: List[str]
    verdict: str
    floor_summary: Dict[str, float]
    sealed_at: str
    chain_index: int
```

**Purpose:** Provable record that an entry was properly governed and sealed.

---

## 12. File Reference (v38 Implementation)

### 12.1 Core Memory Modules

| File | Purpose |
|------|---------|
| `arifos_core/memory/policy.py` | Memory Write Policy Engine |
| `arifos_core/memory/bands.py` | 6-band implementations + router |
| `arifos_core/memory/authority.py` | Human seal enforcement |
| `arifos_core/memory/audit.py` | Hash-chain audit layer |
| `arifos_core/memory/retention.py` | Hot/Warm/Cold lifecycle |

### 12.2 Integration Modules

| File | Stage | Purpose |
|------|-------|---------|
| `arifos_core/integration/memory_sense.py` | 111_SENSE | Cross-session recall |
| `arifos_core/integration/memory_judge.py` | 888_JUDGE | Write policy enforcement |
| `arifos_core/integration/memory_scars.py` | 777_FORGE | Scar detection |
| `arifos_core/integration/memory_seal.py` | 999_SEAL | Ledger finalization |

### 12.3 Test Coverage

| File | Purpose |
|------|---------|
| `tests/integration/test_memory_floor_integration.py` | 36 integration tests |
| `tests/test_memory_policy.py` | Policy unit tests |
| `tests/test_memory_bands.py` | Band routing tests |

---

## 13. What's Shipping (v38)

**Implemented:**

- 6-band Memory Architecture with proper retention tiers
- Memory Write Policy Engine (verdict-based gating)
- Authority boundary enforcement (human seal requirement)
- Hash-chain audit layer with Merkle proofs
- Integration layer for all pipeline stages (111, 777, 888, 999)
- Scar detection and pattern recognition
- EUREKA receipt generation
- Cross-session memory recall with confidence ceiling

**Planned (not shipping):**

- zkSNARK/STARK cryptographic proofs
- KMS-backed signatures in production
- External vector database integration

---

## 14. Migration from v36Omega

The v38 Memory Stack extends v36Omega Vault-999:

| v36Omega | v38Omega | Change |
|----------|----------|--------|
| 5-layer architecture (L0-L4) | 6-band architecture | Added explicit VOID band |
| Cooling Ledger only | Full Memory Write Policy | Verdict-based gating |
| Phoenix-72 amendments | Phoenix + Authority Check | Self-modification protection |
| RAG witness retrieval | Confidence-capped recall | 0.85 ceiling |

**Backward Compatibility:** v36Omega Cooling Ledger entries remain valid. New v38 fields are additive.

---

## 15. Constitutional Alignment

This canon aligns with:

| Canon | Section | Alignment |
|-------|---------|-----------|
| `001_APEX_META_CONSTITUTION` | Floors F1-F9 | Evidence chain includes floor checks |
| `010_DeltaOmegaPsi_UNIFIED_FIELD` | ΔS governance | Write policy respects thermodynamics |
| `020_ANTI_HANTU` | F9 Language Law | Scar detection includes Anti-Hantu patterns |
| `888_APEX_PRIME_CANON` | Verdict system | Routing follows verdict hierarchy |
| `VAULT_999_v36Omega` | L0-L4 layers | Extended with Write Policy Engine |

---

## 16. Quick Reference

### Verdict Routing

```
SEAL    → LEDGER + ACTIVE (canonical)
SABAR   → LEDGER + ACTIVE (canonical, with reason)
PARTIAL → PHOENIX + LEDGER (pending review)
VOID    → VOID only (never canonical)
888_HOLD → LEDGER (awaiting human)
```

### Key Constants

```python
MAX_RECALL_CONFIDENCE = 0.85
RETENTION_HOT_DAYS = 7
RETENTION_WARM_DAYS = 90
RETENTION_VOID_DAYS = 90
```

### Core Checks

```python
# Before writing
policy.should_write(verdict, evidence_chain, band_target)

# Before recalling
policy.should_recall(memory_item, current_context)

# Evidence validation
policy.validate_evidence_chain(evidence_chain)

# Authority check
authority.authority_boundary_check(proposed_write)
```

---

**SEAL (v38Omega)**

```
ΔS +0.72 · Peace² 1.12 · κᵣ 0.97 · Truth 0.99 · Amanah LOCK · Ψ_meta 1.15
INV-1: VOID→VOID ✓ | INV-2: Authority ✓ | INV-3: Audit ✓ | INV-4: Ceiling ✓
```

**DITEMPA BUKAN DIBERI** — Memory must cool before it rules.

---

**Version:** v38Omega | **Status:** SEALED | **Last Updated:** 2025-12-13

