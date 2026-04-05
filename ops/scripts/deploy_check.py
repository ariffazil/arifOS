#!/usr/bin/env python3
"""
arifOS MCP - Pre-Deployment Readiness Checker
=============================================

A simple tool for AI agents to check if the system is ready for deployment.
Run this before deploying to catch issues early.

Usage:
    python scripts/deploy_check.py
    python scripts/deploy_check.py --fix

Returns exit code 0 if ready, 1 if not.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    remedy: Optional[str] = None


class DeploymentReadinessChecker:
    """Check if arifOS is ready for deployment."""
    
    def __init__(self, auto_fix: bool = False):
        self.auto_fix = auto_fix
        self.results: list[CheckResult] = []
        self.project_root = Path(__file__).parent.parent
        
    def check_git_status(self) -> CheckResult:
        """Check if git working directory is clean."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                check=True,
            )
            if result.stdout.strip():
                return CheckResult(
                    name="Git Status",
                    passed=False,
                    message=f"Uncommitted changes:\n{result.stdout}",
                    remedy="Run: git add . && git commit -m 'Pre-deploy changes'",
                )
            return CheckResult(
                name="Git Status",
                passed=True,
                message="Working directory clean",
            )
        except subprocess.CalledProcessError as e:
            return CheckResult(
                name="Git Status",
                passed=False,
                message=f"Git command failed: {e}",
                remedy="Ensure git is installed and this is a git repository",
            )
    
    def check_branch(self) -> CheckResult:
        """Check if on main branch for production."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                check=True,
            )
            branch = result.stdout.strip()
            if branch == "main":
                return CheckResult(
                    name="Git Branch",
                    passed=True,
                    message="On main branch ✓",
                )
            return CheckResult(
                name="Git Branch",
                passed=True,  # Warning only for staging
                message=f"On branch '{branch}' (OK for staging)",
            )
        except subprocess.CalledProcessError as e:
            return CheckResult(
                name="Git Branch",
                passed=False,
                message=f"Failed to get branch: {e}",
            )
    
    def check_tests_pass(self) -> CheckResult:
        """Check if tests are passing."""
        critical_tests = [
            ("Unit Tests", ["pytest", "tests/core/", "-x", "-q"]),
            ("Constitutional Tests", ["pytest", "tests/03_constitutional/", "-x", "-q"]),
        ]
        
        for test_name, test_cmd in critical_tests:
            try:
                result = subprocess.run(
                    test_cmd,
                    capture_output=True,
                    cwd=self.project_root,
                )
                if result.returncode != 0:
                    return CheckResult(
                        name=f"Tests ({test_name})",
                        passed=False,
                        message=f"{test_name} are failing",
                        remedy=f"Fix failing tests or run: pytest {test_cmd[-2]} -v",
                    )
            except FileNotFoundError:
                return CheckResult(
                    name=f"Tests ({test_name})",
                    passed=False,
                    message="pytest not found",
                    remedy="Install: pip install pytest",
                )
        
        return CheckResult(
            name="Tests",
            passed=True,
            message="All critical tests passing ✓",
        )
    
    def check_docker_available(self) -> CheckResult:
        """Check if Docker is available."""
        try:
            result = subprocess.run(
                ["docker", "version"],
                capture_output=True,
            )
            if result.returncode == 0:
                return CheckResult(
                    name="Docker",
                    passed=True,
                    message="Docker available ✓",
                )
            return CheckResult(
                name="Docker",
                passed=True,  # Warning only
                message="Docker not running (needed for local testing only)",
            )
        except FileNotFoundError:
            return CheckResult(
                name="Docker",
                passed=True,  # Warning only
                message="Docker not installed (needed for local testing only)",
            )
    
    def check_deploy_script(self) -> CheckResult:
        """Check if deploy script exists and is runnable."""
        deploy_script = self.project_root / "scripts" / "deploy.py"
        if not deploy_script.exists():
            return CheckResult(
                name="Deploy Script",
                passed=False,
                message="scripts/deploy.py not found",
                remedy="Ensure deployment scripts are present",
            )
        
        # Check if Python can parse it
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(deploy_script)],
                capture_output=True,
            )
            if result.returncode == 0:
                return CheckResult(
                    name="Deploy Script",
                    passed=True,
                    message="Deploy script ready ✓",
                )
            return CheckResult(
                name="Deploy Script",
                passed=False,
                message="Deploy script has syntax errors",
            )
        except Exception as e:
            return CheckResult(
                name="Deploy Script",
                passed=False,
                message=f"Failed to check deploy script: {e}",
            )
    
    def check_version_updated(self) -> CheckResult:
        """Check if version has been updated (optional)."""
        try:
            pyproject = self.project_root / "pyproject.toml"
            if not pyproject.exists():
                return CheckResult(
                    name="Version",
                    passed=True,
                    message="pyproject.toml not found (optional check)",
                )
            
            content = pyproject.read_text()
            # Just check it exists, don't validate format
            if "version" in content:
                return CheckResult(
                    name="Version",
                    passed=True,
                    message="Version configured in pyproject.toml",
                )
            return CheckResult(
                name="Version",
                passed=True,  # Warning only
                message="No version found in pyproject.toml",
            )
        except Exception as e:
            return CheckResult(
                name="Version",
                passed=True,  # Warning only
                message=f"Could not check version: {e}",
            )
    
    def run_all_checks(self) -> list[CheckResult]:
        """Run all readiness checks."""
        checks = [
            self.check_git_status,
            self.check_branch,
            self.check_tests_pass,
            self.check_docker_available,
            self.check_deploy_script,
            self.check_version_updated,
        ]
        
        self.results = []
        for check_func in checks:
            result = check_func()
            self.results.append(result)
            
            # Print progress
            symbol = "✅" if result.passed else "❌"
            print(f"{symbol} {result.name}: {result.message.split(chr(10))[0]}")
        
        return self.results
    
    def print_summary(self):
        """Print final summary."""
        print("\n" + "="*60)
        
        failed = [r for r in self.results if not r.passed]
        passed = [r for r in self.results if r.passed]
        
        if failed:
            print(f"❌ READINESS CHECK FAILED: {len(failed)} issue(s) found")
            print("="*60)
            for result in failed:
                print(f"\n🔴 {result.name}")
                print(f"   Issue: {result.message}")
                if result.remedy:
                    print(f"   Fix: {result.remedy}")
            print("\n" + "="*60)
            print("Fix the issues above, then run this script again.")
            return False
        else:
            print(f"✅ ALL CHECKS PASSED: {len(passed)}/{len(self.results)}")
            print("="*60)
            print("\n🚀 System is ready for deployment!")
            print("\nNext steps:")
            print("  Staging:    make deploy-staging")
            print("  Production: make deploy-production")
            print("  Dry run:    make deploy-dry-run")
            return True


def main():
    parser = argparse.ArgumentParser(
        description="Check if arifOS is ready for deployment",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to auto-fix issues where possible",
    )
    
    args = parser.parse_args()
    
    print("🔍 arifOS Deployment Readiness Check")
    print("="*60)
    print()
    
    checker = DeploymentReadinessChecker(auto_fix=args.fix)
    checker.run_all_checks()
    ready = checker.print_summary()
    
    sys.exit(0 if ready else 1)


if __name__ == "__main__":
    main()
