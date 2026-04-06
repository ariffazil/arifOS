import os
import re

root_dirs = [r"C:\ariffazil\arifOS\tests", r"C:\ariffazil\arifOS\core", r"C:\ariffazil\arifOS\ops", r"C:\ariffazil\arifOS\arifosmcp", r"C:\ariffazil\arifOS\archive", r"C:\ariffazil\arifOS\geox", r"C:\ariffazil\arifOS\sites", r"C:\ariffazil\arifOS\tools", r"C:\ariffazil\arifOS\apps"]

patterns = [
    (re.compile(r"from arifosmcp\.core\b"), "from core"),
    (re.compile(r"import arifosmcp\.core\b"), "import core"),
    (re.compile(r"arifosmcp\.core\b"), "core"), # catch-all for docs or other references like arifosmcp.core_init
]

for d in root_dirs:
    if not os.path.exists(d):
        continue
    for root, dirs, files in os.walk(d):
        for file in files:
            if file.endswith(".py") or file.endswith(".md") or file.endswith(".html"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    new_content = content
                    for pattern, replacement in patterns:
                        new_content = pattern.sub(replacement, new_content)
                    
                    if new_content != content:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        print(f"Updated {file_path}")
                except Exception as e:
                    pass
