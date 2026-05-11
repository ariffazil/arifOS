import os
import ast

TOOLS = [
    "arifos_000_init",
    "arifos_111_sense",
    "arifos_222_witness",
    "arifos_333_mind",
    "arifos_444_kernel",
    "arifos_555_memory",
    "arifos_666_heart",
    "arifos_777_ops",
    "arifos_888_judge",
    "arifos_999_vault",
    "arifos_forge",
    "arifos_gateway",
    "arifos_sabar",
]

# Local workspace path
BASE_DIR = r"C:\ariffazil\arifOS\arifosmcp\tools"


def verify_execute_function(path: str):
    """Checks if the file has an async def execute() function."""
    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    for node in tree.body:
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "execute":
            return True
    return False


def verify_no_forbidden_patterns(path: str):
    """Checks for forbidden imports or calls."""
    forbidden = ["import2", "subprocess", "os.system"]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    for pattern in forbidden:
        if pattern in content:
            raise AssertionError(f"Forbidden pattern '{pattern}' detected in {path}")


def main():
    print("🔍 INITIALIZING ARCHITECT VALIDATION [NEXT HORIZON]")
    passed = 0
    missing = 0

    for tool in TOOLS:
        # Expected filename mapping
        suffix = tool.replace("arifos_", "")
        filename = f"_{suffix}.py"
        path = os.path.join(BASE_DIR, filename)

        if not os.path.exists(path):
            print(f"[?] {tool}: Missing file {filename}")
            missing += 1
            continue

        try:
            verify_no_forbidden_patterns(path)
            if not verify_execute_function(path):
                raise AssertionError("Missing 'async def execute()' function")

            print(f"[✓] {tool}: PASS")
            passed += 1
        except Exception as e:
            print(f"[!] {tool}: FAILED - {str(e)}")

    print("-" * 40)
    print(f"VERDICT: {passed}/13 tools verified.")
    if missing > 0:
        print(f"WARNING: {missing} tools are yet to be forged.")

    if passed == 13:
        print("ANTIGRAVITY SEAL = TRUE")


if __name__ == "__main__":
    main()
