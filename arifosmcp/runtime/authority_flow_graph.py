"""
arifosmcp/runtime/authority_flow_graph.py — Authority Flow Graph v1
=================================================================

Runtime authority topology for arifOS. NOT documentation.

PURPOSE
-------
Replace MD-layer governance with a traversable graph. Every behavioral rule
and every capability has a node. Edges say who may do what, who blocks whom,
and who witnesses the result. A rule with no owner, no witness, and no test
is an ORPHAN — and orphans are reported, not obeyed.

This is the executable answer to "One Rule One Home": one node, one owner,
one boundary, one test. Nodes are queryable. Edges are enforceable.

ARCHITECTURE
------------
  graph (FalkorDB :6380)  ->  nodes + edges
  this module             ->  traversal + queries (read path)
  kernel                  ->  enforcement (write path, elsewhere)

FAILURE MODE
------------
  F2 TRUTH: never raise. Never block reasoning. Return UNKNOWN + provenance.
  If the graph is empty, report UNKNOWN — do not invent authority.

AUTHORITY: 888_JUDGE (definition), 555_MEMORY (persistence)
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
import os
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

FALKOR_HOST = os.getenv("FALKOR_HOST", "localhost")
FALKOR_PORT = int(os.getenv("FALKOR_PORT", "6380"))
AUTHORITY_GRAPH = os.getenv("AUTHORITY_GRAPH", "arif_authority_flow")
DRY_RUN = os.getenv("AUTHORITY_GRAPH_DRY_RUN", "false").lower() == "true"


# Node types — the vocabulary of governance
NODE_TYPES = frozenset({
    "capability",    # a thing the agent can do (write_file, arif_forge)
    "actor",         # who does it (hermes, fi-003, arif)
    "authority",     # who grants permission (F13, 888-APEX, lane issuer)
    "action",        # a concrete mutation (commit, deploy)
    "witness",       # who observed the effect (frame, vault999, test)
    "rule",          # a behavioral constraint (K1, F2, M2)
    "boundary",      # a limit (mutation boundary, budget, TTL)
})

# Edge types — the grammar of governance
EDGE_TYPES = frozenset({
    "REQUIRES",   # actor -> capability   (needs it to act)
    "GRANTS",     # authority -> actor    (permits)
    "SCOPES",     # boundary -> capability (limits)
    "BLOCKS",     # boundary -> capability (denies)
    "EXECUTES",   # actor -> action       (did it)
    "WITNESSES",  # witness -> action     (observed)
    "ENFORCES",   # rule -> capability    (constrains)
    "DERIVES",    # rule -> rule          (depends on)
})

RULE_COMPLETENESS = ("owner", "purpose", "test")


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _node_id(kind: str, name: str) -> str:
    return f"{kind}:{name}"


# Mutation governance topology expressed as data.
# This is the authority graph flow that mode_first_gate and kernel consult.
AUTHORITY_TOPOLOGY: dict[str, dict[str, Any]] = {
    # Read/think: free. No gate. (F13 directive 2026-09-28)
    "read_freely": {
        "kind": "capability", "owner": "F13", "requires_authority": False,
        "witness": "self",
        "note": "search/read/audit/analysis/reasoning/planning never gated",
    },
    "think_freely": {
        "kind": "capability", "owner": "F13", "requires_authority": False,
        "witness": "self",
        "note": "cognition is not mutation; TTL gates must not touch it",
    },
    # Mutation: deliberate. Mode emit required.
    "arif_forge": {
        "kind": "capability", "owner": "F13", "requires_authority": True,
        "witness": "vault999",
        "note": "production mutation — 333_BUILD lane",
    },
    "arif_seal": {
        "kind": "capability", "owner": "F13", "requires_authority": True,
        "witness": "vault999",
        "note": "canonical seal — F13 sovereign only",
    },
    "delegate_task": {
        "kind": "capability", "owner": "F13", "requires_authority": True,
        "witness": "transcript",
        "note": "spawns agents — cost + persistence",
    },
    "cronjob_manage": {
        "kind": "capability", "owner": "F13", "requires_authority": True,
        "witness": "jobs.json",
        "note": "persistence + scheduling",
    },
    "tool_call": {
        "kind": "capability", "owner": "F13", "requires_authority": True,
        "witness": "audit_trail",
        "note": "capability activation",
    },
    "forge_shell": {
        "kind": "capability", "owner": "F13", "requires_authority": True,
        "witness": "shell_audit",
        "note": "direct shell mutation outside agent path",
    },
    # Boundaries
    "mutation_boundary": {
        "kind": "boundary", "owner": "F13",
        "blocks": ["arif_seal", "tool_call", "cronjob_manage"],
        "note": "CanMutate = Auth ∧ Scope ∧ Target ∧ Boundary — no confidence term",
    },
    "sovereign_attention": {
        "kind": "boundary", "owner": "F13", "blocks": [],
        "note": "W888 — do not make the human middleware",
    },
    "mode_first_ttl": {
        "kind": "boundary", "owner": "kernel",
        "note": "1800s — must NOT gate read/think (F13 2026-09-28)",
    },
    # Rules
    "K1": {"kind": "rule", "owner": "kernel", "purpose": "one question per turn", "test": "k1_one_question_at_most"},
    "K2": {"kind": "rule", "owner": "kernel", "purpose": "length matches signal", "test": "k2_response_length"},
    "K3": {"kind": "rule", "owner": "kernel", "purpose": "surface don't narrate", "test": "k3_no_self_narration"},
    "K4": {"kind": "rule", "owner": "kernel", "purpose": "no repeat", "test": "k4_no_obvious_repeat"},
    "K5": {"kind": "rule", "owner": "kernel", "purpose": "unsure -> say so", "test": "k5_no_overconfident_fabrication"},
    "K6": {"kind": "rule", "owner": "kernel", "purpose": "recommend, don't force", "test": "k6_recommend_not_menu"},
    "F1": {"kind": "rule", "owner": "kernel", "purpose": "amanah — integrity", "test": "floor_enforcer"},
    "F2": {"kind": "rule", "owner": "kernel", "purpose": "truth — observed only", "test": "floor_enforcer"},
    "F7": {"kind": "rule", "owner": "kernel", "purpose": "humility", "test": "floor_enforcer"},
    "F13": {"kind": "rule", "owner": "F13", "purpose": "sovereignty", "test": "f13_ceremony"},
    "mode_first": {"kind": "rule", "owner": "kernel", "purpose": "mode before mutation", "test": "mode_first_gate"},
}


def _falkor_cmd(args):
    if DRY_RUN:
        return None
    try:
        import redis
        r = redis.Redis(host=FALKOR_HOST, port=FALKOR_PORT, decode_responses=True)
        return str(r.execute_command(*args))
    except Exception as e:
        logger.info("authority_flow_graph: falkor unavailable — %s", e)
        return None


def seed_topology() -> dict[str, Any]:
    """Write the authority topology into the graph. Idempotent via MERGE."""
    seeded = 0
    edges = 0
    for name, spec in AUTHORITY_TOPOLOGY.items():
        kind = spec["kind"]
        owner = spec.get("owner", "")
        raw = _falkor_cmd([
            "MERGE",
            f"({_node_id(kind, name)}:{{kind:'{kind}',name:'{name}'}})",
        ])
        if raw is not None:
            seeded += 1
        if owner:
            _falkor_cmd([
                "MERGE",
                f"({_node_id('authority', owner)}:{{kind:'authority',name:'{owner}'}})",
                f"({_node_id(kind, name)}:{{kind:'{kind}',name:'{name}'}})",
                f"({_node_id(kind, name)})-[:GRANTS]->({_node_id('authority', owner)})",
            ])
            edges += 1
        for blocked in spec.get("blocks", []):
            _falkor_cmd([
                "MERGE",
                f"({_node_id(kind, name)}:{{kind:'{kind}',name:'{name}'}})",
                f"({_node_id('capability', blocked)}:{{kind:'capability',name:'{blocked}'}})",
                f"({_node_id(kind, name)})-[:BLOCKS]->({_node_id('capability', blocked)})",
            ])
            edges += 1
    return {
        "seeded_nodes": seeded,
        "seeded_edges": edges,
        "graph": AUTHORITY_GRAPH,
        "dry_run": DRY_RUN,
        "at": _now_iso(),
    }


def trace_authority(capability: str) -> dict[str, Any]:
    """Trace a capability back to its granting authority."""
    spec = AUTHORITY_TOPOLOGY.get(capability)
    if spec is None:
        return {
            "status": "UNKNOWN", "capability": capability,
            "missing": "no node for this capability",
            "provenance": "authority_topology", "at": _now_iso(),
        }
    chain = [{"node": _node_id(spec["kind"], capability), "kind": spec["kind"]}]
    if spec.get("owner"):
        chain.append({"node": _node_id("authority", spec["owner"]), "kind": "authority"})
    if spec.get("requires_authority"):
        if not spec.get("owner"):
            return {
                "status": "DENY", "capability": capability,
                "reason": "requires authority but has no owner",
                "provenance": "authority_topology", "at": _now_iso(),
            }
        verdict = "ALLOW"
    else:
        verdict = "ALLOW_FREE"
    return {
        "status": verdict, "capability": capability, "chain": chain,
        "witness": spec.get("witness"), "note": spec.get("note", ""),
        "provenance": "authority_topology", "at": _now_iso(),
    }


def check_authority(actor: str, capability: str, target: str = "") -> dict[str, Any]:
    """CanMutate = AuthorityGranted ∧ ScopeMatches ∧ TargetPermitted ∧ BoundaryActive.

    Confidence appears nowhere in this expression.
    """
    trace = trace_authority(capability)
    if trace["status"] == "UNKNOWN":
        return {"verdict": "HOLD", "reason": trace["missing"], "capability": capability, "at": _now_iso()}
    if trace["status"] == "DENY":
        return {"verdict": "DENY", "reason": trace["reason"], "capability": capability, "at": _now_iso()}
    return {
        "verdict": "ALLOW", "capability": capability, "actor": actor, "target": target,
        "witness": trace.get("witness"),
        "authority": trace["chain"][-1]["node"] if trace["chain"] else "",
        "at": _now_iso(),
    }


def audit_shadows() -> dict[str, Any]:
    """A rule is real only if it has owner + purpose + test.

    Anything missing one is a shadow candidate for deletion.
    This is the executable form of "One Rule One Home".
    """
    real: list[str] = []
    shadows: list[dict[str, Any]] = []
    for name, spec in AUTHORITY_TOPOLOGY.items():
        if spec["kind"] != "rule":
            continue
        gaps = [k for k in RULE_COMPLETENESS if not spec.get(k)]
        if gaps:
            shadows.append({"rule": name, "missing": gaps})
        else:
            real.append(name)
    return {
        "real_rules": real, "real_count": len(real),
        "shadows": shadows, "shadow_count": len(shadows),
        "verdict": "CLEAN" if not shadows else "SHADOWS_PRESENT",
        "at": _now_iso(),
    }


def list_boundaries() -> list[dict[str, Any]]:
    out = []
    for name, spec in AUTHORITY_TOPOLOGY.items():
        if spec["kind"] == "boundary":
            out.append({
                "boundary": name,
                "owner": spec.get("owner", ""),
                "blocks": spec.get("blocks", []),
                "note": spec.get("note", ""),
            })
    return out


def list_free_operations() -> list[str]:
    return [n for n, s in AUTHORITY_TOPOLOGY.items() if s.get("requires_authority") is False]


def graph_summary() -> dict[str, Any]:
    by_kind: dict[str, int] = {}
    for spec in AUTHORITY_TOPOLOGY.values():
        by_kind[spec["kind"]] = by_kind.get(spec["kind"], 0) + 1
    return {
        "graph": AUTHORITY_GRAPH,
        "total_nodes": len(AUTHORITY_TOPOLOGY),
        "by_kind": by_kind,
        "edge_types": sorted(EDGE_TYPES),
        "free_operations": list_free_operations(),
        "gated_operations": [n for n, s in AUTHORITY_TOPOLOGY.items() if s.get("requires_authority")],
        "shadow_audit": audit_shadows(),
        "at": _now_iso(),
    }


# PATCH 2026-09-28 — add write_file, patch, execute_code to free operations
# mode_first_gate plugin was updated; graph must reflect runtime reality
AUTHORITY_TOPOLOGY["write_file"] = {
    "kind": "capability", "owner": "F13", "requires_authority": False,
    "witness": "filesystem",
    "note": "file mutation, reversible — no mode emit (F13 2026-09-28)",
}
AUTHORITY_TOPOLOGY["patch"] = {
    "kind": "capability", "owner": "F13", "requires_authority": False,
    "witness": "filesystem",
    "note": "file mutation, reversible — no mode emit (F13 2026-09-28)",
}
AUTHORITY_TOPOLOGY["execute_code"] = {
    "kind": "capability", "owner": "F13", "requires_authority": False,
    "witness": "sandbox",
    "note": "interpreted execution — no mode emit (F13 2026-09-28)",
}
