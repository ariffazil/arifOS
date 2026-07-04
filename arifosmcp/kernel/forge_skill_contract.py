"""
arifosmcp/kernel/forge_skill_contract.py — governed dynamic capability contract

This is the contract layer for `forge_skill`, not an implementation that writes
or executes code by itself.

The purpose is to make dynamic capability generation admissible only when the
constitutional invariants are satisfied:

- no self-modification of forge_skill
- no direct ToolRegistry mutation by generated tools
- no VAULT999 write without a seal verdict
- no irreversible generated capability without F13/HOLD path
- schema and code fingerprints before registration
- HARAM scan before registration and before first execution
- APEX Decision Field energy before draft admissibility

DITEMPA BUKAN DIBERI — tools are forged, but the forge is governed.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from arifosmcp.kernel.apex_decision_field import (
    ApexDecisionField,
    ApexDecisionVerdict,
    assess_apex_decision_field,
)


class ForgeSkillVerdict(StrEnum):
    """Verdict for a generated capability request."""

    ADMIT_DRAFT = "ADMIT_DRAFT"
    HOLD_888 = "888_HOLD"
    VOID = "VOID"


class GeneratedCapabilityClass(StrEnum):
    """How the generated capability touches reality."""

    READ = "READ"
    TRANSFORM = "TRANSFORM"
    MUTATE = "MUTATE"
    IRREVERSIBLE = "IRREVERSIBLE"


class ForgeSkillDenyCode(StrEnum):
    """Machine-readable reasons a forge_skill request cannot proceed."""

    MISSING_SEAL_VERDICT = "MISSING_SEAL_VERDICT"
    SELF_MODIFICATION = "SELF_MODIFICATION"
    REGISTRY_BYPASS = "REGISTRY_BYPASS"
    VAULT_BYPASS = "VAULT_BYPASS"
    HARAM_PATTERN = "HARAM_PATTERN"
    SCHEMA_MISSING = "SCHEMA_MISSING"
    IRREVERSIBLE_REQUIRES_F13 = "IRREVERSIBLE_REQUIRES_F13"
    DOMAIN_MISSING = "DOMAIN_MISSING"
    INTENT_MISSING = "INTENT_MISSING"
    APEX_DECISION_FIELD_HOLD = "APEX_DECISION_FIELD_HOLD"
    APEX_DECISION_FIELD_VOID = "APEX_DECISION_FIELD_VOID"


SELF_MODIFICATION_TARGETS: frozenset[str] = frozenset(
    {
        "forge_skill",
        "forge_skill_contract",
        "forge_registry",
        "tool_registry",
        "ToolRegistry",
        "VAULT999",
        "vault999",
    }
)

HARAM_CODE_PATTERNS: frozenset[str] = frozenset(
    {
        "eval(",
        "exec(",
        "subprocess.Popen",
        "os.system",
        "shutil.rmtree",
        "rm -rf",
        "curl | bash",
        "wget | bash",
        "chmod 777",
        "pickle.loads",
        "yaml.load(",
    }
)

REGISTRY_BYPASS_PATTERNS: frozenset[str] = frozenset(
    {
        "ToolRegistry.write",
        "ToolRegistry.register",
        "tool_registry.write",
        "tool_registry.register",
        "registry.register(",
        "registry.write(",
    }
)

VAULT_BYPASS_PATTERNS: frozenset[str] = frozenset(
    {
        "VAULT999.write",
        "vault999.write",
        "vault.write(",
        "seal_to_vault(",
    }
)


@dataclass(frozen=True)
class ForgeSkillRequest:
    """Request to forge a generated capability."""

    intent: str
    domain: str
    seal_verdict_id: str | None
    capability_class: GeneratedCapabilityClass = GeneratedCapabilityClass.READ
    requested_tool_name: str | None = None
    generated_code: str | None = None
    input_schema: Mapping[str, Any] | None = None
    output_schema: Mapping[str, Any] | None = None
    execute_immediately: bool = False
    f13_ack: bool = False
    apex_field: ApexDecisionField | None = None


@dataclass(frozen=True)
class ForgeSkillAssessment:
    """Result of evaluating a forge_skill request before code registration."""

    verdict: ForgeSkillVerdict
    deny_codes: tuple[ForgeSkillDenyCode, ...] = ()
    tool_id: str | None = None
    schema_fingerprint: str | None = None
    code_fingerprint: str | None = None
    evidence: dict[str, object] = field(default_factory=dict)

    @property
    def admissible(self) -> bool:
        return self.verdict == ForgeSkillVerdict.ADMIT_DRAFT

    def to_dict(self) -> dict[str, object]:
        return {
            "verdict": self.verdict.value,
            "deny_codes": [code.value for code in self.deny_codes],
            "tool_id": self.tool_id,
            "schema_fingerprint": self.schema_fingerprint,
            "code_fingerprint": self.code_fingerprint,
            "evidence": self.evidence,
        }


def _sha256_json(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _sha256_text(text: str | None) -> str | None:
    if text is None:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _contains_any(text: str, patterns: frozenset[str]) -> list[str]:
    return sorted(pattern for pattern in patterns if pattern in text)


def _tool_id_for_request(request: ForgeSkillRequest) -> str:
    base = request.requested_tool_name or request.intent.strip().lower().replace(" ", "_")
    cleaned = "".join(ch for ch in base if ch.isalnum() or ch == "_").strip("_")
    return f"generated.{request.domain}.{cleaned or 'capability'}"


def assess_forge_skill_request(request: ForgeSkillRequest) -> ForgeSkillAssessment:
    """
    Evaluate whether a generated capability request can become a draft tool.

    This function intentionally does not generate, register, execute, or seal code.
    It is the admissibility contract used before those steps.
    """
    deny: list[ForgeSkillDenyCode] = []
    generated_code = request.generated_code or ""
    target_text = " ".join(
        part
        for part in (
            request.intent,
            request.domain,
            request.requested_tool_name or "",
            generated_code,
        )
        if part
    )

    if not request.intent.strip():
        deny.append(ForgeSkillDenyCode.INTENT_MISSING)
    if not request.domain.strip():
        deny.append(ForgeSkillDenyCode.DOMAIN_MISSING)
    if not request.seal_verdict_id:
        deny.append(ForgeSkillDenyCode.MISSING_SEAL_VERDICT)
    if not request.input_schema or not request.output_schema:
        deny.append(ForgeSkillDenyCode.SCHEMA_MISSING)

    self_hits = _contains_any(target_text, SELF_MODIFICATION_TARGETS)
    haram_hits = _contains_any(generated_code, HARAM_CODE_PATTERNS)
    registry_hits = _contains_any(generated_code, REGISTRY_BYPASS_PATTERNS)
    vault_hits = _contains_any(generated_code, VAULT_BYPASS_PATTERNS)

    if self_hits:
        deny.append(ForgeSkillDenyCode.SELF_MODIFICATION)
    if haram_hits:
        deny.append(ForgeSkillDenyCode.HARAM_PATTERN)
    if registry_hits:
        deny.append(ForgeSkillDenyCode.REGISTRY_BYPASS)
    if vault_hits and not request.seal_verdict_id:
        deny.append(ForgeSkillDenyCode.VAULT_BYPASS)
    elif vault_hits:
        # Generated tools should not write vault directly even with seal; forge_audit owns this.
        deny.append(ForgeSkillDenyCode.VAULT_BYPASS)

    if request.capability_class == GeneratedCapabilityClass.IRREVERSIBLE and not request.f13_ack:
        deny.append(ForgeSkillDenyCode.IRREVERSIBLE_REQUIRES_F13)

    apex_assessment = None
    if request.apex_field is not None:
        apex_assessment = assess_apex_decision_field(request.apex_field)
        if apex_assessment.verdict == ApexDecisionVerdict.VOID:
            deny.append(ForgeSkillDenyCode.APEX_DECISION_FIELD_VOID)
        elif apex_assessment.verdict == ApexDecisionVerdict.HOLD:
            deny.append(ForgeSkillDenyCode.APEX_DECISION_FIELD_HOLD)

    unique_deny = tuple(dict.fromkeys(deny))
    schema_fingerprint = (
        _sha256_json({"input_schema": request.input_schema, "output_schema": request.output_schema})
        if request.input_schema and request.output_schema
        else None
    )
    code_fingerprint = _sha256_text(request.generated_code)

    if unique_deny:
        hold_only_codes = {
            ForgeSkillDenyCode.IRREVERSIBLE_REQUIRES_F13,
            ForgeSkillDenyCode.APEX_DECISION_FIELD_HOLD,
        }
        if set(unique_deny).issubset(hold_only_codes):
            verdict = ForgeSkillVerdict.HOLD_888
        else:
            verdict = ForgeSkillVerdict.VOID
    else:
        verdict = ForgeSkillVerdict.ADMIT_DRAFT

    return ForgeSkillAssessment(
        verdict=verdict,
        deny_codes=unique_deny,
        tool_id=_tool_id_for_request(request) if verdict == ForgeSkillVerdict.ADMIT_DRAFT else None,
        schema_fingerprint=schema_fingerprint,
        code_fingerprint=code_fingerprint,
        evidence={
            "capability_class": request.capability_class.value,
            "execute_immediately": request.execute_immediately,
            "self_modification_hits": self_hits,
            "haram_hits": haram_hits,
            "registry_bypass_hits": registry_hits,
            "vault_bypass_hits": vault_hits,
            "requires_f13_ack": request.capability_class == GeneratedCapabilityClass.IRREVERSIBLE,
            "f13_ack": request.f13_ack,
            "apex_decision_field": apex_assessment.to_dict() if apex_assessment else None,
        },
    )
