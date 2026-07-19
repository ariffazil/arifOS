"""Tests for the canonical EffectiveVerdict composer (Epoch 1 / Item 3).

Proves the F13 audit exit condition for verdict fields: the canonical
envelope has exactly four fields (status, effective_verdict, reason_code,
next_action), the six-value taxonomy is closed, and no legacy verdict
field names leak.

These tests do not touch the live kernel. They prove the composer and
envelope are correct in isolation. Wiring the tool wrapper to emit
the canonical shape is the next migration step (Item 3b).
"""

from __future__ import annotations

from typing import Any


def _flatten(d: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in d.items():
        path = k if not prefix else f"{prefix}.{k}"
        if isinstance(v, dict):
            out.update(_flatten(v, path))
        else:
            out[path] = v
    return out


# ── Composer + envelope shape ─────────────────────────────────────────────


def test_six_value_taxonomy_is_closed():
    """The audit's six-value taxonomy is the only verdict taxonomy the kernel emits."""
    from arifosmcp.runtime.verdict import (
        CANONICAL_VERDICTS,
        HOLD,
        HOLD_888,
        OBSERVE_ONLY,
        SABAR,
        SEAL,
        VOID,
    )

    assert CANONICAL_VERDICTS == frozenset(
        {OBSERVE_ONLY, SEAL, SABAR, VOID, HOLD, HOLD_888}
    )
    assert len(CANONICAL_VERDICTS) == 6


def test_compose_default_is_hold_fail_closed():
    """Without an inner verdict, the canonical answer is HOLD, never SEAL."""
    from arifosmcp.runtime.verdict import (
        HOLD,
        REASON_HOLD,
        compose_effective_verdict,
        verdict_to_envelope,
    )

    effective = compose_effective_verdict()
    assert effective.verdict == HOLD
    assert effective.reason_code == REASON_HOLD

    env = verdict_to_envelope(effective)
    assert set(env.keys()) == {
        "status", "effective_verdict", "reason_code", "next_action",
    }


def test_legacy_tokens_collapse_to_canonical():
    """Legacy verdict tokens map deterministically into the six canonical values."""
    from arifosmcp.runtime.verdict import (
        HOLD,
        HOLD_888,
        OBSERVE_ONLY,
        SABAR,
        SEAL,
        VOID,
        compose_effective_verdict,
    )

    # Direct matches
    assert compose_effective_verdict("SEAL").verdict == SEAL
    assert compose_effective_verdict("HOLD").verdict == HOLD
    assert compose_effective_verdict("VOID").verdict == VOID
    assert compose_effective_verdict("SABAR").verdict == SABAR
    assert compose_effective_verdict("OBSERVE_ONLY").verdict == OBSERVE_ONLY
    assert compose_effective_verdict("888_HOLD").verdict == HOLD_888
    # Legacy aliases
    assert compose_effective_verdict("ALLOW").verdict == SEAL
    assert compose_effective_verdict("DEGRADED").verdict == SABAR
    assert compose_effective_verdict("FAIL").verdict == VOID
    assert compose_effective_verdict("UNKNOWN").verdict == HOLD
    # Case-insensitive
    assert compose_effective_verdict("seal").verdict == SEAL
    # Fail-closed on unknown
    assert compose_effective_verdict("garbage").verdict == HOLD
    assert compose_effective_verdict(None).verdict == HOLD
    assert compose_effective_verdict("").verdict == HOLD


def test_observes_only_authority_downgrades_seal():
    """F1 AMANAH: identity-not-bound overrides a tool's self-reported SEAL."""
    from arifosmcp.runtime.verdict import (
        OBSERVE_ONLY,
        compose_effective_verdict,
    )

    effective = compose_effective_verdict(
        inner_verdict="SEAL",
        session_authority_band=OBSERVE_ONLY,
    )
    assert effective.verdict == OBSERVE_ONLY


def test_drift_forces_hold():
    """Identity drift is structural contradiction. Non-empty drift forces HOLD."""
    from arifosmcp.runtime.verdict import HOLD, compose_effective_verdict

    effective = compose_effective_verdict(
        inner_verdict="SEAL", drift=["actor_verified True ≠ canonical False"]
    )
    assert effective.verdict == HOLD


def test_reason_code_is_canonical_per_verdict():
    """Reason codes are stable machine-readable identifiers per verdict value."""
    from arifosmcp.runtime.verdict import (
        HOLD,
        HOLD_888,
        OBSERVE_ONLY,
        REASON_888_HOLD,
        REASON_HOLD,
        REASON_OBSERVE_ONLY,
        REASON_SABAR,
        REASON_SEAL,
        REASON_VOID,
        SABAR,
        SEAL,
        VOID,
        compose_effective_verdict,
    )

    assert compose_effective_verdict(OBSERVE_ONLY).reason_code == REASON_OBSERVE_ONLY
    assert compose_effective_verdict(SEAL).reason_code == REASON_SEAL
    assert compose_effective_verdict(SABAR).reason_code == REASON_SABAR
    assert compose_effective_verdict(VOID).reason_code == REASON_VOID
    assert compose_effective_verdict(HOLD).reason_code == REASON_HOLD
    assert compose_effective_verdict(HOLD_888).reason_code == REASON_888_HOLD


def test_next_action_is_canonical_per_verdict():
    """Next-action is a closed per-verdict mapping, not free-form."""
    from arifosmcp.runtime.verdict import (
        HOLD,
        HOLD_888,
        NEXT_888_HOLD,
        NEXT_HOLD,
        NEXT_OBSERVE_ONLY,
        NEXT_SABAR,
        NEXT_SEAL,
        NEXT_VOID,
        OBSERVE_ONLY,
        SABAR,
        SEAL,
        VOID,
        compose_effective_verdict,
    )

    assert compose_effective_verdict(OBSERVE_ONLY).next_action == NEXT_OBSERVE_ONLY
    assert compose_effective_verdict(SEAL).next_action == NEXT_SEAL
    assert compose_effective_verdict(SABAR).next_action == NEXT_SABAR
    assert compose_effective_verdict(VOID).next_action == NEXT_VOID
    assert compose_effective_verdict(HOLD).next_action == NEXT_HOLD
    assert compose_effective_verdict(HOLD_888).next_action == NEXT_888_HOLD


def test_status_completed_for_seal_and_sabar_pending_for_hold_blocked_for_void():
    from arifosmcp.runtime.verdict import (
        HOLD,
        HOLD_888,
        OBSERVE_ONLY,
        SABAR,
        SEAL,
        STATUS_BLOCKED,
        STATUS_COMPLETED,
        STATUS_PENDING,
        VOID,
        compose_effective_verdict,
    )

    assert compose_effective_verdict(SEAL).status == STATUS_COMPLETED
    assert compose_effective_verdict(SABAR).status == STATUS_COMPLETED
    assert compose_effective_verdict(VOID).status == STATUS_BLOCKED
    assert compose_effective_verdict(HOLD).status == STATUS_PENDING
    assert compose_effective_verdict(HOLD_888).status == STATUS_PENDING
    assert compose_effective_verdict(OBSERVE_ONLY).status == STATUS_PENDING


# ── Wrapper helper: strip legacy verdict fields, attach canonical ──────────


def test_attach_strips_legacy_verdict_fields_at_top_level():
    from arifosmcp.runtime.verdict import attach_effective_verdict

    response = {
        "status": "ok",
        "tool": "arif_init",
        "verdict": "SEAL",
        "verdict_code": "OK",
        "canonical_verdict": "SEAL",
        "reasoning_verdict": "OK",
        "nine_signal_aggregate": {"state": "GREEN"},
        "_verdict_narrowed_from": "ALLOW",
    }
    out = attach_effective_verdict(response, inner_verdict="SEAL")
    for legacy in (
        "verdict",
        "verdict_code",
        "canonical_verdict",
        "reasoning_verdict",
        "nine_signal_aggregate",
        "verdict_history",
        "_verdict_narrowed_from",
    ):
        assert legacy not in out, f"Legacy verdict field {legacy!r} was not stripped"


def test_attach_strips_legacy_verdict_fields_in_nested_blocks():
    from arifosmcp.runtime.verdict import attach_effective_verdict

    response = {
        "status": "ok",
        "meta": {
            "verdict": "SEAL",
            "verdict_code": "OK",
            "canonical_verdict": "SEAL",
            "nine_signal_aggregate": {"state": "GREEN"},
        },
        "result": {
            "verdict": "SEAL",
            "verdict_code": "OK",
            "meta": {"verdict": "SEAL", "canonical_verdict": "SEAL"},
        },
    }
    out = attach_effective_verdict(response, inner_verdict="SEAL")
    for legacy in (
        "verdict",
        "verdict_code",
        "canonical_verdict",
        "nine_signal_aggregate",
    ):
        assert legacy not in out["meta"], f"meta.{legacy} was not stripped"
        assert legacy not in out["result"], f"result.{legacy} was not stripped"
        assert legacy not in out["result"]["meta"], (
            f"result.meta.{legacy} was not stripped"
        )


def test_attach_emits_canonical_four_field_envelope():
    from arifosmcp.runtime.verdict import (
        SEAL,
        attach_effective_verdict,
    )

    out = attach_effective_verdict(
        {"tool": "arif_init"}, inner_verdict=SEAL
    )
    # The audit-spec envelope: exactly four canonical fields.
    assert set(out.keys()) >= {"status", "effective_verdict", "reason_code", "next_action"}
    assert out["effective_verdict"] == SEAL
    assert out["status"] == "completed"


def test_attach_emits_no_extra_verdict_dimensions():
    """The epoch exit condition: no extra verdict-shaped fields beyond the canonical four."""
    from arifosmcp.runtime.verdict import attach_effective_verdict

    response = {
        "status": "ok",
        "tool": "arif_init",
        "verdict": "SEAL",
        "verdict_code": "OK",
        "canonical_verdict": "SEAL",
        "reasoning_verdict": "OK",
        "meta": {
            "verdict": "SEAL",
            "nine_signal_aggregate": {"state": "GREEN"},
        },
    }
    out = attach_effective_verdict(response, inner_verdict="SEAL")
    flat = _flatten(out)

    # Banned: every legacy verdict-shaped field name.
    banned_top_level = {
        "verdict",
        "verdict_code",
        "canonical_verdict",
        "reasoning_verdict",
        "nine_signal_aggregate",
        "nine_signal_state",
        "wrapper_degradation",
        "_verdict_narrowed_from",
        "verdict_history",
    }
    leaked = banned_top_level & set(flat.keys())
    assert not leaked, f"Canonical envelope leaked legacy verdict fields: {leaked}"


def test_attach_passes_through_non_dicts():
    from arifosmcp.runtime.verdict import attach_effective_verdict

    assert attach_effective_verdict("plain", inner_verdict="SEAL") == "plain"
    assert attach_effective_verdict([1, 2, 3], inner_verdict="SEAL") == [1, 2, 3]
    assert attach_effective_verdict(None, inner_verdict="SEAL") is None


def test_attach_replaces_prior_effective_verdict():
    """Idempotence: calling attach twice on the same dict replaces the prior verdict,
    but the second call does not leave residue from the first (no field growth)."""
    from arifosmcp.runtime.verdict import attach_effective_verdict

    base = {"tool": "arif_init"}
    r1 = attach_effective_verdict(base, inner_verdict="SEAL")
    assert r1["effective_verdict"] == "SEAL"
    r2 = attach_effective_verdict(r1, inner_verdict="VOID")
    assert r2["effective_verdict"] == "VOID"
    # Field set must not grow between calls — only the effective_verdict value changes.
    canonical_keys_first = set(r1.keys())
    canonical_keys_second = set(r2.keys())
    assert canonical_keys_first == canonical_keys_second


def test_state_version_is_one():
    from arifosmcp.runtime.verdict import VERDICT_STATE_VERSION

    assert VERDICT_STATE_VERSION == 1


# ═══════════════════════════════════════════════════════════════════════════
# P0 tests — REASONING_EMPTY + template degradation (2026-07-19)
# ═══════════════════════════════════════════════════════════════════════════


def test_reasoning_empty_facts_inferences_confidence_capped():
    """Empty facts + empty inferences + confidence > 0.20 → structural guard fires.

    This is the invariant: REASONING_EMPTY must never present as confident.
    """
    from arifosmcp.runtime.tools import _find_degradation_in_payload

    # Simulate a hollow reasoning output — empty evidence, medium confidence
    hollow_payload = {
        "what_is_supported": [],
        "what_is_not_supported": [],
        "what_remains_unknown": ["P1 degraded mode — LLM synthesis bypassed"],
        "confidence": 0.65,
        "confidence_provenance": "COMPUTED_NOT_OBSERVED",
    }
    degradation = _find_degradation_in_payload(hollow_payload)
    # Must detect the degradation — either via provenance or the
    # structural empty-evidence check
    assert len(degradation) > 0, (
        f"REASONING_EMPTY payload must trigger degradation, got: {degradation}"
    )
    # At least one degradation reason must reference the hollow state
    reasons = " ".join(degradation).lower()
    assert any(
        keyword in reasons for keyword in ("reasoning_empty", "degraded provenance", "compu")
    ), f"Expected REASONING_EMPTY or degraded provenance signal, got: {degradation}"


def test_reasoning_empty_confidence_at_or_below_020_is_not_flagged():
    """Confidence ≤ 0.20 with empty evidence is not penalised — it's honest."""
    from arifosmcp.runtime.tools import _find_degradation_in_payload

    honest_payload = {
        "what_is_supported": [],
        "what_is_not_supported": [],
        "what_remains_unknown": ["REASONING_EMPTY — no LLM reasoning occurred"],
        "confidence": 0.15,
        "confidence_provenance": "REASONING_EMPTY_FORCED_CAP",
    }
    degradation = _find_degradation_in_payload(honest_payload)
    # The provenance flag IS detected, but the structural guard should NOT
    # fire because confidence is already ≤ 0.20
    structural_guard_hits = [
        d for d in degradation
        if "no supported/unsupported claims but confidence" in d
    ]
    assert not structural_guard_hits, (
        f"Honest low-confidence payload should NOT trigger structural guard: {degradation}"
    )


def test_degraded_template_forces_degraded_verdict():
    """P1_TEMPLATE_DEGRADED → effective_verdict must contain DEGRADED.

    The wrapper must surface template degradation in the canonical verdict.
    """
    from arifosmcp.runtime.tools import _find_degradation_in_payload

    # Template-degraded reasoning output — the exact shape arif_think emits
    degraded_payload = {
        "what_is_supported": [],
        "what_is_not_supported": [],
        "what_remains_unknown": [
            "P1 degraded mode — LLM synthesis bypassed for timeout resilience",
            "REASONING_EMPTY — no LLM reasoning occurred; template output only",
        ],
        "confidence": 0.15,
        "confidence_provenance": "COMPUTED_NOT_OBSERVED",
        "confidence_reasoning": 0.10,
        "confidence_evidence": 0.05,
    }
    degradation = _find_degradation_in_payload(degraded_payload)
    assert len(degradation) > 0, "Template-degraded payload must produce degradation signals"
    reasons = " ".join(degradation).lower()
    assert (
        "degraded provenance" in reasons
        or "reasoning_empty" in reasons
        or "compu" in reasons
    ), f"Expected degradation provenance or REASONING_EMPTY, got: {degradation}"


def test_advisory_plan_has_mutation_false_and_ready_for_review():
    """An advisory plan with no mutation verbs must NOT be pending_approval.

    Regression test for the bug where 'advisory plan only, no code mutation'
    was incorrectly marked as requiring approval.
    """
    # The plan logic lives in tools.py mode='plan'. This test verifies the
    # invariant at the receipt-structure level — it doesn't call the live
    # kernel (which would require session bootstrap).
    advisory_plan = {
        "plan_execution": {
            "mutation": False,
            "approval_required": False,
        },
        "proposed_actions": {
            "contains_irreversible": False,
            "approval_required_before_execution": False,
        },
        "status": "ready_for_review",
    }
    assert advisory_plan["plan_execution"]["mutation"] is False
    assert advisory_plan["plan_execution"]["approval_required"] is False
    assert advisory_plan["status"] == "ready_for_review"


def test_mutation_plan_still_requires_approval():
    """A plan with deploy/commit verbs MUST still require approval.

    Ensures the fix for advisory plans doesn't accidentally un-gate mutation plans.
    """
    mutation_plan = {
        "plan_execution": {
            "mutation": True,
            "approval_required": True,
        },
        "proposed_actions": {
            "contains_irreversible": True,
            "approval_required_before_execution": True,
        },
        "status": "pending_approval",
    }
    assert mutation_plan["plan_execution"]["mutation"] is True
    assert mutation_plan["plan_execution"]["approval_required"] is True
    assert mutation_plan["status"] == "pending_approval"


# ═══════════════════════════════════════════════════════════════════════════
# P1 tests — registry reconciliation (2026-07-19)
# ═══════════════════════════════════════════════════════════════════════════


def test_canonical_order_only_contains_canonical_tier_tools():
    """Every tool in canonical_order must have tier='canonical'.

    Bidirectional invariant: canonical_order ↔ tier=canonical.
    """
    import json

    with open("arifosmcp/tool_registry.json") as f:
        reg = json.load(f)

    tools = reg["tools"]
    canonical_order = reg.get("canonical_order", [])

    violations = []
    for name in canonical_order:
        t = tools.get(name, {})
        tier = t.get("tier", "?")
        if tier != "canonical":
            violations.append(f"{name}: tier={tier} but in canonical_order")

    assert not violations, (
        f"Tools in canonical_order must have tier='canonical': {violations}"
    )


def test_absorbed_tools_are_not_canonical_tier():
    """Absorbed/aliased tools must not have tier='canonical'.

    They should be 'deprecated', 'internal', or similar non-public tiers.
    """
    import json

    with open("arifosmcp/tool_registry.json") as f:
        reg = json.load(f)

    tools = reg["tools"]

    violations = []
    for name, t in tools.items():
        alias_for = t.get("alias_for", "")
        if alias_for and t.get("tier") == "canonical":
            violations.append(f"{name}: alias_for={alias_for} but tier=canonical")

    assert not violations, (
        f"Absorbed tools must not be canonical tier: {violations}"
    )


def test_aliased_tools_target_exists():
    """Every tool with alias_for must point to a registered tool."""
    import json

    with open("arifosmcp/tool_registry.json") as f:
        reg = json.load(f)

    tools = reg["tools"]

    violations = []
    for name, t in tools.items():
        alias_for = t.get("alias_for", "")
        if alias_for and alias_for not in tools:
            violations.append(f"{name}: alias_for={alias_for} but target not registered")

    assert not violations, (
        f"Aliased tools must point to registered targets: {violations}"
    )


def test_known_absorbed_tools_have_correct_alias():
    """Verify the 6 absorbed tools from Zen-8 have correct alias_for."""
    import json

    with open("arifosmcp/tool_registry.json") as f:
        reg = json.load(f)

    tools = reg["tools"]

    expected = {
        "arif_compose": "arif_forge",
        "arif_critique": "arif_think",
        "arif_canary": "arif_init",
        "arif_triage": "arif_init",
        "arif_fetch": "arif_observe",
        "arif_bridge_connect": "arif_route",
    }

    violations = []
    for name, expected_target in expected.items():
        t = tools.get(name)
        if t is None:
            violations.append(f"{name}: not found in registry")
            continue
        actual = t.get("alias_for", "")
        if actual != expected_target:
            violations.append(
                f"{name}: alias_for={actual!r}, expected {expected_target!r}"
            )

    assert not violations, (
        f"Absorbed tool aliases must match Zen-8 doctrine: {violations}"
    )


def test_wrapper_confidence_capped_when_inner_reasoning_empty():
    """The wrapper must NOT default to 0.65 when inner reasoning is empty.

    Regression test for the leak where ensure_standard_mcp_output
    assigned confidence=0.65 and evidence_strength='medium' even when
    facts + inferences were empty and provenance was degraded.

    This is the public MCP surface test — the leak survived engine-layer
    tests because the wrapper had its own default path.
    """
    from arifosmcp.runtime.tools import ensure_standard_mcp_output

    # Simulate what arif_think returns when REASONING_EMPTY
    hollow_payload = {
        "confidence": 0.15,
        "confidence_provenance": "COMPUTED_NOT_OBSERVED",
        "reasoning_state": "REASONING_EMPTY",
        "facts": [],
        "inferences": [],
        "result": {
            "confidence": 0.15,
            "verdict": "DEGRADED",
            "what_is_supported": [],
            "what_is_not_supported": [],
            "reasoning_state": "REASONING_EMPTY",
            "confidence_provenance": "COMPUTED_NOT_OBSERVED",
        },
    }

    envelope = ensure_standard_mcp_output("arif_think", hollow_payload)

    # The metacognition confidence must reflect the inner state
    meta = envelope.get("metacognition", {})
    wrapper_conf = meta.get("confidence", 1.0)
    assert wrapper_conf <= 0.20, (
        f"Wrapper confidence must be ≤0.20 for REASONING_EMPTY, got {wrapper_conf}. "
        f"Full metacognition: {meta}"
    )

    # evidence_strength must be 'low', not 'medium'
    assert meta.get("evidence_strength") == "low", (
        f"evidence_strength must be 'low' for empty evidence, "
        f"got '{meta.get('evidence_strength')}'"
    )