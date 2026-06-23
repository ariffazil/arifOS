#!/usr/bin/env python3
"""Bounded explanation engine — arifos-abduction runtime.

Generates K candidate explanations, scores them, filters by the
attestation floor receipt, and emits a BoundedExplanation.

This is a deterministic stub. The real LLM-driven expansion is a separate
runtime concern (the orchestrator calls mcp_arifos_arif_mind_reason or the
organ-specific MCP). The stub produces structurally valid candidates with
synthetic scores so the orchestrator's end-to-end flow can be tested.

Usage:
    python3 bounded_explain.py '<json input>'
    echo '<json input>' | python3 bounded_explain.py -

Input:
{
  "request": "<text>",
  "abstraction_label": {"organ": "GEOX", ...},
  "floor_receipt": {...},
  "evidence_refs": [...],
  "entropy_budget_tokens": 4000,
  "top_k": 3
}
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, asdict
from typing import Any


SCHEMA_VERSION = "2.0.0"
HARD_K_CAP = 7


@dataclass
class Candidate:
    id: str
    claim: str
    evidence_basis: list
    falsifier: str
    score: float
    uncertainty: float
    complexity: int
    entropy_spent: int
    floor_warnings: list

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BoundedExplanation:
    schema_version: str
    request_hash: str
    organ: str
    candidates: list
    best: str | None
    dropped_count: int
    entropy_total: int
    budget_remaining: int
    refinements: int
    bounded: bool
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)


def _hash(payload: Any) -> str:
    canon = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _generate_candidates(
    request: str,
    organ: str,
    evidence_refs: list[str],
    top_k: int,
) -> list[Candidate]:
    """Generate up to 2*top_k raw candidates with deterministic placeholders.

    In production, this is replaced by the organ-specific MCP call
    (mcp_arifos_arif_mind_reason, mcp_geox_geox_evidence_reason, etc.).
    The stub produces structurally valid candidates so the orchestrator
    pipeline can be verified end-to-end.
    """
    raw: list[Candidate] = []
    seeds = [
        f"Primary hypothesis for organ={organ}: standard explanation of '{request[:60]}'",
        f"Alternative hypothesis: regime shift or boundary case for '{request[:60]}'",
        f"Conservative hypothesis: minimal-change explanation of '{request[:60]}'",
        f"Disruptive hypothesis: novel mechanism for '{request[:60]}'",
        f"Historical analogy: prior pattern matching for '{request[:60]}'",
    ]
    for i, claim in enumerate(seeds[: 2 * top_k]):
        score = round(0.95 - i * 0.12, 3)
        complexity = 1 + i
        entropy = 200 + i * 50
        raw.append(
            Candidate(
                id=f"c{i + 1}",
                claim=claim,
                evidence_basis=list(evidence_refs[: 2 + i]),
                falsifier=(
                    f"Disprove c{i + 1} by: running a falsification test that "
                    f"observes the predicted pattern failing under organ={organ}."
                ),
                score=max(0.05, min(0.99, score)),
                uncertainty=round(0.1 + i * 0.05, 3),
                complexity=complexity,
                entropy_spent=entropy,
                floor_warnings=[],
            )
        )
    return raw


def _filter_by_floors(
    candidates: list[Candidate], floor_receipt: dict
) -> tuple[list[Candidate], int]:
    """Drop candidates that would cause attested floors to fail."""
    fail = set(floor_receipt.get("floors_fail", []))
    if not fail:
        return candidates, 0
    dropped = 0
    kept: list[Candidate] = []
    for c in candidates:
        # F12/F9/F1 fail → drop everything (request is fundamentally tainted)
        if fail & {"L12", "F9", "F1", "L11", "L13"}:
            dropped += 1
            continue
        kept.append(c)
    return kept, dropped


def _score(c: Candidate, floor_receipt: dict, max_evidence: int) -> float:
    """Composite score: floor alignment + evidence support + Occam."""
    floor_alignment = 1.0 if c.floor_warnings == [] else 0.7
    evidence_support = min(1.0, len(c.evidence_basis) / max(1, max_evidence))
    occam = 1.0 / (1 + c.complexity * 0.1)
    uncertainty_penalty = c.uncertainty
    score = 0.4 * floor_alignment + 0.3 * evidence_support + 0.2 * occam - 0.1 * uncertainty_penalty
    return round(max(0.0, min(0.99, score)), 3)


def bounded_explain(
    request: str,
    abstraction_label: dict,
    floor_receipt: dict,
    evidence_refs: list[str],
    entropy_budget_tokens: int,
    top_k: int = 3,
    refinements: int = 0,
    prior_best: str | None = None,
) -> BoundedExplanation:
    from datetime import datetime, timezone

    if entropy_budget_tokens <= 0:
        return BoundedExplanation(
            schema_version=SCHEMA_VERSION,
            request_hash=_hash({"request": request}),
            organ=abstraction_label.get("organ", "arifOS"),
            candidates=[],
            best=None,
            dropped_count=0,
            entropy_total=0,
            budget_remaining=entropy_budget_tokens,
            refinements=refinements,
            bounded=True,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    top_k = min(top_k, HARD_K_CAP)
    organ = abstraction_label.get("organ", "arifOS")
    raw = _generate_candidates(request, organ, evidence_refs, top_k)

    # If a prior best is given, seed a refinement candidate first
    if prior_best:
        refinement = Candidate(
            id="c_refine",
            claim=f"Refined version of {prior_best} for '{request[:60]}'",
            evidence_basis=list(evidence_refs[:3]),
            falsifier=f"Disprove by re-running with prior_best != {prior_best}",
            score=0.85,
            uncertainty=0.15,
            complexity=2,
            entropy_spent=250,
            floor_warnings=[],
        )
        raw.insert(0, refinement)

    # Filter by floors
    kept, dropped = _filter_by_floors(raw, floor_receipt)

    # Re-score
    max_evid = max((len(c.evidence_basis) for c in kept), default=1)
    for c in kept:
        c.score = _score(c, floor_receipt, max_evid)

    # Sort by score, keep top_k
    kept.sort(key=lambda c: c.score, reverse=True)
    kept = kept[:top_k]

    # Enforce entropy budget
    entropy_spent = sum(c.entropy_spent for c in kept)
    if entropy_spent > entropy_budget_tokens:
        # Drop the lowest-scoring candidates until under budget
        kept.sort(key=lambda c: (c.score, -c.entropy_spent))
        while kept and entropy_spent > entropy_budget_tokens:
            dropped_c = kept.pop(0)
            entropy_spent -= dropped_c.entropy_spent
        kept.sort(key=lambda c: c.score, reverse=True)
        if not kept:
            return BoundedExplanation(
                schema_version=SCHEMA_VERSION,
                request_hash=_hash({"request": request}),
                organ=organ,
                candidates=[],
                best=None,
                dropped_count=dropped,
                entropy_total=0,
                budget_remaining=entropy_budget_tokens,
                refinements=refinements,
                bounded=True,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

    best = kept[0].id if kept else None
    return BoundedExplanation(
        schema_version=SCHEMA_VERSION,
        request_hash=_hash({"request": request}),
        organ=organ,
        candidates=[c.to_dict() for c in kept],
        best=best,
        dropped_count=dropped,
        entropy_total=entropy_spent,
        budget_remaining=entropy_budget_tokens - entropy_spent,
        refinements=refinements,
        bounded=True,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def main() -> int:
    raw = sys.stdin.read() if len(sys.argv) < 2 or sys.argv[1] == "-" else open(sys.argv[1]).read()
    data = json.loads(raw)
    result = bounded_explain(
        request=data.get("request", ""),
        abstraction_label=data.get("abstraction_label", {}),
        floor_receipt=data.get("floor_receipt", {}),
        evidence_refs=data.get("evidence_refs", []),
        entropy_budget_tokens=int(data.get("entropy_budget_tokens", 4000)),
        top_k=int(data.get("top_k", 3)),
        refinements=int(data.get("refinements", 0)),
        prior_best=data.get("prior_best"),
    )
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
