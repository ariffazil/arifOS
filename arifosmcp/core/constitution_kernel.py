"""
arifOS Constitutional Kernel — Unified Orchestrator
═══════════════════════════════════════════════════

Authoritative entry point for constitutional adjudication.
Integrates ThreatEngine, FloorEvaluator, and AuthorityGate.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field, field_validator

from arifosmcp.core.threat_engine import ThreatEngine, ThreatAssessment, IrreversibilityLevel, ThreatCategory, THREAT_IRREVERSIBILITY
from arifosmcp.core.floor_evaluator import FloorEvaluator, FloorResult
from arifosmcp.core.authority_gate import AuthorityGate, AuthorityProof, WitnessType

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

    @field_validator("url")
    @classmethod
    def _validate_url_scheme(cls, v: str | None) -> str | None:
        if v and not v.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL scheme: {v}")
        return v

    def payload_text(self) -> str:
        for attr in ("candidate", "manifest", "query", "url"):
            val = getattr(self, attr)
            if val: return val
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
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

class ConstitutionKernel:
    def __init__(self) -> None:
        self.threat_engine = ThreatEngine()
        self.floor_evaluator = FloorEvaluator()
        self.authority_gate = AuthorityGate()

    def evaluate(self, context: ActionContext) -> ConstitutionalVerdict:
        threat = self.threat_engine.classify(context.payload_text())
        floors = self.floor_evaluator.evaluate(context, threat)
        authority = self.authority_gate.verify(context, threat)

        # Simplified verdict logic from monolith
        if floors.verdict == "VOID" or not authority.authorized:
            status = "HOLD"
            verdict = "VOID" if floors.verdict == "VOID" else "HOLD"
        elif floors.verdict == "HOLD":
            status = "HOLD"; verdict = "HOLD"
        else:
            status = "OK"; verdict = "SEAL"

        return ConstitutionalVerdict(
            status=status,
            verdict=verdict,
            threat=threat,
            floors=floors,
            authority=authority,
            irreversibility=threat.irreversibility
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
