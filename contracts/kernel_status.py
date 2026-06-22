"""
contracts/kernel_status.py — arif_kernel_status Engine (v0.2.0)
═══════════════════════════════════════════════════════════════

Implements all 9 declared modes:
  - discover              — contract family, counts, stages, channels, taxonomies
  - list_capabilities     — normalized tool list with governance metadata
  - show_contract         — full contract + derived audit/denial for one tool
  - find_orphans          — three-way drift: YAML ↔ generated graph ↔ runtime registry
  - show_audit_map        — audit event → tool mapping (who emits what)
  - find_contract_drift   — field-level drift between SSOT and generated graph
  - explain_denial        — human-readable denial code explanation
  - show_channel_matrix   — channel policy enforcement matrix
  - show_floor_coverage   — constitutional floor coverage analysis

Stable response envelope:
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
    "show_audit_map", "find_contract_drift", "explain_denial",
    "show_channel_matrix", "show_floor_coverage",
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
# Mode: show_audit_map
# ════════════════════════════════════════════════════════════════════════════════

def mode_show_audit_map(args: dict) -> dict:
    """Return audit event → tool mapping (who emits what)."""
    graph = _load_graph()
    ssot = _load_ssot()

    # Build event → tools mapping
    event_to_tools: dict[str, list[str]] = {}
    for node in graph["nodes"]:
        for event in node.get("audit_events", []):
            event_to_tools.setdefault(event, []).append(node["tool_name"])

    # Build tool → events mapping
    tool_to_events: dict[str, list[str]] = {}
    for node in graph["nodes"]:
        tool_to_events[node["tool_name"]] = sorted(node.get("audit_events", []))

    # Get SSOT audit events for comparison
    ssot_events = {e["event"] for e in ssot.get("audit_events", [])}
    graph_events = set(event_to_tools.keys())

    items = [
        {
            "event": event,
            "tools": sorted(tools),
            "tool_count": len(tools),
        }
        for event, tools in sorted(event_to_tools.items())
    ]

    warnings = []
    orphan_events = ssot_events - graph_events
    if orphan_events:
        warnings.append(f"SSOT defines {len(orphan_events)} events not used by any tool: {sorted(orphan_events)}")

    return _envelope(
        "show_audit_map",
        counts={
            "total_events": len(event_to_tools),
            "total_tools_with_events": len(tool_to_events),
            "ssot_events": len(ssot_events),
            "graph_events": len(graph_events),
            "orphan_events": len(orphan_events),
        },
        items=items,
        warnings=warnings,
        audit_map=event_to_tools,
        tool_map=tool_to_events,
    )


# ════════════════════════════════════════════════════════════════════════════════
# Mode: find_contract_drift
# ════════════════════════════════════════════════════════════════════════════════

def mode_find_contract_drift(args: dict) -> dict:
    """Field-level drift detection between SSOT and generated graph.

    Compares each tool's fields in tools.yaml against the generated
    capability_graph.json. Reports mismatches, missing fields, and
    value differences.
    """
    ssot = _load_ssot()
    graph = _load_graph()

    # Build SSOT tool lookup
    ssot_tools: dict[str, dict] = {}
    for section in ("canonical_tools", "diagnostic", "federated_organs", "sanctioned_non_arif"):
        for t in ssot.get(section, []):
            ssot_tools[t["canonical_name"]] = t

    # Build graph tool lookup
    graph_tools: dict[str, dict] = {
        n["tool_name"]: n for n in graph["nodes"]
    }

    drift_items = []
    warnings = []

    # Check tools in SSOT but not in graph
    ssot_only = sorted(set(ssot_tools.keys()) - set(graph_tools.keys()))
    if ssot_only:
        warnings.append(f"{len(ssot_only)} tools in SSOT but not in graph")
        for tool in ssot_only:
            drift_items.append({
                "tool": tool,
                "drift_type": "ssot_only",
                "detail": "Tool defined in SSOT but missing from generated graph",
            })

    # Check tools in graph but not in SSOT
    graph_only = sorted(set(graph_tools.keys()) - set(ssot_tools.keys()))
    if graph_only:
        warnings.append(f"{len(graph_only)} tools in graph but not in SSOT")
        for tool in graph_only:
            drift_items.append({
                "tool": tool,
                "drift_type": "graph_only",
                "detail": "Tool in generated graph but not defined in SSOT",
            })

    # Field-level comparison for tools in both
    comparable_fields = [
        "axis", "pipeline_stage", "channel", "reversibility",
        "blast_radius", "authority_required", "irreversible",
    ]

    for tool_name in sorted(set(ssot_tools.keys()) & set(graph_tools.keys())):
        ssot_t = ssot_tools[tool_name]
        graph_t = graph_tools[tool_name]

        for field in comparable_fields:
            ssot_val = ssot_t.get(field)
            graph_val = graph_t.get(field)
            if ssot_val is not None and graph_val is not None:
                # Normalize for comparison
                ssot_norm = str(ssot_val).lower()
                graph_norm = str(graph_val).lower()
                if ssot_norm != graph_norm:
                    drift_items.append({
                        "tool": tool_name,
                        "drift_type": "field_mismatch",
                        "field": field,
                        "ssot_value": ssot_val,
                        "graph_value": graph_val,
                    })

        # Check modes
        ssot_modes = set(ssot_t.get("modes", []))
        graph_modes = set(graph_t.get("modes", []))
        if ssot_modes and graph_modes and ssot_modes != graph_modes:
            drift_items.append({
                "tool": tool_name,
                "drift_type": "modes_mismatch",
                "ssot_modes": sorted(ssot_modes),
                "graph_modes": sorted(graph_modes),
            })

    return _envelope(
        "find_contract_drift",
        counts={
            "ssot_tools": len(ssot_tools),
            "graph_tools": len(graph_tools),
            "ssot_only": len(ssot_only),
            "graph_only": len(graph_only),
            "field_drifts": len([d for d in drift_items if d["drift_type"] == "field_mismatch"]),
            "mode_drifts": len([d for d in drift_items if d["drift_type"] == "modes_mismatch"]),
            "total_drifts": len(drift_items),
        },
        items=drift_items,
        warnings=warnings,
    )


# ════════════════════════════════════════════════════════════════════════════════
# Mode: explain_denial
# ════════════════════════════════════════════════════════════════════════════════

def mode_explain_denial(args: dict) -> dict:
    """Return human-readable explanation of a denial code.

    Args:
        args.code: The denial code to explain (e.g., PLAN_MISSING)
    """
    code = args.get("code")
    if not code:
        return _envelope("explain_denial", ok=False,
                         denials=["missing required arg: code"])

    ssot = _load_ssot()
    graph = _load_graph()

    # Find in SSOT denial codes
    ssot_denial = None
    for d in ssot.get("denial_codes", []):
        if d["code"] == code:
            ssot_denial = d
            break

    # Find in graph denial codes
    graph_denial = None
    for d in graph.get("denial_codes", []):
        if d["code"] == code:
            graph_denial = d
            break

    if not ssot_denial and not graph_denial:
        return _envelope(
            "explain_denial", ok=False,
            denials=[f"denial code '{code}' not found in SSOT or generated graph"],
        )

    # Use SSOT as primary source, graph as fallback
    denial = ssot_denial or graph_denial

    # Find tools that reference this denial code
    referencing_tools = [
        n["tool_name"] for n in graph["nodes"]
        if code in n.get("denial_codes", [])
    ]

    items = [{
        "code": code,
        "floor": denial.get("floor", "unknown"),
        "severity": denial.get("severity", "unknown"),
        "retryability": denial.get("retryability", "unknown"),
        "description": denial.get("description", ""),
        "remediation": denial.get("remediation", ""),
        "referencing_tools": sorted(referencing_tools),
        "referencing_tool_count": len(referencing_tools),
    }]

    warnings = []
    if ssot_denial and graph_denial:
        # Check for drift between SSOT and graph
        for field in ("floor", "severity", "retryability", "description", "remediation"):
            if ssot_denial.get(field) != graph_denial.get(field):
                warnings.append(f"Drift detected in {field}: SSOT={ssot_denial.get(field)}, graph={graph_denial.get(field)}")

    return _envelope(
        "explain_denial",
        counts={"referencing_tools": len(referencing_tools)},
        items=items,
        warnings=warnings,
    )


# ════════════════════════════════════════════════════════════════════════════════
# Mode: show_channel_matrix
# ════════════════════════════════════════════════════════════════════════════════

def mode_show_channel_matrix(args: dict) -> dict:
    """Return channel policy enforcement matrix.

    Shows which tools are in which channel, and the policy constraints
    for each channel (plan requirements, blast radius caps, authority).
    """
    graph = _load_graph()
    ssot = _load_ssot()

    # Channel policies from SSOT taxonomies
    channel_policies = {
        "stable": {
            "plan_required": "risk-based",
            "max_blast_radius": "medium",
            "floor_relaxation": "never",
            "external_effects": "allowed",
        },
        "beta": {
            "plan_required": "always",
            "max_blast_radius": "civilizational",
            "floor_relaxation": "never",
            "external_effects": "allowed_with_sovereign_ack",
        },
        "sandbox": {
            "plan_required": "always",
            "max_blast_radius": "low",
            "floor_relaxation": "never",
            "external_effects": "blocked",
        },
    }

    # Build channel → tools mapping
    channel_tools: dict[str, list[dict]] = {}
    for node in graph["nodes"]:
        channel = node.get("channel", "unknown")
        channel_tools.setdefault(channel, []).append({
            "tool_name": node["tool_name"],
            "authority_required": node.get("authority_required", "unknown"),
            "blast_radius": node.get("blast_radius", "unknown"),
            "irreversible": node.get("irreversible", False),
            "requires_plan": node.get("requires_plan", False),
        })

    items = []
    for channel in sorted(channel_tools.keys()):
        tools = channel_tools[channel]
        policy = channel_policies.get(channel, {})
        items.append({
            "channel": channel,
            "policy": policy,
            "tool_count": len(tools),
            "tools": sorted(tools, key=lambda t: t["tool_name"]),
        })

    # Validation warnings
    warnings = []
    for node in graph["nodes"]:
        channel = node.get("channel", "unknown")
        if channel == "beta":
            if node.get("authority_required") != "sovereign" and not node.get("hold_conditions"):
                warnings.append(f"Beta tool '{node['tool_name']}' lacks sovereign authority or hold_conditions")
        if channel == "sandbox":
            if node.get("irreversible"):
                warnings.append(f"Sandbox tool '{node['tool_name']}' is irreversible (violates sandbox policy)")

    return _envelope(
        "show_channel_matrix",
        counts={
            "total_channels": len(channel_tools),
            "stable_tools": len(channel_tools.get("stable", [])),
            "beta_tools": len(channel_tools.get("beta", [])),
            "sandbox_tools": len(channel_tools.get("sandbox", [])),
        },
        items=items,
        warnings=warnings,
    )


# ════════════════════════════════════════════════════════════════════════════════
# Mode: show_floor_coverage
# ════════════════════════════════════════════════════════════════════════════════

def mode_show_floor_coverage(args: dict) -> dict:
    """Return constitutional floor coverage analysis.

    Shows which floors are referenced by which tools' denial codes,
    and identifies floors with no tool coverage.
    """
    graph = _load_graph()
    ssot = _load_ssot()

    # Build floor → tools mapping from denial codes
    floor_tools: dict[str, list[str]] = {}
    floor_denial_codes: dict[str, list[str]] = {}

    # Get floor mappings from SSOT denial codes
    code_to_floor: dict[str, str] = {}
    for d in ssot.get("denial_codes", []):
        code_to_floor[d["code"]] = d.get("floor", "unknown")

    # Also from graph denial codes
    for d in graph.get("denial_codes", []):
        if d["code"] not in code_to_floor:
            code_to_floor[d["code"]] = d.get("floor", "unknown")

    # Map tools to floors via their denial codes
    for node in graph["nodes"]:
        tool_name = node["tool_name"]
        for code in node.get("denial_codes", []):
            floor = code_to_floor.get(code, "unknown")
            floor_tools.setdefault(floor, []).append(tool_name)
            floor_denial_codes.setdefault(floor, []).append(code)

    # Deduplicate
    for floor in floor_tools:
        floor_tools[floor] = sorted(set(floor_tools[floor]))
        floor_denial_codes[floor] = sorted(set(floor_denial_codes[floor]))

    # All constitutional floors
    all_floors = {f"F{i}" for i in range(1, 14)}
    covered_floors = set(floor_tools.keys()) - {"unknown"}
    uncovered_floors = sorted(all_floors - covered_floors)

    items = []
    for floor in sorted(floor_tools.keys()):
        items.append({
            "floor": floor,
            "tool_count": len(floor_tools[floor]),
            "tools": floor_tools[floor],
            "denial_codes": floor_denial_codes[floor],
            "denial_code_count": len(floor_denial_codes[floor]),
        })

    warnings = []
    if uncovered_floors:
        warnings.append(f"{len(uncovered_floors)} floors have no tool coverage: {uncovered_floors}")

    return _envelope(
        "show_floor_coverage",
        counts={
            "total_floors": len(all_floors),
            "covered_floors": len(covered_floors),
            "uncovered_floors": len(uncovered_floors),
            "total_tools_with_floor_refs": len(set().union(*floor_tools.values())) if floor_tools else 0,
        },
        items=items,
        warnings=warnings,
        uncovered_floors=uncovered_floors,
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
        "show_audit_map": mode_show_audit_map,
        "find_contract_drift": mode_find_contract_drift,
        "explain_denial": mode_explain_denial,
        "show_channel_matrix": mode_show_channel_matrix,
        "show_floor_coverage": mode_show_floor_coverage,
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
