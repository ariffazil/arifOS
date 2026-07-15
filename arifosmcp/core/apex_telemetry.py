"""
arifosmcp/core/apex_telemetry.py — APEX Telemetry Pipeline (ATP) Gate
═══════════════════════════════════════════════════════════════════════
DITEMPA BUKAN DIBERI

The ATP is the QDF (Quantized Decision Function) gate that sits BEFORE any
tool executes in arifOS. Currently the 7 canonical APEX scalars
(G, C_dark, W³, κ_r, ψ_le, peace², QDF) are computed as diagnostic logs.

ATP promotes them to a LIVE EXECUTION GATE.

Architecture
------------
Every arif_forge_execute call (stage 010) will pass through ATP before
executing. (Wiring is TASK-P2-02, F13-gated — DO NOT wire here.)

Gate condition
--------------
    QDF = G × (1 - C_dark) × W³ × κ_r × ψ_le

    PASS  (verdict = SEAL) iff:
        QDF   ≥ 0.70
        C_dark < 0.30
        W³    ≥ 0.95

    FAIL  (verdict = HOLD):
        any scalar undefined / NaN / Inf / "UNMEASURED"
        C_dark ≥ 0.30
        W³    < 0.95
        QDF   < 0.70

    VOID is NEVER emitted by this evaluator. Scalar measurement failure
    (UNMEASURED / NaN) is HOLD, not VOID — per F9 anti-hantu doctrine:
    "Measurement failure ≠ hard floor." This is a deliberate distinction
    so that telemetry outages cannot manufacture a constitutional breach.

Constitutional floors enforced
------------------------------
F1  AMANAH      — pure function. No mutation, no side effects. The caller
                  controls state; this evaluator only reads the input dict
                  and returns a verdict envelope. Reversibility preserved
                  by construction.
F2  TRUTH       — every input value is validated as a finite real number.
                  No coercion of strings, NaN, or Inf into numbers.
F9  ANTI-HANTU  — never fabricate missing scalars. UNMEASURED inputs
                  become HOLD, never a fabricated 0.0 default that would
                  silently PASS the gate.
F11 AUDIT       — evaluator returns a `reason` string for the caller's
                  audit trail. ATP does NOT write to VAULT999 directly;
                  that is the caller's responsibility via arif_vault_seal.
F13 SOVEREIGN   — scaffold only (F1/F11 gates). Wiring ATP to
                  arif_forge_execute (TASK-P2-02) requires explicit F13
                  approval from Arif. The scaffold does not auto-wire.

NON-CONSTITUTIONAL NOTE
-----------------------
peace² is a canonical APEX scalar (one of the 7) but is NOT part of the
QDF formula above (per the canonical APEX equation set sealed 2026-07-15
in bbb5075bd). peace² is required to be PRESENT in the input (F9: no
fabrication) but does not enter the composite QDF. A future QDF revision
may wire peace² in.

Author  : 888-APEX / Claude Code perspective
Task    : TASK-P2-01 (scaffold only; wiring is F13-gated P2-02)
Epoch   : 2026-07-15
"""

from __future__ import annotations

import math
from typing import Any

__all__ = [
    "ApexTelemetryEvaluator",
    "ATP_PASS_THRESHOLDS",
    "ATP_REQUIRED_SCALARS",
    "AtpResult",
]


# ─── Threshold constants — single source of truth for the ATP gate ────────
# These are the EXPLICIT thresholds mandated by TASK-P2-01.
# Any future tuning requires F13 SOVEREIGN approval.

ATP_PASS_THRESHOLDS: dict[str, float] = {
    "qdf_min": 0.70,  # Composite QDF lower bound
    "c_dark_max": 0.30,  # Anti-hantu ceiling (F9)
    "w3_min": 0.95,  # Tri-witness floor (F3)
}

# Canonical input keys — all seven must be present (F9: no fabrication).
# Two spelling variants are accepted to absorb the federation's existing
# lowercase and mathematical notations, then normalized internally.
ATP_REQUIRED_SCALARS: tuple[str, ...] = (
    "G",
    "C_dark",
    "W3",
    "kappa_r",
    "psi_le",
    "peace_squared",
)


# Type alias for the evaluate() return shape.
AtpResult = dict[str, Any]


# ─── Internal helpers ─────────────────────────────────────────────────────


def _is_measurable(value: Any) -> bool:
    """True iff value is a finite real number (F2/F9: no fabrication).

    Rejects:
        None
        strings (incl. "UNMEASURED")
        NaN, +Inf, -Inf
        bool (subclass of int but semantically a flag, not a scalar)
        non-numeric containers (dict, list, tuple, set)
    """
    if value is None or isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return math.isfinite(float(value))
    # Strings, dicts, lists, etc. — never silently coerced.
    return False


def _coerce_scalar(
    apex_scalars: dict[str, Any],
    candidates: tuple[str, ...],
) -> float | None:
    """Return the first measurable scalar found under any candidate key.

    Returns None if no candidate key holds a measurable value.
    """
    for key in candidates:
        if key not in apex_scalars:
            continue
        if _is_measurable(apex_scalars[key]):
            return float(apex_scalars[key])
    return None


def _all_undefined(apex_scalars: dict[str, Any]) -> bool:
    """True iff NONE of the required scalars is measurable.

    Used to distinguish the "total telemetry outage" case (HOLD with
    explicit "all undefined" reason) from the "one scalar missing" case
    (HOLD with explicit per-scalar reason). Both are HOLD; the reason
    string differs for audit clarity.
    """
    groups: tuple[tuple[str, ...], ...] = (
        ("G", "G_star"),
        ("C_dark", "c_dark"),
        ("W3", "w3"),
        ("kappa_r",),
        ("psi_le",),
        ("peace_squared", "peace2"),
    )
    return all(_coerce_scalar(apex_scalars, g) is None for g in groups)


# ─── Public evaluator ────────────────────────────────────────────────────


class ApexTelemetryEvaluator:
    """Pure evaluator for the APEX Telemetry Pipeline (ATP) QDF gate.

    No I/O, no globals mutated, no side effects. Each call is a pure
    function of its input dict. F1 AMANAH preserved by construction:
    the input dict is never mutated; the returned dict is fresh.

    Wiring this evaluator into arif_forge_execute is TASK-P2-02 and is
    F13 SOVEREIGN-gated. The scaffold does NOT auto-wire.
    """

    def evaluate(self, apex_scalars: dict[str, Any]) -> AtpResult:
        """Evaluate the QDF gate for one arif_forge_execute call.

        Parameters
        ----------
        apex_scalars : dict
            The 7 canonical APEX scalars. Accepted key spellings:
                G               | G_star
                C_dark          | c_dark
                W3              | w3
                kappa_r
                psi_le
                peace_squared   | peace2
            Values may be int, float, None, or the string "UNMEASURED".
            Any other type is rejected as malformed (HOLD).

        Returns
        -------
        AtpResult : dict
            pass     (bool)   — True iff the gate authorizes execution.
            qdf      (float)  — recomputed QDF value, or NaN if uncomputable.
            verdict  (str)    — "SEAL" or "HOLD". Never "VOID".
            reason   (str)    — audit-trail message for the caller.

        Constitutional
        --------------
        F1  AMANAH    — pure function; no mutation of inputs.
        F2  TRUTH     — every value numeric-validated; no silent coercion.
        F9  ANTI-HANTU — UNMEASURED / NaN / Inf → HOLD, never fabricated
                        to 0.0 to mask the failure.
        F11 AUDIT     — caller records `reason` to VAULT999 via
                        arif_vault_seal (ATP does not write directly).
        """
        # ── Step 1: detect total-telemetry-outage first (test case 5) ──
        # Distinguishing "all 7 undefined" from "1 of 7 undefined" lets
        # the audit trail surface the right operator action: re-acquire
        # all telemetry vs. re-acquire one channel.
        if _all_undefined(apex_scalars):
            return {
                "pass": False,
                "qdf": float("nan"),
                "verdict": "HOLD",
                "reason": (
                    "ATP-HOLD: all 7 APEX scalars undefined. Scalar "
                    "measurement failure is HOLD (not VOID). "
                    "Re-acquire telemetry before forging."
                ),
            }

        # ── Step 2: extract each required scalar (F9: never fabricate) ─
        # APEX scalars use canonical mathematical notation by design.
        G = _coerce_scalar(apex_scalars, ("G", "G_star"))  # noqa: N806
        C_dark = _coerce_scalar(apex_scalars, ("C_dark", "c_dark"))  # noqa: N806
        W3 = _coerce_scalar(apex_scalars, ("W3", "w3"))  # noqa: N806
        kappa_r = _coerce_scalar(apex_scalars, ("kappa_r",))
        psi_le = _coerce_scalar(apex_scalars, ("psi_le",))
        peace_sq = _coerce_scalar(apex_scalars, ("peace_squared", "peace2"))

        missing: list[str] = []
        if G is None:
            missing.append("G")
        if C_dark is None:
            missing.append("C_dark")
        if W3 is None:
            missing.append("W3")
        if kappa_r is None:
            missing.append("kappa_r")
        if psi_le is None:
            missing.append("psi_le")
        if peace_sq is None:
            missing.append("peace_squared")

        if missing:
            return {
                "pass": False,
                "qdf": float("nan"),
                "verdict": "HOLD",
                "reason": (
                    f"ATP-HOLD: scalar measurement failure on "
                    f"{', '.join(missing)}. F9 anti-hantu: never fabricate "
                    "missing scalars. Re-acquire telemetry before forging."
                ),
            }

        # At this point all 6 required scalars are measurable floats.
        # Narrow types for the type checker.
        assert G is not None
        assert C_dark is not None
        assert W3 is not None
        assert kappa_r is not None
        assert psi_le is not None
        assert peace_sq is not None

        # ── Step 3: recompute QDF (never trust an input QDF value) ────
        # The QDF input key is accepted but ignored — F2 TRUTH / F9
        # anti-hantu: never trust a pre-computed composite.
        qdf = G * (1.0 - C_dark) * W3 * kappa_r * psi_le

        if not math.isfinite(qdf):
            return {
                "pass": False,
                "qdf": float("nan"),
                "verdict": "HOLD",
                "reason": (
                    "ATP-HOLD: QDF non-finite (overflow/NaN). Numerical "
                    "instability in scalar feed. Re-acquire telemetry."
                ),
            }

        # ── Step 4: enforce hard floors ────────────────────────────────
        # C_dark floor (F9 anti-hantu) is checked BEFORE the QDF composite
        # because anti-hantu is a constitutional floor; QDF is composite.
        if C_dark >= ATP_PASS_THRESHOLDS["c_dark_max"]:
            return {
                "pass": False,
                "qdf": qdf,
                "verdict": "HOLD",
                "reason": (
                    f"ATP-HOLD: C_dark={C_dark:.4f} >= 0.30 "
                    "(F9 anti-hantu ceiling). Shadow score too high; "
                    "forging blocked."
                ),
            }

        # W³ floor (F3 witness) — same precedence.
        if W3 < ATP_PASS_THRESHOLDS["w3_min"]:
            return {
                "pass": False,
                "qdf": qdf,
                "verdict": "HOLD",
                "reason": (
                    f"ATP-HOLD: W3={W3:.4f} < 0.95 (F3 witness floor). "
                    "Tri-witness consensus insufficient; forging blocked."
                ),
            }

        # ── Step 5: enforce composite QDF gate ─────────────────────────
        if qdf < ATP_PASS_THRESHOLDS["qdf_min"]:
            return {
                "pass": False,
                "qdf": qdf,
                "verdict": "HOLD",
                "reason": (
                    f"ATP-HOLD: QDF={qdf:.4f} < 0.70 (composite gate). "
                    "Governed intelligence potential below execution "
                    "threshold; forging blocked."
                ),
            }

        # ── Step 6: all gates cleared → SEAL ──────────────────────────
        return {
            "pass": True,
            "qdf": qdf,
            "verdict": "SEAL",
            "reason": (
                f"ATP-SEAL: QDF={qdf:.4f} >= 0.70, "
                f"C_dark={C_dark:.4f} < 0.30, W3={W3:.4f} >= 0.95. "
                "All seven APEX scalars within band."
            ),
        }
