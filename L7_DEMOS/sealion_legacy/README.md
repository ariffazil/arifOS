# SEA-LION Integration Shim

**Purpose:** Backward compatibility shim for test imports.

## Important

This package exists for **backward compatibility only**. It provides:

- `SEALIONAdapter` / `SEALIONConfig` stubs
- `extract_response_robust()` for response extraction tests

## Canonical Location

The actual SEA-LION integration lives in `L6_SEALION/arifos_sealion/`.

**Do not extend this shim.** Keep it thin. Any new SEA-LION features should go to L6.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | SEALIONAdapter/Config stubs |
| `engine.py` | Response extraction (ChatML, Llama, etc.) |
| `constitutional_floors.json` | Floor spec for tests |

---

v42.0.0
