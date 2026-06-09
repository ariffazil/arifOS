"""
arifOS Route Query Policy Engine — Deterministic routing rules.

arifos_route_query is the mandatory pre-retrieval gate. Every agent
MUST call this before any search/discovery tool. It determines:
  - Which lane to use (exploit / explore / hybrid)
  - Budget allocation per lane
  - Contradiction quota enforcement
  - Auth/entitlement checks
  - Audit trail generation

DITEMPA BUKAN DIBERI — Routing is deterministic, not vibes.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ── Lane Enum ──────────────────────────────────────────────────────────────


class QueryLane(str, Enum):
    EXPLOIT = "exploit"       # Relevance-first: known docs, activity signals
    EXPLORE = "explore"       # Discovery-first: orphans, contradictions, old docs
    HYBRID = "hybrid"         # Both lanes, with explicit ratio


class RouteReason(str, Enum):
    EXPLICIT_MODE = "explicit_mode"             # User specified mode
    QUERY_TYPE_EXPLORATORY = "query_exploratory" # "find evidence against X"
    QUERY_TYPE_LOOKUP = "query_lookup"          # "open file X"
    EXPLORE_QUOTA_UNMET = "explore_quota_unmet"  # Session hasn't hit min explore
    DEFAULT_FALLBACK = "default_fallback"        # No signal — exploit default


# ── Budget ─────────────────────────────────────────────────────────────────


class BudgetExceededError(Exception):
    """Raised when lane budget is exhausted."""


@dataclass
class LaneBudget:
    """Per-lane token/result budget with enforcement."""
    max_results: int = 10
    max_tokens: int = 8000
    _consumed_results: int = 0
    _consumed_tokens: int = 0

    @property
    def remaining_results(self) -> int:
        return max(0, self.max_results - self._consumed_results)

    @property
    def remaining_tokens(self) -> int:
        return max(0, self.max_tokens - self._consumed_tokens)

    def consume(self, results: int = 0, tokens: int = 0) -> None:
        self._consumed_results += results
        self._consumed_tokens += tokens
        if self._consumed_results > self.max_results:
            raise BudgetExceededError(
                f"Result budget exceeded: {self._consumed_results}/{self.max_results}"
            )


@dataclass
class DualLaneBudget:
    """Budget across both lanes with hard floors."""
    exploit: LaneBudget = field(default_factory=LaneBudget)
    explore: LaneBudget = field(default_factory=LaneBudget)
    # Hard floors
    min_explore_ratio: float = 0.20   # Minimum 20% of results from explore lane
    min_contradiction_docs: int = 1   # Minimum contradiction documents per session
    _session_contradiction_count: int = 0

    @property
    def explore_ratio(self) -> float:
        total = self.exploit._consumed_results + self.explore._consumed_results
        if total == 0:
            return 0.0
        return self.explore._consumed_results / total

    @property
    def explore_quota_met(self) -> bool:
        if self.exploit._consumed_results == 0:
            return True  # No queries yet — no violation
        return self.explore_ratio >= self.min_explore_ratio

    @property
    def contradiction_quota_met(self) -> bool:
        return self._session_contradiction_count >= self.min_contradiction_docs

    def record_contradiction(self) -> None:
        self._session_contradiction_count += 1


# ── Route Decision ──────────────────────────────────────────────────────────


@dataclass
class RouteDecision:
    """Deterministic output of the route policy engine."""
    lane: QueryLane
    reason: RouteReason
    exploit_budget: LaneBudget
    explore_budget: LaneBudget
    target_tools: list[str]          # Tools to use for this query
    constraints: dict[str, Any]      # Additional constraints for tool calls
    auth_context: dict[str, Any]     # Identity + entitlement propagation
    audit: "RouteAuditEntry"         # Full audit trail


# ── Policy Config ──────────────────────────────────────────────────────────


@dataclass
class RoutePolicyConfig:
    """Configuration for the route policy engine."""
    # Lane defaults
    default_lane: QueryLane = QueryLane.EXPLOIT
    exploit_tools: tuple[str, ...] = (
        "arif_memory_recall",
        "arif_sense_observe",
        "arif_evidence_fetch",
    )
    explore_tools: tuple[str, ...] = (
        "arif_sense_observe",   # with contrast query
        "arif_memory_recall",   # with orphan mode
        "arif_gateway_connect", # cross-organ discovery
    )
    # Budget floors (L0 governance)
    min_explore_ratio: float = 0.20
    min_contradiction_docs: int = 1
    max_exploit_results: int = 10
    max_explore_results: int = 5
    # Query classification triggers
    exploration_triggers: tuple[str, ...] = (
        "contradict", "challenge", "anomal",
        "unknown", "discover", "novel",
        "what if", "alternative", "opposing",
        "evidence against", "argue against",
        "orphan", "forgotten", "historical",
        "different from", "unlike",
    )
    lookup_triggers: tuple[str, ...] = (
        "open", "read", "show", "get",
        "find file", "where is",
    )
    # Session tracking
    session_explore_target: int = 3  # Min explore queries per session


# ── Audit Entry ────────────────────────────────────────────────────────────


@dataclass
class RouteAuditEntry:
    """Structured audit fields for every route decision."""
    session_id: str
    actor_id: str
    query_hash: str          # SHA256 of query (truncated)
    lane: str
    reason: str
    mode: str                # "exploit" | "explore" | "hybrid"
    exploit_tools: list[str]
    explore_tools: list[str]
    budget_exploit_results: int
    budget_explore_results: int
    session_explore_ratio: float
    session_contradiction_count: int
    contradiction_quota_met: bool
    exploration_triggered: bool
    timestamp: str
    latency_ms: float
    error: str | None = None
    fallback_used: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "query_hash": self.query_hash,
            "lane": self.lane,
            "reason": self.reason,
            "mode": self.mode,
            "exploit_tools": self.exploit_tools,
            "explore_tools": self.explore_tools,
            "budget_exploit_results": self.budget_exploit_results,
            "budget_explore_results": self.budget_explore_results,
            "session_explore_ratio": self.session_explore_ratio,
            "session_contradiction_count": self.session_contradiction_count,
            "contradiction_quota_met": self.contradiction_quota_met,
            "exploration_triggered": self.exploration_triggered,
            "timestamp": self.timestamp,
            "latency_ms": self.latency_ms,
            "error": self.error,
            "fallback_used": self.fallback_used,
        }


# ── Policy Engine ──────────────────────────────────────────────────────────


class RoutePolicyEngine:
    """
    Deterministic routing engine for arifos_route_query.

    Rules (in priority order):
      1. Explicit mode override → use specified lane
      2. Query contains exploration trigger → EXPLORE
      3. Session hasn't met min explore quota → HYBRID
      4. Query is a lookup → EXPLOIT
      5. Default → EXPLOIT (fail-safe: relevance over noise)
    """

    def __init__(self, config: RoutePolicyConfig | None = None):
        self.config = config or RoutePolicyConfig()
        self._session_budget: DualLaneBudget = DualLaneBudget(
            exploit=LaneBudget(max_results=self.config.max_exploit_results),
            explore=LaneBudget(max_results=self.config.max_explore_results),
            min_explore_ratio=self.config.min_explore_ratio,
            min_contradiction_docs=self.config.min_contradiction_docs,
        )

    def classify_query(self, query: str) -> tuple[bool, bool]:
        """Classify query: (is_exploratory, is_lookup)."""
        qlower = query.lower()
        is_exploratory = any(t in qlower for t in self.config.exploration_triggers)
        is_lookup = any(t in qlower for t in self.config.lookup_triggers)
        return is_exploratory, is_lookup

    def decide(
        self,
        query: str,
        session_id: str,
        actor_id: str,
        explicit_mode: str | None = None,
        auth_context: dict[str, Any] | None = None,
    ) -> RouteDecision:
        """
        Deterministic routing decision. No LLM. No vibes. Pure rules.
        """
        t0 = time.monotonic()
        error: str | None = None
        fallback_used = False
        lane: QueryLane
        reason: RouteReason

        try:
            is_exploratory, is_lookup = self.classify_query(query)

            # Rule 1: Explicit mode
            if explicit_mode:
                try:
                    lane = QueryLane(explicit_mode)
                    reason = RouteReason.EXPLICIT_MODE
                except ValueError:
                    lane = self.config.default_lane
                    reason = RouteReason.DEFAULT_FALLBACK
                    fallback_used = True
                    error = f"Invalid explicit_mode '{explicit_mode}', fell back to {lane.value}"

            # Rule 2: Exploration trigger
            elif is_exploratory:
                lane = QueryLane.EXPLORE
                reason = RouteReason.QUERY_TYPE_EXPLORATORY

            # Rule 3: Session quota unmet
            elif not self._session_budget.explore_quota_met:
                lane = QueryLane.HYBRID
                reason = RouteReason.EXPLORE_QUOTA_UNMET

            # Rule 4: Lookup
            elif is_lookup:
                lane = QueryLane.EXPLOIT
                reason = RouteReason.QUERY_TYPE_LOOKUP

            # Rule 5: Default
            else:
                lane = self.config.default_lane
                reason = RouteReason.DEFAULT_FALLBACK

        except Exception as e:
            # Fail-closed: default to EXPLOIT (safest lane)
            lane = QueryLane.EXPLOIT
            reason = RouteReason.DEFAULT_FALLBACK
            fallback_used = True
            error = f"Route policy error: {e} — fell back to EXPLOIT"
            logger.exception("Route policy engine failure — fail-closed to EXPLOIT")

        # Build decision
        exploit_tools = list(self.config.exploit_tools)
        explore_tools = list(self.config.explore_tools)

        # Determine tools based on lane
        if lane == QueryLane.EXPLOIT:
            target_tools = exploit_tools
            active_explore = False
        elif lane == QueryLane.EXPLORE:
            target_tools = explore_tools
            active_explore = True
        else:  # HYBRID
            target_tools = exploit_tools + explore_tools
            active_explore = True

        # Build audit entry
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:12]
        audit = RouteAuditEntry(
            session_id=session_id,
            actor_id=actor_id,
            query_hash=query_hash,
            lane=lane.value,
            reason=reason.value,
            mode=lane.value,
            exploit_tools=exploit_tools,
            explore_tools=explore_tools,
            budget_exploit_results=self._session_budget.exploit.remaining_results,
            budget_explore_results=self._session_budget.explore.remaining_results,
            session_explore_ratio=self._session_budget.explore_ratio,
            session_contradiction_count=self._session_budget._session_contradiction_count,
            contradiction_quota_met=self._session_budget.contradiction_quota_met,
            exploration_triggered=is_exploratory,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            latency_ms=(time.monotonic() - t0) * 1000,
            error=error,
            fallback_used=fallback_used,
        )

        return RouteDecision(
            lane=lane,
            reason=reason,
            exploit_budget=self._session_budget.exploit,
            explore_budget=self._session_budget.explore,
            target_tools=target_tools,
            constraints={
                "active_explore": active_explore,
                "min_contradiction_docs": self.config.min_contradiction_docs,
                "contradiction_quota_met": self._session_budget.contradiction_quota_met,
                "explore_quota_met": self._session_budget.explore_quota_met,
            },
            auth_context=auth_context or {},
            audit=audit,
        )

    def record_contradiction(self) -> None:
        """Call after a contradiction document is surfaced."""
        self._session_budget.record_contradiction()

    @property
    def session_budget(self) -> DualLaneBudget:
        return self._session_budget


# ── Singleton ──────────────────────────────────────────────────────────────


_route_policy_engine: RoutePolicyEngine | None = None


def get_route_policy_engine() -> RoutePolicyEngine:
    global _route_policy_engine
    if _route_policy_engine is None:
        _route_policy_engine = RoutePolicyEngine()
    return _route_policy_engine


def reset_route_policy_engine() -> None:
    global _route_policy_engine
    _route_policy_engine = RoutePolicyEngine()
