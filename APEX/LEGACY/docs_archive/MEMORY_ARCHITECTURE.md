# MEMORY_ARCHITECTURE.md — arifOS v38 Memory Stack

**Status:** SEALED | **Version:** v38 | **Canon:** ARIFOS_MEMORY_STACK_v36.3O.md

---

## Overview

arifOS memory is **governance, not storage**. The 6-band MemoryContext provides constitutional memory that:

1. Cannot be bypassed by the LLM
2. Maintains immutable law (VaultBand)
3. Preserves audit trail (LedgerBand)
4. Enables pattern learning through scars (WitnessBand)
5. **[v38]** Enforces verdict-based write gating via Memory Write Policy Engine

Memory MUST flow through APEX PRIME. No band may override constitutional floors.

---

## 1. Six Memory Bands

| Band | Code Symbol | Purpose | Retention |
|------|-------------|---------|-----------|
| **VAULT** | `VaultBand` | Read-only constitution snapshot (L0) | **PERMANENT** |
| **LEDGER** | `CoolingLedgerBand` | Hash-chained audit trail | WARM (90 days) |
| **ACTIVE** | `ActiveStreamBand` | Volatile working state | HOT (7 days) |
| **PHOENIX** | `PhoenixCandidatesBand` | Amendment proposals pending review | WARM (90 days) |
| **WITNESS** | `WitnessBand` | Soft evidence, scars collection | WARM (90 days) |
| **VOID** | `VoidBandStorage` | Diagnostic only, NEVER canonical | 90-day retention |

### Band Hierarchy

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

---

## 2. v38 Memory Write Policy Engine

### 2.1 Core Invariants

| # | Invariant | Enforcement |
|---|-----------|-------------|
| 1 | **VOID verdicts NEVER become canonical memory** | `MemoryWritePolicy.should_write()` gates all writes |
| 2 | **Authority boundary: humans seal law, AI proposes** | `MemoryAuthorityCheck.authority_boundary_check()` |
| 3 | **Every write must be auditable (evidence chain)** | `MemoryAuditLayer.record_write()` with hash-chain |
| 4 | **Recalled memory = suggestion, not fact** | Confidence ceiling (0.85) on all recalls |

### 2.2 v38 Components

| Component | File | Purpose |
|-----------|------|---------|
| `MemoryWritePolicy` | `arifos_core/memory/policy.py` | Verdict-based write gating |
| `MemoryBandRouter` | `arifos_core/memory/bands.py` | Routes writes to correct bands |
| `MemoryAuthorityCheck` | `arifos_core/memory/authority.py` | Human seal enforcement |
| `MemoryAuditLayer` | `arifos_core/memory/audit.py` | Hash-chain integrity verification |
| `MemoryRetentionManager` | `arifos_core/memory/retention.py` | Hot/Warm/Cold lifecycle |

### 2.3 Verdict → Band Routing

| Verdict | Target Band(s) | Notes |
|---------|----------------|-------|
| SEAL | LEDGER, ACTIVE | Canonical memory, full audit |
| PARTIAL | ACTIVE, PHOENIX | Pending review |
| 888_HOLD | ACTIVE | Requires human approval for LEDGER |
| VOID | **VOID only** | NEVER canonical |
| SABAR | LEDGER, ACTIVE | Logged but requires remediation |

```python
# From policy.py — Verdict routing logic
VERDICT_BAND_ROUTING = {
    "SEAL": [MemoryBandTarget.LEDGER, MemoryBandTarget.ACTIVE],
    "SABAR": [MemoryBandTarget.LEDGER, MemoryBandTarget.ACTIVE],
    "PARTIAL": [MemoryBandTarget.ACTIVE, MemoryBandTarget.PHOENIX],
    "VOID": [MemoryBandTarget.VOID],  # ONLY VOID!
    "888_HOLD": [MemoryBandTarget.ACTIVE, MemoryBandTarget.PHOENIX],
    "HOLD": [MemoryBandTarget.ACTIVE, MemoryBandTarget.PHOENIX],
}
```

---

## 3. Integration Layer (v38)

### 3.1 Pipeline Integration Modules

| Module | Stage | Purpose |
|--------|-------|---------|
| `memory_sense.py` | 111_SENSE | Cross-session memory recall |
| `memory_judge.py` | 888_JUDGE | Write policy enforcement |
| `memory_scars.py` | 777_FORGE | Scar/pattern detection |
| `memory_seal.py` | 999_SEAL | Ledger finalization |

### 3.2 Flow: 111_SENSE (Memory Recall)

```python
# From integration/memory_sense.py
sense_integration = MemorySenseIntegration(write_policy, band_router)

# 1. Check if Vault consultation needed for constitutional topics
should_recall, reason = sense_should_recall_from_vault(query)

# 2. Load cross-session memory
result = sense_integration.load_cross_session_memory(RecallContext(query=query))

# 3. Inject with caveat (suggestions, not facts)
context = sense_integration.inject_context(result, existing_context)
```

**Key Point:** Recalled memories have a confidence ceiling of 0.85. They are SUGGESTIONS that must pass current floor checks.

### 3.3 Flow: 888_JUDGE (Write Gating)

```python
# From integration/memory_judge.py
judge_integration = MemoryJudgeIntegration(
    write_policy, band_router, authority_check, audit_layer
)

# Process verdict write
context = JudgeWriteContext(
    verdict="SEAL",
    content={"response": "..."},
    floor_scores=floor_scores,
)

result = judge_integration.process_verdict_write(context)
# Returns: JudgeWriteResult with success, target_band, evidence_hash
```

### 3.4 Flow: 777_FORGE (Scar Detection)

```python
# From integration/memory_scars.py
scars_integration = MemoryScarsIntegration(write_policy, band_router)

# Detect patterns that warrant scars
result = scars_integration.detect_patterns(ScarDetectionContext(
    content={"response": "..."},
    verdict="VOID",
    floor_scores=floor_scores,
))

# Returns: ScarDetectionResult with patterns_found, severity, proposals
```

**Scar Types:**
- `FLOOR_VIOLATION` — Floor check failed
- `NEAR_MISS` — Close to violation threshold
- `AUTHORITY_BREACH` — Authority boundary crossed
- `HARM_DETECTED` — Harmful content patterns
- `VOID_PATTERN` — Pattern leading to VOID verdict
- `SABAR_TRIGGER` — SABAR protocol triggered

### 3.5 Flow: 999_SEAL (Finalization)

```python
# From integration/memory_seal.py
seal_integration = MemorySealIntegration(
    write_policy, band_router, audit_layer, retention_manager
)

# Finalize to ledger
result = seal_integration.finalize_to_ledger(SealContext(
    entry_id="entry-123",
    verdict="SEAL",
    content={"response": "..."},
    evidence_hash="sha256...",
    floor_scores=floor_scores,
))

# Returns: SealResult with status (SEALED, VOID_ARCHIVED, PENDING, etc.)
# Also emits EUREKA receipt with Merkle proof
```

---

## 4. Authority Boundary Enforcement

### 4.1 Authority Matrix

| Action | HUMAN | APEX_PRIME | 888_JUDGE | PHOENIX_72 |
|--------|-------|------------|-----------|------------|
| WRITE_VAULT | ✓ | ✗ | HUMAN_REQUIRED | ✗ |
| SEAL_AMENDMENT | ✓ | ✗ | ✗ | ✗ |
| WRITE_LEDGER | ✓ | ✓ | ✓ | ✗ |
| WRITE_ACTIVE | ✓ | ✓ | ✓ | ✗ |
| MODIFY_CONSTITUTION | ✓ | ✗ | ✗ | ✗ |

### 4.2 Self-Modification Protection

```python
# From authority.py — Critical boundary check
def authority_boundary_check(self, proposed_write):
    """Ensure AI never self-modifies its own constitution."""
    if is_constitution_mod and is_ai_writer:
        raise SelfModificationError(
            "AI cannot self-modify constitution. Only humans can seal constitutional changes."
        )
```

**Key Rule:** AI can PROPOSE amendments (via Phoenix-72), but ONLY humans can SEAL them to Vault.

---

## 5. Retention Tiers (v38)

| Tier | Duration | Bands | Purpose |
|------|----------|-------|---------|
| **HOT** | 0-7 days | ACTIVE | Fast queries, active governance |
| **WARM** | 7-90 days | LEDGER, PHOENIX, WITNESS | Phoenix-72 pattern synthesis |
| **COLD** | Permanent | VAULT | Constitutional law, never expires |
| **VOID** | 90 days | VOID | Diagnostic only, auto-cleanup |

```python
# From retention.py
BAND_TIER_MAP = {
    BandName.CCC: RetentionTier.COLD,    # Permanent
    BandName.BBB: RetentionTier.WARM,   # 90 days
    BandName.ACTIVE: RetentionTier.HOT,    # 7 days
    BandName.PHOENIX: RetentionTier.WARM,  # 90 days
    BandName.WITNESS: RetentionTier.WARM,  # 90 days
    BandName.VOID: RetentionTier.VOID,     # 90 days, then delete
}
```

---

## 6. Hash-Chain & Audit Trail

### 6.1 Evidence Hash Computation

```python
# From audit.py
def compute_evidence_hash(floor_checks, verdict, timestamp):
    """Compute evidence hash tying memory write to governance origin."""
    evidence = {
        "floor_checks": floor_checks,
        "verdict": verdict,
        "timestamp": timestamp,
    }
    return hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()
```

### 6.2 Audit Record Structure

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

### 6.3 Chain Verification

```python
# From audit.py
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

## 7. EUREKA Receipt (zkPC L4)

When entries are sealed to the ledger, an EUREKA receipt is emitted:

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

**Purpose:** Cryptographic proof that an entry was properly governed and sealed. Can be verified independently.

---

## 8. Key Invariants Summary

### INV-1: VaultBand Immutability
VaultBand is frozen at initialization. Any modification attempt raises `AttributeError`.

### INV-2: VOID Never Canonical
VOID verdicts ONLY write to VOID band. `MemoryWritePolicy` enforces this gate.

### INV-3: Human Seal for Constitutional Changes
`MemoryAuthorityCheck` raises `HumanApprovalRequiredError` or `SelfModificationError` if AI attempts constitutional modification.

### INV-4: Evidence Chain Required
All writes must have valid evidence chain with floor_checks, verdict, timestamp, and hash.

### INV-5: Recalled Memory Has Confidence Ceiling
Cross-session memory recall capped at 0.85 confidence. Recalled data is SUGGESTION, not FACT.

---

## 9. File Reference (v38)

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

## 10. What's Shipping (v38)

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

**Version:** v38.0 | **Last Updated:** 2025-12-13


