import os
import re


def refactor_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    new_content = content

    # 1. arifos_core -> arifos.core
    new_content = re.sub(r'from arifos.core', 'from arifos.core', new_content)
    new_content = re.sub(r'import arifos.core', 'import arifos.core', new_content)

    # 2. arifos_clip -> arifos.protocol
    new_content = re.sub(r'from arifos.protocol', 'from arifos.protocol', new_content)
    new_content = re.sub(r'import arifos.protocol', 'import arifos.protocol', new_content)

    # 3. arifos_orchestrator -> arifos.orchestrator
    new_content = re.sub(r'from arifos.orchestrator', 'from arifos.orchestrator', new_content)
    new_content = re.sub(r'import arifos.orchestrator', 'import arifos.orchestrator', new_content)

    # 4. Cleanup 'from arifos import' to 'from arifos.core import' if it refers to core modules?
    # No, arifos/__init__.py will handle re-exports.

    if new_content != content:
        print(f"Refactoring {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

def main():
    targets = ["tests", "scripts", "arifos"]
    root = os.getcwd()

    for target in targets:
        target_path = os.path.join(root, target)
        if not os.path.exists(target_path):
            continue

        for subdir, dirs, files in os.walk(target_path):
            if "archive_local" in subdir:
                continue
            for file in files:
                if file.endswith(".py"):
                    refactor_file(os.path.join(subdir, file))

if __name__ == "__main__":
    main()
