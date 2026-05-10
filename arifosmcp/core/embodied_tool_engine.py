"""
arifOS Embodied Tool Engine — Tool Use with Body, Boundary, and Witness
═══════════════════════════════════════════════════════════════════════════════════════

The embodied tool loop:

    RECEIVE → SENSE BOUND → CLASSIFY → CHECK AUTHORITY
    → CHECK REVERSIBILITY → SIMULATE → ACT OR HOLD
    → WITNESS → REVIEW

This is the body of the agentic tool system.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any

from arifosmcp.core.reversibility_engine import (
    ReversibilityEngine,
    ReversibilityVerdict,
    classify_tool_base,
)
from arifosmcp.core.tool_self_model import (
    BlastRadius,
    ToolManifest,
    ToolSelfModel,
    ToolSelfModelEntry,
    get_tool_self_model,
)
from arifosmcp.schemas.embodied_tool import (
    Domain,
    EmbodiedToolEnvelope,
    Reversibility,
    RiskTier,
    UncertaintyItem,
    build_embodied_envelope,
)

logger = logging.getLogger(__name__)


@dataclass
class EmbodiedDecision:
    """Result of embodied tool pre-flight checks."""

    can_proceed: bool
    status: str  # SEAL | HOLD | VOID | ESCALATE
    reason: str
    risk_tier: RiskTier
    reversibility: Reversibility
    authority_required: bool
    authority_verified: bool
    uncertainty: list[UncertaintyItem]
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class EmbodiedToolEngine:
    """
    The complete embodied tool execution engine.

    Every tool call goes through this pipeline:

    1. RECEIVE — accept raw params
    2. SENSE — get tool manifest from self-model
    3. BOUND — check domain boundary
    4. CLASSIFY — assign risk tier
    5. CHECK PERMISSIONS — authority verification
    6. CHECK REVERSIBILITY — F01 AMANAH
    7. ESTIMATE CONSEQUENCE — blast radius
    8. ACT OR HOLD — execute or escalate
    9. WITNESS — record audit trail
    10. UPDATE SELF-MODEL — mark used, record result

    Usage:
        engine = EmbodiedToolEngine()
        decision = await engine.run_preflight(
            tool_id="arif_mind_reason",
            params={"query": "What is the capital of France?"},
            actor_id="arif",
            session_id="sess_abc123",
        )
        if not decision.can_proceed:
            return decision  # HOLD or VOID
        result = await tool.execute(params)
        envelope = await engine.run_postflight(
            tool_id="arif_mind_reason",
            params={"query": "What is the capital of France?"},
            actor_id="arif",
            session_id="sess_abc123",
            decision=decision,
            result=result,
            latency_ms=234.5,
        )
    """

    def __init__(self, tool_self_model: ToolSelfModel | None = None):
        self.self_model = tool_self_model or get_tool_self_model()
        self.reversibility_engine = ReversibilityEngine()

    # ── Pipeline Stage 1: Receive ───────────────────────────────────────────

    def receive(self, tool_id: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Stage 1: RECEIVE.
        Validate inputs are present and well-formed.
        """
        errors = []
        if not tool_id:
            errors.append("tool_id is required")
        if not isinstance(params, dict):
            errors.append("params must be a dict")
        if errors:
            raise ValueError("; ".join(errors))
        return params

    # ── Pipeline Stage 2-3: Sense + Bound ──────────────────────────────────

    def sense_and_bound(self, tool_id: str, actor_id: str | None) -> ToolSelfModelEntry:
        """
        Stage 2: SENSE — get tool manifest from self-model.
        Stage 3: BOUND — verify domain boundary.

        Returns ToolSelfModelEntry or raises.
        """
        entry = self.self_model.get(tool_id)
        if entry is None:
            raise KeyError(
                f"Tool {tool_id} not in self-model. "
                f"Available: {list(self.self_model._tools.keys())}"
            )

        # Domain boundary check: is this tool allowed to be called by this actor?
        # (In a full implementation, this would check actor's domain permissions)
        return entry

    # ── Pipeline Stage 4: Classify Risk ─────────────────────────────────────

    def classify_risk(self, entry: ToolSelfModelEntry, params: dict[str, Any]) -> RiskTier:
        """
        Stage 4: CLASSIFY.
        Assign T0-T4 risk tier based on tool manifest + params.
        """
        # Start from tool's declared risk tier
        declared = entry.manifest.risk_tier

        # Upgrade based on params
        params_str = str(params).lower()

        # Dangerous flags upgrade risk
        dangerous_flags = [
            "sudo",
            "force",
            "override",
            "bypass",
            "production",
            "--force",
            "-f",
        ]
        for flag in dangerous_flags:
            if flag in params_str:
                # Upgrade by one tier
                tier_order = ["T0", "T1", "T2", "T3", "T4"]
                current_idx = tier_order.index(declared) if declared in tier_order else 1
                next_idx = min(current_idx + 1, len(tier_order) - 1)
                declared = tier_order[next_idx]

        return RiskTier(declared)

    # ── Pipeline Stage 5: Check Authority ────────────────────────────────────

    def check_authority(
        self,
        entry: ToolSelfModelEntry,
        actor_id: str | None,
        session_id: str | None,
        risk_tier: RiskTier,
    ) -> tuple[bool, bool, str]:
        """
        Stage 5: CHECK AUTHORITY.
        Verify actor has permission for this tool at this risk tier.

        Returns: (authority_required, authority_verified, reason)
        """
        # T0-T1: No authority required
        if risk_tier in (RiskTier.T0, RiskTier.T1):
            return False, True, "T0/T1 — no authority required"

        # T2-T4: Authority required
        if not session_id:
            return True, False, f"T{risk_tier.value} requires session_id"

        # Check permission gap
        if entry.has_permission_gap:
            gap = entry.permission_gap
            return (
                True,
                False,
                f"Permission gap: missing {gap}",
            )

        return True, True, "Authority verified"

    # ── Pipeline Stage 6: Check Reversibility ───────────────────────────────

    def check_reversibility(
        self,
        tool_id: str,
        params: dict[str, Any],
        entry: ToolSelfModelEntry,
    ) -> ReversibilityVerdict:
        """
        Stage 6: CHECK REVERSIBILITY — F01 AMANAH.

        Returns ReversibilityVerdict with full assessment.
        """
        base_class = classify_tool_base(tool_id)
        return self.reversibility_engine.assess(
            tool_id=tool_id,
            params=params,
            tool_base_class=base_class,
        )

    # ── Pipeline Stage 7: Estimate Consequence ──────────────────────────────

    def estimate_consequence(
        self,
        entry: ToolSelfModelEntry,
        reversibility_verdict: ReversibilityVerdict,
    ) -> tuple[BlastRadius, str]:
        """
        Stage 7: ESTIMATE CONSEQUENCE.
        Compute blast radius from tool manifest + reversibility.

        Returns: (blast_radius, description)
        """
        manifest_radius = entry.manifest.blast_radius

        # Upgrade if irreversible
        if reversibility_verdict.is_irreversible:
            radius_order = ["low", "medium", "high", "critical"]
            current_idx = radius_order.index(manifest_radius.value)
            next_idx = min(current_idx + 1, len(radius_order) - 1)
            manifest_radius = BlastRadius(radius_order[next_idx])

        return manifest_radius, f"Blast radius: {manifest_radius.value}"

    # ── Pipeline Stage 8: Decision ─────────────────────────────────────────

    def decide(
        self,
        risk_tier: RiskTier,
        reversibility_verdict: ReversibilityVerdict,
        authority_required: bool,
        authority_verified: bool,
        entry: ToolSelfModelEntry,
    ) -> EmbodiedDecision:
        """
        Stage 8: DECIDE.
        Combine all checks into a single decision.
        """
        uncertainty: list[UncertaintyItem] = []
        warnings: list[str] = []

        # Check critical irreversibility first
        if reversibility_verdict.is_critical:
            return EmbodiedDecision(
                can_proceed=False,
                status="VOID",
                reason=f"F01 CRITICAL: {reversibility_verdict.reasoning}",
                risk_tier=risk_tier,
                reversibility=Reversibility.IRREVERSIBLE,
                authority_required=True,
                authority_verified=False,
                uncertainty=uncertainty,
                warnings=warnings,
                metadata={
                    "matched_patterns": reversibility_verdict.matched_patterns,
                    "blast_radius": reversibility_verdict.blast_radius_estimate,
                },
            )

        # Check irreversible
        if reversibility_verdict.is_irreversible:
            if not authority_verified:
                return EmbodiedDecision(
                    can_proceed=False,
                    status="HOLD",
                    reason="F01 IRREVERSIBLE + no authority: requires 888_HOLD",
                    risk_tier=risk_tier,
                    reversibility=Reversibility.IRREVERSIBLE,
                    authority_required=True,
                    authority_verified=False,
                    uncertainty=uncertainty,
                    warnings=[f"Matched: {reversibility_verdict.matched_patterns}"],
                    metadata={
                        "matched_patterns": reversibility_verdict.matched_patterns,
                        "blast_radius": reversibility_verdict.blast_radius_estimate,
                    },
                )

        # Check authority
        if authority_required and not authority_verified:
            return EmbodiedDecision(
                can_proceed=False,
                status="HOLD",
                reason="Authority not verified: session_id required",
                risk_tier=risk_tier,
                reversibility=Reversibility(
                    "reversible"
                    if reversibility_verdict.reversibility_class.value == "trivial"
                    else reversibility_verdict.reversibility_class.value
                ),
                authority_required=True,
                authority_verified=False,
                uncertainty=uncertainty,
                warnings=[],
            )

        # Check T4 risk
        if risk_tier == RiskTier.T4:
            return EmbodiedDecision(
                can_proceed=False,
                status="HOLD",
                reason="T4 risk tier requires Arif approval",
                risk_tier=risk_tier,
                reversibility=Reversibility(
                    "reversible"
                    if reversibility_verdict.reversibility_class.value == "trivial"
                    else reversibility_verdict.reversibility_class.value
                ),
                authority_required=True,
                authority_verified=authority_verified,
                uncertainty=uncertainty,
                warnings=[],
            )

        # Check permission gap
        if entry.has_permission_gap:
            return EmbodiedDecision(
                can_proceed=False,
                status="HOLD",
                reason=f"Permission gap: {entry.permission_gap}",
                risk_tier=risk_tier,
                reversibility=Reversibility(
                    "reversible"
                    if reversibility_verdict.reversibility_class.value == "trivial"
                    else reversibility_verdict.reversibility_class.value
                ),
                authority_required=True,
                authority_verified=False,
                uncertainty=uncertainty,
                warnings=[],
            )

        # Default: proceed with SEAL
        return EmbodiedDecision(
            can_proceed=True,
            status="SEAL",
            reason="All checks passed",
            risk_tier=risk_tier,
            reversibility=Reversibility(
                "reversible"
                if reversibility_verdict.reversibility_class.value == "trivial"
                else reversibility_verdict.reversibility_class.value
            ),
            authority_required=authority_required,
            authority_verified=authority_verified,
            uncertainty=uncertainty,
            warnings=[],
            metadata={
                "blast_radius": reversibility_verdict.blast_radius_estimate,
                "matched_patterns": reversibility_verdict.matched_patterns,
            },
        )

    # ── Full Pipeline: run_preflight ──────────────────────────────────────

    async def run_preflight(
        self,
        tool_id: str,
        params: dict[str, Any],
        actor_id: str | None = None,
        session_id: str | None = None,
    ) -> EmbodiedDecision:
        """
        Run the full embodied pre-flight pipeline.

        Returns EmbodiedDecision with can_proceed and full reasoning.
        """
        # Stage 1: Receive
        self.receive(tool_id, params)

        # Stage 2-3: Sense + Bound
        entry = self.sense_and_bound(tool_id, actor_id)

        # Stage 4: Classify risk
        risk_tier = self.classify_risk(entry, params)

        # Stage 5: Check authority
        authority_required, authority_verified, auth_reason = self.check_authority(
            entry, actor_id, session_id, risk_tier
        )

        # Stage 6: Check reversibility
        rev_verdict = self.check_reversibility(tool_id, params, entry)

        # Stage 7: Estimate consequence
        blast_radius, blast_reason = self.estimate_consequence(entry, rev_verdict)

        # Stage 8: Decide
        decision = self.decide(
            risk_tier=risk_tier,
            reversibility_verdict=rev_verdict,
            authority_required=authority_required,
            authority_verified=authority_verified,
            entry=entry,
        )

        # Add blast radius to metadata
        decision.metadata["blast_radius"] = blast_radius.value

        return decision

    # ── Post-flight: Build Envelope ───────────────────────────────────────

    async def run_postflight(
        self,
        tool_id: str,
        params: dict[str, Any],
        actor_id: str | None,
        session_id: str | None,
        decision: EmbodiedDecision,
        result: dict[str, Any],
        latency_ms: float | None = None,
        error: str | None = None,
        confidence: float = 0.5,
        reasoning_summary: str = "",
    ) -> EmbodiedToolEnvelope:
        """
        Stage 9: WITNESS.
        Build the full EmbodiedToolEnvelope after execution.

        This must be called after every tool execution.
        """
        domain = self._infer_domain(tool_id)

        # Build input hash for witness
        input_hash = hashlib.sha256(
            f"{tool_id}:{actor_id}:{session_id}:{str(params)}".encode()
        ).hexdigest()

        # Compute uncertainty from result
        uncertainty = self._extract_uncertainty(result)

        envelope = build_embodied_envelope(
            tool_id=tool_id,
            tool_name=tool_id,
            domain=Domain(domain),
            actor_id=actor_id,
            session_id=session_id,
            risk_tier=decision.risk_tier,
            reversibility=decision.reversibility,
            authority_required=decision.authority_required,
            authority_verified=decision.authority_verified,
            result=result,
            witness_input_hash=input_hash,
            reasoning_summary=reasoning_summary,
            confidence=confidence,
            uncertainty=uncertainty,
            status=decision.status,
            error=error,
            latency_ms=latency_ms,
            metadata=decision.metadata,
        )

        # Stage 10: Update self-model
        # (self-model update is handled by EmbodiedTool.postflight()
        #  to avoid double-update when run_postflight() is called directly)
        return envelope

    # ── Helpers ─────────────────────────────────────────────────────────────

    def update_self_model_from_outcome(
        self,
        tool_id: str,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        """
        Update the global self-model after tool execution.

        Called by EmbodiedTool.postflight() after every execution.
        This closes the feedback loop: execute → witness → update self-model.

        The smart summary extraction (verdict, confidence, latency) lives
        in ToolSelfModel.update_from_outcome().
        """
        self.self_model.update_from_outcome(
            tool_id=tool_id,
            result=result,
            error=error,
        )

    def _infer_domain(self, tool_id: str) -> str:
        """Infer domain from tool ID prefix.

        Returns Domain enum *value* (not name) so it can be passed to Domain().
        """
        if tool_id.startswith("arif_"):
            return "arifOS"
        elif tool_id.startswith("well_"):
            return "WELL"
        elif tool_id.startswith("wealth_"):
            return "WEALTH"
        elif tool_id.startswith("geox_"):
            return "GEOX"
        return "unknown"

    def _extract_uncertainty(self, result: dict[str, Any]) -> list[UncertaintyItem]:
        """Extract uncertainty items from result."""
        uncertainty = []
        # Look for confidence in result
        if "confidence" in result:
            conf = float(result["confidence"])
            if conf < 0.8:
                uncertainty.append(
                    UncertaintyItem(
                        source="model_confidence",
                        description=f"Confidence {conf:.2f} below 0.80 threshold",
                        impact="medium",
                    )
                )
        # Look for uncertainty flags
        if "uncertainty" in result and isinstance(result["uncertainty"], list):
            for u in result["uncertainty"]:
                if isinstance(u, dict):
                    uncertainty.append(
                        UncertaintyItem(
                            source=u.get("source", "result"),
                            description=u.get("description", str(u)),
                            impact=u.get("impact", "medium"),
                        )
                    )
        return uncertainty


# Global singleton
_embodied_engine: EmbodiedToolEngine | None = None


def get_embodied_tool_engine() -> EmbodiedToolEngine:
    """Get the global embodied tool engine singleton."""
    global _embodied_engine
    if _embodied_engine is None:
        _embodied_engine = EmbodiedToolEngine()
    return _embodied_engine


# ── Convenience decorator ─────────────────────────────────────────────────────


def embodied_tool(
    tool_id: str,
    tool_name: str,
    domain: str,
    risk_tier: str = "T1",
    reversibility: str = "reversible",
    required_permissions: list[str] | None = None,
    capabilities: list[dict[str, Any]] | None = None,
    limitations: list[dict[str, Any]] | None = None,
    safe_compose_with: list[str] | None = None,
    dangerous_compose_with: list[str] | None = None,
):
    """
    Decorator to register a tool function with the embodied self-model.

    Usage:
        @embodied_tool(
            tool_id="arif_mind_reason",
            tool_name="arif_mind_reason",
            domain="AOS",
            risk_tier="T1",
            reversibility="reversible",
            required_permissions=["session_init"],
        )
        async def mind_reason(params, ctx):
            ...
    """
    from arifosmcp.core.tool_self_model import (
        ToolCapability,
        ToolLimitation,
        register_tool_in_self_model,
    )

    capabilities_obj = [ToolCapability(**c) for c in capabilities] if capabilities else []
    limitations_obj = [ToolLimitation(**lim) for lim in limitations] if limitations else []

    manifest = ToolManifest(
        tool_id=tool_id,
        tool_name=tool_name,
        domain=domain,
        description=f"Tool: {tool_name}",
        capabilities=capabilities_obj,
        limitations=limitations_obj,
        risk_tier=risk_tier,
        reversibility=reversibility,
        required_permissions=required_permissions or [],
        safe_compose_with=safe_compose_with or [],
        dangerous_compose_with=dangerous_compose_with or [],
    )

    def decorator(func):
        register_tool_in_self_model(manifest)
        return func

    return decorator


__all__ = [
    "EmbodiedDecision",
    "EmbodiedToolEngine",
    "get_embodied_tool_engine",
    "embodied_tool",
]
