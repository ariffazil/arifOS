# 04_measurement - Metrics Layer

**Version:** v42.0 | **Status:** DRAFT

---

## Purpose

This layer defines the measurement system of arifOS:

- **GENIUS LAW** - G, C_dark, Psi metrics
- **Truth Polarity** - Clarifying vs obscuring truth

---

## Files

| File | Purpose |
|------|---------|
| `04_GENIUS_LAW_v42.md` | Core measurement metrics |

---

## Core Metrics

| Metric | Symbol | Range | SEAL Threshold |
|--------|--------|-------|----------------|
| Genius Index | G | [0, 1.2] | >= 0.80 |
| Dark Cleverness | C_dark | [0, 1] | < 0.30 |
| Vitality | Psi | [0, 2+] | >= 1.00 |

---

## Truth Polarity

| Polarity | Definition | Verdict |
|----------|------------|---------|
| Truth-Light | True + clarifying | SEAL |
| Shadow-Truth | True but obscuring | SABAR |
| Weaponized-Truth | True but harmful | VOID |
| False-Claim | Inaccurate | VOID |

---

## Dependencies

- `00_foundation/` - Physics
- `01_floors/` - Thresholds

## Dependents

- `02_actors/` - Engines use metrics
- `03_runtime/` - Pipeline uses metrics

---

**DITEMPA BUKAN DIBERI** - Forged, not given; truth must cool before it rules.
