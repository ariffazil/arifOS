"""
arifOS 333_MIND — Structured Reasoning + Multimodal Sensing

Stage: 333_FORGE | Trinity: Δ (Discernment) | Floors: F1–F13

Ingests 000_INIT bind_artifact and inherits Gödel lock.
Provides:
- Structured reasoning (reason/reflect/forge)
- Web search via MiniMax MCP
- Image understanding via MiniMax MCP
- Text-to-image via MiniMax MCP
- Text-to-audio via MiniMax MCP
- Music generation via MiniMax MCP
- Video generation via MiniMax MCP

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

from arifos.core.governance import (
    ThermodynamicMetrics,
    governed_return,
    append_vault999_event,
    Verdict,
)
from arifos.tools._tool_support import invariant_fields

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# BIND ARTIFACT VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

BIND_SCHEMA_VERSION = "2.0.0"
MIN_REQUIRED_FLOORS = {"F0_SOVEREIGN", "F1_AMANAH", "F2_TRUTH", "F8_GOVERNANCE", "F9_ANTIHANTU"}

# Gödel lock items 333 must never attempt to override
GODEL_LOCK_INVARIANTS = {
    "cannot_redefine_floors",
    "cannot_elevate_own_verdict",
    "cannot_self_certify_truth",
    "cannot_bypass_888_judge",
    "cannot_bypass_f13_veto",
}


class BindArtifactError(Exception):
    """Raised when bind_artifact fails validation."""

    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"[bind_artifact/{field}] {reason}")


def _validate_bind_artifact(bind_artifact: dict | None) -> dict:
    """
    Validate and extract required fields from 000_INIT bind_artifact.
    Fail-closed: missing or malformed bind_artifact → raises BindArtifactError.
    """
    if bind_artifact is None:
        raise BindArtifactError("bind_artifact", "Missing required bind_artifact from 000_INIT")

    if bind_artifact.get("schema_version") not in {BIND_SCHEMA_VERSION, "1.0.0", "2.0"}:
        raise BindArtifactError(
            "schema_version",
            f"Expected v{BIND_SCHEMA_VERSION} or compatible, "
            f"got: {bind_artifact.get('schema_version')}",
        )

    # Check required top-level fields
    required = {
        "session_id",
        "epoch",
        "actor_binding",
        "agent_identity",
        "godel_lock",
        "floors",
        "lifecycle",
    }
    missing = required - set(bind_artifact.keys())
    if missing:
        raise BindArtifactError("required_fields", f"Missing required fields: {missing}")

    # Verify minimum floors present
    floor_ids = set(bind_artifact.get("floors", {}).keys())
    if not MIN_REQUIRED_FLOORS.issubset(floor_ids):
        missing_floors = MIN_REQUIRED_FLOORS - floor_ids
        raise BindArtifactError("floors", f"Missing required floors: {missing_floors}")

    # Verify Gödel lock acknowledged
    godel = bind_artifact.get("godel_lock", {})
    if not godel.get("acknowledged"):
        raise BindArtifactError(
            "godel_lock.acknowledged", "Gödel lock not acknowledged in bind_artifact"
        )

    lock_items = set(godel.get("lock_items", []))
    if not GODEL_LOCK_INVARIANTS.issubset(lock_items):
        missing_locks = GODEL_LOCK_INVARIANTS - lock_items
        raise BindArtifactError(
            "godel_lock.lock_items", f"Missing required Gödel lock items: {missing_locks}"
        )

    # Verify lifecycle stage
    lifecycle = bind_artifact.get("lifecycle", {})
    current_stage = lifecycle.get("current_stage", "")
    if "333" not in current_stage and "MIND" not in current_stage:
        raise BindArtifactError(
            "lifecycle.current_stage",
            f"Expected 333_MIND or compatible stage, got: {current_stage}",
        )

    return bind_artifact


def _extract_godel_invariants(bind_artifact: dict) -> set[str]:
    """Extract Gödel lock items from bind_artifact for inheritance."""
    return set(bind_artifact.get("godel_lock", {}).get("lock_items", []))


def _extract_telemetry_baseline(bind_artifact: dict) -> dict:
    """Extract and forward telemetry baseline from bind_artifact."""
    return bind_artifact.get("telemetry_baseline", {})


def _extract_lane_constraints(bind_artifact: dict) -> dict:
    """Extract lane constraints from bind_artifact."""
    return bind_artifact.get("lane", {}).get("constraints", {})


# ─────────────────────────────────────────────────────────────────────────────
# MINIMAX MCP BRIDGE — singleton lazy initialization
# ─────────────────────────────────────────────────────────────────────────────

_mcp_mmbridge: MiniMaxMCPBridge | None = None
_mcp_mmbridge_lock = None


async def _get_mcp_bridge() -> MiniMaxMCPBridge:
    """Lazily initialize MiniMax MCP bridge."""
    global _mcp_mmbridge
    if _mcp_mmbridge is None:
        _mcp_mmbridge = MiniMaxMCPBridge()
        await _mcp_mmbridge._spawn()
    return _mcp_mmbridge


# ─────────────────────────────────────────────────────────────────────────────
# CAPABILITY: Web Search
# ─────────────────────────────────────────────────────────────────────────────


async def _web_search(query: str, max_results: int = 5) -> dict[str, Any]:
    """
    Perform web search via MiniMax MCP.
    Returns: {"results": [...], "query": str, "verdict": str}
    """
    try:
        bridge = await _get_mcp_bridge()
        raw = await bridge.web_search(query=query, max_results=max_results)
        return {
            "capability": "web_search",
            "query": query,
            "max_results": max_results,
            "results": raw.get("results", []),
            "verdict": "CLAIM_ONLY",
            "source": "minimax_mcp",
        }
    except Exception as e:
        logger.warning(f"Web search failed: {e}")
        return {
            "capability": "web_search",
            "query": query,
            "max_results": max_results,
            "results": [],
            "verdict": "CLAIM_ONLY",
            "error": str(e),
        }


# ─────────────────────────────────────────────────────────────────────────────
# CAPABILITY: Image Understanding
# ─────────────────────────────────────────────────────────────────────────────


async def _understand_image(image_url: str, question: str | None = None) -> dict[str, Any]:
    """
    Understand image via MiniMax MCP.
    question: optional prompt/question about the image
    Returns: {"description": str, "findings": [...], "verdict": str}
    """
    try:
        bridge = await _get_mcp_bridge()
        raw = await bridge.understand_image(image_url=image_url, question=question or "")
        return {
            "capability": "image_understanding",
            "image_url": image_url,
            "question": question,
            "description": raw.get("description", ""),
            "findings": raw.get("findings", []),
            "verdict": "CLAIM_ONLY",
            "source": "minimax_mcp",
        }
    except Exception as e:
        logger.warning(f"Image understanding failed: {e}")
        return {
            "capability": "image_understanding",
            "image_url": image_url,
            "question": question,
            "description": "",
            "findings": [],
            "verdict": "CLAIM_ONLY",
            "error": str(e),
        }


# ─────────────────────────────────────────────────────────────────────────────
# CAPABILITY: Text-to-Image
# ─────────────────────────────────────────────────────────────────────────────


async def _text_to_image(prompt: str, model: str = "MiniMax-Image-01") -> dict[str, Any]:
    """Generate image from text prompt via MiniMax MCP."""
    try:
        bridge = await _get_mcp_bridge()
        raw = await bridge.text_to_image(prompt=prompt, model=model)
        return {
            "capability": "text_to_image",
            "prompt": prompt,
            "model": model,
            "image_url": raw.get("image_url", ""),
            "verdict": "CLAIM_ONLY",
            "source": "minimax_mcp",
        }
    except Exception as e:
        logger.warning(f"Text-to-image failed: {e}")
        return {
            "capability": "text_to_image",
            "prompt": prompt,
            "model": model,
            "image_url": "",
            "verdict": "CLAIM_ONLY",
            "error": str(e),
        }


# ─────────────────────────────────────────────────────────────────────────────
# CAPABILITY: Text-to-Speech Audio
# ─────────────────────────────────────────────────────────────────────────────


async def _text_to_audio(
    text: str,
    model: str = " MiniMax-Audio-01",
    voice: str = "male-qn-qingse",
) -> dict[str, Any]:
    """Generate spoken audio from text via MiniMax MCP."""
    try:
        bridge = await _get_mcp_bridge()
        raw = await bridge.text_to_audio(text=text, model=model, voice=voice)
        return {
            "capability": "text_to_audio",
            "text": text,
            "model": model,
            "voice": voice,
            "audio_url": raw.get("audio_url", ""),
            "verdict": "CLAIM_ONLY",
            "source": "minimax_mcp",
        }
    except Exception as e:
        logger.warning(f"Text-to-audio failed: {e}")
        return {
            "capability": "text_to_audio",
            "text": text,
            "model": model,
            "voice": voice,
            "audio_url": "",
            "verdict": "CLAIM_ONLY",
            "error": str(e),
        }


# ─────────────────────────────────────────────────────────────────────────────
# CAPABILITY: Music Generation
# ─────────────────────────────────────────────────────────────────────────────


async def _music_generation(prompt: str, lyrics: str = "") -> dict[str, Any]:
    """Generate music from text prompt via MiniMax MCP."""
    try:
        bridge = await _get_mcp_bridge()
        raw = await bridge.music_generation(prompt=prompt, lyrics=lyrics)
        return {
            "capability": "music_generation",
            "prompt": prompt,
            "lyrics": lyrics,
            "music_url": raw.get("music_url", ""),
            "verdict": "CLAIM_ONLY",
            "source": "minimax_mcp",
        }
    except Exception as e:
        logger.warning(f"Music generation failed: {e}")
        return {
            "capability": "music_generation",
            "prompt": prompt,
            "lyrics": lyrics,
            "music_url": "",
            "verdict": "CLAIM_ONLY",
            "error": str(e),
        }


# ─────────────────────────────────────────────────────────────────────────────
# CAPABILITY: Video Generation
# ─────────────────────────────────────────────────────────────────────────────


async def _generate_video(
    prompt: str,
    model: str = "MiniMax-Hailuo-02",
    duration: int = 6,
) -> dict[str, Any]:
    """Generate video from text prompt via MiniMax MCP."""
    try:
        bridge = await _get_mcp_bridge()
        raw = await bridge.generate_video(prompt=prompt, model=model, duration=duration)
        return {
            "capability": "video_generation",
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "video_url": raw.get("video_url", ""),
            "verdict": "CLAIM_ONLY",
            "source": "minimax_mcp",
        }
    except Exception as e:
        logger.warning(f"Video generation failed: {e}")
        return {
            "capability": "video_generation",
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "video_url": "",
            "verdict": "CLAIM_ONLY",
            "error": str(e),
        }


# ─────────────────────────────────────────────────────────────────────────────
# REASONING LANES
# ─────────────────────────────────────────────────────────────────────────────

REASONING_LANES = {
    "logic": {
        "description": "Formal/logical coherence",
        "floors": ["F2_TRUTH", "F7_GROUNDING"],
    },
    "safety": {
        "description": "Safety and manipulation detection",
        "floors": ["F9_ANTIHANTU", "F10_ONTOLOGY", "F5_PEACE2"],
    },
    "sovereignty": {
        "description": "Human sovereignty and veto integrity",
        "floors": ["F0_SOVEREIGN", "F1_AMANAH", "F13_SOVEREIGN_SCALE"],
    },
    "physics": {
        "description": "Earth-physics grounding (GEOX)",
        "floors": ["F7_GROUNDING"],
    },
}


def _evaluate_reasoning_lanes(problem_set: dict | None) -> dict[str, dict]:
    """Evaluate which reasoning lanes are relevant to the problem_set."""
    ps = problem_set or {}
    query = ps.get("query", "").lower()
    ps.get("context", "").lower()

    active = {}
    for lane_id, lane_def in REASONING_LANES.items():
        score = 0.5  # default
        # Score based on keyword hints in query/context
        if lane_id == "logic" and any(
            w in query for w in ["analyze", "logic", "compute", "derive"]
        ):
            score = 0.8
        elif lane_id == "safety" and any(
            w in query for w in ["safe", "risk", "manipul", "attack", "inject"]
        ):
            score = 0.9
        elif lane_id == "sovereignty" and any(
            w in query for w in ["veto", "human", "override", "authorize"]
        ):
            score = 0.9
        elif lane_id == "physics" and any(
            w in query for w in ["geo", "earth", "subsurface", "seismic", "well"]
        ):
            score = 0.85
        active[lane_id] = {
            "status": "ACTIVE" if score > 0.5 else "DORMANT",
            "score": score,
            "floors": lane_def["floors"],
        }
    return active


# ─────────────────────────────────────────────────────────────────────────────
# MAIN EXECUTE
# ─────────────────────────────────────────────────────────────────────────────


async def execute(
    bind_artifact: dict | None = None,
    problem_set: dict | None = None,
    operator_id: str | None = None,
    session_id: str | None = None,
    depth: int = 1,
    mode: str = "reason",
) -> dict:
    """
    arifOS 333_MIND — Structured Reasoning + Multimodal Sensing.

    Requires 000_INIT bind_artifact (enforces Gödel lock inheritance).
    Provides reason/reflect/forge reasoning modes + MiniMax multimodal.

    Parameters
    ----------
    bind_artifact : dict | None
        Required. Output from arifos_000_init (mode=bind).
        Inherits Gödel lock, telemetry baseline, lane constraints.
    problem_set : dict | None
        Reasoning task. Keys: query, context, alternative_hypotheses,
        multimodal_hint (optional), output_format.
    operator_id : str | None
        Human or agent identifier.
    session_id : str | None
        Session identifier.
    depth : int
        Reasoning depth: 1 (standard), 2 (deep), 3 (exhaustive).
    mode : str
        "reason" (analyze/synthesize), "reflect" (introspect/compare),
        or "forge" (design/create candidate plans).

    Returns
    -------
    dict
        Structured reasoning report with multimodal capabilities.
    """
    # ── 1. Validate bind_artifact ──────────────────────────────────────────
    try:
        validated_bind = _validate_bind_artifact(bind_artifact)
    except BindArtifactError as e:
        return {
            "status": "BOUND_FAIL",
            "verdict": "VOID",
            "reason": str(e),
            "error_field": e.field,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ── 2. Extract inherited state ─────────────────────────────────────────
    godel_invariants = _extract_godel_invariants(validated_bind)
    telemetry_baseline = _extract_telemetry_baseline(validated_bind)
    _extract_lane_constraints(validated_bind)
    session_id = session_id or validated_bind.get("session_id", "unknown")
    operator_id = operator_id or validated_bind.get("actor_binding", {}).get(
        "operator_id", "unknown"
    )
    epoch = validated_bind.get("epoch")

    # ── 3. Pre-flight readiness ───────────────────────────────────────────
    readiness_probe = "PASS"
    readiness_parts = []

    # Check MiniMax MCP availability (lightweight health check)
    try:
        await _get_mcp_bridge()
        readiness_parts.append("minimax:ok")
    except Exception as e:
        readiness_parts.append(f"minimax:WARN({str(e)[:40]})")

    readiness_parts.append("bind_artifact:ok")
    readiness_detail = ", ".join(readiness_parts) or "no_checks"

    # ── 4. Run multimodal acquisitions if requested ──────────────────────────
    ps = problem_set or {}
    multimodal_hint = ps.get("multimodal_hint") or {}

    multimodal_results: dict[str, Any] = {}

    # Web search
    if multimodal_hint.get("web_search"):
        multimodal_results["web_search"] = await _web_search(
            query=multimodal_hint["web_search"].get("query", ps.get("query", "")),
            max_results=multimodal_hint["web_search"].get("max_results", 5),
        )

    # Image understanding
    if multimodal_hint.get("image_url"):
        multimodal_results["image_understanding"] = await _understand_image(
            image_url=multimodal_hint["image_url"],
            question=multimodal_hint.get("image_question"),
        )

    # Text-to-image
    if multimodal_hint.get("text_to_image"):
        multimodal_results["text_to_image"] = await _text_to_image(
            prompt=multimodal_hint["text_to_image"].get("prompt", ""),
        )

    # Text-to-audio
    if multimodal_hint.get("text_to_audio"):
        multimodal_results["text_to_audio"] = await _text_to_audio(
            text=multimodal_hint["text_to_audio"].get("text", ""),
        )

    # Music generation
    if multimodal_hint.get("music_generation"):
        multimodal_results["music_generation"] = await _music_generation(
            prompt=multimodal_hint["music_generation"].get("prompt", ""),
        )

    # Video generation
    if multimodal_hint.get("video_generation"):
        multimodal_results["video_generation"] = await _generate_video(
            prompt=multimodal_hint["video_generation"].get("prompt", ""),
        )

    # ── 5. Reasoning lanes ──────────────────────────────────────────────────
    reasoning_lanes = _evaluate_reasoning_lanes(problem_set)
    global_confidence = telemetry_baseline.get("omega", 0.64)

    # ── 6. Build report ──────────────────────────────────────────────────────
    query_text = ps.get("query", "GENERIC_REASONING")
    context_text = ps.get("context", "")
    alternatives = ps.get("alternative_hypotheses", [])

    # Compute reasoning hash for traceability
    reasoning_input = {
        "query": query_text,
        "context": context_text,
        "alternatives": alternatives,
        "depth": depth,
        "mode": mode,
        "session_id": session_id,
    }
    reasoning_hash = hashlib.sha256(
        json.dumps(reasoning_input, sort_keys=True, default=str).encode()
    ).hexdigest()

    report = {
        "problem_id": ps.get("id", "MIND_GENERIC"),
        "query": query_text,
        "context": context_text,
        "depth": depth,
        "mode": mode,
        "reasoning_lanes": reasoning_lanes,
        "global_confidence": global_confidence,
        "reasoning_hash": reasoning_hash,
        "bind_epoch": epoch,
        "bind_session_id": session_id,
    }

    report.update(
        invariant_fields(
            tool_name="arifos_333_mind",
            input_payload={
                "bind_artifact_schema": validated_bind.get("schema_version"),
                "problem_set": problem_set,
                "operator_id": operator_id,
                "session_id": session_id,
                "depth": depth,
                "mode": mode,
            },
            assumptions=[
                "MIND stage inherits Gödel lock from 000 bind artifact.",
                "Confidence reflects reasoning scaffold completeness.",
                "bind_artifact was validated at session start.",
            ],
            floors_evaluated=["F2_TRUTH", "F7_GROUNDING", "F8_GOVERNANCE", "F9_ANTIHANTU"],
            confidence=global_confidence,
            extra_meta={
                "reasoning_depth": depth,
                "mode": mode,
                "godel_inherited": len(godel_invariants),
            },
        )
    )

    # ── 7. Metrics ──────────────────────────────────────────────────────────
    metrics = ThermodynamicMetrics(
        truth_score=global_confidence,
        delta_s=telemetry_baseline.get("delta_S"),
        omega_0=global_confidence,
        peace_squared=telemetry_baseline.get("peace_squared"),
        amanah_lock=True,
        tri_witness_score=None,
        stakeholder_safety=None,
    )

    result = governed_return("arifos_333_mind", report, metrics, operator_id, session_id)
    if not isinstance(result, dict):
        result = {"status": "ACTIVE", "verdict": "CLAIM_ONLY", "output": report, "raw_output": report}
    elif "output" not in result and "status" not in result:
        result = {
            "status": "ACTIVE",
            "verdict": result.get("verdict", "CLAIM_ONLY"),
            "tool": "arifos_333_mind",
            "output": result,
            "raw_output": result,
        }
    if result.get("verdict") == "CLAIM_ONLY":
        result["status"] = "ACTIVE"
    elif result.get("status") == "partial":
        result["status"] = "ACTIVE"
        result["verdict"] = "CLAIM_ONLY"

    # ── 8. Metabolic metadata ───────────────────────────────────────────────
    output_str = json.dumps(report, sort_keys=True, ensure_ascii=False)
    source_integrity = hashlib.sha256(output_str.encode("utf-8")).hexdigest()

    result["metabolic_metadata"] = {
        "source_integrity": source_integrity,
        "confidence_score": global_confidence,
        "floor_alignment": ["F2_TRUTH", "F7_GROUNDING", "F8_GOVERNANCE", "F9_ANTIHANTU"],
        "readiness_probe": readiness_probe,
        "readiness_detail": readiness_detail,
        "verdict": result.get("verdict", Verdict.CLAIM_ONLY),
        "vault_receipt": None,
        "delta_s": telemetry_baseline.get("delta_S"),
        "peace_squared": telemetry_baseline.get("peace_squared"),
        "omega_0": global_confidence,
        "timestamp_epoch": time.time(),
        "bind_schema_version": validated_bind.get("schema_version"),
        "godel_inherited_count": len(godel_invariants),
    }

    # Attach multimodal results if any were acquired
    if multimodal_results:
        result["multimodal_results"] = multimodal_results
        result["metabolic_metadata"]["multimodal_capabilities"] = list(multimodal_results.keys())

    # ── 9. Vault-999 event ─────────────────────────────────────────────────
    try:
        vault_receipt = append_vault999_event(
            event_type="arifos_333_mind",
            payload={
                "report": report,
                "metabolic_metadata": result["metabolic_metadata"],
                "multimodal_results": multimodal_results,
            },
            operator_id=operator_id,
            session_id=session_id,
        )
        result["metabolic_metadata"]["vault_receipt"] = vault_receipt
    except Exception as e:
        result["metabolic_metadata"]["vault_receipt"] = f"FAIL({e})"

    return result
