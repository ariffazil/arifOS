import os
import re
import sys


def find_orphans(root_dir):
    py_files = []
    for root, dirs, files in os.walk(root_dir):
        if "archive" in root or "tests" in root or "venv" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                rel_path = os.path.relpath(os.path.join(root, file), root_dir)
                py_files.append(rel_path)

    referenced_modules = set()
    module_pattern = re.compile(r"(?:from|import)\s+([a-zA-Z0-9_\.]+)")

    for root, dirs, files in os.walk(root_dir):
        if "archive" in root or "venv" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding="utf-8") as f:
                        for line in f:
                            matches = module_pattern.findall(line)
                            for match in matches:
                                referenced_modules.add(match)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}", file=sys.stderr)

    # Entrypoints from pyproject.toml
    entrypoints = [
        "arifosmcp.transport.__main__",
        "arifosmcp.runtime.__main__",
        "arifosmcp.intelligence.cli",
        "arifosmcp.intelligence.__main__",
    ]
    for ep in entrypoints:
        referenced_modules.add(ep)

    orphans = []
    for rel_path in py_files:
        module_name = rel_path.replace(os.sep, ".").replace(".py", "")

        # Check if the module name or any prefix is referenced
        is_referenced = False
        for ref in referenced_modules:
            if (
                ref == module_name
                or ref.startswith(module_name + ".")
                or module_name.startswith(ref + ".")
            ):
                is_referenced = True
                break

        if not is_referenced:
            orphans.append(rel_path)

    return orphans


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    orphans = find_orphans(root)
    print(
        "Potential Orphans (not imported by any non-test file, excluding __init__.py and common entrypoints):"
    )
    for o in orphans:
        print(o)
