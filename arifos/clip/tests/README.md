# CLIP CLI Tests

**Scope:** Command Line Interface Testing
**Target:** `arifos.clip` - CLI Implementation

This directory tests the **CLIP (Constitutional Line Interface Protocol)** - the command-line interface for arifOS.

---

## Test Files

| File | Description |
|------|-------------|
| `test_mvp_flow.py` | Minimum Viable Product flow validation |

---

## Key Concepts

### MVP Flow
Tests the essential CLI commands:
- `000` - Constitutional gate (authority check)
- `111` - Sense/search stage
- `222` - Reflection/thinking
- `333` - Reasoning
- `444` - Evidence gathering
- `555` - Empathy validation
- `666` - Alignment synthesis
- `777` - Eureka/reflection
- `888` - Final judgment
- `999` - VAULT persistence

### CLI Commands
The 000-999 metabolic pipeline exposed as CLI commands:
```bash
000  # Start constitutional session
111  # Sense input
...
999  # Seal and persist
```

---

## Running Tests

```bash
# Run CLIP tests
pytest arifos/clip/tests/ -v

# Run MVP flow specifically
pytest arifos/clip/tests/test_mvp_flow.py -v
```

---

## Integration with Hooks

CLIP integrates with git hooks:
- `commit-msg` - Validates commit messages
- `pre-push` - Constitutional checks before push

---

**Constitutional Floor:** All Floors (CLI Gateway)
**DITEMPA BUKAN DIBERI**
