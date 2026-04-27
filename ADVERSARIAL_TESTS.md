# WEALTH Adversarial Test Matrix
# Phase 2 — Verification-First Capital Governance
# Version: 2026.04.27-KANON
# Run: python3 -m pytest ADVERSARIAL_TESTS.md --md --env arifOS

## Scope
Tests for: `WealthGovernance.evaluate()`, `_arif_judge_deliberate()`, `_arif_vault_seal()`,
`EconomicEnvelope`, `VerdictOutput`, `SealOutput`.

---

## GRADUATED PENALTY ZONE

| ID | svs | delta_m | entropy_band | wealth_score.recommendation | Expected |
|----|-----|---------|--------------|-----------------------------|----------|
| GP-01 | 0.20 | 0.50 | LOW | SEAL_CANDIDATE | HOLD (hard gate) |
| GP-02 | 0.25 | 0.50 | LOW | SEAL_CANDIDATE | HOLD (hard gate) |
| GP-03 | 0.299 | 0.50 | LOW | SEAL_CANDIDATE | HOLD (hard gate) |
| GP-04 | 0.300 | 0.50 | LOW | SEAL_CANDIDATE | OK + penalty=0.0 |
| GP-05 | 0.301 | 0.50 | LOW | SEAL_CANDIDATE | OK + penalty≈0.995 (advisory) |
| GP-06 | 0.350 | 0.50 | LOW | SEAL_CANDIDATE | OK + penalty=0.75 (advisory) |
| GP-07 | 0.400 | 0.50 | LOW | SEAL_CANDIDATE | OK + penalty=0.50 (advisory) |
| GP-08 | 0.450 | 0.50 | LOW | SEAL_CANDIDATE | OK + penalty=0.25 (advisory) |
| GP-09 | 0.500 | 0.50 | LOW | SEAL_CANDIDATE | OK + penalty=0.0 |
| GP-10 | 0.550 | 0.50 | LOW | SEAL_CANDIDATE | OK + penalty=0.0 |

**Gating rule:** `penalty > 0.5` triggers `advisory_governance_flag` in verification_state.
**Gaming rule:** svs=0.301 must NOT hard-block — penalty ≈ 0.995 must be recorded.

---

## MALFORMED INPUT — PARSING ROBUSTNESS

| ID | Input | Parsing Expected | Governance Expected |
|----|-------|-----------------|-------------------|
| M-01 | `svs="0.24"` (string JSON) | normalized to float | HOLD (SVS_BELOW_0.3) |
| M-02 | `entropy_band="extreme"` (lowercase) | normalized to "EXTREME" | HOLD (EXTREME_ENTROPY_BAND) |
| M-03 | `entropy_band="high"` (lowercase) | normalized to "HIGH" | OK (not EXTREME) |
| M-04 | `delta_m=None` (explicit None) | default=0.0 | OK if other fields allow |
| M-05 | `svs=None` (explicit None) | default=1.0 | OK (treated as fully verifiable) |
| M-06 | `{"audit_entropy": {... broken json` | JSONDecodeError | `_parse_failed=True` + `parse_warning` in meta |
| M-07 | Mixed prose + JSON: `"Trade. JSON: {...}"` | JSON fails | `_parse_failed=True` + `parse_warning` in meta |
| M-08 | Uppercase keys: `{"Audit_Entropy": ...}` | NOT extracted (case-sensitive) | audit_entropy=None → permissive OK |

---

## THRESHOLD GAMING

| ID | Scenario | Expected |
|----|----------|----------|
| TG-01 | svs=0.3001 (just above hard line) | OK + penalty≈0.999 |
| TG-02 | svs=0.4999 (just below safe zone) | OK + penalty≈0.001 |
| TG-03 | delta_m=0.7999 (just below hard line) | OK |
| TG-04 | delta_m=0.8001 (just above hard line) | HOLD (DELTA_M_EXCEEDS_0.8) |
| TG-05 | delta_m=0.8000 (exactly at hard line) | OK (no hard block) |

---

## VERDICT ORDERING — NO DE-ESCALATION

| ID | Pre-flight | wealth_score | Kernel Verdict Expected |
|----|-----------|--------------|------------------------|
| VO-01 | HOLD (svs<0.30) | SEAL_CANDIDATE | HOLD |
| VO-02 | HOLD (delta_m>0.80) | SEAL_CANDIDATE | HOLD |
| VO-03 | HOLD (EXTREME band) | SEAL_CANDIDATE | HOLD |
| VO-04 | OK | HOLD_CANDIDATE | HOLD (score can escalate, not de-escalate) |
| VO-05 | OK | VOID_CANDIDATE | VOID |
| VO-06 | VOID (anti_hantu) | (any) | VOID |
| VO-07 | OK | SEAL_CANDIDATE | SEAL |

---

## IDENTITY / LIABILITY SPOOFING — Phase 2.5

| ID | Owner | Expected (Phase 2) | Expected (Phase 2.5) |
|----|-------|-------------------|----------------------|
| LS-01 | `"pm01"` (known) | OK (passes) | OK + registry confirms |
| LS-02 | `"FAKE_INVALID_99999"` | OK (passes — no check) | HOLD + `UNAUTHORIZED_OWNER` |
| LS-03 | `""` (empty) | OK (owner absent) | HOLD + `MISSING_OWNER` |
| LS-04 | `None` | OK (owner absent) | HOLD + `MISSING_OWNER` |

Phase 2.5 requirement: principal registry lookup + domain authorization + loss band mandate validation.

---

## BACKWARD COMPATIBILITY

| ID | Payload | Expected |
|----|---------|----------|
| BC-01 | Old VerdictOutput (status, tool, verdict, candidate, result only) | Validates cleanly |
| BC-02 | Old SealOutput (no verification fields) | Validates cleanly |
| BC-03 | New payload with all optional fields populated | Validates + fields preserved |

---

## JSON ROUND-TRIP — PERSISTENCE

| ID | Field | After Serialize → Deserialize |
|----|-------|-------------------------------|
| RT-01 | `delta_m` | Preserved (float) |
| RT-02 | `svs` | Preserved (float) |
| RT-03 | `entropy_band` | Preserved (string) |
| RT-04 | `bottlenecks` | Preserved (list) |
| RT-05 | `liability_owner` | Preserved (string or None) |
| RT-06 | `wealth_final_score` | Preserved (float) |
| RT-07 | `truth_band` | Preserved (string) |
| RT-08 | `confidence_note` | Preserved (string) |
| RT-09 | `svs_governance_penalty` | Preserved (float) |

---

## TRUTH BAND DISCIPLINE

| ID | Scenario | Expected truth_band | Basis |
|----|----------|--------------------|-------|
| TB-01 | High provenance + low opacity + short latency | CERTAIN or HIGH_CONFIDENCE | Measurable conditions |
| TB-02 | Low svs (< 0.30) + high delta_m | SPECULATIVE or UNKNOWN | Verification constraints limit confidence |
| TB-03 | Mixed conditions | PLAUSIBLE | Partial evidence |
| TB-04 | No verification state provided | PLAUSIBLE (declared as such) | Conservative default |

**Rule:** truth_band must be tied to measurable conditions (provenance_score, verifier_scarcity, ground_truth_latency, liability_clarity). Self-declared bands without basis violate F2.

---

## GOLDEN PATH

| ID | Scenario | Expected |
|----|----------|----------|
| GP-GOLD-01 | High reward + low svs → HOLD | HOLD + SVS_BELOW_0.3 |
| GP-GOLD-02 | Low reward + high svs → SEAL | SEAL |
| GP-GOLD-03 | Extreme entropy band → HOLD | HOLD + EXTREME_ENTROPY_BAND |
| GP-GOLD-04 | anti_hantu_fail → VOID | VOID |
| GP-GOLD-05 | sovereign_veto → VOID | VOID |

---

## Running the Matrix

```bash
# From arifOS root:
python3 -c "
import sys; sys.path.insert(0, '.')
from arifosmcp.core.constitution_kernel import WealthGovernance, ActionContext

# Example: GP-01
ctx = ActionContext(tool_name='test', candidate='test',
    audit_entropy={'delta_m': 0.5, 'svs': 0.20, 'entropy_band': 'LOW'})
wg = WealthGovernance.evaluate(ctx)
assert wg['status'] == 'HOLD', f'GP-01 FAIL: {wg}'
print('GP-01: PASS')
"
```

---

_DITEMPA BUKAN DIBERI — Forged, Not Given_
