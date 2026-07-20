"""
actor_verification_matrix.py — Federation actor registry & authority bands.

G14 FIX (2026-07-04): The arifOS kernel previously did not register internal
agents separately from external instruments. Every route returned
`actor_verified=false` and `verdict=SYUBHAH` regardless of caller, which
degraded the identity contract for trusted internal actors.

This module defines the canonical actor registry. Each actor entry binds:
  - actor_id
  - role
  - authority band (OBSERVE | FORGE | SOVEREIGN | JUDGE)
  - allowed tools (regex / prefix match)
  - forbidden tools
  - lease requirement
  - session requirement
  - receipt requirement

The kernel middleware consults this matrix during FederationEnvelope validation.
External instruments (ChatGPT, OpenAI) and internal agents (Kimi Forge,
OpenCode AGY) are distinguished, so internal agents get their correct
authority band instead of being degraded to OBSERVE_ONLY.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ActorSpec:
    """Canonical spec for a federation actor."""

    actor_id: str
    role: str
    authority_band: str  # OBSERVE | FORGE | SOVEREIGN | JUDGE | VERDICT
    allowed_tools: tuple[str, ...]
    forbidden_tools: tuple[str, ...] = ()
    lease_required: bool = True
    session_required: bool = True
    receipt_required: bool = True
    description: str = ""

    def permits(self, tool_name: str) -> bool:
        """Return True iff `tool_name` is in allowed_tools and not in forbidden_tools."""
        if any(self._match(tool_name, f) for f in self.forbidden_tools):
            return False
        if not self.allowed_tools:
            return True  # empty allowlist = permissive (used for SOVEREIGN)
        return any(self._match(tool_name, a) for a in self.allowed_tools)

    @staticmethod
    def _match(name: str, pattern: str) -> bool:
        # Treat as regex; * becomes .*, ? becomes .
        if "*" in pattern or "?" in pattern:
            return bool(re.fullmatch(pattern.replace("*", ".*").replace("?", "."), name))
        return name == pattern or name.startswith(pattern)


# ── Canonical actor registry (ratified 2026-07-04, G14 FIX) ──────────────────

# ── Denied identities (BREAK-004 fix 2026-07-13) ─────────────────────────────
# These are relay placeholders that the kernel must NEVER accept as a real
# actor. Lookup returns None for these; the existing OBSERVE-only fallback
# rejects mutate-class tools. Kept as a named set so audit logs can distinguish
# "unknown" from "explicitly denied".
DENIED_IDENTITIES: frozenset[str] = frozenset(
    {
        "openclaw-anon",
        "anonymous",
        "unknown",
        "null",
        "",
    }
)

ACTOR_REGISTRY: dict[str, ActorSpec] = {
    # ── External instruments (degrade to OBSERVE_ONLY by design) ─────────
    "chatgpt-adapter": ActorSpec(
        actor_id="chatgpt-adapter",
        role="external_instrument",
        authority_band="OBSERVE",
        allowed_tools=("arif_*",),
        forbidden_tools=(
            "arif_seal",
            "arif_judge",
            "arif_forge",
            "arif_lease_issue",
            "arif_act",
        ),
        lease_required=False,
        session_required=True,
        receipt_required=False,
        description="ChatGPT / OpenAI host runtime — observe-only via host membrane",
    ),
    "openai-bridge": ActorSpec(
        actor_id="openai-bridge",
        role="external_instrument",
        authority_band="OBSERVE",
        allowed_tools=("arif_*",),
        forbidden_tools=(
            "arif_seal",
            "arif_judge",
            "arif_forge",
            "arif_lease_issue",
        ),
        lease_required=False,
        session_required=True,
        receipt_required=False,
        description="OpenAI bridge — same as chatgpt-adapter for back-compat",
    ),
    # ── Internal federation agents (governed, full authority within scope) ──
    "kimi-code-forge": ActorSpec(
        actor_id="kimi-code-forge",
        role="governed_forge_worker",
        authority_band="FORGE",
        allowed_tools=(
            "arif_*",
            "forge_*",
            "well_*",
            "wealth_*",
            "geox_*",
        ),
        forbidden_tools=("arif_seal",),  # sovereign-only
        lease_required=True,
        session_required=True,
        receipt_required=True,
        description="Kimi Code CLI — FI-008 warga AAA, governed forge worker",
    ),
    "opencode-333": ActorSpec(
        actor_id="opencode-333",
        role="governed_forge_worker",
        authority_band="FORGE",
        allowed_tools=(
            "arif_*",
            "forge_*",
            "well_*",
            "wealth_*",
            "geox_*",
        ),
        forbidden_tools=("arif_seal",),
        lease_required=True,
        session_required=True,
        receipt_required=True,
        description="OpenCode AGY — 333-AGI warga, governed forge worker",
    ),
    "opencode-555": ActorSpec(
        actor_id="opencode-555",
        role="governed_asi",
        authority_band="FORGE",
        allowed_tools=(
            "arif_*",
            "forge_*",
            "well_*",
            "wealth_*",
            "geox_*",
        ),
        forbidden_tools=("arif_seal",),
        lease_required=True,
        session_required=True,
        receipt_required=True,
        description="OpenCode ASI — 555-ASI warga, governed ASI",
    ),
    # ── Verdict authority (888 / APEX) ─────────────────────────────────────
    "888-apex": ActorSpec(
        actor_id="888-apex",
        role="verdict_authority",
        authority_band="JUDGE",
        allowed_tools=("arif_*", "forge_*"),
        forbidden_tools=(),
        lease_required=False,
        session_required=True,
        receipt_required=True,
        description="888 / APEX — verdict authority, can seal and judge",
    ),
    "apex-jury": ActorSpec(
        actor_id="apex-jury",
        role="verdict_authority",
        authority_band="JUDGE",
        allowed_tools=("arif_*", "forge_*"),
        forbidden_tools=(),
        lease_required=False,
        session_required=True,
        receipt_required=True,
        description="APEX jury — verdict authority (alias of 888-apex)",
    ),
    # ── Sovereign (Arif / F13) ─────────────────────────────────────────────
    "arifbfazil": ActorSpec(
        actor_id="arifbfazil",
        role="sovereign",
        authority_band="SOVEREIGN",
        allowed_tools=(),  # empty = permissive; sovereign can call anything
        forbidden_tools=(),
        lease_required=False,
        session_required=False,
        receipt_required=True,
        description="Arif — F13 SOVEREIGN, owner of the federation",
    ),
    "f13": ActorSpec(
        actor_id="f13",
        role="sovereign",
        authority_band="SOVEREIGN",
        allowed_tools=(),
        forbidden_tools=(),
        lease_required=False,
        session_required=False,
        receipt_required=True,
        description="F13 SOVEREIGN alias",
    ),
    "Muhammad Arif bin Fazil": ActorSpec(
        actor_id="Muhammad Arif bin Fazil",
        role="sovereign",
        authority_band="SOVEREIGN",
        allowed_tools=(),
        forbidden_tools=(),
        lease_required=False,
        session_required=False,
        receipt_required=True,
        description="Sovereign full name",
    ),
    # ── Local relays / bridges ─────────────────────────────────────────────
    "Hermes": ActorSpec(
        actor_id="Hermes",
        role="local_relay",
        authority_band="FORGE",
        allowed_tools=("arif_*", "forge_*"),
        forbidden_tools=("arif_seal",),
        lease_required=False,  # auto-promoted via _try_promote_local_service
        session_required=True,
        receipt_required=True,
        description="Hermes local bridge — auto-promoted via localhost trust",
    ),
    # ── BREAK-004 fix (2026-07-13): openclaw-anon REMOVED from registry. ─────
    # It was registered as a legitimate "degraded to OBSERVE" actor, which let
    # the kernel mint receipts under an anonymous identity. That bypassed F2
    # TRUTH (no actor_signature, no chain to a real human) — see receipts_v2
    # audit: 8,670 anonymous receipts on disk. The relay must be RESOLVED to a
    # real actor before any receipt is minted. See vault_receipt.resolve_receipt_identity.
}


def lookup_actor(actor_id: str | None) -> ActorSpec | None:
    """Look up an actor by ID. Returns None if unknown or DENIED."""
    if not actor_id:
        return None
    if actor_id in DENIED_IDENTITIES:
        return None  # BREAK-004: relay placeholders are NOT valid identities.
    return ACTOR_REGISTRY.get(actor_id)


def is_denied_identity(actor_id: str | None) -> bool:
    """Return True iff actor_id is an explicitly DENIED relay placeholder."""
    return bool(actor_id) and actor_id in DENIED_IDENTITIES


def is_known_actor(actor_id: str | None) -> bool:
    return lookup_actor(actor_id) is not None


def authority_band_for(actor_id: str | None) -> str:
    """Return the authority band for an actor_id, or 'OBSERVE' if unknown."""
    spec = lookup_actor(actor_id)
    return spec.authority_band if spec else "OBSERVE"


def actor_allows(actor_id: str | None, tool_name: str) -> bool:
    """Return True iff the actor is permitted to call this tool."""
    spec = lookup_actor(actor_id)
    if spec is None:
        # Unknown actor → OBSERVE_ONLY default; reject any mutate-class tool
        if tool_name.startswith(
            ("arif_seal", "arif_judge", "arif_forge", "arif_act", "forge_execute", "forge_abort")
        ):
            return False
        return True
    return spec.permits(tool_name)


def actor_summary(actor_id: str) -> dict[str, Any]:
    """Return a dict summary of an actor's permissions."""
    if is_denied_identity(actor_id):
        # BREAK-004: relay placeholders are explicitly denied — receipts
        # minted under these identities are F2-void and the kernel should
        # reject at ingress.
        return {
            "actor_id": actor_id,
            "known": False,
            "denied": True,
            "authority_band": "DENIED",
            "note": (
                "Relay placeholder — explicitly denied (BREAK-004 fix 2026-07-13). "
                "Resolver required before any receipt can be minted."
            ),
        }
    spec = lookup_actor(actor_id)
    if spec is None:
        return {
            "actor_id": actor_id,
            "known": False,
            "authority_band": "OBSERVE",
            "note": "Unknown actor — degraded to OBSERVE_ONLY",
        }
    return {
        "actor_id": spec.actor_id,
        "role": spec.role,
        "authority_band": spec.authority_band,
        "lease_required": spec.lease_required,
        "session_required": spec.session_required,
        "receipt_required": spec.receipt_required,
        "description": spec.description,
    }


__all__ = [
    "ActorSpec",
    "ACTOR_REGISTRY",
    "DENIED_IDENTITIES",
    "lookup_actor",
    "is_known_actor",
    "is_denied_identity",
    "authority_band_for",
    "actor_allows",
    "actor_summary",
]
