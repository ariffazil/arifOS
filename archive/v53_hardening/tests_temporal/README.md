# Temporal & Freshness Tests

**Scope:** Temporal Decay, Evidence Freshness, Time-Based Governance
**Target:** Freshness Policy, Temporal Intelligence

This directory tests the **temporal layer** that governs how evidence confidence decays over time and how temporal reasoning affects decisions.

---

## Test Files

| File | Description |
|------|-------------|
| `test_freshness.py` | Exponential decay and humility expansion over time |
| `test_temporal_intelligence.py` | Temporal reasoning and time-aware decision making |

---

## Key Concepts

### Freshness Decay
Evidence confidence decays exponentially with age:
```
confidence(t) = initial_confidence × e^(-λt)
```

Where:
- `t` = time since evidence creation
- `λ` = decay constant (domain-specific)

### Humility Expansion (F7)
Uncertainty increases with temporal distance:
- Recent events: Ω₀ = 0.03 (3% uncertainty)
- Older events: Ω₀ → 0.05 (5% uncertainty)
- Ancient events: Ω₀ > 0.05 (requires explicit acknowledgment)

### Temporal Governance
Time-sensitive queries require:
- Recency verification
- Freshness thresholds
- Explicit staleness warnings

---

## Running Tests

```bash
# Run all temporal tests
pytest tests/temporal/ -v

# Run freshness tests
pytest tests/temporal/test_freshness.py -v

# Run temporal intelligence tests
pytest tests/temporal/test_temporal_intelligence.py -v
```

---

**Constitutional Floor:** F7 (Humility), F2 (Truth)
**DITEMPA BUKAN DIBERI**
