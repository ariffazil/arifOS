"""
generate_tool_manifest.py — Auto-generate llms.txt from live tool registry.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import datetime
from typing import Any


def _canonical_tool_list() -> list[dict[str, Any]]:
    """Extract canonical tool data from constitutional_map."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    tools = []
    for name, spec in CANONICAL_TOOLS.items():
        tools.append(
            {
                "name": name,
                "stage": spec.get("stage", "unknown"),
                "lane": spec.get("lane", "AGI"),
                "access": spec.get("access", "public"),
                "description": spec.get("description", "").split(".")[0].strip(),
                "floors": [str(f) for f in spec.get("floors", [])],
                "modes": spec.get("modes", []),
                "irreversible": spec.get("irreversible", False),
            }
        )
    return tools


def _operational_tool_list() -> list[dict[str, Any]]:
    """Extract operational (diagnostic) tool data from constitutional_map."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from arifosmcp.constitutional_map import DIAGNOSTIC_TOOLS

    tools = []
    for name, spec in DIAGNOSTIC_TOOLS.items():
        tools.append(
            {
                "name": name,
                "tier": spec.get("tier", "unknown"),
                "namespace": spec.get("namespace", "").split("(")[0].strip(),
                "risk_tier": spec.get("risk_tier", "low"),
                "description": spec.get("description", "").split(".")[0].strip(),
                "modes": spec.get("modes", []),
                "irreversible": spec.get("irreversible", False),
            }
        )
    return tools


def _all_mcp_tools() -> list[dict[str, Any]]:
    """Combine canonical + operational for full MCP surface list."""
    return _canonical_tool_list() + _operational_tool_list()


def _canonical_resources_list() -> list[dict[str, Any]]:
    """Extract registered resources catalog."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from arifosmcp.resources.resources_index import _build_resource_catalog
        catalog = _build_resource_catalog()
        return catalog.get("resources", [])
    except Exception as e:
        # Fallback list if import fails
        fallback_uris = [
            "arifos://doctrine", "arifos://trinity", "arifos://schema",
            "arifos://civilization", "arifos://seal-readiness", "arifos://jurisdiction",
            "arifos://identity", "arifos://memory", "arifos://vitals",
            "arifos://bootstrap", "arifos://human/metabolized", "arifos://loop-engineering",
            "arifos://quickstart", "arifos://mcp-alignment", "arifos://mcp/surface-map"
        ]
        fallback_desc = {
            "arifos://doctrine": "Immutable 13-floor constitution (F1–F13). All tools and agents operate within these floors.",
            "arifos://trinity": "AAA Trinity lane architecture: AGI proposes, ASI/APEX judges/authorizes, FORGE executes, SEAL records.",
            "arifos://schema": "Complete canonical blueprint of the arifOS MCP surface — tools, lanes, floors.",
            "arifos://civilization": "Organs, strata, constitutional boundaries, and entropy responsibility models.",
            "arifos://seal-readiness": "Vault integrity, disambiguated seal types, and seal gates.",
            "arifos://jurisdiction": "Autonomy bands (GREEN to BLACK), CapabilityGrants, and rules.",
            "arifos://identity": "Sovereign identity manifest and root of accountability chains.",
            "arifos://memory": "6-layer memory architecture: ephemeral to immutable VAULT999.",
            "arifos://vitals": "Constitutional metrics and green/yellow/red thresholds.",
            "arifos://bootstrap": "Complete federation knowledge-graph context in a single call.",
            "arifos://human/metabolized": "Compact human intelligence/context (nutrient representation).",
            "arifos://loop-engineering": "7-stage reality engineering loop (K1 dual naming).",
            "arifos://quickstart": "LLM client onboarding and fast-start guide.",
            "arifos://mcp-alignment": "MCP specification conformance and client compatibility matrix.",
            "arifos://mcp/surface-map": "Map of owned tools and resources across organs."
        }
        return [
            {
                "uri": uri,
                "family": "canonical",
                "mime_type": "text/plain",
                "dynamic": False,
                "description": fallback_desc.get(uri, "arifOS core resource"),
                "floors": ["F2", "F4"]
            } for uri in fallback_uris
        ]


def manifest_hash() -> str:
    """SHA256 of the full manifest JSON for cross-reference."""
    manifest = {
        "canonical_tools": len(_canonical_tool_list()),
        "operational_tools": len(_operational_tool_list()),
        "tools_exposed_via_mcp": len(_all_mcp_tools()),
        "canonical_resources": len(_canonical_resources_list()),
    }
    raw = json.dumps(manifest, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def generate_llms_txt() -> str:
    """Generate llms.txt content from the live registry."""
    canonical = _canonical_tool_list()
    operational = _operational_tool_list()
    resources = _canonical_resources_list()
    total_tools = len(canonical) + len(operational)
    mhash = manifest_hash()

    lines: list[str] = []
    lines.append("# arifOS — Constitutional AI Governance Kernel")
    lines.append(f"> Auto-generated from live tool and resource registries. Hash: {mhash}")
    lines.append(
        f"> Total MCP: {total_tools} Tools | {len(resources)} Resources | Status: OPERATIONAL"
    )
    lines.append("> Port: 8088 | License: AGPL-3.0 | Status: OPERATIONAL")
    lines.append("")
    lines.append("## Docs")
    lines.append("- [AGENTS.md](file:///root/AGENTS.md): Main agent landing protocol and Output Contract (F13 absolute)")
    lines.append("- [CONTEXT.md](file:///root/CONTEXT.md): Tiered session-bound operational context")
    lines.append("- [MCP-RESOURCES-MAP.md](file:///root/AAA/docs/MCP-RESOURCES-MAP.md): Full federation cross-organ resource mapping")
    lines.append("- [INVARIANTS.md](file:///root/AAA/docs/INVARIANTS.md): 11 Physics + 7 Zen principles")
    lines.append("")
    lines.append("## MCP Tools — Complete Surface")
    lines.append(
        f"arifOS exposes {total_tools} MCP tools: {len(canonical)} canonical constitutional tools"
    )
    lines.append(f"and {len(operational)} operational support tools.")
    lines.append("")

    # Category breakdown
    tiers: dict[str, int] = {}
    for t in operational:
        tier = t["tier"]
        tiers[tier] = tiers.get(tier, 0) + 1

    lines.append("### Operational Categories")
    for tier, count in sorted(tiers.items()):
        lines.append(f"- {tier}: {count} tools")
    lines.append("")

    # Canonical tools
    lines.append(f"### Canonical Constitutional Tools ({len(canonical)})")
    lines.append("| Tool | Stage | Access | Reversible | Modes |")
    lines.append("|------|-------|--------|------------|-------|")
    for t in canonical:
        rev = chr(10003) if not t["irreversible"] else chr(10007) + " HOLD"
        modes = ", ".join(t["modes"][:6])
        if len(t["modes"]) > 6:
            modes += f" +{len(t['modes']) - 6} more"
        lines.append(f"| `{t['name']}` | {t['stage']} | {t['access']} | {rev} | {modes} |")
    lines.append("")

    # Operational tools
    lines.append("### Operational Support Tools ({})".format(len(operational)))
    lines.append("| Tool | Category | Risk | Mutates | Modes |")
    lines.append("|------|----------|------|---------|-------|")
    for t in operational:
        irr = chr(10007) + " HOLD" if t["irreversible"] else "no"
        modes = ", ".join(t["modes"][:4])
        if len(t["modes"]) > 4:
            modes += f" +{len(t['modes']) - 4} more"
        lines.append(f"| `{t['name']}` | {t['tier']} | {t['risk_tier']} | {irr} | {modes} |")
    lines.append("")

    # MCP Resources section
    lines.append("## MCP Resources — Canonical & Embodied")
    lines.append("Unlike Tools (which represent mutable side-effects), Resources represent addressable, read-only state and facts.")
    lines.append("All resources carry an explicit `truth_level` under the arifOS truth hierarchy:")
    lines.append("1. **SOVEREIGN_CANON** (immutable constitution/directs)")
    lines.append("2. **SEALED_VAULT** (append-only logs, signed judgments)")
    lines.append("3. **TRUSTED_REPO** (git SOT)")
    lines.append("4. **OBSERVED_EXTERNAL** (real-time environment/telemetry)")
    lines.append("5. **USER_CLAIM** (unverified human input)")
    lines.append("6. **MODEL_INFERENCE** (AI assertions)")
    lines.append("7. **UNTRUSTED** (unverified external context)")
    lines.append("")
    lines.append("### Registered arifOS MCP Resources")
    lines.append("| URI | Family | Linked Floors | Description |")
    lines.append("|-----|--------|---------------|-------------|")
    
    # Sort resources by family then URI
    sorted_resources = sorted(resources, key=lambda x: (x.get("family", ""), x.get("uri", "")))
    for r in sorted_resources:
        floors = ", ".join(r.get("floors", []))
        lines.append(f"| `{r['uri']}` | {r['family']} | {floors} | {r['description']} |")
    lines.append("")

    lines.append("## Federation Resources Map (Cross-Organ)")
    lines.append("To prevent chaos and duplicate context (F4 CLARITY), do not duplicate these namespaces. Route or read accordingly:")
    lines.append("")
    lines.append("### Control Plane & A2A State (AAA — L3)")
    lines.append("- `aaa://state/agent-registry` — Live registry of active agent cards")
    lines.append("- `aaa://state/a2a-cards` — Peer capability profiles (`agent-card-*.json`)")
    lines.append("- `aaa://state/zen-init` — Central AAA init template constraints")
    lines.append("- `aaa://state/cockpit` — Global session queues and orchestration panels")
    lines.append("")
    lines.append("### Governed Actuator (A-FORGE — L2)")
    lines.append("- `aforge://execution/leases/status` — Agent concurrency lease status")
    lines.append("- `aforge://execution/reality/loop` — Reality loop transaction snapshots")
    lines.append("- `aforge://execution/receipts/{id}` — Signed mutation receipts of executed commands")
    lines.append("")
    lines.append("### Earth Intelligence Substrate (GEOX — L1)")
    lines.append("- `geox://evidence/{well,seismic,prospect,claim}` — Underground geologic evidence assets")
    lines.append("- `geox://basins/index` — Structural/basin index files")
    lines.append("- `geox://claims/graph` — Geological claim networks and structural uncertainty data")
    lines.append("")
    lines.append("### Capital Intelligence Substrate (WEALTH — L1)")
    lines.append("- `wealth://capital/npv|emv|irr|risk|thresholds` — NPV, IRR, and EMV calculation variables")
    lines.append("- `wealth://collapse/signatures` — Failure forensics for entities or portfolios")
    lines.append("- `wealth://flows` — Personal, market, and macro capital flows")
    lines.append("")
    lines.append("### Vitality Substrate (WELL — L1)")
    lines.append("- `well://identity` — Five-well frame (Homeostasis, Metabolism, Governance, Coupling, Utility)")
    lines.append("- `well://metabolic/flux` — Human metabolic rate indicators (reflect-only)")
    lines.append("- `well://decision/classes` — Human vs machine decision metrics")
    lines.append("")

    # A2A Protocol section
    lines.append("## A2A Protocol — Peer-to-Peer Collaboration")
    lines.append("In addition to MCP (which handles direct client-server data and tool access), the arifOS federation utilizes the **Agent-to-Agent (A2A)** protocol for peer-to-peer collaboration, agreement, and task delegation.")
    lines.append("")
    lines.append("### 1. A2A Communication Fabric (The Protocol)")
    lines.append("- `message/send` — Submit a message/task to another agent. Enforces mandatory `session_id` to prevent Ghost Tasks.")
    lines.append("- `message/stream` — Stream real-time agent output using Server-Sent Events (SSE).")
    lines.append("- `tasks/get` — Retrieve status and history of a routed task.")
    lines.append("- `tasks/list` — List tasks, filterable by multi-tenancy `tenant`.")
    lines.append("- `tasks/cancel` — Abort a running task execution.")
    lines.append("- `tasks/subscribe` — Real-time event subscription for task state changes.")
    lines.append("")
    lines.append("### 2. A2A Transactional Layer (The Meaning-Exchange)")
    lines.append("- **Agent Cards** (`https://aaa.arif-fazil.com/.well-known/agent-card.json`) — Canonical A2A card owned by AAA (FEDERATION_CONTRACT §5.4.5). Declares agent capabilities, static/JWT auth schemes, and autonomy boundaries (`canDo`/`cannotDo`).")
    lines.append("- **Autonomy Tiers** — Strict boundary constraints defined per agent card:")
    lines.append("  - **T1 (Execution)** — Routine, local operations (no HOLD).")
    lines.append("  - **T2 (Negotiation)** — Refactoring/deployment tasks (announce, medium risk).")
    lines.append("  - **T3 (Architectural)** — Irreversible/constitutional adjustments (888_HOLD mandatory).")
    lines.append("- **Task States** — Wire state machine mapping:")
    lines.append("  - `TASK_STATE_INPUT_REQUIRED` — Maps internally to arifOS `HOLD_888` verdict.")
    lines.append("  - `TASK_STATE_REJECTED` — Maps internally to arifOS `VOID` verdict.")
    lines.append("")
    lines.append("### 3. Orchestration & Coordination")
    lines.append("- **Context Lineage** (`contextId` / `contextLineage`) — Tracks the parent arifOS `session_id` throughout the lifecycle of delegated messages/tasks to ensure end-to-end auditability and eliminate Ghost Tasks.")
    lines.append("")

    lines.append("## Constitutional Floors (F1-F13)")
    lines.append("F1 AMANAH . F2 TRUTH . F3 TRI-WITNESS . F4 CLARITY . F5 PEACE2")
    lines.append("F6 EMPATHY . F7 HUMILITY . F8 GENIUS . F9 ANTIHANTU . F10 ONTOLOGY")
    lines.append("F11 AUDITABILITY . F12 RESILIENCE . F13 SOVEREIGN (human veto FINAL)")
    lines.append("")
    lines.append("## Federation Organs - MCP Endpoints")
    lines.append("")
    lines.append("| Organ | MCP Endpoint | Role | Tools |")
    lines.append("|------|-------------|------|-------|")
    lines.append(
        f"| **arifOS** (8088) | `mcp.arif-fazil.com/mcp` | Governance kernel | {len(_canonical_tool_list())} canonical + {len(_operational_tool_list())} operational |"
    )
    lines.append(
        "| **A-FORGE** (7071) | `forge.arif-fazil.com/mcp` | Engineering actuator | 59 (filesystem, git, docker, postgres, vault, shell, job, lease, agent) |"
    )
    lines.append(
        "| **GEOX** (8081) | `geox.arif-fazil.com/mcp` | Earth intelligence | 33 canonical tools |"
    )
    lines.append(
        "| **WEALTH** (18082) | `wealth.arif-fazil.com/mcp` | Capital intelligence | 20+ tools |"
    )
    lines.append("| **WELL** (18083) | `well.arif-fazil.com/mcp` | Human readiness | 18+ tools |")
    lines.append(
        "| **AAA** (3001) | `aaa.arif-fazil.com` | Control plane cockpit | A2A server, React SPA |"
    )
    lines.append("")
    lines.append("## Agent Rules (mandatory)")
    lines.append("1. Never skip the 000-999 pipeline")
    lines.append("2. Never self-certify (F2 TRUTH)")
    lines.append("3. Never fabricate evidence (F9 ANTIHANTU)")
    lines.append("4. Never bypass human veto (F13 SOVEREIGN)")
    lines.append("5. Reversible-first: commit before big changes (F1 AMANAH)")
    lines.append("")
    lines.append("### Tool Location Rules")
    lines.append(
        "- arifOS (8088) = governance only (judge, seal, reason, critique, hermes, lease, attest)"
    )
    lines.append(
        "- A-FORGE (7071) = engineering only (forge_*, filesystem, git, docker, postgres, shell, job)"
    )
    lines.append("- forge_* on arifOS = DEPRECATED PROXY (calls forwarded to A-FORGE)")
    lines.append("- GEOX/WEALTH/WELL = domain evidence organs")
    lines.append("")
    lines.append("## Verification")
    lines.append(f"- tools/list count should match total ({total_tools})")
    lines.append("- canonical_tools + operational_tools == tools_exposed_via_mcp")
    lines.append(f"- Manifest hash: {mhash}")
    lines.append("- Manifest URL: https://arifos.arif-fazil.com/tools.json")
    lines.append("")
    lines.append(f"--- Auto-generated {datetime.datetime.now(datetime.timezone.utc).isoformat()} ---")

    return "\n".join(lines)


def main() -> None:
    """Generate llms.txt and output manifest JSON for CI."""
    txt = generate_llms_txt()
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    targets = [
        os.path.join(repo_root, "llms.txt"),
        os.path.join(repo_root, "static", "llms.txt"),
        os.path.join(repo_root, "arifosmcp", "static", "llms.txt"),
        os.path.join(repo_root, "arifosmcp", "sites", "llms.txt"),
        os.path.join(repo_root, "arifosmcp", "sites", "developer", "llms.txt"),
    ]
    for path in targets:
        with open(path, "w") as f:
            f.write(txt)
        print(f"[MANIFEST] Wrote {path} ({len(txt)} chars)")
    print(
        f"[MANIFEST] Canonical Tools: {len(_canonical_tool_list())} | Operational Tools: {len(_operational_tool_list())}"
    )
    print(f"[MANIFEST] Canonical Resources: {len(_canonical_resources_list())}")
    print(f"[MANIFEST] Total MCP tools: {len(_all_mcp_tools())}")
    print(f"[MANIFEST] Hash: {manifest_hash()}")


if __name__ == "__main__":
    main()
