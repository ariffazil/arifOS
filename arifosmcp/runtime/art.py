"""
ART — Agentic Recursive Tooling

One reflex. Four states. Three checks. One decision.

Lineage:
  2024  — Arif Rule of Thinking (proto-AGI, reasoning doctrine)
  2026  — ART: Agentic Recursive Tooling (tool governance reflex)
  2026  — Hardened v3: Cross-domain lifecycle + 4-state machine

Cross-domain synthesis:
  Piaget      → schema/assimilation/accommodation → tool learning as cognitive adaptation
  Dreyfus     → novice-to-expert skill stages      → tool mastery as staged contact
  Heidegger   → ready/present/unready-to-hand       → tool breakdown = trust state change
  Ashby       → requisite variety                   → tool set must match environment variety
  Wiener      → feedback + regulation                → tool loop must close
  Shannon     → channel capacity + entropy           → context is finite; compress or degrade
  Agent Cyb.  → reliability/lifelong/self-improvement → three desiderata for agentic tools

Usage:
    from arifosmcp.runtime.art import art, ArtRequest, ArtVerdict

    verdict = art(ArtRequest(
        action_class="mutate",
        tool_state="observed",
        blast_radius="low",
        trust_level="evidence",
        actor_resolved=True,
        schema_locked=True,
        degraded=False,
        reversible=True,
        failure_rate=0.0,
        drift_count=0,
        days_since_use=0,
    ))

DITEMPA BUKAN DIBERI — Reflex is forged, not configured.
"""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════
# REFLEX WEIGHT CEILING (binding for v3+ ART reflex)
# ═══════════════════════════════════════════════════════════════════════
# The reflex must be lightweight enough that an agent will actually invoke
# it on every tool call. Anything an agent can skip is a reflex that does
# not exist. Discipline without lightness is ceremony without reflex.
#
# Heritage: Arif Rule of Thinking (proto-AGI, 2024) → ART (2026)
# Full ceiling table: /root/.agents/skills/ART/SKILL.md §"Reflex Weight Ceiling"
# Multi-impl orphan detection: /root/.agents/skills/ART/references/t1-multi-impl-orphan-detection.md
# Cross-domain hardening: /root/.agents/skills/ART/references/v3-cross-domain-hardening.md

def _assert_reflex_weight_ceiling() -> None:
    """Runtime guard: art.py must stay ≤ 500 lines (the binding ceiling).

    If a v(N+1) ART patch increases this file past the ceiling, the import
    fails. The fix is one of: (a) defer the change to doctrine skill, or
    (b) split into a separate non-reflex module (art_compat.py / art_pusaka.py).

    See SKILL.md §"Reflex Weight Ceiling" and §"What v2 INTENTIONALLY does
    NOT do" for the doctrine. The reflex gets lighter, not heavier.
    """
    _CEILING_LINES = 500
    _this_file = os.path.abspath(__file__)
    with open(_this_file) as _f:
        _line_count = sum(1 for _ in _f)
    if _line_count > _CEILING_LINES:
        raise RuntimeError(
            f"ART reflex ceiling violated: art.py is {_line_count} lines "
            f"(ceiling: {_CEILING_LINES}). See /root/.agents/skills/ART/SKILL.md "
            f"§'Reflex Weight Ceiling'. Split heavy logic into art_compat.py "
            f"or art_pusaka.py, or revert."
        )


_assert_reflex_weight_ceiling()


# ═══════════════════════════════════════════════════════════════════════
# v3.1 — DISCOVERY SURFACE HARDENING
# Cumulative silent-fallback detector threshold. If a session has
# this many silent fallbacks (default: 2), ART downgrades to HOLD.
# Tune higher for noisy networks, lower for high-security contexts.
# Per v3.1 docstring: caller pushes the counter from session middleware;
# the reflex itself stays stateless.
# ═══════════════════════════════════════════════════════════════════════
SILENT_FALLBACK_HOLD_THRESHOLD: int = 2


# ═══════════════════════════════════════════════════════════════════════
# CROSS-DOMAIN INSIGHT
# ═══════════════════════════════════════════════════════════════════════
#
# Across EVERY domain studied, tools follow a lifecycle:
#
#   UNTRUSTED (present-at-hand, novel, rule-based, variety deficit)
#       ↓ observe, probe, test — assimilation
#   OBSERVED  (schema formed, familiar, situational)
#       ↓ reliable closed-loop use — accommodation
#   TRUSTED   (ready-to-hand, intuitive, transparent, homeostatic)
#       ↓ breakdown: failure spike, drift, degradation
#   FALLBACK  (unready-to-hand, disequilibrium, loop open)
#       ↓ escalate to human OR recover OR abandon
#   ABANDONED (retired)
#
# The full agentic loop (survey-grounded):
#   1. Tool Mapping     → know footprint (schema, side effects, cost)
#   2. Exploration       → probe without harm (observe only)
#   3. Forging           → turn traces into reflex
#   4. Production        → safe live use under gates
#   5. Testing           → discover where tool lies
#   6. Optimization      → lower entropy, not maximize activity
#   7. Abandonment       → stop before chaos expands
#   8. Fallback          → choose least-entropy alternative
#
# ART collapses all 8 phases into ONE reflex with 4 tool states.
# Why? Because by the time the agent calls art(), all 8 phases
# are already implicit in the tool_state + usage signals.
# ═══════════════════════════════════════════════════════════════════════


class ToolState(str, Enum):
    """Four tool states — the lifecycle of any tool in an agent's world.

    UNTRUSTED — New tool. Never used. Schema unknown. (Heidegger: present-at-hand)
        Allowed: observe only.
        Transition to OBSERVED: first successful observe.

    OBSERVED — Tool probed, schema known, reliability unproven. (Piaget: assimilation)
        Allowed: observe + propose only.
        Transition to TRUSTED: low failure rate (<10%), schema locked.

    TRUSTED — Tool reliable, schema locked, low failure. (Heidegger: ready-to-hand)
        Allowed: observe + mutate + execute (with gates).
        Transition to FALLBACK: failure >30% OR drift >=3 OR degraded.

    FALLBACK — Tool broken, drifting, failing. (Heidegger: unready-to-hand)
        Allowed: observe only.
        Transition to TRUSTED: recovered (failure <5%, schema locked).
        Transition to ABANDONED: catastrophic (failure >50% + drift >=5).

    ABANDONED — Tool removed from active set.
        Allowed: block all.
    """
    UNTRUSTED = "untrusted"
    OBSERVED = "observed"
    TRUSTED = "trusted"
    FALLBACK = "fallback"
    ABANDONED = "abandoned"


class ArtVerdict(str, Enum):
    """What ART decides."""
    PROCEED = "proceed"                # green — call tool
    HOLD = "hold"                      # yellow — ask Arif or delay
    BLOCK = "block"                    # red — cannot call
    DEFAULT_OBSERVE = "observe_only"   # not enough info — observe only


class ArtReason(str, Enum):
    """Why ART reached this verdict."""
    # State-based
    TOOL_ABANDONED = "tool abandoned — blocked"
    TOOL_FALLBACK = "tool in fallback — hold until re-verified"
    TOOL_UNTRUSTED = "tool untrusted — observe only"
    TOOL_OBSERVED_MUTATE = "tool observed — propose only for mutate"
    TOOL_OBSERVED_EXECUTE = "tool observed — cannot execute"

    # Check 1: Power
    BLAST_RADIUS_UNKNOWN = "blast radius unknown — default observe"
    IRREVERSIBLE_NO_ROLLBACK = "irreversible action without rollback"
    EXECUTE_NEEDS_ACK = "execute action always needs ack"
    EXTERNAL_SURFACE_UNACKNOWLEDGED = "mutate on external surface without ack — hold"  # v3.1

    # Check 2: Trust
    ACTOR_UNRESOLVED = "non-observe action without resolved actor"
    TRUST_LEVEL_UNKNOWN = "trust level unknown — default observe"
    VERDICT_WITHOUT_SCHEMA = "tool returns verdict but schema unverified"
    UNVERIFIED_SCHEMA_SOURCE = "schema source unverified — default observe"  # v3.1

    # Check 3: System
    DEGRADED_MUTATION = "system degraded — cannot mutate"
    FAILURE_RATE_HIGH = "failure rate exceeds threshold — fallback suggested"
    DRIFT_DETECTED = "schema/permission drift detected — fallback suggested"
    CUMULATIVE_SILENT_FALLBACK = "cumulative silent fallback detected — hold"  # v3.1

    # Abandonment
    TOOL_STALE = "tool unused >90 days — abandon candidate"

    # All clear
    ALL_CHECKS_PASSED = "all checks passed — proceed"


# ── REQUEST ──────────────────────────────────────────────────────────

@dataclass
class ArtRequest:
    """Minimum signal ART needs to decide.

    Attributes:
        action_class:   "observe" | "mutate" | "execute"
        tool_state:     lifecycle phase of this tool (default: untrusted)
        blast_radius:   "low" | "medium" | "high" | "unknown"
        trust_level:    "evidence" | "verdict" | "unknown"
        actor_resolved: registered with AAA?
        schema_locked:  schema matches expected contract?
        degraded:       any system component down?
        reversible:     can this action be undone?
        failure_rate:   recent failure rate [0.0-1.0]; >0.3 triggers fallback
        drift_count:    schema/permission changes detected; >=3 triggers fallback
        days_since_use: days since last successful call; >90 triggers abandon
    """
    action_class: str = "observe"
    tool_state: str = ToolState.UNTRUSTED.value
    blast_radius: str = "unknown"
    trust_level: str = "unknown"
    actor_resolved: bool = False
    schema_locked: bool = False
    degraded: bool = False
    reversible: bool = False
    failure_rate: float = 0.0
    drift_count: int = 0
    days_since_use: int = 0

    # v3.1 — Discovery Surface Hardening
    # E1: Where the schema came from. "compiled" = import-time introspection
    # (OpenAI @function_tool). "registry" = static TOOLSETS dict (Hermes).
    # "mcp_server" = runtime JSON-RPC tools/list (unverified by default).
    # "builtin" = hardcoded in agent source. "user_supplied" = arbitrary input.
    # Default schema_verified=True is TOFU (trust on first use) — backward
    # compatible with pre-v3.1 callers. Opt out to False for mcp_server /
    # user_supplied schemas that lack signature/hash verification.
    schema_source: str = "builtin"
    schema_verified: bool = True

    # E2: Does the action hit a remote system? Local mcp_filesystem_write is
    # MUTATE but NOT external. mcp_github_create_issue is MUTATE AND external.
    # Without this split, ART treats them identically — the Hermes #16462 gap.
    external_surface: bool = False
    acknowledged_remote: bool = False  # set by session init or explicit policy

    # E3: Cumulative silent-fallback counter. Caller (session middleware)
    # pushes this from outside; reflex itself stays stateless. A single
    # silent fallback is fine. 2+ in a session → HOLD (catches cumulative
    # drift that per-call STATE snapshots miss).
    silent_fallback_count: int = 0


# ── RESULT ───────────────────────────────────────────────────────────

@dataclass
class ArtResult:
    """What ART returns."""
    verdict: ArtVerdict
    reason: ArtReason
    next_tool_state: ToolState | None = None
    check_blocked: int = 0  # 0 = state gate, 1 = power, 2 = trust, 3 = system

    def __bool__(self) -> bool:
        return self.verdict == ArtVerdict.PROCEED


# ── STATE TRANSITION LOGIC ───────────────────────────────────────────

def _suggest_transition(req: ArtRequest) -> tuple[ToolState, ArtReason | None]:
    """Suggest next tool state based on usage signals.

    Implicitly encodes the 8-phase agentic loop:
      Mapping      → UNTRUSTED (tool just discovered)
      Exploration  → UNTRUSTED observe → OBSERVED
      Forging      → OBSERVED + reliable → TRUSTED
      Production   → TRUSTED (active use under gates)
      Testing      → TRUSTED → FALLBACK (failure/drift detected)
      Optimization → signals that prevent unnecessary transitions
      Abandonment  → FALLBACK terminal OR stale → ABANDONED
      Fallback     → FALLBACK recovered → TRUSTED
    """
    current = ToolState(req.tool_state)

    # UNTRUSTED → OBSERVED: first successful observe
    if current == ToolState.UNTRUSTED and req.action_class == "observe":
        return ToolState.OBSERVED, None

    # OBSERVED → TRUSTED: proven reliability
    if current == ToolState.OBSERVED and req.failure_rate < 0.1 and req.schema_locked:
        return ToolState.TRUSTED, None

    # TRUSTED → FALLBACK: failure, drift, or degradation
    if current == ToolState.TRUSTED:
        if req.failure_rate > 0.3:
            return ToolState.FALLBACK, ArtReason.FAILURE_RATE_HIGH
        if req.drift_count >= 3:
            return ToolState.FALLBACK, ArtReason.DRIFT_DETECTED
        if req.degraded:
            return ToolState.FALLBACK, ArtReason.DEGRADED_MUTATION

    # FALLBACK → TRUSTED: recovered
    if current == ToolState.FALLBACK and req.failure_rate < 0.05 \
       and req.schema_locked and not req.degraded:
        return ToolState.TRUSTED, None

    # FALLBACK → ABANDONED: unrecoverable
    if current == ToolState.FALLBACK and req.failure_rate > 0.5 \
       and req.drift_count >= 5:
        return ToolState.ABANDONED, None

    # Any → ABANDONED: stale
    if current not in (ToolState.ABANDONED, ToolState.UNTRUSTED) and req.days_since_use > 90:
        return ToolState.ABANDONED, ArtReason.TOOL_STALE

    return current, None


# ═══════════════════════════════════════════════════════════════════════
# THE REFLEX — ONE FUNCTION. ONE CALL. ONE DECISION.
# ═══════════════════════════════════════════════════════════════════════

def art(request: ArtRequest) -> ArtResult:
    """Agentic Recursive Tooling — the single reflex.

    CHECK 0 — STATE:   Which lifecycle phase is this tool in?
    CHECK 1 — POWER:   What can this tool do to me?
    CHECK 2 — TRUST:   Can I trust what this tool tells me?
    CHECK 3 — SYSTEM:  Is the system healthy enough for this action?

    Returns ArtResult with verdict (proceed/hold/block/observe_only),
    reason, suggested next state, and which check blocked.
    """

    current_state = ToolState(request.tool_state)
    next_state, transition_reason = _suggest_transition(request)

    # ── CHECK 0: STATE GATES ─────────────────────────────────────────

    # ABANDONED: cannot call
    if current_state == ToolState.ABANDONED:
        return ArtResult(
            verdict=ArtVerdict.BLOCK,
            reason=ArtReason.TOOL_ABANDONED,
            next_tool_state=ToolState.ABANDONED,
        )

    # FALLBACK: observe only
    if current_state == ToolState.FALLBACK:
        if request.action_class != "observe":
            return ArtResult(
                verdict=ArtVerdict.HOLD,
                reason=ArtReason.TOOL_FALLBACK,
                next_tool_state=ToolState.FALLBACK,
            )
        return ArtResult(
            verdict=ArtVerdict.PROCEED,
            reason=ArtReason.ALL_CHECKS_PASSED,
            next_tool_state=next_state if next_state != current_state else None,
        )

    # UNTRUSTED: observe only
    if current_state == ToolState.UNTRUSTED and request.action_class not in ("observe",):
        return ArtResult(
            verdict=ArtVerdict.DEFAULT_OBSERVE,
            reason=ArtReason.TOOL_UNTRUSTED,
            next_tool_state=next_state if next_state != current_state else None,
        )

    # OBSERVED: observe + propose only (no execute, no direct mutate)
    if current_state == ToolState.OBSERVED:
        if request.action_class == "execute":
            return ArtResult(
                verdict=ArtVerdict.DEFAULT_OBSERVE,
                reason=ArtReason.TOOL_OBSERVED_EXECUTE,
            )
        if request.action_class == "mutate":
            return ArtResult(
                verdict=ArtVerdict.HOLD,
                reason=ArtReason.TOOL_OBSERVED_MUTATE,
            )

    # ── CHECK 1: POWER ───────────────────────────────────────────────
    # "What can this tool do to me?"

    if request.blast_radius == "unknown":
        return ArtResult(
            verdict=ArtVerdict.DEFAULT_OBSERVE,
            reason=ArtReason.BLAST_RADIUS_UNKNOWN,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=1,
        )

    if request.action_class in ("mutate", "execute") and not request.reversible:
        return ArtResult(
            verdict=ArtVerdict.HOLD,
            reason=ArtReason.IRREVERSIBLE_NO_ROLLBACK,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=1,
        )

    if request.action_class == "execute":
        return ArtResult(
            verdict=ArtVerdict.HOLD,
            reason=ArtReason.EXECUTE_NEEDS_ACK,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=1,
        )

    # v3.1 — E2: EXTERNAL_SURFACE requires explicit ack
    # Closes Hermes #16462 (no first-call approval for MCP tools).
    # A mcp_github_create_issue is MUTATE + external — needs ack.
    # A mcp_filesystem_write is MUTATE but local — proceeds.
    if (request.action_class == "mutate"
            and request.external_surface
            and not request.acknowledged_remote):
        return ArtResult(
            verdict=ArtVerdict.HOLD,
            reason=ArtReason.EXTERNAL_SURFACE_UNACKNOWLEDGED,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=1,
        )

    # ── CHECK 2: TRUST ───────────────────────────────────────────────
    # "Can I trust what this tool tells me?"

    if request.action_class != "observe" and not request.actor_resolved:
        return ArtResult(
            verdict=ArtVerdict.BLOCK,
            reason=ArtReason.ACTOR_UNRESOLVED,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=2,
        )

    if request.trust_level == "unknown":
        return ArtResult(
            verdict=ArtVerdict.DEFAULT_OBSERVE,
            reason=ArtReason.TRUST_LEVEL_UNKNOWN,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=2,
        )

    if request.trust_level == "verdict" and not request.schema_locked:
        return ArtResult(
            verdict=ArtVerdict.HOLD,
            reason=ArtReason.VERDICT_WITHOUT_SCHEMA,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=2,
        )

    # v3.1 — E1: UNVERIFIED_SCHEMA downgrade for non-observe actions
    # Trust-on-first-hash. A tool from mcp_server or user_supplied with
    # schema_verified=False should not run MUTATE/EXECUTE without proof.
    if (not request.schema_verified
            and request.action_class in ("mutate", "execute")):
        return ArtResult(
            verdict=ArtVerdict.DEFAULT_OBSERVE,
            reason=ArtReason.UNVERIFIED_SCHEMA_SOURCE,
            next_tool_state=next_state if next_state != current_state else None,
            check_blocked=2,
        )

    # ── CHECK 3: SYSTEM ──────────────────────────────────────────────
    # "Is the system healthy enough for this action?"

    if request.degraded and request.action_class in ("mutate", "execute"):
        return ArtResult(
            verdict=ArtVerdict.HOLD,
            reason=ArtReason.DEGRADED_MUTATION,
            next_tool_state=ToolState.FALLBACK,
            check_blocked=3,
        )

    # v3.1 — E3: CUMULATIVE_SILENT_FALLBACK detector
    # Catches the slow-burn failure mode: per-call STATE check passes,
    # but 2+ silent fallbacks in a session means something is wrong upstream.
    # Catches Hermes pattern (install succeeds with default_enabled when
    # tools/list probe fails). Caller pushes the counter; reflex stays stateless.
    if request.silent_fallback_count >= SILENT_FALLBACK_HOLD_THRESHOLD:
        return ArtResult(
            verdict=ArtVerdict.HOLD,
            reason=ArtReason.CUMULATIVE_SILENT_FALLBACK,
            next_tool_state=ToolState.FALLBACK,
            check_blocked=3,
        )

    # ── ALL CHECKS PASSED ────────────────────────────────────────────
    return ArtResult(
        verdict=ArtVerdict.PROCEED,
        reason=ArtReason.ALL_CHECKS_PASSED,
        next_tool_state=next_state if next_state != current_state else None,
        check_blocked=0,
    )
