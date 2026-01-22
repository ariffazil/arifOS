# Memory Bands v38 - Policy & Current State

**Version:** v38.0 (EUREKA)  
**Status:** EXTRACTION from existing codebase  
**Purpose:** Document the 6 Memory Bands, verdict routing, v38 Memory Write Policy Engine, and current implementation

---

## 1. The 6 Memory Bands

**Source:** `arifos_core/memory/bands.py`

Memory bands are governed storage tiers with different retention policies and write permissions.

### 1.1 Band Table

| Band | Purpose | Tier | Retention | Mutable | Human Seal | Canonical |
|------|---------|------|-----------|---------|------------|-----------|
| **VAULT** | Immutable constitution | COLD | Permanent | ❌ No | ✅ Required | ✅ Yes |
| **LEDGER** | Audit trail | WARM | 365 days | ❌ No | ❌ No | ✅ Yes |
| **ACTIVE** | Working memory | HOT | 7 days | ✅ Yes | ❌ No | ❌ No |
| **PHOENIX** | Amendment proposals | WARM | 90 days | ✅ Yes | ✅ For sealing | ❌ Until sealed |
| **WITNESS** | Observer context | WARM | 30 days | ✅ Yes | ❌ No | ❌ No |
| **VOID** | Rejected content | VOID | 90 days | ✅ Yes | ❌ No | ❌ NEVER |

**Module:** `arifos_core/memory/bands.py`

### 1.2 Band Enum

```python
class BandName(str, Enum):
    CCC = "CCC"
    BBB = "BBB"
    ACTIVE = "ACTIVE"
    PHOENIX = "PHOENIX"
    WITNESS = "WITNESS"
    VOID = "VOID"
```

### 1.3 Retention Tiers

**Source:** `arifos_core/memory/bands.py::RetentionTier`

```python
class RetentionTier(str, Enum):
    HOT = "HOT"      # weeks (7 days)
    WARM = "WARM"    # months (30-365 days)
    COLD = "COLD"    # years/permanent
    VOID = "VOID"    # 90 days then auto-delete
```

**Retention Days:**
- `RETENTION_HOT_DAYS = 7`
- `RETENTION_WARM_DAYS = 90`
- `RETENTION_COLD_DAYS = 365`
- `RETENTION_VOID_DAYS = 90`

---

## 2. Band Properties (Detailed)

**Source:** `arifos_core/memory/bands.py::BAND_PROPERTIES`

### 2.1 VAULT (Immutable Canon)

```python
"VAULT": {
    "mutable": False,
    "retention": RetentionTier.COLD,
    "retention_days": None,  # Permanent
    "requires_human_seal": True,
    "canonical": True,
}
```

**Purpose:** Constitutional law (L0), sealed amendments, governance rules

**Write Permission:** Only HUMAN and 888_JUDGE (for Phoenix-72 sealing)

**Read Access:** Universal (all stages)

**Storage:** `canon/` directory, version-controlled

---

### 2.2 LEDGER (Audit Trail)

```python
"LEDGER": {
    "mutable": False,
    "retention": RetentionTier.WARM,
    "retention_days": 365,
    "requires_human_seal": False,
    "canonical": True,
}
```

**Purpose:** Append-only audit log for all governance decisions

**Write Permission:** APEX_PRIME, 888_JUDGE

**Format:** JSONL (JSON Lines)

**File:** `cooling_ledger/L1_cooling_ledger.jsonl`

**Hash-Chained:** Yes (SHA-256)

---

### 2.3 ACTIVE (Working Memory)

```python
"ACTIVE": {
    "mutable": True,
    "retention": RetentionTier.HOT,
    "retention_days": 7,
    "requires_human_seal": False,
    "canonical": False,
}
```

**Purpose:** Session context, recent scars, ephemeral state

**Write Permission:** 111_SENSE, 222_REFLECT, 333_REASON, 777_FORGE, HUMAN

**Cleared:** On session exit or after 7 days

**Storage:** In-memory + temp files in `runtime/active/`

---

### 2.4 PHOENIX (Human-Sealed Amendments)

```python
"PHOENIX": {
    "mutable": True,
    "retention": RetentionTier.WARM,
    "retention_days": 90,
    "requires_human_seal": True,  # For sealing into VAULT
    "canonical": False,  # Until sealed
}
```

**Purpose:** Proposed amendments awaiting Phoenix-72 review

**Write Permission:** 888_JUDGE, PHOENIX_72, HUMAN

**Phoenix-72 Process:**
1. PARTIAL verdict → write to PHOENIX
2. Human review (up to 72 hours)
3. Approved → seal into VAULT
4. Rejected → decay to VOID

**Storage:** `cooling_ledger/proposed/` directory

---

### 2.5 WITNESS (Observer Context)

```python
"WITNESS": {
    "mutable": True,
    "retention": RetentionTier.WARM,
    "retention_days": 30,
    "requires_human_seal": False,
    "canonical": False,
}
```

**Purpose:** Soft evidence, embeddings, RAG context (NOT binding facts)

**Write Permission:** All stages (advisory data)

**Note:** Witness memory is **suggestion, not fact** (0.85 confidence ceiling on recalls)

**Storage:** Vector DB or `runtime/witness/`

---

### 2.6 VOID (Diagnostic Only)

```python
"VOID": {
    "mutable": True,
    "retention": RetentionTier.VOID,
    "retention_days": 90,
    "requires_human_seal": False,
    "canonical": False,  # NEVER canonical
}
```

**Purpose:** Rejected outputs, scar analysis, diagnostic data

**Write Permission:** APEX_PRIME, 777_FORGE

**Critical Invariant:** VOID verdicts **NEVER become canonical memory**

**Auto-Delete:** After 90 days (entropy dump)

**Storage:** `runtime/void/`

---

## 3. Verdict → Band Routing

**Source:** `arifos_core/memory/policy.py::VERDICT_BAND_ROUTING`

### 3.1 Routing Table

```python
VERDICT_BAND_ROUTING: Dict[str, List[str]] = {
    "SEAL": ["LEDGER", "ACTIVE"],      # Canonical + session
    "SABAR": ["LEDGER", "ACTIVE"],     # Canonical + session (with reason)
    "PARTIAL": ["PHOENIX", "LEDGER"],  # Queue for review + log
    "VOID": ["VOID"],                   # Diagnostic ONLY, never canonical
    "888_HOLD": ["LEDGER"],             # Log hold for audit
    "SUNSET": ["PHOENIX"],              # v38.2: Revocation pulse (LEDGER → PHOENIX)
}
```

### 3.2 Routing Logic

**SEAL Verdict:**
- Write to LEDGER (append-only audit)
- Write to ACTIVE (session context for recall)
- **Result:** Canonical memory + available for next query

**SABAR Verdict:**
- Write to LEDGER with `sabar_reason` field
- Write to ACTIVE for repair tracking
- **Result:** Pause for floor repair, logged for audit

**PARTIAL Verdict:**
- Write to PHOENIX (pending human review)
- Write to LEDGER (audit trail)
- **Result:** Awaiting Phoenix-72 decision (72-hour window)

**VOID Verdict:**
- Write to VOID band ONLY
- **NEVER** write to LEDGER or ACTIVE
- **Result:** Diagnostic retention, auto-delete after 90 days

**888_HOLD Verdict:**
- Write to LEDGER for audit
- Do NOT write to ACTIVE (not available for recall)
- **Result:** Logged, awaiting human approval

**SUNSET Verdict (v38.2):**
- Move previously sealed entry from LEDGER → PHOENIX
- Keep evidence chain intact
- **Result:** Lawful revocation when facts change

---

## 4. v38 Memory Write Policy Engine

**Module:** `arifos_core/memory/policy.py`

**Class:** `MemoryWritePolicy`

### 4.1 Core Philosophy

> "Memory is governance, not storage. What gets remembered is controlled by verdicts."

### 4.2 The 4 Core Invariants

**Source:** `arifos_core/memory/policy.py::MemoryWritePolicy` docstring

| # | Invariant | Enforcement |
|---|-----------|-------------|
| **INV-1** | VOID verdicts NEVER become canonical memory | `should_write()` gates all writes |
| **INV-2** | Authority boundary: humans seal law, AI proposes | `MemoryAuthorityCheck.authority_boundary_check()` |
| **INV-3** | Every write must be auditable (evidence chain) | `MemoryAuditLayer.record_write()` with hash-chain |
| **INV-4** | Recalled memory = suggestion, not fact | Confidence ceiling (0.85) on all recalls |

### 4.3 Verdict-Based Gating

**Function:** `MemoryWritePolicy.should_write(verdict, evidence_chain, band_target) -> WriteDecision`

**Logic:**
1. Check verdict type (VOID → reject if band != VOID)
2. Validate evidence chain (floor check present?)
3. Check band permissions (who can write to this band?)
4. Check human seal requirement (VAULT/PHOENIX sealing)
5. Return `WriteDecision` with `allowed: bool` and reason

**Example:**
```python
policy = MemoryWritePolicy()
decision = policy.should_write(
    verdict="VOID",
    evidence_chain={"floors_checked": True},
    band_target="LEDGER"
)
# decision.allowed = False
# decision.reason = "VOID verdicts cannot write to LEDGER"
```

### 4.4 Human Seal Enforcement

**Module:** `arifos_core/memory/authority.py`

**Class:** `MemoryAuthorityCheck`

**Method:** `authority_boundary_check(operation, band, writer_id) -> bool`

**Rules:**
- **VAULT writes:** Require `writer_id = "HUMAN"` or Phoenix-72 seal
- **PHOENIX sealing:** Require human approval (interactive prompt)
- **LEDGER writes:** AI-permitted (APEX_PRIME, 888_JUDGE)
- **ACTIVE writes:** AI-permitted (all stages)

**Enforcement Point:** Stage 999_SEAL before ledger finalization

---

## 5. Writer Permissions

**Source:** `arifos_core/memory/bands.py::WRITER_PERMISSIONS`

```python
WRITER_PERMISSIONS: Dict[str, List[str]] = {
    "APEX_PRIME": ["LEDGER", "VOID"],
    "111_SENSE": ["ACTIVE"],
    "222_REFLECT": ["ACTIVE"],
    "333_REASON": ["ACTIVE"],
    "777_FORGE": ["VOID", "ACTIVE"],
    "888_JUDGE": ["VAULT", "PHOENIX", "LEDGER"],
    "PHOENIX_72": ["PHOENIX"],
    "HUMAN": ["VAULT", "PHOENIX", "LEDGER", "ACTIVE"],
}
```

**Reasoning:**
- **APEX_PRIME:** Issues verdicts → writes to LEDGER
- **111_SENSE:** Recalls memory → reads VAULT/LEDGER/ACTIVE
- **777_FORGE:** Detects scars → writes to VOID (diagnostic)
- **888_JUDGE:** Constitutional judiciary → can seal to VAULT (after human approval)
- **HUMAN:** Absolute authority over all bands

---

## 6. MemoryBandRouter Class

**Module:** `arifos_core/memory/bands.py`

**Class:** `MemoryBandRouter`

### 6.1 Methods

**route_write(verdict, content, writer_id) -> List[str]:**
- Returns list of target bands based on verdict
- Enforces writer permissions
- Example: `route_write("SEAL", {...}, "APEX_PRIME") -> ["LEDGER", "ACTIVE"]`

**get_band(band_name) -> MemoryBand:**
- Returns band instance (VaultBand, LedgerBand, etc.)

**write_to_band(band_name, entry, writer_id) -> bool:**
- Write entry to specified band
- Checks permissions, validates entry
- Returns success/failure

---

## 7. Phoenix-72 Finalization Process

**Canon:** `canon/05_COOLING_LEDGER_PHOENIX_v38Omega.md`

**Timeline:**
1. **t=0:** PARTIAL verdict issued, write to PHOENIX + LEDGER
2. **t<72h:** Human reviews proposed amendment
3. **t=72h:** Decision required:
   - **Approved:** Seal to VAULT (becomes canonical law)
   - **Rejected:** Decay to VOID (entropy dump)
   - **No action:** Automatic decay to VOID (entropy rot)

**v38.2 Scheduler:**
- `SABAR_TIMEOUT_HOURS = 24` (SABAR → PARTIAL)
- `PHOENIX_LIMIT_HOURS = 72` (PARTIAL → VOID)

**Enforcement:** `arifos_core/kernel.py::check_entropy_rot()`

---

## 8. Memory Entry Dataclass

**Source:** `arifos_core/memory/bands.py::MemoryEntry`

```python
@dataclass
class MemoryEntry:
    entry_id: str
    band: str
    content: Dict[str, Any]
    timestamp: str
    writer_id: str
    verdict: Optional[str] = None
    evidence_hash: Optional[str] = None
    prev_hash: Optional[str] = None
    hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Deserialize from storage"""
```

---

## 9. Test Files

**Memory Band Tests:**
- `tests/integration/test_memory_band_routing_v38.py` — Verdict → band routing
- `tests/integration/test_memory_floor_integration.py` — Floor + memory integration (36 tests)
- `tests/test_memory_bands.py` — Band properties and permissions

**Policy Tests:**
- `tests/integration/test_memory_policy_spec_alignment.py` — Policy ↔ spec alignment
- `tests/test_policy.py` — MemoryWritePolicy unit tests

**Integration Tests:**
- `tests/integration/test_memory_integration_v38_eureka.py` — Full pipeline + memory
- `tests/integration/test_memory_eureka_comprehensive_v38.py` — EUREKA comprehensive (36 tests)

**Test Assertions (Key):**
- VOID verdicts never write to LEDGER or ACTIVE
- SEAL verdicts always write to both LEDGER and ACTIVE
- PHOENIX entries require human seal to move to VAULT
- Recalled memory has confidence ceiling (0.85)
- Evidence chain present for all writes

---

## 10. References

**Canon:**
- `canon/07_CCC/ARIFOS_MEMORY_STACK_v38Omega.md` — Memory stack law
- `canon/05_COOLING_LEDGER_PHOENIX_v38Omega.md` — Phoenix-72 spec

**Spec:**
- `spec/pipeline_v38Omega.yaml` — Verdict routing spec
- `spec/arifos_v38_2.yaml` — v38.2 time governance

**Docs:**
- `docs/MEMORY_ARCHITECTURE.md` — Memory system overview
- `docs/MEMORY_WRITE_POLICY.md` — Write policy details
- `docs/arifOS-MEMORY-FORGING-DEEPRESEARCH.md` — EUREKA design

**Code:**
- `arifos_core/memory/bands.py` — 6 band implementations + router
- `arifos_core/memory/policy.py` — Memory Write Policy Engine
- `arifos_core/memory/authority.py` — Human seal enforcement
- `arifos_core/memory/audit.py` — Hash-chain audit layer
- `arifos_core/memory/retention.py` — Hot/Warm/Cold/Void lifecycle
- `arifos_core/kernel.py` — v38.2 entropy rot + SUNSET

---

**END OF DOCUMENT 4**

