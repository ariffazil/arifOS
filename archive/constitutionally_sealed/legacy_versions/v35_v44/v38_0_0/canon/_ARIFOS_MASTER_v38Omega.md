# ARIFOS MASTER v38Omega

**arifOS v38 Constitutional Law Stack — Master Index**

```
+=============================================================================+
|  ARIFOS v38Omega LAW STACK — MASTER INDEX                                   |
|  "DITEMPA BUKAN DIBERI — Forged, not given"                                 |
+=============================================================================+
|  Version:     v38.0.0                                                       |
|  Status:      SEALED                                                        |
|  Release:     Formalization + Alignment Only                                |
|  Tests:       5 alignment suites (200+ assertions)                          |
+=============================================================================+
```

---

## 1. Overview

**v38Omega is a formalization release.** No runtime threshold changes. All existing behavior is preserved.

This release formalizes the arifOS constitutional law stack into a coherent canon→spec→code→tests pattern:

- **Canon (`.md`)**: Human-readable constitutional law
- **Spec (`.json`/`.yaml`)**: Machine-readable schemas and thresholds
- **Code (`arifos_core/`)**: Runtime implementation
- **Tests (`tests/test_*_v38_alignment.py`)**: Alignment verification

**Key Insight:** The spec is the single source of truth for thresholds. Canon documents the law. Tests verify alignment. Code implements.

---

## 2. v38Omega Law Layers

### Layer 1: Constitutional Floors (F1–F9)

| Type | File |
|------|------|
| Canon | `canon/01_CONSTITUTIONAL_FLOORS_v38Omega.md` |
| Spec | `spec/constitutional_floors_v38Omega.json` |
| Tests | `tests/test_constitutional_floors_v38_alignment.py` |

**Defines:** 9 constitutional floors (F1 Amanah through F9 Anti-Hantu), hard/soft classification, thresholds, verdict hierarchy.

### Layer 2: GENIUS LAW (G, C_dark, Ψ)

| Type | File |
|------|------|
| Canon | `canon/02_GENIUS_LAW_v38Omega.md` |
| Spec | `spec/genius_law_v38Omega.json` |
| Tests | `tests/test_genius_law_v38_alignment.py` |

**Defines:** GENIUS metrics (G ≥ 0.80, C_dark < 0.30), Truth Polarity classification, Ψ vitality calculation.

### Layer 3: 000→999 Pipeline

| Type | File |
|------|------|
| Canon | `canon/03_PIPELINE_v38Omega.md` |
| Spec | `spec/pipeline_v38Omega.yaml` |
| Tests | `tests/test_pipeline_v38_alignment.py` |

**Defines:** 10-stage metabolic pipeline (000 VOID through 999 SEAL), Class A/B routing, AAA Trinity integration.

### Layer 4: W@W Prompt Floors

| Type | File |
|------|------|
| Canon | `canon/04_WAW_PROMPT_FLOORS_v38Omega.md` |
| Spec | `spec/waw_prompt_floors_v38Omega.json` |
| Tests | `tests/test_waw_prompt_v38_alignment.py` |

**Defines:** W@W Federation (5 organs), @PROMPT governance, Anti-Hantu tiers, Truth Polarity, signal schemas.

### Layer 5: Cooling Ledger & Phoenix-72

| Type | File |
|------|------|
| Canon | `canon/05_COOLING_LEDGER_PHOENIX_v38Omega.md` |
| Spec | `spec/cooling_ledger_phoenix_v38Omega.json` |
| Tests | `tests/test_cooling_phoenix_v38_alignment.py` |

**Defines:** Hash-chain audit trail, verdict→band routing, scar lifecycle, Phoenix-72 amendment engine, retention tiers.

---

## 3. Memory Stack (Extended)

The v38 memory write policy is documented in:

| Type | File |
|------|------|
| Canon | `canon/07_CCC/ARIFOS_MEMORY_STACK_v38Omega.md` |
| Code | `arifos_core/memory/policy.py` |
| Code | `arifos_core/memory/bands.py` |
| Code | `arifos_core/memory/authority.py` |

**Defines:** 6 memory bands (VAULT, LEDGER, ACTIVE, PHOENIX, WITNESS, VOID), 4 invariants, EUREKA receipts.

---

## 4. Alignment Test Summary

| Test Suite | Tests | Coverage |
|------------|-------|----------|
| `test_constitutional_floors_v38_alignment.py` | ~40 | Floor thresholds, types, spec structure |
| `test_genius_law_v38_alignment.py` | ~35 | G/C_dark thresholds, Truth Polarity |
| `test_pipeline_v38_alignment.py` | ~30 | Stage definitions, Class A/B paths |
| `test_waw_prompt_v38_alignment.py` | 51 | W@W organs, Anti-Hantu, signals |
| `test_cooling_phoenix_v38_alignment.py` | 41 | Verdict routing, scar lifecycle |

**Run all alignment tests:**
```bash
pytest tests/test_*_v38_alignment.py -v
```

---

## 5. Key Invariants

### Memory Invariants (INV-1 through INV-4)

| ID | Statement |
|----|-----------|
| **INV-1** | VOID verdicts NEVER become canonical memory |
| **INV-2** | Humans seal law, AI proposes (authority boundary) |
| **INV-3** | Every write must be auditable (evidence chain) |
| **INV-4** | Recalled memory = suggestion, not fact (0.85 ceiling) |

### Floor Invariants

| Floor | Threshold | Type | Invariant |
|-------|-----------|------|-----------|
| F1 Amanah | LOCK | Hard | Irreversible actions require explicit consent |
| F2 Truth | ≥ 0.99 | Hard | Factual accuracy required |
| F7 Ω₀ | 0.03–0.05 | Hard | Uncertainty must be stated |
| F9 Anti-Hantu | PASS | Hard | No consciousness claims |

---

## 6. Verdict Hierarchy

```
SABAR > VOID > 888_HOLD > PARTIAL > SEAL

SABAR:    Floor violated. STOP. Repair first.
VOID:     Hard floor failed. Cannot proceed.
888_HOLD: High-stakes. Needs explicit confirmation.
PARTIAL:  Soft floor warning. Proceed with caution.
SEAL:     All floors pass. Approved to execute.
```

---

## 7. What v38Omega Does NOT Change

This is a **formalization release**. The following remain unchanged:

- ✅ All runtime thresholds (F1–F9, G, C_dark, Peace², κᵣ)
- ✅ Pipeline stage behavior
- ✅ W@W Federation voting logic
- ✅ Anti-Hantu patterns and severity
- ✅ Cooling Ledger hash-chain format
- ✅ Phoenix-72 amendment workflow
- ✅ Memory band routing

**Rule:** Do not change thresholds without an explicit law amendment through Phoenix-72.

---

## 8. Future Path (v39+)

| Version | Focus | Status |
|---------|-------|--------|
| **v38** | Formalization + Alignment | SEALED |
| **v39** | Body API (FastAPI Grid) | PLANNED |
| **v40** | Hands (MCP + IDE) | PLANNED |
| **v41** | Input Hygiene + zkPC Design | RESEARCH |

See `docs/FUTURE_PATH_v38_v42.md` for full roadmap.

---

## 9. Quick Reference

### Run All v38 Alignment Tests
```bash
pytest tests/test_*_v38_alignment.py -v
```

### Verify Ledger Integrity
```bash
arifos-verify-ledger
```

### Check Floor Status
```bash
python -m arifos_core.pipeline
```

---

## 10. Seal

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.

v38Omega seals the constitutional law stack:
- 5 canon documents
- 5 spec files
- 5 alignment test suites
- 200+ alignment assertions
- 0 runtime behavior changes

**Python decides. Claude proposes. Humans seal.**

---

**Version:** v38.0.0 | **Status:** SEALED | **Last Updated:** 2025-12-13

