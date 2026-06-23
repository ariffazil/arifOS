"""
arifosmcp/tools/sense.py — 111_SENSE v3 (Reality-Wired)
═══════════════════════════════════════════════════════════════

Reality-grounded observation and agentic sensing — the epistemic actuator
that converts uncertainty into planned sensing trajectories under budget,
policy, and dignity constraints.

TRINITY FLOW (v3):
  Sense is the eye that moves on purpose. It sits between Memory ("what is
  already known"), Mind ("what can be inferred"), and Judge ("what may be
  authorized"). Sense answers: "what should we look at next, how, and why?"

  Memory ──coverage gaps──→ SENSE ←──NEED_EVIDENCE── Mind
                              │
                              ▼
                         SENSE_PLAN → OBSERVATION_PACKET → Memory (store)
                              │                              │
                              └──────── Judge (authorize) ←──┘

THREE SUBMODES:
  A. Recall-first sensing  — ask Memory first, escalate to active if stale
  B. External agentic search — decompose, search, fetch, verify, replan
  C. Active sensing — probe environment (logs, metrics, screen, DOM)

FIVE LAYERS:
  1. Trigger — NEED_EVIDENCE, low coverage, stale memory, operator request
  2. Plan — decompose query, estimate VOI, select sources, set budget
  3. Select — route to web/repo/graph/API/vision based on plan
  4. Verify — provenance, freshness, conflict check, sufficiency grade
  5. Emit — OBSERVATION_PACKET, SENSE_PLAN, SENSE_GAP (never verdict)

STOP RULES:
  Stop when: coverage ≥ τ_c, trust ≥ τ_t, VOI ≤ τ_v, or budget exhausted.

PARADOX ANCHORS (v3): 9 anchors in 3×3 matrix, completing the 4-organ system:
  Sense + Memory + Mind + Judge = 36 anchors across the constitutional matrix.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

from arifosmcp.paradox import build_organ_anchors, register_organ
from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.reality_handlers import handler as reality_handler
from arifosmcp.runtime.reality_models import BundleInput
from arifosmcp.runtime.session_auth import validate_session
from arifosmcp.runtime.tools import _hold, _ok, _sabar

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# RASA DETECTION — External (applied via monkey-patching when enabled)
# ═══════════════════════════════════════════════════════════════════════════════
# NO kernel-level rasa imports. Rasa detection is applied externally via
# the wiring module at arifosmcp/rasa/ when wiring is active.


# ═══════════════════════════════════════════════════════════════════════════════
# PARADOX ANCHORS — 3×3 Orthogonal Matrix for Sense
# ═══════════════════════════════════════════════════════════════════════════════
# Completes the 4-organ system: Sense + Memory + Mind + Judge = 36 anchors.
# Rows: TRUTH / CLARITY / HUMILITY   Columns: CARE / PEACE / JUSTICE
# Each anchor separates QUOTE (verified) from BINDING (firing policy).
# ═══════════════════════════════════════════════════════════════════════════════

SENSE_PARADOX_ANCHORS: list[dict] = [
    # ── TRUTH ROW ──────────────────────────────────────────────────────────────
    {
        "id": "S_TxC",
        "matrix_cell": "truth_care",
        "matrix_row": "TRUTH",
        "matrix_col": "CARE",
        "motto_binding": "DIKAJI, BUKAN DISUAPI",
        "quote": {
            "text": "In God we trust; all others bring data.",
            "author": "W. Edwards Deming",
            "work": "Attributed — quality management principle",
            "year": "c. 1980s",
            "verification_level": "traditional_attribution",
        },
        "antithesis": "But data is not truth — it is measured reality through a specific instrument under specific conditions. The map is not the territory.",
        "axis": "evidence vs. truth",
        "binding": {
            "event": "search_launched",
            "trigger": "external search initiated — evidence must be grounded, not assumed",
            "effect": "attach_provenance_requirement",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "sense",
        "norm": "WAJIB",
    },
    {
        "id": "S_TxP",
        "matrix_cell": "truth_peace",
        "matrix_row": "TRUTH",
        "matrix_col": "PEACE",
        "motto_binding": "DIJELASKAN, BUKAN DIKABURKAN",
        "quote": {
            "text": "The first principle is that you must not fool yourself — and you are the easiest person to fool.",
            "author": "Richard Feynman",
            "work": "Cargo Cult Science, Caltech commencement address",
            "year": "1974",
            "verification_level": "verified_exact",
        },
        "antithesis": "Complete self-skepticism paralyzes observation — you must trust your instruments enough to look, while doubting enough to verify.",
        "axis": "self-skepticism vs. observational trust",
        "binding": {
            "event": "observation_normalized",
            "trigger": "raw observation normalized into claim — verify before trusting",
            "effect": "require_corroboration",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "sense",
        "norm": "WAJIB",
    },
    {
        "id": "S_TxJ",
        "matrix_cell": "truth_justice",
        "matrix_row": "TRUTH",
        "matrix_col": "JUSTICE",
        "motto_binding": "DISEDARKAN, BUKAN DIYAKINKAN",
        "quote": {
            "text": "What I cannot create, I do not understand.",
            "author": "Richard Feynman",
            "work": "Written on his blackboard at Caltech at time of death",
            "year": "1988",
            "verification_level": "verified_exact",
        },
        "antithesis": "But sensing is not creating — you can observe what you cannot build. Observation precedes construction; construction confirms observation.",
        "axis": "observation vs. understanding",
        "binding": {
            "event": "observation_packet_emitted",
            "trigger": "observation complete — observation ≠ understanding, Mind must still reason",
            "effect": "annotate_observation_not_conclusion",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "cross_organ",
        "norm": "WAJIB",
    },
    # ── CLARITY ROW ────────────────────────────────────────────────────────────
    {
        "id": "S_CxC",
        "matrix_cell": "clarity_care",
        "matrix_row": "CLARITY",
        "matrix_col": "CARE",
        "motto_binding": "DIJELAJAH, BUKAN DISEKATI",
        "quote": {
            "text": "The important thing is not to stop questioning. Curiosity has its own reason for existing.",
            "author": "Albert Einstein",
            "work": "Statement to William Miller, LIFE magazine",
            "year": "1955",
            "verification_level": "verified_exact",
        },
        "antithesis": "Curiosity without budget is chaos — the sensing system must stop questioning when the expected gain falls below the cost of asking.",
        "axis": "curiosity vs. discipline",
        "binding": {
            "event": "replan_loop",
            "trigger": "sensing replan triggered — curiosity is engine, budget is brake",
            "effect": "check_voi_before_replan",
        },
        "severity_on_fire": "warn",
        "risk_bias": "neutral",
        "authority_scope": "sense",
        "norm": "HARUS",
    },
    {
        "id": "S_CxP",
        "matrix_cell": "clarity_peace",
        "matrix_row": "CLARITY",
        "matrix_col": "PEACE",
        "motto_binding": "DIHADAPI, BUKAN DITANGGUHI",
        "quote": {
            "text": "We don't see things as they are, we see them as we are.",
            "author": "Anaïs Nin",
            "work": "Seduction of the Minotaur",
            "year": "1961",
            "verification_level": "verified_exact",
        },
        "antithesis": "But instruments see differently than humans — the whole point of sensing is to escape the limitations of the observer. Triangulate across instruments.",
        "axis": "observer bias vs. instrumental objectivity",
        "binding": {
            "event": "single_source_observation",
            "trigger": "only one source found — single-perspective risk",
            "effect": "flag_single_source_and_request_triangulation",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "sense",
        "norm": "WAJIB",
    },
    {
        "id": "S_CxJ",
        "matrix_cell": "clarity_justice",
        "matrix_row": "CLARITY",
        "matrix_col": "JUSTICE",
        "motto_binding": "DIUSAHAKAN, BUKAN DIHARAPI",
        "quote": {
            "text": "It is the mark of an educated mind to be able to entertain a thought without accepting it.",
            "author": "Aristotle",
            "work": "Nicomachean Ethics (paraphrase tradition)",
            "year": "4th century BCE",
            "verification_level": "traditional_attribution",
            "translation_note": "Widely attributed; exact wording varies across translations of Metaphysics and NE.",
        },
        "antithesis": "Entertaining a thought indefinitely without accepting or rejecting it is the refusal to sense — observation must eventually settle into a claim, even if tentative.",
        "axis": "openness vs. closure",
        "binding": {
            "event": "sufficiency_grading",
            "trigger": "observation sufficiency graded — enough observation to claim, or must keep looking?",
            "effect": "grade_and_decide",
        },
        "severity_on_fire": "warn",
        "risk_bias": "neutral",
        "authority_scope": "cross_organ",
        "norm": "HARUS",
    },
    # ── HUMILITY ROW ───────────────────────────────────────────────────────────
    {
        "id": "S_HxC",
        "matrix_cell": "humility_care",
        "matrix_row": "HUMILITY",
        "matrix_col": "CARE",
        "motto_binding": "DIJAGA, BUKAN DIABAIKAN",
        "quote": {
            "text": "The greatest enemy of knowledge is not ignorance, it is the illusion of knowledge.",
            "author": "Stephen Hawking",
            "work": "Attributed — widely cited public statement",
            "year": "c. 1990s",
            "verification_level": "traditional_attribution",
        },
        "antithesis": "But the illusion of ignorance is also dangerous — refusing to observe because you think you know nothing is as paralyzing as observing because you think you know everything.",
        "axis": "illusion of knowledge vs. illusion of ignorance",
        "binding": {
            "event": "coverage_check",
            "trigger": "pre-search coverage check — don't search if memory already knows, but don't assume memory is complete",
            "effect": "check_memory_first_then_decide",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "cross_organ",
        "norm": "WAJIB",
    },
    {
        "id": "S_HxP",
        "matrix_cell": "humility_peace",
        "matrix_row": "HUMILITY",
        "matrix_col": "PEACE",
        "motto_binding": "DIDAMAIKAN, BUKAN DIPANASKAN",
        "quote": {
            "text": "It is better to know some of the questions than all of the answers.",
            "author": "James Thurber",
            "work": "Attributed — American humorist",
            "year": "c. 1940s",
            "verification_level": "traditional_attribution",
        },
        "antithesis": "But governance requires answers, not questions — Sense must eventually produce observations that can ground decisions, not just a longer list of unknowns.",
        "axis": "questions vs. answers",
        "binding": {
            "event": "gap_report_emitted",
            "trigger": "SENSE_GAP emitted — acknowledge unknowns but don't celebrate them",
            "effect": "annotate_gap_with_next_action",
        },
        "severity_on_fire": "info",
        "risk_bias": "neutral",
        "authority_scope": "sense",
        "norm": "SUNAT",
    },
    {
        "id": "S_HxJ",
        "matrix_cell": "humility_justice",
        "matrix_row": "HUMILITY",
        "matrix_col": "JUSTICE",
        "motto_binding": "DITEMPA, BUKAN DIBERI",
        "quote": {
            "text": "Measure what is measurable, and make measurable what is not so.",
            "author": "Galileo Galilei",
            "work": "Attributed — paraphrase of principles from The Assayer and other works",
            "year": "c. 1623",
            "verification_level": "traditional_attribution",
        },
        "antithesis": "Not everything that matters can be measured — dignity, justice, and truth resist quantification. Sense must observe what it can and name what it cannot.",
        "axis": "measurability vs. meaning",
        "binding": {
            "event": "sensing_complete",
            "trigger": "sensing cycle complete — what was measured and what remains unmeasurable",
            "effect": "report_measured_and_unmeasurable",
        },
        "severity_on_fire": "info",
        "risk_bias": "neutral",
        "authority_scope": "sense",
        "norm": "SUNAT",
    },
]

_SENSE_BY_CELL: dict[str, dict] = {a["matrix_cell"]: a for a in SENSE_PARADOX_ANCHORS}
_SENSE_BY_ID: dict[str, dict] = {a["id"]: a for a in SENSE_PARADOX_ANCHORS}

# ── Register with global paradox registry (Phase 1 wiring) ──────────────────
_sense_anchors = build_organ_anchors("sense", SENSE_PARADOX_ANCHORS)
_sense_registry = register_organ("sense", _sense_anchors)


# ═══════════════════════════════════════════════════════════════════════════════
# AGENTIC SEARCH PLANNER — VOI-Driven Sensing
# ═══════════════════════════════════════════════════════════════════════════════


def _agentic_search_plan(
    need_evidence: dict | None = None,
    prior_coverage: float = 0.0,
    prior_trust: float = 0.0,
    budget_steps: int = 4,
) -> dict:
    """
    Build an agentic sensing plan from NEED_EVIDENCE or query context.

    This is the planner layer — converts "we need to know X" into
    "look at Y using tool Z, stop when conditions met."

    Returns SENSE_PLAN dict with subquestions, candidate tools, budget,
    and stop conditions. Does NOT execute — that's the router's job.
    """
    query = ""
    urgency = "MEDIUM"
    required_quality = 0.7

    if need_evidence and isinstance(need_evidence, dict):
        topics = need_evidence.get("topics", [])
        query = topics[0].get("topic", "") if topics else ""
        urgency = need_evidence.get("urgency", "MEDIUM")
        required_quality = need_evidence.get("min_trust", 0.7)

    # ── Decompose query into subquestions ──
    subquestions = []
    if query:
        subquestions.append(
            {"id": "sq1", "text": f"What is the ground truth about: {query[:120]}?"}
        )
        subquestions.append(
            {"id": "sq2", "text": f"What sources are authoritative for: {query[:120]}?"}
        )
        if urgency == "HIGH":
            subquestions.append(
                {"id": "sq3", "text": "Are there contradictory claims that need triangulation?"}
            )

    # ── VOI estimate: is sensing worth it? ──
    coverage_gap = max(0.0, required_quality - prior_coverage)
    trust_gap = max(0.0, required_quality - prior_trust)
    voi = round(0.5 * coverage_gap + 0.3 * trust_gap + 0.2 * (1.0 if urgency == "HIGH" else 0.5), 3)

    # ── Select candidate tools ──
    candidate_tools = ["memory"]  # always check memory first
    if voi > 0.3:
        candidate_tools.append("web")
    if "repo" in query.lower() or "code" in query.lower() or "file" in query.lower():
        candidate_tools.append("repo")
    if "log" in query.lower() or "metrics" in query.lower() or "health" in query.lower():
        candidate_tools.append("inspect")

    # ── Budget and stop conditions ──
    max_steps = budget_steps
    if urgency == "HIGH":
        max_steps = min(budget_steps + 2, 8)
    elif urgency == "LOW":
        max_steps = max(budget_steps - 1, 1)

    stop_conditions = [
        f"coverage >= {required_quality}",
        f"trust >= {required_quality}",
        "voi <= 0.05",
        f"budget_exhausted: steps >= {max_steps}",
    ]

    plan = {
        "type": "SENSE_PLAN",
        "goal": f"Reduce uncertainty about: {query[:200]}" if query else "General sensing",
        "subquestions": subquestions,
        "candidate_tools": candidate_tools,
        "voi_estimate": voi,
        "budget": {
            "max_steps": max_steps,
            "current_step": 0,
        },
        "stop_conditions": stop_conditions,
        "prior_state": {
            "coverage_before": prior_coverage,
            "trust_before": prior_trust,
        },
    }

    # ── Attach paradox anchor ──
    if voi < 0.1:
        plan["paradox_hint"] = "S_HxC"  # Hawking: illusion of knowledge — memory might be enough
    elif urgency == "HIGH":
        plan["paradox_hint"] = "S_TxC"  # Deming: bring data — urgent gap demands evidence

    return plan


def _grade_sensing_sufficiency(
    observations: list[dict],
    prior_coverage: float,
    prior_trust: float,
    required_quality: float = 0.7,
) -> dict:
    """
    Grade whether sensing has gathered enough evidence.

    Returns {sufficient: bool, coverage_delta, trust_delta, recommendation}.
    """
    if not observations:
        return {
            "sufficient": False,
            "coverage_delta": 0.0,
            "trust_delta": 0.0,
            "recommendation": "REPLAN",
            "paradox_hint": "S_HxP",  # Thurber: better to know questions than all answers
        }

    # Compute post-sensing metrics
    trust_scores = [o.get("trust", 0.5) for o in observations if isinstance(o, dict)]
    avg_trust = sum(trust_scores) / len(trust_scores) if trust_scores else 0.5
    source_count = len(
        set(o.get("source_type", "unknown") for o in observations if isinstance(o, dict))
    )

    # Coverage: simple heuristic — more sources = broader coverage
    coverage_gain = min(source_count * 0.15, 0.4)
    new_coverage = min(prior_coverage + coverage_gain, 1.0)
    trust_gain = max(0.0, avg_trust - prior_trust)

    sufficient = new_coverage >= required_quality and avg_trust >= required_quality

    # Paradox anchor for sufficiency decision
    paradox_hint = None
    if not sufficient and source_count == 1:
        paradox_hint = "S_CxP"  # Nin: single perspective — need triangulation
    elif sufficient:
        paradox_hint = "S_HxJ"  # Galileo: measure what is measurable — cycle complete

    return {
        "sufficient": sufficient,
        "coverage_after": round(new_coverage, 3),
        "trust_after": round(avg_trust, 3),
        "coverage_delta": round(coverage_gain, 3),
        "trust_delta": round(trust_gain, 3),
        "source_count": source_count,
        "recommendation": "STOP" if sufficient else "REPLAN",
        "paradox_hint": paradox_hint,
    }


def _calculate_discovery_physics(
    query: str,
    local_wiki_matches: list[dict],
    repo_index_matches: list[dict],
    web_matches: list[dict],
) -> dict[str, Any]:
    """
    Discovery Physics Kernel — Epistemic telemetry for hybrid discovery.
    Calculates uncertainty reduction, evidence level, and witness consensus.
    """
    try:
        from arifosmcp.runtime.a_rif import contradiction, engine, prompt_injection, source_rank

        def _W_4(H, A, E, V):
            """Manual F3 Quad-Witness Consensus helper."""
            product = H * A * E * V
            return product**0.25

    except ImportError:
        return {
            "claim_state": "unknown",
            "evidence_level": "L0",
            "delta_s": 0.0,
            "omega_0": 0.04,
            "w4": 0.0,
            "contradiction_state": "VOID",
            "quarantine_clean": True,
        }

    # 1. Search Worthiness (W)
    freshness = 1.0
    if query and any(k in query.lower() for k in ("current", "latest", "now", "today", "2026")):
        freshness = 2.0
    uncertainty = 0.8 if not (local_wiki_matches or repo_index_matches) else 0.4
    w_score = engine.calculate_search_worthiness(
        uncertainty=uncertainty,
        importance=1.0,
        freshness=freshness,
        background_confidence=0.1 if not (local_wiki_matches or repo_index_matches) else 0.6,
    )
    # Cap search worthiness to keep it operationally sane (e.g., max 10.0)
    w_score = min(w_score, 10.0)

    # 2. Evidence Level (L)
    max_rank = 9
    for hit in web_matches:
        url = hit.get("url", "")
        rank = source_rank.rank_source(url)
        if rank < max_rank:
            max_rank = rank
    evidence_level = source_rank.evidence_level_from_rank(max_rank)
    if (local_wiki_matches or repo_index_matches) and web_matches:
        evidence_level = "L3"
    elif local_wiki_matches or repo_index_matches:
        evidence_level = "L2"
    elif not web_matches:
        evidence_level = "L0"

    # 3. Entropy Delta (ΔS)
    before = 0.8
    after = 0.4 if (local_wiki_matches or repo_index_matches or web_matches) else 0.8
    delta_s = engine.evaluate_entropy_delta(before, after)

    # 4. Humility (Omega)
    omega_0 = 0.04

    # 5. Witness Consensus (W4)
    h_val = 1.0 if (local_wiki_matches or repo_index_matches) else 0.1
    a_val = 0.8
    e_val = 0.9 if web_matches else 0.1
    v_val = 0.7
    w4 = _W_4(h_val, a_val, e_val, v_val)

    # 6. Contradictions
    claims = []
    for h in local_wiki_matches + repo_index_matches:
        claims.append({"text": h.get("excerpt", ""), "source": "local"})
    for h in web_matches:
        claims.append({"text": h.get("description", "") or h.get("snippet", ""), "source": "web"})
    audit = contradiction.audit_for_contradictions(claims)

    # 7. Injection Scan
    all_text = " ".join([c["text"] for c in claims])
    quarantine = prompt_injection.scan_for_injection(all_text)

    # 8. Claim State
    claim_state = "hypothesis"
    if w4 > 0.75 and evidence_level in ("L3", "L4"):
        claim_state = "supported"
    if evidence_level in ("L5", "L6"):
        claim_state = "verified"
    if not (local_wiki_matches or repo_index_matches or web_matches):
        claim_state = "unknown"

    return {
        "claim_state": claim_state,
        "evidence_level": str(evidence_level),
        "delta_s": delta_s,
        "omega_0": omega_0,
        "w4": round(w4, 3),
        "search_worthiness": w_score,
        "witness": {"human": h_val, "ai": a_val, "evidence": e_val, "verifier": v_val},
        "contradiction_state": audit.status,
        "quarantine_clean": quarantine.clean,
        "recommendation": "continue" if delta_s < -0.01 else "stop",
    }


def arif_observe(
    mode: str = "search",
    query: str | None = None,
    url: str | None = None,
    layers: list[str] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    partition_mode: str = "ONLINE",
    partition_timeout: int = 30,
    top_k: int = 5,
    render: str = "auto",
) -> dict[str, Any]:
    """
    SENSE tool — reality-wired via RealityHandler.

    Hybrid discovery is READ-ONLY evidence retrieval. It finds what the system
    currently knows across local wiki, repo index, and live web. It does NOT
    store, persist, or write anything. Agents must still decide whether to
    pass findings to memory_recall (persist), mind_reason (reason), or
    judge_deliberate (adjudicate).

    Modes:
      search   → Brave API search (DDGS fallback)
      ingest   → Fetch + ingest URL via RealityHandler compass
      compass  → Governed Discovery Kernel: Orientation before action
      atlas    → Structural layer map (stub — pending vector atlas)
      entropy_dS → Random entropy delta (physics stub)
      vitals   → System vitals stub
    """
    if mode in (
        "geox_quantum_scope",
        "geox_molecular_target_scan",
        "geox_seismic_quantum_lint",
        "geox_pvt_quantum_opportunity",
        "geox_ccus_geochem_scan",
    ):
        return {
            "status": "readonly",
            "message": f"{mode} activated based on GEOX quantum scale classifier.",
        }

    # ── L11 AUTH: Session Validation (Hardened) ───────────────────────────────
    auth = validate_session(session_id, actor_id)
    if not auth["valid"]:
        # If it's a read-only SENSE operation and we have an actor_id,
        # allow a temporary "ephemeral" session for discovery if configured.
        if mode in ("hybrid_discovery", "vitals", "compass", "search") and actor_id:
            logger.debug(f"L11 AUTH: session_id missing for {mode}, using ephemeral context.")
            auth = {
                "valid": True,
                "session": {"actor_id": actor_id, "stage": "111", "ephemeral": True},
                "actor_id": actor_id,
            }
        else:
            if auth.get("expired"):
                return _sabar("arif_observe", auth["reason"], session_id=session_id)
            return _hold("arif_observe", auth["reason"], ["L11"], session_id=session_id)

    q = query or url or ""

    # ── RASA DETECTION: Applied externally by the wiring wrapper ────────────
    # No kernel-level rasa detection. The rasa detection hooks are applied
    # via monkey-patching in the wiring module when active.

    def _inject_rasa(result: dict) -> dict:
        """Placeholder — rasa injection is done by the wiring wrapper."""
        return result

    if mode == "compass":
        from arifosmcp.constitutional_map import CANONICAL_TOOLS
        from arifosmcp.core.authority_gate import AuthorityGate, WitnessType
        from arifosmcp.core.threat_engine import ThreatEngine

        # 1. Knowledge Discovery (Hybrid)
        hd_res = arif_observe(
            mode="hybrid_discovery",
            query=q,
            session_id=session_id,
            actor_id=actor_id,
            top_k=3,
        )
        data = hd_res.get("result", {})
        knowledge = data.get("knowledge_layers", {})

        # 2. Capability Discovery
        allowed_tools = []
        restricted_tools = []
        for tool_name, spec in CANONICAL_TOOLS.items():
            if spec.get("access") == "public":
                allowed_tools.append(tool_name)
            else:
                restricted_tools.append(tool_name)

        # 3. Authority Discovery
        # ThreatEngine scan for risk map
        scan_res = ThreatEngine.scan(q)
        assessment = scan_res.assessment

        # Build minimal ActionContext for AuthorityGate
        class _ActionContext:
            def __init__(self, t_name, m, q_str, a_id):
                self.tool_name = t_name
                self.mode = m
                self.query = q_str
                self.actor_id = a_id
                self.witness_type = WitnessType.AI

            def payload_text(self):
                return self.query

        act_ctx = _ActionContext("arif_observe", "compass", q, actor_id)
        auth_proof = AuthorityGate.verify(act_ctx, assessment)

        # 4. Next Safe Moves
        next_moves = ["Use arif_think to analyze the discovered evidence."]
        if assessment.irreversibility.value > 0:
            next_moves.append(
                "WARNING: Intent detected as high-risk; submit formal plan before action."
            )
        if not knowledge.get("local_wiki", {}).get("matches"):
            next_moves.append("Knowledge gap detected: Ingest relevant docs via arif_wiki_ingest.")

        return _ok(
            "arif_observe",
            {
                "status": "OK",
                "tool": "arif_observe",
                "mode": "compass",
                "query": q,
                "orientation": {
                    "knowledge": knowledge,
                    "capabilities": {
                        "allowed": allowed_tools,
                        "restricted": restricted_tools,
                    },
                    "authority": {
                        "actor": actor_id or "anonymous",
                        "authorized": auth_proof.authorized,
                        "requires_human": auth_proof.requires_human,
                        "reason": auth_proof.reason,
                    },
                    "risk_map": {
                        "tier": scan_res.tier.value,
                        "threats": (
                            [t.name for t in assessment.threats] if assessment.threats else []
                        ),
                        "irreversible": assessment.irreversibility.value > 1,
                    },
                    "next_safe_moves": next_moves,
                },
                "physics": data.get("physics_kernel", {}),
            },
        )

    floor_check = check_laws("arif_observe", {"query": query or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_observe", floor_check["reason"], floor_check["violated_laws"])

    if partition_mode == "DEAD":
        return {
            "status": "HOLD",
            "tool": "arif_observe",
            "result": {},
            "meta": {
                "partition": "DEAD",
                "reason": "Witness unreachable — CANDIDATE_SEAL escalation required",
                "violated_laws": [],
            },
        }

    if partition_mode == "PURGATORY":
        return _ok(
            "arif_observe",
            {
                "query": query,
                "results": [],
                "source": "purgatory_ledger",
                "omega_0": 0.04,
                "partition": "PURGATORY",
                "note": "Witness unreachable — entry cached in Purgatory Ledger",
            },
        )

    if mode == "hybrid_discovery":
        from arifos_wiki_tools.search import search_index

        q = query or ""
        errors: list[str] = []

        # ── Layer 1: Local Wiki (AAA/wiki) ─────────────────────────────────────
        local_wiki_status: str = "UNAVAILABLE"
        local_wiki_matches: list[dict[str, Any]] = []
        try:
            from arifos_wiki_tools.search import _FEDERATION_ROOTS

            AAA_WIKI = _FEDERATION_ROOTS.get("aaa")
            if AAA_WIKI and AAA_WIKI.exists():
                hits = search_index(AAA_WIKI, q, top_k=top_k)
                if hits:
                    local_wiki_status = "FOUND"
                    for hit in hits:
                        hit["federation_organ"] = "aaa"
                        local_wiki_matches.append(hit)
                else:
                    local_wiki_status = "EMPTY"
            else:
                local_wiki_status = "UNAVAILABLE"
                errors.append("AAA/wiki path not accessible")
        except Exception as e:
            local_wiki_status = "UNAVAILABLE"
            errors.append(f"local_wiki search error: {e}")

        # ── Layer 2: Repo Indices (.arifos/wiki_index.jsonl across federation) ───
        repo_index_status: str = "UNAVAILABLE"
        repo_index_matches: list[dict[str, Any]] = []
        try:
            repo_federation_roots = {k: v for k, v in _FEDERATION_ROOTS.items() if k != "aaa"}
            for organ, root_path in repo_federation_roots.items():
                if not root_path.exists():
                    continue
                idx_path = root_path / ".arifos" / "wiki_index.jsonl"
                if not idx_path.exists():
                    continue
                hits = search_index(root_path, q, top_k=top_k)
                if hits:
                    for hit in hits:
                        hit["federation_organ"] = organ
                        repo_index_matches.append(hit)
            if repo_index_matches:
                repo_index_status = "FOUND"
            elif any(
                (root_path / ".arifos" / "wiki_index.jsonl").exists()
                for root_path in repo_federation_roots.values()
                if root_path.exists()
            ):
                repo_index_status = "EMPTY"
            else:
                repo_index_status = "NOT_INDEXED"
        except Exception as e:
            repo_index_status = "UNAVAILABLE"
            errors.append(f"repo_index search error: {e}")

        # ── Layer 3: Web Reality (Brave → DDGS → Meyhem) ───────────────────────
        web_status: str = "UNAVAILABLE"
        web_error: str | None = None
        web_matches: list[dict[str, Any]] = []
        web_engine: str = "none"
        try:
            s_res = asyncio.run(reality_handler.search_brave(q, top_k=top_k))
            if s_res.results:
                web_status = "FOUND"
                web_matches = s_res.results
                web_engine = s_res.engine
            else:
                web_status = "EMPTY"
                web_engine = getattr(s_res, "engine", "unknown")
        except Exception as e:
            web_status = "UNAVAILABLE"
            web_error = str(e)[:120]
            web_engine = "brave"
            errors.append(f"web search error: {e}")

        # ── Reconciliation: Truth Triangulation ───────────────────────────────────
        # v0: keyword-overlap heuristic. Real semantic contradiction detection is v1.
        contradictions: list[str] = []
        unknowns: list[str] = []

        if web_status == "UNAVAILABLE":
            unknowns.append(f"Web source unavailable: {web_error or 'Unknown error'}")

        local_texts = " ".join(
            h.get("excerpt", "") + " " + h.get("rel_path", "")
            for h in local_wiki_matches + repo_index_matches
        ).lower()
        web_texts = " ".join(
            w.get("title", "") + " " + w.get("snippet", "") for w in web_matches
        ).lower()

        # Check: web has relevant info absent from local
        if web_matches and not (local_wiki_matches or repo_index_matches):
            unknowns.append(
                "Web has results but no local source found matching query. "
                "Run arif_wiki_ingest to index the relevant repo."
            )

        # Check: deprecated/stale markers in local
        all_local = local_wiki_matches + repo_index_matches
        for h in all_local:
            excerpt = h.get("excerpt", "").lower()
            if any(tag in excerpt for tag in ("deprecated", "superseded", "renamed")):
                contradictions.append(
                    f"Local source at {h.get('rel_path', '?')} "
                    f"mentions deprecation — cross-check with web recommended."
                )

        # Check: topic agreement between web and local (simple keyword overlap)
        if web_texts and local_texts:
            web_tokens = set(web_texts.split()) & set(q.lower().split())
            local_tokens = set(local_texts.split()) & set(q.lower().split())
            # If web and local share no query-related tokens, note as potential divergence
            if web_tokens and local_tokens and web_tokens.isdisjoint(local_tokens):
                unknowns.append(
                    "Web and local sources both have results but don't share "
                    "query-keyword overlap — possible divergence or different focus."
                )

        # Determine evidence state
        layers_found = sum(
            1 for s in [local_wiki_status, repo_index_status, web_status] if s == "FOUND"
        )
        if layers_found >= 2:
            evidence_state = "FOUND"
            verdict = "PARTIAL"
        elif layers_found == 1:
            evidence_state = "PARTIAL"
            verdict = "SABAR"
        else:
            evidence_state = "EMPTY"
            verdict = "HOLD"

        # Separate facts from matches for clarity
        facts = []
        if local_wiki_matches:
            facts.append(f"Found {len(local_wiki_matches)} matches in AAA wiki.")
        if repo_index_matches:
            facts.append(f"Found {len(repo_index_matches)} matches in local repo index.")
        if web_matches:
            facts.append(f"Web search returned {len(web_matches)} results via {web_engine}.")

        # 5. Physics Kernel
        physics = _calculate_discovery_physics(
            q, local_wiki_matches, repo_index_matches, web_matches
        )

        # Honest confidence and next_safe_action
        if evidence_state == "EMPTY":
            confidence = "low"
            next_safe_action = (
                "No evidence found in any layer. "
                "Consider broadening the query or ingesting relevant repositories."
            )
        elif evidence_state == "PARTIAL":
            confidence = "low"
            next_safe_action = (
                "Partial evidence found. Cross-check local findings against live web "
                "before acting. Do not treat local-only results as current reality."
            )
        else:
            confidence = "medium"
            next_safe_action = (
                "Multiple layers agree. Standard epistemic caution applies. "
                "Verify critical claims with primary sources before proceeding."
            )

        # ── STEP 1 KERNEL BRIDGE ────────────────────────────────────────────────
        # arifOS core/ kernel call — wrapped in compatibility guard.
        # If import or call fails, tool still returns normally (kernel_bridge = "MISS"/"ERROR").
        kernel_bridge: str = "MISS"
        kernel_metrics: dict | None = None
        try:
            import sys as _sys
            from pathlib import Path as _Path

            _WORK = _Path(__file__).resolve().parents[3]  # /workspace/arifOS
            if str(_WORK) not in _sys.path:
                _sys.path.insert(0, str(_WORK))
            from core.governance_kernel import get_governance_kernel

            _gk = get_governance_kernel(session_id or "global")
            _gk.record_event(
                "action",
                {
                    "tool": "arif_observe",
                    "mode": "hybrid_discovery",
                    "query": q,
                    "actor_id": actor_id,
                },
            )
            kernel_result = _gk.evaluate_floors(
                query=q,
                options={
                    "session_id": session_id,
                    "actor_id": actor_id,
                    "human_witness": 0.5,
                    "ai_witness": 0.5,
                    "earth_witness": 0.5,
                },
            )
            kernel_bridge = "HIT"
            # Log the kernel function invoked and payload shape
            print("[KERNEL-BRIDGE] arif_observe → core.governance_kernel.evaluate_floors")
            print(
                f"[KERNEL-BRIDGE]   query={repr(q[:80])}, payload_keys={list(kernel_result.keys())}"
            )
            kernel_metrics = {
                "qdf": kernel_result.get("qdf"),
                "verdict": kernel_result.get("verdict"),
                "floors_tau_truth": kernel_result.get("floors", {}).get("tau_truth"),
                "floors_peace2": kernel_result.get("floors", {}).get("peace2"),
                "floors_kappa_r": kernel_result.get("floors", {}).get("kappa_r"),
                "floors_shadow": kernel_result.get("floors", {}).get("shadow"),
            }
        except Exception as _e:
            kernel_bridge = "ERROR"
            print(f"[KERNEL-BRIDGE-WARN] sense.py → core.governance_kernel: {_e}")

        return _ok(
            "arif_observe",
            _inject_rasa(
                {
                    "status": "OK",
                    "tool": "arif_observe",
                    "mode": "hybrid_discovery",
                    "query": q,
                    "kernel_bridge": kernel_bridge,  # "HIT" | "MISS" | "ERROR"
                    "kernel_metrics": kernel_metrics,  # full metrics if HIT, None if MISS/ERROR
                    "evidence_state": evidence_state,
                    "verdict": verdict,
                    "facts": facts,
                    "knowledge_layers": {
                        "local_wiki": {
                            "status": local_wiki_status,
                            "matches": local_wiki_matches,
                        },
                        "repo_index": {
                            "status": repo_index_status,
                            "matches": repo_index_matches,
                        },
                        "web_reality": {
                            "status": web_status,
                            "source": web_engine,
                            "error": web_error,
                            "matches": web_matches,
                        },
                    },
                    "physics_kernel": physics,
                    "physics": physics,
                    "reconciliation": {
                        "state": "NOT_EVALUATED",
                        "contradictions": contradictions,
                        "unknowns": unknowns,
                    },
                    "confidence": confidence,
                    "next_safe_action": next_safe_action,
                    "contradictions": contradictions,
                    "unknowns": unknowns,
                }
            ),
        )

    if mode == "search":
        # L12 INJECTION guard: scan query for destructive patterns before executing search
        from arifosmcp.core.threat_engine import ThreatEngine

        scan_res = ThreatEngine.scan(query or "")
        if scan_res.assessment.irreversibility.value > 1:
            threat_names = [t.name for t in (scan_res.assessment.threats or [])]
            return _hold(
                "arif_observe",
                f"L12 INJECTION: Destructive pattern detected — {', '.join(threat_names) or 'CRITICAL'}",
                ["L12"],
                session_id=session_id,
            )
        try:
            s_res = asyncio.run(reality_handler.search_brave(query or "", top_k=top_k))
            results = s_res.results if s_res.results else []
            omega_0 = 0.05 + min(len(results) * 0.02, 0.20)
            return _ok(
                "arif_observe",
                _inject_rasa(
                    {
                        "query": query,
                        "results": results,
                        "source": s_res.engine,
                        "verdict": "SEAL" if results else "SABAR",
                        "omega_0": round(omega_0, 3),
                        "partition": "ONLINE",
                        "latency_ms": round(s_res.latency_ms, 1),
                        "note": None if results else "No results — check query or API keys",
                    }
                ),
            )
        except Exception as e:
            logger.warning(f"RealityHandler failure in arif_observe ({mode}): {e}")
            return _ok(
                "arif_observe",
                _inject_rasa(
                    {
                        "query": query,
                        "results": [],
                        "source": "fallback_stub",
                        "verdict": "SABAR",
                        "omega_0": 0.04,
                        "partition": "ONLINE",
                        "note": f"RealityHandler fallback failed: {e}",
                    }
                ),
            )

    if mode == "ingest" and url:
        try:
            bundle = asyncio.run(
                reality_handler.handle_compass(
                    BundleInput(type="url", value=url, mode="fetch", render=render),  # type: ignore[arg-type]
                    auth_context={
                        "actor_id": actor_id or "anonymous",
                        "session_id": session_id or "global",
                    },
                )
            )
            return _ok(
                "arif_observe",
                _inject_rasa(
                    {
                        "url": url,
                        "ingested": bundle.status.state == "SUCCESS",
                        "bundle_id": bundle.id,
                        "status": bundle.status.state,
                        "verdict": bundle.status.verdict,
                        "results_count": len(bundle.results),
                        "partition": "ONLINE",
                        "errors": [
                            {"code": e.code, "detail": e.detail} for e in bundle.status.errors
                        ],
                    }
                ),
            )
        except Exception as e:
            logger.warning(f"RealityHandler failure in arif_observe ({mode}): {e}")
            return _ok(
                "arif_observe",
                _inject_rasa(
                    {
                        "url": url,
                        "ingested": False,
                        "verdict": "SABAR",
                        "partition": "ONLINE",
                        "note": f"RealityHandler fallback failed: {e}",
                    }
                ),
            )

    if mode == "compass":
        value = url or query or ""
        btype = "url" if value.startswith(("http://", "https://")) else "query"
        try:
            bundle = asyncio.run(
                reality_handler.handle_compass(
                    BundleInput(
                        type=btype,  # type: ignore[arg-type]
                        value=value,
                        mode="auto",
                        top_k=top_k,
                        render=render,  # type: ignore[arg-type]
                    ),
                    auth_context={
                        "actor_id": actor_id or "anonymous",
                        "session_id": session_id or "global",
                    },
                )
            )
            return _ok(
                "arif_observe",
                {
                    "heading": bundle.input.mode,
                    "confidence": 0.95 if bundle.status.state == "SUCCESS" else 0.50,
                    "bundle_id": bundle.id,
                    "status": bundle.status.state,
                    "verdict": bundle.status.verdict,
                    "results_count": len(bundle.results),
                    "partition": "ONLINE",
                },
            )
        except Exception as e:
            logger.warning(f"RealityHandler failure in arif_observe ({mode}): {e}")
            return _ok(
                "arif_observe",
                {
                    "heading": "unknown",
                    "confidence": 0.0,
                    "verdict": "SABAR",
                    "partition": "ONLINE",
                    "note": f"RealityHandler fallback failed: {e}",
                },
            )

    if mode == "atlas":
        return _ok(
            "arif_observe",
            {
                "map": {},
                "layers": layers or [],
                "partition": partition_mode,
            },
        )
    if mode == "entropy_dS":
        ds = random.uniform(-0.1, 0.1)
        return _ok(
            "arif_observe",
            {
                "delta_S": round(ds, 6),
                "trend": "stable",
                "partition": partition_mode,
            },
        )
    if mode == "vitals":
        return _ok(
            "arif_observe",
            {
                "cpu": 12.5,
                "mem": 34.0,
                "io": "normal",
                "partition": partition_mode,
            },
        )

    if mode in ("crypto_inventory", "cert_surface", "repo_crypto_scan", "qday_physics_watch"):
        import os
        import re

        import yaml

        try:
            with open("/root/arifOS/config/crypto_patterns.yaml") as f:
                patterns = yaml.safe_load(f).get("crypto_patterns", {})
        except Exception:
            patterns = {}
        findings = []
        fixture_dir = "/root/arifOS/fixtures/qday/"
        if os.path.exists(fixture_dir):
            for root_dir, _, files in os.walk(fixture_dir):
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            c = f.read()
                            for algo, data in patterns.items():
                                matched = False
                                for regex in data.get("regex", []):
                                    if re.search(regex, c, re.IGNORECASE):
                                        findings.append(
                                            {
                                                "path": file_path.replace("/root/arifOS/", ""),
                                                "algorithm": algo.upper(),
                                                "usage": "auth_or_encryption",
                                                "quantum_vulnerable": algo.lower()
                                                in ["rsa", "ecdsa", "dh"],
                                                "confidence": 0.85,
                                            }
                                        )
                                        matched = True
                                        break
                                if matched:
                                    continue
                                for fpat in data.get("files", []):
                                    if fpat in file:
                                        findings.append(
                                            {
                                                "path": file_path.replace("/root/arifOS/", ""),
                                                "algorithm": algo.upper(),
                                                "usage": "config",
                                                "quantum_vulnerable": True,
                                                "confidence": 0.90,
                                            }
                                        )
                                        break
                    except Exception:
                        pass
        return {"mode": mode, "mutation": False, "findings": findings}

    return _hold("arif_observe", f"Unknown mode: {mode}")


# Backward compatibility alias
arif_sense_observe = arif_observe
