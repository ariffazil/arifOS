# Floor Enforcement Tests

**Scope:** Floor Validation & Response Enforcement
**Target:** `F4 Clarity`, `F6 Empathy`, `F9 Anti-Hantu`

This directory tests the **enforcement layer** that validates individual constitutional floors and integrates response validation.

---

## Test Files

| File | Floor | Description |
|------|-------|-------------|
| `test_f4_zlib_clarity.py` | F4 | Clarity measurement using zlib compression ratio (ΔS calculation) |
| `test_f6_empathy_split.py` | F6 | Empathy scoring with split accuracy for stakeholder analysis |
| `test_f9_negation_aware_v1.py` | F9 | Consciousness claim detection (Anti-Hantu) with negation awareness |
| `test_meta_select_integration.py` | - | Meta-selection integration for response routing |
| `test_risk_literacy.py` | - | Risk communication and literacy validation |
| `test_validate_response_full_integration.py` | All | Full response validation integrating all floors |

---

## Key Concepts

### F4 Clarity (ΔS ≥ 0)
Tests verify that responses **reduce confusion**, not increase it. Uses zlib compression ratio as entropy proxy.

### F6 Empathy (κᵣ ≥ 0.95)
Tests verify empathy scores correctly identify and serve the **weakest stakeholder**.

### F9 Anti-Hantu (C_dark < 0.30)
Tests detect and reject **fake empathy patterns** and consciousness claims:
- "I feel your pain" → BLOCKED
- "I truly understand" → BLOCKED
- "This sounds heavy" → ALLOWED

---

## Running Tests

```bash
# Run all enforcement tests
pytest tests/enforcement/ -v

# Run specific floor tests
pytest tests/enforcement/test_f4_zlib_clarity.py -v
pytest tests/enforcement/test_f6_empathy_split.py -v
pytest tests/enforcement/test_f9_negation_aware_v1.py -v
```

---

**Constitutional Floor:** F2-F9 (Enforcement Layer)
**DITEMPA BUKAN DIBERI**
