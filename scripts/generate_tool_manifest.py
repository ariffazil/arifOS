import json
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path("/root/arifOS")
sys.path.insert(0, str(project_root))

from arifosmcp.constitutional_map import CANONICAL_TOOLS

manifest = {
    "server_name": "arifOS_MCP",
    "version": "v2026.05.05",
    "tools": []
}

for tool_name, spec in CANONICAL_TOOLS.items():
    manifest["tools"].append({
        "name": tool_name,
        "description": spec.get("description", ""),
        "category": "canonical",
        "risk_tier": spec.get("risk_tier", "medium"),
        "irreversible": spec.get("irreversible", False),
        "floors": spec.get("floors", []),
        "eureka_insight": spec.get("eureka_insight", "")
    })

# Write the manifest
output_file = project_root / "TOOL_MANIFEST.json"
with open(output_file, "w") as f:
    json.dump(manifest, f, indent=2)

print(f"Manifest written to {output_file}")
