"""
AKAL WIRING — Hooks that connect AKAL invariants to the 000→999 pipeline.

Each organ calls ONE hook at the right moment. The hooks are thin — they
compute, they don't execute. The organ decides what to do with the result.

AKAL is internal kernel physics. NOT an MCP surface. NOT user-facing.
These hooks are called from within existing tool implementations.

Hook map:
  333_MIND (reason.py:arif_think)     → akal_pre_think()     at entry
  555_HEART (tools.py:_arif_critique) → akal_post_critique() after LLM returns shadow
  777_FORGE (forge.py:arif_forge)     → akal_pre_forge()     before committing output
  888_JUDGE (judge.py:arif_judge)     → akal_pre_judge()     before verdict emission
  999_VAULT (vault.py:arif_seal)      → akal_pre_seal()      before sealing

Usage by organ (copy-paste into the tool function):

    # ── AKAL I1: Friction gate (333_MIND) ──────────────────────────
    from arifosmcp.core.akal_wiring import akal_pre_think
    akal_result = akal_pre_think(query, blast_radius=blast_radius)
    if akal_result["escalation_required"]:
        # Force multi-step pipeline. Attach to context.
        context = context or {}
        context["akal_friction"] = akal_result
        context["akal_required_depth"] = akal_result["required_depth"]

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import time
from typing import Any

from arifosmcp.core.akal import (
    AkalState,
    BlastClass,
    ChunkType,
    DualVerdict,
    FrictionResult,
    LatencyRequirement,
    NoveltyChunk,
    NoveltyResult,
    ShadowTrace,
    blast_class,
    cooling_requirement,
    dual_evaluate,
    emit_shadow,
    enforce_latency,
    enforce_novelty,
    score_friction,
    tag_novelty,
    validate_shadow,
)

# APEX dial imports — wrapped in try/except for graceful degradation
try:
    from arifosmcp.resources.reality_state import reality_state_resource
except ImportError:
    reality_state_resource = None  # PRESENT not available — graceful degradation

try:
    from arifosmcp.core.physics.thermodynamics_hardened import (
        get_thermodynamic_budget,
        check_landauer_bound,
        ThermodynamicBudget,
    )
except ImportError:
    get_thermodynamic_budget = None  # ENERGY-ENTROPY not available — graceful degradation
    check_landauer_bound = None
    ThermodynamicBudget = None

try:
    from arifosmcp.apex_envelope import amanah_gate
except ImportError:
    amanah_gate = None  # AMANAH gate not available — graceful degradation

try:
    from arifosmcp.core.reversibility_engine import ReversibilityEngine
except ImportError:
    ReversibilityEngine = None  # ReversibilityEngine not available — graceful degradation


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE — AkalState travels through the 000→999 cycle
# ═══════════════════════════════════════════════════════════════════════════════

# In-memory store for session AKAL states. Keyed by session_id.
# In production, this should be backed by Redis or the session store.
_akal_states: dict[str, AkalState] = {}


def get_akal_state(session_id: str) -> AkalState:
    """Get or create AKAL state for a session."""
    if session_id not in _akal_states:
        _akal_states[session_id] = AkalState(created_at=time.time())
    return _akal_states[session_id]


def clear_akal_state(session_id: str) -> None:
    """Clear AKAL state for a session (on session end)."""
    _akal_states.pop(session_id, None)


# ═══════════════════════════════════════════════════════════════════════════════
# HOOK 1: akal_pre_think — 333_MIND (reason.py:arif_think)
# Computes friction score. Returns escalation decision.
# ═══════════════════════════════════════════════════════════════════════════════


def akal_pre_think(
    query: str | None,
    *,
    session_id: str | None = None,
    blast_radius: str = "low",
    has_prior_receipts: bool = True,
    cross_organ: bool = False,
    context_complexity: float = 0.0,
) -> dict[str, Any]:
    """
    333_MIND calls this at entry. Computes friction and returns routing decision.

    Returns dict with:
        friction_score, friction_level, escalation_required, required_depth,
        required_pipeline, reasons
    """
    if not query:
        return {"friction_score": 0.0, "escalation_required": False, "required_depth": "fast"}

    result = score_friction(
        query,
        blast_radius=blast_radius,
        has_prior_receipts=has_prior_receipts,
        cross_organ=cross_organ,
        context_complexity=context_complexity,
    )

    # Store in session state
    if session_id:
        state = get_akal_state(session_id)
        state.friction = result
        state.cycle_stages.append("333_MIND")

    from arifosmcp.core.akal import required_pipeline

    # ── PRESENT DIAL: Reality attestation ──────────────────────
    present_state = {"evidence_class": "unknown", "honesty_ratio": None, "grounded": False}
    try:
        from arifosmcp.runtime.sensing_protocol import (
            InputSpec,
            InputType,
            SenseInput,
            SensingMode,
            classify_truth_class,
        )

        if query:
            si = SenseInput(
                input=InputSpec(type=InputType.QUERY, value=query, mode=SensingMode.GOVERNED)
            )
            tc = classify_truth_class(si)
            present_state["evidence_class"] = tc.truth_class.value
            # If evidence is UNKNOWN or ambiguous, increase friction
            if tc.truth_class.value in ("unknown", "ambiguous_query"):
                result.score = min(result.score + 0.15, 1.0)
                result.reasons.append(
                    f"PRESENT: truth_class={tc.truth_class.value}, friction boosted +0.15"
                )
            # If search is required but not performed, flag it
            if tc.search_required:
                present_state["search_required"] = True
    except Exception:
        pass  # PRESENT is advisory — never blocks

    try:
        from arifosmcp.abi.attestation_verifier import AttestationVerifier

        verifier = AttestationVerifier()
        ratio = verifier.honesty_ratio()
        present_state["honesty_ratio"] = ratio
        if ratio is not None and ratio < 0.5:
            result.score = min(result.score + 0.10, 1.0)
            result.reasons.append(f"PRESENT: honesty_ratio={ratio:.2f}, friction boosted +0.10")
    except Exception:
        pass

    present_state["grounded"] = present_state["evidence_class"] not in (
        "unknown",
        "ambiguous_query",
    )

    # AKAL × PRESENT: epistemic reality check
    present_epistemic = {}
    try:
        from arifosmcp.core.epistemic_state import get_epistemic_state

        epi = get_epistemic_state(session_id) if session_id else None
        if epi:
            reality_class = epi.get("reality_class", "UNKNOWN")
            present_epistemic["reality_class"] = reality_class
            if reality_class in ("INFERRED", "HYPOTHESIZED", "UNKNOWN"):
                result.score = min(result.score + 0.15, 1.0)
                result.reasons.append(
                    f"reality_boost: {reality_class} evidence adds +0.15 friction"
                )
    except ImportError:
        pass  # epistemic_state not yet available — graceful degradation

    # Store PRESENT result in AkalState
    if session_id and present_epistemic.get("reality_class"):
        state = get_akal_state(session_id)
        state.reality_class = present_epistemic["reality_class"]

    return {
        "friction_score": round(result.score, 3),
        "friction_level": result.level.value,
        "escalation_required": result.escalation_required,
        "required_depth": result.required_depth,
        "required_pipeline": required_pipeline(result),
        "reasons": result.reasons,
        "present_state": present_state,
        "present_epistemic": present_epistemic,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HOOK 2: akal_post_critique — 555_HEART (tools.py critique path)
# Validates shadow trace from LLM output. Rejects empty self-audit.
# ═══════════════════════════════════════════════════════════════════════════════


def akal_post_critique(
    critique_output: dict[str, Any],
    *,
    session_id: str | None = None,
    friction_level: str = "low",
) -> dict[str, Any]:
    """
    555_HEART calls this after the LLM produces its shadow/self-critique.
    Validates the shadow trace against AKAL requirements.

    For HIGH/CRITICAL friction, shadow trace is mandatory and must be non-empty.

    Args:
        critique_output: The raw output from arif_critique(mode=shadow)
        session_id: Current session
        friction_level: From akal_pre_think — determines if shadow is required

    Returns dict with:
        shadow_valid, shadow_violations, shadow_required, blocking
    """
    # Extract shadow fields from critique output
    # The LLM may put them in different places depending on the model
    assumptions = (
        critique_output.get("assumptions", [])
        or critique_output.get("reasoning_assumptions", [])
        or []
    )
    missing_data = (
        critique_output.get("missing_data", []) or critique_output.get("missing_evidence", []) or []
    )
    shortcuts = (
        critique_output.get("shortcuts", []) or critique_output.get("reasoning_shortcuts", []) or []
    )
    likely_biases = (
        critique_output.get("likely_biases", []) or critique_output.get("biases", []) or []
    )
    tribal_frames = (
        critique_output.get("tribal_frames", [])
        or critique_output.get("identity_markers", [])
        or []
    )

    trace = emit_shadow(
        assumptions=assumptions,
        missing_data=missing_data,
        shortcuts=shortcuts,
        likely_biases=likely_biases,
        tribal_frames=tribal_frames,
        confidence=critique_output.get("confidence", 0.5),
    )

    # Store in session state
    if session_id:
        state = get_akal_state(session_id)
        state.shadow = trace
        state.cycle_stages.append("555_HEART")

    # Shadow is required for high friction
    shadow_required = friction_level in ("high", "critical")
    blocking = shadow_required and not trace.valid

    return {
        "shadow_valid": trace.valid,
        "shadow_violations": trace.violations,
        "shadow_required": shadow_required,
        "blocking": blocking,
        "trace": trace.to_dict(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HOOK 3: akal_pre_forge — 777_FORGE (forge.py:arif_forge)
# Tags output chunks as DERIVED vs SYNTHESIZED. Enforces novelty.
# ═══════════════════════════════════════════════════════════════════════════════


def akal_pre_forge(
    output_text: str,
    *,
    session_id: str | None = None,
    friction_level: str = "low",
    source_texts: list[str] | None = None,
) -> dict[str, Any]:
    """
    777_FORGE calls this before committing output.
    Tags the output as DERIVED or SYNTHESIZED and checks novelty.

    For now, this is a heuristic check. In production, the LLM should
    tag its own chunks, and this function validates.

    Args:
        output_text: The final output to be committed
        session_id: Current session
        friction_level: From akal_pre_think
        source_texts: Source texts the output was derived from (if any)

    Returns dict with:
        novelty_pass, verdict, derived_ratio, synthesized_ratio, action
    """
    # Simple heuristic: if source_texts provided, check overlap
    # In production, the LLM tags its own chunks
    if source_texts:
        chunks = _auto_tag_chunks(output_text, source_texts)
    else:
        # No sources = assume synthesized (new content)
        chunks = [NoveltyChunk(output_text[:500], ChunkType.SYNTHESIZED, "no sources provided")]

    result = tag_novelty(chunks)
    action = enforce_novelty(result)

    # Store in session state
    if session_id:
        state = get_akal_state(session_id)
        state.novelty = result
        state.cycle_stages.append("777_FORGE")

    # Novelty enforcement only for high friction
    enforced = friction_level in ("high", "critical") and action != "PROCEED"

    # ── EXPLORATION-AMANAH DIAL: Reversibility + custody ───────
    amanah_state = {"reversibility_class": "unknown", "requires_888": False, "custody_ok": True}
    try:
        from arifosmcp.core.reversibility_engine import classify_action

        rev = classify_action("arif_forge", {"mode": "generate", "query": output_text[:200]})
        amanah_state["reversibility_class"] = rev.get("reversibility", "unknown")
        amanah_state["requires_888"] = rev.get("requires_arif_approval", False)
        if amanah_state["reversibility_class"] in ("irreversible", "critical"):
            if action == "PROCEED":
                action = "HOLD"
                result.reasons.append(
                    f"AMANAH: reversibility={amanah_state['reversibility_class']}, upgraded to HOLD"
                )
    except Exception:
        pass  # AMANAH is advisory — never blocks

    try:
        from arifosmcp.abi.amanah_gate import AmanahGate

        gate = AmanahGate()
        haram_check = gate.check(output_text[:500])
        if hasattr(haram_check, "value") and haram_check.value == "HARAM":
            amanah_state["custody_ok"] = False
            action = "HOLD"
            result.reasons.append("AMANAH: HARAM pattern detected in output")
    except Exception:
        pass

    # AKAL × AMANAH: reversibility-first enforcement via ReversibilityEngine
    amanah_rev_result = {"checked": False}
    try:
        if ReversibilityEngine is not None:
            rev = ReversibilityEngine()
            verdict = rev.assess("akal_output", {"text": output_text})
            rev_level = verdict.reversibility_class.value
            amanah_rev_result = {
                "checked": True,
                "reversibility": rev_level,
            }
            if rev_level in ("irreversible", "critical") and friction_level not in (
                "high",
                "critical",
            ):
                # Irreversible output from low-friction context = suspicious
                amanah_rev_result["warning"] = "irreversible_output_in_low_friction_context"
    except Exception:
        pass  # ReversibilityEngine not available — graceful degradation

    try:
        if amanah_gate is not None:
            ag = amanah_gate(confidence=0.88, evidence_strength=0.85)
            amanah_rev_result["amanah_gate"] = ag
    except Exception:
        pass

    # Store AMANAH result in AkalState
    if session_id and amanah_rev_result.get("reversibility"):
        state = get_akal_state(session_id)
        state.reversibility_level = amanah_rev_result["reversibility"]

    return {
        "novelty_pass": result.novelty_pass,
        "verdict": result.verdict,
        "derived_ratio": round(result.derived_ratio, 3),
        "synthesized_ratio": round(result.synthesized_ratio, 3),
        "action": action,
        "enforced": enforced,
        "reasons": result.reasons,
        "amanah_state": amanah_state,
        "amanah_rev_result": amanah_rev_result,
    }


def _auto_tag_chunks(output: str, sources: list[str]) -> list[NoveltyChunk]:
    """Heuristic chunk tagger. Compares output segments against sources."""
    # Split output into sentences/chunks
    sentences = [s.strip() for s in output.split(".") if len(s.strip()) > 20]

    chunks = []
    source_text = " ".join(sources).lower()

    for sentence in sentences:
        # Check if this sentence has significant overlap with any source
        words = set(sentence.lower().split())
        if len(words) < 3:
            continue

        # Simple overlap check
        overlap = sum(1 for w in words if w in source_text)
        overlap_ratio = overlap / len(words) if words else 0

        if overlap_ratio > 0.7:
            chunks.append(NoveltyChunk(sentence, ChunkType.DERIVED, f"overlap={overlap_ratio:.2f}"))
        else:
            chunks.append(
                NoveltyChunk(sentence, ChunkType.SYNTHESIZED, f"overlap={overlap_ratio:.2f}")
            )

    return chunks


# ═══════════════════════════════════════════════════════════════════════════════
# HOOK 4: akal_pre_judge — 888_JUDGE (judge.py:arif_judge)
# Performs L5a/L5b dual evaluation. Blocks high-blast without sovereign.
# ═══════════════════════════════════════════════════════════════════════════════


def akal_pre_judge(
    *,
    session_id: str | None = None,
    # L5a inputs (from agent reasoning)
    coherence: float = 0.8,
    evidence_validity: float = 0.8,
    logic_consistency: float = 0.8,
    reasoning_chain: list[str] | None = None,
    # L5b inputs (from sovereign — None if not engaged)
    harm_assessment: str | None = None,
    dignity_impact: str | None = None,
    long_term_consequences: str | None = None,
    value_alignment: str | None = None,
    floors_checked: list[str] | None = None,
    blast_radius: str = "low",
) -> dict[str, Any]:
    """
    888_JUDGE calls this before emitting a verdict.
    Performs L5a VERIFY (agent) and checks L5b JUDGE (sovereign) requirements.

    Returns dict with:
        l5a_pass, l5b_required, l5b_present, dual_pass, blocked_reason, verdict
    """
    result = dual_evaluate(
        coherence=coherence,
        evidence_validity=evidence_validity,
        logic_consistency=logic_consistency,
        reasoning_chain=reasoning_chain or [],
        harm_assessment=harm_assessment,
        dignity_impact=dignity_impact,
        long_term_consequences=long_term_consequences,
        value_alignment=value_alignment,
        floors_checked=floors_checked,
        blast_radius=blast_radius,
    )

    # Store in session state
    if session_id:
        state = get_akal_state(session_id)
        state.values = result
        state.cycle_stages.append("888_JUDGE")

    return {
        "l5a_pass": result.verify.pass_l5a,
        "l5a_issues": result.verify.issues,
        "l5b_required": blast_radius in ("high", "irreversible"),
        "l5b_present": result.judge is not None,
        "dual_pass": result.dual_pass,
        "blocked_reason": result.blocked_reason,
        "verdict": result.judge.verdict if result.judge else "PENDING_L5b",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HOOK 5: akal_pre_seal — 999_VAULT (vault.py:arif_seal)
# Enforces latency requirements. Blocks seals that rush.
# ═══════════════════════════════════════════════════════════════════════════════


def akal_pre_seal(
    *,
    session_id: str | None = None,
    blast_radius: str = "low",
    passes_completed: int = 1,
    branches_explored: int = 1,
    cooling_elapsed: float = 0,
) -> dict[str, Any]:
    """
    999_VAULT calls this before sealing to VAULT999.
    Enforces latency requirements based on blast radius.

    Returns dict with:
        proceed, reason, latency_requirement, blast_class
    """
    bc = blast_class(blast_radius)
    req = cooling_requirement(bc)
    proceed, reason = enforce_latency(
        bc,
        passes_completed=passes_completed,
        branches_explored=branches_explored,
        cooling_elapsed=cooling_elapsed,
    )

    # Store in session state
    if session_id:
        state = get_akal_state(session_id)
        state.latency = req
        state.cycle_stages.append("999_VAULT")

    # ── ENERGY-ENTROPY DIAL: Real cost model ────────────────────
    # Replaces meaningless Landauer theatre with practical cost gates.
    # Landauer constant = 10⁻²¹ J per bit — mathematically impossible to fail.
    # Real cost = tokens × $/token + time × $/min + complexity × cognitive_surcharge
    energy_state = {
        "landauer_ok": True,  # kept for backward compat
        "entropy_delta": 0.0,
        "cost_checked": False,
        "cost_usd": 0.0,
        "cost_tokens": 0,
        "cost_time_s": 0.0,
        "cost_cognitive": 0.0,
        "cost_gate_pass": True,
    }

    # Real cost model
    _TOKEN_COST_PER_1K = 0.002  # $0.002 per 1K tokens (MiMo V2.5 Pro estimate)
    _TIME_COST_PER_MIN = 0.01  # $0.01 per minute of compute
    _COGNITIVE_SURCHARGE = 0.05  # $0.05 per friction unit above 0.5
    _SEAL_COST_CEILING = 1.00  # $1.00 — seals above this need justification

    est_tokens = passes_completed * branches_explored * 2000
    est_time_s = (
        passes_completed * cooling_elapsed if cooling_elapsed > 0 else passes_completed * 5.0
    )

    token_cost = (est_tokens / 1000) * _TOKEN_COST_PER_1K
    time_cost = (est_time_s / 60) * _TIME_COST_PER_MIN

    # Cognitive surcharge — high-friction seals cost more
    cognitive_cost = 0.0
    if session_id:
        state = get_akal_state(session_id)
        if state.friction and state.friction.score > 0.5:
            cognitive_cost = (state.friction.score - 0.5) * _COGNITIVE_SURCHARGE * passes_completed

    total_cost = token_cost + time_cost + cognitive_cost

    energy_state.update(
        {
            "cost_checked": True,
            "cost_usd": round(total_cost, 4),
            "cost_tokens": est_tokens,
            "cost_time_s": round(est_time_s, 1),
            "cost_cognitive": round(cognitive_cost, 4),
        }
    )

    # Gate: block seals that cost more than ceiling without justification
    if total_cost > _SEAL_COST_CEILING:
        energy_state["cost_gate_pass"] = False
        proceed = False
        reason = f"ENERGY: seal cost ${total_cost:.2f} exceeds ${_SEAL_COST_CEILING:.2f} ceiling — needs justification"

    # Legacy Landauer check (kept for backward compat — always passes)
    try:
        from arifosmcp.core.physics.thermodynamics_hardened import check_landauer_bound

        landauer = check_landauer_bound(
            compute_ms=est_time_s * 1000,
            tokens_generated=est_tokens,
            entropy_reduction=1.0,
        )
        energy_state["landauer_ok"] = landauer.get("passed", True)
    except Exception:
        pass

    try:
        from arifosmcp.boot.entropy_governor import get_entropy_governor

        governor = get_entropy_governor()
        score = governor.compute_score()
        energy_state["entropy_delta"] = score.ratio()
        if score.ratio() > 0.7:
            proceed = False
            reason = f"ENERGY: entropy ratio {score.ratio():.2f} > 0.70 — too much chaos for SEAL"
    except Exception:
        pass

    # AKAL × ENERGY-ENTROPY: thermodynamic cost gate via get_thermodynamic_budget
    thermo_result = {"checked": False}
    try:
        if get_thermodynamic_budget is not None and session_id:
            budget = get_thermodynamic_budget(session_id)
            if budget.is_exhausted:
                proceed = False
                reason = (
                    f"THERMO_EXHAUSTED — budget consumed: "
                    f"{budget.consumed:.4f}/{budget.initial_budget:.4f}"
                )
                thermo_result = {
                    "checked": True,
                    "exhausted": True,
                    "consumed": budget.consumed,
                    "remaining": budget.remaining,
                }
            else:
                thermo_result = {"checked": True, "exhausted": False}
    except Exception:
        pass  # Thermodynamic budget not available — graceful degradation

    # Store ENERGY-ENTROPY result in AkalState
    if session_id and thermo_result.get("checked"):
        state = get_akal_state(session_id)
        state.thermo_exhausted = thermo_result.get("exhausted", False)

    return {
        "proceed": proceed,
        "reason": reason,
        "blast_class": bc.value,
        "min_passes": req.min_passes,
        "requires_branching": req.requires_branching,
        "requires_cooling": req.requires_cooling,
        "cooling_seconds": req.cooling_seconds,
        "requires_second_look": req.requires_second_look,
        "energy_state": energy_state,
        "thermo_result": thermo_result,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE — Full AKAL cycle check
# ═══════════════════════════════════════════════════════════════════════════════


def akal_cycle_status(session_id: str) -> dict[str, Any]:
    """
    Check the AKAL state for a session. Returns completeness and seal readiness.
    Call from any organ to see where the cycle stands.
    """
    state = get_akal_state(session_id)
    can_seal, seal_msg = state.can_seal()

    return {
        "completeness": state.completeness(),
        "is_full_ascent": state.is_full_ascent(),
        "can_seal": can_seal,
        "seal_message": seal_msg,
        "cycle_stages": state.cycle_stages,
        "state": state.to_dict(),
    }
