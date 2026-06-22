"""Live EurekaMode GEOX LEM test — v3 with DDG Lite + Prospector _search_step."""
import asyncio, json, sys, time
sys.path.insert(0, "/root/arifOS")
from arifosmcp.runtime.explore import arif_explore


async def main():
    print("═══ EUREKA MODE — GEOX LEM (v3 fixed) ═══\n")

    t0 = time.monotonic()
    result = await arif_explore(
        goal="Find real Eureka insights on building a Large Earth Model (LEM)",
        mode="eureka",
        seed_question=(
            "State of the art in Earth foundation models Khoj IBM Earth AI "
            "NASA Prithvi Stanford multimodal geoscience transformers "
            "physics-constrained neural operators sparse Earth data "
            "geological consistency losses open-source LEM projects scaling"
        ),
        max_depth=3,
        max_steps=6,
        time_budget_s=120,
        trace_id="geox-lem-eureka-003",
    )
    elapsed = time.monotonic() - t0

    # ── Summary ──
    graph = result.get("exploration_graph", {})
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    findings = result.get("findings", [])
    gaps = result.get("gaps", [])
    metrics = result.get("metrics", {})
    verdict = result.get("verdict", {})

    print(f"Status: {result.get('status')} | {elapsed:.1f}s")
    print(f"Nodes: {len(nodes)} | Edges: {len(edges)} | Findings: {len(findings)} | Gaps: {len(gaps)}")
    print(f"Coverage: {metrics.get('coverage',0):.2f} | Confidence: {metrics.get('confidence',0):.2f} | Steps: {metrics.get('steps')}")
    print(f"Saturation: {verdict.get('saturation')} | NextMoves: {len(verdict.get('next_moves',[]))}")

    print("\n─── NODES ───")
    for n in nodes:
        meta = n.get("meta", {})
        label = n.get("label", "")[:100]
        target = meta.get("target_mode", meta.get("type", ""))
        print(f"  [{n.get('mode','?')[0:12]}] {label}")
        if meta:
            extras = []
            if meta.get("novel_findings") is not None:
                extras.append(f"novel={meta['novel_findings']}")
            if meta.get("dry_cycles") is not None:
                extras.append(f"dry={meta['dry_cycles']}")
            if meta.get("cycle"):
                extras.append(f"cycle={meta['cycle']}")
            if meta.get("symbol_count"):
                extras.append(f"symbols={meta['symbol_count']}")
            if extras:
                print(f"       {' | '.join(extras)}")

    print("\n─── EDGES ───")
    for e in edges:
        rel = e.get("relation", "?")
        marker = "⭐" if rel == "corroborates" else ("→" if rel == "resolves" else "·")
        print(f"  {marker} [{rel}] conf={e.get('confidence',1):.2f}")

    print("\n─── FINDINGS ───")
    for f in findings:
        summary = f.get("summary", "")[:200]
        conf = f.get("confidence", 0)
        bar = "▓" * int(conf * 10) + "░" * (10 - int(conf * 10))
        print(f"  [{bar}] {summary}")
        for s in (f.get("sources") or [])[:2]:
            print(f"       ← {s[:120]}")

    print("\n─── GAPS ───")
    for g in gaps[:8]:
        print(f"  - {g[:150]}")

    print(f"\n═══ COMPLETE ({elapsed:.1f}s) ═══")
    return result


if __name__ == "__main__":
    result = asyncio.run(main())
    with open("/root/arifOS/last_eureka_result.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
