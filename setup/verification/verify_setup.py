#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arifOS Visual Studio Setup Verification Script
Verifies all dependencies and configuration are correct.

Usage:
    python verify_setup.py
"""

import sys
from typing import List, Tuple


# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def check_python_version() -> Tuple[bool, str]:
    """Verify Python version is 3.10+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)"

def check_import(module_name: str, display_name: str = None) -> Tuple[bool, str]:
    """Check if a module can be imported"""
    if display_name is None:
        display_name = module_name

    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        return True, f"{display_name} {version}"
    except ImportError as e:
        return False, f"{display_name} not found: {str(e)}"

def check_arifos_core() -> Tuple[bool, str]:
    """Check arifOS core functionality"""
    try:
        from arifos.core.system.apex_prime import APEX_VERSION, APEXPrime
        apex = APEXPrime()
        return True, f"arifOS APEX Prime {APEX_VERSION} OK"
    except Exception as e:
        return False, f"arifOS APEX Prime initialization failed: {str(e)}"

def check_docker() -> Tuple[bool, str]:
    """Check Docker availability"""
    import subprocess
    try:
        result = subprocess.run(['docker', '--version'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, version
        return False, "Docker command failed"
    except FileNotFoundError:
        return False, "Docker not found in PATH"
    except subprocess.TimeoutExpired:
        return False, "Docker command timeout (is Docker running?)"
    except Exception as e:
        return False, f"Docker check error: {str(e)}"

def run_verification():
    """Run all verification checks"""

    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}arifOS Visual Studio Setup Verification{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

    checks: List[Tuple[str, callable]] = [
        ("Python Version", check_python_version),
        ("NumPy", lambda: check_import("numpy", "NumPy")),
        ("Pydantic", lambda: check_import("pydantic")),
        ("LiteLLM", lambda: check_import("litellm")),
        ("FastAPI", lambda: check_import("fastapi")),
        ("Uvicorn", lambda: check_import("uvicorn")),
        ("FastMCP", lambda: check_import("fastmcp", "FastMCP")),
        ("DSPy", lambda: check_import("dspy", "DSPy")),
        ("Pytest", lambda: check_import("pytest")),
        ("Black", lambda: check_import("black")),
        ("Ruff", lambda: check_import("ruff")),
        ("arifOS APEX Prime", check_arifos_core),
        ("Docker", check_docker),
    ]

    results = []
    max_name_len = max(len(name) for name, _ in checks)

    print(f"{Colors.BOLD}Core Dependencies:{Colors.END}\n")

    for check_name, check_func in checks:
        try:
            passed, message = check_func()
            results.append(passed)

            status = "[OK]" if passed else "[FAIL]"
            padding = " " * (max_name_len - len(check_name))

            if passed:
                print(f"  {status} {check_name}{padding}  {Colors.GREEN}{message}{Colors.END}")
            else:
                print(f"  {status} {check_name}{padding}  {Colors.RED}{message}{Colors.END}")

        except Exception as e:
            results.append(False)
            print(f"  [FAIL] {check_name}  {Colors.RED}Error: {str(e)}{Colors.END}")

    # Summary
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    total = len(results)
    passed = sum(results)
    failed = total - passed

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[OK] All checks passed! ({passed}/{total}){Colors.END}")
        print(f"\n{Colors.GREEN}Your Visual Studio environment is fully configured for arifOS!{Colors.END}")
        print(f"\n{Colors.BOLD}Next steps:{Colors.END}")
        print(f"  1. Read QUICK_START_VISUAL_STUDIO.md")
        print(f"  2. Activate environment: .venv\\Scripts\\Activate.ps1")
        print(f"  3. Run tests: pytest")
        print(f"  4. Start coding: code .")
        print(f"\n{Colors.BOLD}DITEMPA BUKAN DIBERI{Colors.END} - Your environment is forged! [checkmark][scales]\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}[FAIL] Some checks failed ({failed}/{total}){Colors.END}")
        print(f"\n{Colors.YELLOW}Failed checks:{Colors.END}")
        for i, (check_name, _) in enumerate(checks):
            if not results[i]:
                print(f"  - {check_name}")

        print(f"\n{Colors.YELLOW}Troubleshooting:{Colors.END}")
        print(f"  1. Activate virtual environment: .venv\\Scripts\\Activate.ps1")
        print(f"  2. Reinstall dependencies: pip install -e \".[all]\"")
        print(f"  3. Check VISUAL_STUDIO_SETUP.md for detailed instructions")
        print(f"  4. For Docker: ensure Docker Desktop is running\n")
        return 1

def main():
    """Main entry point"""
    try:
        exit_code = run_verification()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Verification cancelled by user.{Colors.END}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}Fatal error:{Colors.END} {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
