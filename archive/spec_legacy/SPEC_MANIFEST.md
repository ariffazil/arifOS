# SPEC_MANIFEST.md

**Purpose:** Declares the canonical specification version for arifOS runtime.

---

## Current Canonical Version

| Attribute | Value |
|-----------|-------|
| **Spec Version** | `v38_3_omega` (v38.3Ω) |
| **Kernel Version** | `42.0.0` |
| **Status** | PRODUCTION |
| **Effective Date** | 2025-12-15 |

---

## Specification Files

### Constitutional Floors (F1-F9)

| File | Purpose | Status |
|------|---------|--------|
| `constitutional_floors_v38Omega.json` | Floor thresholds | CANONICAL |

### GENIUS LAW

| File | Purpose | Status |
|------|---------|--------|
| `genius_law_v38Omega.json` | G, C_dark, Ψ formulas | CANONICAL |

### Pipeline (000→999)

| File | Purpose | Status |
|------|---------|--------|
| `pipeline_v38Omega.yaml` | Stage definitions | CANONICAL |

### W@W Federation

| File | Purpose | Status |
|------|---------|--------|
| `waw_prompt_floors_v38Omega.json` | W@W agent floors | CANONICAL |

### Cooling Ledger & Phoenix

| File | Purpose | Status |
|------|---------|--------|
| `cooling_ledger_phoenix_v38Omega.json` | Audit trail config | CANONICAL |

---

## Version History

| Version | Status | Notes |
|---------|--------|-------|
| `v38_3_omega` | CANONICAL | Memory as Law (EUREKA) |
| `v38_2_omega` | STABLE | Time as Governor |
| `v38_1_omega` | ARCHIVED | Initial v38 |
| `v36_3_omega` | ARCHIVED | Pre-EUREKA |

---

## Amendment Process (Phoenix-72)

To change a spec threshold:

1. **Propose** — Create amendment in `canon/07_CCC/`
2. **Cool** — 72-hour review period
3. **Witness** — Requires F3 Tri-Witness (human + AI + evidence)
4. **Seal** — Human approval via `arifos-seal-canon`
5. **Bump** — Update this manifest + `pyproject.toml`

**Rule:** Spec changes require Phoenix-72 cooling period. No exceptions.

---

## Loading Specs in Code

```python
from arifos_core.enforcement.metrics import _load_floors_spec_v38

spec = _load_floors_spec_v38()
print(spec["version"])  # "v38.3Omega"
```

---

## Alignment Tests

```bash
# Verify code matches spec
pytest tests/test_*_v38_alignment.py -v
```

---

**DITEMPA BUKAN DIBERI** — Spec is law. Code follows spec.

