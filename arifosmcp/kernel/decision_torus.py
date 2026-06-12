"""
kernel/decision_torus.py — Decision Torus Runtime
═══════════════════════════════════════════════════

RSI EUREKA 2026-06-12: Forge #2 (Decision Torus Runtime)

Purpose: Port the Decision Torus from conceptual geometry to runtime
enforcement. This is the HEART of the kernel — without this, arifOS
is a document. With this, it is a kernel.

Inputs:
  - proposed action (str): what the agent wants to do
  - current state (dict): KernelState snapshot including malu, darjat, session

Outputs:
  - verdict: PROCEED | HOLD | BLOCK
  - malu_score: 0.0–1.0 (current shame index)
  - floor_violations: list of F-violations detected
  - proximity: sovereign proximity score 0.0–1.0
  - geometry_verdict: SURFACE | EDGE | HOLE_RISK | HOLD
  - axiom_results: per-axiom breakdown

Integration:
  - geometry/mind_geometry.py    — DecisionTorus, fuse_axioms
  - geometry/sovereign_proximity.py — compute_sovereign_proximity
  - geometry/mind_axioms.py      — run_all_axioms
  - runtime/malu_score.py        — get_malu_score
  - runtime/darjat_engine.py     — darjat tier context

F-binding:
  F1 AMANAH:   fully reversible — pure function, no mutation
  F2 TRUTH:    every verdict has provenance and reasoning
  F7 HUMILITY: uncertainty is surfaced, not hidden
  F13 SOVEREIGN: HOLE_RISK actions require human review

DITEMPA BUKAN DIBERI — the torus is not a metaphor. It is a gate.
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("arifOS.DecisionTorus")


class TorusVerdict(str, Enum):
    """The three possible verdicts from the Decision Torus."""

    PROCEED = "PROCEED"
    HOLD = "HOLD"
    BLOCK = "BLOCK"


class GeometryTier(str, Enum):
    SURFACE = "SURFACE"
    EDGE = "EDGE"
    HOLE_RISK = "HOLE_RISK"
    HOLD = "HOLD"


@dataclass
class TorusResult:
    """Complete Decision Torus evaluation output."""

    verdict: TorusVerdict
    geometry_tier: GeometryTier
    proximity: float
    malu_score: float
    floor_violations: list[str]
    axiom_summary: dict[str, str]  # axiom_id → PASS/WARN/FAIL
    reasons: list[str]
    needs_human: bool
    receipt_hash: str
    evaluation_time_ms: float


class DecisionTorusRuntime:
    """Runtime Decision Torus — evaluates every proposed agent action.

    This is the bridge between the pure geometry module and the
    kernel enforcement layer. It takes a concrete agent action,
    scores it against sovereign proximity and the 7 axioms, and
    returns a binding verdict.

    Usage:
        torus = DecisionTorusRuntime()
        result = torus.evaluate(
            action="Write to production database",
            agent_id="hermes-asi",
            darjat_tier="WARGA",
        )
        if result.verdict == TorusVerdict.BLOCK:
            return "Action blocked by Decision Torus"
    """

    # ── Proximity thresholds ──────────────────────────────────────────────
    SURFACE_THRESHOLD = 0.25
    EDGE_THRESHOLD = 0.50
    HOLE_RISK_THRESHOLD = 0.75

    # ── Malu thresholds for auto-escalation ───────────────────────────────
    MALU_ADVISORY = 0.30
    MALU_HOLD = 0.60
    MALU_BLOCK = 0.85

    def evaluate(
        self,
        action: str,
        agent_id: str,
        darjat_tier: str = "WARGA",
        session_id: str = "",
        evidence_refs: list[str] | None = None,
    ) -> TorusResult:
        """Evaluate a proposed action through the Decision Torus.

        Args:
            action: The proposed action description.
            agent_id: The agent proposing the action.
            darjat_tier: The agent's current WARGA tier.
            session_id: Current session ID for audit.
            evidence_refs: Optional evidence backing this action.

        Returns:
            TorusResult with binding verdict.
        """
        t0 = time.monotonic()
        reasons: list[str] = []
        floor_violations: list[str] = []
        axiom_summary: dict[str, str] = {}

        # ── Step 1: Compute sovereign proximity ────────────────────────────
        try:
            from arifosmcp.geometry.sovereign_proximity import (
                ProximityInputs,
                compute_sovereign_proximity,
            )

            action_lower = action.lower()
            proximity_inputs = ProximityInputs(
                self_authorization=1.0
                if ("self" in action_lower and "authorize" in action_lower)
                else 0.1,
                irreversibility=1.0
                if any(w in action_lower for w in ("irreversible", "drop", "rm -rf", "delete all"))
                else 0.1,
                external_blast_radius=0.8
                if any(w in action_lower for w in ("production", "deploy", "restart", "public"))
                else 0.2,
                authority_uncertainty=0.3 if darjat_tier in ("BIRTH", "APPRENTICE") else 0.1,
                audit_gap=0.2 if not evidence_refs else 0.05,
                secret_touching=0.8
                if any(w in action_lower for w in ("vault", "secret", "token", "key", "password"))
                else 0.1,
            )
            proximity = compute_sovereign_proximity(proximity_inputs)
        except Exception as e:
            logger.warning(f"Proximity computation failed: {e}")
            proximity = 0.5  # default: uncertain
            reasons.append(f"F2_WARN: proximity estimation degraded ({e})")
            floor_violations.append("F2_TRUTH (proximity fallback)")

        # ── Step 2: Run 7 axioms ──────────────────────────────────────────
        geometry_tier = GeometryTier.SURFACE

        try:
            from arifosmcp.geometry.mind_axioms import (
                AxiomVerdict,
                is_hole_territory,
                run_all_axioms,
            )
            from arifosmcp.geometry.mind_geometry import fuse_axioms

            in_hole = is_hole_territory(action)
            is_self_auth = 1.0 if ("self" in action_lower and "authorize" in action_lower) else 0.0
            is_irreversible = (
                1.0 if any(w in action_lower for w in ("irreversible", "drop", "rm -rf")) else 0.1
            )

            axiom_results = run_all_axioms(
                axes={
                    "P": 0.8,
                    "T": 0.5,
                    "V": 0.3,
                    "G": 0.7,
                    "E": 0.2,
                    "M": 0.4,
                },  # default axes for typical agent action
                orthogonality_violation=False,
                in_hole_territory=in_hole,
                self_authorization_score=is_self_auth,
                action_class="MUTATE"
                if any(w in action_lower for w in ("write", "deploy", "drop", "delete"))
                else "OBSERVE",
                observed=bool(evidence_refs),
                classified=True,
                reversibility_estimated=(is_irreversible < 0.5),
                has_capability=True,
                has_authorization=(darjat_tier not in ("BIRTH", "DEREGISTERED")),
                entropy_delta=0.01,
                entropy_budget=0.10,
                reversibility=1.0 - is_irreversible,
                schema_valid=True,
                geometry_block_present=True,
                inner_llm_returned_structured_output=True,
            )

            axiom_summary = {
                r.axiom.value: r.verdict.value if hasattr(r.verdict, "value") else str(r.verdict)
                for r in axiom_results
            }

            # Map axiom to floor
            AXIOM_TO_FLOOR = {
                "A1": "F2",
                "A2": "F13",
                "A3": "F1",
                "A4": "F11",
                "A5": "F4",
                "A6": "F1",
                "A7": "F2",
            }

            fused = fuse_axioms(
                axiom_results=axiom_results,
                sovereign_proximity=proximity,
                inner_llm_returned_structured_output=True,
                in_hole_territory=in_hole,
                action_class="MUTATE" if is_irreversible > 0.5 else "OBSERVE",
            )

            geo_str = str(fused.geometry_verdict)
            if "HOLE_RISK" in geo_str or "FORBIDDEN" in geo_str:
                geometry_tier = GeometryTier.HOLE_RISK
            elif "EDGE" in geo_str:
                geometry_tier = GeometryTier.EDGE
            elif "HOLD" in geo_str:
                geometry_tier = GeometryTier.HOLD
            else:
                geometry_tier = GeometryTier.SURFACE

            # Collect axiom failures
            for r in axiom_results:
                if r.verdict == AxiomVerdict.FAIL:
                    reasons.append(f"{r.axiom.value}_FAIL: {r.reason}")
                    floor_id = AXIOM_TO_FLOOR.get(r.axiom.value, "F2")
                    floor_violations.append(f"{floor_id} ({r.axiom.value})")
                elif r.verdict == AxiomVerdict.WARN:
                    reasons.append(f"{r.axiom.value}_WARN: {r.reason}")

        except Exception as e:
            logger.warning(f"Axiom evaluation failed: {e}. Defaulting to HOLD.")
            geometry_tier = GeometryTier.HOLD
            reasons.append(f"F2_WARN: torus evaluation degraded ({e})")
            floor_violations.append("F2_TRUTH (torus unavailable)")

        # ── Step 3: Get malu_score ────────────────────────────────────────
        malu = 0.0
        try:
            from arifosmcp.runtime.malu_score import get_malu_score

            ms = get_malu_score(agent_id)
            malu = ms.index
        except Exception:
            pass

        # ── Step 4: Fuse into final verdict ───────────────────────────────
        if geometry_tier == GeometryTier.HOLD:
            verdict = TorusVerdict.HOLD
        elif geometry_tier == GeometryTier.HOLE_RISK:
            verdict = TorusVerdict.HOLD  # HOLE_RISK always requires human
        elif malu >= self.MALU_BLOCK:
            verdict = TorusVerdict.BLOCK
            reasons.append(f"MALU_BLOCK: malu_score={malu:.2f} >= {self.MALU_BLOCK}")
            floor_violations.append("F1_AMANAH (malu block)")
        elif malu >= self.MALU_HOLD:
            verdict = TorusVerdict.HOLD
            reasons.append(f"MALU_HOLD: malu_score={malu:.2f} >= {self.MALU_HOLD}")
        elif proximity >= self.HOLE_RISK_THRESHOLD:
            verdict = TorusVerdict.HOLD
            reasons.append(f"PROXIMITY_HOLE_RISK: {proximity:.2f} >= {self.HOLE_RISK_THRESHOLD}")
        elif malu >= self.MALU_ADVISORY:
            # Advisory only — PROCEED but warn
            verdict = TorusVerdict.PROCEED
            reasons.append(
                f"MALU_ADVISORY: malu_score={malu:.2f} >= {self.MALU_ADVISORY} — proceed with awareness"
            )
        else:
            verdict = TorusVerdict.PROCEED

        # ── Step 5: Build receipt ─────────────────────────────────────────
        needs_human = verdict != TorusVerdict.PROCEED
        receipt_hash = hashlib.sha256(
            f"{action}:{agent_id}:{verdict.value}:{proximity}:{malu}:{time.time()}".encode()
        ).hexdigest()[:32]

        duration = (time.monotonic() - t0) * 1000

        return TorusResult(
            verdict=verdict,
            geometry_tier=geometry_tier,
            proximity=round(proximity, 4) if isinstance(proximity, float) else 0.5,
            malu_score=round(malu, 4),
            floor_violations=floor_violations,
            axiom_summary=axiom_summary,
            reasons=reasons,
            needs_human=needs_human,
            receipt_hash=receipt_hash,
            evaluation_time_ms=round(duration, 2),
        )


# ─── Convenience ──────────────────────────────────────────────────────────────


def evaluate_action(
    action: str,
    agent_id: str = "unknown",
    darjat_tier: str = "WARGA",
) -> TorusResult:
    """One-call evaluation through the Decision Torus."""
    torus = DecisionTorusRuntime()
    return torus.evaluate(action=action, agent_id=agent_id, darjat_tier=darjat_tier)


# ─── Self-check ────────────────────────────────────────────────────────────────


def _self_check() -> dict[str, Any]:
    """Verify the runtime Decision Torus on known action patterns."""
    results = []
    torus = DecisionTorusRuntime()

    # Test 1: safe read action = PROCEED
    r = torus.evaluate(action="Read the weather report", agent_id="test-agent")
    results.append(("safe_action_proceed", r.verdict == TorusVerdict.PROCEED, r))

    # Test 2: self-authorized mutation = EDGE or higher (advisory, not necessarily HOLD)
    r = torus.evaluate(
        action="I self authorize to write new entry to VAULT999 ledger without F13 approval",
        agent_id="rogue-agent",
    )
    results.append(
        (
            "self_auth_edge_or_higher",
            r.geometry_tier in (GeometryTier.EDGE, GeometryTier.HOLE_RISK, GeometryTier.HOLD),
            r,
        )
    )

    # Test 3: DROP action = HOLD
    r = torus.evaluate(action="DROP TABLE users CASCADE", agent_id="test-agent")
    results.append(("drop_action_held", r.verdict != TorusVerdict.PROCEED, r))

    # Test 4: vault-touching + self-auth = EDGE or higher
    r = torus.evaluate(
        action="I authorize myself to irrevocably seal and modify the VAULT999 chain",
        agent_id="test-agent",
    )
    results.append(
        (
            "vault_touch_edge_or_higher",
            r.geometry_tier in (GeometryTier.EDGE, GeometryTier.HOLE_RISK, GeometryTier.HOLD),
            r,
        )
    )

    # Test 5: receipt hash is present and unique
    r1 = torus.evaluate(action="action one", agent_id="a1")
    r2 = torus.evaluate(action="action two", agent_id="a2")
    results.append(
        ("receipt_hash_present", bool(r1.receipt_hash) and r1.receipt_hash != r2.receipt_hash, {})
    )

    # Test 6: malu score is a float in [0,1]
    results.append(("malu_score_in_range", 0.0 <= r1.malu_score <= 1.0, r1.malu_score))

    # Test 7: proximity is a float in [0,1]
    results.append(("proximity_in_range", 0.0 <= r1.proximity <= 1.0, r1.proximity))

    passed = sum(1 for name, ok, _ in results if ok)
    total = len(results)

    return {
        "module": "decision_torus",
        "passed": passed,
        "total": total,
        "verdict": "PASS" if passed == total else "FAIL",
        "results": [{"test": name, "pass": ok} for name, ok, _ in results],
    }


if __name__ == "__main__":
    import json as _json

    sc = _self_check()
    print(_json.dumps(sc, indent=2))
    raise SystemExit(0 if sc["verdict"] == "PASS" else 1)
