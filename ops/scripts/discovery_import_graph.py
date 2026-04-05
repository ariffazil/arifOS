import os
import re

TARGETS = [
    "arifosmcp.transport/streamable_http_server.py",
    "arifosmcp.transport/rest.py",
    "arifosmcp.transport/server.py",
    "core/shared/floors.py",
]

# We also want to check `core/enforcement/`
ENFORCEMENT_DIR = "core/enforcement"

REPO_ROOT = r"c:\Users\User\arifOS"


def check_existence():
    print("=== FILE EXISTENCE ===")
    for target in TARGETS:
        path = os.path.join(REPO_ROOT, target.replace("/", os.sep))
        print(f"{target}: {'EXISTS' if os.path.exists(path) else 'MISSING'}")

    enf_path = os.path.join(REPO_ROOT, ENFORCEMENT_DIR.replace("/", os.sep))
    if os.path.exists(enf_path):
        print(f"{ENFORCEMENT_DIR}/: EXISTS")
        for f in os.listdir(enf_path):
            if f.endswith(".py"):
                print(f"  - {f}")
    else:
        print(f"{ENFORCEMENT_DIR}/: MISSING")
    print()


def find_imports():
    print("=== IMPORT GRAPH ===")
    # Extremely basic grep for import statements related to our targets
    # e.g., "import arifosmcp.transport.server", "from arifosmcp.transport.rest import"

    patterns = {
        "arifosmcp.transport/streamable_http_server.py": [
            r"arifosmcp.transport\.streamable_http_server"
        ],
        "arifosmcp.transport/rest.py": [r"arifosmcp.transport\.rest"],
        "arifosmcp.transport/server.py": [r"arifosmcp.transport\.server"],
        "core/shared/floors.py": [r"core\.shared\.floors"],
        "core/enforcement/": [r"core\.enforcement"],
    }

    # We will search .py files
    results = {k: [] for k in patterns.keys()}

    for root, _dirs, files in os.walk(REPO_ROOT):
        if ".venv" in root or ".git" in root or "__pycache__" in root:
            continue
        for f in files:
            if not f.endswith(".py"):
                continue
            filepath = os.path.join(root, f)
            try:
                with open(filepath, encoding="utf-8") as file:
                    content = file.read()

                    for target, pat_list in patterns.items():
                        for pat in pat_list:
                            if re.search(pat, content):
                                rel_path = os.path.relpath(filepath, REPO_ROOT)
                                results[target].append(rel_path)
                                break
            except Exception:
                pass

    for target, usage in results.items():
        print(f"Target: {target}")
        if usage:
            for u in usage:
                print(f"  imported by: {u}")
        else:
            print("  imported by: [NO USAGE FOUND]")


if __name__ == "__main__":
    check_existence()
    find_imports()
