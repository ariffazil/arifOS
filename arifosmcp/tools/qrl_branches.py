"""QRL increment 1 — branch generation from the PlanGraph frontier.

Scope 3: upgrade arif_think branches from FIXED TEMPLATES (ba79005b2
generate_paths) to candidates DERIVED from the current PlanGraph frontier +
evidence. Templates remain a labelled fallback (source="template"), never
silent. ADVISORY_ONLY + unsealable (thinking is not acting).
"""

from __future__ import annotations

import re
from typing import Any

from arifosmcp.tools.planner import (
    PlanGraph,
    PlanNode,
    generate_paths,
    load_open_loops,
)

_BRANCH_SOURCE_RE = re.compile(r"open_loop|888_HOLD|prediction|CONTESTED", re.IGNORECASE)


def _frontier_nodes(pg: PlanGraph) -> list[PlanNode]:
    return [n for n in pg.nodes if n.status in ("pending", "frontier")]


def _derived_candidates(pg: PlanGraph, loops: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Derive candidate next-actions from the graph frontier + evidence.

    Each candidate comes from a real frontier node or evidence item (open
    loop / due prediction), NOT from a canned template. Falls back to
    template paths only when derivation yields < 3 distinct candidates —
    and the fallback is labelled.
    """
    candidates: list[dict[str, Any]] = []
    seen_names: set[str] = set()

    # 1) one candidate per frontier node that carries EVIDENCE (evidence_refs
    #    or live provenance). Bare pending nodes with no evidence are not a
    #    basis for an action candidate — they are the template engine's own
    #    bookkeeping nodes.
    evidentiary = [
        n
        for n in _frontier_nodes(pg)
        if n.evidence_refs or n.provenance == "live"
    ]
    for node in evidentiary[:3]:
        name = f"advance-{node.id}"
        if name in seen_names:
            continue
        seen_names.add(name)
        candidates.append(
            {
                "id": f"c_{len(candidates) + 1}",
                "name": name,
                "source": "derived",
                "basis": f"frontier node {node.id}: {node.goal[:90]}",
                "steps": [
                    f"observe current state of {node.id}",
                    f"act reversibly on: {node.goal[:80]}",
                    f"verify against node evidence_refs {node.evidence_refs}",
                ],
                "reversibility": node.reversibility,
                "blast_radius": node.blast_radius,
                "expected_uncertainty_reduction": 0.3,
                "falsifier": f"{node.id} already done/superseded on re-read → dead path",
                "evidence_refs": node.evidence_refs or [node.id],
            }
        )

    # 2) one candidate per open loop (evidence-derived, up to 2)
    for loop in loops[:2]:
        name = f"close-loop-{loop['id']}"
        if name in seen_names:
            continue
        seen_names.add(name)
        candidates.append(
            {
                "id": f"c_{len(candidates) + 1}",
                "name": name,
                "source": "derived",
                "basis": f"carry-forward open loop {loop['id']}: {loop['content'][:90]}",
                "steps": [
                    f"scope loop {loop['id']} from carry-forward (live read)",
                    "propose the smallest reversible closure step",
                    "verify closure against a reality probe before declaring done",
                ],
                "reversibility": "reversible",
                "blast_radius": "organ" if "CONTESTED" in loop["content"].upper() else "session",
                "expected_uncertainty_reduction": 0.45,
                "falsifier": "loop superseded/duplicate on re-read → closure adds nothing",
                "evidence_refs": [loop["id"]],
            }
        )

    return candidates


def _template_candidates(pg: PlanGraph) -> list[dict[str, Any]]:
    """Labelled fallback: the ba79005b2 fixed-template paths."""
    out: list[dict[str, Any]] = []
    for c in pg.candidates:
        out.append(
            {
                "id": c.id,
                "name": c.name,
                "source": "template",  # labelled — never silent
                "basis": "fixed template (ba79005b2 generate_paths fallback)",
                "steps": c.steps,
                "reversibility": c.reversibility,
                "blast_radius": c.blast_radius,
                "expected_uncertainty_reduction": c.expected_uncertainty_reduction,
                "falsifier": c.falsifier,
                "evidence_refs": c.evidence_refs,
            }
        )
    return out


def branches(
    query: str,
    *,
    cf_path: str | None = None,
    now: float | None = None,
    min_candidates: int = 3,
) -> dict[str, Any]:
    """Generate ≥3 candidate next-actions derived from PlanGraph frontier + evidence.

    Returns ADVISORY body: candidates (each source=derived|template),
    plan_graph_id, and honest fallback labels. Never emits a verdict.
    """
    kwargs: dict[str, Any] = {}
    if cf_path:
        kwargs["cf_path"] = cf_path
    if now is not None:
        kwargs["now"] = now
    pg = generate_paths(query or "branches", **kwargs)
    loops = load_open_loops(**({"path": cf_path} if cf_path else {}))

    derived = _derived_candidates(pg, loops)
    candidates: list[dict[str, Any]] = list(derived)
    fallback_used = False
    if len(candidates) < min_candidates:
        fallback_used = True
        for t in _template_candidates(pg):
            if t["name"] not in {c["name"] for c in candidates}:
                candidates.append(t)

    body: dict[str, Any] = {
        "mode": "branches",
        "authority": "ADVISORY",
        "sealable": False,
        "plan_graph_id": pg.id,
        "root_intent": pg.root_intent[:120],
        "n_candidates": len(candidates),
        "candidates": candidates,
        "derived_count": len(derived),
        "template_fallback": fallback_used,
        "advisory": pg.advisory,
        "unsealable": True,
    }
    if len(candidates) < min_candidates:
        body["degraded"] = True
        body["degraded_reason"] = (
            f"only {len(candidates)} distinct candidates derivable from frontier+evidence"
        )
    return body
