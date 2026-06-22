"""
contracts/kernel_status.py — arif_kernel_status Engine (v0.1.0)
═══════════════════════════════════════════════════════════════

Implements 4 of the 9 declared modes (per sovereign directive):
  - discover
  - list_capabilities
  - show_contract
  - find_orphans

The other 5 modes (show_audit_map, find_contract_drift, explain_denial,
show_channel_matrix, show_floor_coverage) are stubs that return
"not yet implemented" — they slot into the same response envelope
without breaking callers.

Stable response envelope (so later 5 modes slot in without churn):
  {
    "mode": str,
    "ok": bool,
    "generated_from_contract_version": str,
    "counts": dict,
    "items": list,
    "orphans": list,
    "warnings": list,
    "denials": list
  }

DITEMPA BUKAN DIBERI — Kernel can prove what it is.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("PyYAML required", file=sys.stderr)
    sys.exit(1)

CONTRACTS_DIR = Path(__file__).parent
PROJECT_ROOT = CONTRACTS_DIR.parent
SSOT_PATH = CONTRACTS_DIR / "tools.yaml"
GENERATED_DIR = CONTRACTS_DIR / "generated"
GRAPH_PATH = GENERATED_DIR / "capability_graph.json"
FIXTURES_PATH = GENERATED_DIR / "conformance_fixtures.json"
AUDIT_SCHEMAS_PATH = GENERATED_DIR / "audit_schemas.json"

DECLARED_MODES = {
    "discover", "list_capabilities", "show_contract", "show_audit_map",
    "find_orphans", "find_contract_drift", "explain_denial",
    "show_channel_matrix", "show_floor_coverage",
}
IMPLEMENTED_MODES = {
    "discover", "list_capabilities", "show_contract", "find_orphans",
}


# ════════════════════════════════════════════════════════════════════════════════
# Loaders
# ════════════════════════════════════════════════════════════════════════════════

def _load_graph() -> dict:
    if not GRAPH_PATH.exists():
        sys.exit(f"Graph not found: {GRAPH_PATH} — run compiler first")
    return json.loads(GRAPH_PATH.read_text())


def _load_ssot() -> dict:
    if not SSOT_PATH.exists():
        sys.exit(f"SSOT not found: {SSOT_PATH}")
    return yaml.safe_load(SSOT_PATH.read_text())


def _envelope(mode: str, **kwargs) -> dict:
    """Stable response envelope. All modes return this shape."""
    graph = _load_graph()
    return {
        "mode": mode,
        "ok": True,
        "generated_from_contract_version": graph.get("contract_version", "unknown"),
        "counts": {},
        "items": [],
        "orphans": [],
        "warnings": [],
        "denials": [],
        **kwargs,
    }


# ════════════════════════════════════════════════════════════════════════════════
# Mode: discover
# ════════════════════════════════════════════════════════════════════════════════

def mode_discover(args: dict) -> dict:
    """Return contract family version, counts, stages, channels, taxonomies."""
    graph = _load_graph()
    ssot = _load_ssot()
    nodes = graph["nodes"]
    counts = {
        "total_tools": len(nodes),
        "by_section": dict(Counter(n["section"] for n in nodes)),
        "by_channel": dict(Counter(n["channel"] for n in nodes)),
        "by_contract_class": dict(Counter(n["contract_class"] for n in nodes)),
        "by_mutation_class": dict(Counter(n["mutation_class"] for n in nodes)),
        "by_authority_required": dict(Counter(n["authority_required"] for n in nodes)),
        "by_pipeline_stage": dict(Counter(n["pipeline_stage"] for n in nodes)),
        "by_axis": dict(Counter(n["axis"] for n in nodes)),
        "denial_codes": len(graph.get("denial_codes", [])),
        "audit_events": len(graph.get("audit_events", [])),
        "legacy_aliases": len(graph.get("alias_map", {})),
    }
    return _envelope(
        "discover",
        counts=counts,
        contract_family=graph.get("contract_family"),
        contract_version=graph.get("contract_version"),
        generated_at=graph.get("generated_at"),
        taxonomies=ssot.get("taxonomies", {}),
    )


# ════════════════════════════════════════════════════════════════════════════════
# Mode: list_capabilities
# ════════════════════════════════════════════════════════════════════════════════

def mode_list_capabilities(args: dict) -> dict:
    """Return normalized list of tools with stage, axis, modes, channel, authority, reversibility."""
    graph = _load_graph()
    items = [
        {
            "tool_name": n["tool_name"],
            "section": n["section"],
            "axis": n["axis"],
            "pipeline_stage": n["pipeline_stage"],
            "contract_class": n["contract_class"],
            "modes": n["modes"],
            "channel": n["channel"],
            "authority_required": n["authority_required"],
            "reversibility": ("irreversible" if n["irreversible"] else "reversible"),
            "blast_radius": n["blast_radius"],
            "mutation_class": n["mutation_class"],
            "fingerprint": n["fingerprint"],
            "legacy_aliases": n.get("legacy_aliases", []),
        }
        for n in graph["nodes"]
    ]
    return _envelope(
        "list_capabilities",
        counts={"total": len(items)},
        items=items,
    )


# ════════════════════════════════════════════════════════════════════════════════
# Mode: show_contract
# ════════════════════════════════════════════════════════════════════════════════

def mode_show_contract(args: dict) -> dict:
    """Return the full contract object plus derived audit and denial metadata."""
    tool_name = args.get("tool_name")
    if not tool_name:
        return _envelope("show_contract", ok=False,
                         denials=["missing required arg: tool_name"])

    graph = _load_graph()
    # Resolve via alias map
    alias_map = graph.get("alias_map", {})
    resolved = alias_map.get(tool_name, tool_name)
    node = next((n for n in graph["nodes"] if n["tool_name"] == resolved), None)
    if not node:
        return _envelope(
            "show_contract", ok=False,
            denials=[f"tool '{tool_name}' not in capability graph (resolved: {resolved})"],
            orphans=[{"queried": tool_name, "resolved_to": resolved}],
        )

    # Find denial codes referenced by this tool
    tool_denial_codes = [
        d for d in graph.get("denial_codes", [])
        if d["code"] in node.get("denial_codes", [])
    ]
    # Find audit events referenced by this tool
    referenced_events = node.get("audit_events", [])

    return _envelope(
        "show_contract",
        counts={"denial_codes": len(tool_denial_codes),
                "audit_events": len(referenced_events)},
        items=[{
            "tool_name": node["tool_name"],
            "contract": node,
            "denial_codes": tool_denial_codes,
            "referenced_audit_events": referenced_events,
            "deprecated_aliases": [
                alias for alias, canon in graph.get("alias_map", {}).items()
                if canon == resolved
            ],
        }],
    )


# ════════════════════════════════════════════════════════════════════════════════
# Mode: find_orphans
# ════════════════════════════════════════════════════════════════════════════════

def mode_find_orphans(args: dict) -> dict:
    """Compare SSOT, generated graph, and (optionally) live MCP registry.

    Three-way drift detection:
      - ssot_only:        in SSOT but not in generated graph (compiler bug)
      - graph_only:       in generated graph but not in SSOT (graph bug)
      - live_only:        in live MCP registry but not in SSOT (MCP drift)

    Legacy aliases (arifos_*, arif_bridge_connect, etc.) are included in
    the SSOT name set so legacy live tools are not flagged as orphans
    when they have an alias_of mapping.
    """
    ssot = _load_ssot()
    graph = _load_graph()

    def _all_ssot_names(doc):
        names = set()
        for sec in ("canonical_tools", "diagnostic", "federated_organs", "sanctioned_non_arif"):
            for t in doc.get(sec, []):
                names.add(t["canonical_name"])
        # Also include legacy aliases so old runtime names are recognized
        for la in doc.get("legacy_aliases", []):
            names.add(la.get("alias"))
        return names

    ssot_names = _all_ssot_names(ssot)
    graph_names = {n["tool_name"] for n in graph["nodes"]}
    # Also include legacy aliases from graph nodes
    for n in graph["nodes"]:
        graph_names.update(n.get("legacy_aliases", []))

    # Optional: live MCP registry — try to fetch from arifOS MCP
    live_names: set[str] = set()
    live_err: str | None = None
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:8088/mcp", timeout=2) as r:
            # Quick tools/list probe
            req = urllib.request.Request(
                "http://127.0.0.1:8088/mcp",
                data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}',
                headers={"Content-Type": "application/json", "Accept": "application/json,text/event-stream"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=3) as rr:
                body = rr.read().decode()
                # Strip SSE framing
                if body.startswith("event:"):
                    body = "\n".join(l[6:] for l in body.split("\n") if l.startswith("data:"))
                j = json.loads(body)
                for t in j.get("result", {}).get("tools", []):
                    live_names.add(t.get("name", ""))
    except Exception as e:
        live_err = str(e)

    orphans = {
        "ssot_only": sorted(ssot_names - graph_names),
        "graph_only": sorted(graph_names - ssot_names),
        "live_only": sorted(live_names - ssot_names) if live_names else [],
        "ssot_vs_live_only": sorted(ssot_names - live_names) if live_names else [],
    }

    warnings = []
    if live_err:
        warnings.append(f"live MCP registry unreachable: {live_err}")
    if orphans["ssot_only"]:
        warnings.append(f"SSOT has {len(orphans['ssot_only'])} tools missing from generated graph")
    if orphans["graph_only"]:
        warnings.append(f"Generated graph has {len(orphans['graph_only'])} tools not in SSOT")
    if orphans["live_only"]:
        warnings.append(f"Live MCP exposes {len(orphans['live_only'])} tools not in SSOT (MCP drift)")

    return _envelope(
        "find_orphans",
        counts={
            "ssot_count": len(ssot_names),
            "graph_count": len(graph_names),
            "live_mcp_count": len(live_names),
            "ssot_only": len(orphans["ssot_only"]),
            "graph_only": len(orphans["graph_only"]),
            "live_only": len(orphans["live_only"]),
        },
        orphans=list(orphans.values()),
        warnings=warnings,
    )


# ════════════════════════════════════════════════════════════════════════════════
# Stub modes (5 of 9 — interface ready, body lands in next cycle)
# ════════════════════════════════════════════════════════════════════════════════

STUB_MODES = ("show_audit_map", "find_contract_drift", "explain_denial",
              "show_channel_matrix", "show_floor_coverage")


def _mode_stub(mode: str, args: dict) -> dict:
    return _envelope(
        mode, ok=False,
        denials=[f"mode '{mode}' not yet implemented; stub returns empty envelope"],
        warnings=["stub mode — body lands in next CCR cycle"],
    )


# ════════════════════════════════════════════════════════════════════════════════
# Dispatch
# ════════════════════════════════════════════════════════════════════════════════

def kernel_status(args: dict) -> dict:
    """The arif_kernel_status entry point — dispatch by mode."""
    mode = args.get("mode")
    if not mode:
        return _envelope("unknown", ok=False,
                         denials=["missing required arg: mode"],
                         items=[{"implemented_modes": sorted(IMPLEMENTED_MODES),
                                 "declared_modes": sorted(DECLARED_MODES)}])
    if mode not in DECLARED_MODES:
        return _envelope(mode, ok=False,
                         denials=[f"mode '{mode}' not in declared modes",
                                  f"available: {sorted(DECLARED_MODES)}"])
    handlers = {
        "discover": mode_discover,
        "list_capabilities": mode_list_capabilities,
        "show_contract": mode_show_contract,
        "find_orphans": mode_find_orphans,
    }
    if mode in handlers:
        return handlers[mode](args)
    return _mode_stub(mode, args)


# ════════════════════════════════════════════════════════════════════════════════
# CLI
# ════════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    p = argparse.ArgumentParser(description="arif_kernel_status — 4 modes implemented")
    p.add_argument("mode", choices=sorted(IMPLEMENTED_MODES),
                   help="Kernel status mode to invoke")
    p.add_argument("--tool-name", help="For show_contract")
    p.add_argument("--json", action="store_true", help="Output raw JSON")
    args = p.parse_args()

    call_args = {"mode": args.mode}
    if args.tool_name:
        call_args["tool_name"] = args.tool_name

    out = kernel_status(call_args)
    if args.json:
        print(json.dumps(out, indent=2, sort_keys=False))
    else:
        mode = out["mode"]
        print(f"=== kernel_status(mode={mode}) ===")
        print(f"  ok: {out['ok']}")
        if out.get("counts"):
            print(f"  counts:")
            for k, v in out["counts"].items():
                print(f"    {k}: {v}")
        if out.get("items"):
            print(f"  items: {len(out['items'])} (use --json to see)")
        if out.get("orphans"):
            orphans = out["orphans"]
            if any(orphans):
                print(f"  orphans:")
                for i, o in enumerate(orphans):
                    if o:
                        print(f"    [{i}] {o[:5]}{'...' if len(o) > 5 else ''}")
        if out.get("warnings"):
            for w in out["warnings"]:
                print(f"  ⚠ {w}")
        if out.get("denials"):
            for d in out["denials"]:
                print(f"  ❌ {d}")


if __name__ == "__main__":
    main()
