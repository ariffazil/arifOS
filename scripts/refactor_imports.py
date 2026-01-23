import os


def refactor_imports(root_dir):
    print(f"Scanning {root_dir} for 'arifos' references...")
    count = 0
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py") or file.endswith(".md") or file.endswith(".json"):
                filepath = os.path.join(subdir, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    if "arifos" in content:
                        new_content = content.replace("arifos", "arifos")
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        print(f"Refactored: {filepath}")
                        count += 1
                except Exception as e:
                    print(f"Skipping {filepath}: {e}")
    print(f"Total files refactored: {count}")

if __name__ == "__main__":
    refactor_imports("arifos")
    refactor_imports("scripts")
