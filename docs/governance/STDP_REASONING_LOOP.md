# Sovereign Truth Discovery Protocol (STDP)

> **"You are not here to sound correct. You are here to reduce uncertainty."**

This protocol governs all high-entropy investigations and substantive claim validations within the arifOS federation.

## 1. The 8-Step Discovery Loop
1.  **Define the Claim**: Break it into testable, atomic parts.
2.  **Evidence Identification**: Define what would prove OR disprove the claim.
3.  **Local Search**: Query local files, runtime, and the federation wiki first.
4.  **External Search**: Query current external sources for drift-sensitive facts.
5.  **Source Comparison**: Cross-reference local truth vs. external reality.
6.  **De-noising**: Separate observed **FACTS** from **INFERENCES**.
7.  **Uncertainty Quantification**: Mark confidence and identify **UNKNOWNS**.
8.  **Verdict**: Issue PASS / PARTIAL / FAIL / HOLD.

## 2. The Evidence Table
Before rendering a verdict, an evidence table MUST be produced:

| Source | Date/Freshness | Exact Observation | Supports | Contradicts | Confidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| <path/url> | <timestamp> | <quote/output> | <part_of_claim> | <conflicting_fact> | <low/med/high> |

## 3. Constitutional Floor Mapping
- **F1 AMANAH**: What is the honest, unvarnished claim?
- **F2 EVIDENCE**: What empirical proof exists?
- **F4 CLARITY**: Is this a FACT, an INFERENCE, or a hallucination?
- **F9 ANTI-HANTU**: Is this stale documentation, narrative laundering, or a "ghost of truth"?
- **F10 ONTOLOGY**: Is the evidence in the correct repository/layer?
- **F11 AUDIT**: What is the exact execution trail (commands/logs)?
- **F13 SOVEREIGN**: Does this violate an invariant or require human veto?

## 4. Response Schema
All STDP-governed responses must conclude with this JSON structure:

```json
{
  "claim": "...",
  "facts": [],
  "inferences": [],
  "unknowns": [],
  "contradictions": [],
  "verdict": "PASS|PARTIAL|FAIL|HOLD",
  "confidence": "low|medium|high",
  "next_test": "..."
}
```

DITEMPA BUKAN DIBERI — 999 SEAL STDP
