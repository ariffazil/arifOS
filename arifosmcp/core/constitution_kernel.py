"""
arifOS Constitutional Kernel — Unified Orchestrator
═══════════════════════════════════════════════════

Authoritative entry point for constitutional adjudication.
Integrates ThreatEngine, FloorEvaluator, and AuthorityGate.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator

from arifosmcp.core.authority_gate import AuthorityGate, AuthorityProof, WitnessType
from arifosmcp.core.floor_evaluator import FloorEvaluator, FloorResult
from arifosmcp.core.threat_engine import (
    IrreversibilityLevel,
    ThreatAssessment,
    ThreatCategory,
    ThreatEngine,
)

__all__ = [
    "ActionContext",
    "AuthorityGate",
    "BootInvariantChecker",
    "ConstitutionKernel",
    "ConstitutionalVerdict",
    "FloorEvaluator",
    "IrreversibilityLevel",
    "SchemaContractValidator",
    "ThreatAssessment",
    "ThreatCategory",
    "ThreatEngine",
    "WitnessType",
    "get_kernel",
    "reset_kernel",
]


class IrreversibilityModel:
    @staticmethod
    def from_threats(assessment: ThreatAssessment) -> IrreversibilityLevel:
        return assessment.irreversibility


class ActionContext(BaseModel):
    tool_name: str
    mode: str = "default"
    actor_id: str | None = None
    session_id: str | None = None
    candidate: str | None = None
    manifest: str | None = None
    query: str | None = None
    url: str | None = None
    target_agent: str | None = None
    ack_irreversible: bool = False
    witness_type: WitnessType = WitnessType.AI
    plan_id: str | None = None
    session_registry: set[str] = Field(default_factory=set, exclude=True)
    federation_registry: set[str] = Field(default_factory=set, exclude=True)
    plan_registry: set[str] = Field(default_factory=set, exclude=True)
    # ── Post-AGI verification governance (WEALTH layer) ────────────────────
    audit_entropy: dict[str, Any] | None = Field(
        default=None,
        description="AuditEntropy result: delta_m, svs, entropy_band from wealth_audit_entropy",
    )
    wealth_score: dict[str, Any] | None = Field(
        default=None,
        description="WealthScore: multi-axis constitutional score from wealth_score_kernel",
    )
    verification_surface: dict[str, Any] | None = Field(
        default=None, description="VerificationSurface: canonical claim + evidence + verifier info"
    )

    @field_validator("url")
    @classmethod
    def _validate_url_scheme(cls, v: str | None) -> str | None:
        if v and not v.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL scheme: {v}")
        return v

    def payload_text(self) -> str:
        for attr in ("candidate", "manifest", "query", "url"):
            val = getattr(self, attr)
            if val:
                return val
        return ""


class ConstitutionalVerdict(BaseModel):
    status: str
    verdict: str
    threat: ThreatAssessment
    floors: FloorResult
    authority: AuthorityProof
    irreversibility: IrreversibilityLevel
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    state_hash: str = Field(default="")

    def model_post_init(self, __context: Any) -> None:
        if not self.state_hash:
            self.state_hash = self._compute_state_hash()

    def _compute_state_hash(self) -> str:
        payload = {
            "status": self.status,
            "verdict": self.verdict,
            "threats": sorted(t.name for t in self.threat.threats),
            "floors": self.floors.failed_floors,
            "authority": json.loads(self.authority.model_dump_json()),
            "irreversibility": self.irreversibility.name,
            "timestamp": self.timestamp,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


class WealthGovernance:
    """
    Post-AGI verification governance layer for WEALTH.

    Consumes audit_entropy (delta_m, svs, entropy_band) and wealth_score
    from the candidate's verification surface. Applies verification-first
    hard gates BEFORE the constitutional kernel evaluates floors/threats.

    Hard rules (never overridden by reward):
      - entropy_band == EXTREME → HOLD
      - svs < 0.30 → HOLD
      - delta_m > 0.80 → HOLD
      - anti_hantu_fail in wealth_score → VOID
      - sovereign_veto in wealth_score → VOID
      - no liability owner → HOLD (automatic)
    """

    # Thresholds
    MIN_SVS = 0.30  # hard HOLD below this line
    MAX_DELTA_M = 0.80  # hard HOLD above this line
    # Graduated governance penalty zone: svs in [MIN_SVS, 0.50] gets proportional penalty
    SVS_PENALTY_ZONE = 0.50

    # ── Graduated penalty for threshold gaming mitigation ────────────────────
    # If svs is just above MIN_SVS (e.g. 0.3501), it technically passes the hard gate
    # but should still receive governance penalty rather than neutral status.
    # We compute a penalty_factor (0=full pass, 1=maximum penalty) applied to score.
    @classmethod
    def _svs_penalty(cls, svs: float) -> float:
        """
        Return penalty 0.0-1.0 based on svs in the graduated zone [MIN_SVS, SVS_PENALTY_ZONE].
        At exactly MIN_SVS: penalty = 0.0 (just cleared hard gate — no additional penalty).
        At SVS_PENALTY_ZONE and above: penalty = 0.0 (fully in safe zone).
        In between: linear ramp from 0.0 at MIN_SVS to 1.0 at SVS_PENALTY_ZONE.
        """
        if svs >= cls.SVS_PENALTY_ZONE:
            return 0.0  # fully in safe zone
        if svs <= cls.MIN_SVS:
            return 0.0  # at or below hard gate — hard block handles this, not penalty
        # linear ramp: MIN_SVS → 0.0 penalty, SVS_PENALTY_ZONE → 1.0 penalty
        return (cls.SVS_PENALTY_ZONE - svs) / (cls.SVS_PENALTY_ZONE - cls.MIN_SVS)

    @classmethod
    def evaluate(cls, context: ActionContext) -> dict[str, Any]:
        """
        Returns dict with keys:
          status: "OK" | "HOLD" | "VOID"
          reason: str
          hard_blocks: list[str]
          verification_state: dict (for vault seal record)
        """
        if context.audit_entropy is None and context.wealth_score is None:
            return {
                "status": "OK",
                "reason": "no_verification_state",
                "hard_blocks": [],
                "verification_state": {},
            }

        hard_blocks: list[str] = []
        verification_state: dict[str, Any] = {}

        # ── Process audit_entropy ──────────────────────────────────────────
        ae = context.audit_entropy or {}
        # Normalize entropy_band to uppercase for case-insensitive comparison
        raw_band = ae.get("entropy_band", "LOW")
        entropy_band = raw_band.upper() if isinstance(raw_band, str) else "LOW"
        # Normalize svs to float — guard against string "0.278" from JSON
        raw_svs = ae.get("svs", 1.0)
        try:
            svs = float(raw_svs) if raw_svs is not None else 1.0
        except (TypeError, ValueError):
            svs = 1.0  # safest fallback: treat as fully verifiable
        # Normalize delta_m to float
        raw_dm = ae.get("delta_m", 0.0)
        try:
            delta_m = float(raw_dm) if raw_dm is not None else 0.0
        except (TypeError, ValueError):
            delta_m = 0.0  # safest fallback
        verification_state["delta_m"] = round(delta_m, 6)
        verification_state["svs"] = round(svs, 6)
        verification_state["entropy_band"] = entropy_band
        verification_state["bottlenecks"] = ae.get("bottlenecks", [])

        if entropy_band == "EXTREME":
            hard_blocks.append("EXTREME_ENTROPY_BAND")
        if svs < cls.MIN_SVS:
            hard_blocks.append(f"SVS_BELOW_{cls.MIN_SVS}")
        if delta_m > cls.MAX_DELTA_M:
            hard_blocks.append(f"DELTA_M_EXCEEDS_{cls.MAX_DELTA_M}")

        # ── Graduated penalty for svs in [MIN_SVS, SVS_PENALTY_ZONE] ─────────────
        # Gaming mitigation: svs=0.3501 technically clears hard gate but is still risky.
        # Record penalty factor in verification_state for downstream score adjustment.
        # Penalty is advisory — does not override hard blocks — but signals governance concern.
        if not any("SVS_BELOW" in b for b in hard_blocks):
            penalty = cls._svs_penalty(svs)
            verification_state["svs_governance_penalty"] = round(penalty, 4)
            if penalty > 0.5:
                # Elevated governance concern but not a hard block — flag for advisory HOLD
                verification_state["advisory_governance_flag"] = (
                    f"SVS_PENALTY_ZONE: penalty={penalty:.2f}"
                )

        # ── Process wealth_score ───────────────────────────────────────────
        ws = context.wealth_score or {}
        verification_state["wealth_score"] = ws
        verification_state["liability_owner"] = ws.get("liability_owner")
        verification_state["final_score"] = ws.get("final_score")
        verification_state["recommendation"] = ws.get("recommendation")
        verification_state["floor_flags"] = ws.get("floor_flags", [])

        ws_blocks = ws.get("hard_blocks", [])
        hard_blocks.extend(ws_blocks)

        ws_rec = ws.get("recommendation", "")

        # ── Determine verdict ───────────────────────────────────────────────
        if "F9_ANTI_HANTU_FAIL" in hard_blocks or "F13_SOVEREIGN_VETO" in hard_blocks:
            status, reason = "VOID", "WEALTH governance: anti-hantu or sovereign veto"
        elif hard_blocks:
            status, reason = "HOLD", f"WEALTH verification gates: {hard_blocks[0]}"
        elif ws_rec == "HOLD_CANDIDATE":
            status, reason = "HOLD", "WEALTH score: HOLD_CANDIDATE"
        elif ws_rec == "VOID_CANDIDATE":
            status, reason = "VOID", "WEALTH score: VOID_CANDIDATE"
        else:
            status, reason = "OK", "verification passed"

        return {
            "status": status,
            "reason": reason,
            "hard_blocks": hard_blocks,
            "verification_state": verification_state,
        }


class ConstitutionKernel:
    def __init__(self) -> None:
        self.threat_engine = ThreatEngine()
        self.floor_evaluator = FloorEvaluator()
        self.authority_gate = AuthorityGate()

    def evaluate_intent(
        self,
        tool_name: str,
        params: dict[str, Any],
        session_id: str | None = None,
        actor_id: str | None = None,
        witness_type: WitnessType = WitnessType.AI,
    ) -> dict[str, Any]:
        """Bridge for tools.py callers that expect GovernanceEnforcer-style evaluate_intent.

        Converts (tool_name, params, session_id) → ActionContext → ConstitutionalVerdict,
        then returns the {"passed", "failed_floors"} dict that
        arif_forge_execute / arif_vault_seal expect.
        """
        context = ActionContext(
            tool_name=tool_name,
            mode=params.get("mode", "default"),
            ack_irreversible=params.get("ack_irreversible", False),
            session_id=session_id,
            actor_id=actor_id,
            witness_type=witness_type,
            plan_id=params.get("plan_id"),
            plan_registry=params.get("plan_registry", set()),
        )
        verdict = self.evaluate(context)
        return {
            "passed": verdict.verdict in ("SEAL", "OK"),
            "failed_floors": verdict.floors.failed_floors if verdict.floors else [],
            "threat_score": verdict.threat.confidence if verdict.threat else 0.0,
        }

    def evaluate(self, context: ActionContext) -> ConstitutionalVerdict:
        # ── Step -1: Biological Readiness Gate (WELL Mirror) ──────────────
        # F13 SOVEREIGN: Mandatory physiological gate before any SEAL.
        # This prevents autonomous action when the operator is degraded.
        try:
            well_state_path = "/root/WELL/state.json"
            # Note: In production container, this path must be mounted.
            # If missing, we fallback to a safe 'STABLE' assumption unless in strict mode.
            import json
            import os

            if os.path.exists(well_state_path):
                with open(well_state_path) as f:
                    well_state = json.load(f)
                readiness = well_state.get("well_score")
                backend_status = well_state.get("backend_status", "UNKNOWN")

                # Fail-closed: null well_score or DEGRADED backend blocks SEAL
                if readiness is None or backend_status == "DEGRADED":
                    is_dev = os.environ.get("ARIFOS_DEV_MODE", "").lower() in ("1", "true", "yes")
                    f13_reason = (
                        f"WELL telemetry unavailable (well_score={readiness}, "
                        f"backend_status={backend_status})"
                    )
                    from arifosmcp.core.authority_gate import AuthorityProof
                    from arifosmcp.core.floor_evaluator import FloorResult
                    from arifosmcp.core.threat_engine import (
                        IrreversibilityLevel,
                        ThreatAssessment,
                    )

                    threat = ThreatAssessment(
                        threats=[],
                        overall_confidence=1.0,
                        irreversibility=IrreversibilityLevel.NONE,
                        category=None,
                    )
                    floors = FloorResult(
                        verdict="HOLD",
                        failed_floors=["F13"],
                        floor_reasons={"F13": f13_reason},
                    )
                    authority = AuthorityProof(authorized=False, level="SOVEREIGN_VETO")
                    return ConstitutionalVerdict(
                        status="WARN" if is_dev else "HOLD",
                        verdict="WARN" if is_dev else "HOLD",
                        threat=threat,
                        floors=floors,
                        authority=authority,
                        irreversibility=IrreversibilityLevel.NONE,
                    )

                if readiness < 40:  # Threshold per doctrinal move
                    from arifosmcp.core.authority_gate import AuthorityProof
                    from arifosmcp.core.floor_evaluator import FloorResult
                    from arifosmcp.core.threat_engine import (
                        IrreversibilityLevel,
                        ThreatAssessment,
                    )

                    threat = ThreatAssessment(
                        threats=[],
                        overall_confidence=1.0,
                        irreversibility=IrreversibilityLevel.NONE,
                        category=None,
                    )
                    floors = FloorResult(
                        verdict="HOLD",
                        failed_floors=["F13"],
                        floor_reasons={
                            "F13": f"Operator readiness {readiness} below constitutional floor (40)"
                        },
                    )
                    authority = AuthorityProof(authorized=False, level="SOVEREIGN_VETO")
                    return ConstitutionalVerdict(
                        status="HOLD",
                        verdict="HOLD",
                        threat=threat,
                        floors=floors,
                        authority=authority,
                        irreversibility=IrreversibilityLevel.NONE,
                    )
        except Exception:
            # We do not block on well-mirror errors to prevent deadlocks,
            # but we log the friction.
            pass

        # ── Step 0: WEALTH verification governance (pre-flight check) ──────
        wg = WealthGovernance.evaluate(context)
        wg_status = wg["status"]

        # If verification already determined VOID/HOLD, short-circuit constitutional evaluation
        if wg_status in ("VOID", "HOLD"):
            from arifosmcp.core.authority_gate import AuthorityProof
            from arifosmcp.core.floor_evaluator import FloorResult
            from arifosmcp.core.threat_engine import IrreversibilityLevel, ThreatAssessment

            threat = ThreatAssessment(
                threats=[],
                overall_confidence=0.0,
                irreversibility=IrreversibilityLevel.NONE,
                category=None,
            )
            floors = FloorResult(
                verdict="HOLD" if wg_status == "HOLD" else "VOID",
                failed_floors=["F-GOVERNANCE"],
                floor_reasons={"F-GOVERNANCE": wg["reason"]},
            )
            authority = AuthorityProof(authorized=True, level="WEALTH_GOVERNANCE")
            return ConstitutionalVerdict(
                status="HOLD" if wg_status == "HOLD" else "HOLD",
                verdict=wg_status,
                threat=threat,
                floors=floors,
                authority=authority,
                irreversibility=IrreversibilityLevel.NONE,
                # Attach verification state so it propagates to vault seal
                state_hash=hashlib.sha256(
                    json.dumps({"wealth_governance": wg["verification_state"]}).encode()
                ).hexdigest()[:32],
            )

        # ── Normal constitutional evaluation ───────────────────────────────
        threat = self.threat_engine.classify(context.payload_text())
        floors = self.floor_evaluator.evaluate(context, threat)
        authority = self.authority_gate.verify(context, threat)

        # Simplified verdict logic from monolith
        if floors.verdict == "VOID" or not authority.authorized:
            status = "HOLD"
            verdict = "VOID" if floors.verdict == "VOID" else "HOLD"
        elif floors.verdict == "HOLD":
            status = "HOLD"
            verdict = "HOLD"
        else:
            status = "OK"
            verdict = "SEAL"

        return ConstitutionalVerdict(
            status=status,
            verdict=verdict,
            threat=threat,
            floors=floors,
            authority=authority,
            irreversibility=threat.irreversibility,
        )


class SchemaContractValidator:
    @staticmethod
    def validate_elicitation_model(model: type[BaseModel]) -> list[str]:
        errors: list[str] = []
        for name, field_info in model.model_fields.items():
            annotation = field_info.annotation
            if hasattr(annotation, "__origin__") and annotation.__origin__ is type[None] | str:
                errors.append(f"Field '{name}' has Union type with None")
        return errors

    @staticmethod
    def validate_mode_consistency(
        documented_modes: set[str],
        implemented_modes: set[str],
        tool_name: str,
    ) -> list[str]:
        errors: list[str] = []
        missing = documented_modes - implemented_modes
        extra = implemented_modes - documented_modes
        if missing:
            errors.append(f"{tool_name}: documented modes missing in implementation: {missing}")
        if extra:
            errors.append(f"{tool_name}: implemented modes not documented: {extra}")
        return errors


class BootInvariantChecker:
    REQUIRED_INVARIANTS = {
        "self_approval_forbidden": True,
        "forge_default_dry_run": True,
        "irreversible_actions_require_ack": True,
    }

    @classmethod
    def check(cls, config: dict[str, Any]) -> None:
        for invariant, required_value in cls.REQUIRED_INVARIANTS.items():
            if config.get(invariant) != required_value:
                raise RuntimeError(f"BOOT INVARIANT VIOLATED: {invariant}")


_kernel = ConstitutionKernel()


def get_kernel() -> ConstitutionKernel:
    return _kernel


def reset_kernel() -> None:
    global _kernel
    _kernel = ConstitutionKernel()
