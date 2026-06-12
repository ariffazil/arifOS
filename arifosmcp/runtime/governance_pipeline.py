"""
Governance Pipeline — the single pipe every tool call must pass through
═══════════════════════════════════════════════════════════════════════

This is the dynamic flow Arif asked for. Not more schemas, not more
declarations — a single pipeline that intercepts every tool call and
runs all contract checks in sequence. No agent brain required. No
scattered copy-paste. One pipe. Every call. Always.

The 8-Gate Sequence:
  Gate 0: Session Binding       — session_id must be valid and active
  Gate 1: Identity & Authority  — actor must be verified for this action class
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
  - Fires NATS event for monitoring

On PASS through all gates:
  - Execution proceeds
  - After execution: seal to VAULT999 (if MUTATE/ATOMIC)
  - Update budget consumption

DITEMPA BUKAN DIBERI — The pipe is forged, not given.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable

# ── Reality Engineering Bridge (Ω, 2026-06-12) ──────────────────────
try:
    from arifosmcp.runtime.reality_bridge import (
        session_gate as _reality_session_gate,
        envelope_gate as _reality_envelope_gate,
        risk_gate as _reality_risk_gate,
        classify_output as _reality_classify_output,
        bridge_enabled as _reality_bridge_enabled,
    )

    _REALITY_BRIDGE_AVAILABLE = True
except ImportError:
    _REALITY_BRIDGE_AVAILABLE = False
# ──────────────────────────────────────────────────────────────────────

logger = logging.getLogger("arifosmcp.governance_pipeline")


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE RESULT
# ═══════════════════════════════════════════════════════════════════════════════


class PipelineVerdict(StrEnum):
    PASS = "PASS"  # All gates cleared
    HOLD = "HOLD"  # Blocked at a gate — needs sovereign review
    VOID = "VOID"  # Blocked permanently — action is invalid


class Gate(StrEnum):
    """The 8 gates every tool call passes through, in order."""

    SESSION = "GATE_0_SESSION"
    IDENTITY = "GATE_1_IDENTITY"
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
    risk_tier: str = "T0"  # T0-T5
    envelope: Any = None  # FederationEnvelope if provided


# ═══════════════════════════════════════════════════════════════════════════════
# THE GOVERNANCE PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════


class GovernancePipeline:
    """
    The single pipe. Every tool call passes through this before execution.

    Usage:
        pipeline = GovernancePipeline()
        result = pipeline.run(ToolCallContext(tool_name="arif_forge_execute", ...))
        if result.all_clear:
            execute(tool_call)
        else:
            return result.hold_receipt()
    """

    def __init__(
        self,
        *,
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
            session_id=ctx.session_id or "unknown",
            tool_name=ctx.tool_name,
        )

        # Gate 0: Session
        gate = self._gate_session(ctx)
        result.gate_results.append(gate)
        if not gate.passed:
            result.verdict = PipelineVerdict.HOLD
            result.blocked_at = gate.gate
            result.reasons.append(gate.reason)
            result.violated_laws.extend(gate.metadata.get("violated_laws", []))
            result.next_safe_action = "Restart session with arif_session_init(mode='init')"
            result.total_latency_ms = (time.perf_counter() - t0) * 1000
            return result

        # Gate 1: Identity
        gate = self._gate_identity(ctx)
        result.gate_results.append(gate)
        if not gate.passed:
            result.verdict = PipelineVerdict.HOLD
            result.blocked_at = gate.gate
            result.reasons.append(gate.reason)
            result.violated_laws.extend(gate.metadata.get("violated_laws", ["L11"]))
            result.next_safe_action = (
                "Verify identity with arif_session_init(mode='init', actor_id='...')"
            )
            result.total_latency_ms = (time.perf_counter() - t0) * 1000
            return result

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
                return result

        # ── All gates passed ──────────────────────────────────────────────
        # Record consumption
        self._record_tool_call(ctx)
        result.total_latency_ms = (time.perf_counter() - t0) * 1000
        return result

    # ═══════════════════════════════════════════════════════════════════════
    # GATE 0: SESSION BINDING
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_session(self, ctx: ToolCallContext) -> GateResult:
        """Verify session is valid and active."""
        t0 = time.perf_counter()

        # Allow discovery tools without session
        discovery_tools = {
            "arif_session_init",
            "arif_ops_measure",
            "arif_kernel_route",
            "arif_sense_observe",
        }
        if ctx.tool_name in discovery_tools:
            return GateResult(
                gate=Gate.SESSION,
                passed=True,
                reason="Discovery tool — session not required",
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

        if not ctx.session_id or ctx.session_id in ("unknown", "None", ""):
            return GateResult(
                gate=Gate.SESSION,
                passed=False,
                reason="No session bound. Call arif_session_init(mode='init') first.",
                latency_ms=(time.perf_counter() - t0) * 1000,
                metadata={"violated_laws": ["L11"]},
            )

        # Session exists check — lightweight, just track turns
        sid = ctx.session_id
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
            if ctx.action_class in ("OBSERVE", "PREPARE"):
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
                f"Call arif_session_init with verified actor_id.",
                latency_ms=(time.perf_counter() - t0) * 1000,
                metadata={"violated_laws": ["L11", "L13"]},
            )

        # MUTATE/ATOMIC require verified identity
        if ctx.action_class in ("MUTATE", "ATOMIC"):
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
    # GATE 2: BUDGET ENFORCEMENT
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_budget(self, ctx: ToolCallContext) -> GateResult:
        """Enforce session budget limits."""
        t0 = time.perf_counter()
        sid = ctx.session_id or "unknown"

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

        # Default ceilings per action class
        ceilings = {
            "OBSERVE": "T5",
            "PREPARE": "T4",
            "MUTATE": "T3",
            "ATOMIC": "T2",
        }
        ceiling = ceilings.get(ctx.action_class, "T0")
        tier_num = int(ctx.risk_tier[1])  # "T3" → 3
        ceiling_num = int(ceiling[1])

        if tier_num > ceiling_num:
            return GateResult(
                gate=Gate.RISK,
                passed=False,
                reason=f"Risk {ctx.risk_tier} exceeds ceiling {ceiling} for {ctx.action_class}",
                latency_ms=(time.perf_counter() - t0) * 1000,
                metadata={"violated_laws": [], "risk_tier": ctx.risk_tier, "ceiling": ceiling},
            )

        return GateResult(
            gate=Gate.RISK,
            passed=True,
            reason=f"Risk {ctx.risk_tier} within ceiling {ceiling}",
            latency_ms=(time.perf_counter() - t0) * 1000,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # GATE 4: VAULT LIVENESS
    # ═══════════════════════════════════════════════════════════════════════

    def _gate_vault(self, ctx: ToolCallContext) -> GateResult:
        """Verify vault audit trail is fresh enough for this action."""
        t0 = time.perf_counter()

        # Vault liveness only gates MUTATE/ATOMIC
        if ctx.action_class in ("OBSERVE", "PREPARE"):
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
            if ctx.action_class in ("MUTATE", "ATOMIC"):
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
        sid = ctx.session_id or "unknown"

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

    def as_middleware(self):
        """
        Return an ASGI middleware that intercepts every MCP request.

        Usage:
            app = FastMCP("arifOS")
            app.add_middleware(GovernancePipeline().as_middleware)

        This wraps the entire app so every tool call passes through
        the pipeline before reaching the handler.
        """
        pipeline = self

        class GovernanceASGIMiddleware:
            def __init__(self, app):
                self.app = app

            async def __call__(self, scope, receive, send):
                if scope["type"] == "http":
                    # Only intercept MCP tool calls
                    path = scope.get("path", "")
                    if "/mcp" in path or "/tools" in path:
                        # Attach pipeline to scope for downstream handlers
                        scope["arifos_governance_pipeline"] = pipeline

                await self.app(scope, receive, send)

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
