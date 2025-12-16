# EUREKA Memory Stack (v42)

**Version:** v42.0 | **Status:** DRAFT | **Last Updated:** 2025-12-16
**Source:** Merged from v38Omega Memory Stack

---

## 1. Purpose

Memory in arifOS is **governance, not storage**. The Memory Stack provides:

1. **Verdict-based write gating** - Only approved verdicts write to canonical bands
2. **Evidence chain requirements** - Every write traces back to floor checks
3. **Authority boundary enforcement** - AI proposes, humans seal law
4. **Confidence-capped recall** - Recalled memory is suggestion, not fact

**Core Principle:** If APEX didn't approve it, memory doesn't record it as canonical.

---

## 2. The 4 Core Invariants

| Invariant | Statement | Enforcement |
|-----------|-----------|-------------|
| **INV-1** | VOID verdicts NEVER become canonical memory | `MemoryWritePolicy.should_write()` |
| **INV-2** | Authority boundary: humans seal law, AI proposes | `MemoryAuthorityCheck` |
| **INV-3** | Every write must be auditable (evidence chain) | `MemoryAuditLayer` |
| **INV-4** | Recalled memory = suggestion, not fact | Confidence ceiling (0.85) |

These invariants are **non-negotiable**. Hard floor violations trigger VOID.

---

## 3. Six Memory Bands

| Band | Code Symbol | Purpose | Retention |
|------|-------------|---------|-----------|
| **L0 VAULT** | `VaultBand` | Read-only constitution | PERMANENT (COLD) |
| **L1 LEDGER** | `CoolingLedgerBand` | Hash-chained audit trail | 90 days (WARM) |
| **L2 ACTIVE** | `ActiveStreamBand` | Volatile working state | 7 days (HOT) |
| **L3 PHOENIX** | `PhoenixCandidatesBand` | Amendment proposals | 90 days (WARM) |
| **L4 WITNESS** | `WitnessBand` | Soft evidence, scars | 90 days (WARM) |
| **L5 VOID** | `VoidBandStorage` | Diagnostic only, NEVER canonical | 90 days (auto-delete) |

### Band Hierarchy

```
VAULT (L0) - IMMUTABLE
    |
LEDGER (L1) - Append-only
    |
WITNESS (L4) - Soft evidence
    |
ACTIVE (L2) - Per-session
    |
PHOENIX (L3) - Pending seal
    |
VOID (L5) - NEVER CANONICAL
```

**Rule:** Higher bands cannot override lower bands. VAULT is supreme law.

---

## 4. Verdict => Band Routing

| Verdict | Target Bands | Canonical? | Notes |
|---------|--------------|------------|-------|
| **SEAL** | LEDGER, ACTIVE | YES | Canonical + session |
| **SABAR** | LEDGER, ACTIVE | YES | With failure reason |
| **PARTIAL** | PHOENIX, LEDGER | PENDING | Queued for review |
| **VOID** | VOID **only** | **NO** | Never canonical |
| **888_HOLD** | LEDGER | PENDING | Awaiting human |
| **SUNSET** | PHOENIX | PENDING | Re-trial required |

### VOID Enforcement (INV-1)

```python
if verdict == "VOID":
    if band_target not in (None, "VOID"):
        raise MemoryPolicyViolation(
            "VOID verdicts can ONLY be written to Void band"
        )
```

---

## 5. Evidence Chain Requirements

Every memory write must include:

| Field | Type | Purpose |
|-------|------|---------|
| `floor_checks` | List[Dict] | Floor check results from 888_JUDGE |
| `hash` | str | SHA-256 linking to verdict |
| `timestamp` | str | ISO 8601 timestamp |
| `verdict` | str | APEX verdict |

---

## 6. Authority Boundary (INV-2)

| Action | HUMAN | APEX | 888_JUDGE | PHOENIX_72 |
|--------|-------|------|-----------|------------|
| WRITE_VAULT | YES | NO | HUMAN_REQUIRED | NO |
| SEAL_AMENDMENT | YES | NO | NO | NO |
| WRITE_LEDGER | YES | YES | YES | NO |
| MODIFY_CONSTITUTION | YES | NO | NO | NO |

**Core Rule:** AI can PROPOSE amendments, but ONLY humans can SEAL them to Vault.

---

## 7. Recall Policy (INV-4)

### Confidence Ceiling

```python
MAX_RECALL_CONFIDENCE = 0.85
```

Even perfectly valid memories cap at 0.85 confidence.

### Confidence Degradation

| Factor | Multiplier |
|--------|------------|
| VOID band source | 0.0 (rejected) |
| Non-SEAL/SABAR verdict | 0.5 |
| Age > 30 days | 0.8 |
| Age > 90 days | 0.7 |
| Missing evidence chain | 0.6 |

---

## 8. Retention Tiers

| Tier | Duration | Bands | Purpose |
|------|----------|-------|---------|
| **HOT** | 0-7 days | ACTIVE | Fast queries |
| **WARM** | 7-90 days | LEDGER, PHOENIX, WITNESS | Pattern synthesis |
| **COLD** | Permanent | VAULT | Constitutional law |
| **VOID** | 90 days | VOID | Diagnostic, auto-cleanup |

---

## 9. EUREKA Receipt

When entries are sealed, an EUREKA receipt provides proof:

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
```

---

**DITEMPA BUKAN DIBERI** - Memory must cool before it rules.
