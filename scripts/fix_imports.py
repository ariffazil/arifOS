import os
import re

TARGET_DIR = "arifos/mcp"

def fix_imports_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern 1: from arifos_core.X import Y -> from arifos.core.X import Y OR from arifos.X import Y?
    # Based on the user prompt: "from arifos_core.mcp.models import VerdictResponse"
    # And we see arifos/mcp/models.py exists (checking via dir next).
    # If arifos/mcp/models.py exists, then `from arifos.mcp.models` is correct.
    # If it was `from arifos_core.core.X`, it becomes `from arifos.core.X`.

    # Simple strategy: replace "arifos_core" with "arifos"
    # But check if it needs to be "arifos.core" in some cases?
    # User said: "Batch fix: Replace all `from arifos_core.` -> `from arifos.`"

    new_content = content.replace("from arifos_core.", "from arifos.")
    new_content = new_content.replace("import arifos_core.", "import arifos.")
    new_content = new_content.replace("import arifos_core", "import arifos")

    if content != new_content:
        print(f"Fixing {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

for root, dirs, files in os.walk(TARGET_DIR):
    for file in files:
        if file.endswith(".py"):
            fix_imports_in_file(os.path.join(root, file))

print("Batch fix complete.")
