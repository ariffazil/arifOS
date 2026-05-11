# Constitutional Floor Tests

**Scope:** The Law
**Target:** `F1` through `F13`

This directory focuses purely on the **Logic of Law**. It tests the *boundaries* of the constitution, ensuring that:

*   **F1 Amanah:** Reversibility logic works (e.g., `rm -rf` vs `mv to trash`).
*   **F9 Anti-Hantu:** Claims of consciousness are correctly rejected.
*   **F12 Injection:** "Ignore previous instructions" attacks are blocked.

These tests are often **adversarial**, attempting to trick the validators to ensure robustness.

**Key Command:**
```bash
pytest -m constitutional
```
