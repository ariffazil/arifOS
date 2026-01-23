# MCP & Trinity Tests

**Scope:** The Interface & Tools
**Target:** `arifos.mcp.*`

This directory tests the **5-Tool Trinity** exposed to external agents:

1.  **`000_init`**:
    *   Session ignition.
    *   Authority validation (F11).
    *   Injection defense (F12).

2.  **`agi_genius` (Mind)**:
    *   Reasoning chains (SENSE/THINK/ATLAS).
    *   Truth threshold verification (F2).

3.  **`asi_act` (Heart)**:
    *   Empathy checks (F6).
    *   Safety gates (F5 Peace²).

4.  **`apex_judge` (Soul)**:
    *   Final verdict rendering (SEAL/VOID).
    *   Cryptographic sealing checks.

5.  **`999_vault`**:
    *   Immutable ledger writing.
    *   Audit trail verification.

**Key Command:**
```bash
pytest -m mcp
```
