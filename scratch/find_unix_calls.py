import os
import re

root_dir = r"C:\ariffazil\arifOS\arifosmcp"
pattern = re.compile(r"\b(uname|geteuid)\b")

matches = []
for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith(".py"):
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if pattern.search(line):
                            matches.append((filepath, i, line.strip()))
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

print(f"Found {len(matches)} matches:")
for filepath, line_num, content in matches:
    print(f"{filepath}:{line_num}: {content}")
