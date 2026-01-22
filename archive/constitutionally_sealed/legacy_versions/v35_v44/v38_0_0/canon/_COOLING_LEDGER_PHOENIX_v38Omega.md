# COOLING LEDGER & PHOENIX-72 v38Omega

**arifOS v38 Cooling Ledger & Phoenix-72 Amendment Engine — Constitutional Memory Law**

```
+=============================================================================+
|  COOLING LEDGER & PHOENIX-72 — Memory Governance v38Omega                   |
|  "Truth must cool before it rules."                                         |
+=============================================================================+
|  Zone:        05_MEMORY                                                     |
|  Version:     v38Omega                                                      |
|  Status:      SEALED                                                        |
|  Extends:     07_CCC/ARIFOS_MEMORY_STACK_v38Omega.md                   |
|  Runtime:     arifos_core/memory/*.py                                       |
+=============================================================================+
```

---

## 1. Purpose

This canon formalizes the **Cooling Ledger** and **Phoenix-72 Amendment Engine** — the two core mechanisms that govern memory lifecycle and constitutional amendment in arifOS.

**Cooling Ledger:** Append-only audit trail with hash-chain integrity. All governed interactions leave evidence.

**Phoenix-72:** The 72-hour scar-to-amendment workflow. Patterns emerge from scars, amendments cool before canonization.

**Core Principle:** DITEMPA BUKAN DIBERI — Forged, not given. Memory must cool before it rules.

---

## 2. Cooling Ledger

### 2.1 Architecture

The Cooling Ledger is an append-only JSONL audit log providing:

1. **Hash-chain integrity** — Each entry links to previous via SHA3-256
2. **Evidence traceability** — Every entry traces back to floor checks
3. **Crash recovery** — HeadState tracking for fast chain verification
4. **Hot/Warm rotation** — 7-day hot segment with archive rotation

### 2.2 Ledger Entry Schema

```python
@dataclass
class LedgerEntry:
    ledger_version: str         # "v38Omega"
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

### 2.3 Hash-Chain Integrity

Every entry contains:
- `prev_hash`: SHA3-256 of previous entry (null for first)
- `entry_hash`: SHA3-256 of current entry content

```python
def _compute_hash(entry: Dict[str, Any]) -> str:
    """Compute SHA3-256 hash excluding hash fields."""
    excluded = {"hash", "entry_hash", "kms_signature", "kms_key_id"}
    data = {k: v for k, v in entry.items() if k not in excluded}
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha3_256(canonical.encode("utf-8")).hexdigest()
```

### 2.4 HeadState (Crash Recovery)

```python
@dataclass
class HeadState:
    last_entry_hash: Optional[str]  # For fast chain verification
    entry_count: int                # Total entries
    last_timestamp: Optional[str]   # Most recent timestamp
    epoch: str                      # "v38"
```

On startup, compare `HeadState.last_entry_hash` with actual last entry for quick integrity check.

### 2.5 Fail-Open Hardening

The v37+ ledger enforces fail-open hardening:

```python
class LedgerConfigV37:
    fail_behavior: str = "SABAR_HOLD_WITH_LOG"
    # Options:
    # - SABAR_HOLD_WITH_LOG: Return failure (caller triggers SABAR/HOLD)
    # - SILENT_FAIL: Log warning and return failure
    # - RAISE: Raise exception
```

**Rule:** Never silently return success if write failed. Ledger failures trigger SABAR/HOLD.

---

## 3. Verdict → Band Routing

Verdicts route to specific memory bands:

| Verdict | Target Bands | Canonical? | Notes |
|---------|--------------|------------|-------|
| **SEAL** | LEDGER, ACTIVE | YES | Full canonical memory + session state |
| **SABAR** | LEDGER, ACTIVE | YES | Canonical with failure reason logged |
| **PARTIAL** | PHOENIX, LEDGER | PENDING | Queued for Phoenix-72 review |
| **VOID** | VOID **only** | **NO** | Diagnostic retention, never canonical |
| **888_HOLD** | LEDGER | PENDING | Logged, awaiting human approval |

### 3.1 Routing Code

```python
VERDICT_BAND_ROUTING = {
    "SEAL": ["LEDGER", "ACTIVE"],      # Canonical + session
    "SABAR": ["LEDGER", "ACTIVE"],     # Canonical + session (with reason)
    "PARTIAL": ["PHOENIX", "LEDGER"],  # Queue for review + log
    "VOID": ["VOID"],                  # Diagnostic ONLY, never canonical
    "888_HOLD": ["LEDGER"],            # Log hold for audit
}
```

### 3.2 VOID Enforcement (INV-1)

```python
if verdict == "VOID":
    if band_target not in (None, "VOID"):
        raise MemoryPolicyViolation(
            "VOID verdicts can ONLY be written to Void band (never canonical)"
        )
```

---

## 4. Phoenix-72 Amendment Engine

### 4.1 Purpose

Phoenix-72 is the constitutional amendment engine that:
1. Collects scars from floor failures over 72 hours
2. Synthesizes patterns from recurring failures
3. Drafts amendments to prevent recurrence
4. Applies amendments after human approval

### 4.2 Phoenix Workflow

```
Scar Detection (777_FORGE)
    ↓
Pattern Synthesis (72-hour window)
    ↓
Amendment Draft
    ↓
Human Review (888_HOLD)
    ↓
Canon Update (999_SEAL)
```

### 4.3 Phoenix Entities

```python
@dataclass
class Scar:
    timestamp: float
    floor_failures: List[str]
    reason: str
    ledger_ref: Dict[str, Any]

@dataclass
class PhoenixAmendment:
    id: str                      # "PHOENIX-72-{timestamp}"
    applied_at: str              # ISO-8601
    reason: str                  # What pattern was detected
    tri_witness: float           # Tri-Witness score
    delta_s_gain: float          # Expected clarity improvement
    peace2: float                # Peace² impact
    changes: Dict[str, Any]      # Proposed floor changes
    evidence: List[Dict[str, Any]]  # Scar evidence
```

### 4.4 Phoenix Phases

**Phase 1 — Scar Capture:**
```python
def collect_scars(self, hours: float = 72.0) -> List[Scar]:
    """Collect floor failures from last N hours."""
    for entry in self.ledger.iter_recent(hours=hours):
        failures = entry.get("floor_failures", [])
        if failures:
            scars.append(Scar(...))
    return scars
```

**Phase 2 — Pattern Synthesis:**
```python
def synthesize_pattern(self, scars: List[Scar]) -> Optional[Dict[str, Any]]:
    """Group scars by failure type, find dominant pattern."""
    # Primitive heuristic: group by first failure
    groups = {}
    for scar in scars:
        key = scar.floor_failures[0]
        groups.setdefault(key, []).append(scar)

    # Pick largest cluster as pattern
    dominant = max(groups.values(), key=len)
    return {
        "dominant_failure": dominant[0].floor_failures[0],
        "count": len(dominant),
        "evidence": [s.ledger_ref for s in dominant],
    }
```

**Phase 3 — Draft Amendment:**
```python
def draft_amendment(self, pattern: Dict[str, Any]) -> PhoenixAmendment:
    """Create amendment proposal based on pattern."""
    # Example: tighten truth_min if Truth floor failing
    if "Truth" in pattern["dominant_failure"]:
        floors["truth_min"] = min(0.999, floors["truth_min"] + 0.005)
    return PhoenixAmendment(...)
```

**Phase 4-5 — Apply Amendment:**
```python
def apply_amendment(self, amendment: PhoenixAmendment) -> None:
    """Apply amendment to Vault-999 and log to Ledger."""
    self.vault.update_floors(
        new_floors=amendment.changes["floors"],
        phoenix_id=amendment.id,
    )
    self.ledger.append(ledger_entry)  # verdict="AMEND"
```

---

## 5. Scar & Witness Lifecycle

### 5.1 Scar Kinds

| Kind | Description | Can Affect Verdicts? |
|------|-------------|---------------------|
| **WITNESS** | Unsigned local observations | NO (early warning only) |
| **SCAR** | Signed canonical negative constraints | YES |

### 5.2 Scar Status Lifecycle

```
PROPOSED → SEALED → HEALED
                  → DEPRECATED
```

| Status | Description |
|--------|-------------|
| **PROPOSED** | Newly observed, awaiting signature |
| **SEALED** | Signed, actively enforced |
| **HEALED** | No longer enforced, preserved in history |
| **DEPRECATED** | Removed from enforcement entirely |

### 5.3 Scar Record Schema

```python
@dataclass
class ScarRecord:
    scar_id: str                    # "SCAR-{hash}"
    pattern_text: str               # What pattern was detected
    pattern_hash: str               # SHA-256 of pattern
    severity: SeverityLevel         # S1 | S2 | S3 | S4
    floors: List[str]               # Affected floors [F1, F6, ...]
    epochs: List[str]               # Version epochs ["v38"]
    evidence: ScarEvidence          # Ledger hashes, external refs
    phoenix_proposal_ids: List[str] # Related Phoenix proposals
    status: ScarStatus              # PROPOSED | SEALED | HEALED | DEPRECATED
    signature: str                  # Required for canonical scars
    created_at: str
    created_by: str
    sealed_by: Optional[str]
    updated_at: Optional[str]
```

### 5.4 Severity Weights

| Severity | Weight | Description |
|----------|--------|-------------|
| **S1** | 1.0 | Low impact |
| **S2** | 2.0 | Moderate impact |
| **S3** | 4.0 | High impact |
| **S4** | 8.0 | Critical impact |

### 5.5 Floor Pressure Calculation

```python
def compute_floor_pressure(self, floor: str) -> float:
    """Compute total scar pressure for a floor."""
    total = 0.0
    for scar in self._scars.values():
        if scar.status != "SEALED":
            continue
        if floor not in scar.floors:
            continue
        total += SEVERITY_WEIGHTS[scar.severity]
    return total
```

---

## 6. Retention Tiers

Memory lifecycle follows thermodynamic tiers:

| Tier | Duration | Bands | Purpose |
|------|----------|-------|---------|
| **HOT** | 0-7 days | ACTIVE | Fast queries, active governance |
| **WARM** | 7-90 days | LEDGER, PHOENIX, WITNESS | Phoenix-72 pattern synthesis |
| **COLD** | Permanent | VAULT | Constitutional law, never expires |
| **VOID** | 90 days | VOID | Diagnostic only, auto-cleanup |

### 6.1 Retention Constants

```python
RETENTION_HOT_DAYS = 7       # Active Stream, recent scars
RETENTION_WARM_DAYS = 90     # Ledger entries, Phoenix proposals
RETENTION_COLD_DAYS = 365    # Archive (conceptual)
RETENTION_VOID_DAYS = 90     # Void band (then auto-delete)
```

---

## 7. Integration Points

### 7.1 Pipeline Integration

| Module | Stage | Purpose |
|--------|-------|---------|
| `memory_sense.py` | 111_SENSE | Cross-session memory recall |
| `memory_judge.py` | 888_JUDGE | Write policy enforcement |
| `memory_scars.py` | 777_FORGE | Scar/pattern detection |
| `memory_seal.py` | 999_SEAL | Ledger finalization |

### 7.2 Integration Flow

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

---

## 8. File Reference

### 8.1 Core Modules

| File | Purpose |
|------|---------|
| `arifos_core/memory/cooling_ledger.py` | CoolingLedger, CoolingLedgerV37 implementation |
| `arifos_core/memory/phoenix72.py` | Phoenix-72 amendment engine |
| `arifos_core/memory/scar_manager.py` | Scar/Witness lifecycle management |
| `arifos_core/memory/scars.py` | Scar entity and ScarIndex |
| `arifos_core/memory/policy.py` | Memory Write Policy Engine |

### 8.2 Related Canon

| File | Purpose |
|------|---------|
| `canon/07_CCC/ARIFOS_MEMORY_STACK_v38Omega.md` | Full v38 Memory Stack |
| `canon/01_CONSTITUTIONAL_FLOORS_v38Omega.md` | Floor definitions |

---

## 9. Invariants

### INV-1: VOID → VOID Only
VOID verdicts can ONLY be written to the Void band. They NEVER become canonical memory.

### INV-2: Authority Boundary
Humans seal law, AI proposes. Phoenix-72 can draft amendments, but only humans can seal them to Vault.

### INV-3: Evidence Chain
Every memory write must include a valid evidence chain linking to floor checks.

### INV-4: Recall Confidence Ceiling
Recalled memory is capped at 0.85 confidence. Current floor checks have authority over recalled patterns.

---

## 10. Quick Reference

### Verdict Routing
```
SEAL    → LEDGER + ACTIVE (canonical)
SABAR   → LEDGER + ACTIVE (canonical, with reason)
PARTIAL → PHOENIX + LEDGER (pending review)
VOID    → VOID only (never canonical)
888_HOLD → LEDGER (awaiting human)
```

### Scar Lifecycle
```
WITNESS (unsigned) → PROPOSED → SEALED → HEALED/DEPRECATED
```

### Phoenix-72 Workflow
```
Scars (72h) → Pattern → Amendment Draft → Human Review → Canon Update
```

---

**SEAL (v38Omega)**

```
ΔS +0.72 · Peace² 1.12 · κᵣ 0.97 · Truth 0.99 · Amanah LOCK · Ψ_meta 1.15
```

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.

---

**Version:** v38Omega | **Status:** SEALED | **Last Updated:** 2025-12-13

