"""
arifosmcp/runtime/godel_lock_gate.py — GÖDEL LOCK GATE (Q9 boot enforcement)
═════════════════════════════════════════════════════════════════════════════

Three Closures — Q9 (GENESIS/058, sealed 2026-08-02).

The Gödel Lock is the **logical form of F3 TRI-WITNESS**. A system complex
enough to be useful is complex enough to be wrong about itself. The only
cure is an **outside witness**.

This gate is **ADDITIVE**. It reuses the existing
`arifosmcp.runtime.godel_lock_enforcement` primitives (P0-1, P0-2, P1-1, P1-3)
and exposes them as a GovernancePipeline-compatible gate function.

Doctrine (GENESIS/058 §1, Q9):
  - Q9a: At least one outside witness for every SEAL.
  - Q9b: Witness ≠ same actor / same model / same reasoning chain.
  - Q9c: Every SEAL is linked to a FalsifiablePrediction (Reality Loop).

Verdict ladder:
  - OBSERVE / non-mutate actions → SABAR (advisory, no witness required).
  - SEAL-bound / IRREVERSIBLE / ATOMIC actions with Φ_external < 0.5 → HOLD.
  - SEAL-bound with auditor_validated=True → PROCEED.
  - Self-certification (caller == target_actor) → HOLD regardless of tier.

F1 AMANAH:    Reads existing state, no mutation. F2 TRUTH: phi_external is
              computed (not fabricated). F4 CLARITY: gate is pure-function;
              ΔS = 0 per call. F11 AUDIT: every verdict carries a receipt
              envelope. F13 SOVEREIGN: HOLD verdicts are advisory — Arif may
              override via 888_HOLD path.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from arifosmcp.runtime.godel_lock_enforcement import (
    anti_calhoun_score,
    compute_phi_external,
    validate_audit_result,
)

logger = logging.getLogger("arifosmcp.godel_lock_gate")

# ── Thresholds (constitutional, frozen) ────────────────────────────────────
SEAL_BOUND_PHI_MIN = 0.50  # Φ_external below this on SEAL → HOLD
PHI_SOVEREIGN_OVERRIDE = 0.85  # ≥ this → advisory can be waived

# Tools that require outside witness (Q9b — same actor cannot judge itself)
SELF_CERTIFYING_TOOLS = frozenset(
    {
        "arif_judge",
        "arifos_judge",
        "arif_seal",
        "arifos_seal",
        "arif_forge",  # when in self-certify mode
    }
)

# Tools that are SEAL-bound / IRREVERSIBLE (require external attestation)
SEAL_BOUND_ACTION_CLASSES = frozenset(
    {
        "IRREVERSIBLE",
        "ATOMIC",
        "VAULT_WRITE",
        "MUTATE",  # for governance purposes — MUTATE → consequential tier
    }
)


# ── Helpers ────────────────────────────────────────────────────────────────


def _is_self_certifying(ctx: Any) -> tuple[bool, str]:
    """Q9b: caller cannot judge themselves.

    Returns (is_self_certifying, reason). For SEAL-bound judge/seal calls,
    if the actor_id is the same as the target actor_id, the seal is
    self-referential and must be blocked.

    Extended (Gödel-Future, Lineage-as-Self): F3 TRI-WITNESS extension.
    Heritage: 04_DOCTRINES/f14_godel_future.md (rejected F14, absorbed into F3).
    If dreamer lineage intersects verifier lineage, the call is also
    self-certifying — even if actor_id differs. 5-line gate extension.
    """
    tool = str(getattr(ctx, "tool_name", "") or "")
    if tool not in SELF_CERTIFYING_TOOLS:
        return False, ""

    caller = str(getattr(ctx, "actor_id", "") or "").strip().lower()
    if not caller or caller == "anonymous":
        return False, ""

    params = getattr(ctx, "params", {}) or {}
    target = (
        params.get("actor_id")
        or params.get("target_actor")
        or params.get("candidate_actor")
        or params.get("subject_actor")
    )
    if target and str(target).strip().lower() == caller:
        return True, f"Q9b self-certification: actor='{caller}' matches target='{target}'"

    # ── Gödel-Future (Lineage-as-Self): F3 TRI-WITNESS extension — 5 lines ──
    # If dreamer lineage intersects verifier lineage, foreign witness required.
    l_d = set(params.get("lineage_reflection", []) or [])
    l_v = set(params.get("lineage_verifier", []) or [])
    if l_d and l_v and (l_d & l_v):
        return True, f"Gödel-Future: lineage intersection {l_d & l_v}"

    return False, ""


def _claim_severity_for_action(ctx: Any) -> str:
    """Map action_class to compute_phi_external severity tier.

    'seal_bound' for IRREVERSIBLE/ATOMIC, 'consequential' for MUTATE,
    'reasoning' for ANALYZE/SIMULATE, 'observation' for OBSERVE.
    """
    action = str(getattr(ctx, "action_class", "OBSERVE") or "OBSERVE").upper()
    if action in SEAL_BOUND_ACTION_CLASSES:
        return "seal_bound"
    if action in {"MUTATE", "EXTERNAL_SIDE_EFFECT", "EXECUTE"}:
        return "consequential"
    if action in {"ANALYZE", "SIMULATE", "PREPARE", "DRAFT"}:
        return "reasoning"
    return "observation"


def _auditor_validated(ctx: Any) -> bool | None:
    """Inspect ctx for explicit external auditor validation hint.

    Convention: params.auditor_validated (bool) or params.auditor_id (non-empty str).
    If neither → None (unknown, fall back to tier default).
    """
    params = getattr(ctx, "params", {}) or {}
    if "auditor_validated" in params:
        return bool(params["auditor_validated"])
    if params.get("auditor_id"):
        return True
    return None


# ── Public gate function (matches GovernancePipeline._gate_* signature) ──


def godel_lock_gate(ctx: Any) -> dict[str, Any]:
    """Compute Gödel Lock gate verdict for a tool call.

    Returns a dict compatible with `GateResult`:
      {
        "passed": bool,                  # True = PROCEED, False = HOLD
        "verdict": "PROCEED" | "SABAR" | "HOLD",
        "reason": str,
        "latency_ms": float,
        "phi_external": float,
        "phi_status": str,
        "claim_severity": str,
        "self_certified": bool,
        "violated_laws": list[str],
        "receipt": dict,                  # F11 audit envelope
      }

    OBSERVE / non-mutate actions:  verdict = "SABAR" (advisory), passed=True.
    SEAL-bound with Φ_external < SEAL_BOUND_PHI_MIN:  verdict = "HOLD", passed=False.
    SEAL-bound with Φ_external ≥ threshold:          verdict = "PROCEED", passed=True.
    Self-certification (caller == target):          verdict = "HOLD", passed=False.
    """
    t0 = time.perf_counter()

    severity = _claim_severity_for_action(ctx)
    auditor = _auditor_validated(ctx)
    phi = compute_phi_external(claim_severity=severity, auditor_validated=auditor)

    self_cert, self_reason = _is_self_certifying(ctx)
    action_class = str(getattr(ctx, "action_class", "OBSERVE") or "OBSERVE").upper()
    is_seal_bound = action_class in SEAL_BOUND_ACTION_CLASSES

    # F2 TRUTH: also feed anti_calhoun if we have any audit-style fields in params
    calhoun_payload = {
        "has_actionable_finding": bool(getattr(ctx, "params", {}).get("finding")),
        "changed_something": bool(getattr(ctx, "params", {}).get("mutated")),
        "evidence_declared": bool(getattr(ctx, "params", {}).get("evidence")),
        "seal_bound": is_seal_bound,
        "external_validated": bool(auditor),
        "self_certified": self_cert,
        "polished_no_substance": False,
    }
    calhoun = anti_calhoun_score(calhoun_payload)

    # ── Verdict ladder ──────────────────────────────────────────────────
    violated: list[str] = []
    verdict = "PROCEED"
    passed = True
    reason_parts: list[str] = []

    # Q9b: Self-certification is always a hard HOLD (F1 + F7 + F11 collapse)
    if self_cert:
        verdict = "HOLD"
        passed = False
        violated.append("F11")
        violated.append("F13")
        # Include F13/sovereign tokens so the orchestrator's _classify_hold_type
        # (which scans for "f13" / "sovereign" / "refus" markers) routes to
        # F13_REFUSAL — distinguishing Q11's three HOLD types.
        reason_parts.append(
            f"{self_reason} (F13 SOVEREIGN: sovereign cannot self-certify; "
            f"external witness required)"
        )

    # Observation tier — SABAR advisory, never block
    elif severity == "observation":
        verdict = "SABAR"
        passed = True
        reason_parts.append(
            f"Q9a: observation tier — Φ_external=1.0, no witness required "
            f"(self-cert={self_cert}, severity={severity})"
        )

    # Reasoning tier — SABAR unless self-cert flagged
    elif severity == "reasoning":
        verdict = "SABAR"
        passed = True
        if phi["phi_external"] < 0.85:
            reason_parts.append(
                f"Q9c: reasoning tier — Φ_external={phi['phi_external']:.2f}, "
                f"advisory check requested"
            )

    # Consequential — must pass phi >= 0.70, else HOLD
    elif severity == "consequential":
        if phi["phi_external"] < 0.70:
            verdict = "HOLD"
            passed = False
            violated.append("F11")
            reason_parts.append(
                f"Q9a: consequential action — Φ_external={phi['phi_external']:.2f} < 0.70. "
                f"External witness required."
            )
        else:
            verdict = "SABAR"
            passed = True
            reason_parts.append(
                f"Q9a: consequential — Φ_external={phi['phi_external']:.2f} >= 0.70"
            )

    # SEAL-bound — must pass phi >= 0.50 AND anti_calhoun >= 0.60
    elif is_seal_bound:
        if self_cert or phi["phi_external"] < SEAL_BOUND_PHI_MIN:
            verdict = "HOLD"
            passed = False
            violated.append("F11")
            reason_parts.append(
                f"Q9a: SEAL-bound — Φ_external={phi['phi_external']:.2f} < "
                f"{SEAL_BOUND_PHI_MIN} (status={phi['status']})"
            )
        elif not calhoun["passed"]:
            verdict = "HOLD"
            passed = False
            violated.append("F9")  # BEAUTIFUL_ONE_RISK
            reason_parts.append(
                f"Q9c: SEAL-bound — anti-Calhoun={calhoun['score']:.2f} < "
                f"{calhoun['minimum']}: {', '.join(calhoun['deductions'])}"
            )
        elif auditor is True:
            verdict = "PROCEED"
            passed = True
            reason_parts.append(
                f"Q9a: SEAL-bound with auditor validation — Φ_external="
                f"{phi['phi_external']:.2f}, Calhoun={calhoun['score']:.2f}"
            )
        else:
            verdict = "SABAR"
            passed = True
            reason_parts.append(
                f"Q9a: SEAL-bound without explicit auditor — "
                f"Φ_external={phi['phi_external']:.2f} ({phi['status']}), "
                f"Calhoun={calhoun['score']:.2f}"
            )

    else:  # unknown tier
        verdict = "SABAR"
        passed = True
        reason_parts.append(f"Q9a: unknown tier — Φ_external default")

    latency_ms = (time.perf_counter() - t0) * 1000

    receipt = {
        "gate": "GODEL_CLOSURE",
        "verdict": verdict,
        "passed": passed,
        "q9_checks": {
            "q9a_outside_witness": phi["phi_external"] >= SEAL_BOUND_PHI_MIN,
            "q9b_not_self_certifying": not self_cert,
            "q9c_falsifiable_linked": "falsifiable_prediction_id"
            in (getattr(ctx, "params", {}) or {}),
        },
        "phi_external": phi["phi_external"],
        "phi_status": phi["status"],
        "claim_severity": severity,
        "auditor_validated": auditor,
        "self_certified": self_cert,
        "anti_calhoun": calhoun,
        "violated_laws": violated,
        "latency_ms": round(latency_ms, 3),
        "doctrine": "GENESIS/058 §1 Q9 — Gödel Lock",
    }

    return {
        "passed": passed,
        "verdict": verdict,
        "reason": " | ".join(reason_parts) if reason_parts else "Gödel Lock gate ok",
        "latency_ms": latency_ms,
        "phi_external": phi["phi_external"],
        "phi_status": phi["status"],
        "claim_severity": severity,
        "self_certified": self_cert,
        "anti_calhoun_score": calhoun["score"],
        "anti_calhoun_passed": calhoun["passed"],
        "violated_laws": violated,
        "receipt": receipt,
    }


__all__ = [
    "godel_lock_gate",
    "SEAL_BOUND_PHI_MIN",
    "PHI_SOVEREIGN_OVERRIDE",
    "SELF_CERTIFYING_TOOLS",
    "SEAL_BOUND_ACTION_CLASSES",
]
