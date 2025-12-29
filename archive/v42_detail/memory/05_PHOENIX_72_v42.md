# Phoenix-72 Amendment Engine (v42)

**Version:** v42.0 | **Status:** DRAFT | **Last Updated:** 2025-12-16
**Source:** Merged from v38Omega Phoenix-72

---

## 1. Purpose

Phoenix-72 is the constitutional amendment engine that:

1. Collects scars from floor failures over 72 hours
2. Synthesizes patterns from recurring failures
3. Drafts amendments to prevent recurrence
4. Applies amendments after human approval

---

## 2. Phoenix Workflow

```
Scar Detection (777_FORGE)
    |
Pattern Synthesis (72-hour window)
    |
Amendment Draft
    |
Human Review (888_HOLD)
    |
Canon Update (999_SEAL)
```

---

## 3. Phoenix Entities

### Scar

```python
@dataclass
class Scar:
    timestamp: float
    floor_failures: List[str]
    reason: str
    ledger_ref: Dict[str, Any]
```

### Amendment

```python
@dataclass
class PhoenixAmendment:
    id: str                      # "PHOENIX-72-{timestamp}"
    applied_at: str              # ISO-8601
    reason: str                  # What pattern was detected
    tri_witness: float           # Tri-Witness score
    delta_s_gain: float          # Expected clarity improvement
    peace2: float                # Peace^2 impact
    changes: Dict[str, Any]      # Proposed floor changes
    evidence: List[Dict[str, Any]]  # Scar evidence
```

---

## 4. Phoenix Phases

### Phase 1 - Scar Capture

```python
def collect_scars(self, hours: float = 72.0) -> List[Scar]:
    """Collect floor failures from last N hours."""
    for entry in self.ledger.iter_recent(hours=hours):
        failures = entry.get("floor_failures", [])
        if failures:
            scars.append(Scar(...))
    return scars
```

### Phase 2 - Pattern Synthesis

```python
def synthesize_pattern(self, scars: List[Scar]) -> Optional[Dict]:
    """Group scars by failure type, find dominant pattern."""
    groups = {}
    for scar in scars:
        key = scar.floor_failures[0]
        groups.setdefault(key, []).append(scar)
    return max(groups.values(), key=len)
```

### Phase 3 - Draft Amendment

```python
def draft_amendment(self, pattern: Dict) -> PhoenixAmendment:
    """Create amendment proposal based on pattern."""
    if "Truth" in pattern["dominant_failure"]:
        floors["truth_min"] = min(0.999, floors["truth_min"] + 0.005)
    return PhoenixAmendment(...)
```

### Phase 4-5 - Apply Amendment

```python
def apply_amendment(self, amendment: PhoenixAmendment) -> None:
    """Apply amendment to Vault and log to Ledger."""
    self.vault.update_floors(
        new_floors=amendment.changes["floors"],
        phoenix_id=amendment.id,
    )
    self.ledger.append(ledger_entry)  # verdict="AMEND"
```

---

## 5. Scar Lifecycle

```
WITNESS (unsigned) => PROPOSED => SEALED => HEALED/DEPRECATED
```

| Status | Description |
|--------|-------------|
| **PROPOSED** | Newly observed, awaiting signature |
| **SEALED** | Signed, actively enforced |
| **HEALED** | No longer enforced, preserved in history |
| **DEPRECATED** | Removed from enforcement entirely |

---

## 6. Severity Weights

| Severity | Weight | Description |
|----------|--------|-------------|
| **S1** | 1.0 | Low impact |
| **S2** | 2.0 | Moderate impact |
| **S3** | 4.0 | High impact |
| **S4** | 8.0 | Critical impact |

---

## 7. Human Seal Requirement

**Invariant:** AI can PROPOSE amendments via Phoenix-72, but ONLY humans can SEAL them to Vault.

This ensures arifOS remains a **governed tool**, not a self-governing entity.

---

**DITEMPA BUKAN DIBERI** - Forged, not given; truth must cool before it rules.
