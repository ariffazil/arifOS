# 🛡️ Failure Doctrine Charter v1.0

**Status:** Canonical Mandate
**Axiom:** Standardized failure grammar prevents system collapse.
**Motto:** *A failure understood is a governed state; a failure ignored is chaos.*

---

## 1. Canonical Failure Classes

Every arifOS MCP MUST classify all errors into one of these six domains.

| Class | Meaning | Impact | Next Safe Action |
| :--- | :--- | :--- | :--- |
| **TOOL_UNAVAILABLE** | Endpoint or service is unreachable. | Functional gap | Use fallback or pause execution. |
| **EPISTEMIC_UNAVAILABLE** | Core knowledge layer (e.g. EVOI) is missing. | Insight gap | Do not make domain claims; advise repair. |
| **SCHEMA_INVALID** | Input/Output shape mismatch. | Logic gap | Halt and repair transformation logic. |
| **DATA_STALE** | Evidence exceeds age threshold. | Trust gap | Fetch fresh data or flag as HYPOTHESIS. |
| **AUTH_MISSING** | Permission or connection missing. | Access gap | Request connection from Operator. |
| **CONFLICTING_VERDICTS** | Subsystems disagree (e.g. WELL vs Forge). | Governance gap | Apply Conservative Wins (most restrictive). |

---

## 2. The Failure Response Packet

When a tool fails, it MUST NOT return a generic error. It MUST return a governed packet matching this schema:

```json
{
  "status": "HOLD | VOID",
  "failure_class": "CLASS_NAME",
  "failure_severity": "LOW | MEDIUM | HIGH | CRITICAL",
  "impact_summary": "What the system cannot do right now.",
  "domain_validity": "What parts of the result are still safe to use.",
  "next_safe_action": "Specific instruction for the Operator.",
  "epistemic_integrity": 0.1,
  "recommended_mode": "pause | draft_only",
  "human_confirmation_required": true,
  "final_authority": "Arif"
}
```

---

## 3. Escalation Rules

### Rule 1: No Silent Failures
Any error in a high-consequence tool MUST trigger an automatic `status: HOLD` and route to `arifOS 888_JUDGE`.

### Rule 2: Partial Validity
If a sub-component fails (e.g., EVOI) but the primary calculation (e.g., NPV) succeeds, the tool MAY return a `PASS` for the primary but MUST include a `CAUTION` and a `failure_class` for the sub-component.

### Rule 3: Conservative Mode Shift
Failure in any component of a `C4/C5` task automatically downgrades the `recommended_mode` to `pause` or `structured_draft`.

---

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**
