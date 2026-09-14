"""
arifos/identity — Agent Identity Binding Module
══════════════════════════════════════════════════

Component #1 of Identity Binding + Consent Architecture.
Provides Ed25519 keypair generation, signing, verification,
and agent identity registry management.

Usage:
    from arifos.identity import AgentIdentity, IdentityRegistry

    # Generate new agent identity
    agent = AgentIdentity.create("opencode", bound_to="arif-fazil/F13")
    agent.save("/root/AAA/agents/opencode/identity.json")

    # Verify agent signature
    is_valid = agent.verify(message, signature)

    # Registry lookup
    registry = IdentityRegistry()
    registry.register(agent)
    pubkey = registry.lookup("opencode")

Forged: 2026-07-29 — DITEMPA BUKAN DIBERI
"""

from .agent_identity import AgentIdentity
from .identity_registry import IdentityRegistry
from .identity_resolver import (
    GuardResult,
    IdentityHold,
    Verdict,
    assert_clear,
    guard,
    identity_bound,
    load_registry,
    resolve,
)

__all__ = [
    "AgentIdentity",
    "IdentityRegistry",
    # Identity interceptor gate — SCAR-2026-09-15-001 (kata nama am vs khas)
    "GuardResult",
    "IdentityHold",
    "Verdict",
    "assert_clear",
    "guard",
    "identity_bound",
    "load_registry",
    "resolve",
]
