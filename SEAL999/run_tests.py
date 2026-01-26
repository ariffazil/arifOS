"""
Test runner for SEAL-999 canonical implementation.
Works around PowerShell && syntax issues.
"""

import sys
import os
import subprocess

def run_tests():
    """Run pytest for vault tests."""
    os.chdir("C:\\Users\\User\\arifOS\\SEAL999_CANONICAL")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/test_vault.py", "-v"],
        capture_output=True,
        text=True
    )
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    print(f"Return code: {result.returncode}")
    return result.returncode == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
