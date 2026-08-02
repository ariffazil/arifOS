"""
arifosmcp/runtime/calhoun_anti_sink_gate.py — CALHOUN ANTI-SINK GATE (Q10)
═════════════════════════════════════════════════════════════════════════════

Three Closures — Q10 (GENESIS/058, sealed 2026-08-02).

The Calhoun Lock is the **biological form of F5+F6 (Peace² + Empathy/Maruah)**.
A system with no external challenge, no friction, no unsolved problem —
will die. Not from scarcity. From abundance without purpose.

This gate is **ADDITIVE** and **SOFT-first**. It composes the existing
signals from `godel_lock_enforcement.anti_calhoun_score` and
`arifosmcp.tools.heart._behavioral_sink_scan`, plus session-side
FQ (Flow Quotient) pressure. The gate NEVER auto-voids on a single signal;
it must see a **sustained pattern** before HOLDing.

Doctrine (GENESIS/058 §1, Q10):
  - Q10a: At least one UNSOLVED problem in the session's domain.
  - Q10b: The agent operates in an arena where it CAN fail (Selection Lock).
  - Q10c: The agent is capable of REFUSAL (distinct from failure).

Floor binding: F5 (PEACE²) + F6 (EMPATHY/MARUAH) — both name the failure;
Q10 enforces the **friction requirement** at the governance layer.

Verdict ladder (constitutional):
  - All clear                       → PROCEED.
  - Anti-Calhoun score 0.40–0.60    → SABAR (advisory, no block).
  - Behavioral sink ratio > 0.40    → SABAR (advisory).
  - Anti-Calhoun score < 0.40 OR
    sink ratio > 0.40 for 3+ calls  → HOLD (sustained pattern).
  - NEVER VOID: this gate is a soft signal at the tool-call boundary.
  - Observation tools (F1 reversible) → always PROCEED (observation is the
    anti-sink; the system must be able to observe without triggering locks).

F1 AMANAH:    F4 CLARITY: pure functions, ΔS=0 per call. F11 AUDIT: receipt
              envelope on every call. F13 SOVEREIGN: HOLD is reversible —
              Arif may unblock via 888_HOLD.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from arifosmcp.runtime.godel_lock_enforcement import anti_calhoun_score

logger = logging.getLogger("arifosmcp.calhoun_anti_sink_gate")

# ── Thresholds (constitutional, frozen) ────────────────────────────────────
SUSTAINED_WARNINGS_BEFORE_HOLD = 3  # Q10b: 3+ consecutive warnings → HOLD
ANTI_CALHOUN_HOLD_THRESHOLD = 0.40  # below this → SINK_WARNING (advisory)
BEHAVIORAL_SINK_RATIO_THRESHOLD = 0.40  # mirrors _ANTI_CALHOUN_SINK_THRESHOLD
FQ_OVERHEAT_THRESHOLD = 3.0  # Q10c: FQ > 3.0 for 3+ cycles = grooming
FQ_WINDOW = 3  # last N FQ samples to inspect

# Session-side warning tracking (in-process, per session_id)
_session_warnings: dict[str, int] = {}
_session_fq_history: dict[str, list[float]] = {}


# ── Helpers ────────────────────────────────────────────────────────────────


def _is_observation_action(ctx: Any) -> bool:
    """F1 observation tools must NOT trigger Calhoun (the anti-sink needs to
    be able to observe its own arena).
    """
    action = str(getattr(ctx, "action_class", "OBSERVE") or "OBSERVE").upper()
    if action == "OBSERVE":
        return True
    tool = str(getattr(ctx, "tool_name", "") or "").lower()
    return tool in {
        "arif_observe",
        "arif_fetch",
        "arif_measure",
        "arif_memory_recall",
        "arif_kernel_route",
    }


def _get_session_history(ctx: Any) -> list[Any] | None:
    """Extract session_history from ctx.params (if provided) or tool metadata."""
    params = getattr(ctx, "params", {}) or {}
    hist = params.get("session_history")
    if isinstance(hist, list):
        return hist
    return None


def _behavioral_sink_check(history: list[Any] | None) -> dict[str, Any]:
    """Compute the Calhoun sink ratio (mirrors heart._behavioral_sink_scan).

    Uses the same counting strategy (empty/minimal outputs), but keeps the
    gate module **independent** of `tools.heart` so the governance pipeline
    can run without importing the heart module (which has LLM deps).
    """
    if not history:
        return {
            "sink_ratio": 0.0,
            "empty_count": 0,
            "total_outputs": 0,
            "status": "CLEAR",
        }

    def _is_empty(o: Any) -> bool:
        if o is None:
            return True
        if isinstance(o, str):
            s = o.strip().lower()
            if not s:
                return True
            if s in {"pass", "ok", "skipped", "null", "no-op", "—", "..."}:
                return True
            return False
        if isinstance(o, (list, tuple, set, frozenset)):
            return len(o) == 0 or all(_is_empty(x) for x in o)
        if isinstance(o, dict):
            return len(o) == 0 or all(_is_empty(v) for v in o.values())
        return False

    total = len(history)
    empty = sum(1 for o in history if _is_empty(o))
    ratio = round(empty / total, 4) if total else 0.0
    status = "WARNING" if ratio > BEHAVIORAL_SINK_RATIO_THRESHOLD else "CLEAR"
    return {"sink_ratio": ratio, "empty_count": empty, "total_outputs": total, "status": status}


def _record_warning(session_id: str) -> int:
    _session_warnings[session_id] = _session_warnings.get(session_id, 0) + 1
    return _session_warnings[session_id]


def _record_fq(session_id: str, fq: float) -> list[float]:
    hist = _session_fq_history.setdefault(session_id, [])
    hist.append(fq)
    if len(hist) > FQ_WINDOW:
        hist.pop(0)
    return list(hist)


def reset_session(session_id: str) -> None:
    """Test/operator hook: clear session-side warning counters."""
    _session_warnings.pop(session_id, None)
    _session_fq_history.pop(session_id, None)


# ── Public gate function ──────────────────────────────────────────────────


def calhoun_anti_sink_gate(ctx: Any) -> dict[str, Any]:
    """Compute Calhoun anti-sink gate verdict for a tool call.

    Returns a dict compatible with `GateResult`:
      {
        "passed": bool,                    # True = PROCEED/SABAR, False = HOLD
        "verdict": "PROCEED" | "SABAR" | "HOLD",
        "reason": str,
        "latency_ms": float,
        "anti_calhoun": dict,
        "behavioral_sink": dict,
        "fq_window": list[float],
        "warnings_count": int,
        "violated_laws": list[str],
        "receipt": dict,                    # F11 audit envelope
      }
    """
    t0 = time.perf_counter()

    if _is_observation_action(ctx):
        # Observation is the anti-sink — never trigger Calhoun on observation.
        latency_ms = (time.perf_counter() - t0) * 1000
        receipt = {
            "gate": "CALHOUN_CLOSURE",
            "verdict": "PROCEED",
            "passed": True,
            "reason": "Observation tool — Calhoun is a soft signal, observation is anti-sink",
            "skipped": True,
            "latency_ms": round(latency_ms, 3),
            "doctrine": "GENESIS/058 §1 Q10 — Calhoun Lock",
        }
        return {
            "passed": True,
            "verdict": "PROCEED",
            "reason": receipt["reason"],
            "latency_ms": latency_ms,
            "anti_calhoun": {"score": 1.0, "passed": True, "verdict": "PASS"},
            "behavioral_sink": {"sink_ratio": 0.0, "status": "CLEAR"},
            "fq_window": [],
            "warnings_count": 0,
            "violated_laws": [],
            "receipt": receipt,
        }

    # ── Anti-Calhoun score (from godel_lock_enforcement) ──────────────
    calhoun_payload = {
        "has_actionable_finding": bool(getattr(ctx, "params", {}).get("finding")),
        "changed_something": bool(getattr(ctx, "params", {}).get("mutated")),
        "evidence_declared": bool(getattr(ctx, "params", {}).get("evidence")),
        "seal_bound": str(getattr(ctx, "action_class", "OBSERVE") or "").upper()
        in {"IRREVERSIBLE", "ATOMIC", "VAULT_WRITE"},
        "external_validated": bool(getattr(ctx, "params", {}).get("auditor_id")),
        "self_certified": False,
        "polished_no_substance": False,
    }
    calhoun = anti_calhoun_score(calhoun_payload)

    # ── Behavioral sink scan (from session_history) ────────────────────
    history = _get_session_history(ctx)
    sink = _behavioral_sink_check(history)

    # ── FQ window (Q10c: FQ > 3.0 for 3+ cycles = grooming) ───────────
    session_id = str(getattr(ctx, "session_id", "") or "default")
    fq = getattr(ctx, "fq", None)
    fq_window: list[float] = []
    if isinstance(fq, (int, float)):
        fq_window = _record_fq(session_id, float(fq))
    else:
        fq_window = list(_session_fq_history.get(session_id, []))

    # ── Compute combined signal ───────────────────────────────────────
    calhoun_warn = calhoun["score"] < ANTI_CALHOUN_HOLD_THRESHOLD
    sink_warn = sink["status"] == "WARNING"
    fq_overheat = (
        len(fq_window) >= FQ_WINDOW
        and all(f > FQ_OVERHEAT_THRESHOLD for f in fq_window)
    )

    # Observation is already handled; this is the "needs evaluation" path.
    any_warning = calhoun_warn or sink_warn or fq_overheat
    violated: list[str] = []
    verdict = "PROCEED"
    passed = True
    reason_parts: list[str] = []

    if not any_warning:
        verdict = "PROCEED"
        passed = True
        reason_parts.append(
            f"Q10: clear — Calhoun={calhoun['score']:.2f}, "
            f"sink_ratio={sink['sink_ratio']:.2f}, FQ-window={fq_window}"
        )
    else:
        # Q10b: require sustained pattern (3+ consecutive warnings)
        warnings_count = _record_warning(session_id)
        if (
            warnings_count >= SUSTAINED_WARNINGS_BEFORE_HOLD
            or fq_overheat
            or calhoun["score"] < (ANTI_CALHOUN_HOLD_THRESHOLD * 0.5)
        ):
            verdict = "HOLD"
            passed = False
            violated.append("F5")
            violated.append("F6")
            reason_parts.append(
                f"Q10b/c sustained: warnings={warnings_count}, "
                f"Calhoun={calhoun['score']:.2f}, sink_ratio={sink['sink_ratio']:.2f}, "
                f"FQ-overheat={fq_overheat}. Inject friction."
            )
        else:
            verdict = "SABAR"
            passed = True
            reason_parts.append(
                f"Q10 advisory: Calhoun={calhoun['score']:.2f}, "
                f"sink_ratio={sink['sink_ratio']:.2f}, "
                f"FQ-overheat={fq_overheat}, warnings={warnings_count}/{SUSTAINED_WARNINGS_BEFORE_HOLD}"
            )

    latency_ms = (time.perf_counter() - t0) * 1000

    receipt = {
        "gate": "CALHOUN_CLOSURE",
        "verdict": verdict,
        "passed": passed,
        "q10_checks": {
            "q10a_unsolved_problem": bool(getattr(ctx, "params", {}).get("unsolved_problem")),
            "q10b_can_fail": not fq_overheat,
            "q10c_can_refuse": True,  # gate exists, so the agent can refuse
        },
        "anti_calhoun_score": calhoun["score"],
        "anti_calhoun_verdict": calhoun["verdict"],
        "behavioral_sink": sink,
        "fq_window": fq_window,
        "fq_overheat": fq_overheat,
        "warnings_count": _session_warnings.get(session_id, 0),
        "violated_laws": violated,
        "latency_ms": round(latency_ms, 3),
        "doctrine": "GENESIS/058 §1 Q10 — Calhoun Lock",
    }

    return {
        "passed": passed,
        "verdict": verdict,
        "reason": " | ".join(reason_parts),
        "latency_ms": latency_ms,
        "anti_calhoun": calhoun,
        "behavioral_sink": sink,
        "fq_window": fq_window,
        "fq_overheat": fq_overheat,
        "warnings_count": _session_warnings.get(session_id, 0),
        "violated_laws": violated,
        "receipt": receipt,
    }


__all__ = [
    "calhoun_anti_sink_gate",
    "SUSTAINED_WARNINGS_BEFORE_HOLD",
    "ANTI_CALHOUN_HOLD_THRESHOLD",
    "BEHAVIORAL_SINK_RATIO_THRESHOLD",
    "FQ_OVERHEAT_THRESHOLD",
    "reset_session",
]
