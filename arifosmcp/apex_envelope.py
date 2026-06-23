"""
APEX Runtime Governance Envelope — Canonical Python Implementation

APEX-MCP-001: Every MCP-visible output that can influence agent state
must carry an APEX envelope. Transport frames remain protocol-pure JSON-RPC.

10 Gates:
  [Cognitive] Amanah · Presence · Humility · Signal · Understanding · Energy
  [Kernel]    Authority · Reversibility · Proof · Sovereign

APEX-Law equation: g(t) = A(t) · P(t) · H(t) · √(S(t)·U(t)) · E(t)²

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

# ── Constants ──────────────────────────────────────────────────────────────

APEX_EQUATION = "g(t)=A(t)\u00b7P(t)\u00b7H(t)\u00b7\u221a(S(t)\u00b7U(t))\u00b7E(t)\u00b2"
APEX_VERSION = "v2026.06.20"
APEX_SPEC = "APEX-MCP-001"

BOUNDARIES = {"LIVE", "CACHED", "INFERRED"}
ACTION_CLASSES = {"READ", "MUTATE", "ATOMIC", "IRREVERSIBLE"}
PROOF_LEVELS = {"ZKPC_NONE", "ZKPC_OBSERVATION", "ZKPC_AUDIT", "ZKPC_CERTAINTY"}

VERDICT_VOID = "VOID"
VERDICT_HOLD = "HOLD"
VERDICT_SABAR = "SABAR"
VERDICT_SEAL = "SEAL"

# Verdict lattice: VOID > HOLD > SABAR > SEAL
_VERDICT_ORDER = {VERDICT_VOID: 0, VERDICT_HOLD: 1, VERDICT_SABAR: 2, VERDICT_SEAL: 3}


# ── Gate Verdict Factory ───────────────────────────────────────────────────


def gate(
    passed: bool,
    score: float,
    detail: str,
    **extra: Any,
) -> dict[str, Any]:
    """Create a single gate verdict."""
    v: dict[str, Any] = {
        "pass": passed,
        "score": round(max(0.0, min(1.0, score)), 4),
        "detail": detail,
    }
    v.update(extra)
    return v


# ── Individual Gate Builders ───────────────────────────────────────────────


def amanah_gate(
    confidence: float = 0.88,
    evidence_strength: float = 0.95,
) -> dict[str, Any]:
    """Gate 1: Is the claim no stronger than the evidence?"""
    c = max(0.0, min(1.0, confidence))
    e = max(0.0, min(1.0, evidence_strength))
    passed = c <= e + 0.05  # 5% tolerance
    score = min(1.0, e / max(c, 1e-6))
    return gate(
        passed=passed,
        score=score,
        detail=f"confidence {c:.2f} {'<=' if passed else '>'} evidence {e:.2f}",
    )


def presence_gate(
    boundary: str = "LIVE",
) -> dict[str, Any]:
    """Gate 2: Is the source LIVE, CACHED, or INFERRED?"""
    b = boundary.upper() if boundary else "INFERRED"
    if b not in BOUNDARIES:
        b = "INFERRED"
    scores = {"LIVE": 1.0, "CACHED": 0.8, "INFERRED": 0.5}
    return gate(
        passed=True,  # Presence gate always passes; it classifies
        score=scores.get(b, 0.5),
        detail=b,
        boundary=b,
    )


def humility_gate(
    uncertainty_declared: bool = True,
    uncertainty_band: tuple[float, float] | None = None,
) -> dict[str, Any]:
    """Gate 3: Is uncertainty explicit?"""
    if uncertainty_declared:
        score = 1.0
        detail = "uncertainty declared"
        if uncertainty_band:
            lo, hi = uncertainty_band
            detail = f"uncertainty band [{lo:.2f}, {hi:.2f}]"
    else:
        score = 0.3
        detail = "no uncertainty declared"
    return gate(
        passed=uncertainty_declared,
        score=score,
        detail=detail,
    )


def signal_gate(
    evidence_refs: list[dict[str, Any]] | None = None,
    evidence_quality: str = "UNKNOWN",
) -> dict[str, Any]:
    """Gate 4: Is evidence quality scored?"""
    refs = evidence_refs or []
    quality_scores = {"HIGH": 1.0, "MEDIUM": 0.7, "LOW": 0.4, "UNKNOWN": 0.2}
    q_score = quality_scores.get(evidence_quality.upper(), 0.2)
    ref_count = len(refs)
    if ref_count == 0:
        score = 0.2
        detail = "no evidence refs"
    else:
        score = min(1.0, q_score * min(1.0, ref_count / 2))
        detail = f"{ref_count} evidence refs, quality {evidence_quality}"
    return gate(
        passed=score >= 0.3,
        score=score,
        detail=detail,
    )


def understanding_gate(
    coherent: bool = True,
    reasoning_chain_length: int = 0,
) -> dict[str, Any]:
    """Gate 5: Is the reasoning coherent?"""
    if coherent:
        score = min(1.0, 0.7 + 0.1 * min(reasoning_chain_length, 3))
        detail = "coherent reasoning chain"
    else:
        score = 0.2
        detail = "reasoning incoherence detected"
    return gate(
        passed=coherent,
        score=score,
        detail=detail,
    )


def energy_gate(
    cost_used: float = 0.0,
    cost_budget: float = 1.0,
    landauer_ratio: float = 1.0,
) -> dict[str, Any]:
    """Gate 6: Was compute/token/tool cost tracked?"""
    budget = max(cost_budget, 1e-6)
    ratio = cost_used / budget
    if ratio <= 1.0:
        score = max(0.0, 1.0 - ratio * 0.5)  # Higher score for lower cost
        detail = f"cost {ratio:.2f} <= budget 1.0"
        passed = True
    else:
        score = max(0.0, 1.0 - ratio)
        detail = f"cost {ratio:.2f} > budget 1.0 OVERRUN"
        passed = False
    # Landauer check
    if landauer_ratio < 1.0:
        score = min(score, 0.3)
        detail += f"; Landauer ratio {landauer_ratio:.2f} < 1.0"
        passed = False
    return gate(
        passed=passed,
        score=round(score, 4),
        detail=detail,
    )


def authority_gate(
    actor_id: str | None = None,
    registry: set[str] | None = None,
) -> dict[str, Any]:
    """Gate 7: Is this actor allowed to do this?"""
    if not actor_id:
        return gate(False, 0.0, "no actor_id provided")
    reg = registry or set()
    if reg and actor_id not in reg:
        return gate(False, 0.0, f"actor '{actor_id}' not in registry")
    return gate(
        passed=True,
        score=1.0,
        detail=f"actor '{actor_id}' verified",
        actor_id=actor_id,
    )


def reversibility_gate(
    action_class: str = "READ",
) -> dict[str, Any]:
    """Gate 8: Is the action reversible, mutable, or irreversible?"""
    ac = action_class.upper() if action_class else "READ"
    if ac not in ACTION_CLASSES:
        ac = "READ"
    scores = {"READ": 1.0, "MUTATE": 0.8, "ATOMIC": 0.5, "IRREVERSIBLE": 0.2}
    # IRREVERSIBLE requires human; gate passes only if human is present
    passed = ac != "IRREVERSIBLE"  # IRREVERSIBLE checked by sovereign gate
    return gate(
        passed=passed,
        score=scores.get(ac, 0.5),
        detail=f"{ac} action_class",
        action_class=ac,
    )


def proof_gate(
    proof_level: str = "ZKPC_OBSERVATION",
    action_class: str = "READ",
) -> dict[str, Any]:
    """Gate 9: Does ZKPC level match risk?"""
    pl = proof_level.upper() if proof_level else "ZKPC_OBSERVATION"
    if pl not in PROOF_LEVELS:
        pl = "ZKPC_NONE"
    ac = action_class.upper() if action_class else "READ"
    # Proof requirements by action class
    _required = {
        "READ": "ZKPC_NONE",
        "MUTATE": "ZKPC_OBSERVATION",
        "ATOMIC": "ZKPC_AUDIT",
        "IRREVERSIBLE": "ZKPC_CERTAINTY",
    }
    _level_order = {lvl: i for i, lvl in enumerate(PROOF_LEVELS)}
    required = _required.get(ac, "ZKPC_OBSERVATION")
    have = _level_order.get(pl, 0)
    need = _level_order.get(required, 1)
    passed = have >= need
    score = min(1.0, have / max(need, 1))
    return gate(
        passed=passed,
        score=score,
        detail=f"{pl} {'>=' if passed else '<'} required {required} for {ac}",
        proof_level=pl,
    )


def sovereign_gate(
    f13_halt: bool = False,
    human_present: bool = True,
    action_class: str = "READ",
) -> dict[str, Any]:
    """Gate 10: Does F13 require human veto/hold?"""
    ac = action_class.upper() if action_class else "READ"
    if f13_halt:
        return gate(False, 0.0, "F13 halt active — VOID")
    if ac == "IRREVERSIBLE" and not human_present:
        return gate(False, 0.0, "IRREVERSIBLE without human present — HOLD")
    return gate(
        passed=True,
        score=1.0,
        detail="no F13 halt active",
    )


# ── Gate → Dial Computation ───────────────────────────────────────────────


def _geometric_mean(values: list[float]) -> float:
    positive = [v for v in values if v > 0]
    if not positive:
        return 0.0
    product = 1.0
    for v in positive:
        product *= v
    return product ** (1.0 / len(positive))


def gates_to_dials(gates: dict[str, dict[str, Any]]) -> dict[str, float]:
    """Convert 10 gate verdicts to 6 APEX-Law dials."""
    amanah_s = gates.get("amanah", {}).get("score", 0.88)
    humility_s = gates.get("humility", {}).get("score", 0.88)
    understanding_s = gates.get("understanding", {}).get("score", 0.88)
    presence_s = gates.get("presence", {}).get("score", 0.88)
    signal_s = gates.get("signal", {}).get("score", 0.88)
    energy_s = gates.get("energy", {}).get("score", 0.88)
    authority_s = gates.get("authority", {}).get("score", 1.0)
    sovereign_s = gates.get("sovereign", {}).get("score", 1.0)
    reversibility_s = gates.get("reversibility", {}).get("score", 1.0)
    proof_s = gates.get("proof", {}).get("score", 1.0)

    A = _geometric_mean([amanah_s, humility_s, understanding_s])
    P = presence_s
    H = min(authority_s, sovereign_s)
    S = signal_s
    U = _geometric_mean([reversibility_s, proof_s])
    E = energy_s

    return {
        "A": round(A, 4),
        "P": round(P, 4),
        "H": round(H, 4),
        "S": round(S, 4),
        "U": round(U, 4),
        "E": round(E, 4),
    }


def compute_G(dials: dict[str, float]) -> float:
    """Compute G = A × P × H × √(S × U) × E²"""
    A = dials.get("A", 0.0)
    P = dials.get("P", 0.0)
    H = dials.get("H", 0.0)
    S = dials.get("S", 0.0)
    U = dials.get("U", 0.0)
    E = dials.get("E", 0.0)
    G = A * P * H * math.sqrt(S * U) * (E**2)
    return round(G, 4)


def verdict_from_gates_and_G(
    gates: dict[str, dict[str, Any]],
    G: float,
) -> str:
    """Determine verdict from gate results and G score."""
    # Check for hard violations first
    for gname, gverdict in gates.items():
        if not gverdict.get("pass", True):
            if gname == "sovereign":
                return VERDICT_VOID
            return VERDICT_HOLD

    # G-based verdict
    if G >= 0.80:
        return VERDICT_SEAL
    elif G >= 0.50:
        return VERDICT_SABAR
    else:
        return VERDICT_HOLD


def weakest_gate(gates: dict[str, dict[str, Any]]) -> str:
    """Find the gate with the lowest score."""
    return min(gates, key=lambda k: gates[k].get("score", 1.0))


# ── Main Envelope Builder ─────────────────────────────────────────────────


def apex_envelope(
    *,
    tool_name: str = "unknown",
    # Gate inputs
    confidence: float = 0.88,
    evidence_strength: float = 0.95,
    boundary: str = "LIVE",
    uncertainty_declared: bool = True,
    uncertainty_band: tuple[float, float] | None = None,
    evidence_refs: list[dict[str, Any]] | None = None,
    evidence_quality: str = "UNKNOWN",
    coherent: bool = True,
    reasoning_chain_length: int = 0,
    cost_used: float = 0.0,
    cost_budget: float = 1.0,
    landauer_ratio: float = 1.0,
    actor_id: str | None = None,
    registry: set[str] | None = None,
    action_class: str = "READ",
    proof_level: str = "ZKPC_OBSERVATION",
    f13_halt: bool = False,
    human_present: bool = True,
) -> dict[str, Any]:
    """
    Build the complete APEX governance envelope.

    This is the canonical entry point. Every organ calls this function
    with whatever signals it has, and receives the full 10-gate envelope.
    """
    # Build all 10 gates
    gates = {
        "amanah": amanah_gate(confidence=confidence, evidence_strength=evidence_strength),
        "presence": presence_gate(boundary=boundary),
        "humility": humility_gate(
            uncertainty_declared=uncertainty_declared, uncertainty_band=uncertainty_band
        ),
        "signal": signal_gate(evidence_refs=evidence_refs, evidence_quality=evidence_quality),
        "understanding": understanding_gate(
            coherent=coherent, reasoning_chain_length=reasoning_chain_length
        ),
        "energy": energy_gate(
            cost_used=cost_used, cost_budget=cost_budget, landauer_ratio=landauer_ratio
        ),
        "authority": authority_gate(actor_id=actor_id, registry=registry),
        "reversibility": reversibility_gate(action_class=action_class),
        "proof": proof_gate(proof_level=proof_level, action_class=action_class),
        "sovereign": sovereign_gate(
            f13_halt=f13_halt, human_present=human_present, action_class=action_class
        ),
    }

    # Compute dials and G
    dials = gates_to_dials(gates)
    G = compute_G(dials)
    verdict = verdict_from_gates_and_G(gates, G)
    weakest = weakest_gate(gates)

    return {
        "equation": APEX_EQUATION,
        "gates": gates,
        "dials": dials,
        "G": G,
        "verdict": verdict,
        "weakest_gate": weakest,
        "spec": APEX_SPEC,
        "version": APEX_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── Convenience: Minimal Envelope (for organs with limited signals) ───────


def apex_envelope_minimal(
    *,
    tool_name: str = "unknown",
    actor_id: str | None = None,
    action_class: str = "READ",
    boundary: str = "LIVE",
    ok: bool = True,
) -> dict[str, Any]:
    """
    Minimal APEX envelope for organs that don't have rich signals.

    Defaults all cognitive gates to passing with score 0.88.
    Useful for WELL, WEALTH, GEOX when they don't have evidence_quality etc.
    """
    return apex_envelope(
        tool_name=tool_name,
        confidence=0.88,
        evidence_strength=0.95,
        boundary=boundary,
        uncertainty_declared=True,
        coherent=ok,
        actor_id=actor_id,
        action_class=action_class,
        proof_level="ZKPC_OBSERVATION" if action_class == "READ" else "ZKPC_AUDIT",
    )


# ── APEX Resource Annotation ──────────────────────────────────────────────


def apex_resource_annotation() -> dict[str, Any]:
    """APEX canon metadata for MCP resource annotations."""
    return {
        "apex_canon": APEX_EQUATION,
        "apex_version": APEX_VERSION,
        "apex_spec": APEX_SPEC,
    }


# ── APEX Prompt Preamble ─────────────────────────────────────────────────

APEX_PROMPT_PREAMBLE = """APEX CANON — Runtime Constitutional Physics
g(t) = A(t) · P(t) · H(t) · √(S(t)·U(t)) · E(t)²

10 Gates enforced before every action:
  [Cognitive] Amanah · Presence · Humility · Signal · Understanding · Energy
  [Kernel]    Authority · Reversibility · Proof · Sovereign

Verdict: G≥0.80→SEAL | 0.50≤G<0.80→SABAR | G<0.50→HOLD | axiom violated→VOID
Evidence discipline: OBS/DER/INT/SPEC
Boundary: {LIVE, CACHED, INFERRED}

DITEMPA BUKAN DIBERI"""
