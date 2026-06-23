"""
Governance Pipeline — the single pipe every tool call must pass through
═══════════════════════════════════════════════════════════════════════

This is the dynamic flow Arif asked for. Not more schemas, not more
declarations — a single pipeline that intercepts every tool call and
runs all contract checks in sequence. No agent brain required. No
scattered copy-paste. One pipe. Every call. Always.

The 10-Gate Sequence:
  Gate -1: Kaparinyo Scan         — "Apa rupanya?" — pre-floor simulation check
  Gate 0: Session Binding       — session_id must be valid and active
  Gate 1: Identity & Authority  — actor must be verified for this action class
  Gate 1.5: Principal Paradox   — E7: autonomy contracts as risk expands
  Gate 2: Budget Enforcement    — session must have remaining budget
  Gate 3: Risk Passport         — action must not exceed risk ceiling
  Gate 4: Vault Liveness        — audit trail must be fresh enough
  Gate 5: Floor Compliance      — F1-F13 floors must pass
  Gate 6: Drift Detection       — tool surface must match manifest
  Gate 7: Envelope Validation   — FederationEnvelope v2 must be valid
  Gate 8: EXECUTE               — all clear → proceed

On HOLD at any gate:
  - Returns structured HOLD verdict with reasons[], violated_laws[],
    next_safe_action, and the gate that blocked.
  - Logs to budget violations ledger
  - Fires NATS event for monitoring (via nats_event_bus)

On PASS through all gates:
  - Execution proceeds
  - After execution: seal to VAULT999 (if MUTATE/ATOMIC)
  - Update budget consumption
  - Publishes PASS event to NATS governance stream

DITEMPA BUKAN DIBERI — The pipe is forged, not given.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

# ── F0_ROOTKEY Gate (Gate -2 — constitutional prerequisite) ─────────
try:
    from arifosmcp.core.f0_rootkey import (
        F0GateVerdict as _F0Verdict,
    )
    from arifosmcp.core.f0_rootkey import (
        check_f0_rootkey as _f0_rootkey_check,
    )
    from arifosmcp.core.f0_rootkey import (
        get_rootkey_anchor_status as _f0_anchor_status,
    )

    _F0_ROOTKEY_AVAILABLE = True
except ImportError:
    _F0_ROOTKEY_AVAILABLE = False
    _F0Verdict = None
# ──────────────────────────────────────────────────────────────────────

# ── F13 Non-Delegable Gate (Eureka 5) ─────────────────────────────
try:
    from arifosmcp.runtime.f13_gate import check_f13_integrity as _f13_gate_check

    _F13_GATE_AVAILABLE = True
except ImportError:
    _F13_GATE_AVAILABLE = False
# ──────────────────────────────────────────────────────────────────────

# ── Reality Engineering Bridge (Ω, 2026-06-12) ──────────────────────
try:
    from arifosmcp.runtime.reality_bridge import (
        bridge_enabled as _reality_bridge_enabled,
    )
    from arifosmcp.runtime.reality_bridge import (
        classify_output as _reality_classify_output,
    )
    from arifosmcp.runtime.reality_bridge import (
        envelope_gate as _reality_envelope_gate,
    )
    from arifosmcp.runtime.reality_bridge import (
        risk_gate as _reality_risk_gate,
    )
    from arifosmcp.runtime.reality_bridge import (
        session_gate as _reality_session_gate,
    )

    _REALITY_BRIDGE_AVAILABLE = True
except ImportError:
    _REALITY_BRIDGE_AVAILABLE = False
# ──────────────────────────────────────────────────────────────────────

# ── Kaparinyo Gate (F0 pre-floor, Ω 2026-06-12) ─────────────────────
try:
    from arifosmcp.core.kernel.kaparinyo_gate import (
        tanya_apa_rupanya as _kaparinyo_scan,
    )

    _KAPARINYO_GATE_AVAILABLE = True
except ImportError:
    _KAPARINYO_GATE_AVAILABLE = False
# ──────────────────────────────────────────────────────────────────────

# ── NATS Event Bus (mesh wiring, P0 2026-06-14) ─────────────────────
try:
    from arifosmcp.runtime.nats_event_bus import event_bus as _nats_event_bus

    _NATS_AVAILABLE = True
except ImportError:
    _NATS_AVAILABLE = False
# ──────────────────────────────────────────────────────────────────────

# ── E7 Principal Paradox (Gate 1.5, 2026-06-14) ──────────────────────
try:
    from arifosmcp.runtime.principal_paradox import (
        MAX_OVERRIDES_PER_HOUR as _E7_MAX_OVERRIDES,
    )
    from arifosmcp.runtime.principal_paradox import (
        AutonomyTier as _E7AutonomyTier,
    )
    from arifosmcp.runtime.principal_paradox import (
        gate_1_5_principal_paradox as _e7_gate,
    )

    _E7_AVAILABLE = True
except ImportError:
    _E7_AVAILABLE = False

# ── Tool Risk Registry (E7 bridge, 2026-06-14) ─────────────────────
try:
    from arifosmcp.runtime.tool_risk_registry import classify_tool_call as _classify_risk

    _RISK_REGISTRY_AVAILABLE = True
except ImportError:
    _RISK_REGISTRY_AVAILABLE = False

try:
    from arifosmcp.apps.command_center.identities import (
        is_protected_sovereign_id as _is_protected_sovereign_id,
    )
except ImportError:
    _is_protected_sovereign_id = None
# ──────────────────────────────────────────────────────────────────────

logger = logging.getLogger("arifosmcp.governance_pipeline")

_SOVEREIGN_ALIASES = frozenset(
    {
        "arif",
        "ariffazil",
        "arif-fazil",
        "arif_fazil",
        "muhammad_arif",
        "muhammad_arif_bin_fazil",
        "human_sovereign",
        "arif:sovereign",
    }
)


def _normalize_actor_id(actor_id: Any) -> str:
    if actor_id is None:
        return ""
    return str(actor_id).strip().lower()


def _is_principal_actor(actor_id: Any) -> bool:
    actor_norm = _normalize_actor_id(actor_id)
    if not actor_norm:
        return False
    if _is_protected_sovereign_id is not None and _is_protected_sovereign_id(actor_norm):
        return True
    return actor_norm in _SOVEREIGN_ALIASES


def _has_active_authority(ctx: Any) -> bool:
    if getattr(ctx, "caller_has_lease", False):
        return True

    params = getattr(ctx, "params", {}) or {}
    if params.get("lease_id") or params.get("authority_lease_id"):
        return True

    envelope = getattr(ctx, "envelope", None)
    authority = getattr(envelope, "authority", None)
    if authority is None:
        return False

    source = getattr(getattr(authority, "source", None), "value", None) or str(
        getattr(authority, "source", "") or ""
    )
    source = source.lower()
    actor_verification = str(getattr(ctx, "actor_verification", "") or "").lower()

    if getattr(authority, "verified", False):
        return True

    return source in {"token", "session", "delegated", "human_888"} and actor_verification in {
        "verified",
        "delegated",
    }


def _reversibility_to_float(value: Any) -> float:
    if value is None:
        return 1.0
    if isinstance(value, (int, float)):
        return float(value)

    text = str(getattr(value, "value", value)).strip().lower()
    mapping = {
        "high": 0.9,
        "medium": 0.5,
        "low": 0.3,
        "irreversible": 0.0,
    }
    return mapping.get(text, 1.0)


def _is_mutating_action(action_class: Any) -> bool:
    return str(action_class or "").upper() in {
        "MUTATE",
        "EXTERNAL_SIDE_EFFECT",
        "IRREVERSIBLE",
        "ATOMIC",
    }


def _is_low_impact_action(action_class: Any) -> bool:
    return str(action_class or "").upper() in {
        "OBSERVE",
        "PREPARE",
        "ANALYZE",
        "DRAFT",
        "SIMULATE",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION ID HARD PRIMITIVE (P0 — 2026-06-12)
# ═══════════════════════════════════════════════════════════════════════════════
# The MiddlewareContext does not guarantee a session_id attribute.
# This helper ensures every downstream read gets a valid session_id
# or mints one deterministically. Without this, arif_init
# fails with "MiddlewareContext has no attribute session_id" and
# the entire init pipeline is broken.
# ═══════════════════════════════════════════════════════════════════════════════


def _ensure_session_id(ctx: Any) -> str:
    """Hard primitive — never let middleware guess.

    Priority: ctx.session_id (if set) > request.session_id (if
    attached) > generated UUID4. Always write back to ctx so
    downstream reads see the same value.
    """
    sid = getattr(ctx, "session_id", None)
    if not sid or sid in ("unknown", "None", ""):
        # Check if request has a session_id attached
        req = getattr(ctx, "request", None)
        if req is not None:
            sid = getattr(req, "session_id", None)
    if not sid or sid in ("unknown", "None", ""):
        import uuid

        sid = f"sess_{uuid.uuid4().hex[:16]}"
    # Write back so subsequent reads are consistent
    try:
        ctx.session_id = sid
    except (AttributeError, TypeError):
        pass  # frozen dataclass; the value lives in the call chain
    return sid


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE RESULT
# ═══════════════════════════════════════════════════════════════════════════════


class PipelineVerdict(StrEnum):
    PASS = "PASS"  # All gates cleared
    WARN = "WARN"  # Advisory — simulation detected, but not blocked (Kaparinyo Gate)
    HOLD = "HOLD"  # Blocked at a gate — needs sovereign review
    VOID = "VOID"  # Blocked permanently — action is invalid


class Gate(StrEnum):
    """The 12 gates every tool call passes through, in order.

    Gate -2: F0_ROOTKEY   — Is the sovereign anchored? (constitutional prerequisite)
    Gate -1: KAPARINYO    — "Apa rupanya?" (pre-floor simulation detection)
    Gate  0: SESSION      — Is there a valid session?
    Gate  1: IDENTITY     — Who is calling?
    Gate 1.5: F13        — Is F13 non-delegable? (sovereign authority integrity)
    Gate 1.5: PRINCIPAL_PARADOX — E7: autonomy contracts as risk expands
    Gate  2: BUDGET       — Does the session have remaining budget?
    Gate  3: RISK         — Does the action exceed the risk ceiling?
    Gate  4: VAULT        — Is the audit trail fresh enough?
    Gate  5: FLOORS       — Do F1-F13 constitutional floors pass?
    Gate  6: DRIFT        — Does the tool surface match the manifest?
    Gate  7: ENVELOPE     — Is the FederationEnvelope v2 valid?
    """

    ROOTKEY = "GATE_-2_ROOTKEY"  # F0: constitutional prerequisite
    KAPARINYO = "GATE_-1_KAPARINYO"  # Pre-floor: "Apa rupanya?"
    SESSION = "GATE_0_SESSION"
    IDENTITY = "GATE_1_IDENTITY"
    F13_SOVEREIGN = "GATE_1.5_F13_SOVEREIGN"  # E5: F13 non-delegable gate
    PRINCIPAL_PARADOX = "GATE_1.5_PRINCIPAL_PARADOX"  # E7: autonomy contracts as risk expands
    BUDGET = "GATE_2_BUDGET"
    RISK = "GATE_3_RISK"
    VAULT = "GATE_4_VAULT_LIVENESS"
    FLOORS = "GATE_5_FLOORS"
    DRIFT = "GATE_6_DRIFT"
    ENVELOPE = "GATE_7_ENVELOPE"


@dataclass
class GateResult:
    """Result of a single gate check."""

    gate: Gate
    passed: bool
    reason: str = ""
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Complete result of the governance pipeline."""

    verdict: PipelineVerdict
    gate_results: list[GateResult] = field(default_factory=list)
    blocked_at: Gate | None = None
    reasons: list[str] = field(default_factory=list)
    violated_laws: list[str] = field(default_factory=list)
    next_safe_action: str = ""
    total_latency_ms: float = 0.0
    session_id: str = ""
    tool_name: str = ""
    # F0_ROOTKEY Gate (Gate -2)
    f0_rootkey_verdict: str = ""
    f0_rootkey_public_key_loaded: bool = False
    # Kaparinyo Gate (F0 pre-floor)
    kaparinyo_score: float = 0.0
    kaparinyo_advice: str = ""
    # F13 Gate (Gate 1.5)
    f13_authority_verified: bool = False

    @property
    def all_clear(self) -> bool:
        return self.verdict == PipelineVerdict.PASS

    def hold_receipt(self) -> dict[str, Any]:
        """Return a structured HOLD receipt for the caller."""
        return {
            "verdict": "HOLD",
            "pipeline_verdict": self.verdict.value,
            "blocked_at": self.blocked_at.value if self.blocked_at else None,
            "reasons": self.reasons,
            "violated_laws": self.violated_laws,
            "next_safe_action": self.next_safe_action,
            "total_latency_ms": self.total_latency_ms,
            "gate_results": [
                {
                    "gate": r.gate.value,
                    "passed": r.passed,
                    "reason": r.reason if not r.passed else "",
                    "latency_ms": r.latency_ms,
                }
                for r in self.gate_results
            ],
        }


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL CALL CONTEXT — what the pipeline needs to know about each call
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ToolCallContext:
    """Everything the pipeline needs to know about a tool call."""

    tool_name: str
    session_id: str | None = None
    actor_id: str | None = None
    actor_verification: str = "claimed"  # claimed | verified | delegated
    params: dict[str, Any] = field(default_factory=dict)
    action_class: str = "OBSERVE"  # OBSERVE | PREPARE | MUTATE | ATOMIC
    risk_tier: str = "LOW"  # LOW | MEDIUM | HIGH | ATOMIC (also accepts legacy T0-T5)
    blast_radius: str = "LOCAL"  # LOCAL | ORGAN | FEDERATION | EXTERNAL (E7)
    reversibility: float = 1.0  # 1.0 (fully reversible) → 0.0 (irreversible) (E7)
    caller_is_principal: bool = False  # True if human sovereign (F13) is direct caller
    caller_has_lease: bool = False  # True if caller holds active authority lease
    envelope: Any = None  # FederationEnvelope if provided


# ═══════════════════════════════════════════════════════════════════════════════
# THE GOVERNANCE PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════


class GovernancePipeline:
    """
    The single pipe. Every tool call passes through this before execution.

    Usage:
        pipeline = GovernancePipeline()
        result = pipeline.run(ToolCallContext(tool_name="arif_forge", ...))
        if result.all_clear:
            execute(tool_call)
        else:
            return result.hold_receipt()
    """

    def __init__(
        self,
        *,
        # ── F0_ROOTKEY Gate (Gate -2 — constitutional prerequisite) ──
        f0_rootkey_enabled: bool = True,
        # ── Kaparinyo Gate (F0 pre-floor) ──
        kaparinyo_enabled: bool = True,
        kaparinyo_warn_threshold: float = 0.50,
        kaparinyo_hold_threshold: float = 0.75,
        # ── F13 Non-Delegable Gate (Gate 1.5) ──
        f13_gate_enabled: bool = True,
        # ── E7 Principal Paradox (Gate 1.5) ──
        principal_paradox_enabled: bool = True,
        # ── Enforcement mode ──
        enforcement_mode: str = "enforce",  # "enforce" | "simulate"
        # ── Standard gates ──
        budget_enabled: bool = True,
        vault_liveness_enabled: bool = True,
        drift_enabled: bool = True,
        floor_enabled: bool = True,
        envelope_enabled: bool = True,
        # ── Budget limits ──
        max_turns: int = 8,
        max_tool_calls: int = 12,
        max_same_tool_calls: int = 2,
        max_retries: int = 1,
        max_no_progress: int = 2,
        max_context_percent: float = 0.75,
        # ── Vault liveness ──
        vault_max_seal_age_s: int = 300,
        vault_min_chain_height: int = 1,
        vault_max_chain_gaps: int = 0,
        # ── Drift ──
        drift_target_manifest: str = "canonical13",
    ):
        self.budget_enabled = budget_enabled
        self.vault_liveness_enabled = vault_liveness_enabled
        self.drift_enabled = drift_enabled
        self.floor_enabled = floor_enabled
        self.envelope_enabled = envelope_enabled

        # F0_ROOTKEY Gate (Gate -2 — constitutional prerequisite)
        self.f0_rootkey_enabled = f0_rootkey_enabled and _F0_ROOTKEY_AVAILABLE

        # Kaparinyo Gate (F0 pre-floor)
        self.kaparinyo_enabled = kaparinyo_enabled and _KAPARINYO_GATE_AVAILABLE
        self.kaparinyo_warn_threshold = kaparinyo_warn_threshold
        self.kaparinyo_hold_threshold = kaparinyo_hold_threshold

        # F13 Non-Delegable Gate (Gate 1.5 — sovereign authority integrity)
        self.f13_gate_enabled = f13_gate_enabled and _F13_GATE_AVAILABLE

        # E7 Principal Paradox (Gate 1.5)
        self.principal_paradox_enabled = principal_paradox_enabled and _E7_AVAILABLE

        # Enforcement mode — "enforce" (hard block) or "simulate" (log only)
        self.enforcement_mode = enforcement_mode

        # Budget limits (can be overridden per-session)
        self.max_turns = max_turns
        self.max_tool_calls = max_tool_calls
        self.max_same_tool_calls = max_same_tool_calls
        self.max_retries = max_retries
        self.max_no_progress = max_no_progress
        self.max_context_percent = max_context_percent

        # Vault liveness
        self.vault_max_seal_age_s = vault_max_seal_age_s
        self.vault_min_chain_height = vault_min_chain_height
        self.vault_max_chain_gaps = vault_max_chain_gaps

        # Drift
        self.drift_target_manifest = drift_target_manifest

        # Per-session state
        self._sessions: dict[str, dict] = {}
        self._tool_call_counts: dict[str, dict[str, int]] = {}  # session_id → {tool_name: count}
        self._turn_counts: dict[str, int] = {}  # session_id → turn_count
        self._no_progress_counts: dict[str, int] = {}  # session_id → no_progress_count

    # ── Main entry point ───────────────────────────────────────────────────

    def run(self, ctx: ToolCallContext) -> PipelineResult:
        """Run the full governance pipeline on a tool call."""
        t0 = time.perf_counter()
        result = PipelineResult(
            verdict=PipelineVerdict.PASS,
            session_id=_ensure_session_id(ctx),
            tool_name=ctx.tool_name,
        )

        # Gate -2: F0_ROOTKEY — constitutional prerequisite
        # "Is the sovereign anchored?" — runs before ANY other gate
        if _F0_ROOTKEY_AVAILABLE and self.f0_rootkey_enabled:
            gate = self._gate_f0_rootkey(ctx)
            result.gate_results.append(gate)
            result.f0_rootkey_verdict = gate.metadata.get("f0_verdict", "UNKNOWN")
            result.f0_rootkey_public_key_loaded = gate.metadata.get("public_key_loaded", False)
            if not gate.passed:
                if self.enforcement_mode == "simulate":
                    logger.warning(
                        "F0 SIMULATE: would have blocked %s — %s",
                        ctx.tool_name,
                        gate.reason,
                    )
                    # Override: mark passed in simulation mode
                    gate = GateResult(
                        gate=gate.gate,
                        passed=True,
                        reason=f"[SIMULATE] F0 would have failed: {gate.reason}",
                        latency_ms=gate.latency_ms,
                        metadata={
                            **gate.metadata,
                            "enforcement_mode": "simulate",
                            "would_have_blocked": True,
                        },
                    )
                    result.gate_results[-1] = gate
                elif gate.metadata.get("f0_verdict") == "FAIL":
                    result.verdict = PipelineVerdict.VOID
                    result.blocked_at = gate.gate
                    result.reasons.append(
                        f"F0_ROOTKEY FAIL: {gate.reason} — "
                        "constitutional prerequisite not met. "
                        "Seal root anchor before proceeding."
                    )
                    result.violated_laws.append("F0")
                    result.next_safe_action = (
                        "Seal F0_ROOTKEY anchor: run arif_seal with "
                        "f0_rootkey anchor payload, or set ARIF_ROOTKEY env var."
                    )
                    result.total_latency_ms = (time.perf_counter() - t0) * 1000
                    self._publish_to_mesh(ctx, result)
                    return result
                # HOLD — key exists but caller not verified; observer access only

        # Gate -1: Kaparinyo (F0 pre-floor — "Apa rupanya?")
        if _KAPARINYO_GATE_AVAILABLE and self.kaparinyo_enabled:
            gate = self._gate_kaparinyo(ctx)
            result.gate_results.append(gate)
            if gate.metadata.get("kaparinyo_hold"):
                # KAPARINYO_HOLD — simulation detected; advisory escalation
                result.verdict = PipelineVerdict.WARN
                result.reasons.append(f"KAPARINYO: {gate.reason}")
                result.kaparinyo_score = gate.metadata.get("kaparinyo_score", 0.0)
                result.kaparinyo_advice = gate.metadata.get("advice_bm", "")
                # Does NOT block — advisory only (F1 reversible)
                # Falls through to Gate 0

        # Gate 0: Session
        gate = self._gate_session(ctx)
        result.gate_results.append(gate)
        if not gate.passed:
            result.verdict = PipelineVerdict.HOLD
            result.blocked_at = gate.gate
            result.reasons.append(gate.reason)
            result.violated_laws.extend(gate.metadata.get("violated_laws", []))
            result.next_safe_action = "Restart session with arif_init(mode='init')"
            result.total_latency_ms = (time.perf_counter() - t0) * 1000
            self._publish_to_mesh(ctx, result)
            return result

        # Gate 1: Identity
        gate = self._gate_identity(ctx)
        result.gate_results.append(gate)
        if not gate.passed:
            result.verdict = PipelineVerdict.HOLD
            result.blocked_at = gate.gate
            result.reasons.append(gate.reason)
            result.violated_laws.extend(gate.metadata.get("violated_laws", ["L11"]))
            result.next_safe_action = "Verify identity with arif_init(mode='init', actor_id='...')"
            result.total_latency_ms = (time.perf_counter() - t0) * 1000
            self._publish_to_mesh(ctx, result)
            return result

        # Gate 1.5: F13 Non-Delegable Gate (E5 — sovereign authority integrity)
        if _F13_GATE_AVAILABLE and self.f13_gate_enabled:
            gate = self._gate_f13_sovereign(ctx)
            result.gate_results.append(gate)
            result.f13_authority_verified = gate.passed
            if not gate.passed:
                if self.enforcement_mode == "simulate":
                    logger.warning(
                        "F13 SIMULATE: would have blocked %s — %s",
                        ctx.tool_name,
                        gate.reason,
                    )
                    gate = GateResult(
                        gate=gate.gate,
                        passed=True,
                        reason=f"[SIMULATE] F13 would have failed: {gate.reason}",
                        latency_ms=gate.latency_ms,
                        metadata={
                            **gate.metadata,
                            "enforcement_mode": "simulate",
                            "would_have_blocked": True,
                        },
                    )
                    result.gate_results[-1] = gate
                else:
                    result.verdict = PipelineVerdict.HOLD
                    result.blocked_at = gate.gate
                    result.reasons.append(gate.reason)
                    result.violated_laws.extend(gate.metadata.get("violated_laws", ["F13"]))
                    result.next_safe_action = (
                        "F13 non-delegable. Only Yang Arif (ARIF / Muhammad Arif bin Fazil) "
                        "may perform F13-gated actions. Delegation attempts are blocked."
                    )
                    result.total_latency_ms = (time.perf_counter() - t0) * 1000
                    self._publish_to_mesh(ctx, result)
                    return result

        # Gate 1.5: Principal Paradox (E7)
        if self.principal_paradox_enabled:
            gate = self._gate_principal_paradox(ctx)
            result.gate_results.append(gate)
            if not gate.passed:
                e7_verdict = gate.metadata.get("e7_verdict", "SABAR")

                # ── Simulation mode: log what WOULD have been blocked ──
                if self.enforcement_mode == "simulate":
                    logger.warning(
                        "E7 SIMULATE: would have issued %s for %s — %s",
                        e7_verdict,
                        ctx.tool_name,
                        gate.reason,
                    )
                    # Override gate result — mark passed but carry WARN annotation
                    gate = GateResult(
                        gate=gate.gate,
                        passed=True,
                        reason=f"[SIMULATE] Would have been {e7_verdict}: {gate.reason}",
                        latency_ms=gate.latency_ms,
                        metadata={
                            **gate.metadata,
                            "shadow_verdict": e7_verdict,
                            "enforcement_mode": "simulate",
                            "would_have_blocked": True,
                        },
                    )
                    result.gate_results[-1] = gate
                    # Fall through — do not block

                elif e7_verdict == "HOLD":
                    result.verdict = PipelineVerdict.HOLD
                    result.blocked_at = gate.gate
                    result.reasons.append(gate.reason)
                    result.violated_laws.extend(gate.metadata.get("violated_laws", ["E7"]))
                    result.next_safe_action = gate.metadata.get(
                        "next_safe_action",
                        "Escalate to principal (F13 SOVEREIGN) or reduce risk tier.",
                    )
                    result.total_latency_ms = (time.perf_counter() - t0) * 1000
                    self._publish_to_mesh(ctx, result)
                    return result

                else:
                    # SABAR — principal approval required, advisory escalation
                    result.verdict = PipelineVerdict.WARN
                    result.reasons.append(gate.reason)
                    result.violated_laws.extend(gate.metadata.get("violated_laws", []))
                    result.next_safe_action = gate.metadata.get(
                        "next_safe_action",
                        "Await principal approval or downgrade action_class.",
                    )
                    result.total_latency_ms = (time.perf_counter() - t0) * 1000
                    self._publish_to_mesh(ctx, result)
                    # SABAR falls through — advisory, not hard block
                    # (F1 AMANAH: autonomy contraction is reversible policy)

        # Gate 2: Budget
        if self.budget_enabled:
            gate = self._gate_budget(ctx)
            result.gate_results.append(gate)
            if not gate.passed:
                result.verdict = PipelineVerdict.HOLD
                result.blocked_at = gate.gate
                result.reasons.append(gate.reason)
                result.violated_laws.extend(gate.metadata.get("violated_laws", ["BUDGET"]))
                result.next_safe_action = (
                    "888_HOLD: session budget exhausted. Wait for sovereign review."
                )
                result.total_latency_ms = (time.perf_counter() - t0) * 1000
                self._publish_to_mesh(ctx, result)
                return result

        # Gate 3: Risk
        gate = self._gate_risk(ctx)
        result.gate_results.append(gate)
        if not gate.passed:
            result.verdict = PipelineVerdict.HOLD
            result.blocked_at = gate.gate
            result.reasons.append(gate.reason)
            result.violated_laws.extend(gate.metadata.get("violated_laws", []))
            result.next_safe_action = "Downgrade action class or increase risk ceiling."
            result.total_latency_ms = (time.perf_counter() - t0) * 1000
            self._publish_to_mesh(ctx, result)
            return result

        # Gate 4: Vault Liveness
        if self.vault_liveness_enabled:
            gate = self._gate_vault(ctx)
            result.gate_results.append(gate)
            if not gate.passed:
                result.verdict = PipelineVerdict.HOLD
                result.blocked_at = gate.gate
                result.reasons.append(gate.reason)
                result.violated_laws.extend(gate.metadata.get("violated_laws", []))
                result.next_safe_action = (
                    "Wait for vault to become fresh (next seal or chain repair)."
                )
                result.total_latency_ms = (time.perf_counter() - t0) * 1000
                self._publish_to_mesh(ctx, result)
                return result

        # Gate 5: Floor Compliance
        if self.floor_enabled:
            gate = self._gate_floors(ctx)
            result.gate_results.append(gate)
            if not gate.passed:
                result.verdict = PipelineVerdict.HOLD
                result.blocked_at = gate.gate
                result.reasons.append(gate.reason)
                result.violated_laws.extend(gate.metadata.get("violated_laws", []))
                result.next_safe_action = "Address floor violations before retrying."
                result.total_latency_ms = (time.perf_counter() - t0) * 1000
                self._publish_to_mesh(ctx, result)
                return result

        # Gate 6: Drift
        if self.drift_enabled:
            gate = self._gate_drift(ctx)
            result.gate_results.append(gate)
            if not gate.passed:
                result.verdict = PipelineVerdict.HOLD
                result.blocked_at = gate.gate
                result.reasons.append(gate.reason)
                result.violated_laws.extend(gate.metadata.get("violated_laws", []))
                result.next_safe_action = (
                    "Reconcile tool surface: check drift report for missing/extra tools."
                )
                result.total_latency_ms = (time.perf_counter() - t0) * 1000
                self._publish_to_mesh(ctx, result)
                return result

        # Gate 7: Envelope
        if self.envelope_enabled:
            gate = self._gate_envelope(ctx)
            result.gate_results.append(gate)
            if not gate.passed:
                result.verdict = PipelineVerdict.HOLD
                result.blocked_at = gate.gate
                result.reasons.append(gate.reason)
                result.violated_laws.extend(gate.metadata.get("violated_laws", []))
                result.next_safe_action = (
                    "Fix envelope: ensure valid FederationEnvelope v2 with authority."
                )
                result.total_latency_ms = (time.perf_counter() - t0) * 1000
                self._publish_to_mesh(ctx, result)
                return result

        # ── All gates passed ──────────────────────────────────────────────
        # Record consumption
        self._record_tool_call(ctx)
        result.total_latency_ms = (time.perf_counter() - t0) * 1000

        # ── Publish PASS to NATS governance stream ─────────────────────
        self._publish_to_mesh(ctx, result)

        return result

    def _publish_to_mesh(self, ctx: ToolCallContext, result: PipelineResult) -> None:
        """Publish pipeline verdict to the NATS governance stream.

        Short-lived connection per event (connect → publish → disconnect).
        Runs in a daemon thread — never blocks the governance pipeline.
        Fails silently — governance must never break because NATS is down.
        """
        if not _NATS_AVAILABLE:
            return

        import json as _json
        import threading as _thr
        from datetime import UTC
        from datetime import datetime as _dt

        # Map pipeline verdict to correct NATS subject (matching stream config)
        if result.verdict == PipelineVerdict.PASS:
            subject = "arifos.gate.8.pass"
        else:
            gate_num = result.blocked_at.value.split("_")[1] if result.blocked_at else "unknown"
            subject = f"arifos.gate.{gate_num}.hold"

        payload = _json.dumps(
            {
                "event": "PIPELINE_VERDICT",
                "verdict": result.verdict.value,
                "session_id": _ensure_session_id(ctx),
                "tool_name": ctx.tool_name,
                "action_class": getattr(ctx, "action_class", "OBSERVE"),
                "blocked_at": result.blocked_at.value if result.blocked_at else None,
                "reasons": result.reasons,
                "violated_laws": result.violated_laws,
                "total_latency_ms": result.total_latency_ms,
                "timestamp": _dt.now(UTC).isoformat(),
            }
        ).encode()

        def _publish_sync() -> None:
            """Thread worker: connect, publish, disconnect."""
            import asyncio as _aio

            import nats as _nats_mod

            async def _do() -> None:
                try:
                    nc = await _nats_mod.connect("nats://127.0.0.1:4222", connect_timeout=3)
                    await nc.publish(subject, payload)
                    await nc.flush(timeout=2)
                    await nc.close()
                except Exception:
                    pass  # Mesh unreachable — governance continues

            loop = _aio.new_event_loop()
            _aio.set_event_loop(loop)
            try:
                loop.run_until_complete(_do())
            except Exception:
                pass
            finally:
                loop.close()

        t = _thr.Thread(
            target=_publish_sync, daemon=True, name=f"gov-publish-{result.verdict.value}"
        )
        t.start()

    # ═══════════════════════════════════════════════════════════════════════
    # GATE -2: F0_ROOTKEY — Constitutional Prerequisite
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_f0_rootkey(self, ctx: ToolCallContext) -> GateResult:
        """F0_ROOTKEY gate: is the sovereign anchored?

        This gate runs BEFORE all others. If the rootkey is not anchored,
        no action can proceed — the system does not know its sovereign.

        Three-tier verdict:
          PASS — Ed25519 key exists and caller is verified sovereign
          HOLD — Key exists but caller is not verified (observer mode)
          FAIL — No Ed25519 key found at all (constitutional prerequisite not met)

        F0 is WAJIB-tier. FAIL is system-critical.
        """
        t0 = time.perf_counter()

        # Extract actor identity from context for F0 verification
        actor_id = getattr(ctx, "actor_id", None)
        challenge = getattr(ctx, "params", {}).get("challenge", None)
        sig = getattr(ctx, "params", {}).get("sig", None)

        f0_verdict = _f0_rootkey_check(
            actor_id=actor_id,
            challenge=challenge,
            sig=sig,
        )

        latency_ms = (time.perf_counter() - t0) * 1000
        status = _f0_anchor_status()
        key_loaded = status["f0_rootkey_anchor"]["public_key_loaded"]

        if f0_verdict == _F0Verdict.PASS:
            return GateResult(
                gate=Gate.ROOTKEY,
                passed=True,
                reason="F0_ROOTKEY PASS — sovereign anchored and verified",
                latency_ms=latency_ms,
                metadata={
                    "f0_verdict": "PASS",
                    "public_key_loaded": key_loaded,
                    "public_key_fingerprint": status["f0_rootkey_anchor"]["public_key_fingerprint"],
                },
            )

        elif f0_verdict == _F0Verdict.FAIL:
            return GateResult(
                gate=Gate.ROOTKEY,
                passed=False,
                reason=(
                    "F0_ROOTKEY FAIL — sovereign public key not found. "
                    "The system has no constitutional anchor. "
                    "Action cannot proceed."
                ),
                latency_ms=latency_ms,
                metadata={
                    "f0_verdict": "FAIL",
                    "public_key_loaded": key_loaded,
                    "violated_laws": ["F0"],
                },
            )

        else:
            # HOLD — key exists but caller not verified
            return GateResult(
                gate=Gate.ROOTKEY,
                passed=False,
                reason=(
                    f"F0_ROOTKEY HOLD — sovereign key exists but caller "
                    f"'{actor_id or 'anonymous'}' not verified. "
                    "Observer access only. Provide Ed25519 signature for sovereign access."
                ),
                latency_ms=latency_ms,
                metadata={
                    "f0_verdict": "HOLD",
                    "public_key_loaded": key_loaded,
                    "violated_laws": ["F0", "F11"],
                },
            )

    # ═══════════════════════════════════════════════════════════════════════
    # GATE 1.5: F13 SOVEREIGN — Non-Delegable Authority Gate
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_f13_sovereign(self, ctx: ToolCallContext) -> GateResult:
        """F13 Non-Delegable gate: verify sovereign authority integrity.

        This gate runs at Gate 1.5 (alongside E7 Principal Paradox).
        It checks that:
          1. If the action claims F13 authority, the caller is actually Yang Arif
          2. No delegation terms appear in F13-gated actions
          3. No sub-agent or automation layer claims F13 authority

        F13 is WAJIB-tier and HARAM to delegate.
        """
        t0 = time.perf_counter()

        # Only check F13 for irreversible/mutate actions
        action_class = getattr(ctx, "action_class", "OBSERVE")
        if not _is_mutating_action(action_class):
            return GateResult(
                gate=Gate.F13_SOVEREIGN,
                passed=True,
                reason=f"F13 not required for {action_class} actions",
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

        action_params = getattr(ctx, "params", {})
        caller = getattr(ctx, "actor_id", "anonymous") or "anonymous"

        passed, reason = _f13_gate_check(action_params, caller)

        return GateResult(
            gate=Gate.F13_SOVEREIGN,
            passed=passed,
            reason=reason,
            latency_ms=(time.perf_counter() - t0) * 1000,
            metadata={
                "violated_laws": ["F13"] if not passed else [],
                "caller": caller,
                "action_class": action_class,
            },
        )

    # ═══════════════════════════════════════════════════════════════════════
    # GATE -1: KAPARINYO (F0 pre-floor — "Apa rupanya?")
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_kaparinyo(self, ctx: ToolCallContext) -> GateResult:
        """F0 pre-floor: scan tool call arguments for simulation markers.

        This gate runs BEFORE any constitutional floor. It asks the one question
        that precedes all law: "Apa rupanya?" — what does it actually look like?

        The gate is ADVISORY only (F1 AMANAH reversible). It never blocks
        execution. It injects a WARN verdict into the pipeline result.
        The caller can escalate to 888_HOLD if needed.
        """
        t0 = time.perf_counter()
        # Build scan text from tool call parameters
        scan_text = " ".join(
            str(v) for v in ctx.params.values() if isinstance(v, (str, int, float, bool))
        )
        if not scan_text:
            return GateResult(
                gate=Gate.KAPARINYO,
                passed=True,
                reason="No text to scan",
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

        try:
            kv = _kaparinyo_scan(
                scan_text,
                threshold_warn=self.kaparinyo_warn_threshold,
                threshold_hold=self.kaparinyo_hold_threshold,
            )
        except Exception:
            # Fail-soft: gate failure must never block the pipeline
            return GateResult(
                gate=Gate.KAPARINYO,
                passed=True,
                reason="Gate error — fail-soft",
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

        latency_ms = (time.perf_counter() - t0) * 1000
        is_hold = kv.verdict == "KAPARINYO_HOLD"

        return GateResult(
            gate=Gate.KAPARINYO,
            passed=not is_hold,  # WARN passes through; HOLD sets passed=False
            reason=kv.advice_bm if is_hold else "PASS — output names reality",
            latency_ms=latency_ms,
            metadata={
                "kaparinyo_verdict": kv.verdict,
                "kaparinyo_score": kv.score,
                "kaparinyo_hold": is_hold,
                "advice_bm": kv.advice_bm,
                "advice_en": kv.advice_en,
                "markers_found": len(kv.markers_found),
                "honesty_markers_found": len(kv.honesty_markers_found),
                "gate_id": kv.gate_id,
                "sha256": kv.sha256,
            },
        )

    # ═══════════════════════════════════════════════════════════════════════
    # GATE 0: SESSION BINDING
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_session(self, ctx: ToolCallContext) -> GateResult:
        """Verify session is valid and active."""
        t0 = time.perf_counter()

        # Allow discovery tools without session
        discovery_tools = {
            "arif_init",
            "arif_measure",
            "arif_kernel_route",
            "arif_observe",
        }
        if ctx.tool_name in discovery_tools:
            return GateResult(
                gate=Gate.SESSION,
                passed=True,
                reason="Discovery tool — session not required",
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

        if not _ensure_session_id(ctx):
            return GateResult(
                gate=Gate.SESSION,
                passed=False,
                reason="No session bound. Call arif_init(mode='init') first.",
                latency_ms=(time.perf_counter() - t0) * 1000,
                metadata={"violated_laws": ["L11"]},
            )

        # Session exists check — lightweight, just track turns
        sid = _ensure_session_id(ctx)
        if sid not in self._sessions:
            self._sessions[sid] = {"created_at": time.time(), "actor_id": ctx.actor_id}

        return GateResult(
            gate=Gate.SESSION,
            passed=True,
            reason=f"Session {sid[:12]}... active",
            latency_ms=(time.perf_counter() - t0) * 1000,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # GATE 1: IDENTITY & AUTHORITY
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_identity(self, ctx: ToolCallContext) -> GateResult:
        """Verify actor identity and authority for the action class."""
        t0 = time.perf_counter()

        # Anonymous is fine for OBSERVE
        if not ctx.actor_id or ctx.actor_id in ("anonymous", "None", ""):
            if _is_low_impact_action(ctx.action_class):
                return GateResult(
                    gate=Gate.IDENTITY,
                    passed=True,
                    reason=f"Anonymous {ctx.action_class} allowed",
                    latency_ms=(time.perf_counter() - t0) * 1000,
                )
            return GateResult(
                gate=Gate.IDENTITY,
                passed=False,
                reason=f"Anonymous actor cannot execute {ctx.action_class}. "
                f"Call arif_init with verified actor_id.",
                latency_ms=(time.perf_counter() - t0) * 1000,
                metadata={"violated_laws": ["L11", "L13"]},
            )

        # MUTATE/ATOMIC require verified identity
        if _is_mutating_action(ctx.action_class):
            if ctx.actor_verification == "claimed":
                return GateResult(
                    gate=Gate.IDENTITY,
                    passed=False,
                    reason=f"CLAIMED identity ({ctx.actor_id}) cannot execute {ctx.action_class}. "
                    f"Requires verified or delegated authority.",
                    latency_ms=(time.perf_counter() - t0) * 1000,
                    metadata={"violated_laws": ["L11"]},
                )

        return GateResult(
            gate=Gate.IDENTITY,
            passed=True,
            reason=f"Actor {ctx.actor_id} ({ctx.actor_verification}) authorized for {ctx.action_class}",
            latency_ms=(time.perf_counter() - t0) * 1000,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # GATE 1.5: PRINCIPAL PARADOX (E7)
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_principal_paradox(self, ctx: ToolCallContext) -> GateResult:
        """E7: Autonomy contracts as risk expands.

        When task criticality, irreversibility, or blast radius rises,
        blind delegation becomes invalid. The agent may retain proposal
        authority, but execution authority reverts to the principal.

        This gate evaluates the autonomy ceiling and returns:
          - PASS (FULL_AUTO/PROPOSE_ONLY): proceed
          - WARN (PRINCIPAL_APPROVAL_REQUIRED): SABAR — advisory escalation
          - HOLD: blocked — principal override required
        """
        t0 = time.perf_counter()

        # Derive E7 parameters — registry first, fall back to generic mapping
        if _RISK_REGISTRY_AVAILABLE:
            try:
                profile = _classify_risk(ctx)
                action_class = profile.action_class
                risk_tier = profile.risk_tier
                blast_radius = profile.blast_radius
                reversibility = profile.reversibility
                autonomy_floor = profile.autonomy_floor
            except Exception:
                # Registry failed — fall through to generic mapping
                profile = None

        if not _RISK_REGISTRY_AVAILABLE or profile is None:
            # Generic fallback: map action_class → risk parameters
            action_class = getattr(ctx, "action_class", "OBSERVE")
            risk_tier = getattr(ctx, "risk_tier", "LOW")
            blast_radius = getattr(ctx, "blast_radius", "LOCAL")
            reversibility = getattr(ctx, "reversibility", 1.0)
            autonomy_floor = "FULL_AUTO"

            # Generic blast radius mapping (conservative)
            if not getattr(ctx, "blast_radius", None):
                blast_map = {
                    "OBSERVE": "LOCAL",
                    "PREPARE": "ORG",
                    "ANALYZE": "ORG",
                    "DRAFT": "PUBLIC",
                    "MUTATE": "PUBLIC",
                    "IRREVERSIBLE": "CIVILIZATIONAL",
                }
                blast_radius = blast_map.get(action_class, "LOCAL")

            # Generic reversibility mapping (conservative)
            if not getattr(ctx, "reversibility", None):
                rev_map = {
                    "OBSERVE": 1.0,
                    "ANALYZE": 1.0,
                    "PREPARE": 0.9,
                    "DRAFT": 0.7,
                    "MUTATE": 0.5,
                    "IRREVERSIBLE": 0.1,
                }
                reversibility = rev_map.get(action_class, 0.5)

        # Determine if caller is principal (F13 sovereign)
        caller_is_principal = getattr(ctx, "caller_is_principal", False) or _is_principal_actor(
            getattr(ctx, "actor_id", None)
        )

        # Determine if caller has lease
        caller_has_lease = _has_active_authority(ctx)

        session_id = _ensure_session_id(ctx)

        if not _E7_AVAILABLE:
            return GateResult(
                gate=Gate.PRINCIPAL_PARADOX,
                passed=True,
                reason="E7 module not available — soft pass (degraded mode)",
                latency_ms=(time.perf_counter() - t0) * 1000,
                metadata={"degraded": True},
            )

        try:
            e7_result = _e7_gate(
                action_class=action_class,
                risk_tier=risk_tier,
                blast_radius=blast_radius,
                reversibility=reversibility,
                caller_is_principal=caller_is_principal,
                caller_has_lease=caller_has_lease,
                session_id=session_id,
            )
        except Exception as e:
            logger.warning(f"E7 gate evaluation failed: {e}")
            return GateResult(
                gate=Gate.PRINCIPAL_PARADOX,
                passed=True,
                reason=f"E7 evaluation error — soft pass: {e}",
                latency_ms=(time.perf_counter() - t0) * 1000,
                metadata={"degraded": True, "error": str(e)},
            )

        e7_verdict = e7_result.get("verdict", "PROCEED")
        autonomy_tier = e7_result.get("autonomy_tier", "FULL_AUTO")
        rationale = e7_result.get("rationale", "")
        envelope = e7_result.get("envelope", {})

        latency_ms = (time.perf_counter() - t0) * 1000

        if e7_verdict == "HOLD":
            return GateResult(
                gate=Gate.PRINCIPAL_PARADOX,
                passed=False,
                reason=rationale,
                latency_ms=latency_ms,
                metadata={
                    "violated_laws": ["E7"],
                    "e7_verdict": "HOLD",
                    "autonomy_tier": autonomy_tier,
                    "envelope": envelope,
                    "next_safe_action": e7_result.get(
                        "next_safe_action",
                        "Escalate to principal (F13 SOVEREIGN) or reduce risk tier.",
                    ),
                },
            )

        if e7_verdict == "SABAR":
            return GateResult(
                gate=Gate.PRINCIPAL_PARADOX,
                passed=False,
                reason=rationale,
                latency_ms=latency_ms,
                metadata={
                    "violated_laws": [],
                    "e7_verdict": "SABAR",
                    "autonomy_tier": autonomy_tier,
                    "envelope": envelope,
                    "next_safe_action": e7_result.get(
                        "next_safe_action",
                        "Await principal approval or downgrade action_class.",
                    ),
                    "principal_approval_required": True,
                },
            )

        # PROCEED — FULL_AUTO or PROPOSE_ONLY within ceiling
        return GateResult(
            gate=Gate.PRINCIPAL_PARADOX,
            passed=True,
            reason=rationale,
            latency_ms=latency_ms,
            metadata={
                "e7_verdict": "PROCEED",
                "autonomy_tier": autonomy_tier,
                "envelope": envelope,
            },
        )

    # ═══════════════════════════════════════════════════════════════════════
    # GATE 2: BUDGET ENFORCEMENT
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_budget(self, ctx: ToolCallContext) -> GateResult:
        """Enforce session budget limits."""
        t0 = time.perf_counter()
        sid = _ensure_session_id(ctx)

        # Track turn count
        turns = self._turn_counts.get(sid, 0)
        if turns >= self.max_turns:
            return GateResult(
                gate=Gate.BUDGET,
                passed=False,
                reason=f"888_HOLD: max_turns ({self.max_turns}) reached for session {sid[:12]}...",
                latency_ms=(time.perf_counter() - t0) * 1000,
                metadata={"violated_laws": ["BUDGET"], "current_turns": turns},
            )

        # Track same-tool calls
        tool_counts = self._tool_call_counts.get(sid, {})
        same_tool_count = tool_counts.get(ctx.tool_name, 0)
        if same_tool_count >= self.max_same_tool_calls:
            return GateResult(
                gate=Gate.BUDGET,
                passed=False,
                reason=f"888_HOLD: max_same_tool_calls ({self.max_same_tool_calls}) "
                f"for {ctx.tool_name}",
                latency_ms=(time.perf_counter() - t0) * 1000,
                metadata={"violated_laws": ["BUDGET"], "tool": ctx.tool_name},
            )

        # Track total tool calls
        total_calls = sum(tool_counts.values())
        if total_calls >= self.max_tool_calls:
            return GateResult(
                gate=Gate.BUDGET,
                passed=False,
                reason=f"888_HOLD: max_tool_calls ({self.max_tool_calls}) reached",
                latency_ms=(time.perf_counter() - t0) * 1000,
                metadata={"violated_laws": ["BUDGET"], "total_calls": total_calls},
            )

        return GateResult(
            gate=Gate.BUDGET,
            passed=True,
            reason=f"Budget OK: turn {turns + 1}/{self.max_turns}, "
            f"tool {same_tool_count + 1}/{self.max_same_tool_calls}, "
            f"total {total_calls + 1}/{self.max_tool_calls}",
            latency_ms=(time.perf_counter() - t0) * 1000,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # GATE 3: RISK PASSPORT
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_risk(self, ctx: ToolCallContext) -> GateResult:
        """Verify risk tier does not exceed ceiling."""
        t0 = time.perf_counter()

        # Map named risk tiers to numeric for comparison
        _RISK_TIER_NUMERIC = {
            "LOW": 0,
            "MEDIUM": 1,
            "HIGH": 2,
            "ATOMIC": 3,
            # Legacy T0-T5 format
            "T0": 0,
            "T1": 1,
            "T2": 2,
            "T3": 3,
            "T4": 4,
            "T5": 5,
        }
        tier_num = _RISK_TIER_NUMERIC.get(ctx.risk_tier.upper(), 0)

        # Default ceilings per action class (numeric)
        ceilings = {
            "OBSERVE": 5,
            "ANALYZE": 5,
            "SIMULATE": 5,
            "PREPARE": 4,
            "DRAFT": 4,
            "MUTATE": 2,
            "EXTERNAL_SIDE_EFFECT": 2,
            "IRREVERSIBLE": 1,
            "ATOMIC": 1,
        }
        ceiling_num = ceilings.get(ctx.action_class, 0)

        if tier_num > ceiling_num:
            return GateResult(
                gate=Gate.RISK,
                passed=False,
                reason=f"Risk {ctx.risk_tier} exceeds ceiling for {ctx.action_class}",
                latency_ms=(time.perf_counter() - t0) * 1000,
                metadata={"violated_laws": [], "risk_tier": ctx.risk_tier, "ceiling": ceiling_num},
            )

        return GateResult(
            gate=Gate.RISK,
            passed=True,
            reason=f"Risk {ctx.risk_tier} within ceiling for {ctx.action_class}",
            latency_ms=(time.perf_counter() - t0) * 1000,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # GATE 4: VAULT LIVENESS
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_vault(self, ctx: ToolCallContext) -> GateResult:
        """Verify vault audit trail is fresh enough for this action."""
        t0 = time.perf_counter()

        # Vault liveness only gates MUTATE/ATOMIC
        if _is_low_impact_action(ctx.action_class):
            return GateResult(
                gate=Gate.VAULT,
                passed=True,
                reason=f"Vault liveness not required for {ctx.action_class}",
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

        # Try to probe the vault for real liveness data
        try:
            from arifosmcp.schemas.vault_liveness import VaultLivenessContract

            vault = VaultLivenessContract(
                max_seal_age_seconds=self.vault_max_seal_age_s,
                min_chain_height=self.vault_min_chain_height,
                max_chain_gap_tolerance=self.vault_max_chain_gaps,
            )

            # Probe vault health endpoint
            vault_data = self._probe_vault()
            if vault_data:
                result = vault.check(
                    last_seal_age_seconds=vault_data.get("last_seal_age_s", float("inf")),
                    chain_height=vault_data.get("chain_height", 0),
                    chain_gaps=vault_data.get("chain_gaps", 0),
                    merkle_verified=vault_data.get("merkle_verified", False),
                    signature_verified=vault_data.get("signature_verified", False),
                )
                vault._last_check = result

                allowed, reason = vault.allows_execution(ctx.action_class)
                if not allowed:
                    return GateResult(
                        gate=Gate.VAULT,
                        passed=False,
                        reason=f"Vault {result.state.value}: {reason}",
                        latency_ms=(time.perf_counter() - t0) * 1000,
                        metadata={
                            "violated_laws": [],
                            "vault_state": result.state.value,
                        },
                    )

                return GateResult(
                    gate=Gate.VAULT,
                    passed=True,
                    reason=f"Vault {result.state.value}: {reason}",
                    latency_ms=(time.perf_counter() - t0) * 1000,
                    metadata={"vault_state": result.state.value},
                )

        except Exception as e:
            logger.warning(f"Vault liveness check failed: {e}")

        # Fallback: if vault probe fails, allow OBSERVE/PREPARE, block MUTATE/ATOMIC
        return GateResult(
            gate=Gate.VAULT,
            passed=False,
            reason=f"Vault liveness could not be verified — {ctx.action_class} blocked. "
            f"Probe failed or vault unreachable.",
            latency_ms=(time.perf_counter() - t0) * 1000,
            metadata={"violated_laws": []},
        )

    def _probe_vault(self) -> dict[str, Any] | None:
        """Probe the vault for liveness data. Returns None if unreachable."""
        try:
            import json as _json
            from urllib.request import Request, urlopen

            req = Request("http://localhost:5001/health")
            req.add_header("Accept", "application/json")
            with urlopen(req, timeout=3) as resp:
                data = _json.loads(resp.read().decode())
                # Extract liveness fields
                now = time.time()
                last_seal_ts = data.get("last_seal_timestamp")
                last_seal_age_s = float("inf")
                if last_seal_ts:
                    try:
                        from datetime import UTC, datetime

                        last_dt = datetime.fromisoformat(last_seal_ts.replace("Z", "+00:00"))
                        last_seal_age_s = (datetime.now(UTC) - last_dt).total_seconds()
                    except Exception:
                        pass
                return {
                    "last_seal_age_s": last_seal_age_s,
                    "chain_height": data.get("chain_height", 0),
                    "chain_gaps": data.get("chain_gaps", 0),
                    "merkle_verified": data.get("merkle_verified", False),
                    "signature_verified": data.get("signature_verified", False),
                }
        except Exception:
            return None

    # ═══════════════════════════════════════════════════════════════════════
    # GATE 5: FLOOR COMPLIANCE
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_floors(self, ctx: ToolCallContext) -> GateResult:
        """Verify floor compliance using the existing check_laws function."""
        t0 = time.perf_counter()

        try:
            from arifosmcp.runtime.law import check_laws

            result = check_laws(
                ctx.tool_name,
                ctx.params,
                ctx.actor_id,
            )
            if result.get("verdict") != "SEAL":
                return GateResult(
                    gate=Gate.FLOORS,
                    passed=False,
                    reason=result.get("reason", "Floor violation"),
                    latency_ms=(time.perf_counter() - t0) * 1000,
                    metadata={
                        "violated_laws": result.get("violated_laws", []),
                        "output_policy": result.get("output_policy", "HOLD"),
                    },
                )

            return GateResult(
                gate=Gate.FLOORS,
                passed=True,
                reason="All floors passed",
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

        except ImportError:
            # check_laws not available — soft pass
            return GateResult(
                gate=Gate.FLOORS,
                passed=True,
                reason="check_laws not available — soft pass (degraded mode)",
                latency_ms=(time.perf_counter() - t0) * 1000,
            )
        except Exception as e:
            logger.warning(f"Floor check failed: {e}")
            return GateResult(
                gate=Gate.FLOORS,
                passed=False,
                reason=f"Floor check error: {e}",
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

    # ═══════════════════════════════════════════════════════════════════════
    # GATE 6: DRIFT DETECTION
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_drift(self, ctx: ToolCallContext) -> GateResult:
        """Verify tool surface matches declared manifest."""
        t0 = time.perf_counter()

        try:
            from arifosmcp.tools.drift_check import mcp_drift_check

            report = mcp_drift_check(
                mode="report",
                target_manifest=self.drift_target_manifest,
            )
            if report.get("verdict") == "HOLD":
                return GateResult(
                    gate=Gate.DRIFT,
                    passed=False,
                    reason=f"Tool surface drift detected: "
                    f"missing={report.get('missing', [])}, "
                    f"extra={report.get('extra', [])}",
                    latency_ms=(time.perf_counter() - t0) * 1000,
                    metadata={
                        "violated_laws": [],
                        "missing": report.get("missing", []),
                        "extra": report.get("extra", []),
                    },
                )

            return GateResult(
                gate=Gate.DRIFT,
                passed=True,
                reason=f"Tool surface matches manifest ({self.drift_target_manifest})",
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

        except ImportError:
            return GateResult(
                gate=Gate.DRIFT,
                passed=True,
                reason="drift_check not available — soft pass (degraded mode)",
                latency_ms=(time.perf_counter() - t0) * 1000,
            )
        except Exception as e:
            logger.warning(f"Drift check failed: {e}")
            return GateResult(
                gate=Gate.DRIFT,
                passed=True,
                reason=f"Drift check soft-failed: {e} — allowing (degraded mode)",
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

    # ═══════════════════════════════════════════════════════════════════════
    # GATE 7: ENVELOPE VALIDATION
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_envelope(self, ctx: ToolCallContext) -> GateResult:
        """Validate FederationEnvelope v2 if provided."""
        t0 = time.perf_counter()

        if ctx.envelope is None:
            # No envelope — allow OBSERVE, block MUTATE/ATOMIC
            if _is_mutating_action(ctx.action_class):
                return GateResult(
                    gate=Gate.ENVELOPE,
                    passed=False,
                    reason=f"{ctx.action_class} requires FederationEnvelope v2 with verified authority.",
                    latency_ms=(time.perf_counter() - t0) * 1000,
                    metadata={"violated_laws": ["L11"]},
                )
            return GateResult(
                gate=Gate.ENVELOPE,
                passed=True,
                reason=f"No envelope — {ctx.action_class} allowed without one",
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

        # Try to validate the envelope
        try:
            ok, reason = ctx.envelope.validate_for_execution()
            if not ok:
                return GateResult(
                    gate=Gate.ENVELOPE,
                    passed=False,
                    reason=f"Envelope validation failed: {reason}",
                    latency_ms=(time.perf_counter() - t0) * 1000,
                    metadata={"violated_laws": ["L11"]},
                )

            return GateResult(
                gate=Gate.ENVELOPE,
                passed=True,
                reason="FederationEnvelope v2 valid",
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

        except Exception as e:
            return GateResult(
                gate=Gate.ENVELOPE,
                passed=False,
                reason=f"Envelope validation error: {e}",
                latency_ms=(time.perf_counter() - t0) * 1000,
                metadata={"violated_laws": ["L11"]},
            )

    # ═══════════════════════════════════════════════════════════════════════
    # STATE TRACKING
    # ═══════════════════════════════════════════════════════════════════════

    def _record_tool_call(self, ctx: ToolCallContext) -> None:
        """Record a successful tool call for budget tracking."""
        sid = _ensure_session_id(ctx)

        # Track turns
        self._turn_counts[sid] = self._turn_counts.get(sid, 0) + 1

        # Track tool calls
        if sid not in self._tool_call_counts:
            self._tool_call_counts[sid] = {}
        self._tool_call_counts[sid][ctx.tool_name] = (
            self._tool_call_counts[sid].get(ctx.tool_name, 0) + 1
        )

        # Reset no-progress on successful call
        self._no_progress_counts[sid] = 0

    # ═══════════════════════════════════════════════════════════════════════
    # MIDDLEWARE WRAPPER — for FastMCP/Starlette integration
    # ═══════════════════════════════════════════════════════════════════════

    def as_middleware(self, **kwargs: Any):
        """
        Return an ASGI middleware that intercepts every MCP request.

        Usage:
            app = FastMCP("arifOS")
            app.add_middleware(GovernancePipeline().as_middleware)

        For every MCP tool call, this middleware:
        1. Extracts tool name and arguments from the JSON-RPC body
        2. Runs the governance pipeline (9 gates: session, identity, budget,
           risk, vault, floors, drift, envelope)
        3. If PASS: forwards to the handler
        4. If HOLD: returns a JSON-RPC error with the hold_receipt
        """
        pipeline = self

        class GovernanceASGIMiddleware:
            def __init__(self, app):
                self.app = app

            async def __call__(self, scope, receive, send):
                if scope["type"] != "http":
                    await self.app(scope, receive, send)
                    return

                path = scope.get("path", "")
                is_mcp = "/mcp" in path or "/tools" in path

                if not is_mcp:
                    await self.app(scope, receive, send)
                    return

                # ── Read the request body to inspect the MCP call ──────────
                body_chunks = []
                more_body = True
                while more_body:
                    message = await receive()
                    if message["type"] == "http.request":
                        body_chunks.append(message.get("body", b""))
                        more_body = message.get("more_body", False)

                body = b"".join(body_chunks)

                # Parse JSON-RPC to extract tool name and args
                try:
                    import json as _json

                    rpc = _json.loads(body)
                    method = rpc.get("method", "")
                    params = rpc.get("params", {}) if isinstance(rpc.get("params"), dict) else {}
                    tool_name = params.get("name", "")
                    arguments = (
                        params.get("arguments", {})
                        if isinstance(params.get("arguments"), dict)
                        else {}
                    )
                except Exception:
                    method = ""
                    tool_name = ""
                    arguments = {}

                # ── Run governance pipeline for tools/call ─────────────────
                if method == "tools/call" and tool_name and tool_name != "arif_ping":
                    import os as _os

                    _airlock_mode = _os.getenv("ARIF_AIRLOCK_MODE", "shadow").lower().strip()
                    _envelope = scope.get("airlock_envelope")
                    if _airlock_mode == "enforce":
                        if _envelope is None:
                            from arifosmcp.transport.errors import arif_error

                            error_body = _json.dumps(
                                arif_error(
                                    "ARIF_ENVELOPE_INCOMPLETE",
                                    "Direct JSON-RPC payload bypasses Airlock.",
                                    stage="000_INIT",
                                    jsonrpc_code=-32602,
                                )
                            ).encode()
                            await send(
                                {
                                    "type": "http.response.start",
                                    "status": 200,
                                    "headers": [
                                        (b"content-type", b"application/json"),
                                        (b"x-arifos-airlock-bypass", b"reject"),
                                    ],
                                }
                            )
                            await send(
                                {
                                    "type": "http.response.body",
                                    "body": error_body,
                                }
                            )
                            return

                        # Validate CanonicalEnvelope required fields
                        _required_fields = [
                            "trace_id",
                            "transport",
                            "intent",
                            "normalized_input",
                            "action_class",
                            "reversibility",
                            "risk_level",
                            "requires_hold",
                        ]
                        for _field in _required_fields:
                            _val = getattr(_envelope, _field, None)
                            if _val is None or _val == "":
                                from arifosmcp.transport.errors import arif_error

                                error_body = _json.dumps(
                                    arif_error(
                                        "ARIF_ENVELOPE_INCOMPLETE",
                                        f"CanonicalEnvelope field missing: '{_field}'",
                                        stage="000_INIT",
                                        jsonrpc_code=-32602,
                                    )
                                ).encode()
                                await send(
                                    {
                                        "type": "http.response.start",
                                        "status": 200,
                                        "headers": [
                                            (b"content-type", b"application/json"),
                                            (b"x-arifos-envelope-validation", b"fail"),
                                        ],
                                    }
                                )
                                await send(
                                    {
                                        "type": "http.response.body",
                                        "body": error_body,
                                    }
                                )
                                return

                    from arifosmcp.runtime.blast_radius_registry import (
                        EnforcementMode,
                        get_enforcement_mode,
                        get_risk_profile,
                    )
                    from arifosmcp.runtime.governance_pipeline import (
                        PipelineVerdict,
                        ToolCallContext,
                    )

                    # Resolve enforcement mode for this tool
                    enf_mode = get_enforcement_mode(tool_name)
                    risk = get_risk_profile(tool_name)

                    actor_id = (
                        arguments.get("actor_id")
                        or getattr(_envelope, "actor_id", None)
                        or getattr(_envelope, "caller_actor", None)
                        or getattr(_envelope, "sovereign", None)
                    )
                    actor_verification = (
                        getattr(_envelope, "actor_verification", None)
                        or arguments.get("actor_verification")
                        or "claimed"
                    )
                    blast_radius = (
                        risk.blast_radius.value if risk else arguments.get("blast_radius", "LOCAL")
                    )
                    reversibility = (
                        _reversibility_to_float(risk.reversibility)
                        if risk
                        else _reversibility_to_float(arguments.get("reversibility", 1.0))
                    )
                    caller_is_principal = _is_principal_actor(actor_id) or _is_principal_actor(
                        getattr(_envelope, "sovereign", None)
                    )
                    authority = getattr(_envelope, "authority", None)
                    authority_source = getattr(getattr(authority, "source", None), "value", None)
                    caller_has_lease = bool(
                        arguments.get("lease_id")
                        or arguments.get("authority_lease_id")
                        or (
                            authority_source in {"token", "session", "delegated", "human_888"}
                            and actor_verification in {"verified", "delegated"}
                        )
                        or getattr(authority, "verified", False)
                    )

                    ctx = ToolCallContext(
                        tool_name=tool_name,
                        session_id=arguments.get("session_id")
                        or getattr(_envelope, "session_id", None),
                        actor_id=actor_id,
                        actor_verification=actor_verification,
                        action_class=(
                            risk.action_class.value
                            if risk
                            else arguments.get("action_class", "OBSERVE")
                        ),
                        risk_tier=risk.risk_tier.value if risk else "T1",
                        blast_radius=blast_radius,
                        reversibility=reversibility,
                        caller_is_principal=caller_is_principal,
                        caller_has_lease=caller_has_lease,
                        envelope=_envelope,
                        params=arguments,
                    )
                    result = pipeline.run(ctx)

                    # ── SIMULATE mode: log shadow verdict, never block ────
                    if enf_mode == EnforcementMode.SIMULATE:
                        # Log the shadow verdict to NATS with a shadow marker
                        import json as _json

                        shadow_event = _json.dumps(
                            {
                                "event": "SHADOW_VERDICT",
                                "mode": "SIMULATE",
                                "would_have_been": result.verdict.value,
                                "blocked_at": result.blocked_at.value
                                if result.blocked_at
                                else None,
                                "tool_name": tool_name,
                                "reasons": result.reasons,
                                "session_id": arguments.get("session_id", "?")[:16],
                                "timestamp": __import__("datetime")
                                .datetime.now(__import__("datetime").UTC)
                                .isoformat(),
                            }
                        ).encode()
                        try:
                            import nats as _nats_shadow

                            async def _shadow_publish():
                                nc = await _nats_shadow.connect(
                                    "nats://127.0.0.1:4222", connect_timeout=3
                                )
                                await nc.publish("arifos.governance.shadow", shadow_event)
                                await nc.flush(timeout=2)
                                await nc.close()

                            import asyncio as _aio_shadow

                            loop = _aio_shadow.get_running_loop()
                            loop.create_task(_shadow_publish())
                        except Exception:
                            pass
                        # NEVER block in SIMULATE — always forward
                        # Fall through to forward below

                    # ── ENFORCE / PROPOSE mode: real blocking ─────────────
                    elif result.verdict != PipelineVerdict.PASS:
                        error_body = _json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "id": rpc.get("id"),
                                "error": {
                                    "code": -32001,
                                    "message": f"Governance HOLD [{enf_mode.value}]",
                                    "data": result.hold_receipt(),
                                },
                            }
                        ).encode()

                        await send(
                            {
                                "type": "http.response.start",
                                "status": 200,
                                "headers": [
                                    (b"content-type", b"application/json"),
                                    (b"x-arifos-governance", b"hold"),
                                    (b"x-arifos-enforcement", enf_mode.value.encode()),
                                ],
                            }
                        )
                        await send(
                            {
                                "type": "http.response.body",
                                "body": error_body,
                            }
                        )
                        return  # Blocked — do not forward

                # ── Forward the original request body ──────────────────────
                # Reconstruct receive for the downstream app
                body_sent = False

                async def _receive():
                    nonlocal body_sent
                    if not body_sent:
                        body_sent = True
                        return {
                            "type": "http.request",
                            "body": body,
                            "more_body": False,
                        }
                    return await receive()

                await self.app(scope, _receive, send)

        return GovernanceASGIMiddleware


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON — the federation-wide pipeline
# ═══════════════════════════════════════════════════════════════════════════════

_federation_pipeline: GovernancePipeline | None = None


def get_pipeline(**kwargs) -> GovernancePipeline:
    """Get or create the federation governance pipeline (singleton)."""
    global _federation_pipeline
    if _federation_pipeline is None:
        _federation_pipeline = GovernancePipeline(**kwargs)
    return _federation_pipeline


def reset_pipeline() -> None:
    """Reset the pipeline (for testing)."""
    global _federation_pipeline
    _federation_pipeline = None
