"""
generate_tool_manifest.py — Auto-generate llms.txt from live tool registry.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Any


def _canonical_tool_list() -> list[dict[str, Any]]:
    """Extract canonical tool data from constitutional_map."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    tools = []
    for name, spec in CANONICAL_TOOLS.items():
        tools.append({
            "name": name,
            "stage": spec.get("stage", "unknown"),
            "lane": spec.get("lane", "AGI"),
            "access": spec.get("access", "public"),
            "description": spec.get("description", "").split(".")[0].strip(),
            "floors": [str(f) for f in spec.get("floors", [])],
            "modes": spec.get("modes", []),
            "irreversible": spec.get("irreversible", False),
        })
    return tools


def _operational_tool_list() -> list[dict[str, Any]]:
    """Extract operational (diagnostic) tool data from constitutional_map."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from arifosmcp.constitutional_map import DIAGNOSTIC_TOOLS

    tools = []
    for name, spec in DIAGNOSTIC_TOOLS.items():
        tools.append({
            "name": name,
            "tier": spec.get("tier", "unknown"),
            "namespace": spec.get("namespace", "").split("(")[0].strip(),
            "risk_tier": spec.get("risk_tier", "low"),
            "description": spec.get("description", "").split(".")[0].strip(),
            "modes": spec.get("modes", []),
            "irreversible": spec.get("irreversible", False),
        })
    return tools


def _all_mcp_tools() -> list[dict[str, Any]]:
    """Combine canonical + operational for full MCP surface list."""
    return _canonical_tool_list() + _operational_tool_list()


def manifest_hash() -> str:
    """SHA256 of the full manifest JSON for cross-reference."""
    manifest = {
        "canonical_tools": len(_canonical_tool_list()),
        "operational_tools": len(_operational_tool_list()),
        "tools_exposed_via_mcp": len(_all_mcp_tools()),
    }
    raw = json.dumps(manifest, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def generate_llms_txt() -> str:
    """Generate llms.txt content from the live registry."""
    canonical = _canonical_tool_list()
    operational = _operational_tool_list()
    total = len(canonical) + len(operational)
    mhash = manifest_hash()

    lines: list[str] = []
    lines.append(f"# arifOS — Constitutional AI Governance Kernel")
    lines.append(f"> Auto-generated from live tool registry. Hash: {mhash}")
    lines.append(f"> Total MCP tools: {total} | Canonical: {len(canonical)} | Operational: {len(operational)}")
    lines.append(f"> Port: 8088 | License: AGPL-3.0 | Status: OPERATIONAL")
    lines.append("")
    lines.append("## MCP Tools — Complete Surface")
    lines.append(f"arifOS exposes {total} MCP tools: {len(canonical)} canonical constitutional tools")
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
            modes += f" +{len(t['modes'])-6} more"
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
            modes += f" +{len(t['modes'])-4} more"
        lines.append(f"| `{t['name']}` | {t['tier']} | {t['risk_tier']} | {irr} | {modes} |")
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
    lines.append(f"| **arifOS** (8088) | `arifos.arif-fazil.com/mcp` | Governance kernel | {len(_canonical_tool_list())} canonical + {len(_operational_tool_list())} operational |")
    lines.append("| **A-FORGE** (7071) | `forge.arif-fazil.com/mcp` | Engineering actuator | 59 (filesystem, git, docker, postgres, vault, shell, job, lease, agent) |")
    lines.append("| **GEOX** (8081) | `geox.arif-fazil.com/mcp` | Earth intelligence | 33 canonical tools |")
    lines.append("| **WEALTH** (18082) | `wealth.arif-fazil.com/mcp` | Capital intelligence | 20+ tools |")
    lines.append("| **WELL** (18083) | `well.arif-fazil.com/mcp` | Human readiness | 18+ tools |")
    lines.append("| **AAA** (3001) | `aaa.arif-fazil.com` | Control plane cockpit | A2A server, React SPA |")
    lines.append("")
    lines.append("## Agent Rules (mandatory)")
    lines.append("1. Never skip the 000-999 pipeline")
    lines.append("2. Never self-certify (F2 TRUTH)")
    lines.append("3. Never fabricate evidence (F9 ANTIHANTU)")
    lines.append("4. Never bypass human veto (F13 SOVEREIGN)")
    lines.append("5. Reversible-first: commit before big changes (F1 AMANAH)")
    lines.append("")
    lines.append("### Tool Location Rules")
    lines.append("- arifOS (8088) = governance only (judge, seal, reason, critique, hermes, lease, attest)")
    lines.append("- A-FORGE (7071) = engineering only (forge_*, filesystem, git, docker, postgres, shell, job)")
    lines.append("- forge_* on arifOS = DEPRECATED PROXY (calls forwarded to A-FORGE)")
    lines.append("- GEOX/WEALTH/WELL = domain evidence organs")
    lines.append("")
    lines.append("## Verification")
    lines.append(f"- tools/list count should match total ({total})")
    lines.append(f"- canonical_tools + operational_tools == tools_exposed_via_mcp")
    lines.append(f"- Manifest hash: {mhash}")
    lines.append(f"- Manifest URL: https://arifos.arif-fazil.com/manifest.txt")
    lines.append("")
    lines.append(f"--- Auto-generated {__import__('datetime').datetime.now().isoformat()} ---")

    return "\n".join(lines)


def main() -> None:
    """Generate llms.txt and output manifest JSON for CI."""
    txt = generate_llms_txt()
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "llms.txt")
    with open(path, "w") as f:
        f.write(txt)
    print(f"[MANIFEST] Wrote {path} ({len(txt)} chars)")
    print(f"[MANIFEST] Canonical: {len(_canonical_tool_list())} | Operational: {len(_operational_tool_list())}")
    print(f"[MANIFEST] Total MCP tools: {len(_all_mcp_tools())}")
    print(f"[MANIFEST] Hash: {manifest_hash()}")


if __name__ == "__main__":
    main()
