"""
arifOS Python Archaeology Scanner (Simplified)
Purpose: Generate governance audit report for Python codebase
"""

import os
from pathlib import Path


def scan_files():
    """Simple file scanner without AST parsing."""
    files = []
    core_dir = "arifos_core"

    for root, dirs, filenames in os.walk(core_dir):
        # Skip pycache
        if "__pycache__" in root:
            continue

        for filename in filenames:
            if not filename.endswith(".py"):
                continue

            filepath = os.path.join(root, filename)
            size_kb = os.path.getsize(filepath) / 1024

            # Count lines
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
            except:
                lines = 0

            # Count imports (simple grep)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    imports = content.count("import ") + content.count("from ")
            except:
                imports = 0

            files.append({
                "path": filepath.replace("\\", "/"),
                "name": filename,
                "size_kb": round(size_kb, 1),
                "lines": lines,
                "imports": imports,
                "directory": os.path.dirname(filepath).replace(core_dir, "").replace("\\", "/").lstrip("/")
            })

    return files

# Run scan
print("Scanning arifos_core/...")
files = scan_files()

print(f"Total files: {len(files)}")
print(f"Total size: {sum(f['size_kb'] for f in files):.1f} KB")

# Sort by size
files.sort(key=lambda x: x["size_kb"], reverse=True)

# Generate report
report = f"""# arifOS Python Archaeology Report
**Date:** 2026-01-06
**Total Files:** {len(files)}
**Total Size:** {sum(f['size_kb'] for f in files):.1f} KB

## Top 30 Files by Size

| Rank | File | Size (KB) | Lines | Imports | Directory |
|------|------|-----------|-------|---------|-----------|
"""

for i, f in enumerate(files[:30], 1):
    report += f"| {i} | `{f['name']}` | {f['size_kb']} | {f['lines']} | {f['imports']} | `{f['directory']}` |\n"

# Directory stats
from collections import defaultdict

dir_counts = defaultdict(int)
for f in files:
    dir_counts[f['directory']] += 1

report += "\n## Directory Distribution\n\n| Directory | File Count |\n|-----------|------------|\n"
for dir_name, count in sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
    report += f"| `{dir_name}` | {count} |\n"

# No imports
no_imports = [f for f in files if f['imports'] == 0 and f['name'] != "__init__.py"]
report += f"\n## Files with NO Imports ({len(no_imports)} files)\n\n| File | Size (KB) | Lines | Path |\n|------|-----------|-------|------|\n"
for f in no_imports[:20]:
    report += f"| `{f['name']}` | {f['size_kb']} | {f['lines']} | `{f['path']}` |\n"

# Save report
with open("PYTHON_ARCHAEOLOGY_REPORT.md", "w", encoding="utf-8") as out:
    out.write(report)

print("Report saved to: PYTHON_ARCHAEOLOGY_REPORT.md")
