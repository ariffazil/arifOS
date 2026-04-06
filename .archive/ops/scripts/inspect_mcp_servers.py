import json
import os
import re


def parse_tools(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    tools = {}
    pattern = r"@mcp\.tool\(\s*name=[\"\'\']([^\"\']+?)[\"\'\'],\s*description=[\"\'\']([^\"\']+?)[\"\'\']"
    for match in re.finditer(pattern, content):
        tools[match.group(1)] = match.group(2)
    return tools


def parse_directory_tools(directory):
    all_tools = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                all_tools.update(parse_tools(os.path.join(root, file)))
    return all_tools


manifest = {"servers": {}}

# arifosmcp.transport
aaa_tools = parse_tools(r"C:\Users\User\arifOS\arifosmcp.transport\server.py")
manifest["servers"]["arifosmcp.transport"] = {"tools": {}}
for name, desc in aaa_tools.items():
    tier = "UNKNOWN"
    if "[Lane:" in desc:
        tier = desc.split("[Lane:")[1].split("]")[0].strip()

    manifest["servers"]["arifosmcp.transport"]["tools"][name] = {
        "source_file": "arifosmcp.transport/server.py",
        "governance_tier": tier,
        "description": desc,
    }
manifest["servers"]["arifosmcp.transport"]["total_tools"] = len(aaa_tools)

# arifosmcp.intelligence
aclip_tools = parse_directory_tools(r"C:\Users\User\arifOS\arifosmcp.intelligence")
manifest["servers"]["arifosmcp.intelligence"] = {"tools": {}}
for name, desc in aclip_tools.items():
    manifest["servers"]["arifosmcp.intelligence"]["tools"][name] = {
        "source_file": "arifosmcp.intelligence/*",
        "governance_tier": "SENSORY (Read-Only)",
        "description": desc,
    }
manifest["servers"]["arifosmcp.intelligence"]["total_tools"] = len(aclip_tools)

manifest_path = r"C:\Users\User\.gemini\antigravity\brain\6b6f58e2-6482-4bda-906e-a7d52f8eb0e2\mcp-manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(json.dumps(manifest, indent=2))
