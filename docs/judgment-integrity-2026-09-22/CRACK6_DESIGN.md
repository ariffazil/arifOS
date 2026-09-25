# Crack #6 + #2 — FINAL Design v4
## 2026-09-22 — after Claude + external Copilot review (paste 9 + paste 13)

artifact_status: PROPOSAL
seal_status: UNSEALED
authority: F13_REQUIRED
execution_authority: NONE

> Status: PROPOSAL. This document defines a candidate design and does not
> constitute an arifOS verdict, authorization, or F13 SEAL. Implementation
> and merge do not confer execution authority.

---

## What This PR Ships

Judgment-integrity only. Four components:

1. **Recursive decision-field discovery** — walk every mapping + sequence node
2. **Closed vocabulary + canonical mapping** — `KernelDecision` × `ConstitutionalVerdict`
3. **Derived `next_safe_action`** — never accepted from input payload as authority
4. **Regression fixtures** — today's actual payload (immutable) + synthetic contradictory payload

**NOT in this PR**: authority service, Ed25519 binding, write-ahead receipts, GUI. All deferred to dependent PRs.

---

## Closed Vocabulary (Two-Layer, Not One)

```python
class KernelDecision(str, Enum):
    ALLOW = "ALLOW"           # kernel-intercept decision
    HOLD = "HOLD"             # kernel held for review

class ConstitutionalVerdict(str, Enum):
    SEAL = "SEAL"             # constitutional verdict (highest)
    HOLD = "HOLD"             # constitutional hold
    SABAR = "SABAR"           # wait for evidence
    VOID = "VOID"             # constitutional rejection
    OBSERVE_ONLY = "OBSERVE_ONLY"

# Foreign tokens mapped EXPLICITLY. Missing mapping = HOLD.
# This table is a SPEC proposal. Constitutional ownership must approve.
RAW_TO_KERNEL: dict[str, KernelDecision] = {
    "ALLOW": KernelDecision.ALLOW,
    "HOLD": KernelDecision.HOLD,
}
RAW_TO_CONSTITUTIONAL: dict[str, ConstitutionalVerdict] = {
    "SEAL": ConstitutionalVerdict.SEAL,
    "HOLD": ConstitutionalVerdict.HOLD,
    "SABAR": ConstitutionalVerdict.SABAR,
    "VOID": ConstitutionalVerdict.VOID,
    "OBSERVE_ONLY": ConstitutionalVerdict.OBSERVE_ONLY,
    # QUALIFY, RETAK, SYUBHAH are layer-specific; map only when owner declares them equivalent.
    # Default policy: unknown → HOLD/UNKNOWN_DECISION_VALUE.
}
```

---

## Verdict-Bearing Keys (closed set, NOT a path list)

```python
VERDICT_BEARING_KEYS = frozenset({
    "verdict",
    "effective_verdict",
    "decision",
    "disposition",
    "outcome",
})

NON_VERDICT_KEYS = frozenset({
    "floor_passed",        # epistemic assertion, not verdict
    "substrate_state",     # substrate status
    "session_state",       # session status
})
```

Any key outside this set is **not** treated as a verdict, even if its value looks like one. Free-text fields (`observed_reality`, `summary`, etc.) → `UNSTRUCTURED_DECISION_SIGNAL` (hint only).

---

## Recursive Walker (schema-recognized verdict-bearing keys)

Discovers verdict-bearing fields at arbitrary depth using schema-recognized verdict-bearing keys. **NOT** "any string containing SEAL anywhere." The walker only inspects keys in `VERDICT_BEARING_KEYS`; free-text fields are explicitly excluded from authoritative verdict discovery and only appear as `UNSTRUCTURED_DECISION_SIGNAL` hints.

```python
from typing import Any, Mapping, Sequence, Iterator

def _walk(payload: Any, path: tuple = ()) -> Iterator[tuple[tuple, str, Any]]:
    if isinstance(payload, Mapping):
        for k, v in payload.items():
            yield from _walk(v, (*path, str(k)))
            yield (*path, str(k)), str(k), v
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        for i, v in enumerate(payload):
            yield from _walk(v, (*path, f"[{i}]"))
```

---

## Reconciler (accumulate all violations, do not early-return)

```python
@dataclass(frozen=True)
class ReconciliationResult:
    status: ConstitutionalVerdict
    consistency: str                          # "CONSISTENT" | "INCONSISTENT"
    issues: tuple[dict, ...]                  # each issue carries path + observed + reason_code
    observations: tuple[dict, ...]            # every verdict-bearing observation made
    seal_eligible: bool                       # verdict == SEAL, nothing else
    authority_enabled: bool                    # ALWAYS False in this PR
    execution_enabled: bool                   # ALWAYS False in this PR
    next_safe_action: str                      # derived, never input-derived

def reconcile_payload(payload: Mapping[str, Any]) -> ReconciliationResult:
    observations: list[dict] = []
    issues: list[dict] = []
    kernel_decisions: set[KernelDecision] = set()
    const_verdicts: set[ConstitutionalVerdict] = set()
    unclassified_tokens: list[dict] = []

    # ── Pass 1: verdict discovery ──
    for path_tuple, key, raw in _walk(payload):
        k = key.strip().lower()
        if k in NON_VERDICT_KEYS:
            continue
        if k not in VERDICT_BEARING_KEYS:
            continue
        if not isinstance(raw, str):
            issues.append({
                "code": "NON_STRING_DECISION_VALUE",
                "path": ".".join(path_tuple),
                "observed": repr(raw),
            })
            continue
        token = raw.strip().upper()
        if token in RAW_TO_KERNEL:
            d = RAW_TO_KERNEL[token]
            kernel_decisions.add(d)
            observations.append({"path": ".".join(path_tuple), "key": k, "layer": "kernel", "raw": token, "canonical": d.value})
        elif token in RAW_TO_CONSTITUTIONAL:
            v = RAW_TO_CONSTITUTIONAL[token]
            const_verdicts.add(v)
            observations.append({"path": ".".join(path_tuple), "key": k, "layer": "constitutional", "raw": token, "canonical": v.value})
        else:
            unclassified_tokens.append({"path": ".".join(path_tuple), "key": k, "raw": token})

    # ── Pass 2: epistemic validation (separate from verdict collection) ──
    for issue in _validate_measurement_integrity(payload):
        issues.append(issue)
    for issue in _validate_claim_provenance(payload):
        issues.append(issue)
    # Free-text signals: treat as hint, not authority
    for hint in _detect_unstructured_decision_signals(payload):
        issues.append({**hint, "weight": "HINT_ONLY"})  # hint weight never overrides structure

    # ── Pass 3: derive verdict ──
    if unclassified_tokens:
        issues.append({
            "code": "UNKNOWN_DECISION_VALUE",
            "tokens": unclassified_tokens,
        })

    if not observations:
        issues.append({"code": "NO_DECISION_OBSERVED"})

    if len(kernel_decisions) > 1:
        issues.append({"code": "INCONSISTENT_KERNEL_DECISIONS", "values": [d.value for d in kernel_decisions]})
    if len(const_verdicts) > 1:
        issues.append({"code": "INCONSISTENT_CONSTITUTIONAL_VERDICTS", "values": [v.value for v in const_verdicts]})
    # Cross-layer conflict: if both layers have observations and they disagree,
    # surface as INCONSISTENT_DECISION_STATE regardless of layer type.
    if kernel_decisions and const_verdicts:
        # Cross-layer consistency requires explicit semantic matrix.
        # Until that matrix exists, any non-empty cross-layer disagreement is fail-closed.
        # (Conservative: HOLD when both layers exist.)
        issues.append({
            "code": "CROSS_LAYER_DECISION_PRESENT",
            "kernel": [d.value for d in kernel_decisions],
            "constitutional": [v.value for v in const_verdicts],
        })

    consistent = not issues
    final_verdict = (
        next(iter(const_verdicts)) if (
            not issues and len(const_verdicts) == 1
        ) else ConstitutionalVerdict.HOLD
    )
    seal_eligible = (
        consistent and final_verdict == ConstitutionalVerdict.SEAL
    )

    next_action = _derive_next_safe_action(
        verdict=final_verdict,
        seal_eligible=seal_eligible,
    )

    return ReconciliationResult(
        status=final_verdict,
        consistency="CONSISTENT" if consistent else "INCONSISTENT",
        issues=tuple(issues),
        observations=tuple(observations),
        seal_eligible=seal_eligible,
        authority_enabled=False,    # always False in this PR
        execution_enabled=False,   # always False in this PR
        next_safe_action=next_action,
    )

def _validate_measurement_integrity(payload: Mapping[str, Any]) -> list[dict]:
    """No measurement is not success."""
    issues: list[dict] = []
    cc = payload.get("constitutional_check")
    if not isinstance(cc, Mapping):
        return issues
    floors_invoked = cc.get("floors_invoked")
    floor_passed = cc.get("floor_passed")
    if floor_passed is True and (
        not isinstance(floors_invoked, Sequence)
        or isinstance(floors_invoked, (str, bytes, bytearray))
        or len(floors_invoked) == 0
    ):
        issues.append({
            "code": "UNMEASURED_PRESENTED_AS_PASSED",
            "path": "constitutional_check.floor_passed",
            "observed": True,
            "related_path": "constitutional_check.floors_invoked",
            "related_observed": list(floors_invoked) if floors_invoked else [],
        })
    return issues

def _validate_claim_provenance(payload: Mapping[str, Any]) -> list[dict]:
    """Label must match provenance."""
    issues: list[dict] = []
    claim_class = str(payload.get("claim_class", "")).strip().upper()
    data_mode = str(payload.get("data_mode", "")).strip().lower()
    # Conservative rule. Replace with explicit compatibility matrix in next contract version.
    if claim_class == "MEASURED" and data_mode in {"derived", "synthetic", "simulated", "inferred"}:
        issues.append({
            "code": "CLAIM_PROVENANCE_MISMATCH",
            "claim_class": claim_class,
            "data_mode": data_mode,
        })
    return issues

def _detect_unstructured_decision_signals(payload: Mapping[str, Any]) -> list[dict]:
    """Free-text fields are HINTS, not verdicts. They never establish SEAL."""
    hints: list[dict] = []
    for path_tuple, key, raw in _walk(payload):
        if key.strip().lower() in VERDICT_BEARING_KEYS or key.strip().lower() in NON_VERDICT_KEYS:
            continue
        if isinstance(raw, str):
            upper = raw.upper()
            for tok in {"SEAL", "HOLD", "SABAR", "VOID", "OBSERVE_ONLY", "ALLOW", "PROCEED", "REJECT"}:
                if tok in upper:
                    hints.append({
                        "code": "UNSTRUCTURED_DECISION_SIGNAL",
                        "path": ".".join(path_tuple),
                        "key": key,
                        "token_seen": tok,
                    })
    return hints

def _derive_next_safe_action(*, verdict: ConstitutionalVerdict, seal_eligible: bool) -> str:
    """Derived ONLY. Never read input next_safe_action as authoritative."""
    if verdict == ConstitutionalVerdict.VOID:
        return "Stop processing this proposal and record the void outcome."
    if verdict == ConstitutionalVerdict.OBSERVE_ONLY:
        return "Observe and record evidence without changing state."
    if verdict == ConstitutionalVerdict.SABAR:
        return "Wait for the required evidence or authority, then reassess."
    if verdict == ConstitutionalVerdict.HOLD:
        return "Resolve the reported inconsistencies and run judgment again."
    # SEAL — even when seal_eligible, never authorize execution in this PR
    if verdict == ConstitutionalVerdict.SEAL and seal_eligible:
        return "Request an external authority grant for the reconciled transaction. (Authority service is not yet implemented.)"
    return "Hold the proposal and investigate the unresolved state."

FORBIDDEN_WHEN_NOT_SEAL_ELIGIBLE = frozenset({
    "seal", "forge", "commit", "execute", "deploy", "send", "transfer",
})

def _assert_safe_action(action: str, seal_eligible: bool) -> None:
    if seal_eligible:
        return
    lowered = action.casefold()
    forbidden = sorted(t for t in FORBIDDEN_WHEN_NOT_SEAL_ELIGIBLE if t in lowered)
    if forbidden:
        raise ValueError(
            f"Derived next_safe_action contains forbidden transition terms "
            f"while seal_eligible is false: {forbidden}"
        )
```

---

## Regression Fixtures

### Fixture 1: Today's actual probe payload (immutable)

`tests/fixtures/arif_judge_2026-09-22.json` — hash-pinned file. NEVER EDIT. Includes the full raw response captured from `https://arifos.arif-fazil.com/mcp` on 2026-09-22.

Two tests on this fixture:

- `test_actual_payload_reconciles_judgment` — verifies the judgment reconciliation result matches expected `EXPECTED_RECONCILED_STATUS` (set on first run; locked thereafter).
- `test_anonymous_actor_cannot_obtain_authority` — passes the reconciled judgment + a None signature to the authority evaluator (separate function, separate test). Asserts `authority_enabled=False`, reason=`UNVERIFIED_ACTOR`.

### Fixture 2: Synthetic contradictory payload

```python
SYNTHETIC_CONTRADICTION = {
    "verdict": "HOLD",
    "effective_verdict": "HOLD",
    "kernel_intercept": {"decision": "ALLOW"},
    "judge_postcondition": {"verdict": "SEAL"},
    "constitutional_check": {
        "floors_invoked": [],
        "floor_passed": True,
    },
    "claim_class": "MEASURED",
    "data_mode": "derived",
    "seal_allowed": False,
    "next_safe_action": "seal the result",  # input, will be ignored
}

def test_synthetic_payload_returns_hold_with_all_issues():
    result = reconcile_payload(SYNTHETIC_CONTRADICTION)
    assert result.status == ConstitutionalVerdict.HOLD
    assert result.consistency == "INCONSISTENT"
    # All violations must surface — no early return
    codes = {i["code"] for i in result.issues}
    assert "INCONSISTENT_CONSTITUTIONAL_VERDICTS" in codes
    assert "CROSS_LAYER_DECISION_PRESENT" in codes
    assert "UNMEASURED_PRESENTED_AS_PASSED" in codes
    assert "CLAIM_PROVENANCE_MISMATCH" in codes
    assert result.seal_eligible is False
    assert result.authority_enabled is False
    assert result.execution_enabled is False
    # Input next_safe_action is ignored, derived output is used
    assert result.next_safe_action != "seal the result"
    # Forbidden transition terms absent
    lowered = result.next_safe_action.casefold()
    for term in FORBIDDEN_WHEN_NOT_SEAL_ELIGIBLE:
        assert term not in lowered
```

### Closed-enum + structural tests

```python
def test_unknown_decision_value_fails_closed():
    r = reconcile_payload({"verdict": "NEW_MAGIC_VERDICT"})
    assert r.status == ConstitutionalVerdict.HOLD
    codes = {i["code"] for i in r.issues}
    assert "UNKNOWN_DECISION_VALUE" in codes
    assert r.authority_enabled is False

def test_no_decision_observed_fails_closed():
    r = reconcile_payload({"constitutional_check": {"floors_invoked": [], "floor_passed": False}})
    assert r.status == ConstitutionalVerdict.HOLD
    codes = {i["code"] for i in r.issues}
    assert "NO_DECISION_OBSERVED" in codes

def test_nested_verdict_discovered_without_path_list():
    """Recursion works — fixed paths don't."""
    r = reconcile_payload({
        "verdict": "HOLD",
        "arbitrarily_nested": {"another_layer": {"decision": "SEAL"}},
    })
    assert r.status == ConstitutionalVerdict.HOLD
    codes = {i["code"] for i in r.issues}
    assert "CROSS_LAYER_DECISION_PRESENT" in codes
```

---

## Do-Not-Merge Guardrails

Reject the PR if any of these are true at CI time:

- unknown decision token passes (i.e., ends in status != HOLD)
- contradictory decision signal produces non-HOLD
- `floor_passed=True` with empty `floors_invoked` does not produce `UNMEASURED_PRESENTED_AS_PASSED`
- `claim_class=MEASURED` + `data_mode=derived/synthetic/simulated/inferred` does not produce `CLAIM_PROVENANCE_MISMATCH`
- input `next_safe_action` survives reconciliation as `result.next_safe_action`
- `result.authority_enabled` is ever True in this PR
- `result.execution_enabled` is ever True in this PR

## Three-Plane Separation (per paste 13)

A reconciled verdict has three independent dimensions. **PR-1 only touches the first**:

| Plane | Meaning | Set by | In PR-1 |
|---|---|---|---|
| `seal_eligible` | Judgment reconciles to SEAL (consistent, no epistemic violations) | PR-1 reconciler | true/false based on payload |
| `authority_enabled` | Human authority verified (Ed25519 signature on single-use grant) | PR-2 authority service | **ALWAYS False** |
| `execution_enabled` | Grant + state recheck passed at execution time | PR-3 executor | **ALWAYS False** |

**A perfectly consistent SEAL returns:**
```json
{
  "verdict": "SEAL",
  "seal_eligible": true,
  "authority_enabled": false,
  "execution_enabled": false
}
```

These three are separate planes. The reconciler may say "judgment is sound" but only the authority service can say "human said yes" and only the executor can say "grant consumed, mutation persisted".

---

## Status Block (machine-readable metadata)

```yaml
artifact_status: PROPOSAL
seal_status: UNSEALED
authority: F13_REQUIRED
execution_authority: NONE
scope: arif_judge payload reconciliation only
dependencies: NONE (independent of authority service, GUI, or Ed25519 lane)
replaces: nothing; additive
reversible: yes (revert commit restores prior behavior)
```
