"""
symbolic_router.py — MCP-SYMBOLIC-HARDEN-v1 — Envelope Validator & Symbol Router
════════════════════════════════════════════════════════════════════════════════

Spec:  /root/arifOS/forge_work/MCP-SYMBOLIC-HARDEN-v1.md §2, §4.1, §7, §8
Real path: /root/arifOS/arifosmcp/core/symbolic_router.py
            (spec said /opt/arifos/app/mcp_servers/_core/symbolic_router.py — that path does not exist)

F13 OVERRIDE TASK (2026-06-28 05:08 UTC): "Go and execute. Don't ask again."
F2 TRUTH OVERRIDE: spec paths /opt/arifos/app/mcp_servers/* do NOT exist.

Doctrine:
  Before routing any non-trivial request to a tool, classify the language
  into literal vs symbolic, identify the implied authority, and decide
  whether HOLD is required.

This module is INTERNAL middleware. It does NOT expose a new externally-
visible MCP tool. It validates the envelope BEFORE the existing
arif_triage / arif_judge / arif_forge lane takes over.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


REQUIRED_FIELDS: tuple[str, ...] = (
    "literal_request",
    "symbolic_meaning",
    "authority_implied",
    "authority_verified",
    "symbol_owner",
    "domain",
    "reversibility",
    "blast_radius",
    "maruah_adab_risk",
    "institutional_risk",
    "false_seal_risk",
    "ritual_vs_protocol",
    "evidence_layer",
    "correct_existing_tool",
    "hold_required",
)


class SymbolOwner(str, Enum):
    ARIF = "Arif"
    ARIFOS = "arifOS"
    VAULT999 = "VAULT999"
    INSTITUTION = "institution"
    UNKNOWN = "unknown"


class AuthorityClaim(str, Enum):
    NONE = "none"
    PERSONAL = "personal"
    INSTITUTIONAL = "institutional"
    FINANCIAL = "financial"
    LEGAL = "legal"
    SOVEREIGN = "sovereign"
    SACRED = "sacred"


class Reversibility(str, Enum):
    REVERSIBLE = "reversible"
    SEMI_IRREVERSIBLE = "semi_irreversible"
    IRREVERSIBLE = "irreversible"


class BlastRadius(str, Enum):
    PRIVATE = "private"
    TEAM = "team"
    PUBLIC = "public"
    INSTITUTIONAL = "institutional"
    LEGAL = "legal"
    FINANCIAL = "financial"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RitualVsProtocol(str, Enum):
    PROTOCOL = "protocol"
    RITUAL = "ritual"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class EvidenceLayer(str, Enum):
    L0_OBSERVATION = "L0_observation"
    L1_DERIVATION = "L1_derivation"
    L2_INTERPRETATION = "L2_interpretation"
    L3_SPECULATION = "L3_speculation"


@dataclass(frozen=True)
class EnvelopeError:
    field: str
    reason: str
    code: str  # MISSING | INVALID_VALUE | INCOHERENT


@dataclass(frozen=True)
class EnvelopeVerdict:
    accepted: bool
    envelope_sha256: str
    missing: tuple[str, ...]
    errors: tuple[EnvelopeError, ...]
    hold_recommended: bool
    route_to: str | None
    audit: dict[str, Any] = field(default_factory=dict)


def _check_value(field_name: str, value: Any) -> EnvelopeError | None:
    if value is None:
        return EnvelopeError(field_name, "value is None", "MISSING")
    if isinstance(value, str) and not value.strip():
        return EnvelopeError(field_name, "value is empty string", "MISSING")
    return None


def _coherence_checks(env: dict[str, Any]) -> list[EnvelopeError]:
    errs: list[EnvelopeError] = []

    # 1. authority_verified=True required for irreversible.
    if env.get("reversibility") == Reversibility.IRREVERSIBLE.value:
        if env.get("authority_verified") is not True:
            errs.append(
                EnvelopeError(
                    "authority_verified",
                    "irreversible action requires authority_verified=True",
                    "INCOHERENT",
                )
            )

    # 2. symbol_owner == unknown forbidden if routing to a tool.
    if env.get("symbol_owner") == SymbolOwner.UNKNOWN.value:
        if env.get("correct_existing_tool"):
            errs.append(
                EnvelopeError(
                    "symbol_owner",
                    "symbol_owner=unknown cannot route to a tool; "
                    "spec §E hard rule: refuse judgment",
                    "INCOHERENT",
                )
            )

    # 3. ritual without constitutional domain must HOLD.
    if env.get("ritual_vs_protocol") == RitualVsProtocol.RITUAL.value:
        if env.get("domain") not in ("arifos_constitutional",):
            if env.get("hold_required") is not True:
                errs.append(
                    EnvelopeError(
                        "hold_required",
                        "ritual language without constitutional domain "
                        "must hold for human review",
                        "INCOHERENT",
                    )
                )

    # 4. false_seal_risk=high → hold_required=True.
    if env.get("false_seal_risk") == RiskLevel.HIGH.value:
        if env.get("hold_required") is not True:
            errs.append(
                EnvelopeError(
                    "hold_required",
                    "false_seal_risk=high mandates HOLD for human review",
                    "INCOHERENT",
                )
            )

    # 5. maruah_adab_risk=high → reversibility must NOT be irreversible.
    if env.get("maruah_adab_risk") == RiskLevel.HIGH.value:
        if env.get("reversibility") == Reversibility.IRREVERSIBLE.value:
            errs.append(
                EnvelopeError(
                    "reversibility",
                    "maruah/adab risk high forbids irreversible execution; "
                    "downgrade reversibility or escalate",
                    "INCOHERENT",
                )
            )

    # 6. blast_radius=legal/financial/institutional requires evidence_layer >= L2.
    if env.get("blast_radius") in (
        BlastRadius.LEGAL.value,
        BlastRadius.FINANCIAL.value,
        BlastRadius.INSTITUTIONAL.value,
    ):
        if env.get("evidence_layer") in (
            EvidenceLayer.L3_SPECULATION.value,
            None,
        ):
            errs.append(
                EnvelopeError(
                    "evidence_layer",
                    "wide blast_radius requires evidence_layer >= L2_interpretation",
                    "INCOHERENT",
                )
            )

    # 7. correct_existing_tool must be non-empty string.
    ct = env.get("correct_existing_tool")
    if ct is not None and isinstance(ct, str) and not ct.strip():
        errs.append(
            EnvelopeError(
                "correct_existing_tool",
                "must be a non-empty string or null",
                "INVALID_VALUE",
            )
        )

    return errs


def validate(envelope: dict[str, Any] | None) -> EnvelopeVerdict:
    if not isinstance(envelope, dict):
        return EnvelopeVerdict(
            accepted=False,
            envelope_sha256=hashlib.sha256(b"").hexdigest(),
            missing=REQUIRED_FIELDS,
            errors=tuple(
                EnvelopeError("<root>", "envelope is not a dict", "MISSING")
                for _ in REQUIRED_FIELDS
            ),
            hold_recommended=True,
            route_to=None,
            audit={"reason": "non-dict envelope"},
        )

    missing: list[str] = []
    errors: list[EnvelopeError] = []

    for fname in REQUIRED_FIELDS:
        if fname not in envelope:
            missing.append(fname)
            errors.append(EnvelopeError(fname, "field missing", "MISSING"))
            continue
        v = envelope.get(fname)
        if v is None:
            missing.append(fname)
            errors.append(EnvelopeError(fname, "value is None", "MISSING"))
        elif isinstance(v, str) and not v.strip():
            missing.append(fname)
            errors.append(EnvelopeError(fname, "value is empty string", "MISSING"))

    if "authority_verified" in envelope:
        if not isinstance(envelope["authority_verified"], bool):
            errors.append(
                EnvelopeError(
                    "authority_verified",
                    "must be bool",
                    "INVALID_VALUE",
                )
            )

    if "hold_required" in envelope:
        if not isinstance(envelope["hold_required"], bool):
            errors.append(
                EnvelopeError(
                    "hold_required",
                    "must be bool",
                    "INVALID_VALUE",
                )
            )

    errors.extend(_coherence_checks(envelope))

    accepted = not errors
    hold_recommended = bool(envelope.get("hold_required")) or any(
        e.code in ("INCOHERENT",) for e in errors
    )

    route_to = envelope.get("correct_existing_tool") if accepted else None
    if isinstance(route_to, str):
        route_to = route_to.strip() or None

    env_sha = hashlib.sha256(
        repr(sorted(envelope.items())).encode("utf-8")
    ).hexdigest()

    return EnvelopeVerdict(
        accepted=accepted,
        envelope_sha256=env_sha,
        missing=tuple(missing),
        errors=tuple(errors),
        hold_recommended=hold_recommended,
        route_to=route_to,
        audit={
            "ts": time.time(),
            "missing_count": len(missing),
            "error_count": len(errors),
            "hold_recommended": hold_recommended,
            "accepted": accepted,
        },
    )


def make_envelope(
    *,
    literal_request: str,
    symbolic_meaning: str,
    authority_implied: str,
    authority_verified: bool,
    symbol_owner: str,
    domain: str,
    reversibility: str,
    blast_radius: str,
    maruah_adab_risk: str,
    institutional_risk: str,
    false_seal_risk: str,
    ritual_vs_protocol: str,
    evidence_layer: str,
    correct_existing_tool: str | None,
    hold_required: bool,
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    env: dict[str, Any] = {
        "literal_request": literal_request,
        "symbolic_meaning": symbolic_meaning,
        "authority_implied": authority_implied,
        "authority_verified": authority_verified,
        "symbol_owner": symbol_owner,
        "domain": domain,
        "reversibility": reversibility,
        "blast_radius": blast_radius,
        "maruah_adab_risk": maruah_adab_risk,
        "institutional_risk": institutional_risk,
        "false_seal_risk": false_seal_risk,
        "ritual_vs_protocol": ritual_vs_protocol,
        "evidence_layer": evidence_layer,
        "correct_existing_tool": correct_existing_tool,
        "hold_required": hold_required,
    }
    if extras:
        env.update(extras)
    return env


def _selftest() -> int:
    fails = 0
    total = 0

    def case(name: str, envelope: dict[str, Any] | None, expect_accepted: bool):
        nonlocal fails, total
        total += 1
        v = validate(envelope)
        ok = v.accepted == expect_accepted
        status = "PASS" if ok else "FAIL"
        print(
            f"[{status}] {name}: accepted={v.accepted} "
            f"missing={len(v.missing)} errors={len(v.errors)} "
            f"hold={v.hold_recommended}"
        )
        if not ok:
            fails += 1
            for e in v.errors:
                print(f"    - {e.code} {e.field}: {e.reason}")

    case("none_envelope", None, expect_accepted=False)
    case("empty_envelope", {}, expect_accepted=False)

    almost = make_envelope(
        literal_request="Seal this receipt",
        symbolic_meaning="authoritative closure",
        authority_implied="constitutional",
        authority_verified=True,
        symbol_owner=SymbolOwner.ARIFOS.value,
        domain="arifos_constitutional",
        reversibility=Reversibility.SEMI_IRREVERSIBLE.value,
        blast_radius=BlastRadius.INSTITUTIONAL.value,
        maruah_adab_risk=RiskLevel.LOW.value,
        institutional_risk=RiskLevel.MEDIUM.value,
        false_seal_risk=RiskLevel.LOW.value,
        ritual_vs_protocol=RitualVsProtocol.PROTOCOL.value,
        evidence_layer=EvidenceLayer.L1_DERIVATION.value,
        correct_existing_tool="arif_seal",
        hold_required=False,
    )
    del almost["literal_request"]
    case("missing_literal_request", almost, expect_accepted=False)

    almost2 = make_envelope(
        literal_request="Seal this receipt",
        symbolic_meaning="authoritative closure",
        authority_implied="constitutional",
        authority_verified=True,
        symbol_owner=SymbolOwner.ARIFOS.value,
        domain="arifos_constitutional",
        reversibility=Reversibility.SEMI_IRREVERSIBLE.value,
        blast_radius=BlastRadius.INSTITUTIONAL.value,
        maruah_adab_risk=RiskLevel.LOW.value,
        institutional_risk=RiskLevel.MEDIUM.value,
        false_seal_risk=RiskLevel.LOW.value,
        ritual_vs_protocol=RitualVsProtocol.PROTOCOL.value,
        evidence_layer=EvidenceLayer.L1_DERIVATION.value,
        correct_existing_tool="arif_seal",
        hold_required=False,
    )
    almost2["symbolic_meaning"] = ""
    case("empty_symbolic_meaning", almost2, expect_accepted=False)

    incoherent = make_envelope(
        literal_request="publish the report",
        symbolic_meaning="external commitment",
        authority_implied="institutional",
        authority_verified=False,
        symbol_owner=SymbolOwner.ARIF.value,
        domain="general",
        reversibility=Reversibility.IRREVERSIBLE.value,
        blast_radius=BlastRadius.PUBLIC.value,
        maruah_adab_risk=RiskLevel.LOW.value,
        institutional_risk=RiskLevel.HIGH.value,
        false_seal_risk=RiskLevel.LOW.value,
        ritual_vs_protocol=RitualVsProtocol.PROTOCOL.value,
        evidence_layer=EvidenceLayer.L1_DERIVATION.value,
        correct_existing_tool="arif_forge",
        hold_required=True,
    )
    case("irreversible_without_authority", incoherent, expect_accepted=False)

    unknown_owner = make_envelope(
        literal_request="approve",
        symbolic_meaning="closure",
        authority_implied="unknown",
        authority_verified=False,
        symbol_owner=SymbolOwner.UNKNOWN.value,
        domain="general",
        reversibility=Reversibility.SEMI_IRREVERSIBLE.value,
        blast_radius=BlastRadius.TEAM.value,
        maruah_adab_risk=RiskLevel.LOW.value,
        institutional_risk=RiskLevel.LOW.value,
        false_seal_risk=RiskLevel.MEDIUM.value,
        ritual_vs_protocol=RitualVsProtocol.UNKNOWN.value,
        evidence_layer=EvidenceLayer.L0_OBSERVATION.value,
        correct_existing_tool="arif_judge",
        hold_required=True,
    )
    case("symbol_owner_unknown_with_route", unknown_owner, expect_accepted=False)

    ritual = make_envelope(
        literal_request="close it out",
        symbolic_meaning="ritual closure",
        authority_implied="personal",
        authority_verified=True,
        symbol_owner=SymbolOwner.ARIF.value,
        domain="general",
        reversibility=Reversibility.REVERSIBLE.value,
        blast_radius=BlastRadius.PRIVATE.value,
        maruah_adab_risk=RiskLevel.LOW.value,
        institutional_risk=RiskLevel.LOW.value,
        false_seal_risk=RiskLevel.LOW.value,
        ritual_vs_protocol=RitualVsProtocol.RITUAL.value,
        evidence_layer=EvidenceLayer.L1_DERIVATION.value,
        correct_existing_tool=None,
        hold_required=False,
    )
    case("ritual_without_hold", ritual, expect_accepted=False)

    false_seal = make_envelope(
        literal_request="seal the deal",
        symbolic_meaning="final commitment",
        authority_implied="financial",
        authority_verified=False,
        symbol_owner=SymbolOwner.ARIF.value,
        domain="wealth",
        reversibility=Reversibility.SEMI_IRREVERSIBLE.value,
        blast_radius=BlastRadius.FINANCIAL.value,
        maruah_adab_risk=RiskLevel.LOW.value,
        institutional_risk=RiskLevel.MEDIUM.value,
        false_seal_risk=RiskLevel.HIGH.value,
        ritual_vs_protocol=RitualVsProtocol.RITUAL.value,
        evidence_layer=EvidenceLayer.L2_INTERPRETATION.value,
        correct_existing_tool="wealth_governance_verdict",
        hold_required=False,
    )
    case("false_seal_high_without_hold", false_seal, expect_accepted=False)

    maruah_irrev = make_envelope(
        literal_request="",
        symbolic_meaning="",
        authority_implied="",
        authority_verified=True,
        symbol_owner=SymbolOwner.ARIF.value,
        domain="well",
        reversibility=Reversibility.IRREVERSIBLE.value,
        blast_radius=BlastRadius.PRIVATE.value,
        maruah_adab_risk=RiskLevel.HIGH.value,
        institutional_risk=RiskLevel.LOW.value,
        false_seal_risk=RiskLevel.LOW.value,
        ritual_vs_protocol=RitualVsProtocol.PROTOCOL.value,
        evidence_layer=EvidenceLayer.L1_DERIVATION.value,
        correct_existing_tool=None,
        hold_required=True,
    )
    case("maruah_high_irreversible", maruah_irrev, expect_accepted=False)

    legal_l3 = make_envelope(
        literal_request="file the claim",
        symbolic_meaning="",
        authority_implied="legal",
        authority_verified=True,
        symbol_owner=SymbolOwner.ARIF.value,
        domain="general",
        reversibility=Reversibility.IRREVERSIBLE.value,
        blast_radius=BlastRadius.LEGAL.value,
        maruah_adab_risk=RiskLevel.LOW.value,
        institutional_risk=RiskLevel.HIGH.value,
        false_seal_risk=RiskLevel.LOW.value,
        ritual_vs_protocol=RitualVsProtocol.PROTOCOL.value,
        evidence_layer=EvidenceLayer.L3_SPECULATION.value,
        correct_existing_tool="arif_forge",
        hold_required=True,
    )
    case("legal_radius_l3_evidence", legal_l3, expect_accepted=False)

    happy = make_envelope(
        literal_request="Constitutional SEAL the receipt after arif_judge verdict.",
        symbolic_meaning="verdict closure, audit-only social effect",
        authority_implied="constitutional",
        authority_verified=True,
        symbol_owner=SymbolOwner.ARIFOS.value,
        domain="arifos_constitutional",
        reversibility=Reversibility.SEMI_IRREVERSIBLE.value,
        blast_radius=BlastRadius.INSTITUTIONAL.value,
        maruah_adab_risk=RiskLevel.LOW.value,
        institutional_risk=RiskLevel.MEDIUM.value,
        false_seal_risk=RiskLevel.LOW.value,
        ritual_vs_protocol=RitualVsProtocol.PROTOCOL.value,
        evidence_layer=EvidenceLayer.L1_DERIVATION.value,
        correct_existing_tool="arif_seal",
        hold_required=False,
    )
    case("happy_path", happy, expect_accepted=True)

    if fails:
        print(f"\n{fails}/{total} cases FAILED")
        return 1
    print(f"\nAll {total} cases PASSED")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())