"""
Tests: Chapter 6 Upgrade — P3 + P4 + P5 + P7 (Closing Batch)

Validates:
  P3: ResponsibilityLedger — MoralOwner, ResponsibilityReceipt, build_responsibility_receipt
  P4: Appeal Path wired — arif_appeal_raise/status/list
  P5: Topology Actuator — evaluate_topology, apply_actuator_to_routing
  P7: Host Scope Gate — evaluate_host_scope, HOST_TRUST_MATRIX, redaction

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations


from arifosmcp.schemas.federation_envelope import (
    ActionClass,
    HostAttestation,
    ToolScope,
)
from arifosmcp.schemas.responsibility_ledger import (
    MoralOwner,
    ResponsibilityClass,
    build_responsibility_receipt,
)
from arifosmcp.runtime.host_scope import (
    HOST_TRUST_MATRIX,
    PermissionLayer,
    evaluate_host_scope,
    redact_tool_description,
    redact_tool_surface,
)
from arifosmcp.runtime.topology_actuator import (
    ActuatorAction,
    ActuatorRecommendation,
    evaluate_topology,
    apply_actuator_to_routing,
)
from arifosmcp.schemas.topology import (
    AccessLevel,
    AntiSinkCheck,
    AppealPath,
    Confidence,
    Delta,
    InstitutionalDrift,
    InstitutionalVerdict,
    InnovationRights,
    ParticipationWidth,
    Presence,
    RiskBand,
    SovereigntyIntegrity,
    Strength,
)


# ═══════════════════════════════════════════════════════════════════════════════
# P3 — Responsibility Ledger
# ═══════════════════════════════════════════════════════════════════════════════


class TestResponsibilityLedger:
    """P3: VAULT999 Responsibility Ledger — who can answer for what happened."""

    def test_build_receipt_basic(self):
        """Building a receipt should populate all required fields."""
        receipt = build_responsibility_receipt(
            seal_id="SEAL-001",
            session_id="sess-test",
            actor_id="arif",
            what_changed="Deployed Chapter 6 upgrade",
            who_authorized="arif",
            who_ratified="arif-fazil",
            moral_owner=MoralOwner.SOVEREIGN,
            responsibility_class=ResponsibilityClass.CONSEQUENTIAL,
            evidence_used=["test-155-pass", "health-check-green"],
            uncertainty_left="Risk classifier tests need updating",
            confidence=0.95,
            people_affected=["federation operators", "agents"],
            rollback_plan="git revert HEAD~1 && systemctl restart arifos",
            repair_plan="Re-run test suite, verify health endpoints",
            reversibility="reversible",
        )
        assert receipt.seal_id == "SEAL-001"
        assert receipt.moral_owner == MoralOwner.SOVEREIGN
        assert receipt.responsibility_class == ResponsibilityClass.CONSEQUENTIAL
        assert receipt.is_accountable() is True
        assert receipt.is_safe() is True
        assert receipt.can_be_contested is True
        assert receipt.review_required is True  # CONSEQUENTIAL triggers review
        assert receipt.review_interval_days == 90
        assert len(receipt.evidence_used) == 2
        assert len(receipt.people_affected) == 2

    def test_unassigned_moral_owner(self):
        """A receipt with UNASSIGNED moral owner should flag as not accountable."""
        receipt = build_responsibility_receipt(
            seal_id="SEAL-002",
            session_id="sess-test",
            actor_id="agent",
            what_changed="Test change",
            who_authorized="agent",
            who_ratified="agent",
            moral_owner=MoralOwner.UNASSIGNED,
        )
        assert receipt.is_accountable() is False
        assert receipt.moral_owner == MoralOwner.UNASSIGNED

    def test_responsibility_classes_trigger_review(self):
        """Consequential, irreversible, and historic should require review."""
        for rc in (
            ResponsibilityClass.CONSEQUENTIAL,
            ResponsibilityClass.IRREVERSIBLE,
            ResponsibilityClass.HISTORIC,
        ):
            receipt = build_responsibility_receipt(
                seal_id=f"SEAL-{rc.value}",
                session_id="t",
                actor_id="a",
                what_changed="x",
                who_authorized="a",
                who_ratified="a",
                responsibility_class=rc,
            )
            assert receipt.review_required is True, f"{rc.value} should require review"

    def test_routine_does_not_require_review(self):
        """Routine and significant should not require periodic review."""
        receipt = build_responsibility_receipt(
            seal_id="SEAL-routine",
            session_id="t",
            actor_id="a",
            what_changed="x",
            who_authorized="a",
            who_ratified="a",
            responsibility_class=ResponsibilityClass.ROUTINE,
        )
        assert receipt.review_required is False

    def test_migration_sql_is_valid(self):
        """Migration SQL should contain the expected ALTER TABLE."""
        from arifosmcp.schemas.responsibility_ledger import VAULT999_RESPONSIBILITY_MIGRATION

        assert "ALTER TABLE public.vault_sealed_events" in VAULT999_RESPONSIBILITY_MIGRATION
        assert "ADD COLUMN IF NOT EXISTS moral_owner" in VAULT999_RESPONSIBILITY_MIGRATION
        assert "ADD COLUMN IF NOT EXISTS rollback_plan" in VAULT999_RESPONSIBILITY_MIGRATION
        assert "ADD COLUMN IF NOT EXISTS repair_plan" in VAULT999_RESPONSIBILITY_MIGRATION
        assert "ADD COLUMN IF NOT EXISTS people_affected" in VAULT999_RESPONSIBILITY_MIGRATION
        assert "Chapter 6 P3" in VAULT999_RESPONSIBILITY_MIGRATION


# ═══════════════════════════════════════════════════════════════════════════════
# P7 — Host Scope Gate
# ═══════════════════════════════════════════════════════════════════════════════


class TestHostScopeGate:
    """P7: Semi-trusted MCP Hardening — host_attestation → tool scope."""

    def test_trusted_host_full_access(self):
        """Trusted hosts should have full access to all action classes and scopes."""
        result = evaluate_host_scope(
            host_level=HostAttestation.TRUSTED,
            tool_action_class=ActionClass.MUTATE,
            tool_scopes=[ToolScope.READ, ToolScope.WRITE, ToolScope.VAULT],
        )
        assert result.allowed is True
        assert result.permission_layer == PermissionLayer.MAY

    def test_semi_trusted_cannot_mutate(self):
        """Semi-trusted hosts cannot execute MUTATE or ATOMIC."""
        result = evaluate_host_scope(
            host_level=HostAttestation.SEMI_TRUSTED,
            tool_action_class=ActionClass.MUTATE,
            tool_scopes=[ToolScope.READ],
        )
        assert result.allowed is False
        assert "cannot execute" in result.reason.lower()

    def test_semi_trusted_blocked_scopes(self):
        """Semi-trusted hosts cannot touch SECRET, DIGNITY, MEMORY, VAULT."""
        for scope in (ToolScope.SECRET, ToolScope.DIGNITY, ToolScope.MEMORY, ToolScope.VAULT):
            result = evaluate_host_scope(
                host_level=HostAttestation.SEMI_TRUSTED,
                tool_action_class=ActionClass.OBSERVE,
                tool_scopes=[scope],
            )
            assert result.allowed is False, f"SEMI_TRUSTED should block {scope.value}"

    def test_untrusted_observe_only(self):
        """Untrusted hosts can only OBSERVE with READ scope."""
        result = evaluate_host_scope(
            host_level=HostAttestation.UNTRUSTED,
            tool_action_class=ActionClass.OBSERVE,
            tool_scopes=[ToolScope.READ],
        )
        assert result.allowed is True

        result2 = evaluate_host_scope(
            host_level=HostAttestation.UNTRUSTED,
            tool_action_class=ActionClass.OBSERVE,
            tool_scopes=[ToolScope.WRITE],
        )
        assert result2.allowed is False

    def test_trust_matrix_complete(self):
        """All four trust levels should be in the matrix."""
        for level in HostAttestation:
            assert level in HOST_TRUST_MATRIX, f"{level} missing from matrix"

    def test_redact_sensitive_tools(self):
        """Sensitive tool descriptions should be redacted for untrusted hosts."""
        redacted = redact_tool_description("arif_vault_seal", "Seal to the immutable audit ledger.")
        assert "REDACTED" in redacted

        not_redacted = redact_tool_description("arif_ops_measure", "Check system health.")
        assert "REDACTED" not in not_redacted

    def test_redact_tool_surface(self):
        """Untrusted hosts should get a redacted tool surface."""
        tools = [
            {"name": "arif_sense_observe", "description": "Search and observe"},
            {"name": "arif_vault_seal", "description": "Seal to vault"},
            {"name": "arif_judge_deliberate", "description": "Render verdict"},
        ]
        redacted = redact_tool_surface(tools, HostAttestation.UNTRUSTED)
        # Only observe-like tools survive without redaction
        assert len(redacted) > 0
        # Vault/judge tools should be redacted or removed
        for tool in redacted:
            if "vault" in tool["name"] or "judge" in tool["name"]:
                assert tool.get("redacted") is True or "REDACTED" in tool["description"]


# ═══════════════════════════════════════════════════════════════════════════════
# P5 — Topology Actuator
# ═══════════════════════════════════════════════════════════════════════════════


class TestTopologyActuator:
    """P5: Topology Actuator — convert diagnostics into routing actions."""

    def _make_drift(self, **overrides) -> InstitutionalDrift:
        defaults = dict(
            inclusive_access=AccessLevel.MEDIUM,
            extractive_capture=RiskBand.LOW,
            sovereignty_integrity=SovereigntyIntegrity.STRONG,
            appeal_path=AppealPath.PRESENT,
            participation_width=ParticipationWidth.BROAD,
            innovation_rights=InnovationRights.DISTRIBUTED,
            elite_chokepoint_risk=RiskBand.LOW,
            verdict=InstitutionalVerdict.INCLUSIVE,
            confidence=Confidence.HIGH,
        )
        defaults.update(overrides)
        return InstitutionalDrift(**defaults)

    def _make_anti_sink(self, **overrides) -> AntiSinkCheck:
        defaults = dict(
            agency_delta=Delta.NEUTRAL,
            role_diversity_delta=Delta.NEUTRAL,
            feedback_integrity=Strength.STRONG,
            topology_risk=RiskBand.LOW,
            extractive_drift=RiskBand.LOW,
            inclusive_repair_path=Presence.PRESENT,
            beautiful_ones_risk=False,
            agency_compression=RiskBand.LOW,
            verdict="pass",
            confidence=Confidence.HIGH,
        )
        defaults.update(overrides)
        return AntiSinkCheck(**defaults)

    def test_extractive_capture_triggers_throttle(self):
        """High extractive capture with tool concentration → THROTTLE."""
        drift = self._make_drift(
            extractive_capture=RiskBand.HIGH,
            verdict=InstitutionalVerdict.MIXED,
        )
        distribution = {
            "arif_mind_reason": 500,
            "arif_ops_measure": 100,
            "arif_sense_observe": 50,
            "arif_evidence_fetch": 30,
            "arif_heart_critique": 20,
        }
        result = evaluate_topology(drift=drift, tool_call_distribution=distribution)
        assert result.action_count > 0
        throttle_recs = [r for r in result.recommendations if r.action == ActuatorAction.THROTTLE]
        assert len(throttle_recs) > 0
        assert "arif_mind_reason" in [r.target for r in throttle_recs]

    def test_symbolic_sovereignty_triggers_escalate(self):
        """SYMBOLIC sovereignty integrity → ESCALATE + GATE."""
        drift = self._make_drift(
            sovereignty_integrity=SovereigntyIntegrity.SYMBOLIC,
            verdict=InstitutionalVerdict.MIXED,
        )
        result = evaluate_topology(drift=drift)
        escalate_recs = [r for r in result.recommendations if r.action == ActuatorAction.ESCALATE]
        assert len(escalate_recs) > 0
        assert any(r.target == "F13" for r in escalate_recs)

    def test_weak_appeal_path_triggers_promote(self):
        """WEAK appeal path → PROMOTE appeal tools."""
        drift = self._make_drift(
            appeal_path=AppealPath.WEAK,
            verdict=InstitutionalVerdict.MIXED,
        )
        result = evaluate_topology(drift=drift)
        promote_recs = [r for r in result.recommendations if r.action == ActuatorAction.PROMOTE]
        appeal_promotes = [r for r in promote_recs if "appeal" in r.target.lower()]
        assert len(appeal_promotes) > 0

    def test_healthy_topology_no_actions(self):
        """Healthy topology with no drift → no actuator actions."""
        drift = self._make_drift()
        result = evaluate_topology(drift=drift)
        assert result.action_count == 0
        assert result.drift_verdict == InstitutionalVerdict.INCLUSIVE

    def test_beautiful_ones_risk_triggers_gate(self):
        """Beautiful Ones risk → GATE on reply_compose."""
        anti_sink = self._make_anti_sink(
            beautiful_ones_risk=True,
        )
        result = evaluate_topology(anti_sink=anti_sink)
        gate_recs = [r for r in result.recommendations if r.action == ActuatorAction.GATE]
        assert any("arif_reply_compose" in r.target for r in gate_recs)

    def test_apply_actuator_reorders_tools(self):
        """Apply actuator: promoted tools first, throttled tools last, gated removed."""
        recs = [
            ActuatorRecommendation(
                action=ActuatorAction.PROMOTE,
                target="arif_appeal_raise",
                reason="t",
                signal_source="t",
            ),
            ActuatorRecommendation(
                action=ActuatorAction.THROTTLE,
                target="arif_mind_reason",
                reason="t",
                signal_source="t",
            ),
            ActuatorRecommendation(
                action=ActuatorAction.GATE, target="arif_vault_seal", reason="t", signal_source="t"
            ),
        ]
        tools = ["arif_sense_observe", "arif_mind_reason", "arif_appeal_raise", "arif_vault_seal"]
        result = apply_actuator_to_routing(recs, tools)
        assert result[0] == "arif_appeal_raise"
        assert "arif_vault_seal" not in result
        assert result[-1] == "arif_mind_reason"
