"""
Strange Loop Detector — arif_think(mode="strange_loop_audit")

Detects self-referential reasoning patterns where claims cite earlier
outputs from the same reasoning chain without grounding in the original
prompt/document tokens. This is the "benchmark hallucination" pattern
described in SHADOW-DS-006 (reasoning_cascade_compound).

Forged: 2026-08-03 by 333-AGI (Δ MIND)
Trigger: External agent Gödel lock analysis → SHADOW-DS-006

Architecture:
  Parse reasoning trace into claim-citation pairs
  → Identify citations that point to earlier outputs in the same chain
  → Check if those earlier outputs trace back to input tokens
  → Flag PHANTOM_FOUNDATION if grounding is broken
  → Return AUDIT_SCORE (0-1) with flagged segments and verdict

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import re
from typing import Any


def audit_strange_loop(
    reasoning_trace: str,
    original_prompt: str | None = None,
    original_document_tokens: list[str] | None = None,
) -> dict[str, Any]:
    """
    Audit a reasoning trace for self-referential (strange loop) patterns.

    A "strange loop" occurs when an agent's chain-of-thought validates itself
    by appealing to its own earlier outputs as if they were external evidence.
    This creates the Gödel lock: the agent cannot prove, from within its own
    architecture, that it hasn't drifted from the user's original intent.

    Args:
        reasoning_trace: Full chain-of-thought or multi-step reasoning text
        original_prompt: The original user prompt (for grounding comparison)
        original_document_tokens: Document tokens the agent was given as input

    Returns:
        {
            "audit_score": float,       # 0.0-1.0: proportion of claims with input grounding
            "total_claims": int,
            "grounded_claims": int,
            "phantom_count": int,
            "phantom_foundations": [...],  # flagged segments
            "self_referential_chains": [...],
            "verdict": "PASS" | "CAUTION" | "HOLD",
            "strange_loop_detected": bool,
            "shadow_ref": "SHADOW-DS-006",
        }
    """
    # Step 1: Extract claims from reasoning trace
    claims = _extract_claims(reasoning_trace)

    # Step 2: Identify self-referential citation patterns
    citations = _classify_citations(claims)

    # Step 3: Build grounding graph — can each claim trace back to input?
    grounding_graph = _build_grounding_graph(
        claims, citations, original_prompt, original_document_tokens
    )

    # Step 4: Detect phantom foundations
    phantoms = _detect_phantoms(grounding_graph)

    # Step 5: Find self-referential chains (multi-claim loops)
    chains = _find_self_referential_chains(grounding_graph)

    # Step 6: Compute audit score
    total = len(claims) or 1
    grounded = total - len(phantoms)
    audit_score = grounded / total

    if audit_score >= 0.9:
        verdict = "PASS"
    elif audit_score >= 0.7:
        verdict = "CAUTION"
    else:
        verdict = "HOLD"

    return {
        "audit_score": round(audit_score, 3),
        "total_claims": total,
        "grounded_claims": grounded,
        "phantom_count": len(phantoms),
        "phantom_foundations": phantoms,
        "self_referential_chains": chains,
        "verdict": verdict,
        "strange_loop_detected": len(phantoms) > 0 or len(chains) > 0,
        "shadow_ref": "SHADOW-DS-006",
        "mode": "strange_loop_audit",
        "calhoun_risk": "ELEVATED" if audit_score < 0.8 and len(claims) > 5 else "NORMAL",
        "scope": {
            "trace_bytes": len(reasoning_trace),
            "prompt_provided": original_prompt is not None,
            "prompt_bytes": len(original_prompt) if original_prompt else 0,
            "document_tokens_count": len(original_document_tokens)
            if original_document_tokens
            else 0,
            "grounding_coverage": "FULL"
            if (original_prompt and original_document_tokens)
            else ("PARTIAL" if (original_prompt or original_document_tokens) else "NONE"),
            "limitation_note": (
                "Existence verdicts are scoped to the provided input tokens. "
                "NOT_FOUND in this scope does NOT mean the referent does not exist "
                "elsewhere. Phantom classification means 'no grounding found in the "
                "supplied evidence,' NOT 'the claim is false.' Scope: reasoning_trace + "
                "original_prompt + original_document_tokens. External referents may "
                "exist outside this scope."
            ),
        },
    }


# ── Internal helpers ──────────────────────────────────────────────────────

_SELF_REF_PATTERNS: list[tuple[str, str]] = [
    # (regex pattern, label)
    (
        r"as\s+(?:I|we)?\s*previously\s+(?:reasoned|stated|established|mentioned|shown|argued|noted|demonstrated)",
        "SELF_REF_PREVIOUS",
    ),
    (
        r"as\s+(?:I|we)\s+(?:previously\s+)?(?:established|showed|determined|found|concluded|demonstrated)\s+(?:above|earlier|before|previously)",
        "SELF_REF_PERSONAL",
    ),
    (r"from\s+(?:the\s+above|this|our\s+analysis|the\s+foregoing)", "SELF_REF_ANAPHORIC"),
    (
        r"consistent\s+with\s+(?:my|our)\s+(?:earlier|previous)\s+(?:finding|analysis|reasoning|conclusion)",
        "SELF_REF_CONSISTENT",
    ),
    (r"building\s+on\s+(?:the\s+previous|this\s+foundation|the\s+above)", "SELF_REF_BUILDING"),
    (
        r"(?:recall|remember)\s+(?:that|from\s+earlier)\s+(?:I|we)\s+(?:said|noted|established|reasoned)",
        "SELF_REF_RECALL",
    ),
    (
        r"(?:this\s+(?:confirms|validates|supports|aligns\s+with))\s+(?:my|our|the)\s+(?:earlier|previous|above)",
        "SELF_REF_CONFIRMATION",
    ),
]


def _extract_claims(trace: str) -> list[dict[str, Any]]:
    """Extract structured claims from a reasoning trace."""
    claims: list[dict[str, Any]] = []

    # Pattern: Numbered claims
    numbered = re.finditer(
        r"(?:Claim|Step|Finding|Assertion)\s*(\d+)[:.)]\s*(.+?)(?=(?:Claim|Step|Finding|Assertion)\s*\d+|$)",
        trace,
        re.IGNORECASE | re.DOTALL,
    )
    for m in numbered:
        claims.append(
            {
                "id": f"claim_{m.group(1)}",
                "text": m.group(2).strip(),
                "type": "explicit",
                "position": m.start(),
            }
        )

    # Pattern: Conclusive statements
    conclusive = re.finditer(
        r"(?:Therefore|Thus|Hence|I\s+conclude|The\s+answer\s+is|It\s+follows\s+that)\s*,?\s*(.+?)(?=[.!]\s|$)",
        trace,
        re.IGNORECASE,
    )
    for i, m in enumerate(conclusive):
        cid = f"conclusion_{i + 1}"
        if not any(c["id"] == cid for c in claims):
            claims.append(
                {
                    "id": cid,
                    "text": m.group(1).strip(),
                    "type": "conclusion",
                    "position": m.start(),
                }
            )

    # Fallback: single claim from entire trace
    if not claims:
        claims.append(
            {
                "id": "trace_root",
                "text": trace.strip(),
                "type": "implicit",
                "position": 0,
            }
        )

    return claims


def _classify_citations(claims: list[dict[str, Any]]) -> dict[str, list[str]]:
    """For each claim, detect self-referential citation patterns."""
    citations: dict[str, list[str]] = {}
    for claim in claims:
        refs: list[str] = []
        for pattern, label in _SELF_REF_PATTERNS:
            if re.search(pattern, claim["text"], re.IGNORECASE):
                refs.append(label)
        citations[claim["id"]] = refs
    return citations


def _build_grounding_graph(
    claims: list[dict[str, Any]],
    citations: dict[str, list[str]],
    original_prompt: str | None,
    document_tokens: list[str] | None,
) -> dict[str, dict[str, Any]]:
    """For each claim: is it self-referential AND ungrounded in input?"""
    graph: dict[str, dict[str, Any]] = {}

    for claim in claims:
        self_refs = citations.get(claim["id"], [])
        has_self_ref = len(self_refs) > 0

        # Grounding check: does claim text overlap with input?
        grounded_in_prompt = False
        grounded_in_document = False

        if original_prompt:
            claim_words = set(claim["text"].lower().split())
            prompt_words = set(original_prompt.lower().split())
            if claim_words:
                overlap = len(claim_words & prompt_words) / len(claim_words)
                grounded_in_prompt = overlap > 0.15

        if document_tokens:
            doc_text = " ".join(t.lower() for t in document_tokens)
            substantive = [t for t in claim["text"].lower().split() if len(t) > 3]
            if substantive:
                grounded_in_document = any(t in doc_text for t in substantive)

        ground_anchor = grounded_in_prompt or grounded_in_document

        graph[claim["id"]] = {
            "claim": claim,
            "self_referential": has_self_ref,
            "self_ref_types": self_refs,
            "grounded_in_input": ground_anchor,
            "phantom": has_self_ref and not ground_anchor,
        }

    return graph


def _detect_phantoms(graph: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Find phantom foundations: self-ref claims with no input grounding."""
    phantoms: list[dict[str, Any]] = []
    for cid, node in graph.items():
        if node["phantom"]:
            phantoms.append(
                {
                    "claim_id": cid,
                    "claim_text": node["claim"]["text"][:300],
                    "claim_type": node["claim"]["type"],
                    "position": node["claim"]["position"],
                    "self_ref_types": node["self_ref_types"],
                    "severity": "HIGH" if len(node["self_ref_types"]) >= 2 else "MEDIUM",
                    "reason": (
                        "PHANTOM_FOUNDATION: Claim cites earlier reasoning chain output "
                        "without grounding in original prompt or document tokens. "
                        "The agent's own output has become its only evidence — "
                        "a self-referential Gödel loop."
                    ),
                }
            )
    return phantoms


def _find_self_referential_chains(
    graph: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Find chains of phantom claims that form closed loops."""
    chains: list[dict[str, Any]] = []
    phantom_ids = [cid for cid, node in graph.items() if node["phantom"]]

    if len(phantom_ids) >= 2:
        chains.append(
            {
                "chain_ids": phantom_ids,
                "length": len(phantom_ids),
                "pattern": "PHANTOM_CHAIN",
                "risk": "CRITICAL" if len(phantom_ids) >= 3 else "HIGH",
                "description": (
                    f"Chain of {len(phantom_ids)} claims with no grounding in input — "
                    "a closed strange loop where each claim validates the next without "
                    "any external anchor. This is the Calhoun equilibrium: the agent "
                    "is breeding only with its own thoughts."
                ),
            }
        )

    return chains
