"""
arifOS Federation Contracts — Organ Boundary Manifest
══════════════════════════════════════════════════════

Single source of truth for orthogonal MCP alignment.
Every organ declares:
  - what it owns (its truth domain)
  - what it must NEVER touch (forbidden domains)
  - what authority it holds (advisory_only vs adjudicative)
  - what outputs it may emit (observation, signal, assessment)
  - what verdicts it is FORBIDDEN from emitting (SEAL, VOID, HOLD, SABAR)

Only arifOS may emit verdicts.
Only arifOS may synthesize cross-organ evidence.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AuthorityLevel(StrEnum):
    """Authority levels in descending order of power."""

    SOVEREIGN = "sovereign"  # Arif only
    ADJUDICATIVE = "adjudicative"  # arifOS only — can emit verdicts
    ADVISORY = "advisory"  # Organs — can observe, assess, signal
    INSTRUMENT = "instrument"  # Sensors — raw data only


class OutputType(StrEnum):
    """Allowed output types for non-arifOS organs."""

    OBSERVATION = "observation"
    ASSESSMENT = "assessment"
    SIGNAL = "signal"
    PRESSURE = "pressure"
    FORECAST = "forecast"
    CONSTRAINT = "constraint"
    UNCERTAINTY = "uncertainty"


class VerdictType(StrEnum):
    """Verdict types — ONLY arifOS may emit these."""

    SEAL = "SEAL"
    HOLD = "HOLD"
    VOID = "VOID"
    SABAR = "SABAR"


class OrganContract(BaseModel):
    """
    Federation contract for a single organ.

    Enforced by arifOS 888_JUDGE and 777_WITNESS gates.
    Violations trigger constitutional floor alerts (L10 ONTOLOGY, L13 SOVEREIGN).
    """

    organ: str = Field(..., description="Canonical organ name")
    owns: list[str] = Field(..., description="Truth domains this organ owns exclusively")
    forbidden_domains: list[str] = Field(
        default_factory=list, description="Domains this organ must NEVER touch"
    )
    authority: AuthorityLevel = Field(..., description="Maximum authority this organ holds")
    allowed_outputs: list[OutputType] = Field(
        default_factory=list, description="Output types this organ may emit"
    )
    forbidden_outputs: list[str] = Field(
        default_factory=list, description="Output types this organ must NEVER emit"
    )
    cannot_emit_verdicts: list[VerdictType] = Field(
        default=[VerdictType.SEAL, VerdictType.HOLD, VerdictType.VOID, VerdictType.SABAR],
        description="Verdict types this organ is forbidden from emitting",
    )
    physics: str = Field(..., description="The single physics this organ speaks")
    notes: str = Field(default="", description="Human-readable boundary notes")

    def validate_output(self, output: dict[str, Any]) -> dict[str, Any]:
        """
        Runtime boundary check — strip any forbidden verdicts from organ output.
        Returns sanitized output + violation flags.
        """
        violations: list[str] = []
        sanitized = dict(output)

        # Strip forbidden verdicts
        if "verdict" in sanitized:
            v = sanitized["verdict"]
            if v in {ve.value for ve in self.cannot_emit_verdicts}:
                violations.append(f"{self.organ}_verdict_violation:{v}")
                sanitized["verdict"] = "OBSERVATION"
                sanitized["_boundary_note"] = (
                    f"{self.organ} attempted to emit {v}. "
                    "Downgraded to OBSERVATION. arifOS alone adjudicates."
                )

        return {
            "output": sanitized,
            "violations": violations,
            "boundary_enforced": len(violations) > 0,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Canonical Federation Contracts — F1–L13 enforced
# ═══════════════════════════════════════════════════════════════════════════════

FEDERATION_CONTRACTS: dict[str, OrganContract] = {
    "arifos": OrganContract(
        organ="arifos",
        owns=[
            "constitutional governance",
            "routing",
            "adjudication",
            "seal",
            "audit",
            "constraint",
        ],
        forbidden_domains=[
            "earth physics",
            "capital optimization",
            "biological diagnosis",
            "execution metabolism",
        ],
        authority=AuthorityLevel.ADJUDICATIVE,
        allowed_outputs=[
            OutputType.OBSERVATION,
            OutputType.ASSESSMENT,
            OutputType.SIGNAL,
            OutputType.PRESSURE,
            OutputType.CONSTRAINT,
            OutputType.UNCERTAINTY,
        ],
        forbidden_outputs=["raw_biometric_data", "raw_seismic_data", "raw_capital_data"],
        cannot_emit_verdicts=[],  # arifOS MAY emit all verdicts
        physics="constraint / governance",
        notes="Supreme Court + Air Traffic Control. Observes, routes, judges, seals, audits, constrains. Never does domain work directly.",
    ),
    "geox": OrganContract(
        organ="geox",
        owns=[
            "subsurface truth",
            "seismic truth",
            "petrophysical truth",
            "geological uncertainty",
            "physics constraints",
        ],
        forbidden_domains=["capital", "governance", "biology", "execution", "morality"],
        authority=AuthorityLevel.ADVISORY,
        allowed_outputs=[
            OutputType.OBSERVATION,
            OutputType.UNCERTAINTY,
            OutputType.CONSTRAINT,
            OutputType.FORECAST,
        ],
        forbidden_outputs=["verdict", "seal", "economic_recommendation", "health_advice"],
        cannot_emit_verdicts=[
            VerdictType.SEAL,
            VerdictType.HOLD,
            VerdictType.VOID,
            VerdictType.SABAR,
        ],
        physics="matter / earth",
        notes="Only answers: 'What is physically true about Earth?' No economics, no ops prioritization, no governance, no WELL state.",
    ),
    "wealth": OrganContract(
        organ="wealth",
        owns=["NPV", "liquidity", "leverage", "economic entropy", "incentives", "regime analysis"],
        forbidden_domains=[
            "geology",
            "biological readiness",
            "constitutional legitimacy",
            "ethics",
            "morality",
        ],
        authority=AuthorityLevel.ADVISORY,
        allowed_outputs=[
            OutputType.OBSERVATION,
            OutputType.ASSESSMENT,
            OutputType.PRESSURE,
            OutputType.FORECAST,
            OutputType.SIGNAL,
        ],
        forbidden_outputs=["verdict", "seal", "medical_advice", "geological_truth"],
        cannot_emit_verdicts=[
            VerdictType.SEAL,
            VerdictType.HOLD,
            VerdictType.VOID,
            VerdictType.SABAR,
        ],
        physics="capital / flow",
        notes="Only answers: 'What preserves or destroys capital?' No geology, no health, no execution, no morality.",
    ),
    "well": OrganContract(
        organ="well",
        owns=[
            "fatigue",
            "stress",
            "readiness",
            "biological telemetry",
            "cognitive pressure",
            "machine stress coupling",
        ],
        forbidden_domains=[
            "governance",
            "routing",
            "constitutional judgment",
            "consensus authority",
            "execution authority",
            "capital optimization",
            "geology",
        ],
        authority=AuthorityLevel.ADVISORY,
        allowed_outputs=[
            OutputType.OBSERVATION,
            OutputType.ASSESSMENT,
            OutputType.SIGNAL,
            OutputType.PRESSURE,
        ],
        forbidden_outputs=[
            "verdict",
            "seal",
            "governance_assessment",
            "routing_decision",
            "economic_recommendation",
        ],
        cannot_emit_verdicts=[
            VerdictType.SEAL,
            VerdictType.HOLD,
            VerdictType.VOID,
            VerdictType.SABAR,
        ],
        physics="biological substrate",
        notes="Only answers: 'Is the substrate stable enough for cognition/execution?' No governance, no routing, no consensus, no seal.",
    ),
    "a_forge": OrganContract(
        organ="a_forge",
        owns=["plan", "execute", "rollback", "deploy", "audit"],
        forbidden_domains=[
            "governance",
            "adjudication",
            "seal",
            "earth physics",
            "capital optimization",
            "biological diagnosis",
        ],
        authority=AuthorityLevel.ADVISORY,
        allowed_outputs=[
            OutputType.OBSERVATION,
            OutputType.ASSESSMENT,
            OutputType.SIGNAL,
            OutputType.CONSTRAINT,
        ],
        forbidden_outputs=["verdict", "seal", "governance_assessment", "routing_decision"],
        cannot_emit_verdicts=[
            VerdictType.SEAL,
            VerdictType.HOLD,
            VerdictType.VOID,
            VerdictType.SABAR,
        ],
        physics="energy / work",
        notes="Controlled mutation under governance. Suggests execution plans. Never self-authorizes. Waits for arifOS verdict.",
    ),
    "aaa": OrganContract(
        organ="aaa",
        owns=["agent coordination", "session orchestration", "A2A mesh"],
        forbidden_domains=[
            "governance",
            "adjudication",
            "seal",
            "earth physics",
            "capital optimization",
            "biological diagnosis",
        ],
        authority=AuthorityLevel.ADVISORY,
        allowed_outputs=[OutputType.OBSERVATION, OutputType.SIGNAL, OutputType.CONSTRAINT],
        forbidden_outputs=["verdict", "seal", "governance_assessment"],
        cannot_emit_verdicts=[
            VerdictType.SEAL,
            VerdictType.HOLD,
            VerdictType.VOID,
            VerdictType.SABAR,
        ],
        physics="coordination / relay",
        notes="Routes agents, manages sessions, bridges A2A. Never adjudicates, never seals.",
    ),
}


def get_contract(organ: str) -> OrganContract | None:
    """Return the federation contract for a given organ, or None if unregistered."""
    return FEDERATION_CONTRACTS.get(organ)


def list_contracts() -> dict[str, OrganContract]:
    """Return all federation contracts."""
    return dict(FEDERATION_CONTRACTS)


def validate_organ_output(organ: str, output: dict[str, Any]) -> dict[str, Any]:
    """
    Validate an organ's output against its federation contract.
    Returns sanitized output + any boundary violations.
    """
    contract = get_contract(organ)
    if contract is None:
        return {
            "output": output,
            "violations": ["unknown_organ"],
            "boundary_enforced": True,
        }
    return contract.validate_output(output)
