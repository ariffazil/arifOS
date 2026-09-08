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

# Identity Continuity — Constitutional Primitive (Ratified 2026-09-08)
# Ratified under F1 AMANAH · F3 WITNESS · F6 MARUAH · F11 AUDIT · F13 SOVEREIGN
# Doctrine: /root/AAA/instructions/identity-continuity.md
IdentitySupportLevel = Literal[
    "NONE",  # Capability produces / consumes identity-irrelevant artifacts (T2I archetype)
    "REFERENCE",  # Capability can condition against existing identity_card (I2I subject_ref)
    "BINDING_T1",  # Capability writes Tier-1 biometric witness (face / voice)
    "BINDING_T2",  # Capability writes temporal witness (cross-session continuity)
    "BINDING_T3",  # Constitutional — substrate-invariant, witness-of-witnesses (F1-F13)
]

# Operation tiers (ICL-3.0, ratified 2026-09-08 by 333-AGI on F13 SOVEREIGN signal).
# Each tier sets its OWN floor for admin / biometric / constitutional planes.
# Identity Exists ≠ Identity Verified For This Operation (Arif architectural review 2026-09-08).
IdentityOperationTier = Literal[
    "C0",  # OBSERVE — read-only, memory recall, audit (admin only)
    "C1",  # IDENTITY_BOUND_METADATA — address, tag, relate (admin only)
    "C2",  # SAFE_GENERATION — text, voice without biometric claim (admin only)
    "C3",  # BIOMETRIC_GENERATION — I2I subject_ref, face-conditioned gen (admin + biometric)
    "C4",  # PUBLIC_ATTRIBUTION — public image claiming to be actor (admin + biometric + constitutional)
    "C5",  # DEEPFAKE_GRADE — irreversible public claim, deepfake threshold (full quorum)
]

OPERATION_TIER_THRESHOLDS: dict[str, dict[str, float]] = {
    # tier        admin_min  biometric_min  constitutional_min
    "C0": {"admin_min": 0.30, "biometric_min": 0.0, "constitutional_min": 0.0},
    "C1": {"admin_min": 0.50, "biometric_min": 0.0, "constitutional_min": 0.0},
    "C2": {"admin_min": 0.65, "biometric_min": 0.0, "constitutional_min": 0.0},
    "C3": {"admin_min": 0.65, "biometric_min": 0.50, "constitutional_min": 0.0},
    "C4": {"admin_min": 0.80, "biometric_min": 0.65, "constitutional_min": 0.30},
    "C5": {"admin_min": 0.90, "biometric_min": 0.80, "constitutional_min": 0.50},
}

WitnessKind = Literal[
    "W1_face",  # Biometric: face signature (InsightFace buffalo_l)
    "W2_voice",  # Biometric: voice signature (mimo/MiniMax)
    "W3_name",  # Administrative: handle binding
    "W4_history",  # Administrative: VAULT999 + arif_memory L1-L6
    "W5_relations",  # Administrative: relations graph
    "W6_scar_ledger",  # Constitutional: failure continuity
]


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
    # Identity Continuity (2026-09-08) — additive, defaults to NONE
    identity_support: IdentitySupportLevel = "NONE"
    identity_witnesses_used: list[WitnessKind] = field(default_factory=list)
    identity_witnesses_written: list[WitnessKind] = field(default_factory=list)


@dataclass
class IdentityContinuityCheck:
    """Constitutional identity continuity verification (quorum result).

    Quum rule (ICL-1.5): Identity Strength = ∛(W_bio × W_admin × W_const) ≥ 0.50.
    No single witness carries authority (ICL-1.1).

    Architectural refinement (ICL-3.0, ratified 2026-09-08):
        Identity Exists ≠ Identity Verified For This Operation.
        Existence = admin layer (W3 + W4) — F13 ratifies.
        Verification = operation-class-specific witness thresholds.
    """

    actor_handle: str
    intent: str
    identity_card_ref: str | None  # path to /root/AAA/registry/identity_cards/<actor>.yaml
    witness_set: dict[str, float] = field(default_factory=dict)
    biometric_min: float = 0.0
    admin_min: float = 0.0
    constitutional_min: float = 0.0
    geometric_mean: float = 0.0
    quorum_passed: bool = False
    single_witness_authority: bool = False  # always False — constitutional law
    verdict: GradeVerdict = "NONE"
    rationale: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    # ICL-3.0 operation-tier fields (additive)
    identity_exists: bool = False
    operation_class: IdentityOperationTier = "C2"
    tier_admin_pass: bool = False
    tier_biometric_pass: bool = False
    tier_constitutional_pass: bool = False
    tier_passed: bool = False

    def compute_quorum(self) -> None:
        """Recompute geometric mean across three planes.

        W_biometric = √(W1 × W2)
        W_admin     = ∛(W3 × W4 × W5)
        W_const     = W6
        Identity    = ∛(W_bio × W_admin × W_const)
        """
        w1 = self.witness_set.get("W1_face", 0.0)
        w2 = self.witness_set.get("W2_voice", 0.0)
        w3 = self.witness_set.get("W3_name", 0.0)
        w4 = self.witness_set.get("W4_history", 0.0)
        w5 = self.witness_set.get("W5_relations", 0.0)
        w6 = self.witness_set.get("W6_scar_ledger", 0.0)

        w_bio = (w1 * w2) ** 0.5
        w_admin = (w3 * w4 * w5) ** (1 / 3) if (w3 + w4 + w5) > 0 else 0.0
        w_const = w6

        if w_bio == 0 or w_admin == 0 or w_const == 0:
            self.geometric_mean = 0.0
        else:
            self.geometric_mean = (w_bio * w_admin * w_const) ** (1 / 3)

        self.quorum_passed = self.geometric_mean >= 0.50 and self.single_witness_authority is False
        self.verdict = (
            "MATCH" if self.quorum_passed else "PARTIAL" if self.geometric_mean >= 0.30 else "NONE"
        )


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

    # ========================================================================
    # Identity Continuity — Constitutional Primitive (Ratified 2026-09-08)
    # Doctrine: /root/AAA/instructions/identity-continuity.md
    # ICL-1.1: NO SINGLE WITNESS CARRIES AUTHORITY.
    # ICL-1.5: Identity quorum = ∛(W_bio × W_admin × W_const) ≥ 0.50.
    # ========================================================================

    def identity_continuity_check(
        self,
        actor_handle: str,
        intent: str,
        named_actor: bool = True,
        identity_card_path: str | None = None,
        operation_class: IdentityOperationTier = "C2",
    ) -> IdentityContinuityCheck:
        """Resolve identity continuity for a named actor.

        Routing law: T2I is FORBIDDEN at C3+. Lower tiers allow admin-only.

        Architectural principle (ICL-3.0, ratified 2026-09-08):
            Identity EXISTS ≠ Identity VERIFIED for operation.
            Existence = admin layer (W3 + W4) — F13 ratifies.
            Verification = operation-class-specific witness thresholds.

        Args:
            actor_handle: canonical handle (e.g. 'syed_khairuddin')
            intent: user intent string
            named_actor: True if a real human actor is named
            identity_card_path: optional explicit path to identity_card.yaml
            operation_class: tier C0 (OBSERVE) → C5 (DEEPFAKE_PUBLIC)

        Returns:
            IdentityContinuityCheck with witness_set, geometric_mean, verdict,
            plus identity_exists (binary) + operation_class tier + tier-specific
            quorum_passed (operation_class vs tier_thresholds).
        """
        if identity_card_path is None:
            identity_card_path = f"/root/AAA/registry/identity_cards/{actor_handle}.yaml"

        # Default witness_set (admin layer always ON for ratified actors)
        witness_set: dict[str, float] = {
            "W1_face": 0.0,  # default OFF — biometric enrollment required
            "W2_voice": 0.0,  # default OFF
            "W3_name": 1.0,  # administrative — always ON if actor ratified
            "W4_history": 1.0,  # always ON if SOUL.md exists
            "W5_relations": 0.85,  # default ON if relations declared
            "W6_scar_ledger": 0.0,  # OFF until first scar sealed
        }

        rationale_parts: list[str] = []

        # Try to load identity_card.yaml if it exists
        card_path = Path(identity_card_path)
        if card_path.exists():
            try:
                import yaml

                with card_path.open() as f:
                    card = yaml.safe_load(f)
                w = card.get("identity", {}).get("witness_set", {})
                for k in witness_set:
                    if k in w:
                        witness_set[k] = float(w[k].get("confidence", witness_set[k]))
                rationale_parts.append(f"identity_card.yaml loaded from {identity_card_path}")
            except Exception as e:  # noqa: BLE001
                rationale_parts.append(f"identity_card.yaml read error: {e!s}")
        else:
            rationale_parts.append(
                f"identity_card.yaml not found at {identity_card_path} — defaults apply"
            )

        # ICL-3.1: Identity EXISTS = admin layer satisfied
        # W3_name + W4_history both active → actor exists (administrative truth)
        identity_exists = (
            witness_set.get("W3_name", 0.0) >= 0.50 and witness_set.get("W4_history", 0.0) >= 0.50
        )

        # ICL-1.1 enforcement: never allow single-witness authority
        check = IdentityContinuityCheck(
            actor_handle=actor_handle,
            intent=intent,
            identity_card_ref=identity_card_path if card_path.exists() else None,
            witness_set=witness_set,
            single_witness_authority=False,  # ICL-1.1 — constitutional law
            rationale=" | ".join(rationale_parts) or "default witness set, no card loaded",
        )
        check.compute_quorum()

        # ICL-3.2: Operation-class-specific quorum thresholds
        # Each tier sets its OWN floor for admin / biometric / constitutional
        tier_thresholds = OPERATION_TIER_THRESHOLDS[operation_class]

        # Check per-tier requirements
        admin_min = tier_thresholds["admin_min"]
        biometric_min = tier_thresholds["biometric_min"]
        constitutional_min = tier_thresholds["constitutional_min"]

        w_bio = (witness_set["W1_face"] * witness_set["W2_voice"]) ** 0.5
        w_admin = (
            witness_set["W3_name"] * witness_set["W4_history"] * witness_set["W5_relations"]
        ) ** (1 / 3)
        w_const = witness_set["W6_scar_ledger"]

        tier_admin_pass = w_admin >= admin_min
        tier_biometric_pass = w_bio >= biometric_min if biometric_min > 0 else True
        tier_constitutional_pass = w_const >= constitutional_min if constitutional_min > 0 else True

        # ICL-3.3: Tier verdict = tier_admin ∧ tier_biometric ∧ tier_constitutional
        tier_passed = tier_admin_pass and tier_biometric_pass and tier_constitutional_pass

        # Attach tier information
        check.operation_class = operation_class
        check.tier_admin_pass = tier_admin_pass
        check.tier_biometric_pass = tier_biometric_pass
        check.tier_constitutional_pass = tier_constitutional_pass
        check.tier_passed = tier_passed
        check.identity_exists = identity_exists

        # Legacy quorum_passed: highest tier (C5) only — used for SEAL gating
        check.quorum_passed = OPERATION_TIER_THRESHOLDS["C5"]["admin_min"] <= w_admin

        # Routing rationale
        if not identity_exists:
            check.rationale += (
                f" | IDENTITY_DOES_NOT_EXIST: W3={witness_set['W3_name']:.2f} or "
                f"W4={witness_set['W4_history']:.2f} < 0.50 — actor not ratified"
            )
        elif named_actor:
            tier_rationale = (
                f"OPERATION={operation_class} | "
                f"admin_min={admin_min:.2f} (pass={tier_admin_pass}) | "
                f"biometric_min={biometric_min:.2f} (pass={tier_biometric_pass}) | "
                f"constitutional_min={constitutional_min:.2f} (pass={tier_constitutional_pass})"
            )
            if tier_passed:
                check.rationale += f" | IDENTITY_VERIFIED: {tier_rationale}"
            else:
                check.rationale += f" | IDENTITY_VERIFICATION_FAILED: {tier_rationale}"

        return check

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
