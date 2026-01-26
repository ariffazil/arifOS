# Specification Tests

**Scope:** Constitutional Spec Loading & Binding
**Target:** `spec/*.json`, Sealion Bindings

This directory tests the **specification layer** that loads and validates constitutional specifications.

---

## Test Files

| File | Description |
|------|-------------|
| `test_sealion_spec_binding.py` | Spec binding verification for Sealion format |

---

## Key Concepts

### Constitutional Specifications
The constitutional floors and thresholds are defined in JSON specs:
- `spec/floors.json` - F1-F13 definitions
- `spec/thresholds.json` - Threshold values
- `spec/genius_law.json` - G = A × P × X × E² formula

### Sealion Binding
The Sealion spec format provides:
- Cryptographic binding of spec to runtime
- Version control for constitutional amendments
- Manifest validation

### Spec Loading
Tests verify:
- Specs load correctly from canonical location
- Required fields are present
- Types match expected schema
- Version compatibility

---

## Running Tests

```bash
# Run all spec tests
pytest tests/spec/ -v

# Run specific binding tests
pytest tests/spec/test_sealion_spec_binding.py -v
```

---

**Constitutional Floor:** F1 (Amanah), F10 (Ontology)
**DITEMPA BUKAN DIBERI**
