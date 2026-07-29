"""
Phase 3 — RASA DERITA mutation gates (cascade + consent).

Machine 888_HOLD when L3+ mutation lacks required envelopes.
Zero new public tools.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from arifosmcp.kernel.rasa_derita_gates import (
    evaluate_from_payload,
    evaluate_mutation_gates,
    schema_load_receipt,
    validate_causal_cascade,
    validate_consent_lease,
)
from arifosmcp.runtime.kernel.judge import judge
from arifosmcp.runtime.kernel.types import (
    EvidenceItem,
    GovernanceScalars,
    GovernanceState,
    RiskProfile,
)


def _valid_cascade() -> dict:
    return {
        "steps": [
            {
                "step": 1,
                "effect": "local file write",
                "affected_party": "operator",
                "severity": "LOW",
                "reversible": True,
            },
            {
                "step": 2,
                "effect": "service reload",
                "affected_party": "service users",
                "severity": "MEDIUM",
                "reversible": True,
            },
            {
                "step": 3,
                "effect": "downstream cache invalidation",
                "affected_party": "federation readers",
                "severity": "LOW",
                "reversible": True,
            },
        ],
        "recovery_path": "git checkout + systemctl restart",
        "reversibility": "PARTIAL",
        "omission_consequence": "drift remains; no harm from waiting",
        "blast_radius": "service",
    }


def _valid_lease(**overrides) -> dict:
    base = {
        "purpose": "deploy patch to arifOS runtime",
        "scope": ["actuate", "store"],
        "expires_at": (datetime.now(UTC) + timedelta(hours=2)).isoformat(),
        "revocable": True,
        "revocation_propagation": "ALL_DERIVED",
        "granted_by": "F13",
    }
    base.update(overrides)
    return base


class TestCausalCascadeGate:
    def test_missing_cascade_holds(self):
        v = validate_causal_cascade(None)
        assert not v.passed
        assert v.code == "888_HOLD"

    def test_two_steps_holds(self):
        v = validate_causal_cascade(
            {
                "steps": [
                    {"effect": "a", "affected_party": "x"},
                    {"effect": "b", "affected_party": "y"},
                ],
                "recovery_path": "rollback",
                "reversibility": "FULL",
                "omission_consequence": "none",
            }
        )
        assert not v.passed

    def test_valid_cascade_passes(self):
        v = validate_causal_cascade(_valid_cascade())
        assert v.passed


class TestConsentLeaseGate:
    def test_missing_lease_holds(self):
        v = validate_consent_lease(None)
        assert not v.passed
        assert v.code == "888_HOLD"

    def test_expired_lease_holds(self):
        v = validate_consent_lease(
            _valid_lease(expires_at=(datetime.now(UTC) - timedelta(hours=1)).isoformat())
        )
        assert not v.passed
        assert any("expired" in r for r in v.reasons)

    def test_revoked_lease_holds(self):
        v = validate_consent_lease(_valid_lease(revoked=True))
        assert not v.passed
        assert any("revok" in r for r in v.reasons)

    def test_valid_lease_passes(self):
        v = validate_consent_lease(_valid_lease())
        assert v.passed


class TestCompositeMutationGates:
    def test_deploy_without_cascade_or_consent_holds(self):
        v = evaluate_mutation_gates(mode="deploy", reversible=False)
        assert not v.passed
        assert v.code == "888_HOLD"

    def test_deploy_with_cascade_and_consent_passes(self):
        v = evaluate_mutation_gates(
            mode="deploy",
            reversible=False,
            causal_cascade=_valid_cascade(),
            consent_lease=_valid_lease(),
        )
        assert v.passed, v.reasons

    def test_observe_without_cascade_passes(self):
        v = evaluate_mutation_gates(mode="observe", reversible=True)
        assert v.passed

    def test_payload_extraction(self):
        payload = {
            "mode": "commit",
            "causal_cascade": _valid_cascade(),
            "consent_lease": _valid_lease(),
        }
        v = evaluate_from_payload(payload, mode="commit", ack_irreversible=True)
        assert v.passed, v.reasons

    def test_payload_missing_holds(self):
        v = evaluate_from_payload({"mode": "deploy"}, mode="deploy", ack_irreversible=True)
        assert not v.passed


class TestKernelJudgeIntegration:
    def test_irreversible_without_cascade_holds(self):
        state = GovernanceState(
            authority_present=True,
            reversible=False,
            action_mode="deploy",
            action_tier="sovereign",
            requires_consent=True,
            scalars=GovernanceScalars(delta=0.1, omega=0.1, psi=0.9),
            evidence=[
                EvidenceItem.create(source="GEOX", payload={"claim": "x"}),
            ],
            risk=RiskProfile(blast_radius="HIGH"),
        )
        out = judge(state)
        assert out.verdict == "HOLD"
        assert out.collapse is not None
        tw_ids = [t.id for t in out.collapse.tripwires]
        assert "RASA_DERITA" in tw_ids

    def test_irreversible_with_gates_can_seal(self):
        state = GovernanceState(
            authority_present=True,
            reversible=False,
            action_mode="deploy",
            action_tier="sovereign",
            requires_consent=True,
            causal_cascade=_valid_cascade(),
            consent_lease=_valid_lease(),
            scalars=GovernanceScalars(delta=0.1, omega=0.1, psi=0.9),
            evidence=[
                EvidenceItem.create(source="GEOX", payload={"claim": "x"}),
            ],
            risk=RiskProfile(blast_radius="HIGH"),
        )
        out = judge(state)
        # May still HOLD on REVERSIBILITY WARN path — irreversible alone is WARN not BLOCK
        # RASA_DERITA should not block
        assert out.collapse is not None
        rd = [t for t in out.collapse.tripwires if t.id == "RASA_DERITA"]
        assert rd and not rd[0].triggered


class TestSchemaLoadReceipt:
    def test_receipt_present(self):
        r = schema_load_receipt()
        assert r["module_id"] == "RASA_DERITA"
        assert r["validation_status"] in ("VALID", "INVALID", "UNAVAILABLE")
        assert "schema_hash" in r or r["validation_status"] == "UNAVAILABLE"
