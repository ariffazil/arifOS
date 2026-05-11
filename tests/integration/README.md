# Integration Tests

**Scope:** End-to-End Workflows
**Target:** Full System (API + Core + MCP)

These tests verify that the entire system works together as an organism.

**Scenarios Tested:**
1.  **The Happy Path:** 000 Ignition → 111 Sense → ... → 999 Seal (Verdict: SEAL).
2.  **The Rejection:** Dangerous input → 555 Empathy Veto → Verdict: VOID.
3.  **The Retry:** Confusing input → 333 Atlas Paradox → Verdict: SABAR.
4.  **The Body API:** HTTP Request (`/govern`) → JSON Response.

**Key Command:**
```bash
pytest -m integration
```
