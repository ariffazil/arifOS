import ast
import json
import os


def extract_tools_ast(filepath):
    if not os.path.exists(filepath):
        return {}

    with open(filepath, encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    tools = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.FunctionDef):
            is_mcp_tool = False
            for dec in node.decorator_list:
                # Check for @mcp.tool or @mcp.tool(...)
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                    if dec.func.value.id == "mcp" and dec.func.attr == "tool":
                        is_mcp_tool = True
                elif isinstance(dec, ast.Attribute):
                    if dec.value.id == "mcp" and dec.attr == "tool":
                        is_mcp_tool = True

            if is_mcp_tool:
                name = node.name
                desc = ast.get_docstring(node) or "No description"

                # Check if the decorator overrides the name/description
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call):
                        for kw in dec.keywords:
                            if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                                name = kw.value.value
                            elif kw.arg == "description" and isinstance(kw.value, ast.Constant):
                                desc = kw.value.value

                tools[name] = desc

    return tools


manifest = {"servers": {}}

# arifosmcp.transport
aaa_tools = extract_tools_ast(r"C:\Users\User\arifOS\arifosmcp.transport\server.py")
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
aclip_tools = {}
for root_dir, _, files in os.walk(r"C:\Users\User\arifOS\arifosmcp.intelligence"):
    for file in files:
        if file.endswith(".py"):
            fpath = os.path.join(root_dir, file)
            file_tools = extract_tools_ast(fpath)
            for name, desc in file_tools.items():
                short_path = "arifosmcp.intelligence/" + os.path.relpath(
                    fpath, r"C:\Users\User\arifOS\arifosmcp.intelligence"
                ).replace("\\", "/")
                aclip_tools[name] = (short_path, desc)

manifest["servers"]["arifosmcp.intelligence"] = {"tools": {}}
for name, (src, desc) in aclip_tools.items():
    manifest["servers"]["arifosmcp.intelligence"]["tools"][name] = {
        "source_file": src,
        "governance_tier": "SENSORY (Read-Only Grounding)",
        "description": desc.split("\n")[0] if desc else "None",
    }
manifest["servers"]["arifosmcp.intelligence"]["total_tools"] = len(aclip_tools)

manifest_path = r"C:\Users\User\.gemini\antigravity\brain\6b6f58e2-6482-4bda-906e-a7d52f8eb0e2\mcp-manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(json.dumps(manifest, indent=2))
