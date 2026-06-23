"""Live EurekaMode GEOX LEM test — v4 with all state-machine fixes."""

import asyncio
import json
import sys
import time

sys.path.insert(0, "/root/arifOS")
from arifosmcp.runtime.explore import arif_explore


async def main():
    print("═══ EUREKA MODE — GEOX LEM (v4 all-fixes) ═══\n")

    t0 = time.monotonic()
    result = await arif_explore(
        goal="Discover architecture patterns for Large Earth Model (LEM)",
        mode="eureka",
        seed_question="Earth foundation models, multimodal geoscience, neural operators, sparse data strategies",
        max_depth=3,
        max_steps=10,
        time_budget_s=30,
        trace_id="geox-lem-v7",
    )
    elapsed = time.monotonic() - t0

    graph = result.get("exploration_graph", {})
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    findings = result.get("findings", [])
    gaps = result.get("gaps", [])
    metrics = result.get("metrics", {})
    verdict = result.get("verdict", {})

    print(f"Status: {result.get('status')} | {elapsed:.1f}s")
    print(f"Steps: {metrics.get('steps')} | Depth: {metrics.get('depth')}")
    print(
        f"Nodes: {len(nodes)} | Edges: {len(edges)} | Findings: {len(findings)} | Gaps: {len(gaps)}"
    )
    print(
        f"Coverage: {metrics.get('coverage', 0):.2f} | Confidence: {metrics.get('confidence', 0):.2f}"
    )
    print(
        f"Saturation: {verdict.get('saturation')} | NextMoves: {len(verdict.get('next_moves', []))}"
    )

    if findings:
        print("\n─── FINDINGS ───")
        for f in findings[:15]:
            conf = f.get("confidence", 0)
            bar = "▓" * int(conf * 10) + "░" * (10 - int(conf * 10))
            print(f"  [{bar}] {f.get('summary', '')[:200]}")
            for s in (f.get("sources") or [])[:2]:
                print(f"       ← {s[:120]}")

    if gaps:
        print("\n─── GAPS ───")
        for g in gaps[:8]:
            print(f"  - {g[:150]}")

    print("\n─── GRAPH NODES ───")
    for n in nodes[:15]:
        meta = n.get("meta", {})
        mode = n.get("mode", "?")
        novel = meta.get("novel_findings", "")
        target = meta.get("target_mode", "")
        sym = meta.get("symbol_count", "")
        label = n.get("label", "")[:100]
        extras = []
        if novel:
            extras.append(f"novel={novel}")
        if sym:
            extras.append(f"symbols={sym}")
        if target:
            extras.append(f"target={target}")
        if meta.get("cycle"):
            extras.append(f"cycle={meta['cycle']}")
        if meta.get("unresolved") is not None and not meta["unresolved"]:
            extras.append("RESOLVED")
        print(f"  [{mode}] {label}")
        if extras:
            print(f"       {' | '.join(extras)}")

    print("\n─── EDGES ───")
    rel_counts = {}
    for e in edges:
        rel = e.get("relation", "?")
        rel_counts[rel] = rel_counts.get(rel, 0) + 1
    for rel, count in sorted(rel_counts.items()):
        print(f"  [{rel}] ×{count}")

    print(f"\n═══ COMPLETE ({elapsed:.1f}s) ═══")
    return result


if __name__ == "__main__":
    result = asyncio.run(main())
    with open("/root/arifOS/last_eureka_result.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
