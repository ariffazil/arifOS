# VAULT Recovery Procedures (v50.3)

## 1. Governance Escalation (HOLD-999)
**Trigger:** 3 consecutive SABAR warnings or explicit HOLD verdict.
**Action:**
1. Stop all automated agents.
2. Human Architect must review `000_WITNESS/` logs.
3. Manual override via `/gitseal APPROVE "Force unlock override"`.

## 2. Rejection Handling (VOID-999)
**Trigger:** Constitutional floor violation (F1-F9).
**Action:**
1. Check `side_data` in verdict response.
2. Identify violated floor (e.g., "F5 Peace Violation").
3. Refine input and retry with `000_init` reset.

## 3. Data Integrity (Corrupted Seal)
**Trigger:** Signature verification failure in `mcp_889_proof`.
**Action:**
1. Retrieve last valid Merkle root from Ledger.
2. Re-sign using `mcp_889_proof`.
3. If failure persists, seal repository as "VOID/COMPROMISED".
