# Meta-Search & Override Integration Tests

**Scope:** F11 Override Logic, Meta-Search Integration
**Target:** Command Authority Overrides

This directory tests **integration scenarios** involving meta-search and F11 command authority overrides.

---

## Test Files

| File | Description |
|------|-------------|
| `test_f11_override_constitutional.py` | F11 command authority override testing |

---

## Key Concepts

### F11 Command Authority
Certain operations require elevated authority:
- Destructive operations (delete, format)
- System modifications
- Credential access

### Override Logic
When an override is requested:
1. Verify authority token
2. Check nonce freshness
3. Validate scope
4. Log to audit trail (VAULT-999)

### Meta-Search Integration
Search operations that cross constitutional boundaries:
- External data sources
- Real-time information
- Potentially stale evidence

---

## Additional Files

This directory also contains integration reports:
- `TEST_META_SEARCH_*.md` - Meta-search test reports

---

## Running Tests

```bash
# Run F11 override tests
pytest tests/test_integration/ -v
```

---

**Constitutional Floor:** F11 (Command Auth), F12 (Injection Defense)
**DITEMPA BUKAN DIBERI**
