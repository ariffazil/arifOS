"""
Epistemic Response Injector — Inject _epistemic into every MCP response
═══════════════════════════════════════════════════════════════════════════════

Every MCP tool in every federation organ should call ``inject_epistemic()``
on its response dict before returning. This ensures the halal/haram boundary
is visible at the transport level.

Two injection modes:

1. **Tool-level** (preferred): Each tool function calls inject_epistemic()
   on its return dict with the correct epistemic classification.

2. **Middleware-level** (fallback): A response middleware can inject a
   default epistemic tag for tools that don't explicitly call it.

Usage::

    from arifosmcp.runtime.epistemic_injector import (
        inject_epistemic,
        EPISTEMIC_DETERMINISTIC,
        EPISTEMIC_AI_ADVISORY,
    )

    async def my_tool(...) -> dict:
        result = {"status": "OK", "data": ...}
        return inject_epistemic(
            result,
            EPISTEMIC_AI_ADVISORY,
            tagged_by="arifOS",
        )

DITEMPA BUKAN DIBERI — Every output carries its own epistemic label.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from arifosmcp.schemas.epistemic_tag import (
    EpistemicTag,
    EPISTEMIC_AI_ADVISORY,
    EPISTEMIC_DETERMINISTIC,
    EPISTEMIC_DOMAIN_COMPUTATION,
    EPISTEMIC_GOVERNANCE_TEMPLATE,
    EPISTEMIC_RETRIEVED,
    assert_tag_valid,
)


def inject_epistemic(
    response: dict[str, Any],
    tag: EpistemicTag,
    tagged_by: str = "arifOS",
    validate: bool = True,
) -> dict[str, Any]:
    """Inject _epistemic into a response dict.

    Args:
        response: The response dict from a tool function.
        tag: EpistemicTag classifying this output.
        tagged_by: Which organ/node injected this tag.
        validate: If True, raises ValueError on halal/haram violation.

    Returns:
        The response dict with _epistemic field added.
    """
    if validate:
        assert_tag_valid(tag)

    response["_epistemic"] = {
        "output_class": tag.output_class.value,
        "ai_involvement": tag.ai_involvement.value,
        "authority_claim": tag.authority_claim.value,
        "evidence_source": tag.evidence_source.value,
        "degraded_reason": tag.degraded_reason,
        "tagged_by": tagged_by,
        "tagged_at": datetime.now(UTC).isoformat(),
        "schema_version": tag.schema_version,
    }
    return response


def has_epistemic(response: dict[str, Any]) -> bool:
    """Check if a response dict already has _epistemic injected."""
    return "_epistemic" in response and isinstance(response["_epistemic"], dict)


def read_epistemic(response: dict[str, Any]) -> dict[str, str] | None:
    """Read the epistemic tag from a response dict. Returns None if missing."""
    epi = response.get("_epistemic")
    if isinstance(epi, dict):
        return epi
    return None


def is_ai_synthesised(response: dict[str, Any]) -> bool:
    """Quick check: is this response AI-synthesised?"""
    epi = read_epistemic(response)
    if epi is None:
        return False  # default: safe
    return epi.get("evidence_source") == "AI_SYNTHESIZED"


def is_ai_generated(response: dict[str, Any]) -> bool:
    """Quick check: was this response AI-generated?"""
    epi = read_epistemic(response)
    if epi is None:
        return False
    return epi.get("ai_involvement") in ("GENERATED", "ASSISTED")


def has_executive_authority(response: dict[str, Any]) -> bool:
    """Quick check: does this response claim executive authority?"""
    epi = read_epistemic(response)
    if epi is None:
        return False
    return epi.get("authority_claim") == "EXECUTIVE"


def epistemic_summary(response: dict[str, Any]) -> str:
    """Return a human-readable epistemic summary string."""
    epi = read_epistemic(response)
    if epi is None:
        return "NO_EPISTEMIC_TAG"
    return (
        f"{epi.get('output_class', '?')}/"
        f"{epi.get('ai_involvement', '?')}/"
        f"{epi.get('authority_claim', '?')}/"
        f"{epi.get('evidence_source', '?')}"
    )


def verify_vault_eligibility(response: dict[str, Any]) -> tuple[bool, str]:
    """Check if a response is eligible for vault sealing.

    Returns:
        (eligible: bool, reason: str)
    """
    epi = read_epistemic(response)
    if epi is None:
        # No epistemic tag = no vault entry (fail-safe)
        return False, "Missing _epistemic tag — cannot verify vault eligibility"

    if epi.get("evidence_source") == "AI_SYNTHESIZED":
        return (
            False,
            "HARAM: AI-synthesised evidence cannot enter vault. "
            "AI may generate explanation, not evidence.",
        )

    if epi.get("ai_involvement") == "GENERATED" and epi.get("authority_claim") == "EXECUTIVE":
        return (
            False,
            "HARAM: AI-generated output must not claim EXECUTIVE authority in vault. "
            "AI may generate interpretation, not authority.",
        )

    return True, "Eligible for vault"


def verify_route_eligibility(
    source_epistemic: dict[str, str],
    target_authority: str = "EXECUTIVE",
) -> tuple[bool, str]:
    """Check if an epistemic-tagged output can be routed to a target authority slot.

    Args:
        source_epistemic: The _epistemic dict from the source response.
        target_authority: The authority claim expected by the destination
                         (NONE, ADVISORY, or EXECUTIVE).

    Returns:
        (eligible: bool, reason: str)
    """
    if not source_epistemic:
        return False, "Missing source _epistemic — cannot verify route eligibility"

    source_authority = source_epistemic.get("authority_claim", "NONE")
    source_ai = source_epistemic.get("ai_involvement", "NONE")

    # AI_ADVISORY output cannot be routed to an EXECUTIVE action slot
    if target_authority == "EXECUTIVE":
        if source_ai in ("GENERATED", "ASSISTED"):
            return (
                False,
                f"HARAM: AI-{source_ai} output ({source_authority}) cannot be routed "
                f"to EXECUTIVE action slot. AI may recommend action, not self-approve action.",
            )
        if source_authority != "EXECUTIVE":
            return (
                False,
                f"Source authority '{source_authority}' is not EXECUTIVE. "
                "Cannot route non-executive output to executive slot.",
            )

    # AI_ADVISORY can route to ADVISORY or NONE
    return True, "Route eligible"


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL CLASSIFICATION REGISTRY
# Maps every known arifOS canonical tool to its epistemic default.
# Organs (GEOX, WEALTH, WELL, A-FORGE, AAA, APEX) should have their own maps.
# ═══════════════════════════════════════════════════════════════════════════════

# Tools where the output is DETERMINISTIC + NONE + EXECUTIVE + COMPUTED
# Haram for AI to fabricate. Must be cryptographic fact.
DETERMINISTIC_TOOLS: set[str] = {
    # Health probes
    "arif_ping",
    "arif_kernel_health",
    "arif_kernel_attest",
    "arif_kernel_status",
    "arif_measure",
    # Transport probes
    "arif_schema_echo",
    "arif_transport_echo",
    "arif_version_echo",
    "arif_initialize_probe",
    # Conformance
    "arif_conformance_report",
    # Session (auth core is deterministic)
    "arif_init",
    "arif_triage",
}

# Tools where the output is AI-generated advisory content
# Wajib AI-assisted. Must never claim EXECUTIVE.
AI_ADVISORY_TOOLS: set[str] = {
    "arif_think",
    "arif_critique",
    "arif_compose",
    "arif_fetch",
}

# Tools that mix AI advisory with deterministic governance
# May have AI-generated explanatory text alongside deterministic core.
GOVERNANCE_TEMPLATE_TOOLS: set[str] = {
    "arif_judge",
    "arif_seal",
    "arif_forge",
}

# Tools that route or bridge — output classification depends on the routed organ
# Default to GORVERNANCE_TEMPLATE / ADVISORY / COMPUTED
ROUTING_TOOLS: set[str] = {
    "arif_kernel_route",
    "arif_route",
    "arif_bridge_connect",
    "arif_gateway_connect",
}

# Domain intelligence tools — output_class depends on the specific tool
# Default to DOMAIN_COMPUTATION / NONE / ADVISORY / COMPUTED
DOMAIN_TOOLS: set[str] = {
    "arif_observe",
    "arif_memory_recall",
}

# Retrieval tools — output is from storage
RETRIEVAL_TOOLS: set[str] = {
    "arif_memory_recall",
}


def get_default_epistemic(tool_name: str) -> EpistemicTag | None:
    """Get the default epistemic tag for a known tool.

    Returns None if the tool is not in the registry.
    """
    if tool_name in DETERMINISTIC_TOOLS:
        return EPISTEMIC_DETERMINISTIC
    if tool_name in AI_ADVISORY_TOOLS:
        return EPISTEMIC_AI_ADVISORY
    if tool_name in GOVERNANCE_TEMPLATE_TOOLS:
        return EPISTEMIC_GOVERNANCE_TEMPLATE
    if tool_name in ROUTING_TOOLS:
        return EPISTEMIC_GOVERNANCE_TEMPLATE
    if tool_name in DOMAIN_TOOLS:
        return EPISTEMIC_DOMAIN_COMPUTATION
    if tool_name in RETRIEVAL_TOOLS:
        return EPISTEMIC_RETRIEVED
    return None


def inject_epistemic_for_tool(
    response: dict[str, Any],
    tool_name: str,
    tagged_by: str = "arifOS",
) -> dict[str, Any]:
    """Inject the default epistemic tag for a known tool by its name.

    If the tool is not in the registry, defaults to DETERMINISTIC (safe fallback).
    """
    tag = get_default_epistemic(tool_name)
    if tag is None:
        # Unknown tool — safe default
        tag = EPISTEMIC_DETERMINISTIC
    return inject_epistemic(response, tag, tagged_by=tagged_by)
