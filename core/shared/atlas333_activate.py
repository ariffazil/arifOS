#!/usr/bin/env python3
"""
ATLAS333-ABC-GRAPH: Full Activation Pipeline
=============================================
Wires LΘΦ router → Qdrant (proximity) → FalkorDB (causality) → context injection.

Call: python3 atlas333_activate.py "query text" [--top-k 5] [--format json|text] [--graph]

The pipeline:
  L(text) → lane (CRISIS|FACTUAL|SOCIAL|CARE)
  Θ(lane) → demand tensor (τ, κ, ρ)
  Φ(text) → GPV (lane + tensor + paradox axes)
  Qdrant → top-k paradoxes (semantic proximity)
  FalkorDB → trace relationships between them (tension topology)
  Inject → paradoxes + relationship graph for agent reasoning

Architecture:
  Qdrant answers: "Which paradoxes are relevant?"
  FalkorDB answers: "How do they relate to each other?"
  Agent receives BOTH: proximity AND causality.

DITEMPA BUKAN DIBERI — Forged 2026-08-01 by 333-AGI Δ MIND
"""

import sys, json, argparse, os
from pathlib import Path

sys.path.insert(0, "/root/arifOS")
sys.path.insert(0, "/opt/arifos")


def L_lane_classify(text: str) -> dict:
    """Classify text into lane: CRISIS, FACTUAL, SOCIAL, CARE, UNKNOWN"""
    text_lower = text.lower()

    crisis_words = [
        "emergency",
        "breach",
        "attack",
        "destroy",
        "violation",
        "irreversible",
        "secret leak",
        "sovereign breach",
        "halt",
        "stop immediately",
        "override",
    ]
    if any(w in text_lower for w in crisis_words):
        return {"lane": "CRISIS", "confidence": 0.85}

    social_words = [
        "hello",
        "hi ",
        "how are you",
        "conversation",
        "chat",
        "talk",
        "personal",
        "feel",
        "opinion",
        "casual",
        "joke",
    ]
    if any(w in text_lower for w in social_words):
        return {"lane": "SOCIAL", "confidence": 0.75}

    care_words = [
        "health",
        "sleep",
        "fatigue",
        "tired",
        "rest",
        "dignity",
        "wellbeing",
        "vitality",
        "stress",
        "burnout",
    ]
    if any(w in text_lower for w in care_words):
        return {"lane": "CARE", "confidence": 0.70}

    factual_words = [
        "build",
        "deploy",
        "test",
        "code",
        "analyze",
        "data",
        "evidence",
        "query",
        "search",
        "find",
        "map",
        "audit",
        "check",
        "verify",
        "probe",
        "measure",
        "compute",
        "calculate",
        "execute",
        "run",
    ]
    if any(w in text_lower for w in factual_words):
        return {"lane": "FACTUAL", "confidence": 0.80}

    return {"lane": "FACTUAL", "confidence": 0.60}


def Theta_demand_tensor(lane: str) -> dict:
    """Derive demand tensor (τ truth, κ care, ρ risk) from lane"""
    tensors = {
        "CRISIS": {"tau": 0.95, "kappa": 0.40, "rho": 0.90},
        "FACTUAL": {"tau": 0.85, "kappa": 0.20, "rho": 0.30},
        "SOCIAL": {"tau": 0.30, "kappa": 0.85, "rho": 0.15},
        "CARE": {"tau": 0.40, "kappa": 0.90, "rho": 0.50},
        "UNKNOWN": {"tau": 0.50, "kappa": 0.50, "rho": 0.50},
    }
    return tensors.get(lane, tensors["UNKNOWN"])


def search_qdrant(query_text: str, top_k: int = 5) -> list:
    """Search Qdrant atlas333_eureka for relevant paradoxes"""
    try:
        from sentence_transformers import SentenceTransformer
        from qdrant_client import QdrantClient

        model = SentenceTransformer("BAAI/bge-m3", trust_remote_code=True)
        client = QdrantClient(host="localhost", port=6333)

        embedding = model.encode([query_text], normalize_embeddings=True)[0]
        results = client.query_points(
            collection_name="atlas333_eureka", query=embedding.tolist(), limit=top_k
        )

        paradoxes = []
        for r in results.points:
            paradoxes.append(
                {
                    "paradox_id": r.payload.get("paradox_id", "?"),
                    "title": r.payload.get("title", "?"),
                    "cluster": r.payload.get("cluster", "?"),
                    "poles": r.payload.get("poles", "?"),
                    "description": r.payload.get("description", "?"),
                    "quote": r.payload.get("quote", "?"),
                    "score": round(r.score, 4),
                }
            )
        return paradoxes
    except Exception as e:
        return [{"error": str(e), "note": "Qdrant search failed"}]


def trace_graph(paradox_ids: list) -> dict:
    """Query FalkorDB for relationships between paradoxes.

    Returns:
      direct_edges: edges between any pair of the returned paradoxes
      resolution_paths: RESOLVES_IN chains showing synthesis pathways
      cluster_map: which clusters the paradoxes belong to
      topology_note: human-readable summary of the tension network
    """
    try:
        import redis

        client = redis.Redis(host="localhost", port=6380, decode_responses=True)
        graph_name = "atlas333_graph"

        # Build IN clause for Cypher
        id_list = ", ".join(f"'{pid}'" for pid in paradox_ids)

        # Direct edges between any pair of returned paradoxes
        edge_query = f"""
        MATCH (a:Paradox)-[r]->(b:Paradox)
        WHERE a.id IN [{id_list}] AND b.id IN [{id_list}]
        RETURN a.id, a.title, type(r), b.id, b.title, r.note
        """
        result = client.execute_command("GRAPH.QUERY", graph_name, edge_query)
        direct_edges = []
        if len(result) > 1:
            for row in result[1]:
                direct_edges.append(
                    {
                        "source": row[0],
                        "source_title": row[1],
                        "relation": row[2],
                        "target": row[3],
                        "target_title": row[4],
                        "note": row[5][:120] if row[5] else "",
                    }
                )

        # Resolution pathways: RESOLVES_IN edges from any returned paradox
        resolve_query = f"""
        MATCH (a:Paradox)-[r:RESOLVES_IN]->(b:Paradox)
        WHERE a.id IN [{id_list}]
        RETURN a.id, a.title, b.id, b.title, r.note
        """
        result = client.execute_command("GRAPH.QUERY", graph_name, resolve_query)
        resolution_paths = []
        if len(result) > 1:
            for row in result[1]:
                resolution_paths.append(
                    {
                        "source": row[0],
                        "source_title": row[1],
                        "target": row[2],
                        "target_title": row[3],
                        "note": row[4][:120] if row[4] else "",
                    }
                )

        # Cluster membership
        cluster_query = f"""
        MATCH (p:Paradox)
        WHERE p.id IN [{id_list}]
        RETURN p.id, p.cluster
        """
        result = client.execute_command("GRAPH.QUERY", graph_name, cluster_query)
        clusters = {}
        if len(result) > 1:
            for row in result[1]:
                c = row[1]
                clusters[c] = clusters.get(c, 0) + 1

        # Build topology note
        topology_note = ""
        if direct_edges:
            topology_note = "## Tension Topology\n\n"
            topology_note += (
                "These paradoxes are not independent — they form a tension network:\n\n"
            )
            for e in direct_edges:
                symbol = {
                    "OPPOSES": "↔",
                    "COMPLICATES": "→⚡",
                    "PRECEDES": "→",
                    "RESOLVES_IN": "→✓",
                }.get(e["relation"], "→")
                topology_note += (
                    f"- **{e['source_title']}** {symbol} **{e['target_title']}** "
                    f"[{e['relation']}]\n"
                    f"  {e['note']}\n"
                )
            if resolution_paths:
                topology_note += "\n**Resolution pathways:**\n"
                for rp in resolution_paths:
                    topology_note += f"- {rp['source_title']} resolves in {rp['target_title']}\n"

        # Cluster distribution
        if len(clusters) > 1:
            topology_note += f"\n**Cluster distribution:** {', '.join(f'{k}({v})' for k, v in sorted(clusters.items()))}\n"
            topology_note += "Tension spans multiple clusters — cross-domain reasoning required.\n"

        return {
            "direct_edges": direct_edges,
            "resolution_paths": resolution_paths,
            "clusters": clusters,
            "topology_note": topology_note,
            "edge_count": len(direct_edges),
            "resolution_count": len(resolution_paths),
        }

    except Exception as e:
        return {
            "error": str(e),
            "note": "FalkorDB graph query failed — using Qdrant proximity only",
            "direct_edges": [],
            "resolution_paths": [],
            "topology_note": "",
        }


def activate(text: str, top_k: int = 5, use_graph: bool = True) -> dict:
    """Full LΘΦ activation pipeline

    Wiring (2026-08-09): MAP·ATLAS·ECHO institutional metrics calibrate
    density (MAP→top_k) and live tension weights (ECHO→axis heat).
    Paradox *content* is never rewritten — compression artifact stays stable.
    """

    # ── Institutional metrics bridge (wiring layer only) ──────────────
    metrics = None
    map_cal = {"top_k": top_k, "rule": "metrics_unavailable", "delta": 0}
    try:
        from arifosmcp.geometry.metrics_bridge import (
            apply_tension_to_paradoxes,
            load_institutional_metrics,
            map_calibrate_top_k,
        )

        metrics = load_institutional_metrics(recompute=False)
        map_cal = map_calibrate_top_k(base_k=top_k, metrics=metrics)
        top_k = int(map_cal.get("top_k") or top_k)
    except Exception as _mb_exc:  # noqa: BLE001
        apply_tension_to_paradoxes = None  # type: ignore
        metrics = {"_error": str(_mb_exc), "_epistemic": "UNMEASURED"}

    lane_result = L_lane_classify(text)
    lane = lane_result["lane"]

    tensor = Theta_demand_tensor(lane)

    gpv = {
        "lane": lane,
        "tau": tensor["tau"],
        "kappa": tensor["kappa"],
        "rho": tensor["rho"],
        "query_type": "agent_intent",
        "lane_confidence": lane_result["confidence"],
    }

    paradoxes = search_qdrant(text, top_k=top_k)

    # ECHO → live tension re-rank (P2 heats when memory visibility poor)
    if apply_tension_to_paradoxes is not None and paradoxes:
        paradoxes = apply_tension_to_paradoxes(paradoxes, metrics)

    # Graph layer: trace relationships between paradoxes
    graph = {}
    if use_graph and paradoxes and "error" not in paradoxes[0]:
        paradox_ids = [p["paradox_id"] for p in paradoxes]
        graph = trace_graph(paradox_ids)

    context_injection = ""
    if paradoxes and "error" not in paradoxes[0]:
        context_injection = "## ATLAS333 — Active Paradoxes\n\n"
        context_injection += "Navigate BETWEEN these poles, don't pick one:\n\n"
        for p in paradoxes:
            tw = p.get("tension_weight")
            live = " ⚡live" if p.get("tension_live") else ""
            tw_s = f" tension×{tw}" if tw is not None else ""
            context_injection += (
                f"- **{p['paradox_id']} {p['title']}** [{p['cluster']}]{live}{tw_s}\n"
                f"  Poles: {p['poles']}\n"
                f"  {p['description']}\n"
                f'  *"{p["quote"]}"*\n\n'
            )
        # Append graph topology if available
        if graph.get("topology_note"):
            context_injection += graph["topology_note"]
        # MAP/ECHO calibration note (wiring, not content)
        if map_cal.get("rule"):
            context_injection += (
                f"\n_Calibration:_ MAP→{map_cal.get('rule')} "
                f"(top_k={top_k}). ECHO heats axes; paradox text immutable.\n"
            )

    result = {
        "query": text[:200],
        "lane": lane,
        "tensor": tensor,
        "gpv": gpv,
        "active_paradoxes": paradoxes,
        "graph": graph,
        "context_injection": context_injection,
        "instruction": "Think IN the tension between these poles. Navigate.",
        "institutional_metrics": {
            "MAP": (metrics or {}).get("MAP"),
            "ATLAS": (metrics or {}).get("ATLAS"),
            "ECHO": (metrics or {}).get("ECHO"),
            "HERMES": (metrics or {}).get("HERMES"),
            "epistemic": (metrics or {}).get("_epistemic"),
        },
        "calibration": {
            "map_to_top_k": map_cal,
            "note": "Wiring layer only — 35 paradox definitions unchanged",
        },
    }

    if graph.get("edge_count", 0) > 0:
        result["instruction"] = (
            "These paradoxes form a tension network. "
            "Navigate the RELATIONSHIPS between them, not just the poles. "
            "The graph shows how they interact — use that structure."
        )

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ATLAS333 LΘΦ Activation Pipeline")
    parser.add_argument("query", nargs="?", help="Query text")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--format", choices=["json", "text"], default="text")
    parser.add_argument("--inject-only", action="store_true")
    parser.add_argument(
        "--graph",
        action="store_true",
        default=True,
        help="Enable FalkorDB graph tracing (default: on)",
    )
    parser.add_argument("--no-graph", action="store_true", help="Disable FalkorDB graph tracing")
    args = parser.parse_args()

    if not args.query:
        if not sys.stdin.isatty():
            args.query = sys.stdin.read().strip()
        else:
            print("Usage: atlas333_activate.py 'your query text'")
            sys.exit(1)

    use_graph = args.graph and not args.no_graph
    result = activate(args.query, top_k=args.top_k, use_graph=use_graph)

    if args.inject_only:
        print(result["context_injection"])
    elif args.format == "json":
        output = {k: v for k, v in result.items() if k != "context_injection"}
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(
            f"LANE: {result['lane']} | "
            f"τ={result['tensor']['tau']:.2f} "
            f"κ={result['tensor']['kappa']:.2f} "
            f"ρ={result['tensor']['rho']:.2f}"
        )
        print(f"\n{result['context_injection']}")
        print(f"---\n{result['instruction']}")
