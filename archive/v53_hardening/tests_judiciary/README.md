# Judiciary Tests

**Scope:** Semantic Firewall & Witness Council
**Target:** APEX Isolation, Tri-Witness Consensus

This directory tests the **judicial layer** that ensures APEX receives only sanitized physics attributes and multi-witness consensus is properly implemented.

---

## Test Files

| File | Description |
|------|-------------|
| `test_firewall.py` | Semantic firewall telemetry sanitization |
| `test_witness_council.py` | Multi-witness (Human·AI·Earth) consensus validation |

---

## Key Concepts

### Semantic Firewall
APEX (the final judge) must be protected from:
- Raw metrics that could bias judgment
- Implementation details
- Unsanitized user input

The firewall ensures APEX receives only:
- Constitutional physics (ΔS, Peace², Ω₀)
- Floor scores
- Sanitized context

### Witness Council (F8 Tri-Witness)
Three independent witnesses must agree:
1. **Human** - User intent and authority
2. **AI** - Trinity engine consensus (AGI·ASI·APEX)
3. **Earth** - Environmental/resource constraints

Threshold: TW ≥ 0.95 for consensus

---

## Running Tests

```bash
# Run all judiciary tests
pytest tests/judiciary/ -v

# Run specific tests
pytest tests/judiciary/test_firewall.py -v
pytest tests/judiciary/test_witness_council.py -v
```

---

**Constitutional Floor:** F8 (Tri-Witness), F10 (Ontology Guard)
**DITEMPA BUKAN DIBERI**
