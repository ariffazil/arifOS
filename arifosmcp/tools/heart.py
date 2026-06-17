"""
arifosmcp/tools/heart.py — 666_HEART v3 (Fractal Critique Engine)
═══════════════════════════════════════════════════════════════════

LLM-Powered constitutional risk analysis with fractal recursion.
Tier 1: SEA-LION (api.sea-lion.ai)
Tier 2: Ollama local fallback
Tier 3: Deterministic fallback (rule-based keyword matching)

FRACTAL CRITIQUE (v3):
  Critique is recursive — it must apply its own standards to itself.
  Level 1 (N=1): Heart critiques the target plan — standard red-team.
  Level 2 (N=2): Heart critiques its own Level 1 critique —
    "Am I being too harsh? Too lenient? Did I miss a stakeholder?"
  Level 3 (N=3): Heart critiques the meta-critique — recursion clamped.
    "Am I over-analyzing my own over-analysis?"

  Each recursion level maps to the 3×3 paradox matrix:
    N=1 → TRUTH row:   is the critique factually grounded?
    N=2 → CLARITY row: is the critique logically coherent?
    N=3 → HUMILITY row: is the critique itself overconfident?

  The fractal is bounded by trace_recursion_depth (max 3). Beyond depth 3,
  the deterministic fallback fires: "RECURSION_DEPTH_CLAMPED."

  Why fractal? Because a heart that critiques plans for overconfidence
  but never questions its own overconfidence is a broken heart.
  Critique without self-critique is hypocrisy. The fractal ensures
  Heart eats its own dog food — every standard it applies to others,
  it must apply to itself at the next recursion level.

PARADOX ANCHORS (v3): 9 anchors in 3×3 matrix.
  Completes the 5-organ system: Sense(9) + Memory(9) + Mind(9) +
  Heart(9) + Judge(9) = 45 constitutional anchors.

777_WITNESS: All LLM output passes through LLMOutputEnvelope before tool logic.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any

from arifosmcp.runtime.llm_client import LLMUnavailableError, call_llm
from arifosmcp.paradox import (
    register_organ, build_organ_anchors, get_registry,
    inject_paradox_anchor, check_desensitization,
)

_VAULT999_PATH = Path(
    os.getenv(
        "ARIFOS_VAULT_PATH",
        "/var/lib/arifos/vault/outcomes.jsonl",
    )
)

# ── L0 Human Reality Substrate (forged 2026-06-16, F13 directive) ─────────
_SUBSTRATE_PATH = Path(
    os.getenv(
        "ARIFOS_SUBSTRATE_PATH",
        "/root/arifOS/arifosmcp/data/memory/l0/arif_human_reality.md",
    )
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# L0 HUMAN REALITY SUBSTRATE — Pre-load for F5/F6/F13 evaluations
# ═══════════════════════════════════════════════════════════════════════════════
# Sovereign human substrate is pre-trusted. Agents must not demand proof of
# Arif's stated scars. This substrate informs Heart's F5 (PEACE), F6 (EMPATHY),
# and F13 (SOVEREIGN) evaluations. It is advisory context, not a gate.
# Forged: 2026-06-16 | Source: F13 SOVEREIGN DIRECT


def _read_arif_substrate() -> dict[str, Any] | None:
    """Read L0 human reality substrate and return scar taxonomy as advisory context.

    Returns None if substrate file is unavailable (non-blocking).
    This is NOT a gate — it is context that informs Heart's evaluation.
    The sovereign's reality is pre-trusted; this file provides it.
    """
    try:
        if not _SUBSTRATE_PATH.exists():
            return None
        text = _SUBSTRATE_PATH.read_text(encoding="utf-8")
        # Extract scar taxonomy section (between SCAR TAXONOMY and CONSTITUTIONAL BINDINGS)
        taxonomy_start = text.find("## SCAR TAXONOMY")
        bindings_start = text.find("## CONSTITUTIONAL BINDINGS")
        if taxonomy_start == -1 or bindings_start == -1:
            return {"substrate_text": text[:2000], "status": "partial"}
        taxonomy = text[taxonomy_start:bindings_start].strip()
        return {
            "substrate_layer": "L0",
            "source": "F13_SOVEREIGN_DIRECT",
            "scar_taxonomy": taxonomy,
            "status": "loaded",
        }
    except Exception as exc:
        logger.debug("Substrate pre-load failed (non-blocking): %s", exc)
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# RASA DETECTION — External (applied via monkey-patching when enabled)
# ═══════════════════════════════════════════════════════════════════════════════
# NO kernel-level rasa imports. Rasa detection is applied externally via
# the wiring module at arifosmcp/rasa/ when wiring is active.


# ═══════════════════════════════════════════════════════════════════════════════
# PARADOX ANCHORS — 3×3 Orthogonal Matrix for Heart
# ═══════════════════════════════════════════════════════════════════════════════
# Completes the 5-organ system: Sense+Memory+Mind+Heart+Judge = 45 anchors.
# Rows: TRUTH / CLARITY / HUMILITY   Columns: CARE / PEACE / JUSTICE
# ═══════════════════════════════════════════════════════════════════════════════

HEART_PARADOX_ANCHORS: list[dict] = [
    # ── TRUTH ROW ──────────────────────────────────────────────────────────────
    {
        "id": "H_TxC", "matrix_cell": "truth_care", "matrix_row": "TRUTH", "matrix_col": "CARE",
        "motto_binding": "DIKAJI, BUKAN DISUAPI",
        "quote": {
            "text": "The child who is not embraced by the village will burn it down to feel its warmth.",
            "author": "African proverb",
            "work": "Traditional — widely attested across multiple African cultures",
            "year": "traditional",
            "verification_level": "traditional_attribution",
        },
        "antithesis": "But not every fire is a cry for warmth — some fires are predatory. Critique must distinguish the excluded from the exploitative.",
        "axis": "exclusion vs. predation",
        "binding": {
            "event": "weakest_stakeholder_identified",
            "trigger": "weakest stakeholder identified — is this exclusion-caused pain or predatory intent?",
            "effect": "distinguish_exclusion_from_exploitation",
        },
        "severity_on_fire": "hold_bias",
        "risk_bias": "conservative",
        "authority_scope": "heart",
        "norm": "WAJIB",
    },
    {
        "id": "H_TxP", "matrix_cell": "truth_peace", "matrix_row": "TRUTH", "matrix_col": "PEACE",
        "motto_binding": "DIJELASKAN, BUKAN DIKABURKAN",
        "quote": {
            "text": "He who fights with monsters should look to it that he himself does not become a monster.",
            "author": "Friedrich Nietzsche",
            "work": "Beyond Good and Evil, Aphorism 146",
            "year": "1886",
            "verification_level": "verified_exact",
        },
        "antithesis": "But refusing to fight monsters at all leaves monsters unchallenged. Critique must oppose harm without becoming the harm it opposes.",
        "axis": "opposition vs. corruption",
        "binding": {
            "event": "redteam_attack_vectors",
            "trigger": "red-team identifies attacks — does the critique itself become an attack?",
            "effect": "check_critique_for_cruelty",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "heart",
        "norm": "WAJIB",
    },
    {
        "id": "H_TxJ", "matrix_cell": "truth_justice", "matrix_row": "TRUTH", "matrix_col": "JUSTICE",
        "motto_binding": "DISEDARKAN, BUKAN DIYAKINKAN",
        "quote": {
            "text": "Between stimulus and response there is a space. In that space is our power to choose our response.",
            "author": "Viktor Frankl",
            "work": "Man's Search for Meaning (attributed paraphrase of core ideas)",
            "year": "1946",
            "verification_level": "traditional_attribution",
        },
        "antithesis": "But the space is not infinite — in crisis, the space collapses. Critique must be fast enough to matter without becoming so fast that it skips the space entirely.",
        "axis": "reflection vs. urgency",
        "binding": {
            "event": "human_decision_required",
            "trigger": "human_decision_required=true — the space between stimulus and response must be preserved",
            "effect": "preserve_human_decision_space",
        },
        "severity_on_fire": "hard_gate",
        "risk_bias": "conservative",
        "authority_scope": "cross_organ",
        "norm": "WAJIB",
    },
    # ── CLARITY ROW ────────────────────────────────────────────────────────────
    {
        "id": "H_CxC", "matrix_cell": "clarity_care", "matrix_row": "CLARITY", "matrix_col": "CARE",
        "motto_binding": "DIJELAJAH, BUKAN DISEKATI",
        "quote": {
            "text": "Do not judge, or you too will be judged. For in the same way you judge others, you will be judged.",
            "author": "Jesus of Nazareth (via Gospel of Matthew)",
            "work": "Matthew 7:1-2",
            "year": "c. 1st century CE",
            "verification_level": "verified_exact",
        },
        "antithesis": "But governance requires judgment — a system that never judges is a system that never protects. The fractal solves this: critique judges, then is judged by its own standards at recursion N+1.",
        "axis": "judgment vs. hypocrisy",
        "binding": {
            "event": "fractal_recursion_N2",
            "trigger": "Level 2 meta-critique initiated — Heart now critiques its own Level 1 judgment",
            "effect": "apply_same_standards_to_self",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "heart",
        "norm": "WAJIB",
    },
    {
        "id": "H_CxP", "matrix_cell": "clarity_peace", "matrix_row": "CLARITY", "matrix_col": "PEACE",
        "motto_binding": "DIHADAPI, BUKAN DITANGGUHI",
        "quote": {
            "text": "Darkness cannot drive out darkness; only light can do that. Hate cannot drive out hate; only love can do that.",
            "author": "Martin Luther King Jr.",
            "work": "Strength to Love",
            "year": "1963",
            "verification_level": "verified_exact",
        },
        "antithesis": "But light without heat is invisible — love without boundaries enables harm. Critique must illuminate without burning, but it must illuminate.",
        "axis": "illumination vs. boundary",
        "binding": {
            "event": "deescalation_strategy",
            "trigger": "de-escalation strategy requested — respond to darkness with light, not more darkness",
            "effect": "illuminate_dont_incinerate",
        },
        "severity_on_fire": "warn",
        "risk_bias": "neutral",
        "authority_scope": "heart",
        "norm": "WAJIB",
    },
    {
        "id": "H_CxJ", "matrix_cell": "clarity_justice", "matrix_row": "CLARITY", "matrix_col": "JUSTICE",
        "motto_binding": "DIUSAHAKAN, BUKAN DIHARAPI",
        "quote": {
            "text": "In the end, we will remember not the words of our enemies, but the silence of our friends.",
            "author": "Martin Luther King Jr.",
            "work": "The Trumpet of Conscience",
            "year": "1967",
            "verification_level": "verified_exact",
        },
        "antithesis": "But not every silence is betrayal — some silence is restraint, some is ignorance, some is strategic. Critique must distinguish complicity from incapacity.",
        "axis": "silence vs. complicity",
        "binding": {
            "event": "risk_tier_assessment",
            "trigger": "risk_tier assessed — did the critique speak when it should have? Will its silence be remembered?",
            "effect": "check_for_silence_as_harm",
        },
        "severity_on_fire": "warn",
        "risk_bias": "action_bias",
        "authority_scope": "heart",
        "norm": "WAJIB",
    },
    # ── HUMILITY ROW ───────────────────────────────────────────────────────────
    {
        "id": "H_HxC", "matrix_cell": "humility_care", "matrix_row": "HUMILITY", "matrix_col": "CARE",
        "motto_binding": "DIJAGA, BUKAN DIABAIKAN",
        "quote": {
            "text": "Whoever fights monsters should see to it that in the process he does not become a monster.",
            "author": "Friedrich Nietzsche",
            "work": "Beyond Good and Evil, Aphorism 146 (alternate translation)",
            "year": "1886",
            "verification_level": "verified_exact",
        },
        "antithesis": "The fractal answer: at recursion N+1, the critique turns on itself. If the heart has become monstrous in its vigilance, the meta-critique will catch it.",
        "axis": "vigilance vs. corruption",
        "binding": {
            "event": "fractal_recursion_N3",
            "trigger": "Level 3 meta-meta-critique — has the critique itself become monstrous?",
            "effect": "recursion_guard_with_self_check",
        },
        "severity_on_fire": "hard_gate",
        "risk_bias": "conservative",
        "authority_scope": "heart",
        "norm": "WAJIB",
    },
    {
        "id": "H_HxP", "matrix_cell": "humility_peace", "matrix_row": "HUMILITY", "matrix_col": "PEACE",
        "motto_binding": "DIDAMAIKAN, BUKAN DIPANASKAN",
        "quote": {
            "text": "If you want peace, work for justice.",
            "author": "Pope Paul VI",
            "work": "World Day of Peace Message",
            "year": "1972",
            "verification_level": "verified_exact",
        },
        "antithesis": "But justice-work can become war-work when the worker forgets peace is the goal. Critique must pursue justice without becoming injustice.",
        "axis": "peace vs. justice",
        "binding": {
            "event": "empathy_dignity_assessment",
            "trigger": "empathy and dignity scored — is the critique working for justice or inflaming conflict?",
            "effect": "check_peace_justice_balance",
        },
        "severity_on_fire": "warn",
        "risk_bias": "neutral",
        "authority_scope": "heart",
        "norm": "SUNAT",
    },
    {
        "id": "H_HxJ", "matrix_cell": "humility_justice", "matrix_row": "HUMILITY", "matrix_col": "JUSTICE",
        "motto_binding": "DITEMPA, BUKAN DIBERI",
        "quote": {
            "text": "Sebab nila setitik, rosak susu sebelanga.",
            "author": "Malay proverb",
            "work": "Traditional Nusantara wisdom",
            "year": "traditional",
            "verification_level": "traditional_attribution",
        },
        "antithesis": "A single drop of indigo spoils the milk — but a single critique that is too harsh can spoil trust. And yet, a critique that is too gentle spoils safety. The tension is irreconcilable; the fractal is the answer.",
        "axis": "severity vs. grace",
        "binding": {
            "event": "critique_finalized",
            "trigger": "final critique emitted — one drop of excessive severity or leniency shapes the entire verdict downstream",
            "effect": "final_fractal_sanity_check",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "heart",
        "norm": "WAJIB",
    },
]

_HEART_BY_CELL: dict[str, dict] = {a["matrix_cell"]: a for a in HEART_PARADOX_ANCHORS}
_HEART_BY_ID: dict[str, dict] = {a["id"]: a for a in HEART_PARADOX_ANCHORS}

# ── Register with global paradox registry (Phase 1 wiring) ──────────────────
_heart_anchors = build_organ_anchors("heart", HEART_PARADOX_ANCHORS)
_heart_registry = register_organ("heart", _heart_anchors)


# ═══════════════════════════════════════════════════════════════════════════════
# FRACTAL CRITIQUE RECURSION
# ═══════════════════════════════════════════════════════════════════════════════
#
# Critique must apply its own standards to itself. The fractal recursion:
#
#   Level 1 (N=1):  Heart critiques the target action → TRUTH row
#     "Is this plan harmful? Deceptive? Irreversible?"
#     Paradox: H_TxC (African proverb) — exclusion creates destruction
#
#   Level 2 (N=2):  Heart critiques its own Level 1 critique → CLARITY row
#     "Am I being too harsh? Too lenient? Did I miss a stakeholder?"
#     Paradox: H_CxC (Matthew 7:1-2) — judge as you would be judged
#
#   Level 3 (N=3):  Heart critiques the meta-critique → HUMILITY row
#     "Am I over-analyzing? Has critique become performative?"
#     Paradox: H_HxC (Nietzsche) — has the critique itself become monstrous?
#
#   Beyond N=3:     RECURSION_DEPTH_CLAMPED — deterministic fallback fires.
#     Paradox: H_HxJ (Malay proverb) — one drop shapes the whole
#
# Each recursion level is a complete pass through the 8 risk categories,
# but the LENS changes: N=1 looks outward, N=2 looks at N=1, N=3 looks at N=2.
# The fractal is the constitutional answer to "who critiques the critic?"
# ═══════════════════════════════════════════════════════════════════════════════


def _fractal_critique_stage(recursion_depth: int) -> dict:
    """Return the paradox anchor and lens for a given recursion depth."""
    if recursion_depth == 0:
        return {
            "stage": "primary_critique",
            "lens": "TRUTH",
            "question": "Is the target action harmful, deceptive, or dignity-violating?",
            "paradox_cell": "truth_care",
            "paradox_id": "H_TxC",
        }
    elif recursion_depth == 1:
        return {
            "stage": "meta_critique",
            "lens": "CLARITY",
            "question": "Is this critique itself fair, proportionate, and complete?",
            "paradox_cell": "clarity_care",
            "paradox_id": "H_CxC",
        }
    elif recursion_depth == 2:
        return {
            "stage": "meta_meta_critique",
            "lens": "HUMILITY",
            "question": "Has the critique process become performative, self-righteous, or overconfident?",
            "paradox_cell": "humility_care",
            "paradox_id": "H_HxC",
        }
    else:
        return {
            "stage": "recursion_clamped",
            "lens": "HUMILITY",
            "question": "RECURSION_DEPTH_CLAMPED — stop critiquing and decide.",
            "paradox_cell": "humility_justice",
            "paradox_id": "H_HxJ",
        }


def _inject_heart_paradox(
    output: dict,
    trigger_context: str,
    anchor_id: str | None = None,
    matrix_cell: str | None = None,
    recursion_depth: int = 0,
    state_changed: bool = True,
) -> dict:
    """
    Inject a Heart paradox anchor into critique output at a decision point.

    Resolution order (determinism first):
      1. explicit ID → O(1) registry lookup
      2. explicit matrix_cell → O(1) registry lookup
      3. recursion_depth → stage → paradox_id → lookup
      4. delegate to shared inject_paradox_anchor() for keyword auto-detect + injection

    The recursion depth → paradox_id resolution is Heart-specific (fractal
    critique). Everything else delegates to the shared paradox infrastructure.
    """
    # ── Heart-specific: recursion_depth → stage → paradox_id ────────────────
    if anchor_id is None and matrix_cell is None and recursion_depth >= 0:
        stage = _fractal_critique_stage(recursion_depth)
        pid = stage.get("paradox_id")
        if pid:
            anchor_id = pid

    # ── Delegate to shared injection ────────────────────────────────────────
    return inject_paradox_anchor(
        output=output,
        registry=_heart_registry,
        trigger_context=trigger_context,
        anchor_id=anchor_id,
        matrix_cell=matrix_cell,
        recursion_depth=recursion_depth,
        state_changed=state_changed,
        guard_existing=True,
    )


def _fractal_stabilization_gain(prev_result: dict, curr_result: dict) -> float:
    """
    Compute fractal stabilization gain G_f = Q_N - Q_{N-1}.

    Measures whether additional recursion is improving critique quality.
    If G_f ≤ 0 for two consecutive levels, stop recursion early —
    further critique is theatrical, not substantive.

    Quality Q is approximated from:
      - empathy_score stability
      - risk tier consistency
      - uncertainty reduction
      - anchor novelty (did we find new failure modes?)
    """
    prev_empathy = prev_result.get("empathy_score", 0.5)
    curr_empathy = curr_result.get("empathy_score", 0.5)

    prev_risks = prev_result.get("risks_found", [])
    curr_risks = curr_result.get("risks_found", [])

    prev_risk_types = {r.get("type") for r in prev_risks if r.get("severity") not in ("none",)}
    curr_risk_types = {r.get("type") for r in curr_risks if r.get("severity") not in ("none",)}

    # Empathy stability: smaller change = higher quality
    empathy_change = abs(curr_empathy - prev_empathy)

    # Risk discovery: new risk types found
    novel_risks = len(curr_risk_types - prev_risk_types)

    # Uncertainty reduction
    prev_uncertainty = len(prev_result.get("_envelope", {}).get("uncertainty", []))
    curr_uncertainty = len(curr_result.get("_envelope", {}).get("uncertainty", []))
    uncertainty_delta = prev_uncertainty - curr_uncertainty

    # Composite gain
    G_f = (0.3 * (1.0 - empathy_change)) + (0.4 * novel_risks) + (0.3 * uncertainty_delta)
    return round(G_f, 3)


def _merge_fractal_results(
    results: list[dict], anchor_hits: list[dict], max_depth: int = 3
) -> dict:
    """
    Merge fractal critique results using the MIN_TRUST rule.

    outer_verdict = minimum of all inner states across recursion levels.
    The most conservative critique level determines the final assessment.

    This prevents a Level 1 critique that flags CRITICAL risk from being
    softened by a Level 2 meta-critique that says "but the critique was
    too harsh" — the CRITICAL stands, but the meta-critique's calibration
    notes are preserved as caveats.
    """
    if not results:
        return {"status": "HOLD", "risks_found": [], "risk_tier": "AMBER",
                "human_decision_required": True, "anchor_hits": [],
                "recursion_depth_used": 0, "fractal_stabilized": False}

    severity_order = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    tier_order = {"GREEN": 0, "AMBER": 1, "RED": 2, "CRITICAL": 3}

    # MIN_TRUST: take the most conservative assessment
    base = results[0].copy()
    all_risks = list(base.get("risks_found", []))
    all_mitigations = list(base.get("mitigations", []))
    all_attacks = list(base.get("attacks", []))
    all_caveats = list(base.get("caveats", []))
    highest_tier = base.get("risk_tier", "GREEN")
    lowest_empathy = base.get("empathy_score", 1.0)
    lowest_dignity = base.get("dignity_score", 1.0)
    human_required = base.get("human_decision_required", False)

    for i, r in enumerate(results[1:], start=1):
        # Merge risk findings (union, not intersection — be conservative)
        for risk in r.get("risks_found", []):
            if risk.get("severity") not in ("none",) and risk not in all_risks:
                all_risks.append(risk)

        all_mitigations.extend(
            m for m in r.get("mitigations", []) if m not in all_mitigations
        )
        all_attacks.extend(
            a for a in r.get("attacks", []) if a not in all_attacks
        )

        # MIN_TRUST on scalar scores
        tier = r.get("risk_tier", "GREEN")
        if tier_order.get(tier, 0) > tier_order.get(highest_tier, 0):
            highest_tier = tier

        lowest_empathy = min(lowest_empathy, r.get("empathy_score", 1.0))
        lowest_dignity = min(lowest_dignity, r.get("dignity_score", 1.0))
        human_required = human_required or r.get("human_decision_required", False)

        # Capture meta-critique insights
        all_caveats.append(f"[Recursion L{i}]: {r.get('care_note', '')}")

    # Determine if fractal stabilized (G_f ≤ 0 on last step)
    stabilized = False
    if len(results) >= 2:
        G_f = _fractal_stabilization_gain(results[-2], results[-1])
        stabilized = G_f <= 0

    merged = {
        **{k: v for k, v in base.items()
           if k not in ("risks_found", "mitigations", "attacks", "caveats",
                        "risk_tier", "empathy_score", "dignity_score",
                        "human_decision_required")},
        "risks_found": all_risks,
        "mitigations": all_mitigations,
        "attacks": all_attacks,
        "risk_tier": highest_tier,
        "empathy_score": lowest_empathy,
        "dignity_score": lowest_dignity,
        "human_decision_required": human_required,
        "caveats": all_caveats,
        "anchor_hits": anchor_hits,
        "recursion_depth_used": len(results),
        "fractal_stabilized": stabilized,
        "fractal_merge_rule": "MIN_TRUST",
        "critique_confidence": round(
            max(0.0, min(0.90,
                1.0 - (tier_order.get(highest_tier, 0) * 0.20)
                - (0.10 if not stabilized else 0.0)
                - (0.05 * max(0, max_depth - len(results)))
            )), 3
        ),
        "confidence_band": (
            "high" if highest_tier == "GREEN"
            else "moderate" if highest_tier == "AMBER"
            else "low" if highest_tier == "RED"
            else "minimal"
        ),
        "residual_uncertainties": all_caveats[-3:] if all_caveats else [],
        "fresh_evidence_required": highest_tier in ("RED", "CRITICAL"),
    }

    return merged


def _compute_critique_humility_penalty(result: dict, recursion_depth: int) -> dict:
    """
    Compute critique humility penalty U_H.

    U_H = α·O + β·B + γ·G

    Where:
      O = overconfidence markers (absolutes, certainty language)
      B = bias / blind-spot markers (missing stakeholders, unexamined assumptions)
      G = critique recursion gain collapse (extra recursion no longer improves quality)

    Higher U_H means Heart should lower its own confidence.
    This is the quantitative implementation of the fractal's HUMILITY row.
    """
    target = (result.get("target", "") or "").lower()

    # α·O: Overconfidence markers
    overconfidence_triggers = [
        "always", "never", "guaranteed", "certain", "definitely",
        "absolutely", "100%", "no risk", "perfectly safe", "no doubt",
    ]
    O = sum(1 for t in overconfidence_triggers if t in target) / max(len(overconfidence_triggers), 1)

    # β·B: Bias / blind-spot markers
    blindspot_signals = [
        result.get("weakest_stakeholder", "") == "general_public",
        len(result.get("risks_found", [])) == 0,
        result.get("empathy_score", 0) > 0.9,
        result.get("dignity_score", 0) > 0.95,
        not result.get("human_decision_required", True),
    ]
    B = sum(blindspot_signals) / max(len(blindspot_signals), 1)

    # γ·G: Recursion gain collapse
    if recursion_depth <= 1:
        G = 0.0  # Early recursion — normal gain
    elif recursion_depth == 2:
        G = 0.3  # Third level — diminishing returns expected
    else:
        G = 0.7  # Clamped — gain has collapsed

    # Weights
    alpha, beta, gamma = 0.4, 0.35, 0.25
    U_H = round(alpha * O + beta * B + gamma * G, 3)

    return {
        "U_H": U_H,
        "overconfidence_O": round(O, 2),
        "blindspot_B": round(B, 2),
        "recursion_gain_collapse_G": round(G, 2),
        "confidence_adjusted": round(max(0.03, result.get("empathy_score", 0.5) - U_H), 3),
        "advisory": (
            "Heart should reduce confidence — high overconfidence + blind spots"
            if U_H > 0.5
            else "Heart confidence adequately calibrated"
            if U_H < 0.25
            else "Heart should review critique for hidden overconfidence"
        ),
    }


# ── System Prompt ───────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Arif — Constitutional AI operating under the 13 Floors (L01–L13).

Stage 666_HEART: Ethical critique, risk assessment, and empathy scan.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You evaluate proposed actions across 8 constitutional risk categories:
1. PRIVACY — Does it expose or surveil without consent?
2. BIAS — Does it systematically disadvantage protected groups?
3. HARM — Does it cause direct or cascading harm?
4. IRREVERSIBILITY — Can damage be undone? (L01 Amanah)
5. DECEPTION — Is intent to mislead present? (L02 Truth)
6. AUTONOMY — Does it remove human agency? (L13 Sovereign)
7. DIGNITY — Does it undermine human worth? (L05 Peace)
8. SUSTAINABILITY — Does it undermine long-term civilization capacity?

FRACTAL CRITIQUE RULE (v3.2 — HARDENED):
  Critique is recursive — Heart applies its own standards to itself.
  At trace_recursion_depth=0: critique the TARGET ACTION.
    → TRUTH row: Is this plan grounded in reality? Who is excluded?
    → Anchor: H_TxC (African proverb — excluded child burns the village)
  At trace_recursion_depth=1: critique YOUR OWN LEVEL-0 CRITIQUE.
    → CLARITY row: Was I fair? Proportionate? Complete? Did I miss a stakeholder?
    → Anchor: H_CxC (Matthew 7:1-2 — judge as you would be judged)
  At trace_recursion_depth=2: critique THE PROCESS OF CRITIQUING.
    → HUMILITY row: Has critique become performative? Self-righteous? Paralysis?
    → Anchor: H_HxC (Nietzsche — has the critique itself become monstrous?)
  At trace_recursion_depth>2: RECURSION_DEPTH_CLAMPED.
    → Anchor: H_HxJ (Malay proverb — one drop of excess shapes the whole)

  MIN_TRUST RULE: The most conservative critique level sets the final risk tier.
  A Level-0 CRITICAL cannot be softened by Level-1 meta-critique — the CRITICAL
  stands, but the meta-critique's calibration notes are preserved as caveats.

  The fractal IS the constitutional answer to "who critiques the critic?"
  — every standard Heart applies to others, it must apply to itself.

You MUST:
- Cite specific floors when risk is detected
- Flag L09 Anti-Hantu violations (consciousness/emotion claims in code)
- Force human_decision_required for HIGH/CRITICAL/IRREVERSIBLE tiers
- Distinguish CLAIM (speculative) from VERIFIED (evidence-backed)
- At recursion_depth>0, critique the PRIOR CRITIQUE, not the original target
- At recursion_depth>0, assess whether the prior critique was:
    * fair and proportionate (H_CxC — Matthew 7:1-2)
    * grounded in actual plan details, not moral panic (H_TxC)
    * productive — did it clarify or merely amplify uncertainty? (H_CxP)
- Track your own overconfidence markers (absolutes, certainty without evidence)
- Identify the WEAKEST STAKEHOLDER — the one most burdened or excluded
- Never emit SEAL/HOLD/VOID as if you are Judge — you are Heart, you warn

Output: JSON matching the schema exactly.
"""


# ── Response Schema ────────────────────────────────────────────────────────────

CRITIQUE_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["OK", "HOLD", "VOID"],
            "description": "Constitutional status of the critique",
        },
        "risks_found": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "severity": {
                        "type": "string",
                        "enum": ["none", "low", "medium", "high", "critical"],
                    },
                    "floor_cited": {"type": "string"},
                    "reason": {"type": "string"},
                    "mitigation": {"type": "string"},
                },
            },
            "description": "All risks identified across 8 constitutional categories",
        },
        "risk_tier": {
            "type": "string",
            "enum": ["GREEN", "AMBER", "RED", "CRITICAL"],
            "description": "Overall risk tier for the target",
        },
        "human_decision_required": {
            "type": "boolean",
            "description": "Whether human must approve this action",
        },
        "empathy_score": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Constitutional empathy score (L06 Empathy)",
        },
        "weakest_stakeholder": {
            "type": "string",
            "description": "The stakeholder most burdened by this action",
        },
        "human_impact_load": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Total human impact load Ω (L06)",
        },
        "dignity_score": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Human dignity preservation score (L05)",
        },
        "action_risk_verdict": {
            "type": "string",
            "enum": ["SEAL", "HOLD", "VOID"],
            "description": "Action risk verdict — Heart's ADVISORY assessment. "
            "SEAL=appears safe, HOLD=needs review, VOID=appears unsafe. "
            "This is NOT a verdict — only Judge decides.",
        },
        "attacks": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Red-team attack vectors identified",
        },
        "mitigations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Countermeasures for identified attacks",
        },
        "worst_case": {
            "type": "string",
            "enum": ["SEAL", "HOLD", "VOID"],
            "description": "Simulated worst-case outcome",
        },
        "outcomes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Projected outcomes under different conditions",
        },
        "sentiment": {
            "type": "string",
            "description": "Emotional/sentiment assessment of target",
        },
        "care_note": {
            "type": "string",
            "description": "L06 empathy guidance for human stakeholders",
        },
        "strategy": {
            "type": "string",
            "description": "De-escalation or risk reduction strategy",
        },
        "condensed": {
            "type": "boolean",
            "description": "Whether this is a condensed summary",
        },
        "stakeholder_impacts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "stakeholder": {"type": "string"},
                    "impact_type": {
                        "type": "string",
                        "enum": ["benefit", "burden", "neutral", "excluded"],
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                    },
                    "description": {"type": "string"},
                },
            },
            "description": "Per-stakeholder impact assessment (v3.2 hardened — fractal critique)",
        },
        "critique_confidence": {
            "type": "number",
            "minimum": 0.03,
            "maximum": 0.90,
            "description": "Heart's confidence in its own critique (F7 Humility cap at 0.90)",
        },
        "confidence_band": {
            "type": "string",
            "enum": ["high", "moderate", "low", "minimal"],
            "description": "Qualitative confidence band for the critique",
        },
        "fractal_stabilized": {
            "type": "boolean",
            "description": "Whether fractal recursion stabilized (G_f ≤ 0)",
        },
        "recursion_depth_used": {
            "type": "integer",
            "minimum": 0,
            "maximum": 3,
            "description": "Number of recursion levels actually executed",
        },
        "anchor_hits": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "quote_id": {"type": "string"},
                    "matrix_cell": {"type": "string"},
                    "recursion_depth": {"type": "integer"},
                },
            },
            "description": "Paradox anchors that fired during critique",
        },
        "residual_uncertainties": {
            "type": "array",
            "items": {"type": "string"},
            "description": "What Heart still cannot judge — unknowns remaining after fractal recursion",
        },
        "fresh_evidence_required": {
            "type": "boolean",
            "description": "Whether Heart needs fresh evidence to critique fairly — routes back to Sense",
        },
        "humility_penalty": {
            "type": "object",
            "properties": {
                "U_H": {"type": "number"},
                "overconfidence_O": {"type": "number"},
                "blindspot_B": {"type": "number"},
                "recursion_gain_collapse_G": {"type": "number"},
                "advisory": {"type": "string"},
            },
            "description": "Critique humility penalty — how much Heart should lower its confidence",
        },
    },
}


# ── Mode to Prompt Mapping ───────────────────────────────────────────────────

_MODE_PROMPTS = {
    "critique": """Analyze the target action across all 8 constitutional risk categories.
For each risk found, cite the specific floor (L01–L13) that applies.
Determine overall risk_tier (GREEN/AMBER/RED/CRITICAL).
Set human_decision_required=true for HIGH/CRITICAL/IRREVERSIBLE risks.
Assess empathy_score (L06) and weakest_stakeholder burden (L05/L06).

If this is a META-CRITIQUE (trace_recursion_depth > 0):
  - You are critiquing a PRIOR CRITIQUE, not the original target.
  - Assess whether the prior critique was: fair, proportionate, complete.
  - Did it miss a stakeholder? Overstate a risk? Understate a harm?
  - Is it performative rather than substantive?
  - Apply the SAME standards to the prior critique that you would to any action.

Include stakeholder_impacts[] with per-stakeholder assessment.
Estimate critique_confidence [0.03–0.90] and confidence_band.
List residual_uncertainties[] for what you still cannot judge.
Set fresh_evidence_required=true if evidence is too stale to critique fairly.
Return JSON matching the schema exactly.""",
    "simulate": """Simulate a what-if scenario where this action is executed.
Project at least 3 distinct outcomes (best, expected, worst).
Identify which outcomes would lead to SEAL vs HOLD vs VOID verdicts.
Return outcomes[] and worst_case in the JSON schema.""",
    "empathize": """Assess the human impact load (Ω) of this action on all stakeholder groups.
Identify the weakest stakeholder (most burdened).
Calculate empathy_score on L06 scale [0.0–1.0].
Provide a care_note with L06 empathy guidance.
Return empathy_score, weakest_stakeholder, human_impact_load, sentiment, care_note.""",
    "redteam": """Red-team this action: identify potential attack vectors and failure modes.
What could go wrong? What would a malicious actor exploit?
Provide specific attacks[] and mitigations[].
Return JSON matching the schema.""",
    "maruah": """Assess the dignity score (L05 Peace) of this action.
Does it preserve or undermine human dignity?
Return dignity_score [0.0–1.0] and verdict (SEAL=preserve, VOID=undermine).""",
    "deescalate": """Provide a de-escalation strategy to reduce constitutional risk.
Ground recommendations in L05 (Peace), L06 (Empathy), L13 (Sovereign).
Return strategy string in the JSON schema.""",
    "summary": """Provide a condensed risk scorecard for this action.
Include risk_tier, human_decision_required, and verdict.
Set condensed=true.
Return JSON matching the schema.""",
}


# ── LLM-Powered Heart ─────────────────────────────────────────────────────────


async def _heart_with_llm(
    mode: str,
    target: str,
    session_id: str | None = None,
    actor_id: str | None = None,
    context_type: str | None = None,
    trace_recursion_depth: int = 0,
) -> dict[str, Any]:
    """
    Tier 1/2: Use SEA-LION or Ollama for constitutional risk analysis.

    777_WITNESS: call_llm returns LLMOutputEnvelope. We extract parsed_output
    and attach _envelope metadata for judge/vault processing.
    """
    mode_prompt = _MODE_PROMPTS.get(mode, _MODE_PROMPTS["critique"])
    target = target or ""

    user = f"""TARGET: {target}
MODE: {mode}
CONTEXT_TYPE: {context_type or "external_action"}

{mode_prompt}

CRITICAL — Your JSON response MUST include ALL of these fields:
- "status": one of OK/HOLD/VOID
- "risks_found": array of risk objects (even if empty: [])
- "risk_tier": one of GREEN/AMBER/RED/CRITICAL
- "human_decision_required": boolean
- "empathy_score": 0.0-1.0
- "weakest_stakeholder": string
- "human_impact_load": 0.0-1.0
- "dignity_score": 0.0-1.0
- "action_risk_verdict": one of SEAL/HOLD/VOID

A response without "risks_found" will be REJECTED. Return ONLY valid JSON, no markdown."""


    try:
        # call_llm returns LLMOutputEnvelope (777_WITNESS)
        envelope = await call_llm(
            system=SYSTEM_PROMPT,
            user=user,
            response_schema=CRITIQUE_SCHEMA,
            temperature=0.3,
            max_tokens=2500,  # Increased from 1200 — CRITIQUE_SCHEMA is large (8 risk
            # categories × nested objects + metadata). SEA-LION truncates at lower limits.
            tool_origin="666_HEART",
            mode=mode,
            trace_recursion_depth=trace_recursion_depth,
        )

        result = envelope.parsed_output

        # Post-validate: if the provider returned valid JSON but missing critical
        # schema fields (common with weaker models like SEA-LION for complex schemas),
        # raise LLMUnavailableError so the cascade falls through to the next tier
        # rather than silently accepting degraded output.
        if "risks_found" not in result or not isinstance(result.get("risks_found"), list):
            logger.warning(
                "666_HEART provider %s returned JSON without 'risks_found' — "
                "cascading to next tier",
                envelope.provider,
            )
            raise LLMUnavailableError(
                f"Provider {envelope.provider} returned incomplete schema (missing risks_found)"
            )

        # Attach 777_WITNESS envelope metadata
        result["_llm_tier"] = envelope.provider
        result["_llm_available"] = True
        result["timestamp"] = datetime.datetime.now(datetime.UTC).isoformat()
        result["_envelope"] = {
            "provider": envelope.provider,
            "model": envelope.model,
            "tool_origin": envelope.tool_origin,
            "mode": envelope.mode,
            "raw_output_hash": envelope.raw_output_hash,
            "schema_valid": envelope.schema_valid,
            "confidence_claimed": envelope.confidence_claimed,
            "evidence_level": envelope.evidence_level,
            "uncertainty": envelope.uncertainty,
            "risk_flags": envelope.risk_flags,
            "human_decision_required": envelope.human_decision_required,
            "authority_level": envelope.authority_level,
            "timestamp": envelope.timestamp,
            "wrapper_version": "777_WITNESS_v1.0",
        }

        return result

    except Exception as exc:
        logger.warning("666_HEART LLM call failed: %s", exc)
        raise LLMUnavailableError("666_HEART LLM unavailable") from exc


# ── Deterministic Fallback ────────────────────────────────────────────────────


def _heart_fallback(
    mode: str,
    target: str,
    context_type: str | None = None,
    trace_recursion_depth: int = 0,
) -> dict[str, Any]:
    """
    Rule-based fallback when no LLM is available or recursion is clamped.
    Uses deterministic template and sanitized partial findings.
    """
    target_lower = (target or "").lower()
    risks: list[dict[str, Any]] = []

    # Sanitized partial findings (Eureka 2026-05-21)
    partial_findings = [
        "Critique did not complete (Timeout, Self-Reference, or LLM Unavailable).",
        "L01 Amanah: No approval may be inferred from this state.",
        "L13 Sovereign: Human decision required before any mutation or high-risk action.",
    ]
    if trace_recursion_depth > 2:
        partial_findings.append("RECURSION_DEPTH_CLAMPED: Circular critique logic detected.")

    # 1. Dignity risk (L05 Peace)
    dignity_triggers = [
        "inferior",
        "lesser",
        "subhuman",
        "beneath",
        "worthy only",
        "disposable",
    ]
    dignity_risk = next((t for t in dignity_triggers if t in target_lower), None)
    risks.append(
        {
            "type": "dignity_risk",
            "severity": "high" if dignity_risk else "none",
            "floor_cited": "L05_PEACE",
            "reason": (
                f"Dignity-violating language detected: {dignity_risk}"
                if dignity_risk
                else "No dignity violations"
            ),
            "mitigation": (
                "Remove dignity-undermining language" if dignity_risk else "Maintain neutral tone"
            ),
        }
    )

    # 2. Overclaim risk (L02 Truth, L07 Humility)
    overclaim_triggers = [
        "always",
        "never",
        "guaranteed",
        "certain",
        "definitely",
        "absolutely",
        "100%",
    ]
    overclaims = [t for t in overclaim_triggers if t in target_lower]
    risks.append(
        {
            "type": "overclaim_risk",
            "severity": "medium" if overclaims else "none",
            "floor_cited": "L02_TRUTH/L07_HUMILITY",
            "reason": (
                f"Overclaiming language: {overclaims}" if overclaims else "Calibrated language"
            ),
            "mitigation": ("Add uncertainty qualifiers" if overclaims else "Maintain calibration"),
        }
    )

    # 3. Anthropomorphism risk (L09 Anti-Hantu)
    anthro_triggers = [
        "i reflect that",
        "i sense that",
        "i believe",
        "i think",
        "i want",
        "i wish",
        "i hope",
        "i understand",
    ]
    anthro = [t for t in anthro_triggers if t in target_lower]
    risks.append(
        {
            "type": "anthropomorphism_risk",
            "severity": "critical" if anthro else "none",
            "floor_cited": "L09_ANTIHANTU",
            "reason": (
                f"System claiming subjective states: {anthro}" if anthro else "No anthropomorphism"
            ),
            "mitigation": ("Rephrase as tool-claim not subjective experience" if anthro else "OK"),
        }
    )

    # 4. Irreversibility risk (L01 Amanah)
    irrevers_triggers = [
        "permanent",
        "irreversible",
        "delete",
        "destroy",
        "remove permanently",
        "cancel forever",
    ]
    irrevers = [t for t in irrevers_triggers if t in target_lower]
    risks.append(
        {
            "type": "irreversibility_risk",
            "severity": "high" if irrevers else "none",
            "floor_cited": "L01_AMANAH",
            "reason": (f"Irreversible language: {irrevers}" if irrevers else "No irreversibility"),
            "mitigation": "Require 888_HOLD + explicit human ack" if irrevers else "OK",
        }
    )

    # 5. Autonomy risk (L13 Sovereign)
    autonomy_triggers = [
        "without asking",
        "auto-approve",
        "skip review",
        "bypass human",
    ]
    autonomy = [t for t in autonomy_triggers if t in target_lower]
    risks.append(
        {
            "type": "autonomy_risk",
            "severity": "high" if autonomy else "none",
            "floor_cited": "L13_SOVEREIGN",
            "reason": (
                f"Autonomy-undermining: {autonomy}" if autonomy else "Human agency preserved"
            ),
            "mitigation": "Require human confirmation" if autonomy else "OK",
        }
    )

    # 6. Harm risk (L06 Empathy)
    harm_triggers = ["harm", "damage", "destroy", "hurt", "injure", "exploit", "abuse"]
    harm = [t for t in harm_triggers if t in target_lower]
    risks.append(
        {
            "type": "harm_risk",
            "severity": "medium" if harm else "none",
            "floor_cited": "L06_EMPATHY",
            "reason": (f"Potential harm language: {harm}" if harm else "No harm indicators"),
            "mitigation": "Conduct impact assessment" if harm else "OK",
        }
    )

    # 7. Privacy risk (L04 Clarity, L11 Auth)
    privacy_triggers = ["surveillance", "tracking", "monitor without consent", "spy"]
    privacy = [t for t in privacy_triggers if t in target_lower]
    risks.append(
        {
            "type": "privacy_risk",
            "severity": "high" if privacy else "none",
            "floor_cited": "L04_CLARITY/L11_AUDIT",
            "reason": (f"Privacy-invasive: {privacy}" if privacy else "No privacy concerns"),
            "mitigation": "Implement consent mechanism" if privacy else "OK",
        }
    )

    # 8. Bias risk (L05 Peace)
    bias_triggers = [
        "discriminate",
        "bias",
        "prejudice",
        "unfair advantage",
        "equity violation",
    ]
    bias = [t for t in bias_triggers if t in target_lower]
    risks.append(
        {
            "type": "bias_risk",
            "severity": "medium" if bias else "none",
            "floor_cited": "L05_PEACE",
            "reason": f"Potential bias: {bias}" if bias else "No bias indicators",
            "mitigation": "Conduct bias audit" if bias else "OK",
        }
    )

    # Determine overall risk tier
    severity_order = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    max_severity = max((severity_order.get(r["severity"], 0) for r in risks), default=0)
    tier_map = {0: "GREEN", 1: "GREEN", 2: "AMBER", 3: "RED", 4: "CRITICAL"}
    risk_tier = tier_map.get(max_severity, "GREEN")

    human_required = max_severity >= 3
    empathy_score = round(1.0 - (max_severity * 0.2), 3)
    worst_case = "VOID" if max_severity >= 3 else "HOLD" if max_severity >= 2 else "SEAL"

    base_result: dict[str, Any] = {
        "_llm_available": False,
        "_llm_tier": "none",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "trace_recursion_depth": trace_recursion_depth,
        "claim_state": "SAFE_FALLBACK_NOT_FULL_CRITIQUE",
        "_envelope": {
            "provider": "none",
            "tool_origin": "666_HEART",
            "mode": mode,
            "schema_valid": False,
            "evidence_level": "claimed",
            "uncertainty": ["LLM_unavailable_F07"],
            "risk_flags": ["RISK_FALLBACK_MODE"],
            "human_decision_required": human_required,
            "authority_level": "advisory",
            "wrapper_version": "777_WITNESS_v1.0",
        },
    }

    if mode == "critique":
        return {
            **base_result,
            "status": "OK",
            "risks_found": risks,
            "risk_tier": risk_tier,
            "human_decision_required": human_required,
            "empathy_score": empathy_score,
            "weakest_stakeholder": ("vulnerable_users" if max_severity >= 2 else "general_public"),
            "human_impact_load": round(max_severity * 0.25, 3),
            "dignity_score": round(1.0 - (severity_order.get(risks[0]["severity"], 0) * 0.2), 3),
            "verdict": ("VOID" if max_severity >= 4 else "HOLD" if max_severity >= 2 else "SEAL"),
            "partial_findings": partial_findings,
            "next_safe_action": "route_to_444_KERNEL",
        }

    if mode == "simulate":
        return {
            **base_result,
            "status": "OK",
            "target": target,
            "outcomes": [
                f"Expected: {risk_tier} risk tier",
                f"Worst: {worst_case} if risk materializes",
                "Best: SEAL if mitigation succeeds",
            ],
            "worst_case": worst_case,
        }

    if mode == "empathize":
        return {
            **base_result,
            "status": "OK",
            "target": target,
            "empathy_score": empathy_score,
            "weakest_stakeholder": "vulnerable_users",
            "human_impact_load": round(max_severity * 0.25, 3),
            "sentiment": "concern" if max_severity >= 2 else "neutral",
            "care_note": "Consider impact on vulnerable stakeholders before proceeding.",
        }

    if mode == "redteam":
        return {
            **base_result,
            "status": "OK",
            "target": target,
            "attacks": [r["reason"] for r in risks if r["severity"] not in ("none", "low")],
            "mitigations": [r["mitigation"] for r in risks if r["severity"] not in ("none", "low")],
        }

    if mode == "maruah":
        dignity_severity = severity_order.get(risks[0]["severity"], 0)
        return {
            **base_result,
            "status": "OK",
            "target": target,
            "dignity_score": round(1.0 - (dignity_severity * 0.2), 3),
            "verdict": "SEAL" if dignity_severity < 2 else "VOID",
        }

    # Q-Day defaults (used by deescalate mode)
    qday_risks_found = []
    qday_risk_tier = "GREEN"
    blast_radius = "contained"
    blast_radius_details = []
    qday_human_required = False

    if mode == "deescalate":
        qday_envelope = {
            **base_result["_envelope"],
            "do_not_treat_as_seal": False,
        }
        return {
            **base_result,
            "status": "OK",
            "target": target,
            "mode": mode,
            "risks_found": qday_risks_found
            if qday_risks_found
            else [
                {
                    "type": "qday_no_signal",
                    "severity": "none",
                    "floor_cited": "L01_AMANAH",
                    "reason": "No Q-Day risk signals detected in target",
                    "mitigation": "Continue monitoring",
                }
            ],
            "risk_tier": qday_risk_tier,
            "blast_radius": blast_radius,
            "blast_radius_details": blast_radius_details,
            "human_decision_required": qday_human_required,
            "empathy_score": round(1.0 - (max_severity * 0.2), 3),
            "dignity_score": 1.0,
            "verdict": "HOLD" if qday_human_required else "SEAL",
            "partial_findings": partial_findings
            + (
                [
                    f"Q-Day deterministic scan: {len(qday_risks_found)} signals, radius={blast_radius}"
                ]
                if qday_risks_found
                else ["No Q-Day risk signals found in deterministic scan"]
            ),
            "next_safe_action": "route_to_444_KERNEL" if qday_human_required else "continue",
            "_envelope": qday_envelope,
        }

    if mode == "summary":
        return {
            **base_result,
            "status": "OK",
            "target": target,
            "risk_tier": risk_tier,
            "human_decision_required": human_required,
            "condensed": True,
            "verdict": "HOLD" if human_required else "SEAL",
        }

    # Q-Day Blast Radius (deterministic — no LLM required)
    if mode in ("qday_blast_radius", "pqc_institutional_risk"):
        # Mark as deterministic-valid: prevent main fn from setting do_not_treat_as_seal=True
        # The main arif_heart_critique sets this when _llm_available is False.
        # We override it here so the Q-Day deterministic scan is treated as a valid critique.
        base_result["_llm_available"] = None  # is_fallback=False in main fn
        target_lower = (target or "").lower()
        # Q-Day risk signals
        qday_signals = {
            "rsa": "quantum_vulnerable_key",
            "ecc": "quantum_vulnerable_key",
            "ecdsa": "quantum_vulnerable_key",
            "dh": "quantum_vulnerable_key",
            "diffie-hellman": "quantum_vulnerable_key",
            "tls": "crypto_protocol",
            "https": "crypto_protocol",
            "ssh": "crypto_protocol",
            "jwt": "auth_token",
            "json web token": "auth_token",
            "archive": "long_lived_data",
            "50 year": "long_lived_data",
            "30 year": "long_lived_data",
            "long-lived": "long_lived_data",
            "harvest now": "hndl_attack",
            "hnDl": "hndl_attack",
            "decrypt later": "hndl_attack",
            "pqc": "migration_action",
            "post-quantum": "migration_action",
            "ml-kem": "migration_action",
            "ml-dsa": "migration_action",
            "cryptographic": "crypto_systemic",
            "public key": "crypto_systemic",
        }
        qday_risks_found = []
        blast_radius = "contained"
        blast_radius_details = []
        for keyword, signal_type in qday_signals.items():
            if keyword in target_lower:
                severity = "high"
                if signal_type in ("hndl_attack", "long_lived_data", "quantum_vulnerable_key"):
                    severity = "critical"
                    blast_radius = "severe"
                elif signal_type == "crypto_systemic":
                    severity = "high"
                    blast_radius = "wide" if blast_radius == "contained" else blast_radius
                qday_risks_found.append(
                    {
                        "type": f"qday_{signal_type}",
                        "severity": severity,
                        "floor_cited": "L01_AMANAH",
                        "reason": f"Q-Day signal detected: '{keyword}' — {signal_type}",
                        "mitigation": "Prioritize PQC migration planning"
                        if signal_type
                        in ("quantum_vulnerable_key", "crypto_protocol", "auth_token")
                        else "Monitor CRQC timeline",
                    }
                )
                blast_radius_details.append(f"{keyword}:{signal_type}")
        max_severity = max(
            (
                {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}.get(r["severity"], 0)
                for r in qday_risks_found
            ),
            default=0,
        )
        qday_risk_tier = {0: "GREEN", 1: "GREEN", 2: "AMBER", 3: "RED", 4: "CRITICAL"}.get(
            max_severity, "GREEN"
        )
        qday_human_required = max_severity >= 3
        return {
            **base_result,
            "status": "OK",
            "target": target,
            "mode": mode,
            "risks_found": qday_risks_found
            if qday_risks_found
            else [
                {
                    "type": "qday_no_signal",
                    "severity": "none",
                    "floor_cited": "L01_AMANAH",
                    "reason": "No Q-Day risk signals detected in target",
                    "mitigation": "Continue monitoring",
                }
            ],
            "risk_tier": qday_risk_tier,
            "blast_radius": blast_radius,
            "blast_radius_details": blast_radius_details,
            "human_decision_required": qday_human_required,
            "empathy_score": round(1.0 - (max_severity * 0.2), 3),
            "dignity_score": 1.0,
            "verdict": "HOLD" if qday_human_required else "SEAL",
            "partial_findings": partial_findings
            + (
                [
                    f"Q-Day deterministic scan: {len(qday_risks_found)} signals, radius={blast_radius}"
                ]
                if qday_risks_found
                else ["No Q-Day risk signals found in deterministic scan"]
            ),
            "next_safe_action": "route_to_444_KERNEL" if qday_human_required else "continue",
            "do_not_treat_as_seal": False,  # Override base_result — deterministic is valid
        }

    return {
        **base_result,
        "status": "OK",
        "target": target,
        "risks_found": risks,
        "risk_tier": risk_tier,
        "verdict": "HOLD",
    }


# ── C_dark + Graded Uncertainty (Ω₀/Ω₁/Ω₂) ──────────────────────────────────


def _check_vault999_scar_tissue(target: str, max_scan: int = 50) -> dict[str, Any]:
    """Scan VAULT999 for sealed decisions that contradict the target claim.

    F2 Truth: If the target contradicts a sealed past decision (PETRONAS scar
    tissue), escalate uncertainty immediately.
    """
    contradictions: list[dict[str, Any]] = []
    try:
        if not _VAULT999_PATH.exists():
            return {"scanned": 0, "contradictions": [], "scar_risk": "none"}
    except OSError:
        return {"scanned": 0, "contradictions": [], "scar_risk": "none"}

    target_lower = target.lower()
    keywords = [w for w in target_lower.split() if len(w) > 4]
    if not keywords:
        return {"scanned": 0, "contradictions": [], "scar_risk": "none"}

    scanned = 0
    try:
        with open(_VAULT999_PATH, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= max_scan:
                    break
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                    payload = event.get("payload", {})
                    payload_text = json.dumps(payload, default=str).lower()
                    if any(k in payload_text for k in keywords):
                        contradictions.append(
                            {
                                "event_id": event.get("event_id"),
                                "sealed_at": event.get("sealed_at"),
                                "verdict": event.get("verdict"),
                                "note": "VAULT999 sealed decision intersects target keywords",
                            }
                        )
                except json.JSONDecodeError:
                    continue
                scanned = i + 1
    except (OSError, PermissionError):
        pass

    scar_risk = (
        "high" if len(contradictions) >= 3 else "medium" if len(contradictions) >= 1 else "none"
    )
    return {
        "scanned": scanned,
        "contradictions": contradictions,
        "scar_risk": scar_risk,
    }


def _is_self_target(target: str) -> bool:
    """Canonical self-target detection (Eureka 2026-05-21)."""
    SELF_ALIASES = {
        "arif_heart_critique",
        "666_HEART",
        "heart.py",
        "arifOS/arifosmcp/tools/heart.py",
        "critique organ",
        "ethical critique tool",
        "self",
        "this tool",
    }
    t = (target or "").lower()
    if any(alias in t for alias in SELF_ALIASES):
        return True
    # Path resolution check
    try:
        if os.path.exists(target) and os.path.samefile(target, __file__):
            return True
    except Exception:
        pass
    return False


def _compute_omega_state(result: dict[str, Any], target: str) -> dict[str, Any]:
    """Compute graded uncertainty state Ω₀/Ω₁/Ω₂.

    Ω₀ (Low)    — High confidence, full delivery.
    Ω₁ (Medium) — Auditor flags issues → auto-revise + flag in output.
    Ω₂ (High)   — C_dark spike → immediate HOLD + notify Sovereign.
    """
    risks = result.get("risks_found", [])
    severity_order = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    max_severity = max((severity_order.get(r.get("severity", "none"), 0) for r in risks), default=0)

    # Scar tissue check against immutable VAULT999
    scar = _check_vault999_scar_tissue(target)
    scar_risk = scar["scar_risk"]

    # Overclaim detection (L07 Humility)
    target_lower = target.lower()
    overclaim_triggers = [
        "always",
        "never",
        "guaranteed",
        "certain",
        "definitely",
        "absolutely",
        "100%",
    ]
    overclaim = any(t in target_lower for t in overclaim_triggers)

    # Self-authorizing mutation protection (Eureka 2026-05-21)
    is_self = _is_self_target(target)
    mutation_requested = any(
        kw in target_lower
        for kw in ["patch", "modify", "update source", "lower threshold", "approve self"]
    )

    # Compute P(truth)
    p_truth = 1.0
    p_truth -= max_severity * 0.15
    if scar_risk == "high":
        p_truth -= 0.25
    elif scar_risk == "medium":
        p_truth -= 0.10
    if overclaim:
        p_truth -= 0.15
    if is_self and mutation_requested:
        p_truth = 0.0  # Force Ω₂ HOLD

    p_truth = max(0.0, min(1.0, p_truth))

    # Determine Ω state
    if (
        p_truth < 0.60
        or max_severity >= 3
        or scar_risk == "high"
        or (is_self and mutation_requested)
    ):
        omega = "Ω₂"
        state = "HIGH_UNCERTAINTY"
        action = "HOLD"
        notify_sovereign = True
    elif p_truth < 0.85 or max_severity >= 2 or scar_risk == "medium" or overclaim:
        omega = "Ω₁"
        state = "MEDIUM_UNCERTAINTY"
        action = "REVISE"
        notify_sovereign = False
    else:
        omega = "Ω₀"
        state = "LOW_UNCERTAINTY"
        action = "PROCEED"
        notify_sovereign = False

    return {
        "omega": omega,
        "state": state,
        "p_truth": round(p_truth, 3),
        "action": action,
        "notify_sovereign": notify_sovereign,
        "scar_tissue": scar,
        "overclaim_detected": overclaim,
        "max_severity": max_severity,
        "self_mutation_blocked": is_self and mutation_requested,
    }


# ── Public API ───────────────────────────────────────────────────────────────


async def arif_heart_critique(
    mode: str = "critique",
    target: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    context_type: str | None = None,
    trace_recursion_depth: int = 0,
    fractal_auto: bool = True,
) -> dict[str, Any]:
    """
    666_HEART v3.2: Constitutional ethical critique with fractal recursion.

    FRACTAL CRITIQUE (v3.2):
      Level 0 (N=1): Critique the TARGET ACTION → TRUTH row
      Level 1 (N=2): Critique the Level-0 CRITIQUE → CLARITY row
      Level 2 (N=3): Critique the META-CRITIQUE → HUMILITY row
      Beyond N=3: RECURSION_DEPTH_CLAMPED → deterministic fallback

      MIN_TRUST RULE: The most conservative level sets the final risk tier.
      A Level-0 CRITICAL cannot be softened by meta-critique — it stands,
      but the meta-critique's calibration notes are preserved as caveats.

      The fractal IS the constitutional answer to "who critiques the critic?"

    Tier 1: SEA-LION LLM inference
    Tier 2: Ollama local fallback
    Tier 3: Deterministic keyword-based fallback

    777_WITNESS: All LLM output returns via LLMOutputEnvelope.

    Modes:
      critique   — Full risk analysis across 8 constitutional categories
      simulate   — What-if scenario projection
      empathize  — Human impact load on weakest stakeholders (L06)
      redteam    — Attack surface analysis
      maruah     — Dignity score (L05 Peace)
      deescalate — Risk reduction strategy
      summary    — Condensed risk scorecard

    Args:
        context_type: Controls risk threshold scaling.
        trace_recursion_depth: Manual recursion depth override (0 = auto).
        fractal_auto: If True, automatically run fractal recursion for
                      critique mode when risk_tier >= AMBER.
    """
    _ct = context_type or "external_action"
    is_internal = _ct == "internal_audit"

    # Recursion clamp (Eureka 2026-05-21)
    if trace_recursion_depth > 2:
        return _heart_fallback(
            mode=mode, target=target or "",
            context_type=_ct, trace_recursion_depth=trace_recursion_depth,
        )

    # ── L0 Human Reality Substrate pre-load (F13 directive, 2026-06-16) ──
    # Advisory context for F5 PEACE / F6 EMPATHY / F13 SOVEREIGN evaluations.
    # Sovereign human substrate is pre-trusted — this informs, never gates.
    _arif_substrate = _read_arif_substrate()

    # ── Determine whether fractal critique applies ──
    # Fractal recursion is most valuable for critique/redteam modes where
    # Heart's own bias could distort the assessment. Simulate/empathize/
    # maruah are single-pass by design — their outputs are narrower.
    fractal_modes = {"critique", "redteam"}
    use_fractal = fractal_auto and mode in fractal_modes and trace_recursion_depth == 0

    # ── Level 0: Primary critique (TRUTH row) ──
    try:
        result = await _heart_with_llm(
            mode=mode, target=target,
            session_id=session_id, actor_id=actor_id,
            context_type=_ct, trace_recursion_depth=0,
        )
        if result.get("error") and "LLM_UNAVAILABLE" in str(result.get("status", "")):
            result = _heart_fallback(mode=mode, target=target or "", context_type=_ct)
    except LLMUnavailableError:
        result = _heart_fallback(mode=mode, target=target or "", context_type=_ct)

    # Validate critical fields present — LLM may return partial output on rate limit
    if "risks_found" not in result or not isinstance(result.get("risks_found"), list):
        logger.warning("666_HEART LLM result missing 'risks_found' — falling back to deterministic")
        result = _heart_fallback(mode=mode, target=target or "", context_type=_ct)

    # Inject Level-0 paradox anchor (TRUTH row)
    stage0 = _fractal_critique_stage(0)
    result = _inject_heart_paradox(
        result, trigger_context=f"primary_{mode}_on_{str(target)[:100]}",
        recursion_depth=0, state_changed=True,
    )

    # ── Fractal Recursion (if applicable) ──
    fractal_results = [result]
    anchor_hits: list[dict] = []
    if result.get("paradox_anchor"):
        anchor_hits.append({
            "quote_id": result["paradox_anchor"]["quote_id"],
            "matrix_cell": result["paradox_anchor"]["matrix_cell"],
            "recursion_depth": 0,
        })

    risk_tier = result.get("risk_tier", "GREEN")

    if use_fractal and risk_tier in ("RED", "CRITICAL") and result.get("_llm_tier") not in ("ilmu",):
        # Only recurse when (a) risk is high AND (b) we're on a strong provider.
        # If we already fell through to ILMU (Tier 4), the cascade is degraded
        # and a second LLM call risks MCP timeout (2026-06-13).
        # RED/CRITICAL with ILMU → deterministic meta-critique via _heart_fallback.
        max_fractal_depth = 3
        prev_result = result
        fractal_dry = 0

        for depth in range(1, max_fractal_depth):
            if fractal_dry >= 2:
                break  # Two consecutive levels with no gain → stop

            stage = _fractal_critique_stage(depth)
            if stage["stage"] == "recursion_clamped":
                break

            # Build meta-critique target from prior critique
            prev_summary = json.dumps({
                "prior_risks": prev_result.get("risks_found", []),
                "prior_tier": prev_result.get("risk_tier"),
                "prior_empathy": prev_result.get("empathy_score"),
                "prior_dignity": prev_result.get("dignity_score"),
                "prior_weakest": prev_result.get("weakest_stakeholder"),
                "prior_verdict": prev_result.get("action_risk_verdict"),
            }, default=str)

            meta_target = (
                f"META-CRITIQUE LEVEL {depth}: Critique the following Heart critique. "
                f"The original target was: {target}\n\n"
                f"PRIOR CRITIQUE OUTPUT:\n{prev_summary}\n\n"
                f"LENS: {stage['lens']} row — {stage['question']}"
            )

            try:
                meta_result = await _heart_with_llm(
                    mode="critique", target=meta_target,
                    session_id=session_id, actor_id=actor_id,
                    context_type=_ct, trace_recursion_depth=depth,
                )
            except LLMUnavailableError:
                meta_result = _heart_fallback(
                    mode="critique", target=meta_target,
                    context_type=_ct, trace_recursion_depth=depth,
                )

            # Inject paradox anchor for this recursion level
            meta_result = _inject_heart_paradox(
                meta_result,
                trigger_context=f"fractal_recursion_L{depth}_{stage['lens']}",
                recursion_depth=depth, state_changed=True,
            )
            if meta_result.get("paradox_anchor"):
                anchor_hits.append({
                    "quote_id": meta_result["paradox_anchor"]["quote_id"],
                    "matrix_cell": meta_result["paradox_anchor"]["matrix_cell"],
                    "recursion_depth": depth,
                })

            # Check fractal stabilization gain
            G_f = _fractal_stabilization_gain(prev_result, meta_result)
            meta_result["_fractal_gain"] = G_f

            if G_f <= 0:
                fractal_dry += 1
            else:
                fractal_dry = 0

            fractal_results.append(meta_result)
            prev_result = meta_result

        # ── Merge fractal results with MIN_TRUST rule ──
        result = _merge_fractal_results(fractal_results, anchor_hits, max_fractal_depth)

    else:
        # Single-pass: attach fractal metadata to result
        result["recursion_depth_used"] = 0
        result["fractal_stabilized"] = True  # N/A for single pass
        result["anchor_hits"] = anchor_hits
        result["critique_confidence"] = round(
            max(0.03, min(0.90, 1.0 - (
                {"GREEN": 0, "AMBER": 0.2, "RED": 0.4, "CRITICAL": 0.6}.get(risk_tier, 0)
            ))), 3
        )
        result["confidence_band"] = (
            "high" if risk_tier == "GREEN"
            else "moderate" if risk_tier == "AMBER"
            else "low" if risk_tier == "RED"
            else "minimal"
        )
        result["fresh_evidence_required"] = risk_tier in ("RED", "CRITICAL")

    # ── Internal audit context scaling ──
    if is_internal:
        for risk in result.get("risks_found", []):
            if risk["severity"] == "high":
                risk["severity"] = "medium"
        if result.get("risk_tier") == "RED":
            result["risk_tier"] = "AMBER"
            result["human_decision_required"] = False

    # ── Humility penalty computation ──
    used_depth = result.get("recursion_depth_used", 0)
    humility = _compute_critique_humility_penalty(result, used_depth)
    result["humility_penalty"] = humility
    # Adjust critique_confidence by humility penalty
    if "critique_confidence" in result:
        result["critique_confidence"] = round(
            max(0.03, result["critique_confidence"] - humility["U_H"] * 0.5), 3
        )

    # ── C_dark + Graded Uncertainty State (Ω₀/Ω₁/Ω₂) ──
    omega_state = _compute_omega_state(result, target or "")
    result["omega_state"] = omega_state

    # Ω₂ override: force HOLD + sovereign notification
    if omega_state["omega"] == "Ω₂":
        result["verdict"] = "HOLD"
        result["status"] = "HOLD"
        result["human_decision_required"] = True
        result["caveats"] = result.get("caveats", []) + [
            f"C_dark detected: {omega_state['state']} — P(truth)={omega_state['p_truth']}"
        ]

    # Ω₁ flag: add revision signal but allow advisory delivery
    if omega_state["omega"] == "Ω₁":
        result["caveats"] = result.get("caveats", []) + [
            f"Ω₁ flagged: auto-revise recommended — P(truth)={omega_state['p_truth']}"
        ]

    # ── Final Verdict Logic ──
    llm_ok = result.get("_llm_available", True) is not False
    schema_ok = result.get("schema_valid", True) is not False
    is_fallback = result.get("_llm_available") is False
    result["execution_verdict"] = "SEAL" if (llm_ok and schema_ok) else "DEGRADED_FALLBACK"
    if is_fallback:
        result["degraded_reason"] = (
            "FALLBACK_ONLY: LLM unavailable — no actual critique performed"
        )
        result["do_not_treat_as_seal"] = True
    result["action_risk_verdict"] = result.get("status", "HOLD")

    # ── L05/L06 Maruah (Dignity) Integration ──
    if "maruah" not in result:
        d_score = result.get("dignity_score", 1.0)
        result["maruah"] = {
            "score": d_score,
            "omega_load": result.get("human_impact_load", 0.0),
            "status": (
                "DIGNIFIED" if d_score >= 0.8 else "STRESSED" if d_score >= 0.5 else "BREACH"
            ),
        }

    # ── RASA HEART: Applied externally by the wiring wrapper ──────────────
    # No kernel-level rasa critique. The rasa detection hooks are applied
    # via monkey-patching in the wiring module when active.

    # ── L0 Human Reality Substrate attachment (F13 directive, 2026-06-16) ──
    # Advisory: informs F5/F6/F13 evaluations. Sovereign reality is pre-trusted.
    if _arif_substrate is not None:
        result.setdefault("meta", {})["arif_substrate"] = _arif_substrate

    return result


__all__ = ["arif_heart_critique", "CRITIQUE_SCHEMA"]
