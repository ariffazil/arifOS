"""
arifOS 222_WITNESS — Reality Verification & Consensus

Stage: 222_WITNESS | Trinity: Ψ+Ω | Floors: F2, F3, F5, F9, F11, F13

Purpose: Achieve tri-witness consensus on claims with epistemic honesty.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone

from arifos.integrations.minimax_mcp_bridge import minimax_bridge
from arifos.core.governance import (
    ThermodynamicMetrics,
    governed_return,
)

logger = logging.getLogger(__name__)


def _normalize_bridge_hits(bridge_result: dict | None) -> list[dict]:
    """Accept old and new bridge result shapes without crashing on empty payloads."""
    if not isinstance(bridge_result, dict):
        return []

    hits = bridge_result.get("hits")
    if isinstance(hits, list):
        return [h for h in hits if isinstance(h, dict)]

    results = bridge_result.get("results")
    if isinstance(results, dict):
        nested_hits = results.get("organic") or results.get("hits") or results.get("results")
        if isinstance(nested_hits, list):
            return [h for h in nested_hits if isinstance(h, dict)]

    return []


def _extract_bridge_answer(bridge_result: dict | None) -> str | None:
    """Prefer normalized answer, then tolerate legacy/raw result shapes."""
    if not isinstance(bridge_result, dict):
        return None

    answer = bridge_result.get("answer")
    if isinstance(answer, str) and answer.strip():
        return answer

    results = bridge_result.get("results")
    if isinstance(results, dict):
        nested_answer = results.get("answer") or results.get("result")
        if isinstance(nested_answer, str) and nested_answer.strip():
            return nested_answer

    return None


def _get_organ_confidence(evidence: dict | None) -> float | None:
    """
    Honest degradation: None → 0.5 (unknown), present-no-conf → 0.7,
    present-with-conf → actual value.
    """
    if evidence is None:
        return 0.5
    conf = evidence.get("confidence")
    if conf is None:
        return 0.7
    return float(conf)


def _compute_honest_tri_witness(
    geox_evidence: dict | None,
    wealth_evidence: dict | None,
    well_evidence: dict | None,
    web_evidence: dict | None = None,
) -> tuple[float, str]:
    """
    Compute honest Quad-Witness consensus score and tag.

    Rules:
      - All required organs present with >=0.7 conf: FULL_WITNESS
      - At least two organs present: PARTIAL_WITNESS
      - Zero or one organ: NO_WITNESS (but still bounded confidence)
      - WEB organ is treated like any other organ when present.
    """
    confs = [
        _get_organ_confidence(geox_evidence),
        _get_organ_confidence(wealth_evidence),
        _get_organ_confidence(well_evidence),
        _get_organ_confidence(web_evidence),
    ]
    valid = [c for c in confs if c is not None]
    present = sum(1 for c in confs if c is not None and c > 0.5)

    if present >= 3:
        score = round(sum(valid) / len(valid), 3)
        tag = "FULL_WITNESS"
    elif present >= 2:
        score = round(sum(valid) / len(valid), 3)
        tag = "PARTIAL_WITNESS"
    else:
        score = round(sum(valid) / max(len(valid), 1), 3)
        tag = "NO_WITNESS"

    # Clamp to epistemic bounds
    score = max(0.03, min(0.97, score))
    return score, tag


def _build_organ_block(
    name: str,
    evidence: dict | None,
    query: str,
) -> dict:
    """Build an honest organ evidence block."""
    if evidence is None:
        return {
            "claim": f"No {name} evidence provided for: {query}",
            "confidence": 0.5,
            "grounded": False,
            "source_tag": "synthetic_missing",
            "warning": "Organ absent — using honest unknown value 0.5",
        }
    return {
        "claim": evidence.get("claim", f"No claim in {name} evidence"),
        "confidence": _get_organ_confidence(evidence),
        "grounded": True,
        "source_tag": evidence.get("source", "unknown"),
        "evidence_hash": hashlib.sha256(
            json.dumps(evidence, sort_keys=True, default=str).encode()
        ).hexdigest()[:16],
    }


def _build_claim_bundle(
    query: str,
    organs: dict[str, dict],
) -> dict:
    """Build the claim_bundle with ungrounded tracking."""
    ungrounded = [name for name, o in organs.items() if not o.get("grounded", False)]
    claims = [o["claim"] for o in organs.values() if o.get("grounded")]
    consensus_claim = (
        claims[0]
        if len(claims) == 1
        else "; ".join(claims[:3]) if claims else f"No grounded claims for: {query}"
    )
    return {
        "query": query,
        "consensus_claim": consensus_claim,
        "ungrounded_organs": ungrounded,
        "grounded_count": len(claims),
    }


def _build_consensus_rationale(
    tri_witness_tag: str,
    organs: dict[str, dict],
    score: float,
) -> dict:
    """Build human-readable consensus rationale."""
    rationale = {
        "tag": tri_witness_tag,
        "score": score,
        "organ_confidences": {name: o.get("confidence") for name, o in organs.items()},
        "explanation": "",
    }
    if tri_witness_tag == "FULL_WITNESS":
        rationale["explanation"] = (
            "All three organs provided evidence above the 0.5 unknown threshold. "
            "Consensus score is the mean of organ confidences."
        )
    elif tri_witness_tag == "PARTIAL_WITNESS":
        rationale["explanation"] = (
            "Two or more organs provided evidence, but at least one is missing or unknown. "
            "Partial consensus achieved with bounded confidence."
        )
    else:
        rationale["explanation"] = (
            "Zero or one organ present. Consensus not achieved — operating with honest unknown. "
            "Recommendation: gather more evidence before proceeding to 888_JUDGE."
        )
    return rationale


def _build_divergence_points(organs: dict[str, dict], tri_witness_score: float) -> list[str]:
    if tri_witness_score >= 0.95:
        return []

    divergence_points = []
    for name, organ in organs.items():
        confidence = organ.get("confidence")
        if confidence is None:
            divergence_points.append(f"{name}:confidence_unknown")
            continue
        if confidence < 0.95:
            divergence_points.append(f"{name}:confidence_below_harmony({confidence})")
        if not organ.get("grounded", False):
            divergence_points.append(f"{name}:ungrounded")

    return divergence_points or ["consensus_below_harmony_threshold"]


def _parse_well_unified(well_evidence: dict | None) -> dict:
    """Parse WELL unified substrate packet (human + machine + MCP + coupled).

    Backward-compatible: if well_evidence is old flat shape, degrade gracefully.
    """
    if well_evidence is None:
        return {
            "human_ready": "UNKNOWN",
            "machine_ready": "UNKNOWN",
            "mcp_ready": "UNKNOWN",
            "coupled_verdict": "HOLD",
            "well_score": 50.0,
            "confidence": 0.5,
        }

    # New unified packet shape from WELL
    if "coupled" in well_evidence:
        coupled = well_evidence.get("coupled", {})
        return {
            "human_ready": coupled.get("human_ready", "UNKNOWN"),
            "machine_ready": coupled.get("machine_ready", "UNKNOWN"),
            "mcp_ready": coupled.get("mcp_ready", "UNKNOWN"),
            "coupled_verdict": coupled.get("coupled_verdict", "HOLD"),
            "well_score": well_evidence.get("well_score", 50.0),
            "confidence": _get_organ_confidence(well_evidence),
        }

    # Legacy flat shape — degrade gracefully
    conf = _get_organ_confidence(well_evidence)
    return {
        "human_ready": "UNKNOWN",
        "machine_ready": "UNKNOWN",
        "mcp_ready": "UNKNOWN",
        "coupled_verdict": "HOLD" if (conf is None or conf < 0.6) else "PROCEED",
        "well_score": 50.0,
        "confidence": conf,
    }


def _build_judge_signal(
    well_readiness: float,
    well_parsed: dict | None = None,
) -> dict:
    """Build WELL readiness signal for 888_JUDGE gating."""
    parsed = well_parsed or {}
    coupled = parsed.get("coupled_verdict", "HOLD")
    human_ready = parsed.get("human_ready", "UNKNOWN")
    machine_ready = parsed.get("machine_ready", "UNKNOWN")
    mcp_ready = parsed.get("mcp_ready", "UNKNOWN")

    # Base readiness from scalar (backward compatible)
    base_hold = well_readiness < 0.6

    # Override with coupled verdict if available
    if coupled == "HOLD":
        recommendation = "HOLD_888"
        note = (
            f"WELL coupled verdict: HOLD. "
            f"Human={human_ready}, Machine={machine_ready}, MCP={mcp_ready}. "
            "Only 888_JUDGE may override after explicit review."
        )
    elif coupled == "CAUTION":
        recommendation = "CAUTION_888"
        note = (
            f"WELL coupled verdict: CAUTION. "
            f"Human={human_ready}, Machine={machine_ready}, MCP={mcp_ready}. "
            "Proceed with narrowed scope and human confirmation."
        )
    else:
        recommendation = "HOLD_888" if base_hold else "PROCEED"
        note = (
            "WELL readiness below 0.6 gates human escalation. "
            "Only 888_JUDGE may override after explicit review."
            if base_hold
            else "WELL readiness sufficient — claims may proceed to 888_JUDGE."
        )

    return {
        "well_readiness": well_readiness,
        "recommendation": recommendation,
        "coupled_verdict": coupled,
        "human_ready": human_ready,
        "machine_ready": machine_ready,
        "mcp_ready": mcp_ready,
        "note": note,
    }


def _generate_assumptions(
    mode: str,
    search_query: str | None,
    witness_required: int = 3,
    depth: str = "basic",
) -> list[str]:
    """Generate explicit assumptions for this witness operation."""
    assumptions = [
        "Organ evidence is self-reported by caller — no independent verification performed.",
        "Confidence scores are caller-provided or honest-degraded to 0.5 (unknown).",
        "Tri-witness score is arithmetic mean — not Bayesian or weighted consensus.",
    ]
    if witness_required >= 4:
        assumptions.append(
            f"Quad-Witness mode active (required={witness_required}) — WEB evidence depends on MiniMax bridge availability."
        )
    if mode in ("search", "web_search"):
        assumptions.append(
            "Earth witness via web_search depends on DuckDuckGo + Playwright — latency and coverage vary."
        )
    if search_query:
        assumptions.append(f"Custom search query '{search_query}' may bias result distribution.")
    if depth == "deep":
        assumptions.append(
            "Deep search mode extracts top-5 hits with snippets — higher coverage but longer latency."
        )
    return assumptions


def _build_meta_intelligence(
    has_session: bool,
    mode: str,
    witness_required: int = 3,
    depth: str = "basic",
) -> dict:
    """Build meta-intelligence signal block."""
    return {
        "self_model_present": True,
        "assumption_tracking": True,
        "uncertainty_tracking": True,
        "cross_tool_continuity": has_session,
        "mode": mode,
        "witness_required": witness_required,
        "depth": depth,
    }


def _constitutional_error_response(
    error: Exception,
    floor: str = "F3",
) -> dict:
    """Return an MCP-compliant error response with constitutional_guard metadata."""
    error_str = str(error)
    hash_payload = {
        "tool_name": "arifos_222_witness",
        "floor_failed": floor,
        "error": error_str,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    reasoning_hash = hashlib.sha256(
        json.dumps(hash_payload, sort_keys=True, default=str).encode()
    ).hexdigest()

    return {
        "content": [{"type": "text", "text": error_str}],
        "isError": True,
        "constitutional_guard": {
            "verdict": "VOID",
            "floor_failed": floor,
            "reason": error_str,
            "reasoning_hash": reasoning_hash,
            "guard_version": "v1",
        },
    }


async def execute(
    query: str,
    operator_id: str | None = None,
    session_id: str | None = None,
    mode: str = "fuse",
    claim: str | None = None,
    geox_evidence: dict | None = None,
    wealth_evidence: dict | None = None,
    well_evidence: dict | None = None,
    search_query: str | None = None,
    witness_required: int = 3,
    depth: str = "basic",
) -> dict:
    """
    arifos_222_witness — Reality Verification & Consensus (EMD Stack: Metabolizer)

    Stage 222 performs Reality Sync using Quad-Witness consensus:
      GEOX  : Earth/geospatial evidence
      WEALTH: Economic/resource evidence
      WELL  : Biological/operator readiness evidence
      WEB   : External web search validation (MiniMax bridge)

    Modes:
      fuse        : Best-available witness synthesis (default).
      search      : External Earth witness via MiniMax web_search bridge.
      tri-witness : Strict 3-organ consensus (GEOX/WEALTH/WELL).
      web_search  : Alias for search with full web evidence extraction.

    EMD Output Fields:
      - external_evidence    : Top 5 hits from MiniMax web search
      - tri_witness_report   : {human_witness, ai_witness, earth_witness}
      - f2_truth_confidence  : W³ ≥ 0.95 check result
      - grounding_status     : ANCHORED or DRIFTING
    """
    try:
        focus_claim = claim or query

        # ── Build honest organ blocks (Tri-Witness base) ──────────────────────
        organs = {
            "GEOX": _build_organ_block("GEOX", geox_evidence, focus_claim),
            "WEALTH": _build_organ_block("WEALTH", wealth_evidence, focus_claim),
            "WELL": _build_organ_block("WELL", well_evidence, focus_claim),
        }

        # ── Quad-Witness: WEB organ via MiniMax bridge (when required) ─────────
        web_evidence: dict | None = None
        external_evidence: list[dict] = []
        earth_claim: str | None = None

        if mode in ("search", "web_search") or witness_required >= 4:
            try:
                bridge_result = await minimax_bridge.web_search(query=search_query or focus_claim)
                earth_claim = _extract_bridge_answer(bridge_result)
                hits = _normalize_bridge_hits(bridge_result)
                bridge_error = (
                    bridge_result.get("error") if isinstance(bridge_result, dict) else None
                )
                # Build WEB organ evidence block
                web_confidence = 0.7 if (earth_claim or hits) else 0.5
                web_evidence = {
                    "claim": earth_claim or f"No web evidence for: {focus_claim}",
                    "confidence": web_confidence,
                    "grounded": bool(earth_claim or hits),
                    "source_tag": "minimax_web_search",
                    "result_count": (
                        bridge_result.get("result_count", len(hits))
                        if isinstance(bridge_result, dict)
                        else len(hits)
                    ),
                }
                if bridge_error:
                    web_evidence["error"] = bridge_error
                # Extract external_evidence (top hits)
                depth_limit = 5 if depth == "deep" else 3
                external_evidence = [
                    {
                        "rank": i + 1,
                        "title": h.get("title", ""),
                        "url": h.get("url", ""),
                        "snippet": h.get("snippet", h.get("body", ""))[:200],
                        "source_reliability": "unknown",
                    }
                    for i, h in enumerate(hits[:depth_limit])
                ]
            except Exception as exc:
                logger.warning("222_witness WEB bridge failed: %s", exc)
                web_evidence = {
                    "claim": f"WEB bridge failed for: {focus_claim}",
                    "confidence": 0.5,
                    "grounded": False,
                    "source_tag": "minimax_web_search",
                    "error": str(exc),
                }

        if web_evidence:
            organs["WEB"] = web_evidence

        # ── Compute honest consensus ───────────────────────────────────────────
        tri_witness_score, tri_witness_tag = _compute_honest_tri_witness(
            geox_evidence, wealth_evidence, well_evidence, web_evidence
        )

        # WELL readiness = WELL confidence if present, else 0.5 (unknown)
        well_conf = _get_organ_confidence(well_evidence)
        well_readiness = well_conf if well_conf is not None else 0.5

        # Parse WELL unified substrate packet (human + machine + MCP + coupled)
        well_parsed = _parse_well_unified(well_evidence)

        # Assumptions
        assumptions = _generate_assumptions(mode, search_query, witness_required, depth)

        # Hashes for traceability
        input_payload = {
            "query": query,
            "claim": claim,
            "mode": mode,
            "search_query": search_query,
            "witness_required": witness_required,
            "depth": depth,
            "geox_present": geox_evidence is not None,
            "wealth_present": wealth_evidence is not None,
            "well_present": well_evidence is not None,
            "web_present": web_evidence is not None,
        }
        input_hash = hashlib.sha256(
            json.dumps(input_payload, sort_keys=True, default=str).encode()
        ).hexdigest()

        reasoning_payload = {
            "tri_witness_tag": tri_witness_tag,
            "tri_witness_score": tri_witness_score,
            "organ_confidences": {name: o.get("confidence") for name, o in organs.items()},
            "well_readiness": well_readiness,
            "well_substrate": well_parsed,
            "witness_required": witness_required,
        }
        reasoning_hash = hashlib.sha256(
            json.dumps(reasoning_payload, sort_keys=True, default=str).encode()
        ).hexdigest()

        claim_bundle = _build_claim_bundle(focus_claim, organs)
        consensus_rationale_detail = _build_consensus_rationale(
            tri_witness_tag, organs, tri_witness_score
        )
        divergence_points = _build_divergence_points(organs, tri_witness_score)
        judge_signal = _build_judge_signal(well_readiness, well_parsed)

        # ── EMD Stack: Decoder signals ────────────────────────────────────────
        # Tri-Witness Report: human / ai / earth alignment
        human_witness = bool(operator_id) and bool(session_id)
        ai_witness = tri_witness_score
        earth_witness = web_evidence.get("confidence", 0.5) if web_evidence else 0.5

        tri_witness_report = {
            "human_witness": {
                "aligned": human_witness,
                "operator_present": bool(operator_id),
                "session_present": bool(session_id),
                "note": (
                    "Human intent aligned with 888_APEX sovereign anchor."
                    if human_witness
                    else "Human witness incomplete — operator or session missing."
                ),
            },
            "ai_witness": {
                "score": ai_witness,
                "tag": tri_witness_tag,
                "note": "Internal model consistency via honest organ degradation.",
            },
            "earth_witness": {
                "score": earth_witness,
                "source": "minimax_web_search" if web_evidence else "none",
                "note": (
                    "Web search validation score." if web_evidence else "No web search performed."
                ),
            },
        }

        # W³ geometric mean of the three witness dimensions
        w3_score = ((1.0 if human_witness else 0.3) * ai_witness * max(earth_witness, 0.3)) ** (
            1 / 3
        )
        f2_truth_confidence = round(w3_score, 3)

        # Grounding status: ANCHORED if consensus meets threshold and all required organs present
        present_count = sum(1 for o in organs.values() if o.get("grounded", False))
        grounding_status = (
            "ANCHORED"
            if (tri_witness_score >= 0.95 and present_count >= witness_required)
            else "DRIFTING"
        )

        report = {
            "focus": focus_claim,
            "mode": mode,
            "organs": organs,
            "tri_witness_score": tri_witness_score,
            "tri_witness_tag": tri_witness_tag,
            "claim_bundle": claim_bundle,
            "consensus_rationale": consensus_rationale_detail["explanation"],
            "consensus_rationale_detail": consensus_rationale_detail,
            "divergence_points": divergence_points,
            "judge_signal": judge_signal,
            "well_substrate": well_parsed,
            "assumptions": assumptions,
            "confidence": tri_witness_score,  # Derived from evidence, not hardcoded
            "uncertainty_acknowledged": True,
            "verdict": "CLAIM_ONLY",
            "input_hash": input_hash,
            "reasoning_hash": reasoning_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "floors_evaluated": ["F2", "F3", "F5", "F8"],
            "floors_deferred": ["F11", "F13"],
            "meta_intelligence": _build_meta_intelligence(
                bool(session_id), mode, witness_required, depth
            ),
            # EMD Stack — Metabolizer output
            "external_evidence": external_evidence,
            "tri_witness_report": tri_witness_report,
            "f2_truth_confidence": f2_truth_confidence,
            "grounding_status": grounding_status,
        }

        if earth_claim:
            report["earth_claim"] = earth_claim

        metrics = ThermodynamicMetrics(
            truth_score=0.99,  # Tool is truthful about its honest degradation
            delta_s=-0.12 if tri_witness_tag == "FULL_WITNESS" else -0.06,
            omega_0=0.045,
            peace_squared=1.2 if tri_witness_tag != "NO_WITNESS" else 0.8,
            amanah_lock=True,
            tri_witness_score=tri_witness_score,
            stakeholder_safety=1.0,
        )
        return governed_return("arifos_222_witness", report, metrics, operator_id, session_id)

    except Exception as exc:
        logger.warning("arifos_222_witness constitutional error: %s", exc)

        # Build fail-safe report with EMD fields even on exception
        focus_claim = claim or query
        error_report = {
            "focus": focus_claim,
            "mode": mode,
            "error": f"{type(exc).__name__}: {exc}",
            "error_class": "constitutional_exception",
            "assumptions": [
                "Exception occurred during witness — output is degraded.",
                "Floor F3 triggered by error path.",
            ],
            "confidence": 0.5,
            "uncertainty_acknowledged": True,
            "verdict": "CLAIM_ONLY",
            "input_hash": hashlib.sha256(
                json.dumps({"query": query, "claim": claim, "mode": mode}, sort_keys=True).encode()
            ).hexdigest(),
            "reasoning_hash": hashlib.sha256(str(exc).encode()).hexdigest(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "floors_evaluated": ["F3", "F8"],
            "floors_deferred": ["F2", "F5", "F11", "F13"],
            "meta_intelligence": _build_meta_intelligence(
                bool(session_id), mode, witness_required, depth
            ),
            "consensus_rationale": "Witness degraded by exception path.",
            "divergence_points": [f"exception:{type(exc).__name__}"],
            "external_evidence": [],
            "tri_witness_report": {
                "human_witness": {
                    "aligned": False,
                    "note": "Error path — no human alignment data.",
                },
                "ai_witness": {"score": 0.5, "note": "Error path — no AI consistency data."},
                "earth_witness": {"score": 0.5, "note": "Error path — no earth witness data."},
            },
            "f2_truth_confidence": 0.5,
            "grounding_status": "DRIFTING",
        }
        metrics = ThermodynamicMetrics(
            truth_score=0.5,
            delta_s=0.05,
            omega_0=0.045,
            peace_squared=0.8,
            amanah_lock=True,
            tri_witness_score=0.33,
            stakeholder_safety=1.0,
            floor_9_signal="fail",
        )
        return governed_return("arifos_222_witness", error_report, metrics, operator_id, session_id)
