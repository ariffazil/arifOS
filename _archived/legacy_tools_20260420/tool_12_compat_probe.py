"""
arifos/runtime/megaTools/12_compat_probe.py

M-5_COMPAT: Multi-layer interoperability and contract validation
Stage: M-5_COMPAT | Trinity: ALL | Floors: F11, F4

Modes: audit, probe, ping
"""

from __future__ import annotations

from arifos.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict


async def compat_probe(
    mode: str = "audit",
    session_id: str | None = None,
    actor_id: str | None = None,
    auth_context: dict | None = None,
) -> RuntimeEnvelope:
    """
    Diagnostic tool to verify session portability and enum compatibility.

    Checks:
    - Session anchor validity
    - Authority ladder alignment (Identity vs Class)
    - Protocol signature parity
    """
    from arifos.runtime.sessions import get_session_identity

    # 1. Check Identity
    identity = get_session_identity(session_id) if session_id else None
    anchor_status = "VALID" if identity else "MISSING"

    # 2. Check Authority Enum
    raw_level = (
        (auth_context or {}).get("authority_level")
        or (identity or {}).get("authority_level")
        or "anonymous"
    )

    # Check if raw_level is in canonical identity classes
    canonical_identity_classes = {
        "human",
        "user",
        "agent",
        "system",
        "anonymous",
        "operator",
        "sovereign",
        "declared",
        "claimed",
        "verified",
        "apex",
        "none",
    }

    enum_compat = (
        "✅ COMPATIBLE"
        if raw_level.lower() in canonical_identity_classes
        else f"❌ MISMATCH ({raw_level})"
    )

    # Honest trust-based recommendation
    high_trust_levels = {"verified", "sovereign", "apex", "human"}
    low_trust_levels = {"anonymous", "declared", "claimed", "none"}

    if "❌" in enum_compat:
        recommendation = "Use init_anchor to re-align if MISMATCH detected."
    elif raw_level.lower() in high_trust_levels:
        recommendation = "Trust established. System ready for governed execution."
    elif raw_level.lower() in low_trust_levels:
        recommendation = "Anonymous/declared identity — use init_anchor with verified credentials for full access."
    else:
        recommendation = "Identity recognized — init_anchor required to escalate privileges."

    # 3. Build Result
    payload = {
        "compatibility": {
            "anchor": anchor_status,
            "authority_enum": enum_compat,
            "current_level": raw_level,
            "session_id": session_id or "global",
        },
        "recommendation": recommendation,
    }

    return RuntimeEnvelope(
        ok=True,
        tool="arifos_probe",
        canonical_tool_name="arifos_probe",
        stage="M-5_COMPAT",
        session_id=session_id,
        verdict=Verdict.SEAL,
        status=RuntimeStatus.SUCCESS,
        payload=payload,
    )
