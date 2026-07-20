"""
arifosmcp/tools/prl_gate.py — PRL Phase 1: Dual-Gate Precedent Retrieval

GATE 1: Geometric Intuition — cosine similarity search with tau >= 0.95
GATE 2: Structural Hard-Filter — Qdrant payload filter on blast_radius
OMEGA Trigger: ambiguous context → HOLD for 888

Constitutional: F2 (truth), F9 (anti-hallucination), F11 (audit)
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any

from arifosmcp.intelligence.embeddings import embed

logger = logging.getLogger(__name__)

PRL_COLLECTION = "arifos_precedent"
PRL_VECTOR_DIM = 1024
PRL_SCORE_THRESHOLD = 0.95

_BLAST_RADIUS_HIERARCHY: dict[str, int] = {
    "L1_LOCAL": 1,
    "L2_SYSTEM": 2,
    "L3_CRITICAL": 3,
}

_QDRANT_CLIENT: Any = None


def _get_qdrant() -> Any:
    """Return QdrantClient or None if unreachable."""
    global _QDRANT_CLIENT
    if _QDRANT_CLIENT is not None:
        return _QDRANT_CLIENT
    try:
        from qdrant_client import QdrantClient  # noqa: PLC0415

        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        client = QdrantClient(url=qdrant_url, timeout=5)
        client.get_collections()
        _QDRANT_CLIENT = client
        return client
    except Exception as exc:
        logger.debug("Qdrant unreachable for PRL gate: %s", exc)
        return None


@dataclass
class PrecedentResult:
    """Result of a PRL precedent query.

    Attributes:
        matched: Whether any precedent matched above the tau threshold
        precedents: List of matching precedent entries with similarity scores
        hold_for_sovereign: True if context is ambiguous (OMEGA trigger)
        tau_max: Highest similarity score found
        gate1_passed: Whether geometric similarity threshold was met
        gate2_passed: Whether blast_radius structural filter was met
    """

    matched: bool = False
    precedents: list[dict[str, Any]] = field(default_factory=list)
    hold_for_sovereign: bool = False
    tau_max: float = 0.0
    gate1_passed: bool = False
    gate2_passed: bool = False


def query_precedent(
    query_text: str,
    current_blast_radius: str = "L2_SYSTEM",
    top_k: int = 3,
) -> PrecedentResult:
    """Search the PRL precedent index for geometrically similar past seals.

    DUAL-GATE architecture:
      GATE 1: Cosine similarity >= 0.95 threshold
      GATE 2: Payload filter — blast_radius must match or be >= current

    Args:
        query_text: The text to search for precedents (e.g., proposed action)
        current_blast_radius: Consequence tier of the current query
        top_k: Maximum number of precedent matches to return

    Returns:
        PrecedentResult with matches, similarity scores, and hold status
    """
    client = _get_qdrant()
    if client is None:
        logger.warning("PRL gate: Qdrant unavailable — returning no precedent")
        return PrecedentResult(
            matched=False,
            hold_for_sovereign=False,
        )

    # Check if collection exists
    try:
        existing = {c.name for c in client.get_collections().collections}
        if PRL_COLLECTION not in existing:
            logger.info("PRL gate: collection '%s' does not exist yet", PRL_COLLECTION)
            return PrecedentResult(
                matched=False,
                hold_for_sovereign=False,
            )
    except Exception as exc:
        logger.warning("PRL gate: collection check failed: %s", exc)
        return PrecedentResult(matched=False, hold_for_sovereign=False)

    # Determine acceptable blast radius levels for GATE 2
    query_level = _BLAST_RADIUS_HIERARCHY.get(current_blast_radius, 2)
    acceptable_radii = [k for k, v in _BLAST_RADIUS_HIERARCHY.items() if v >= query_level]
    if not acceptable_radii:
        acceptable_radii = ["L2_SYSTEM"]

    try:
        from qdrant_client.models import (
            FieldCondition,
            Filter,
            MatchAny,
        )  # noqa: PLC0415

        vector = embed(query_text, dim=PRL_VECTOR_DIM)

        # GATE 2: Payload filter on blast_radius
        payload_filter = Filter(
            must=[
                FieldCondition(
                    key="blast_radius",
                    match=MatchAny(any=acceptable_radii),
                ),
            ],
        )

        results = client.query_points(
            collection_name=PRL_COLLECTION,
            query=vector,
            query_filter=payload_filter,
            limit=top_k,
            score_threshold=PRL_SCORE_THRESHOLD,
            with_payload=True,
        ).points
    except Exception as exc:
        logger.error("PRL gate: Qdrant search failed: %s", exc)
        return PrecedentResult(matched=False, hold_for_sovereign=False)

    # Process results
    precedents: list[dict[str, Any]] = []
    tau_max = 0.0
    gate1_passed = False

    for pt in results:
        score = float(getattr(pt, "score", 0.0))
        if score > tau_max:
            tau_max = score
        if score >= PRL_SCORE_THRESHOLD:
            gate1_passed = True
        payload = pt.payload or {}
        precedents.append(
            {
                "entry_id": str(payload.get("entry_id", getattr(pt, "id", ""))),
                "payload_summary": str(payload.get("payload_summary", "")),
                "similarity": round(score, 4),
                "blast_radius": str(payload.get("blast_radius", "L2_SYSTEM")),
                "session_id": str(payload.get("session_id", "")),
                "timestamp": str(payload.get("timestamp", "")),
            }
        )

    gate2_passed = len(precedents) > 0

    # OMEGA trigger: if we got results but GATE 1 threshold wasn't met,
    # context is ambiguous — hold for sovereign
    hold = bool(precedents) and not gate1_passed

    return PrecedentResult(
        matched=gate1_passed and gate2_passed,
        precedents=precedents,
        hold_for_sovereign=hold,
        tau_max=tau_max,
        gate1_passed=gate1_passed,
        gate2_passed=gate2_passed,
    )


def prl_precheck(
    query_text: str,
    blast_radius: str = "L2_SYSTEM",
) -> dict[str, Any]:
    """Pre-flight PRL check before executing a governed action.

    Called before arif_judge to surface binding precedent.
    If precedent matches, the action is geometrically bound —
    must comply with past verdicts or escalate to 888.

    Args:
        query_text: Description of the proposed action
        blast_radius: Consequence tier of the proposed action

    Returns:
        Dict with {block_precedent, matched_rules, tau_max, hold_for_888, reason}
    """
    result = query_precedent(query_text, current_blast_radius=blast_radius)

    if result.hold_for_sovereign:
        return {
            "block_precedent": True,
            "hold_for_888": True,
            "reason": "ambiguous_context",
            "tau_max": result.tau_max,
            "matched_rules": result.precedents,
        }

    if result.matched:
        return {
            "block_precedent": True,
            "hold_for_888": False,
            "reason": "precedent_matched",
            "tau_max": result.tau_max,
            "matched_rules": result.precedents,
        }

    return {
        "block_precedent": False,
        "hold_for_888": False,
        "reason": "no_precedent",
        "tau_max": result.tau_max,
        "matched_rules": [],
    }


def inject_prl_constraint(
    precheck_result: dict[str, Any],
    query_text: str = "",
    blast_radius: str = "L2_SYSTEM",
) -> str:
    """Format PRL precedent as an F9-compliant constraint block.

    Suitable for injection into the arif_judge reasoning chain.
    Provides geometric binding without claiming authority —
    precedents are evidence, not verdicts.

    Args:
        precheck_result: Output from prl_precheck()
        query_text: The original query (for context)
        blast_radius: Current blast radius classification

    Returns:
        Formatted constraint block string for judge injection
    """
    if not precheck_result.get("block_precedent"):
        return (
            "## PRECEDENT CONSTRAINT (VAULT999)\n"
            "No binding precedent found.  Proceed with standard judgment.\n"
        )

    matched = precheck_result.get("matched_rules", [])
    tau_max = precheck_result.get("tau_max", 0.0)
    hold_for_888 = precheck_result.get("hold_for_888", False)

    lines = [
        "## PRECEDENT CONSTRAINT (VAULT999) — ",
        "The following verdicts are geometrically bound to this query. ",
        "Comply or escalate to 888.",
        "",
        f"Query: {query_text[:200]}{'...' if len(query_text) > 200 else ''}",
        f"Blast radius: {blast_radius}",
        f"τ: {tau_max:.4f}",
        f"Threshold: {PRL_SCORE_THRESHOLD}",
        "",
    ]

    if hold_for_888:
        lines.append("## OMEGA TRIGGER: Ambiguous context — HOLD for 888")
        lines.append("Similarity below threshold.  Precedent exists but geometry is weak.")
        lines.append("Sovereign review required before execution.")
        lines.append("")

    if matched:
        lines.append("### Matched Precedents")
        lines.append("")
        for i, prec in enumerate(matched):
            lines.append(f"**Precedent {i + 1}:**")
            lines.append(f"- Entry ID: `{prec['entry_id']}`")
            lines.append(f"- Similarity: {prec['similarity']:.4f}")
            lines.append(f"- Blast Radius: {prec['blast_radius']}")
            lines.append(f"- Summary: {prec['payload_summary'][:300]}")
            lines.append("")

    return "\n".join(lines)


__all__ = [
    "PrecedentResult",
    "query_precedent",
    "prl_precheck",
    "inject_prl_constraint",
    "PRL_COLLECTION",
    "PRL_SCORE_THRESHOLD",
]
