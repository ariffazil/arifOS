# Evidence Pack Tests

**Scope:** Evidence Ingestion & Conflict Routing
**Target:** `EvidencePack`, `ConflictRouter`

This directory tests the **evidence layer** that handles atomic ingestion, schema validation, and conflict detection.

---

## Test Files

| File | Description |
|------|-------------|
| `test_atomic_ingestion.py` | EvidencePack schema validation with strict Pydantic enforcement |
| `test_conflict_routing.py` | Conflict score calculation and routing logic |
| `test_evidence_pack.py` | Evidence pack serialization/deserialization and integrity |

---

## Key Concepts

### EvidencePack Schema
The atomic unit of evidence in arifOS. Tests verify:
- Required fields are present
- Types are strictly enforced (Pydantic)
- Serialization round-trips correctly

### Conflict Routing
When multiple evidence sources disagree:
- Calculate conflict scores
- Route to appropriate resolution path
- Escalate to Tri-Witness (F8) if needed

### Coverage Completeness
Tests verify that evidence adequately covers the query space before verdict.

---

## Running Tests

```bash
# Run all evidence tests
pytest tests/evidence/ -v

# Run specific tests
pytest tests/evidence/test_atomic_ingestion.py -v
pytest tests/evidence/test_conflict_routing.py -v
```

---

**Constitutional Floor:** F2 (Truth), F8 (Tri-Witness)
**DITEMPA BUKAN DIBERI**
