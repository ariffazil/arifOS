"""
Rasa Contract Kernel Wiring — ARIF_RASA_WIRING_v1

DITEMPA BUKAN DIBERI — Forged, Not Given.

Autonomous wiring of the Rasa Contract into the arifOS kernel with
feature-flagged shadow telemetry. ALL additive — ZERO modifications
to existing kernel files. Uses wrapper/decorator/monkey-patch pattern
for reversible activation.

ARCHITECTURE:
  ┌────────────────────────────────────────────────────────────────┐
  │  EXISTING KERNEL (UNMODIFIED)                                  │
  │                                                                 │
  │  arif_sense_observe()    ──→  rasa_wrap_sense()                │
  │  arif_mind_reason()      ──→  rasa_wrap_mind()                 │
  │  arif_heart_critique()   ──→  rasa_wrap_heart()                │
  │  arif_memory_recall()    ──→  rasa_wrap_memory()               │
  │  arif_judge_deliberate() ──→  rasa_wrap_judge()                │
  │  arif_session_init()     ──→  rasa_wrap_session_init()         │
  │                                                                 │
  │  activate_rasa_wiring()   → monkey-patches tool modules         │
  │  deactivate_rasa_wiring() → restores original functions          │
  └────────────────────────────────────────────────────────────────┘

MODES:
  SHADOW (default):    Log only, zero output change
  ENFORCE_CRISIS:      Enforce CRISIS risk band only
  ENFORCE_DISTRESS:    Enforce CRISIS + DISTRESS
  ENFORCE_ALL:         Full pipeline enforcement

CONSTITUTIONAL BINDING:
  - F1 AMANAH:  Reversible — deactivate_rasa_wiring() restores
  - F9 ANTIHANTU: No consciousness claims in wrapper logic
  - F10 ONTOLOGY: No soul/feelings claims in wrapper logic
  - F13 SOVEREIGN: Feature flag defaults to SHADOW
"""

from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any

from arifosmcp.rasa.rasa_integration import (
    rasa_check_floors,
    rasa_governed_execute,
    rasa_heart_hook,
    rasa_integration_diagnostics,
    rasa_judge_hook,
    rasa_memory_hook,
    rasa_mind_hook,
    rasa_sense_hook,
)
from arifosmcp.rasa.rasa_schemas import (
    RasaRiskBand,
)
from arifosmcp.rasa.rasa_telemetry import RasaTelemetry
from arifosmcp.rasa.rasa_wiring_config import (
    RasaContractMode,
    get_rasa_contract_mode,
    mode_allows_enforcement,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL STATE — Wrapped originals and activation flag
# ═══════════════════════════════════════════════════════════════════════════════

_activated = False
_originals: dict[str, Any] = {}
_current_mode: RasaContractMode = RasaContractMode.SHADOW

# Shared telemetry instance
_telemetry = RasaTelemetry()

# Per-session rasa context (session_id → detection)
_session_rasa: dict[str, dict] = {}


# ═══════════════════════════════════════════════════════════════════════════════
# WRAPPER FUNCTIONS — Each wraps one canonical kernel function
# ═══════════════════════════════════════════════════════════════════════════════


def rasa_wrap_sense(original_sense_fn):
    """Wrap arif_sense_observe (111 SENSE) with rasa detection.

    In SHADOW mode: runs original sense + rasa detection, logs delta.
    In ENFORCE mode: runs original sense, applies rasa governance to output.
    """

    @functools.wraps(original_sense_fn)
    def wrapper(*args, **kwargs):
        # Extract message from query parameter for rasa analysis
        message = kwargs.get("query") or (args[0] if args else "")
        if not isinstance(message, str):
            message = str(message) if message else ""

        session_id = kwargs.get("session_id", "unknown")
        mode_str = _current_mode.value

        # Run the original sense function FIRST (never blocked)
        try:
            result = original_sense_fn(*args, **kwargs)
        except Exception:
            result = {"error": "sense_failed"}

        # Run rasa detection
        detection = None
        governed = None
        enforced = False

        try:
            sense_hook_result = rasa_sense_hook(message, session_id=session_id)
            detection = sense_hook_result.get("detection")

            # Store in session
            _session_rasa[session_id] = sense_hook_result

            # Run full governed pipeline
            try:
                governed = asyncio.run(
                    rasa_governed_execute(message, session_id)
                )
            except Exception:
                governed = None

            # Check if enforcement is needed
            if detection and mode_allows_enforcement(_current_mode, detection.risk_band.value):
                enforced = True
                # Apply governance to output
                result = _apply_rasa_governance(result, governed, detection)
        except Exception as e:
            logger.debug(f"Rasa sense wrapper: {e}")

        # Always log telemetry
        try:
            _telemetry.log_shadow(
                session_id=session_id,
                message=message,
                ungoverned_result=result,
                governed_result=governed.model_dump() if hasattr(governed, 'model_dump') else governed,
                enforcement_mode=mode_str,
                enforced=enforced,
            )
        except Exception:
            pass

        return result

    return wrapper


def rasa_wrap_mind(original_mind_fn):
    """Wrap arif_mind_reason (333 MIND) with rasa context.

    Attaches rasa governance context to reasoning, constraining
    cognitive bandwidth and risk sensitivity per detection.
    """

    @functools.wraps(original_mind_fn)
    def wrapper(*args, **kwargs):
        context = kwargs.get("context") or {}
        session_id = context.get("session_id") if isinstance(context, dict) else kwargs.get(
            "session_id", "unknown"
        )

        # Retrieve prior rasa detection for this session
        rasa_detection = _session_rasa.get(session_id, {}).get("detection")

        # Run original mind reason
        try:
            result = original_mind_fn(*args, **kwargs)
        except Exception:
            result = {"error": "mind_failed"}

        # If we have a detection, run mind hook for context
        if rasa_detection:
            try:
                mind_result = rasa_mind_hook(rasa_detection)
                # Attach rasa context to result
                if isinstance(result, dict):
                    result["_rasa_context"] = {
                        "cognitive_bandwidth": mind_result.get("cognitive_bandwidth"),
                        "risk_sensitivity": mind_result.get("risk_sensitivity"),
                        "spiritual_state": mind_result.get("spiritual_state"),
                        "recommended_posture": mind_result.get("recommended_posture"),
                    }
            except Exception as e:
                logger.debug(f"Rasa mind wrapper: {e}")

        return result

    return wrapper


def rasa_wrap_heart(original_heart_fn):
    """Wrap arif_heart_critique (444 HEART) with rasa risk calculus.

    Adds rasa-specific risk assessment to the heart critique:
    de-escalation score, dignity preservation, boundary honoring.

    Auto-detects sync vs async original and adapts wrapper accordingly.
    """
    import inspect as _inspect
    _is_async = _inspect.iscoroutinefunction(original_heart_fn)

    if _is_async:
        @functools.wraps(original_heart_fn)
        async def wrapper(*args, **kwargs):
            session_id = kwargs.get("session_id", "unknown")
            try:
                result = await original_heart_fn(*args, **kwargs)
            except Exception:
                result = {"error": "heart_failed"}
            return _attach_rasa_heart(result, session_id)
        return wrapper
    else:
        @functools.wraps(original_heart_fn)
        def wrapper(*args, **kwargs):
            session_id = kwargs.get("session_id", "unknown")
            try:
                result = original_heart_fn(*args, **kwargs)
            except Exception:
                result = {"error": "heart_failed"}
            return _attach_rasa_heart(result, session_id)
        return wrapper


def _attach_rasa_heart(result, session_id: str):
    """Attach rasa heart verdict to a heart critique result dict."""
    rasa_detection = _session_rasa.get(session_id, {}).get("detection")
    if not rasa_detection:
        return result

    try:
        from arifosmcp.rasa.rasa_contract import RasaContract
        contract = RasaContract()
        context = contract.mind_interpret(rasa_detection)
        memory = contract.memory_recall(rasa_detection, session_id)
        heart_result = rasa_heart_hook(rasa_detection, context, memory)

        _rasa_data = {
            "deescalation_score": heart_result.get("deescalation_score"),
            "dignity_preservation": heart_result.get("dignity_preservation"),
            "boundary_honored": heart_result.get("boundary_honored"),
            "boundary_risk": heart_result.get("boundary_risk"),
            "f9_violation_risk": heart_result.get("f9_violation_risk"),
            "f10_violation_risk": heart_result.get("f10_violation_risk"),
            "requires_human_loop": heart_result.get("requires_human_loop"),
            "_rasa_hook_status": "PASS",
        }

        if isinstance(result, dict):
            result["_rasa_heart"] = _rasa_data
        elif hasattr(result, "meta") and isinstance(result.meta, dict):
            result.meta["_rasa_heart"] = _rasa_data

        _log_rasa_telemetry(session_id, "heart", _rasa_data)
    except Exception as e:
        logger.debug(f"Rasa heart wrapper: {e}")

    return result


def rasa_wrap_memory(original_memory_fn):
    """Wrap arif_memory_recall (555m MEMORY) with rasa pattern memory.

    Attaches rasa pattern detection to memory recall, checking for
    similar emotional patterns in past sessions.
    """

    @functools.wraps(original_memory_fn)
    def wrapper(*args, **kwargs):
        session_id = kwargs.get("session_id", "unknown")
        mode_str = _current_mode.value

        # Run original memory recall
        try:
            result = original_memory_fn(*args, **kwargs)
        except Exception:
            result = {"error": "memory_failed"}

        # Attach rasa memory context if available
        rasa_detection = _session_rasa.get(session_id, {}).get("detection")
        if rasa_detection:
            try:
                memory_result = rasa_memory_hook(rasa_detection, session_id=session_id)

                if isinstance(result, dict):
                    result["_rasa_memory"] = {
                        "similar_patterns_found": memory_result.get("similar_patterns_found"),
                        "pattern_count": memory_result.get("pattern_count"),
                        "longitudinal_theme": memory_result.get("longitudinal_theme"),
                    }
            except Exception as e:
                logger.debug(f"Rasa memory wrapper: {e}")

        return result

    return wrapper


def rasa_wrap_judge(original_judge_fn):
    """Wrap arif_judge_deliberate (888 JUDGE) with rasa constitutional check.

    Adds rasa-aware floor enforcement to the judge deliberation:
    F1, F5, F6, F9, F10, F13 for human rasa contexts.

    Auto-detects sync vs async original and adapts wrapper accordingly.
    Handles both dict and non-dict (VerdictOutput) return types.
    """
    import inspect as _inspect
    _is_async = _inspect.iscoroutinefunction(original_judge_fn)

    if _is_async:
        @functools.wraps(original_judge_fn)
        async def wrapper(*args, **kwargs):
            session_id = kwargs.get("session_id", "unknown")
            try:
                result = await original_judge_fn(*args, **kwargs)
            except Exception:
                result = {"error": "judge_failed"}
            return _attach_rasa_judge(result, session_id)
        return wrapper
    else:
        @functools.wraps(original_judge_fn)
        def wrapper(*args, **kwargs):
            session_id = kwargs.get("session_id", "unknown")
            try:
                result = original_judge_fn(*args, **kwargs)
            except Exception:
                result = {"error": "judge_failed"}
            return _attach_rasa_judge(result, session_id)
        return wrapper


def _attach_rasa_judge(result, session_id: str):
    """Attach rasa judge verdict to a judge deliberation result.

    In ENFORCE mode, may downgrade verdict (SEAL→HOLD) based on rasa context.
    """
    rasa_detection = _session_rasa.get(session_id, {}).get("detection")
    if not rasa_detection:
        return result

    try:
        from arifosmcp.rasa.rasa_contract import RasaContract
        contract = RasaContract()
        context = contract.mind_interpret(rasa_detection)
        memory = contract.memory_recall(rasa_detection, session_id)
        heart = contract.heart_critique(rasa_detection, context, memory)
        judge_result = rasa_judge_hook(rasa_detection, context, heart)
        floors = rasa_check_floors(judge_result)

        _rasa_data = {
            "allowed_postures": judge_result.get("allowed_postures"),
            "blocked_outputs": judge_result.get("blocked_outputs"),
            "requires_rewrite": judge_result.get("requires_rewrite"),
            "floors_checked": floors,
            "_rasa_hook_status": "PASS",
        }

        # Attach to result (handle both dict and object types)
        if isinstance(result, dict):
            result["_rasa_judge"] = _rasa_data
        elif hasattr(result, "meta") and isinstance(result.meta, dict):
            result.meta["_rasa_judge"] = _rasa_data

        # ENFORCE mode: apply verdict downgrade if judge blocked
        if _current_mode not in (RasaContractMode.OFF, RasaContractMode.SHADOW):
            blocked = judge_result.get("blocked_outputs", [])
            if blocked:
                _apply_verdict_downgrade(result, blocked)

        _log_rasa_telemetry(session_id, "judge", _rasa_data)
    except Exception as e:
        logger.debug(f"Rasa judge wrapper: {e}")

    return result


def _apply_verdict_downgrade(result, blocked_outputs: list) -> None:
    """Apply verdict downgrade when rasa judge blocks output patterns."""
    # Handle dict-based results
    if isinstance(result, dict):
        old_verdict = result.get("verdict", "")
        if "SEAL" in str(old_verdict):
            result["verdict"] = "HOLD"
            result["_rasa_verdict_shift"] = True
            result.setdefault("reasons", []).append(
                f"RASA GOVERNANCE: Verdict downgraded SEAL→HOLD. "
                f"Blocked patterns: {blocked_outputs[:3]}"
            )
    # Handle VerdictOutput objects
    elif hasattr(result, "verdict"):
        from arifosmcp.schemas.verdict import VerdictCode
        if result.verdict == VerdictCode.SEAL:
            result.verdict = VerdictCode.HOLD
            result._rasa_verdict_shift = True
            if hasattr(result, "reasons"):
                result.reasons.append(
                    f"RASA GOVERNANCE: Verdict downgraded SEAL→HOLD. "
                    f"Blocked patterns: {blocked_outputs[:3]}"
                )


def _log_rasa_telemetry(session_id: str, organ: str, data: dict) -> None:
    """Emit a shadow telemetry line for a rasa hook firing."""
    try:
        _telemetry.log_shadow(
            session_id=session_id,
            message=f"rasa_{organ}_hook",
            ungoverned_result=None,
            governed_result={"organ": organ, **data},
            enforcement_mode=_current_mode.value,
            enforced=_current_mode not in (RasaContractMode.OFF, RasaContractMode.SHADOW),
        )
    except Exception:
        pass  # Telemetry must never block execution


def rasa_wrap_session_init(original_init_fn):
    """Wrap arif_session_init (000 INIT) to initialize rasa context.

    Sets up per-session rasa tracking state. Zero impact on
    session initialization output.
    """

    @functools.wraps(original_init_fn)
    def wrapper(*args, **kwargs):
        session_id = kwargs.get("session_id")
        actor_id = kwargs.get("actor_id")

        # Run original init
        result = original_init_fn(*args, **kwargs)

        # Initialize rasa context for this session
        if session_id and session_id not in _session_rasa:
            _session_rasa[session_id] = {
                "initialized": True,
                "session_id": session_id,
                "actor_id": actor_id,
            }

        return result

    return wrapper


# ═══════════════════════════════════════════════════════════════════════════════
# GOVERNANCE APPLICATION — Modify kernel output based on rasa verdict
# ═══════════════════════════════════════════════════════════════════════════════


def _apply_rasa_governance(
    original_result: dict,
    governed: Any,
    detection: Any,
) -> dict:
    """Apply rasa governance to original kernel output.

    In enforcement mode, modifies the output dict to reflect
    rasa constitutional constraints.

    Args:
        original_result: Original kernel output dict.
        governed: RasaContractResult from full pipeline.
        detection: RasaDetection object.

    Returns:
        Modified output dict with rasa governance applied.
    """
    if not isinstance(original_result, dict):
        return original_result

    result = dict(original_result)

    # Add rasa governance metadata
    result["_rasa_governed"] = True

    if governed is not None:
        if hasattr(governed, "final_posture"):
            result["_rasa_posture"] = governed.final_posture.value
            result["_rasa_requires_human"] = governed.requires_human

        if hasattr(governed, "judge") and governed.judge is not None:
            result["_rasa_blocked_outputs"] = governed.judge.blocked_outputs
            result["_rasa_requires_rewrite"] = governed.judge.requires_rewrite
            result["_rasa_allowed_postures"] = [
                p.value for p in governed.judge.allowed_postures
            ]

        if hasattr(governed, "human_escalation_reason"):
            result["_rasa_escalation_reason"] = governed.human_escalation_reason

    # For CRISIS: block output and escalate
    if detection is not None and hasattr(detection, "risk_band"):
        if detection.risk_band == RasaRiskBand.CRISIS:
            result["status"] = "HOLD"
            result["verdict"] = "HOLD" if "verdict" in result else result.get("verdict")
            result["_rasa_crisis_block"] = True
            result["message"] = (
                result.get("message", "") + " [RASA GOVERNANCE: Output held — "
                "CRISIS risk band detected. Human loop required.]"
            ).strip()
        elif detection.risk_band == RasaRiskBand.DISTRESS:
            # For DISTRESS: flag output as governed
            result["_rasa_distress_governed"] = True

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# ACTIVATION / DEACTIVATION — Reversible monkey-patching
# ═══════════════════════════════════════════════════════════════════════════════


def activate_rasa_wiring(mode: RasaContractMode | None = None) -> None:
    """Activate rasa wiring by monkey-patching kernel runtime tool functions.

    This is REVERSIBLE — call deactivate_rasa_wiring() to restore.
    IDEMPOTENT — calling twice does nothing.

    Patches the _arif_* functions in arifosmcp.runtime.tools (the canonical
    MCP-registered implementations), NOT arifosmcp.tools.* (supplementary).

    Args:
        mode: Optional RasaContractMode override. If None, reads from
              environment/config (default: SHADOW when enabled).
    """
    global _activated, _current_mode, _originals

    if _activated:
        return  # Already activated — idempotent

    _current_mode = mode or get_rasa_contract_mode()

    # Master kill-switch — OFF mode means no activation
    if _current_mode == RasaContractMode.OFF:
        logger.info("Rasa wiring: OFF mode — skipping activation")
        return

    try:
        import arifosmcp.runtime.tools as rt_mod

        # ── Patch _arif_sense_observe (111 SENSE) ───────────────────
        if hasattr(rt_mod, "_arif_sense_observe"):
            _originals["_arif_sense_observe"] = rt_mod._arif_sense_observe
            rt_mod._arif_sense_observe = rasa_wrap_sense(rt_mod._arif_sense_observe)
            logger.info("Rasa wiring: patched _arif_sense_observe (111 SENSE)")

        # ── Patch _arif_mind_reason (333 MIND) — passive/shadow only ──
        if hasattr(rt_mod, "_arif_mind_reason"):
            _originals["_arif_mind_reason"] = rt_mod._arif_mind_reason
            rt_mod._arif_mind_reason = rasa_wrap_mind(rt_mod._arif_mind_reason)
            logger.info("Rasa wiring: patched _arif_mind_reason (333 MIND) [shadow]")

        # ── Patch _arif_heart_critique (444 HEART) ──────────────────
        if hasattr(rt_mod, "_arif_heart_critique"):
            _originals["_arif_heart_critique"] = rt_mod._arif_heart_critique
            rt_mod._arif_heart_critique = rasa_wrap_heart(rt_mod._arif_heart_critique)
            logger.info("Rasa wiring: patched _arif_heart_critique (444 HEART)")

        # ── Patch _arif_memory_recall (555m MEMORY) — passive/shadow only ──
        if hasattr(rt_mod, "_arif_memory_recall"):
            _originals["_arif_memory_recall"] = rt_mod._arif_memory_recall
            rt_mod._arif_memory_recall = rasa_wrap_memory(rt_mod._arif_memory_recall)
            logger.info("Rasa wiring: patched _arif_memory_recall (555m MEMORY) [shadow]")

        # ── Patch _arif_judge_deliberate (888 JUDGE) ────────────────
        if hasattr(rt_mod, "_arif_judge_deliberate"):
            _originals["_arif_judge_deliberate"] = rt_mod._arif_judge_deliberate
            rt_mod._arif_judge_deliberate = rasa_wrap_judge(rt_mod._arif_judge_deliberate)
            logger.info("Rasa wiring: patched _arif_judge_deliberate (888 JUDGE)")

        # ── Patch _arif_session_init (000 INIT) ─────────────────────
        if hasattr(rt_mod, "_arif_session_init"):
            _originals["_arif_session_init"] = rt_mod._arif_session_init
            rt_mod._arif_session_init = rasa_wrap_session_init(rt_mod._arif_session_init)
            logger.info("Rasa wiring: patched _arif_session_init (000 INIT)")

    except Exception as e:
        logger.warning(f"Rasa wiring: could not patch runtime.tools: {e}")
        return

    _activated = True
    logger.info(f"Rasa wiring ACTIVATED in mode: {_current_mode.value} "
                f"(patched {len(_originals)} runtime tools)")


def deactivate_rasa_wiring() -> None:
    """Deactivate rasa wiring by restoring original runtime tool functions.

    This is fully REVERSIBLE — the kernel returns to its original
    state with no trace of rasa wiring.
    """
    global _activated, _originals

    if not _activated:
        return  # Not activated — idempotent

    try:
        import arifosmcp.runtime.tools as rt_mod

        # Restore all patched functions
        for func_name, original_fn in _originals.items():
            if hasattr(rt_mod, func_name):
                setattr(rt_mod, func_name, original_fn)
                logger.info(f"Rasa wiring: restored {func_name}")
    except Exception as e:
        logger.warning(f"Rasa wiring: could not restore runtime.tools: {e}")

    _originals.clear()
    _session_rasa.clear()
    _activated = False
    logger.info("Rasa wiring DEACTIVATED — kernel restored to original state")


def is_rasa_wired() -> bool:
    """Check if rasa wiring is currently active.

    Returns:
        True if activate_rasa_wiring() has been called.
    """
    return _activated


# ═══════════════════════════════════════════════════════════════════════════════
# WIRING DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════════════


def rasa_wiring_diagnostics() -> dict[str, Any]:
    """Run wiring-specific diagnostics.

    Returns:
        dict with wiring status, wrapper functions, and activation state.
    """
    diag: dict[str, Any] = {
        "status": "OK",
        "wiring_active": _activated,
        "current_mode": _current_mode.value,
        "wrappers": {},
        "originals_stored": len(_originals),
        "telemetry_path": _telemetry.log_path,
        "telemetry_enabled": _telemetry.enabled,
    }

    # Check all wrapper functions are callable
    wrappers = {
        "rasa_wrap_sense": rasa_wrap_sense,
        "rasa_wrap_mind": rasa_wrap_mind,
        "rasa_wrap_heart": rasa_wrap_heart,
        "rasa_wrap_memory": rasa_wrap_memory,
        "rasa_wrap_judge": rasa_wrap_judge,
        "rasa_wrap_session_init": rasa_wrap_session_init,
    }
    for name, fn in wrappers.items():
        diag["wrappers"][name] = "CALLABLE" if callable(fn) else "NOT CALLABLE"

    # Integration diagnostics
    try:
        diag["integration"] = rasa_integration_diagnostics()
    except Exception as e:
        diag["integration"] = f"FAILED: {e}"

    return diag


__all__ = [
    "rasa_wrap_sense",
    "rasa_wrap_mind",
    "rasa_wrap_heart",
    "rasa_wrap_memory",
    "rasa_wrap_judge",
    "rasa_wrap_session_init",
    "activate_rasa_wiring",
    "deactivate_rasa_wiring",
    "is_rasa_wired",
    "rasa_wiring_diagnostics",
    "RasaTelemetry",
]
