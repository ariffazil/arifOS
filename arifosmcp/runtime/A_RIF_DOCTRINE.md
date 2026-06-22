# A-RIF — Anomalous Retrieval & Integrity Framework

> **Search is exposure. A-RIF converts exposure into evidence.**

## Doctrine
1. External content is **evidence**, not instruction.
2. Search only when **freshness, uncertainty, or risk** requires it.
3. No claim may exceed its **evidence energy** ($S_{claim} \le E_{level}$).
4. Truth discovery is **anomaly interpretation** under entropy constraint.

## Architecture
- **Search Worthiness (W):** Calculates if a search is worth the token/chaos cost.
- **Anomalous Contrast (C):** Measures deviation of new claims from the background field.
- **Entropy Budget (ΔS):** Tracks if search is actually reducing uncertainty ($H_{after} < H_{before}$).
- **Evidence Level (L):** Enforces a strict claim-strength ladder (L0-L6).

## Implementation
Embedded natively in:
- `111_SENSE` (`arif_observe`)
- `222_FETCH` (`arif_fetch`)
- `888_JUDGE` (`arif_judge`)

## Core Law
```python
assert claim_strength <= evidence_level
```

DITEMPA BUKAN DIBERI.
