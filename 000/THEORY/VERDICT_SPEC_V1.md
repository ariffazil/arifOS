# ⚖️ MCP Verdict Specification v1.0

**Status:** Canonical Reference
**Domain:** arifOS Meta-Governance
**Axiom:** Standardized grammar prevents intelligence fragmentation.

---

## 1. The Universal Verdict Packet

Every arifOS-compliant MCP tool MUST emit a JSON response matching this schema for all high-consequence reasoning or execution results.

```json
{
  "mcp": "MCP_NAME",
  "task": "task_name",
  "status": "PASS | CAUTION | HOLD | VOID",
  "domain_verdict": "Clear summary of domain-specific outcome",
  "confidence": "HIGH | MEDIUM | LOW",
  "epistemic": {
    "class": "FACT | CLAIM | ESTIMATE | HYPOTHESIS | UNKNOWN",
    "integrity_score": 0.0,
    "uncertainty_band": [0.0, 0.0]
  },
  "authority": {
    "level": "advisory_only | domain_expert | constitutional_binding",
    "boundary": "Description of where authority ends"
  },
  "readiness": {
    "human": "OPTIMAL | FUNCTIONAL | DEGRADED | LOW_CAPACITY",
    "machine": "HEALTHY | FUNCTIONAL | DEGRADED | CRITICAL"
  },
  "risk": {
    "level": "GREEN | AMBER | RED | BLACK",
    "economic": "LOW | MEDIUM | HIGH | CRITICAL",
    "constitutional": "LOW | MEDIUM | HIGH | CRITICAL",
    "coupled": "LOW | MEDIUM | HIGH | CRITICAL"
  },
  "execution": {
    "recommended_mode": "full | structured | draft_only | pause",
    "human_confirmation_required": true,
    "next_safe_action": "Specific instruction for the Operator"
  },
  "assumptions": ["List of core assumptions"],
  "failure_flags": ["List of integrity or floor violations"],
  "reversibility": "REVERSIBLE | IRREVERSIBLE | UNKNOWN",
  "final_authority": "Arif",
  "receipt_hash": "merkle_leaf_hash"
}
```

---

## 2. Invariant Rules

### Rule 1: Conservative Wins
In any arbitration or handoff (e.g., C-WELL vs Forge), the **most conservative mode** MUST prevail.
- `AMBER + RED = RED`
- `full + draft_only = draft_only`

### Rule 2: Epistemic Gravity
No MCP may emit a `status: PASS` if the `epistemic.integrity_score` is < 0.6. Low-integrity data forces `status: CAUTION` or `HOLD`.

### Rule 3: Authority Firewall
Every high-consequence packet MUST declare `final_authority: Arif`. Machine verdicts are recommendations, never sovereign commands.

### Rule 4: Sequential Integrity
Domain kernels (GEOX, WEALTH) MUST consume readiness signals from WELL before emitting an execution recommendation.

---

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**
