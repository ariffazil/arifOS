import os

replacements = {
    "arifosmcp.runtime.floor": "arifosmcp.runtime.floor",
    "arifosmcp.runtime.session": "arifosmcp.runtime.session",
    "arifosmcp.runtime.resource": "arifosmcp.runtime.resource",
    "arifosmcp.runtime.prompt": "arifosmcp.runtime.prompt",
    "arifosmcp.runtime.schema": "arifosmcp.runtime.schema",
    "arifosmcp.runtime.enforcer": "arifosmcp.runtime.enforcer",
    "arifosmcp.runtime.dispatcher": "arifosmcp.runtime.dispatcher",
    "arifosmcp.runtime.guard": "arifosmcp.runtime.guard",
    "arifosmcp.runtime.continuity": "arifosmcp.runtime.continuity",
    "arifosmcp.runtime.compression": "arifosmcp.runtime.compression",
}

root_dir = r"c:\ariffazil\arifOS\arifosmcp\runtime"

for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            new_content = content
            for old, new in replacements.items():
                new_content = new_content.replace(old, new)
            
            if new_content != content:
                print(f"Updating {path}")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
