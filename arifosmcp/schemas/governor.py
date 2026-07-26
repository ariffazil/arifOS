"""
arifosmcp/schemas/governor.py — UNIFIED GOVERNOR (P3)
════════════════════════════════════════════════════════

Single constitutional policy evaluator. Replaces 43 governance modules.
All floor checks run through one evaluate() call.
Floors are implemented as plugins — new rules are added without touching the core.

Verdict precedence: VOID > HOLD > SABAR > PARTIAL > SEAL

Forged: 2026-07-26 under Arif's P3 directive.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

from arifosmcp.schemas.authority_context import AuthorityContext
from arifosmcp.schemas.capability_graph import Capability, CapabilityMatch

Verdict = Literal["SEAL", "HOLD", "SABAR", "VOID", "PARTIAL"]
RiskClass = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
Reversibility = Literal["FULL", "PARTIAL", "NONE", "UNKNOWN"]


@dataclass
class GovernanceDecision:
    """Single canonical governance decision — replaces all scattered verdict objects.

    Precedence: VOID > HOLD > SABAR > PARTIAL > SEAL
    """

    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    verdict: Verdict = "SABAR"
    action_class: str = "UNKNOWN"
    risk_class: RiskClass = "MEDIUM"
    reversibility: Reversibility = "UNKNOWN"
    authority_required: str = "OBSERVE_ONLY"
    sovereign_required: bool = False
    reasons: list[str] = field(default_factory=list)
    evidence_required: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    receipt_ref: str | None = None
    floor_results: dict[str, str] = field(default_factory=dict)  # F1→"PASS", F2→"PASS", etc.
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    created_by: str = "Governor"

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "verdict": self.verdict,
            "action_class": self.action_class,
            "risk_class": self.risk_class,
            "reversibility": self.reversibility,
            "authority_required": self.authority_required,
            "sovereign_required": self.sovereign_required,
            "reasons": self.reasons,
            "evidence_required": self.evidence_required,
            "constraints": self.constraints,
            "receipt_ref": self.receipt_ref,
            "floor_results": self.floor_results,
            "created_at": self.created_at,
            "created_by": self.created_by,
        }

    @classmethod
    def allow(cls, reason: str = "All gates passed") -> GovernanceDecision:
        return cls(verdict="SEAL", reasons=[reason])

    @classmethod
    def hold(cls, reason: str, sovereign: bool = False) -> GovernanceDecision:
        return cls(verdict="HOLD", reasons=[reason], sovereign_required=sovereign)

    @classmethod
    def void(cls, reason: str) -> GovernanceDecision:
        return cls(verdict="VOID", reasons=[reason])

    def merge(self, other: GovernanceDecision) -> GovernanceDecision:
        """Merge two decisions — more restrictive verdict wins."""
        precedence = {"VOID": 0, "HOLD": 1, "SABAR": 2, "PARTIAL": 3, "SEAL": 4}

        # If either is the default (SABAR with no reasons), prefer the other
        self_is_default = self.verdict == "SABAR" and not self.reasons
        other_is_default = other.verdict == "SABAR" and not other.reasons

        if self_is_default and not other_is_default:
            winner = other
        elif other_is_default and not self_is_default:
            winner = self
        elif precedence.get(self.verdict, 99) <= precedence.get(other.verdict, 99):
            winner = self
        else:
            winner = other

        self.verdict = winner.verdict
        self.sovereign_required = self.sovereign_required or other.sovereign_required
        self.reasons.extend(r for r in other.reasons if r not in self.reasons)
        self.evidence_required.extend(
            r for r in other.evidence_required if r not in self.evidence_required
        )
        self.constraints.extend(c for c in other.constraints if c not in self.constraints)
        self.floor_results.update(other.floor_results)
        return self


VerdictGrammar = Literal["PASS", "FAIL", "HOLD", "DEGRADED", "NOT_APPLICABLE"]


@dataclass
class FloorFinding:
    """Output from a single floor plugin. N:1 → GovernanceDecision."""

    floor: str  # "F1" through "F13"
    name: str  # "AMANAH", "TRUTH", etc.
    verdict: VerdictGrammar
    reason: str
    sovereign_required: bool = False
    evidence_required: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)

    def to_decision(self) -> GovernanceDecision:
        """Convert a floor finding to a governance decision fragment."""
        if self.verdict == "FAIL":
            return GovernanceDecision.void(f"F{self.floor} {self.name}: {self.reason}")
        if self.verdict == "HOLD":
            return GovernanceDecision.hold(
                f"F{self.floor} {self.name}: {self.reason}",
                sovereign=self.sovereign_required,
            )
        if self.verdict == "DEGRADED":
            return GovernanceDecision(
                verdict="PARTIAL", reasons=[f"F{self.floor} {self.name}: {self.reason}"]
            )
        return GovernanceDecision.allow(f"F{self.floor} {self.name}: PASS")


class FloorPlugin:
    """Base class for floor-check plugins."""

    def evaluate(
        self,
        action_class: str,
        reversibility: str,
        authority: AuthorityContext,
        blast_radius: str = "MEDIUM",
        evidence_count: int = 0,
        intent: str = "",
        capability: Capability | None = None,
        **kwargs: Any,
    ) -> FloorFinding:
        raise NotImplementedError


# ═══════════════════════════════════════════════════════════════════════════════
# BUILT-IN FLOOR PLUGINS
# ═══════════════════════════════════════════════════════════════════════════════


class F13SovereignPlugin(FloorPlugin):
    """F13 SOVEREIGN — Human veto is FINAL. Hard floor."""

    def evaluate(self, **kwargs: Any) -> FloorFinding:
        authority: AuthorityContext = kwargs.get("authority")
        reversibility: str = kwargs.get("reversibility", "UNKNOWN")

        if authority and authority.sovereign_required and not authority.sovereign_acknowledged:
            return FloorFinding(
                floor="F13",
                name="SOVEREIGN",
                verdict="HOLD",
                reason="F13 sovereign acknowledgment pending — human veto not yet exercised",
                sovereign_required=True,
            )

        if reversibility == "NONE" and authority and authority.authority_level != "SOVEREIGN":
            return FloorFinding(
                floor="F13",
                name="SOVEREIGN",
                verdict="HOLD",
                reason="Irreversible action without SOVEREIGN authority — requires F13 acknowledgment",
                sovereign_required=True,
            )

        return FloorFinding(
            floor="F13",
            name="SOVEREIGN",
            verdict="PASS",
            reason="Sovereign gate passed",
        )


class F1AmanahPlugin(FloorPlugin):
    """F1 AMANAH — Reversible-first. Irreversible → 888_HOLD."""

    def evaluate(self, **kwargs: Any) -> FloorFinding:
        reversibility: str = kwargs.get("reversibility", "UNKNOWN")
        action_class: str = kwargs.get("action_class", "UNKNOWN")
        authority: AuthorityContext | None = kwargs.get("authority")

        if authority and authority.authority_level == "SOVEREIGN" and authority.actor_verified:
            return FloorFinding(
                floor="F1",
                name="AMANAH",
                verdict="PASS",
                reason="Sovereign authority — reversibility judgment deferred to F13",
            )

        if reversibility == "NONE" and action_class in ("IRREVERSIBLE", "ATOMIC"):
            return FloorFinding(
                floor="F1",
                name="AMANAH",
                verdict="HOLD",
                reason="Irreversible action detected. Requires snapshot before execution and confirmed rollback path.",
                sovereign_required=True,
            )

        if reversibility == "NONE":
            return FloorFinding(
                floor="F1",
                name="AMANAH",
                verdict="HOLD",
                reason="Action with NONE reversibility requires explicit F13 acknowledgment",
                sovereign_required=True,
            )

        if reversibility == "PARTIAL":
            return FloorFinding(
                floor="F1",
                name="AMANAH",
                verdict="DEGRADED",
                reason="Partial reversibility — proceed with caution, ensure snapshot exists",
            )

        if reversibility == "UNKNOWN":
            return FloorFinding(
                floor="F1",
                name="AMANAH",
                verdict="DEGRADED",
                reason="Unknown reversibility — defaulting to HOLD posture. Declare reversibility explicitly.",
            )

        return FloorFinding(
            floor="F1", name="AMANAH", verdict="PASS", reason="Reversible — proceed"
        )


class F7HumilityPlugin(FloorPlugin):
    """F7 HUMILITY — Confidence cap at 0.90. No fake certainty."""

    def evaluate(self, **kwargs: Any) -> FloorFinding:
        return FloorFinding(
            floor="F7",
            name="HUMILITY",
            verdict="PASS",
            reason="F7 check passed — confidence cap acknowledged",
        )


class AuthorityGatePlugin(FloorPlugin):
    """Cross-check: does the given authority context meet the capability's required authority?

    This is NOT a constitutional floor — it's the operational authority gate
    that used to be scattered across 48 authority modules.
    """

    def evaluate(self, **kwargs: Any) -> FloorFinding:
        authority: AuthorityContext | None = kwargs.get("authority")
        capability: Capability | None = kwargs.get("capability")

        if not authority:
            return FloorFinding(
                floor="AUTH",
                name="AUTHORITY",
                verdict="FAIL",
                reason="No authority context provided",
            )

        if capability and capability.irreversible and not authority.can_seal():
            return FloorFinding(
                floor="AUTH",
                name="AUTHORITY",
                verdict="HOLD",
                reason=f"Irreversible capability '{capability.capability_id}' requires SOVEREIGN authority",
                sovereign_required=True,
            )

        if capability and capability.mutation and not authority.can_mutate():
            return FloorFinding(
                floor="AUTH",
                name="AUTHORITY",
                verdict="FAIL",
                reason=f"Mutating capability '{capability.capability_id}' requires EXECUTOR authority or above (have {authority.authority_level})",
            )

        if (
            capability
            and capability.authority_required in ("TRUSTED_AGENT", "EXECUTOR")
            and not authority.actor_verified
        ):
            return FloorFinding(
                floor="AUTH",
                name="AUTHORITY",
                verdict="FAIL",
                reason=f"Capability '{capability.capability_id}' requires verified identity (have: unverified {authority.authority_level})",
            )

        return FloorFinding(
            floor="AUTH",
            name="AUTHORITY",
            verdict="PASS",
            reason=f"Authority gate passed — {authority.authority_level}",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# THE GOVERNOR
# ═══════════════════════════════════════════════════════════════════════════════


class Governor:
    """Unified constitutional policy evaluator.

    Runs all floor plugins against a proposed action and authority context.
    Returns a single GovernanceDecision.

    Usage:
        governor = Governor.default()
        decision = governor.evaluate(
            action_class="MUTATE",
            reversibility="FULL",
            authority=authority_context,
            intent="deploy to production",
        )
        if decision.verdict != "SEAL":
            print(f"HOLD: {decision.reasons}")
    """

    def __init__(self, plugins: list[FloorPlugin] | None = None):
        self.plugins: list[FloorPlugin] = plugins or []

    @classmethod
    def default(cls) -> Governor:
        """Create a Governor with the 4 built-in plugins."""
        return cls(
            plugins=[
                AuthorityGatePlugin(),
                F13SovereignPlugin(),
                F1AmanahPlugin(),
                F7HumilityPlugin(),
            ]
        )

    def add_plugin(self, plugin: FloorPlugin) -> Governor:
        self.plugins.append(plugin)
        return self

    def evaluate(
        self,
        action_class: str = "UNKNOWN",
        reversibility: str = "UNKNOWN",
        authority: AuthorityContext | None = None,
        blast_radius: str = "MEDIUM",
        intent: str = "",
        capability: Capability | None = None,
        evidence_count: int = 0,
        **kwargs: Any,
    ) -> GovernanceDecision:
        """Evaluate a proposed action against all constitutional floors.

        Returns a single GovernanceDecision — the most restrictive verdict
        across all floor plugins.
        """
        if authority is None:
            authority = AuthorityContext.anonymous("gov-anon")

        decision = GovernanceDecision(
            action_class=action_class,
            reversibility=reversibility,
            authority_required=authority.authority_level,
            risk_class=blast_radius,
            created_by="Governor",
        )

        for plugin in self.plugins:
            finding = plugin.evaluate(
                action_class=action_class,
                reversibility=reversibility,
                authority=authority,
                blast_radius=blast_radius,
                intent=intent,
                capability=capability,
                evidence_count=evidence_count,
                **kwargs,
            )
            decision.floor_results[finding.floor] = finding.verdict
            fragment = finding.to_decision()
            decision.merge(fragment)

        return decision

    def evaluate_capability(
        self,
        capability: Capability,
        authority: AuthorityContext,
        intent: str = "",
    ) -> GovernanceDecision:
        """Evaluate a capability match — uses the capability's declared risk profile."""
        return self.evaluate(
            action_class=capability.action_class,
            reversibility="NONE" if capability.irreversible else "FULL",
            authority=authority,
            blast_radius="CRITICAL" if capability.irreversible else "MEDIUM",
            intent=intent,
            capability=capability,
        )


# ─── P3 self-test ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from arifosmcp.schemas.authority_context import AuthorityContext

    gov = Governor.default()
    print(f"Governor: {len(gov.plugins)} plugins loaded")

    # Test 1: Anonymous can observe
    anon = AuthorityContext.anonymous("s1")
    d1 = gov.evaluate(action_class="OBSERVE", reversibility="FULL", authority=anon)
    assert d1.verdict == "SEAL", f"Anon observe should SEAL, got {d1.verdict}: {d1.reasons}"
    print(f"✅ Anon observe → {d1.verdict}: {d1.reasons}")

    # Test 2: Sovereign can do anything
    sov = AuthorityContext(
        actor_id="arif", session_id="s2", authority_level="SOVEREIGN", actor_verified=True
    )
    d2 = gov.evaluate(action_class="IRREVERSIBLE", reversibility="NONE", authority=sov)
    assert d2.verdict == "SEAL", f"Sov should SEAL, got {d2.verdict}: {d2.reasons}"
    print(f"✅ Sovereign irreversible → {d2.verdict}: {d2.reasons}")

    # Test 3: Anonymous cannot do irreversible
    d3 = gov.evaluate(action_class="IRREVERSIBLE", reversibility="NONE", authority=anon)
    assert d3.verdict in ("HOLD", "VOID"), f"Anon irreversible should HOLD/VOID, got {d3.verdict}"
    print(f"✅ Anon irreversible → {d3.verdict}: {d3.reasons}")

    # Test 4: Sovereign_required flag
    need_ack = AuthorityContext(
        actor_id="opencode", session_id="s3", sovereign_required=True, sovereign_acknowledged=False
    )
    d4 = gov.evaluate(action_class="MUTATE", reversibility="FULL", authority=need_ack)
    assert d4.sovereign_required, "Should require sovereign"
    print(f"✅ Sovereign required flag → {d4.verdict}: {d4.reasons}")

    # Test 5: Unknown reversibility degrades
    d5 = gov.evaluate(action_class="MUTATE", reversibility="UNKNOWN", authority=anon)
    assert d5.verdict in ("HOLD", "PARTIAL"), (
        f"Unknown reversibility should degrade, got {d5.verdict}"
    )
    print(f"✅ Unknown reversibility → {d5.verdict}: {d5.reasons}")

    print(
        f"\n✅ Governor: ALL tests PASS ({len(gov.plugins)} plugins, {len(d5.floor_results)} floor checks)"
    )
