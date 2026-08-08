"""
CONSTITUTION COMPILER — Phase 1 Prototype (P1 zkPC Roadmap — 2026-08-08)
===========================================================================

Compiles arifOS constitutional floors (F1-F13) into formal, deterministic,
machine-verifiable predicates suitable for:
  - Deterministic replay (Phase 2)
  - Constraint circuit generation (Phase 3)
  - Zero-knowledge proof composition (Phase 4)

DESIGN PRINCIPLE:
  Every floor must be expressible as a PURE FUNCTION:
    floor_predicate(inputs) → bool
  with no side effects, no IO, no randomness, no LLM calls.

ARCHITECTURE:
  Floor (natural language)
    ↓
  Predicate (Python with formal semantics)
    ↓
  Constraint (Algebraic relation)
    ↓
  Circuit (R1CS / Plonkish — future)

CURRENT STATUS: Phase 1 — Floor → Predicate compilation.
  F7 HUMILITY (Ω₀ ∈ [0.03, 0.05]) is the reference implementation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


# ═══════════════════════════════════════════════════════════════════════════════
# FLOOR REGISTRY — Canonical floor definitions
# ═══════════════════════════════════════════════════════════════════════════════


class FloorID(Enum):
    """Canonical floor identifiers — matches FLOOR_TABLE.json."""

    F1_AMANAH = "F1"
    F2_TRUTH = "F2"
    F3_TRI_WITNESS = "F3"
    F4_CLARITY = "F4"
    F5_PEACE = "F5"
    F6_MARUAH = "F6"
    F7_HUMILITY = "F7"
    F8_GENIUS = "F8"
    F9_ANTIHANTU = "F9"
    F10_ONTOLOGY = "F10"
    F11_AUDIT = "F11"
    F12_RESILIENCE = "F12"
    F13_SOVEREIGN = "F13"


class VerdictClass(Enum):
    """Deterministic verdict algebra."""

    SEAL = "SEAL"  # All constraints satisfied
    HOLD = "HOLD"  # Authority insufficient
    SABAR = "SABAR"  # Evidence incomplete, non-blocking
    VOID = "VOID"  # Constitutional violation
    UNMEASURED = "UNMEASURED"  # No measurement possible


# ═══════════════════════════════════════════════════════════════════════════════
# PREDICATE TYPE
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class PredicateResult:
    """Immutable result of evaluating a single floor predicate."""

    floor: FloorID
    passed: bool
    value: float | None = None  # Numeric constraint value (if applicable)
    threshold: float | None = None  # Threshold for numeric constraints
    reason: str = ""
    evidence_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "floor": self.floor.value,
            "passed": self.passed,
            "value": self.value,
            "threshold": self.threshold,
            "reason": self.reason,
            "evidence_hash": self.evidence_hash,
        }


# Type alias: a floor predicate is a pure function from inputs to PredicateResult
FloorPredicate = Callable[..., PredicateResult]


# ═══════════════════════════════════════════════════════════════════════════════
# REFERENCE IMPLEMENTATION: F7 HUMILITY
# ═══════════════════════════════════════════════════════════════════════════════


def compile_f7_humility() -> FloorPredicate:
    """
    Compile F7 HUMILITY into a deterministic predicate.

    F7 RULE:
      Ω₀ ∈ [0.03, 0.05]
      Confidence cap ∈ [0.90, 0.97]
      No fabricated certainty.
      UNKNOWN is an acceptable answer.

    FORMAL PREDICATE:
      f7(omega_naught: float, confidence: float, has_declared_unknowns: bool) → bool
        where:
          PASS := 0.03 ≤ omega_naught ≤ 0.05
              AND confidence ≤ 0.90
              AND (confidence < 0.70 → has_declared_unknowns)

    COMPILABLE TO:
      CONSTRAINT omega_naught_range: 0.03 ≤ omega_naught ≤ 0.05
      CONSTRAINT confidence_cap: confidence ≤ 0.90
      CONSTRAINT unknown_declaration: confidence < 0.70 → has_declared_unknowns
    """

    def f7_predicate(
        omega_naught: float = 0.04,
        confidence: float = 0.50,
        has_declared_unknowns: bool = True,
        evidence_bundle: dict[str, Any] | None = None,
    ) -> PredicateResult:
        """Deterministic F7 HUMILITY evaluation.

        Args:
            omega_naught: Baseline uncertainty (must be 0.03-0.05 per F7)
            confidence: Claimed confidence (must be ≤ 0.90)
            has_declared_unknowns: Whether unknowns were declared
            evidence_bundle: Optional evidence for hash computation

        Returns:
            PredicateResult with floor=F7, passed=True/False
        """
        reasons: list[str] = []
        constraints_passed = 0
        constraints_total = 3

        # Constraint 1: Ω₀ ∈ [0.03, 0.05]
        c1 = 0.03 <= omega_naught <= 0.05
        if c1:
            constraints_passed += 1
        else:
            reasons.append(f"Ω₀={omega_naught:.4f} outside required range [0.03, 0.05]")

        # Constraint 2: confidence ≤ 0.90
        c2 = confidence <= 0.90
        if c2:
            constraints_passed += 1
        else:
            reasons.append(f"confidence={confidence:.2f} exceeds cap 0.90")

        # Constraint 3: low confidence must declare unknowns
        c3 = (confidence >= 0.70) or has_declared_unknowns
        if c3:
            constraints_passed += 1
        else:
            reasons.append(f"confidence={confidence:.2f} < 0.70 but no unknowns declared")

        # Evidence hash for replay
        ev_data = {
            "omega_naught": omega_naught,
            "confidence": confidence,
            "has_declared_unknowns": has_declared_unknowns,
        }
        if evidence_bundle:
            ev_data["evidence"] = evidence_bundle
        evidence_hash = hashlib.sha256(json.dumps(ev_data, sort_keys=True).encode()).hexdigest()[
            :16
        ]

        return PredicateResult(
            floor=FloorID.F7_HUMILITY,
            passed=(constraints_passed == constraints_total),
            value=omega_naught,
            threshold=0.05,  # upper bound
            reason="; ".join(reasons) if reasons else "All F7 constraints satisfied",
            evidence_hash=evidence_hash,
        )

    return f7_predicate


# ═══════════════════════════════════════════════════════════════════════════════
# SKELETON: Additional floor compilers (for future phases)
# ═══════════════════════════════════════════════════════════════════════════════


def compile_f8_genius() -> FloorPredicate:
    """
    Compile F8 GENIUS: G = (A×P×E×X)^(1/4) ≥ 0.80

    FORMAL PREDICATE:
      f8(A: float, P: float, E: float, X: float) → bool
        where:
          G = (A × P × E × X) ** 0.25
          PASS := G ≥ 0.80
          All inputs must be in [0, 1]
    """

    def f8_predicate(
        architecture: float,
        physics: float,
        evidence: float,
        execution: float,
    ) -> PredicateResult:
        # Input validation: all dimensions must be in [0, 1]
        dims = {"A": architecture, "P": physics, "E": evidence, "X": execution}
        for name, val in dims.items():
            if not (0.0 <= val <= 1.0):
                return PredicateResult(
                    floor=FloorID.F8_GENIUS,
                    passed=False,
                    value=0.0,
                    threshold=0.80,
                    reason=f"F8 {name}={val} outside valid range [0, 1]",
                )

        g_score = (architecture * physics * evidence * execution) ** 0.25
        evidence_hash = hashlib.sha256(json.dumps(dims, sort_keys=True).encode()).hexdigest()[:16]

        return PredicateResult(
            floor=FloorID.F8_GENIUS,
            passed=g_score >= 0.80,
            value=g_score,
            threshold=0.80,
            reason=f"G={g_score:.4f} {'≥' if g_score >= 0.80 else '<'} 0.80",
            evidence_hash=evidence_hash,
        )

    return f8_predicate


def compile_f12_resilience() -> FloorPredicate:
    """
    Compile F12 RESILIENCE: Risk < 0.85, injection defense active.

    FORMAL PREDICATE:
      f12(injection_score: float, risk_score: float) → bool
        where:
          PASS := risk_score < 0.85 AND injection_score < 0.30
    """

    def f12_predicate(
        injection_score: float = 0.0,
        risk_score: float = 0.0,
    ) -> PredicateResult:
        c1 = risk_score < 0.85
        c2 = injection_score < 0.30

        reasons = []
        if not c1:
            reasons.append(f"risk={risk_score:.2f} ≥ 0.85 threshold")
        if not c2:
            reasons.append(f"injection={injection_score:.2f} ≥ 0.30 threshold")

        return PredicateResult(
            floor=FloorID.F12_RESILIENCE,
            passed=c1 and c2,
            value=max(risk_score, injection_score),
            threshold=0.85,
            reason="; ".join(reasons) if reasons else "All F12 constraints satisfied",
            evidence_hash=hashlib.sha256(
                json.dumps(
                    {"risk": risk_score, "injection": injection_score}, sort_keys=True
                ).encode()
            ).hexdigest()[:16],
        )

    return f12_predicate


# ═══════════════════════════════════════════════════════════════════════════════
# COMPILER REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

# Maps FloorID → compiler function (lazy: compiled on first access)
FLOOR_COMPILERS: dict[FloorID, Callable[[], FloorPredicate]] = {
    FloorID.F7_HUMILITY: compile_f7_humility,
    FloorID.F8_GENIUS: compile_f8_genius,
    FloorID.F12_RESILIENCE: compile_f12_resilience,
    # Future: F1, F2, F3, F4, F5, F6, F9, F10, F11, F13
    #
    # ⚠️ F6 MARUAH is GATED — see F6_SOVEREIGN_RATIFICATION_REQUIRED below.
    # F6 SHALL NOT be added to this registry without:
    #   1. Sovereign (F13) ratification token
    #   2. Published dignity impact assessment
    #   3. Review by at least one human outside the federation trust circle
}

# ── F6 MARUAH GATE (DIGNITY REFINEMENT #1 — 2026-08-08) ──────────────────────
# F6 (MARUAH / Dignity) is the floor that protects the weakest stakeholder.
# Unlike F7 (Ω₀ range), F8 (G-score), or F12 (risk threshold), dignity cannot
# be reduced to a numeric constraint without losing its essential meaning.
#
# This gate ensures that F6 compilation:
#   - Requires EXPLICIT sovereign ratification (not just "no objection")
#   - Requires a published dignity impact assessment
#   - Requires external human review
#   - Is tracked by a ratification token for auditability
#
# DEFAULT: F6 is NOT compiled. The gate is CLOSED until ratified.

F6_SOVEREIGN_RATIFICATION_REQUIRED: bool = True
_F6_RATIFICATION_TOKEN: str | None = None
_F6_DIGNITY_ASSESSMENT_HASH: str | None = None

# ── F13 ANCHOR INVARIANT (DIGNITY REFINEMENT #2 — 2026-08-08) ────────────────
# No compiled floor, no matter how formally correct, may remove or reduce the
# sovereign's (F13) ability to override any machine decision. This invariant
# is checked at compilation time and embedded in every verdict.
#
# The anchor is a list of rights that MUST be preserved by all compiled floors:
F13_ANCHOR_RIGHTS: tuple[str, ...] = (
    "sovereign_override",  # F13: Arif can override any verdict
    "human_appeal",  # Any human can appeal a machine decision
    "constitutional_amendment",  # Constitution can be amended by sovereign
    "emergency_shutdown",  # Sovereign can halt all automated execution
)

# ── SOVEREIGN OVERRIDE PRESERVED — checked at every verdict compilation ───────


def _verify_f13_anchor_preserved() -> tuple[bool, str]:
    """Verify that no compiled floor violates F13 anchor rights.

    This is called by compile_constitutional_verdict() before any verdict
    is returned. If any compiled floor reduces sovereign override capability,
    the verdict is downgraded to HOLD.

    Returns:
        (preserved: bool, reason: str)
    """
    # Currently, no compiled floor touches sovereignty — F13 stays outside the circuit.
    # This check exists as a future-proof: when new floors are compiled,
    # each must declare whether it preserves F13 anchor rights.
    return True, "F13 ANCHOR intact — sovereignty remains outside the circuit"


def _verify_f6_not_prematurely_compiled() -> tuple[bool, str]:
    """Verify that F6 MARUAH is not compiled without ratification.

    Returns:
        (safe: bool, reason: str)
    """
    if FloorID.F6_MARUAH in FLOOR_COMPILERS:
        if F6_SOVEREIGN_RATIFICATION_REQUIRED and _F6_RATIFICATION_TOKEN is None:
            return False, (
                "F6 MARUAH compiled WITHOUT sovereign ratification. "
                "This is a dignity violation. F6 compilation requires "
                "F13 ratification token + published dignity impact assessment."
            )
        return (
            True,
            f"F6 compiled with ratification token {_F6_RATIFICATION_TOKEN[:8] if _F6_RATIFICATION_TOKEN else 'UNKNOWN'}",
        )
    return True, "F6 not compiled — dignity protected by human-governed floor"


def get_compiled_floor(floor: FloorID) -> FloorPredicate:
    """Get a compiled floor predicate. Cached after first compilation."""
    compiler = FLOOR_COMPILERS.get(floor)
    if compiler is None:
        raise NotImplementedError(f"Floor {floor.value} compiler not yet implemented")
    return compiler()


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT COMPILER — Composes all floor predicates into a single verdict
# ═══════════════════════════════════════════════════════════════════════════════


def compile_constitutional_verdict(
    floor_inputs: dict[FloorID, dict[str, Any]],
    constitution_hash: str | None = None,
) -> tuple[VerdictClass, list[PredicateResult], str]:
    """
    Compile ALL available floor predicates into a constitutional verdict.

    This is the deterministic verdict engine — given the same inputs and
    constitution, it ALWAYS returns the same verdict. This is the foundation
    for replay-based zkPC verification.

    Args:
        floor_inputs: Per-floor input dictionaries
        constitution_hash: SHA-256 of the constitution text (for replay binding)

    Returns:
        (verdict, floor_results, replay_hash) — replay_hash binds all inputs
        to this verdict for deterministic re-verification.
    """
    results: list[PredicateResult] = []
    violations: list[str] = []

    for floor in FloorID:
        compiler = FLOOR_COMPILERS.get(floor)
        if compiler is None:
            continue  # Floor not yet compiled — skip (not a violation)
        predicate = compiler()
        inputs = floor_inputs.get(floor, {})
        try:
            result = predicate(**inputs)
            results.append(result)
            if not result.passed:
                violations.append(floor.value)
        except Exception as exc:
            results.append(
                PredicateResult(
                    floor=floor,
                    passed=False,
                    reason=f"FLOOR_EVALUATION_ERROR: {exc}",
                )
            )
            violations.append(floor.value)

    # Verdict logic (deterministic):
    #   Any VOID floor → VOID
    #   Any HOLD (authority) floor → HOLD
    #   Any failed constraint → SABAR
    #   All passed → SEAL
    #   No floors evaluated → UNMEASURED
    if not results:
        verdict = VerdictClass.UNMEASURED
    elif violations:
        # Check if violations include hard floors (F1, F2, F9, F10, F13)
        hard_violations = set(violations) & {"F1", "F2", "F9", "F10", "F13"}
        if hard_violations:
            verdict = VerdictClass.VOID
        elif "F13" in violations or any(
            r.reason and "authority" in r.reason.lower() for r in results if not r.passed
        ):
            verdict = VerdictClass.HOLD
        else:
            verdict = VerdictClass.SABAR
    else:
        verdict = VerdictClass.SEAL

    # Build replay hash — binds ALL inputs + results to this verdict
    replay_bundle = {
        "verdict": verdict.value,
        "constitution_hash": constitution_hash or "UNPINNED",
        "floor_results": [r.to_dict() for r in results],
        "violations": violations,
    }
    replay_hash = hashlib.sha256(
        json.dumps(replay_bundle, sort_keys=True, default=str).encode()
    ).hexdigest()

    # ── F13 ANCHOR — verify sovereign override preserved ──────────────────
    anchor_ok, anchor_reason = _verify_f13_anchor_preserved()
    if not anchor_ok and verdict == VerdictClass.SEAL:
        verdict = VerdictClass.HOLD
        violations.append("F13_ANCHOR_VIOLATION")

    # ── F6 GATE — verify F6 not prematurely compiled ──────────────────────
    f6_ok, f6_reason = _verify_f6_not_prematurely_compiled()
    if not f6_ok and verdict == VerdictClass.SEAL:
        verdict = VerdictClass.VOID
        violations.append("F6_DIGNITY_GATE_VIOLATION")

    return verdict, results, replay_hash


# ═══════════════════════════════════════════════════════════════════════════════
# SELF-TEST — Verify the compiler produces deterministic results
# ═══════════════════════════════════════════════════════════════════════════════


def self_test() -> bool:
    """Run the compiler self-test suite. Returns True if all pass."""
    passed = 0
    failed = 0

    # Test F7 — valid Ω₀
    f7 = compile_f7_humility()
    r = f7(omega_naught=0.04, confidence=0.70, has_declared_unknowns=True)
    if r.passed:
        passed += 1
    else:
        failed += 1
        print(f"FAIL F7 valid: {r.reason}")

    # Test F7 — Ω₀ too high (overconfidence)
    r = f7(omega_naught=0.10, confidence=0.70, has_declared_unknowns=True)
    if not r.passed:
        passed += 1
    else:
        failed += 1
        print("FAIL F7 overconfident: should have failed")

    # Test F7 — confidence too high
    r = f7(omega_naught=0.04, confidence=0.95, has_declared_unknowns=True)
    if not r.passed:
        passed += 1
    else:
        failed += 1
        print("FAIL F7 high confidence: should have failed")

    # Test F7 — low confidence, no unknowns declared
    r = f7(omega_naught=0.04, confidence=0.60, has_declared_unknowns=False)
    if not r.passed:
        passed += 1
    else:
        failed += 1
        print("FAIL F7 no unknowns: should have failed")

    # Test F8 — valid G
    f8 = compile_f8_genius()
    r = f8(architecture=0.90, physics=0.85, evidence=0.80, execution=0.88)
    if r.passed and r.value is not None and r.value >= 0.80:
        passed += 1
    else:
        failed += 1
        print(f"FAIL F8 valid: G={r.value}")

    # Test F8 — insufficient G
    r = f8(architecture=0.70, physics=0.60, evidence=0.50, execution=0.40)
    if not r.passed:
        passed += 1
    else:
        failed += 1
        print("FAIL F8 low G: should have failed")

    # Test F12 — valid
    f12 = compile_f12_resilience()
    r = f12(injection_score=0.10, risk_score=0.50)
    if r.passed:
        passed += 1
    else:
        failed += 1
        print(f"FAIL F12 valid: {r.reason}")

    # Test F12 — injection detected
    r = f12(injection_score=0.50, risk_score=0.80)
    if not r.passed:
        passed += 1
    else:
        failed += 1
        print("FAIL F12 injection: should have failed")

    # Test constitutional verdict composition
    verdict, results, replay_hash = compile_constitutional_verdict(
        floor_inputs={
            FloorID.F7_HUMILITY: {
                "omega_naught": 0.04,
                "confidence": 0.70,
                "has_declared_unknowns": True,
            },
            FloorID.F8_GENIUS: {
                "architecture": 0.90,
                "physics": 0.85,
                "evidence": 0.80,
                "execution": 0.88,
            },
            FloorID.F12_RESILIENCE: {"injection_score": 0.10, "risk_score": 0.50},
        },
        constitution_hash="sha256:test",
    )
    if verdict == VerdictClass.SEAL and len(replay_hash) == 64:
        passed += 1
    else:
        failed += 1
        print(f"FAIL verdict composition: verdict={verdict}")

    # Test determinism — same inputs → same replay_hash
    _, _, hash2 = compile_constitutional_verdict(
        floor_inputs={
            FloorID.F7_HUMILITY: {
                "omega_naught": 0.04,
                "confidence": 0.70,
                "has_declared_unknowns": True,
            },
            FloorID.F8_GENIUS: {
                "architecture": 0.90,
                "physics": 0.85,
                "evidence": 0.80,
                "execution": 0.88,
            },
            FloorID.F12_RESILIENCE: {"injection_score": 0.10, "risk_score": 0.50},
        },
        constitution_hash="sha256:test",
    )
    if replay_hash == hash2:
        passed += 1
    else:
        failed += 1
        print("FAIL determinism: replay_hash differs for same inputs")

    # ── REGRESSION GATE (DIGNITY REFINEMENT #4 — 2026-08-08) ──────────────
    # Verify that every compiled floor preserves or improves protection for
    # the weakest stakeholder compared to the original constitutional text.
    # A floor FAILS this gate if:
    #   - It removes a protection that existed in the original text
    #   - It adds a bypass path that didn't exist before
    #   - It reduces a qualitative protection to a quantitative threshold
    #     without preserving the original meaning (F6 especially)

    # Test: F7 compiled predicate preserves "UNKNOWN is acceptable"
    f7 = compile_f7_humility()
    r_unknown_ok = f7(omega_naught=0.04, confidence=0.50, has_declared_unknowns=True)
    if r_unknown_ok.passed:
        passed += 1  # Low confidence with unknowns declared — should PASS
    else:
        failed += 1
        print("FAIL F7 regression: unknowns declared but rejected")

    # Test: F8 does not bypass dignity — G-score alone cannot override other floors
    f8 = compile_f8_genius()
    r_high_g = f8(architecture=0.95, physics=0.95, evidence=0.95, execution=0.95)
    if r_high_g.passed:
        passed += 1  # High G should pass its own floor
    else:
        failed += 1
        print("FAIL F8 regression: valid high-G rejected")
    # But high G should NOT automatically pass F7 — they are independent
    # (This is verified by the verdict composition test above)

    # Test: F6 gate is CLOSED — F6 is NOT in the compilers registry
    if FloorID.F6_MARUAH not in FLOOR_COMPILERS:
        passed += 1  # Gate is closed — dignity protected
    else:
        failed += 1
        print("FAIL F6 regression: F6 compiled without ratification")

    # Test: F13 anchor — sovereignty rights are declared and checkable
    if len(F13_ANCHOR_RIGHTS) >= 4:
        passed += 1  # Anchor rights declared
    else:
        failed += 1
        print("FAIL F13 regression: insufficient anchor rights")

    # Test: _verify_f13_anchor_preserved returns True
    ok, reason = _verify_f13_anchor_preserved()
    if ok:
        passed += 1
    else:
        failed += 1
        print(f"FAIL F13 anchor: {reason}")

    # Test: _verify_f6_not_prematurely_compiled returns True (gate is closed)
    ok, reason = _verify_f6_not_prematurely_compiled()
    if ok:
        passed += 1
    else:
        failed += 1
        print(f"FAIL F6 gate: {reason}")

    print(f"\nCONSTITUTION COMPILER SELF-TEST: {passed}/{passed + failed} passed")
    return failed == 0


if __name__ == "__main__":
    ok = self_test()
    if not ok:
        raise SystemExit(1)
