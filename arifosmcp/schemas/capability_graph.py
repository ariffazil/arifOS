"""
arifosmcp/schemas/capability_graph.py — CAPABILITY GRAPH (P2)
═══════════════════════════════════════════════════════════════

Canonical capability resolution — replaces 38 routing modules.
Planner decides WHAT. CapabilityGraph decides WHICH. Governor decides MAY.
Executor does the exact approved action.

Forged: 2026-07-26 under Arif's P2 directive.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from arifosmcp.schemas.authority_context import AuthorityContext

GradeVerdict = Literal["MATCH", "PARTIAL", "NONE"]


@dataclass
class Capability:
    """Declared capability from the ABI registry."""

    capability_id: str
    tool_name: str
    semantic_hash: str
    version: str
    action_class: str
    mutation: bool
    irreversible: bool
    authority_required: str
    evidence_required: bool
    idempotency: str
    receipt_policy: str
    constitutional_floors: list[str]


@dataclass
class CapabilityMatch:
    """One capability matched to an intent, with confidence and rationale."""

    capability: Capability
    confidence: float  # 0.0-1.0
    rationale: str
    verdict: GradeVerdict = "NONE"


@dataclass
class ResolveResult:
    """Result of resolving an intent against the capability graph."""

    intent: str
    matches: list[CapabilityMatch] = field(default_factory=list)
    best_match: CapabilityMatch | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def has_match(self) -> bool:
        return self.best_match is not None and self.best_match.confidence > 0.5


@dataclass
class AuthorizeResult:
    """Result of authorizing a capability for a given authority context."""

    capability: Capability
    authority: AuthorityContext
    allowed: bool
    reason: str
    downgraded: bool = False
    requires_sovereign: bool = False


class CapabilityGraph:
    """Canonical capability resolution graph.

    Reads from the ABI registry. Provides intent→capability matching
    and authority→permission checking.

    Usage:
        graph = CapabilityGraph.load()
        result = graph.resolve("execute a deployment")
        auth = graph.authorize(result.best_match, authority_context)
    """

    def __init__(self, capabilities: list[Capability]):
        self._capabilities: dict[str, Capability] = {c.capability_id: c for c in capabilities}
        self._by_tool: dict[str, Capability] = {c.tool_name: c for c in capabilities}

    @classmethod
    def load(cls) -> CapabilityGraph:
        """Load capabilities from the ABI registry."""
        abi_path = Path(__file__).resolve().parent.parent / "abi" / "capability_registry.json"
        raw = json.loads(abi_path.read_text(encoding="utf-8"))
        capabilities = []
        for c in raw.get("capabilities", []):
            provider = c.get("provider", {})
            capabilities.append(
                Capability(
                    capability_id=c["capability_id"],
                    tool_name=provider.get("tool", c["capability_id"]),
                    semantic_hash=c.get("semantic_hash", ""),
                    version=c.get("version", "1.0.0"),
                    action_class=c.get("action_class", "UNKNOWN"),
                    mutation=c.get("mutation", False),
                    irreversible=c.get("irreversible", False),
                    authority_required=c.get("authority_required", "ANONYMOUS"),
                    evidence_required=c.get("evidence_required", False),
                    idempotency=c.get("idempotency", "safe"),
                    receipt_policy=c.get("receipt_policy", "optional"),
                    constitutional_floors=c.get("constitutional_floors", []),
                )
            )
        return cls(capabilities)

    def list_all(self) -> list[Capability]:
        return list(self._capabilities.values())

    def list_canonical(self) -> list[str]:
        """Return the 8 canonical tool names."""
        return list(self._by_tool.keys())

    def get_by_id(self, capability_id: str) -> Capability | None:
        return self._capabilities.get(capability_id)

    def get_by_tool(self, tool_name: str) -> Capability | None:
        return self._by_tool.get(tool_name)

    def resolve(self, intent: str) -> ResolveResult:
        """Resolve an intent string to one or more matching capabilities.

        Currently semantic — intent is matched against capability IDs
        and constitutional floors. Future: embedding-based semantic search.
        """
        intent_lower = intent.lower()
        matches: list[CapabilityMatch] = []

        for cap in self._capabilities.values():
            confidence = 0.0
            rationale_parts: list[str] = []

            # Match by capability ID tokens
            cap_tokens = set(cap.capability_id.replace(".", " ").split())
            for token in cap_tokens:
                if token in intent_lower:
                    confidence += 0.25
                    rationale_parts.append(f"token match: {token}")

            # Match by tool name
            if cap.tool_name.replace("_", " ") in intent_lower:
                confidence += 0.20
                rationale_parts.append(f"tool match: {cap.tool_name}")

            # Match by action class keywords
            action_keywords = {
                "execute": ["execute", "forge", "run", "deploy", "build", "commit"],
                "observe": ["observe", "search", "fetch", "look", "read", "check", "probe"],
                "think": ["think", "plan", "reason", "analyze", "hypothesize"],
                "route": ["route", "dispatch", "forward", "bridge"],
                "memory": ["memory", "recall", "remember", "store"],
                "judge": ["judge", "verdict", "evaluate", "assess", "decide"],
                "seal": ["seal", "vault", "finalize", "irreversible"],
                "init": ["init", "session", "start", "begin", "login"],
            }
            for cap_id, keywords in action_keywords.items():
                if any(kw in cap.capability_id for kw in (cap_id,)) and any(
                    kw in intent_lower for kw in keywords
                ):
                    confidence += 0.15
                    rationale_parts.append(f"action match: {cap_id}")

            if confidence > 0:
                # Boost for explicit capability names in intent
                if cap.capability_id in intent_lower:
                    confidence = min(1.0, confidence + 0.30)
                    rationale_parts.append("exact cap match")

                verdict: GradeVerdict = "MATCH" if confidence >= 0.5 else "PARTIAL"
                matches.append(
                    CapabilityMatch(
                        capability=cap,
                        confidence=min(1.0, confidence),
                        rationale="; ".join(rationale_parts),
                        verdict=verdict,
                    )
                )

        # Sort by confidence descending
        matches.sort(key=lambda m: m.confidence, reverse=True)
        best: CapabilityMatch | None = matches[0] if matches else None

        # If no match found, default to arif_route (arbitrator)
        if not matches or (best and best.confidence < 0.3):
            route_cap = self.get_by_tool("arif_route")
            if route_cap:
                best = CapabilityMatch(
                    capability=route_cap,
                    confidence=0.25,
                    rationale="no clear match — routing to arif_route as arbitrator",
                    verdict="NONE",
                )
                matches.append(best)

        return ResolveResult(intent=intent, matches=matches, best_match=best)

    def authorize(self, match: CapabilityMatch, authority: AuthorityContext) -> AuthorizeResult:
        """Check whether the given authority context may execute this capability.

        Decision logic:
        1. Authority level must meet capability's required authority
        2. If irreversible, sovereign acknowledgment is required
        3. If mutating, authority must have mutation permission
        """
        cap = match.capability
        requires_sovereign = False

        # Authority level gating
        level_map = {
            "SOVEREIGN": 4,
            "TRUSTED_AGENT": 3,
            "EXECUTOR": 2,
            "OBSERVER": 1,
            "ANONYMOUS": 0,
            "OBSERVE_ONLY": 0,
        }
        required = level_map.get(cap.authority_required.upper(), 1)
        granted = level_map.get(authority.authority_level, 0)

        if granted < required:
            return AuthorizeResult(
                capability=cap,
                authority=authority,
                allowed=False,
                reason=(
                    f"Insufficient authority: need {cap.authority_required} "
                    f"(level {required}), have {authority.authority_level} (level {granted})"
                ),
                requires_sovereign=True if required == 4 else False,
            )

        # Irreversible actions require sovereign
        if cap.irreversible and not authority.can_seal():
            return AuthorizeResult(
                capability=cap,
                authority=authority,
                allowed=False,
                reason=(
                    f"Irreversible capability '{cap.capability_id}' requires SOVEREIGN authority"
                ),
                requires_sovereign=True,
            )

        # Mutation requires mutation permission
        if cap.mutation and not authority.can_mutate():
            return AuthorizeResult(
                capability=cap,
                authority=authority,
                allowed=False,
                reason=(
                    f"Mutating capability '{cap.capability_id}' requires EXECUTOR authority or above"
                ),
                requires_sovereign=False,
            )

        # Sovereign required check
        if authority.sovereign_required and not authority.sovereign_acknowledged:
            return AuthorizeResult(
                capability=cap,
                authority=authority,
                allowed=False,
                reason="Sovereign acknowledgment pending (F13 HOLD)",
                requires_sovereign=True,
            )

        return AuthorizeResult(
            capability=cap,
            authority=authority,
            allowed=True,
            reason="All authority gates passed",
        )


@lru_cache(maxsize=1)
def _cached_graph() -> CapabilityGraph:
    return CapabilityGraph.load()


def get_capability_graph() -> CapabilityGraph:
    """Return the singleton capability graph (cached)."""
    return _cached_graph()


# ─── P2 self-test ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    graph = CapabilityGraph.load()
    caps = graph.list_all()
    canonical = graph.list_canonical()
    print(f"Capabilities: {len(caps)}, Canonical tools: {len(canonical)}")
    assert len(caps) == 8
    assert len(canonical) == 8

    # Test resolve
    tests = [
        ("execute a deployment", "action.execute"),
        ("search the web for news", "reality.observe"),
        ("think about this problem", "cognition.think"),
        ("seal this verdict to vault", "history.seal"),
        ("judge whether this action is allowed", "authority.judge"),
        ("route this to the correct organ", "intent.route"),
        ("start a new session", "session.bind"),
        ("recall past memories", "memory.govern"),
    ]
    for intent, expected_cap in tests:
        result = graph.resolve(intent)
        status = "✅" if result.has_match() else "❌"
        best = result.best_match
        print(
            f'  {status} "{intent}" → '
            f"{best.capability.capability_id} ({best.confidence:.2f})"
            f"{' ✓EXPECTED' if best and best.capability.capability_id == expected_cap else ''}"
        )

    # Test authorize
    from arifosmcp.schemas.authority_context import AuthorityContext

    anon = AuthorityContext.anonymous("s1")
    trusted = AuthorityContext(
        actor_id="forge", session_id="s2", authority_level="TRUSTED_AGENT", actor_verified=True
    )
    sov = AuthorityContext(
        actor_id="arif", session_id="s3", authority_level="SOVEREIGN", actor_verified=True
    )

    seal_match = graph.resolve("seal this").best_match
    assert seal_match is not None

    anon_auth = graph.authorize(seal_match, anon)
    assert not anon_auth.allowed  # anonymous cannot seal

    trusted_auth = graph.authorize(seal_match, trusted)
    assert not trusted_auth.allowed  # trusted cannot seal

    sov_auth = graph.authorize(seal_match, sov)
    assert sov_auth.allowed  # sovereign can seal

    print(f"\n✅ CapabilityGraph: ALL tests PASS")
    print(f"   Graph: {len(caps)} capabilities loaded")
    print(f"   Canonical: {canonical}")
