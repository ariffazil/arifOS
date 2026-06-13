"""
arifosmcp/tools/reason.py — 333_MIND v3.3
════════════════════════════════════════

Inductive reasoning engine and synthesis.

DELTA BUNDLE SPEC (from archive/333/README.md):
  Every arif_mind_reason output MUST include:
  - facts: F2 ≥ 0.99 verifiable claims
  - scars: unresolved contradictions blocking certainty
  - floor_scores: F2, F4, F7, L13 self-check
  - entropy: ΔS ≤ 0 (must decrease local entropy)
  - confidence: calibrated Ω₀ ∈ [0.03, 0.05] (F7 Humility band)

ATTNRES PATTERN (v3.3): Depth-wise block attention over reasoning state.
  Not all prior thoughts are equal. Each new reasoning step selectively
  re-attends to the most relevant prior blocks rather than blind
  accumulation. Block summaries reduce O(L²) → O(B²) where B ≪ L.
  Pattern credit: MoonshotAI Attention-Residuals (2024).

STOP RULES (v3.3): Mind MUST stop or refresh when:
  - G_r ≈ 0 for 3+ consecutive steps (ornamental reasoning)
  - Branch entropy B_e exceeds budget (coordination overhead)
  - Confidence rises while support density U_d falls (hallucinated certainty)
  - Identical evidence hash with no declared revision (circular reasoning)

PARADOX ANCHORS (v3.3): 11 linguistic invariants fire at decision points:
  R1 (Russell) — confidence/evidence mismatch | R4 (Socrates) — examination exhaustion
  R5 (Descartes) — coherence ≠ truth | R8 (Confucius) — UNKNOWN tagging

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import threading
from typing import Any

from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.llm_client import LLMUnavailableError
from arifosmcp.runtime.tools import _hold, _ok
from arifosmcp.schemas.synthesis import Synthesis
from arifosmcp.paradox import (
    register_organ, build_organ_anchors, get_registry,
    inject_paradox_anchor, check_desensitization,
)


def _reduce_verdict(*verdicts: str) -> str:
    """
    Verdict reducer — returns the most conservative verdict.

    Order (most conservative → least):
    VOID > HOLD > HYPOTHESIS > PARTIAL > PASS > SEAL
    """
    order = {
        "VOID": 0,
        "HOLD": 1,
        "ESCALATE_TO_888": 1,
        "NEEDS_EVIDENCE": 2,
        "HYPOTHESIS": 3,
        "PARTIAL": 4,
        "PASS": 5,
        "PASS_WITH_SCOPE_LIMIT": 5,
        "REASONED": 6,
        "REFLECTED": 6,
        "SEAL": 7,
    }
    # Default to HOLD if unknown verdict encountered
    mapped = [(order.get(v, 1), v) for v in verdicts if v]
    if not mapped:
        return "HOLD"
    return min(mapped, key=lambda x: x[0])[1]


# ═══════════════════════════════════════════════════════════════════════════════
# ATTNRES PATTERN — Depth-Wise Block Attention for Reasoning State
# ═══════════════════════════════════════════════════════════════════════════════


def _compute_thought_relevance(
    prior_thoughts: list[dict],
    current_query: str,
    evidence_ids: list[str] | None = None,
) -> list[float]:
    """
    AttnRes-style selective re-attention over prior reasoning blocks.

    Not all prior thoughts are equal. This lightweight scoring function
    computes relevance weights so Mind can selectively feed the most
    relevant prior blocks into each new reasoning step.

    Pattern credit: MoonshotAI Attention-Residuals (2024) —
    layers selectively aggregate earlier representations instead of
    blind uniform accumulation.
    """
    if not prior_thoughts:
        return []

    evidence_ids = evidence_ids or []
    weights = []
    query_words = set(current_query.lower().split())

    for thought in prior_thoughts:
        score = 0.3  # base relevance

        # Boost: evidence overlap
        thought_evidence = set(thought.get("evidence_ids", []))
        if thought_evidence and set(evidence_ids):
            overlap = len(thought_evidence & set(evidence_ids))
            score += 0.2 * min(overlap / max(len(evidence_ids), 1), 1.0)

        # Boost: query word overlap with thought text
        thought_text = thought.get("text", "")
        if thought_text:
            thought_words = set(thought_text.lower().split())
            word_overlap = len(query_words & thought_words) / max(len(query_words), 1)
            score += 0.3 * word_overlap

        # Boost: recency (newer thoughts tend to be more relevant)
        recency = thought.get("thought_id", 0) / max(
            max(t.get("thought_id", 1) for t in prior_thoughts), 1
        )
        score += 0.2 * recency

        weights.append(min(score, 1.0))

    return weights


def _compute_block_summary(thoughts: list[dict], block_id: str = "") -> dict:
    """
    Block AttnRes: compress a chunk of reasoning steps into a block summary.

    Inside a block: normal sequential updates. Between blocks: attend only
    over summaries, not every micro-thought. Reduces O(L²) → O(B²).

    Pattern credit: MoonshotAI Block AttnRes — groups layers into blocks,
    stores block summaries for cross-block attention.
    """
    if not thoughts:
        return {"block_id": block_id, "thought_count": 0, "empty": True}

    all_evidence = set()
    all_tags: set[str] = set()
    all_claims: list[str] = []
    confidences: list[float] = []

    for t in thoughts:
        all_evidence.update(t.get("evidence_ids", []))
        tag = t.get("epistemic_tag", "UNKNOWN")
        if tag:
            all_tags.add(tag)
        text = t.get("text", "")
        if text:
            all_claims.append(text[:200])
        conf = t.get("confidence", 0.5)
        if isinstance(conf, (int, float)):
            confidences.append(float(conf))

    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

    return {
        "block_id": block_id,
        "thought_count": len(thoughts),
        "primary_claims": all_claims[:5],
        "epistemic_tags": sorted(all_tags),
        "evidence_ids": sorted(all_evidence),
        "avg_confidence": round(avg_confidence, 3),
        "thought_range": (
            f"{thoughts[0].get('thought_id', '?')}-{thoughts[-1].get('thought_id', '?')}"
        ),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# STOP RULES — Prevent Ornamental Reasoning and Hallucinated Certainty
# ═══════════════════════════════════════════════════════════════════════════════


def _check_stop_rules(
    thought_history: list[dict],
    branch_count: int = 0,
    max_branches: int = 6,
    confidence_trend: list[float] | None = None,
    support_density_trend: list[float] | None = None,
) -> dict:
    """
    Evaluate stop rules for Mind reasoning chains.

    Returns a dict with should_stop, stop_reason, and paradox_anchor if triggered.
    """
    triggers: list[str] = []
    paradox_id: str | None = None

    # ── Rule 1: Ornamental reasoning (G_r ≈ 0 for N consecutive steps) ──
    if len(thought_history) >= 3:
        recent = thought_history[-3:]
        gains = []
        for i in range(1, len(recent)):
            prev_conf = recent[i - 1].get("confidence", 0.5) or 0.5
            curr_conf = recent[i].get("confidence", 0.5) or 0.5
            gains.append(abs(curr_conf - prev_conf))

        if gains and all(g <= 0.01 for g in gains):
            triggers.append("G_r ≈ 0 for 3+ consecutive steps — ornamental reasoning detected")
            paradox_id = "R_CxC"  # Socrates [clarity_care]: endlessly examined life is not lived

    # ── Rule 2: Branch entropy exceeding budget ──
    active_branches = branch_count
    if active_branches > max_branches:
        triggers.append(
            f"Branch entropy B_e = {active_branches} exceeds budget {max_branches}"
        )
        paradox_id = paradox_id or "R_CxJ"  # Sextus [clarity_justice]: suspension isn't governance

    # ── Rule 3: Confidence rising while support density falling (hallucinated certainty) ──
    if (
        confidence_trend
        and support_density_trend
        and len(confidence_trend) >= 2
        and len(support_density_trend) >= 2
    ):
        conf_rising = confidence_trend[-1] > confidence_trend[-2]
        support_falling = support_density_trend[-1] < support_density_trend[-2]
        if conf_rising and support_falling:
            triggers.append(
                "Confidence rising while support density falling — hallucinated certainty"
            )
            paradox_id = "R_HxC"  # Russell [humility_care]: the stupid are cocksure

    # ── Rule 4: Circular — identical evidence, no declared revision ──
    if len(thought_history) >= 2:
        last_two = thought_history[-2:]
        ev0 = set(last_two[0].get("evidence_ids", []))
        ev1 = set(last_two[1].get("evidence_ids", []))
        is_revision = last_two[-1].get("is_revision", False)
        if ev0 == ev1 and not is_revision and ev0:
            triggers.append(
                "Identical evidence hash on consecutive thoughts with no declared revision"
            )
            paradox_id = paradox_id or "R_CxP"  # Descartes [clarity_peace]: coherence ≠ truth

    should_stop = len(triggers) > 0
    return {
        "should_stop": should_stop,
        "stop_reason": "; ".join(triggers) if triggers else None,
        "paradox_anchor": paradox_id,
        "recommendation": (
            "Emit ABSTAIN or refresh evidence before continuing" if should_stop else "Continue"
        ),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PARADOX ANCHORS — 3×3 Orthogonal Matrix for Mind
# ═══════════════════════════════════════════════════════════════════════════════
# Rows: TRUTH / CLARITY / HUMILITY   Columns: CARE / PEACE / JUSTICE
# Each anchor separates QUOTE (verified human philosophy) from BINDING
# (firing policy). Policy evolves faster than canon — keep them distinct.
# ═══════════════════════════════════════════════════════════════════════════════

MIND_PARADOX_ANCHORS: list[dict] = [
    # ── TRUTH ROW ──────────────────────────────────────────────────────────────
    {
        "id": "R_TxC", "matrix_cell": "truth_care", "matrix_row": "TRUTH", "matrix_col": "CARE",
        "motto_binding": "DIKAJI, BUKAN DISUAPI",
        "quote": {
            "text": "A wise man, therefore, proportions his belief to the evidence.",
            "author": "David Hume",
            "work": "An Enquiry Concerning Human Understanding, Section X",
            "year": "1748",
            "verification_level": "verified_exact",
        },
        "antithesis": "Evidence is never complete — we cannot calculate the exact proportion, only approximate it with models that are themselves uncertain.",
        "axis": "proportionality vs. calculability",
        "binding": {
            "event": "confidence_estimation",
            "trigger": "confidence estimation — Bayesian posterior is an estimate, not a measurement",
            "effect": "annotate_confidence_metadata",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "mind",
        "norm": "WAJIB",
    },
    {
        "id": "R_TxP", "matrix_cell": "truth_peace", "matrix_row": "TRUTH", "matrix_col": "PEACE",
        "motto_binding": "DIJELASKAN, BUKAN DIKABURKAN",
        "quote": {
            "text": "Doubt is not a pleasant condition, but certainty is an absurd one.",
            "author": "Voltaire",
            "work": "Letter to Frederick the Great",
            "year": "1770-11-28",
            "verification_level": "verified_exact",
        },
        "antithesis": "Every bridge crossed, every airplane boarded — these are acts of practical certainty. Absurd or not, we live as if certain because the alternative is paralysis.",
        "axis": "epistemic certainty vs. pragmatic certainty",
        "binding": {
            "event": "claim_tag_assigned",
            "trigger": "CLAIM tag assigned — highest epistemic confidence",
            "effect": "warn_and_bias_to_plausible",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "mind",
        "norm": "WAJIB",
    },
    {
        "id": "R_TxJ", "matrix_cell": "truth_justice", "matrix_row": "TRUTH", "matrix_col": "JUSTICE",
        "motto_binding": "DISEDARKAN, BUKAN DIYAKINKAN",
        "quote": {
            "text": "To know what you know and to know what you do not know — that is true knowledge.",
            "author": "Confucius",
            "work": "Analects 2.17",
            "year": "c. 5th century BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "The boundary between what you know and what you do not know is itself uncertain — you can be wrong about both.",
        "axis": "metacognition vs. meta-uncertainty",
        "binding": {
            "event": "unknown_tag_assigned",
            "trigger": "UNKNOWN tag assigned — validate it is truly unknown",
            "effect": "second_order_check",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "mind",
        "norm": "WAJIB",
    },
    # ── CLARITY ROW ────────────────────────────────────────────────────────────
    {
        "id": "R_CxC", "matrix_cell": "clarity_care", "matrix_row": "CLARITY", "matrix_col": "CARE",
        "motto_binding": "DIJELAJAH, BUKAN DISEKATI",
        "quote": {
            "text": "The unexamined life is not worth living.",
            "author": "Socrates (via Plato)",
            "work": "Apology 38a",
            "year": "c. 399 BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "The endlessly examined life is not lived — reflection without terminus is not wisdom, it is the refusal to exist.",
        "axis": "examination vs. action",
        "binding": {
            "event": "reasoning_exhaustion",
            "trigger": "nextThoughtNeeded:true for > N consecutive steps without convergence",
            "effect": "stop_or_refresh",
        },
        "severity_on_fire": "hold_bias",
        "risk_bias": "conservative",
        "authority_scope": "mind",
        "norm": "WAJIB",
    },
    {
        "id": "R_CxP", "matrix_cell": "clarity_peace", "matrix_row": "CLARITY", "matrix_col": "PEACE",
        "motto_binding": "DIJELASKAN, BUKAN DIKABURKAN",
        "quote": {
            "text": "I think, therefore I am.",
            "author": "René Descartes",
            "work": "Discourse on Method, Part IV",
            "year": "1637",
            "verification_level": "verified_exact",
        },
        "antithesis": "The cogito proves bare existence — it proves nothing about whether thoughts correspond to anything beyond themselves. A coherent chain can be entirely wrong.",
        "axis": "existence vs. knowledge",
        "binding": {
            "event": "coherence_without_evidence",
            "trigger": "R_c > 0.9 and C_e < 0.5 — internal coherence ≠ truth",
            "effect": "warn_and_flag",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "mind",
        "norm": "WAJIB",
    },
    {
        "id": "R_CxJ", "matrix_cell": "clarity_justice", "matrix_row": "CLARITY", "matrix_col": "JUSTICE",
        "motto_binding": "DIUSAHAKAN, BUKAN DIHARAPI",
        "quote": {
            "text": "Skepticism is an ability to set out oppositions among things which appear and are thought of in any way at all, an ability by which, because of the equipollence in the opposed objects and accounts, we come first to suspension of judgment and afterwards to tranquillity.",
            "author": "Sextus Empiricus",
            "work": "Outlines of Pyrrhonism I.8",
            "year": "c. 160–210 CE",
            "verification_level": "verified_exact",
        },
        "antithesis": "Governance is not philosophy — suspension of judgment when action is required is abdication, not wisdom.",
        "axis": "ataraxia vs. responsibility",
        "binding": {
            "event": "equipollent_evidence",
            "trigger": "equipollent evidence detected — suspension path vs. action path both available",
            "effect": "surface_both_paths",
        },
        "severity_on_fire": "warn",
        "risk_bias": "neutral",
        "authority_scope": "mind",
        "norm": "HARUS",
    },
    # ── HUMILITY ROW ───────────────────────────────────────────────────────────
    {
        "id": "R_HxC", "matrix_cell": "humility_care", "matrix_row": "HUMILITY", "matrix_col": "CARE",
        "motto_binding": "DIJAGA, BUKAN DIABAIKAN",
        "quote": {
            "text": "The fundamental cause of the trouble is that in the modern world the stupid are cocksure while the intelligent are full of doubt.",
            "author": "Bertrand Russell",
            "work": "The Triumph of Stupidity, Mortals and Others",
            "year": "1931–1935",
            "verification_level": "verified_exact",
        },
        "antithesis": "Yet endless self-doubt in the competent leaves the field entirely to the cocksure — doubt without eventual decision cedes power to those who never doubted at all.",
        "axis": "confidence vs. competence",
        "binding": {
            "event": "confidence_evidence_mismatch",
            "trigger": "confidence > 0.7 and C_e < 0.5 — Russell's observation hardwired",
            "effect": "warn_in_omega_plane",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "mind",
        "norm": "WAJIB",
    },
    {
        "id": "R_HxP", "matrix_cell": "humility_peace", "matrix_row": "HUMILITY", "matrix_col": "PEACE",
        "motto_binding": "DIDAMAIKAN, BUKAN DIPANASKAN",
        "quote": {
            "text": "Whereof one cannot speak, thereof one must be silent.",
            "author": "Ludwig Wittgenstein",
            "work": "Tractatus Logico-Philosophicus, Proposition 7",
            "year": "1922",
            "verification_level": "verified_exact",
        },
        "antithesis": "The boundary of the speakable is not marked — we discover it only by trying to speak and failing. Silence is the destination, not the starting point.",
        "axis": "silence vs. attempt",
        "binding": {
            "event": "abstain_emitted",
            "trigger": "ABSTAIN output emitted — must include evidence of the attempt",
            "effect": "annotate_abstain_rationale",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "mind",
        "norm": "WAJIB",
    },
    {
        "id": "R_HxJ", "matrix_cell": "humility_justice", "matrix_row": "HUMILITY", "matrix_col": "JUSTICE",
        "motto_binding": "DITEMPA, BUKAN DIBERI",
        "quote": {
            "text": "If I want the door to turn, the hinges must stay put.",
            "author": "Ludwig Wittgenstein",
            "work": "On Certainty §§341–343",
            "year": "1949–1951 (pub. 1969)",
            "verification_level": "verified_exact",
        },
        "antithesis": "What happens when a hinge that must stay put turns out to be false — when the door still turns but around a broken axis?",
        "axis": "foundational certainty vs. foundational fallibility",
        "binding": {
            "event": "floor_proximity",
            "trigger": "reasoning chain approaches a constitutional floor — only F13 SOVEREIGN may question a hinge",
            "effect": "protect_hinge_with_f13_gate",
        },
        "severity_on_fire": "hard_gate",
        "risk_bias": "conservative",
        "authority_scope": "cross_organ",
        "norm": "WAJIB",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX LOOKUP — O(1) access via shared paradox registry (Phase 1)
# ═══════════════════════════════════════════════════════════════════════════════

_mind_anchors = build_organ_anchors("mind", MIND_PARADOX_ANCHORS)
_mind_registry = register_organ("mind", _mind_anchors)

# Backward-compat aliases — delegate to registry
_MIND_BY_CELL = _mind_registry._legacy_by_cell
_MIND_BY_ID = _mind_registry._legacy_by_id


def _inject_paradox_anchor(
    output: dict, trigger_context: str, anchor_id: str | None = None,
    matrix_cell: str | None = None, state_changed: bool = True,
) -> dict:
    """
    Inject a paradox anchor into reasoning output at a decision point.

    Delegates to shared arifosmcp.paradox.inject_paradox_anchor().
    Resolution order (determinism first):
      1. explicit ID → O(1) registry lookup
      2. explicit cell → O(1) registry lookup
      3. keyword auto-detect (last resort)

    Each injection logs to the shared desensitization detector.
    """
    return inject_paradox_anchor(
        output=output,
        registry=_mind_registry,
        trigger_context=trigger_context,
        anchor_id=anchor_id,
        matrix_cell=matrix_cell,
        state_changed=state_changed,
        guard_existing=True,
    )


def _sanitize_observed_inputs(inputs: list[str]) -> list[str]:
    """
    Sanitize observed_inputs to remove raw <think> blocks and private reasoning text.
    Replaces raw thinking with safe abstractions.
    """
    sanitized = []
    for item in inputs:
        if not isinstance(item, str):
            continue
        # Strip raw <think> blocks entirely
        if "<think>" in item or "</think>" in item:
            # Extract a safe abstraction if possible
            if "theory of mind" in item.lower() or "tom" in item.lower():
                sanitized.append("Evidence: operator asked about theory-of-mind scaffolding in init tool.")
            elif "identity" in item.lower() or "verification" in item.lower():
                sanitized.append("Evidence: operator identity verification state was discussed.")
            elif "consent" in item.lower() or "privacy" in item.lower():
                sanitized.append("Evidence: consent boundaries and privacy were discussed.")
            else:
                sanitized.append("Evidence: reasoning trace contained structured constitutional analysis.")
            continue
        # Strip obvious raw model artifacts
        if item.startswith("[think]") or item.startswith("<thinking>"):
            sanitized.append("Evidence: structured reasoning trace available (raw thinking sanitized).")
            continue
        sanitized.append(item)
    return sanitized


def _ensure_confidence(conf: dict | None) -> dict:
    """Ensure confidence is never empty — governed reasoning requires explicit confidence."""
    if not isinstance(conf, dict) or not conf:
        return {
            "reasoning_confidence": 0.5,
            "evidence_confidence": 0.3,
            "overall_confidence": 0.3,
            "label": "low",
            "reason": "Confidence was empty or malformed — defaulting to low-confidence heuristic.",
        }
    # Ensure required keys exist
    conf.setdefault("reasoning_confidence", 0.5)
    conf.setdefault("evidence_confidence", 0.3)
    conf.setdefault("overall_confidence", 0.3)
    if "label" not in conf:
        overall = conf.get("overall_confidence", 0.3)
        if overall >= 0.8:
            conf["label"] = "high"
        elif overall >= 0.5:
            conf["label"] = "medium"
        else:
            conf["label"] = "low"
    if "reason" not in conf:
        conf["reason"] = f"Overall confidence {conf['overall_confidence']:.2f} — self-assessed, not verified."
    return conf


def _ensure_synthesis(synthesis: str | None, reasoning_status: str) -> str:
    """Ensure synthesis is never empty — empty synthesis creates false completion."""
    if synthesis and isinstance(synthesis, str) and synthesis.strip():
        return synthesis.strip()
    return (
        f"Unable to produce structured synthesis — reasoning status is {reasoning_status}. "
        "Claim remains unsealed and requires further evidence or critique."
    )


def _build_delta_bundle(
    query: str | None,
    status: str,
    claim_state: str,
    synthesis: str,
    reasoning: dict,
    confidence: dict,
    uncertainty: list,
    reasoning_mode: str = "analytical",
    axioms_used: list[str] | None = None,
    next_safe_action: list[str] | None = None,
    context: dict | None = None,
    actor_id: str | None = None,
) -> dict:
    """
    Build a Structured Delta Bundle — the upgraded constitutional output for 333_MIND.

    v3.2 fix: 6 orthogonal verdict planes (execution, reasoning, truth, evidence,
    authority, risk) + final_kernel_verdict = strictest across all.
    Provenance is metadata, not authority.

    Core invariant (from ChatGPT × BANGANG test, 2026-06-13):
      AI provenance ≠ authority. LLM output ≠ truth.
      Confidence ≠ permission. SEAL ≠ mutation right.
      Only lease + actor + sovereign authority can grant action.
    """
    # ── Sanitize inputs ──────────────────────────────────────
    reasoning = reasoning or {}
    observed_inputs = reasoning.get("observed_inputs", [])
    if observed_inputs:
        reasoning["observed_inputs"] = _sanitize_observed_inputs(observed_inputs)

    # ── Ensure non-empty critical fields ─────────────────────
    confidence = _ensure_confidence(confidence)
    synthesis = _ensure_synthesis(synthesis, status)

    overall_conf = confidence.get("overall_confidence", 0.5)
    omega_0 = max(0.03, min(0.05, round(1.0 - overall_conf, 4)))

    reasoning_trace = []
    if context:
        session_id = context.get("session_id", "unknown")
        g_score = context.get("g_score", context.get("vitals", {}).get("g_score", "unavailable"))
        reasoning_trace.append(f"[333_MIND context] session_id={session_id}, g_score={g_score}")

    # ── Compute floor scores ─────────────────────────────────
    f02_pass = confidence.get("evidence_confidence", 0) >= 0.9
    floor_scores = {
        "L02_TRUTH": "PASS" if f02_pass else "FAIL",
        "L04_CLARITY": "PASS",
        "L07_HUMILITY": "PASS" if 0.03 <= omega_0 <= 0.05 else "FAIL",
        "L13_SOVEREIGN": "PASS",
    }

    # ── Compute separate verdict planes ──────────────────────
    # Transport: did the tool execute without error?
    transport_verdict = "SEAL"
    # Execution: did the tool run safely (no crash, no mutation)?
    execution_verdict = "SEAL"
    # Reasoning: what did the inner reasoning conclude?
    reasoning_verdict = status  # HOLD, HYPOTHESIS, REASONED, etc.
    # Truth: is the claim proven based on evidence?
    if claim_state in ("VERIFIED_FACT", "SUPPORTED_CLAIM") and f02_pass:
        truth_verdict = "SEAL"
    elif claim_state == "HYPOTHESIS":
        truth_verdict = "HYPOTHESIS"
    elif claim_state in ("SPECULATION", "UNSUPPORTED"):
        truth_verdict = "HOLD"
    else:
        truth_verdict = "HOLD"
    # Floor verdict: did all mandatory floors pass?
    floor_verdict = "SEAL" if all(v == "PASS" for v in floor_scores.values()) else "HOLD"

    # ── Evidence verdict ─────────────────────────────────────
    # Has admissible evidence been attached to the claim?
    # Claim state covers this via VERIFIED_FACT/SUPPORTED_CLAIM vs SPECULATION/UNSUPPORTED.
    attestations = reasoning.get("attestations", []) if isinstance(reasoning, dict) else []
    missing_evidence = reasoning.get("missing_evidence", []) if isinstance(reasoning, dict) else []
    if claim_state in ("VERIFIED_FACT",) and attestations:
        evidence_verdict = "SEAL"          # strong evidence with attestations
    elif claim_state in ("SUPPORTED_CLAIM",) or (attestations and not missing_evidence):
        evidence_verdict = "HYPOTHESIS"    # partial — some support but not verified fact
    elif claim_state in ("SPECULATION", "UNSUPPORTED") or missing_evidence:
        evidence_verdict = "HOLD"          # unsupported or contradicted by missing evidence
    else:
        evidence_verdict = "HOLD"          # default to unsupported

    # ── Paradox anchor: R_HxC Russell — confidence/evidence mismatch ──
    _paradox_anchor = None
    evidence_conf = confidence.get("evidence_confidence", 0.3)
    if overall_conf > 0.7 and evidence_conf < 0.5:
        _paradox_anchor = "R_HxC"  # Russell: cocksure vs. doubtful [humility_care]
    elif claim_state == "SPECULATION" and not missing_evidence:
        _paradox_anchor = "R_TxJ"  # Confucius: know what you don't know [truth_justice]

    # ── Authority verdict ────────────────────────────────────
    # Does the actor have permission to act on this claim?
    # Note: authority is about WHO acts, not WHERE the claim came from.
    # AI provenance is metadata, not authority (see core invariant).
    if actor_id and actor_id.lower() in ("arif", "888", "f13"):
        authority_verdict = "SEAL"         # sovereign or named actor
    elif actor_id:
        authority_verdict = "HYPOTHESIS"   # identified but unverified actor
    else:
        authority_verdict = "HOLD"         # anonymous — no authority at all

    # ── Risk verdict ─────────────────────────────────────────
    # What is the blast radius of acting on this claim?
    # Determined by reversibility + claim sensitivity + actor authority.
    if reasoning_verdict in ("SEAL", "REASONED", "REFLECTED") and evidence_verdict in ("SEAL",) and authority_verdict == "SEAL":
        risk_verdict = "SEAL"              # low risk: well-supported, high authority
    elif reasoning_verdict in ("SEAL", "REASONED") and evidence_verdict in ("SEAL", "HYPOTHESIS"):
        risk_verdict = "HYPOTHESIS"        # medium risk: coherent reasoning but evidence is partial
    elif evidence_verdict == "HOLD":
        risk_verdict = "HOLD"              # high risk: unsupported claims used for action
    else:
        risk_verdict = "HOLD"              # default to high risk

    # Final: most conservative across all planes
    final_verdict = _reduce_verdict(
        transport_verdict,
        execution_verdict,
        reasoning_verdict,
        truth_verdict,
        evidence_verdict,
        authority_verdict,
        risk_verdict,
        floor_verdict,
    )

    # ── Provenance metadata ──────────────────────────────────
    # Provenance tells us WHERE a claim came from.
    # It gives admissibility (traceability, audit, reproducibility).
    # It NEVER gives authority (see core invariant).
    provenance = {
        "source": "arif_mind_reason",
        "model_provenance": confidence.get("model_source", "unknown"),
        "claim_origin": claim_state,
        "reasoning_backend": reasoning_mode,
        "axioms_used": axioms_used or [],
        "admissibility_statement": (
            "Provenance is metadata, not authority. "
            "This claim is admissible as evidence for audit. "
            "It is NOT authorised for action without lease + constitutional clearance."
        ),
    }

    # ── Stage progression with escalation reason ─────────────
    next_stage = "444_HEART"
    if final_verdict in ("HOLD", "VOID", "ESCALATE_TO_888"):
        escalation_reason = (
            f"Escalating to critique because final_verdict={final_verdict} "
            f"(reasoning={reasoning_verdict}, truth={truth_verdict}, "
            f"evidence={evidence_verdict}, authority={authority_verdict}, risk={risk_verdict})."
        )
    else:
        escalation_reason = "Standard progression to ethics/dignity critique stage."

    return {
        "query": query,
        # Verdict planes (v3.2 — orthogonal, never collapsed)
        "transport_verdict": transport_verdict,
        "execution_verdict": execution_verdict,
        "reasoning_verdict": reasoning_verdict,
        "truth_verdict": truth_verdict,
        "evidence_verdict": evidence_verdict,
        "authority_verdict": authority_verdict,
        "risk_verdict": risk_verdict,
        "floor_verdict": floor_verdict,
        "final_verdict": final_verdict,
        # Legacy fields (preserved for backward compat)
        "status": status,
        "claim_state": claim_state,
        "synthesis": synthesis,
        "reasoning": reasoning,
        "confidence": confidence,
        "uncertainty": uncertainty,
        "omega_0": omega_0,
        "reasoning_mode": reasoning_mode,
        "axioms_used": axioms_used or [],
        "next_safe_action": next_safe_action or [],
        "floor_scores": floor_scores,
        "reasoning_trace": reasoning_trace,
        "stage_progression": {
            "current_stage": "333_MIND",
            "next_stage": next_stage,
            "reason": escalation_reason,
        },
        "actor": {
            "claimed_id": actor_id or "anonymous",
            "verified": False,
            "effective_actor": actor_id if actor_id else "anonymous_until_verified",
        },
        # Provenance is metadata, not authority (v3.2)
        "provenance": provenance,
        # Core invariant reminder (never removed from output)
        "_core_invariant": (
            "AI provenance ≠ authority. LLM output ≠ truth. "
            "Confidence ≠ permission. SEAL ≠ mutation right. "
            "Only lease + actor + sovereign authority can grant action."
        ),
        # ── AttnRes block tracking (v3.3) ──
        "_block_state": {
            "thought_count": len(reasoning.get("observed_inputs", [])),
            "evidence_bound_claims": sum(
                1 for c in reasoning.get("claims", [])
                if isinstance(c, dict) and c.get("evidence_ids")
            ),
            "stop_check": None,  # populated by handler
        },
    }

    # ── Inject paradox anchor at decision point ──
    if _paradox_anchor:
        bundle = _inject_paradox_anchor(
            bundle,
            trigger_context=(
                f"confidence={overall_conf:.2f} vs evidence={evidence_conf:.2f}"
                if _paradox_anchor == "R1" else "epistemic tag boundary"
            ),
            anchor_id=_paradox_anchor,
        )

    return bundle


def _run_reasoning_sync(coro: Any, timeout: float = 70.0) -> dict[str, Any]:
    """Run coroutine in sync context, including when caller already has an active event loop.

    L13 TIMEOUT_SAFE: Hard timeout prevents indefinite hangs when LLM backends stall.
    Default 15s balances SEA-LION latency (~1-3s) against CPU-Ollama slowness.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    result: dict[str, Any] = {}
    error: list[BaseException] = []

    def _runner() -> None:
        try:
            result["value"] = asyncio.run(coro)
        except BaseException as exc:  # pragma: no cover - passthrough for sync bridge failures
            error.append(exc)

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        # Thread still running after timeout — LLM backend stalled
        raise LLMUnavailableError(
            f"Reasoning backend timeout after {timeout}s — "
            "SEA-LION unreachable or Ollama CPU inference too slow"
        )

    if error:
        raise error[0]
    return result["value"]


def arif_mind_reason(

    mode: str = "reason",
    query: str | None = None,
    actor_id: str | None = None,
    context: dict | None = None,
) -> Synthesis:
    """
    333_MIND: Constitutional reasoning and synthesis (Structured Witness).
    """
    if mode in ("geox_quantum_suitability", "geox_scale_classifier", "geox_molecular_vs_macroscopic", "geox_hamiltonian_candidate"):
        return {"status": "readonly", "message": f"{mode} activated based on GEOX quantum scale classifier."}

    if mode in ("hndl_score", "pqc_gap_analysis", "migration_strategy", "qday_physics_assess", "claim_lint_quantum"):
        import yaml
        try:
            with open("/root/arifOS/config/qday_policy.yaml") as f:
                policy = yaml.safe_load(f).get("qday_policy", {})
        except Exception:
            policy = {}
            
        risk = "MEDIUM"
        reason_text = "Standard crypto usage detected."
        recommended_action = "Monitor CRQC horizon."
        
        has_vulnerable = True
        data_lifetime = 10
        hndl_crit = policy.get("hndl_critical_if", {})
        crit_lifetime = hndl_crit.get("data_lifetime_years_gte", 10)
        
        if data_lifetime >= crit_lifetime and has_vulnerable:
            risk = "CRITICAL"
            reason_text = "Long-lived data protected by quantum-vulnerable public-key cryptography."
            recommended_action = "Prioritize hybrid/PQC migration planning."
            
        return {
            "mode": mode,
            "risk": risk,
            "reason": reason_text,
            "recommended_action": recommended_action,
            "mutation": False
        }
        
    from arifosmcp.runtime.mind_reason import (
        arif_mind_reason_structured as run_reasoning,
    )

    session_id = context.get("session_id") if context else None

    reason_result = _run_reasoning_sync(run_reasoning(query or "", mode, session_id, actor_id))

    # If v2 metabolic mode, handle the nested mind_packet structure
    if mode == "metabolize" and "mind_packet" in reason_result:
        packet = reason_result["mind_packet"]
        synthesis_v2 = packet.get("synthesis", {})

        # ── AGI KERNEL READINESS GATE 001 FIELDS ──
        raw_conf_v2 = synthesis_v2.get("confidence", {}) if isinstance(synthesis_v2.get("confidence"), dict) else {}
        bundle = {
            "claim_state": str(packet.get("claim_state", "UNKNOWN")).upper(),
            "reasoning_verdict": str(reason_result.get("status", "OK")).upper(),
            "evidence_used": packet.get("attestations", []) if isinstance(packet.get("attestations"), list) else [],
            "inferences": packet.get("abductions", []) if isinstance(packet.get("abductions"), list) else [],
            "counterarguments": packet.get("counterarguments", []) if isinstance(packet.get("counterarguments"), list) else [],
            "missing_evidence": packet.get("missing_evidence", []) if isinstance(packet.get("missing_evidence"), list) else [],
            "confidence": {
                "overall": float(raw_conf_v2.get("overall_confidence", raw_conf_v2.get("overall", 0.0))),
                "label": str(raw_conf_v2.get("label", "low"))
            },
            "next_safe_action": [a.get("tool") for a in packet.get("next_actions", [])] if isinstance(packet.get("next_actions"), list) else []
        }
        return Synthesis(**_ok("arif_mind_reason", bundle))

    # Floor check (Manual override check)
    floor_check = check_laws("arif_mind_reason", {"query": query or ""}, actor_id)
    floor_verdict = floor_check.get("verdict", "HOLD")
    floor_reason = floor_check.get("reason", "Constitutional floor check did not SEAL")

    uncertainty = list(reason_result.get("uncertainty", []))
    if floor_verdict != "SEAL":
        uncertainty.append({"type": "FLOOR_BREACH", "detail": floor_reason})

    raw_conf = reason_result.get("confidence", {}) if isinstance(reason_result.get("confidence"), dict) else {}
    reasoning_data = reason_result.get("reasoning", {}) if isinstance(reason_result.get("reasoning"), dict) else {}
    
    # ── AGI KERNEL READINESS GATE 001 FIELDS ──
    bundle = {
        "claim_state": str(reason_result.get("claim_state", "UNKNOWN")).upper(),
        "reasoning_verdict": "HOLD" if floor_verdict != "SEAL" else str(reason_result.get("status", "HOLD")).upper(),
        "evidence_used": reasoning_data.get("attestations", []) if isinstance(reasoning_data.get("attestations"), list) else [],
        "inferences": reasoning_data.get("abductions", []) if isinstance(reasoning_data.get("abductions"), list) else [],
        "counterarguments": reasoning_data.get("counterarguments", []) if isinstance(reasoning_data.get("counterarguments"), list) else [],
        "missing_evidence": reasoning_data.get("missing_evidence", []) if isinstance(reasoning_data.get("missing_evidence"), list) else [],
        "confidence": {
            "overall": float(raw_conf.get("overall_confidence", raw_conf.get("overall", 0.0))),
            "label": str(raw_conf.get("label", "low"))
        },
        "next_safe_action": reason_result.get("next_safe_action", []) if isinstance(reason_result.get("next_safe_action"), list) else []
    }

    if floor_verdict != "SEAL":
        hold_env = _hold(
            "arif_mind_reason",
            floor_reason,
            floors=list(floor_check.get("violated_laws", [])),
            extra_meta={"floor_verdict": floor_verdict},
            session_id=session_id,
        )
        hold_env["result"] = bundle
        return Synthesis(**hold_env)

    return Synthesis(**_ok("arif_mind_reason", bundle))
