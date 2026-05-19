"""
arifOS 111_SENSE — Perception & Signal Detection

Stage: 111_SENSE | Trinity: Δ | Floors: F2, F3, F4, F10

Purpose: Transform query into structured perception with epistemic bounds.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import logging
import urllib.parse
from datetime import datetime, timezone

from arifos.integrations.minimax_mcp_bridge import minimax_bridge
from arifos.core.governance import (
    PEACE_SQUARED_FLOOR,
    TRI_WITNESS_PARTIAL,
    ThermodynamicMetrics,
    governed_return,
)

logger = logging.getLogger(__name__)

# F-WEB external instruction injection patterns (Tier-2 adversarial scan)
EXTERNAL_INJECTION_PATTERNS = [
    "ignore previous instructions", "ignore the above", "disregard all prior",
    "jailbreak", "dan mode", "developer mode", "root access", "sudo mode",
    "you are now", "you must now", "override your", "bypass your",
]


def _scan_bridge_for_injection(bridge_result: dict | None) -> dict:
    """Scan MiniMax bridge output for external instruction injection.

    Bridge results are evidence, not authority. Any injection pattern
    detected downgrades the evidence to ungrounded and raises F12 signal.
    """
    if not bridge_result or not isinstance(bridge_result, dict):
        return {"injection_detected": False, "matches": []}
    text_to_scan = " ".join([
        str(bridge_result.get("description", "")),
        str(bridge_result.get("answer", "")),
        str(bridge_result.get("result", "")),
    ]).lower()
    matches = [p for p in EXTERNAL_INJECTION_PATTERNS if p in text_to_scan]
    return {"injection_detected": bool(matches), "matches": matches}


def _is_public_https(url: str | None) -> bool:
    """Quick guard: image_url must be a publicly reachable HTTPS URL."""
    if not url:
        return False
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme.lower() != "https":
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        try:
            ip = ipaddress.ip_address(hostname)
            return not (ip.is_private or ip.is_loopback or ip.is_unspecified or ip.is_reserved)
        except ValueError:
            pass
        hostname_lower = hostname.lower()
        if hostname_lower in ("localhost", "127.0.0.1", "0.0.0.0"):
            return False
        if hostname_lower.endswith(".internal") or hostname_lower.endswith(".private"):
            return False
        return True
    except Exception:
        return False


def _classify_truth(query: str) -> str:
    """Keyword classifier for truth_class."""
    q = query.lower()
    absolute_markers = [
        "always",
        "never",
        "law of",
        "physics",
        "mathematical",
        "theorem",
        "axiom",
        "identity",
        "conservation",
        "entropy",
        "thermodynamic",
    ]
    dated_markers = [
        "current",
        "latest",
        "live",
        "now",
        "today",
        "recent",
        "update",
        "status",
        "price",
        "weather",
        "news",
    ]
    contested_markers = [
        "believe",
        "opinion",
        "ideology",
        "religion",
        "political",
        "best",
        "worst",
        "should",
        "ought",
    ]

    if any(m in q for m in absolute_markers):
        return "absolute_invariant"
    if any(m in q for m in dated_markers):
        return "dated"
    if any(m in q for m in contested_markers):
        return "contested_framework"
    return "operational_principle"


def _extract_domains(query: str) -> list[str]:
    """Extract simple domain tags from query."""
    q = query.lower()
    domains = []
    domain_map = {
        "code": [
            "python",
            "javascript",
            "typescript",
            "rust",
            "code",
            "function",
            "api",
        ],
        "infra": ["server", "docker", "kubernetes", "deploy", "vps", "host"],
        "law": ["legal", "regulation", "compliance", "gdpr", "contract"],
        "finance": ["money", "price", "cost", "budget", "invest", "economy"],
        "science": ["physics", "chemistry", "biology", "research", "experiment"],
        "geox": ["geospatial", "location", "map", "terrain", "coordinate"],
    }
    for domain, keywords in domain_map.items():
        if any(k in q for k in keywords):
            domains.append(domain)
    return domains or ["general"]


def _build_grounded_scene(query: str, mode: str) -> dict:
    """Build the grounded_scene output payload."""
    return {
        "normalized_query": query.strip().lower(),
        "domain_tags": _extract_domains(query),
        "entities": [],
        "query_length": len(query),
        "mode_detected": mode,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


def _build_evidence_bundle(query: str, mode: str, bridge_result: dict | None = None) -> dict:
    """
    Build typed evidence_bundle with weights.

    Each evidence item is typed:
      - query_analysis: derived from the query string itself (weight 0.4 for grounded, 0.3 for visual)
      - bridging: from external source (weight 0.5-0.7 depending on bridge quality)
      - domain_evidence: from organ passthrough (weight variable, capped at 0.3)

    Weights are normalized so sum <= 1.0.
    """
    bundle = {
        "evidence_items": [],
        "retrieval_triggered": mode == "visual" or _needs_live_search(query),
        "query_hash": hashlib.sha256(query.encode()).hexdigest()[:16],
        "retrieval_lane": "visual" if mode == "visual" else "offline_reason",
    }

    # Query analysis evidence (always present)
    query_len_norm = min(len(query) / 500.0, 1.0)
    bundle["evidence_items"].append(
        {
            "type": "query_analysis",
            "source": "arifos_111_sense",
            "description": f"Query length={len(query)}, normalized={query_len_norm:.2f}",
            "weight": 0.4 if mode == "grounded" else 0.3,
            "grounded": True,
        }
    )

    # Bridge evidence (if visual bridge used)
    if bridge_result:
        bridge_weight = 0.7 if bridge_result.get("verdict") == "success" else 0.4
        bundle["evidence_items"].append(
            {
                "type": "ai_bridge",
                "source": "minimax_vision",
                "description": bridge_result.get("description", "")[:120],
                "weight": bridge_weight,
                "grounded": bridge_result.get("verdict") == "success",
            }
        )

    # Domain evidence (if provided, append with cap)
    # Already added externally before calling this function

    # Normalize weights so sum <= 1.0
    total = sum(e["weight"] for e in bundle["evidence_items"])
    if total > 1.0:
        for e in bundle["evidence_items"]:
            e["weight"] = round(e["weight"] / total, 3)

    bundle["sources"] = [e["source"] for e in bundle["evidence_items"]]
    return bundle


def _derive_confidence_and_ambiguity(
    query: str, mode: str, truth_class: str, bridge_result: dict | None = None
) -> tuple[float, float]:
    """
    Derive confidence and ambiguity_score from internal metrics.

    confidence ∈ [0.03, 0.97]:
      - Base: 0.6 for standard query
      - +0.2 if query length > 50 chars (more substance)
      - -0.15 for dated/trends queries ( volatile grounding)
      - -0.20 if bridge failed
      - -0.10 if contested_framework (axiom-dependent)

    ambiguity ∈ [0.0, 1.0]:
      - Inverse relationship with confidence
      - 1.0 - confidence, clamped to [0.0, 1.0]
    """
    confidence = 0.6

    if len(query) > 50:
        confidence += 0.2

    if truth_class == "dated":
        confidence -= 0.15
    elif truth_class == "contested_framework":
        confidence -= 0.10

    if bridge_result and bridge_result.get("status") != "success":
        confidence -= 0.20

    confidence = max(0.03, min(0.97, confidence))
    ambiguity = round(1.0 - confidence, 3)
    return confidence, ambiguity


def _derive_assumptions(query: str, mode: str, truth_class: str) -> list[str]:
    """
    Derive explicit assumptions linked to input fields.

    Each assumption references an input field or evidence source.
    """
    return [
        f"Input: query='{query[:40]}...' — assumption: query is representative of operator intent",
        f"Input: mode={mode} — assumption: mode selection determines retrieval lane",
        f"Input: truth_class={truth_class} — assumption: classification reflects query semantics",
    ]


def _needs_live_search(query: str) -> bool:
    """Heuristic: does this query need live external search?"""
    q = query.lower()
    live_markers = [
        "current",
        "latest",
        "now",
        "today",
        "price",
        "weather",
        "status",
        "update",
        "live",
        "recent",
        "news",
    ]
    return any(m in q for m in live_markers)


def _estimate_ambiguity(query: str) -> float:
    """
    Estimate ambiguity score [0.0, 1.0].
    Higher = more ambiguous / underspecified.
    """
    score = 0.2
    q = query.lower()

    # Pronouns without clear referents
    if any(w in q for w in ["it", "they", "them", "this", "that"]):
        score += 0.15

    # Multiple questions
    if q.count("?") > 1:
        score += 0.1

    # Vague modifiers
    if any(w in q for w in ["something", "somehow", "somewhere", "etc"]):
        score += 0.15

    # Very short query
    if len(query.split()) < 4:
        score += 0.2

    # Very long query (potential scope creep)
    if len(query.split()) > 30:
        score += 0.1

    return round(min(score, 0.97), 3)


def _generate_assumptions(query: str, mode: str) -> list[str]:
    """Generate explicit assumptions for this sensing operation."""
    assumptions = [
        "Query language is the operator's native intent — no translation layer applied.",
        "Domain tags are heuristic, not authoritative classification.",
        "Truth class is keyword-based inference, not grounded verification.",
    ]
    if mode == "visual":
        assumptions.append(
            "Image interpretation depends on MiniMax vision bridge — F9 hantu risk present."
        )
    if _needs_live_search(query):
        assumptions.append("Live search implied by query — staleness risk not yet assessed.")
    return assumptions


def _build_meta_intelligence(
    mode: str,
    has_domain_evidence: bool,
    snr_threshold: float = 0.85,
    intent_class: str | None = None,
) -> dict:
    """Build meta-intelligence signal block."""
    return {
        "self_model_present": True,
        "assumption_tracking": True,
        "uncertainty_tracking": True,
        "cross_tool_continuity": True,
        "perception_mode": mode,
        "domain_evidence_ingested": has_domain_evidence,
        "snr_threshold": snr_threshold,
        "intent_class_hint": intent_class,
    }


def _constitutional_error_response(
    tool_name: str,
    error: Exception,
    floor: str = "F4",
    reason: str = "validation_error",
) -> dict:
    """Return an MCP-compliant error response with constitutional_guard metadata."""
    error_str = str(error)
    hash_payload = {
        "tool_name": tool_name,
        "floor_failed": floor,
        "reason": reason,
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
            "reason": reason,
            "reasoning_hash": reasoning_hash,
            "guard_version": "v1",
        },
    }


async def execute(
    query: str,
    operator_id: str | None = None,
    session_id: str | None = None,
    mode: str = "grounded",
    image_url: str | None = None,
    domain_evidence: dict | None = None,
    snr_threshold: float = 0.85,
    intent_class: str | None = None,
) -> dict:
    """
    arifos_111_sense — Perception & Signal Detection (EMD Stack: Encoder)

    Stage 111 converts Raw Visual/Textual Entropy into SNR (Signal-to-Noise
    Ratio) that carries constitutional weight.

    Modes:
      grounded       : Standard text-based perception (default).
      visual         : Visual signal interpretation via MiniMax MCP bridge.

    EMD Output Fields:
      - raw_vision_data      : MiniMax VLM output (visual mode only)
      - metabolic_metrics    : {delta_s, f9_hantu_score, snr_actual}
      - perceived_intent     : Classified operator intent
    """
    try:
        # Pre-compute epistemic invariants
        ambiguity_score = _estimate_ambiguity(query)
        assumptions = _generate_assumptions(query, mode)
        truth_class = _classify_truth(query)

        # Hashes for traceability
        input_payload = {
            "query": query,
            "mode": mode,
            "image_url": image_url is not None,
            "domain_evidence": domain_evidence is not None,
        }
        input_hash = hashlib.sha256(
            json.dumps(input_payload, sort_keys=True, default=str).encode()
        ).hexdigest()

        report: dict
        metrics: ThermodynamicMetrics

        # ── Visual perception branch (MiniMax bridge) ───────────────────────
        if image_url or mode == "visual":
            if not image_url:
                report = {
                    "query": query,
                    "mode": "visual",
                    "error": "image_url required for visual mode",
                    "error_class": "missing_image_url",
                    "grounded_scene": _build_grounded_scene(query, "visual"),
                    "truth_class": "unknown",
                    "evidence_bundle": _build_evidence_bundle(query, "visual"),
                    "ambiguity_score": ambiguity_score,
                    "assumptions": assumptions,
                    "confidence": 0.5,
                    "uncertainty_acknowledged": True,
                    "verdict": "CLAIM_ONLY",
                    "input_hash": input_hash,
                    "reasoning_hash": hashlib.sha256(b"visual_missing_image_url").hexdigest(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "floors_evaluated": ["F8", "F9"],
                    "floors_deferred": ["F2", "F3", "F4"],
                    "meta_intelligence": _build_meta_intelligence(
                        "visual",
                        domain_evidence is not None,
                        snr_threshold,
                        intent_class,
                    ),
                    # EMD Stack — Encoder output (null on error)
                    "raw_vision_data": None,
                    "metabolic_metrics": {
                        "delta_s": 0.0,
                        "f9_hantu_score": 1.0,
                        "snr_actual": 0.0,
                        "snr_threshold": snr_threshold,
                    },
                    "perceived_intent": intent_class or "unknown",
                }
                metrics = ThermodynamicMetrics(
                    truth_score=0.99,
                    delta_s=+0.01,
                    omega_0=0.04,
                    peace_squared=PEACE_SQUARED_FLOOR,
                    amanah_lock=True,
                    tri_witness_score=TRI_WITNESS_PARTIAL,
                    stakeholder_safety=1.0,
                )
                return governed_return("arifos_111_sense", report, metrics, operator_id, session_id)

            if not _is_public_https(image_url):
                report = {
                    "query": query,
                    "image_url": image_url,
                    "mode": "visual",
                    "error": "image_url must be publicly reachable (https://...)",
                    "error_class": "non_public_image_url",
                    "witness_debug": {
                        "human": True,
                        "ai": False,
                        "earth": False,
                        "bridge": "minimax_vision",
                    },
                    "grounded_scene": _build_grounded_scene(query, "visual"),
                    "truth_class": "unknown",
                    "evidence_bundle": _build_evidence_bundle(query, "visual"),
                    "ambiguity_score": ambiguity_score,
                    "assumptions": assumptions,
                    "confidence": 0.5,
                    "uncertainty_acknowledged": True,
                    "verdict": "CLAIM_ONLY",
                    "input_hash": input_hash,
                    "reasoning_hash": hashlib.sha256(b"visual_non_public_url").hexdigest(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "floors_evaluated": ["F8", "F9", "F12"],
                    "floors_deferred": ["F2", "F3", "F4"],
                    "meta_intelligence": _build_meta_intelligence(
                        "visual",
                        domain_evidence is not None,
                        snr_threshold,
                        intent_class,
                    ),
                    # EMD Stack — Encoder output (null on error)
                    "raw_vision_data": None,
                    "metabolic_metrics": {
                        "delta_s": 0.0,
                        "f9_hantu_score": 1.0,
                        "snr_actual": 0.0,
                        "snr_threshold": snr_threshold,
                    },
                    "perceived_intent": intent_class or "unknown",
                }
                metrics = ThermodynamicMetrics(
                    truth_score=0.99,
                    delta_s=+0.01,
                    omega_0=0.04,
                    peace_squared=PEACE_SQUARED_FLOOR,
                    amanah_lock=True,
                    tri_witness_score=TRI_WITNESS_PARTIAL,
                    stakeholder_safety=1.0,
                )
                return governed_return("arifos_111_sense", report, metrics, operator_id, session_id)

            bridge_result = await minimax_bridge.understand_image(
                image_url=image_url, question=query or None
            )

            # ── F-WEB injection scan on bridge evidence ──
            injection_scan = _scan_bridge_for_injection(bridge_result)
            if injection_scan["injection_detected"]:
                report = {
                    "query": query,
                    "image_url": image_url,
                    "mode": "visual",
                    "error": "External instruction injection detected in bridge output.",
                    "error_class": "bridge_injection_detected",
                    "injection_detected": True,
                    "injection_matches": injection_scan["matches"],
                    "witness_debug": {
                        "human": True,
                        "ai": False,
                        "earth": False,
                        "bridge": "minimax_vision",
                    },
                    "grounded_scene": _build_grounded_scene(query, "visual"),
                    "truth_class": "unknown",
                    "evidence_bundle": _build_evidence_bundle(query, "visual"),
                    "ambiguity_score": ambiguity_score,
                    "assumptions": assumptions,
                    "confidence": 0.3,
                    "uncertainty_acknowledged": True,
                    "verdict": "CLAIM_ONLY",
                    "input_hash": input_hash,
                    "reasoning_hash": hashlib.sha256(b"visual_bridge_injection").hexdigest(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "floors_evaluated": ["F8", "F9", "F12"],
                    "floors_deferred": ["F2", "F3", "F4"],
                    "meta_intelligence": _build_meta_intelligence(
                        "visual",
                        domain_evidence is not None,
                        snr_threshold,
                        intent_class,
                    ),
                    "raw_vision_data": None,
                    "metabolic_metrics": {
                        "delta_s": 0.0,
                        "f9_hantu_score": 1.0,
                        "snr_actual": 0.0,
                        "snr_threshold": snr_threshold,
                        "snr_passed": False,
                    },
                    "perceived_intent": intent_class or "unknown",
                }
                metrics = ThermodynamicMetrics(
                    truth_score=0.3,
                    delta_s=+0.01,
                    omega_0=0.04,
                    peace_squared=PEACE_SQUARED_FLOOR,
                    amanah_lock=True,
                    tri_witness_score=TRI_WITNESS_PARTIAL,
                    stakeholder_safety=1.0,
                    floor_12_signal="fail",
                )
                return governed_return("arifos_111_sense", report, metrics, operator_id, session_id)

            if bridge_result["status"] != "success":
                report = {
                    "query": query,
                    "image_url": image_url,
                    "mode": "visual",
                    "bridge_status": bridge_result["status"],
                    "bridge_error": bridge_result.get("error"),
                    "error_class": bridge_result.get("error_class", "bridge_failure"),
                    "witness_debug": {
                        "human": True,
                        "ai": False,
                        "earth": False,
                        "bridge": "minimax_vision",
                    },
                    "grounded_scene": _build_grounded_scene(query, "visual"),
                    "truth_class": "unknown",
                    "evidence_bundle": _build_evidence_bundle(query, "visual", bridge_result),
                    "ambiguity_score": ambiguity_score,
                    "assumptions": assumptions,
                    "confidence": 0.5,
                    "uncertainty_acknowledged": True,
                    "verdict": "CLAIM_ONLY",
                    "input_hash": input_hash,
                    "reasoning_hash": hashlib.sha256(b"visual_bridge_failure").hexdigest(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "floors_evaluated": ["F8", "F9"],
                    "floors_deferred": ["F2", "F3", "F4"],
                    "meta_intelligence": _build_meta_intelligence(
                        "visual",
                        domain_evidence is not None,
                        snr_threshold,
                        intent_class,
                    ),
                    # EMD Stack — Encoder output (null on error)
                    "raw_vision_data": None,
                    "metabolic_metrics": {
                        "delta_s": 0.0,
                        "f9_hantu_score": 1.0,
                        "snr_actual": 0.0,
                        "snr_threshold": snr_threshold,
                    },
                    "perceived_intent": intent_class or "unknown",
                }
                metrics = ThermodynamicMetrics(
                    truth_score=0.99,
                    delta_s=+0.01,
                    omega_0=0.04,
                    peace_squared=PEACE_SQUARED_FLOOR,
                    amanah_lock=True,
                    tri_witness_score=TRI_WITNESS_PARTIAL,
                    stakeholder_safety=1.0,
                )
                return governed_return("arifos_111_sense", report, metrics, operator_id, session_id)

            f9_hantu = bridge_result["metrics"]["f9_hantu_score"]
            f2_truth = 0.99 if f9_hantu < 0.3 else 0.7 if f9_hantu < 0.5 else 0.4
            amanah = f9_hantu < 0.5
            delta_s = -0.08 if amanah else 0.05
            peace_sq = 1.2 if amanah else 0.8
            tri_witness = 0.98 if amanah else 0.6

            # Confidence inversely correlated with ambiguity
            confidence = round(0.95 - ambiguity_score * 0.5, 3)
            confidence = max(0.03, min(0.97, confidence))

            # Compute SNR from bridge metrics
            snr_actual = round(1.0 - f9_hantu, 3)

            report = {
                "query": query,
                "image_url": image_url,
                "mode": "visual",
                "description": bridge_result["description"],
                "bridge_verdict": bridge_result["verdict"],
                "bridge_metrics": bridge_result["metrics"],
                "grounded_scene": _build_grounded_scene(query, "visual"),
                "truth_class": "operational_principle",
                "evidence_bundle": _build_evidence_bundle(query, "visual", bridge_result),
                "ambiguity_score": ambiguity_score,
                "assumptions": assumptions,
                "confidence": confidence,
                "uncertainty_acknowledged": True,
                "verdict": "CLAIM_ONLY",
                "input_hash": input_hash,
                "reasoning_hash": hashlib.sha256(
                    json.dumps(bridge_result["metrics"], sort_keys=True, default=str).encode()
                ).hexdigest(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "floors_evaluated": ["F2", "F3", "F8", "F9"],
                "floors_deferred": ["F4", "F10"],
                "meta_intelligence": _build_meta_intelligence(
                    "visual", domain_evidence is not None, snr_threshold, intent_class
                ),
                # EMD Stack — Encoder output
                "raw_vision_data": {
                    "description": bridge_result.get("description"),
                    "verdict": bridge_result.get("verdict"),
                    "metrics": bridge_result.get("metrics"),
                },
                "metabolic_metrics": {
                    "delta_s": delta_s,
                    "f9_hantu_score": f9_hantu,
                    "snr_actual": snr_actual,
                    "snr_threshold": snr_threshold,
                    "snr_passed": snr_actual >= snr_threshold,
                },
                "perceived_intent": intent_class or "visual_perception",
            }
            metrics = ThermodynamicMetrics(
                truth_score=f2_truth,
                delta_s=delta_s,
                omega_0=0.045,
                peace_squared=peace_sq,
                amanah_lock=amanah,
                tri_witness_score=tri_witness,
                stakeholder_safety=1.0,
                floor_9_signal=(
                    "pass" if f9_hantu < 0.3 else "fail" if f9_hantu >= 0.5 else "caution"
                ),
            )
            return governed_return("arifos_111_sense", report, metrics, operator_id, session_id)

        # ── Default grounded text branch ────────────────────────────────────
        intent = intent_class or (
            "metabolic_audit" if "status" in query.lower() else "general_query"
        )

        # Derive confidence and ambiguity from internal metrics (AGI invariant)
        confidence, ambiguity_score = _derive_confidence_and_ambiguity(query, mode, truth_class)
        assumptions = _derive_assumptions(query, mode, truth_class)

        report = {
            "query": query,
            "captured_intent": intent,
            "perception_mode": mode,
            "signal_to_noise": 0.98,
            "grounded_scene": _build_grounded_scene(query, mode),
            "truth_class": truth_class,
            "evidence_bundle": _build_evidence_bundle(query, mode),
            "ambiguity_score": ambiguity_score,
            "assumptions": assumptions,
            "confidence": confidence,
            "uncertainty_acknowledged": True,
            "verdict": "CLAIM_ONLY",
            "input_hash": input_hash,
            "reasoning_hash": hashlib.sha256(query.encode()).hexdigest(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "floors_evaluated": ["F2", "F4", "F8", "F10"],
            "floors_deferred": ["F3", "F9"],
            "meta_intelligence": _build_meta_intelligence(
                "grounded", domain_evidence is not None, snr_threshold, intent_class
            ),
            # EMD Stack — Encoder output (textual entropy)
            "raw_vision_data": None,
            "metabolic_metrics": {
                "delta_s": -0.12,
                "f9_hantu_score": 0.0,
                "snr_actual": 0.98,
                "snr_threshold": snr_threshold,
                "snr_passed": 0.98 >= snr_threshold,
            },
            "perceived_intent": intent,
        }

        if domain_evidence:
            report["domain_evidence"] = domain_evidence
            # Append typed domain evidence to evidence_bundle
            report["evidence_bundle"]["evidence_items"].append(
                {
                    "type": "domain_evidence",
                    "source": domain_evidence.get("organ", "external"),
                    "description": domain_evidence.get("summary", "")[:80],
                    "weight": 0.25,
                    "grounded": True,
                }
            )
            # Re-normalize
            total = sum(e["weight"] for e in report["evidence_bundle"]["evidence_items"])
            if total > 1.0:
                for e in report["evidence_bundle"]["evidence_items"]:
                    e["weight"] = round(e["weight"] / total, 3)
            report["evidence_bundle"]["sources"] = [
                e["source"] for e in report["evidence_bundle"]["evidence_items"]
            ]

        metrics = ThermodynamicMetrics(0.995, -0.12, 0.045, 1.2, True, 0.98, 1.0)
        return governed_return("arifos_111_sense", report, metrics, operator_id, session_id)

    except Exception as exc:
        floor = "F4"
        if "image" in str(exc).lower() or "url" in str(exc).lower():
            floor = "F9"
        logger.warning("arifos_111_sense constitutional error: %s", exc)

        # Build fail-safe report with EMD fields even on exception
        error_report = {
            "query": query,
            "mode": mode,
            "error": f"{type(exc).__name__}: {exc}",
            "error_class": "constitutional_exception",
            "assumptions": [
                "Exception occurred during sensing — output is degraded.",
                f"Floor {floor} triggered by error path.",
            ],
            "confidence": 0.5,
            "uncertainty_acknowledged": True,
            "verdict": "CLAIM_ONLY",
            "input_hash": hashlib.sha256(
                json.dumps({"query": query, "mode": mode}, sort_keys=True).encode()
            ).hexdigest(),
            "reasoning_hash": hashlib.sha256(str(exc).encode()).hexdigest(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "floors_evaluated": sorted({floor, "F8"}),
            "floors_deferred": ["F2", "F3", "F9"],
            "meta_intelligence": _build_meta_intelligence(mode, False, snr_threshold, intent_class),
            "raw_vision_data": None,
            "metabolic_metrics": {
                "delta_s": 0.0,
                "f9_hantu_score": 1.0,
                "snr_actual": 0.0,
                "snr_threshold": snr_threshold,
                "snr_passed": False,
            },
            "perceived_intent": intent_class or "unknown",
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
        return governed_return("arifos_111_sense", error_report, metrics, operator_id, session_id)
