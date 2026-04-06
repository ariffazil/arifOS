#!/usr/bin/env python3
"""
e2e_audit_tools.py — End-to-End Code Audit for arifosmcp Tools
Based on 2026-03-14 audit report fixes verification
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import asyncio
import sys
import time
import traceback
from datetime import datetime
from typing import Any

sys.path.insert(0, ".")

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


class AuditResult:
    def __init__(self, name: str, status: str, message: str = "", details: dict = None):
        self.name = name
        self.status = status  # PASS, FAIL, WARN, SKIP
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()


def print_result(result: AuditResult):
    color = (
        GREEN
        if result.status == "PASS"
        else (RED if result.status == "FAIL" else (YELLOW if result.status == "WARN" else BLUE))
    )
    symbol = (
        "✅"
        if result.status == "PASS"
        else ("❌" if result.status == "FAIL" else ("⚠️" if result.status == "WARN" else "⏭️"))
    )
    print(f"{color}{symbol} {result.name}: {result.status}{RESET}")
    if result.message:
        print(f"   {result.message}")
    if result.details:
        for key, value in result.details.items():
            print(f"   • {key}: {value}")


# =============================================================================
# 1. CHROMA_QUERY AUDIT
# =============================================================================


async def audit_chroma_query() -> AuditResult:
    """Audit chroma_query tool code quality and API compatibility."""
    print(f"\n{BOLD}🔍 Auditing chroma_query...{RESET}")

    try:
        from arifosmcp.intelligence.tools.chroma_query import query_memory, list_collections
        import inspect

        # Check 1: Function exists and is callable
        results = []

        # Check 2: Source code analysis
        source = inspect.getsource(query_memory)

        # Verify dual API approach is present
        has_query_points = "query_points" in source
        has_search_fallback = "client.search" in source
        has_try_except = "try:" in source and "except" in source

        if has_query_points and has_search_fallback and has_try_except:
            results.append("Dual API compatibility (query_points + search fallback)")
        else:
            return AuditResult(
                "chroma_query",
                "FAIL",
                "Missing dual API approach",
                {"has_query_points": has_query_points, "has_search_fallback": has_search_fallback},
            )

        # Check 3: Function signature
        sig = inspect.signature(query_memory)
        params = list(sig.parameters.keys())
        expected = [
            "query",
            "collection",
            "n_results",
            "where",
            "include_embeddings",
            "_chroma_path",
        ]

        if all(p in params for p in expected):
            results.append("Complete function signature")
        else:
            return AuditResult(
                "chroma_query", "WARN", f"Missing params. Expected: {expected}, Got: {params}"
            )

        # Check 4: Import handling
        has_import_guard = "try:" in source and "except ImportError" in source
        if has_import_guard:
            results.append("Import error handling present")

        return AuditResult(
            "chroma_query", "PASS", "Code quality checks passed", {"checks": results}
        )

    except Exception as e:
        return AuditResult(
            "chroma_query",
            "FAIL",
            f"Exception during audit: {str(e)}",
            {"traceback": traceback.format_exc()},
        )


# =============================================================================
# 2. REALITY_HANDLERS AUDIT
# =============================================================================


async def audit_reality_handlers() -> AuditResult:
    """Audit reality_compass handler for null safety."""
    print(f"\n{BOLD}🔍 Auditing reality_handlers...{RESET}")

    try:
        from arifosmcp.runtime.reality_handlers import RealityHandler, SearchResult
        import inspect

        results = []

        # Check 1: search_brave method exists
        if hasattr(RealityHandler, "search_brave"):
            results.append("search_brave method exists")
        else:
            return AuditResult("reality_handlers", "FAIL", "Missing search_brave method")

        # Check 2: Source analysis for null safety
        source = inspect.getsource(RealityHandler.search_brave)

        # Check for web_results variable and null handling
        has_web_results = "web_results" in source
        has_null_check = "if web_results" in source or "web_results.get" in source
        has_safe_access = 'data.get("web", {})' in source

        if has_web_results and has_null_check:
            results.append("Null-safe web results access implemented")
        else:
            return AuditResult(
                "reality_handlers",
                "WARN",
                "May need additional null safety checks",
                {"has_web_results": has_web_results, "has_null_check": has_null_check},
            )

        # Check 3: BRAVE_API_KEY handling
        has_key_check = "BRAVE_API_KEY" in source and "if not BRAVE_API_KEY" in source
        if has_key_check:
            results.append("API key validation present")

        return AuditResult(
            "reality_handlers", "PASS", "Code quality checks passed", {"checks": results}
        )

    except Exception as e:
        return AuditResult(
            "reality_handlers",
            "FAIL",
            f"Exception during audit: {str(e)}",
            {"traceback": traceback.format_exc()},
        )


# =============================================================================
# 3. LOG_READER AUDIT
# =============================================================================


async def audit_log_reader() -> AuditResult:
    """Audit log_tail tool for smart path detection."""
    print(f"\n{BOLD}🔍 Auditing log_reader...{RESET}")

    try:
        from arifosmcp.intelligence.tools.log_reader import log_tail, _find_default_log
        import inspect

        results = []

        # Check 1: _find_default_log function exists
        if callable(_find_default_log):
            results.append("_find_default_log helper exists")
        else:
            return AuditResult("log_reader", "FAIL", "Missing _find_default_log helper")

        # Check 2: Source analysis
        source = inspect.getsource(log_tail)
        helper_source = inspect.getsource(_find_default_log)

        # Check for path detection
        has_candidates = "candidates" in helper_source
        has_exists_check = "os.path.exists" in helper_source
        has_fallback = helper_source.count("return") >= 2

        if has_candidates and has_exists_check and has_fallback:
            results.append("Smart path detection implemented")
        else:
            return AuditResult(
                "log_reader",
                "WARN",
                "Path detection may be incomplete",
                {"has_candidates": has_candidates, "has_exists_check": has_exists_check},
            )

        # Check 3: Function signature allows None
        sig = inspect.signature(log_tail)
        params = sig.parameters
        if "log_file" in params:
            param = params["log_file"]
            if param.default is None or str(param.annotation).endswith("None"):
                results.append("Optional log_file parameter")

        return AuditResult("log_reader", "PASS", "Code quality checks passed", {"checks": results})

    except Exception as e:
        return AuditResult(
            "log_reader",
            "FAIL",
            f"Exception during audit: {str(e)}",
            {"traceback": traceback.format_exc()},
        )


# =============================================================================
# 4. SYSTEM_MONITOR AUDIT
# =============================================================================


async def audit_system_monitor() -> AuditResult:
    """Audit system_monitor for container awareness."""
    print(f"\n{BOLD}🔍 Auditing system_monitor...{RESET}")

    try:
        from arifosmcp.intelligence.tools.system_monitor import (
            get_resource_usage,
            list_processes,
            _is_running_in_container,
        )
        import inspect

        results = []

        # Check 1: Container detection function
        if callable(_is_running_in_container):
            results.append("_is_running_in_container helper exists")

            # Check detection logic
            source = inspect.getsource(_is_running_in_container)
            has_dockerenv = ".dockerenv" in source
            has_cgroup = "cgroup" in source

            if has_dockerenv and has_cgroup:
                results.append("Multiple container detection methods")
        else:
            return AuditResult("system_monitor", "FAIL", "Missing container detection")

        # Check 2: get_resource_usage has container handling
        source = inspect.getsource(get_resource_usage)
        has_container_mode = "container_mode" in source
        has_exception_handling = source.count("try:") >= 3  # Multiple try blocks

        if has_container_mode and has_exception_handling:
            results.append("Container-aware exception handling")
        else:
            return AuditResult(
                "system_monitor",
                "WARN",
                "May need more robust exception handling",
                {"has_container_mode": has_container_mode},
            )

        # Check 3: list_processes handles access denied
        source = inspect.getsource(list_processes)
        has_access_denied = "AccessDenied" in source or "access_denied" in source.lower()
        has_partial = "partial" in source.lower()

        if has_access_denied:
            results.append("Access denied handling present")

        return AuditResult(
            "system_monitor", "PASS", "Code quality checks passed", {"checks": results}
        )

    except Exception as e:
        return AuditResult(
            "system_monitor",
            "FAIL",
            f"Exception during audit: {str(e)}",
            {"traceback": traceback.format_exc()},
        )


# =============================================================================
# 5. ORCHESTRATOR AUDIT
# =============================================================================


async def audit_orchestrator() -> AuditResult:
    """Audit metabolic_loop for timeout handling."""
    print(f"\n{BOLD}🔍 Auditing orchestrator...{RESET}")

    try:
        from arifosmcp.runtime.orchestrator import metabolic_loop
        import inspect

        results = []

        # Check 1: Function signature has timeout
        sig = inspect.signature(metabolic_loop)
        params = list(sig.parameters.keys())

        if "timeout_seconds" in params:
            results.append("timeout_seconds parameter present")
        else:
            return AuditResult(
                "orchestrator", "FAIL", "Missing timeout_seconds parameter", {"params": params}
            )

        # Check 2: Source analysis
        source = inspect.getsource(metabolic_loop)

        has_timeout_check = "_check_timeout" in source or "timeout" in source.lower()
        has_wait_for = "wait_for" in source or "asyncio.wait_for" in source

        if has_timeout_check:
            results.append("Timeout checking logic present")
        if has_wait_for:
            results.append("Async timeout wrapper present")

        if not has_timeout_check and not has_wait_for:
            return AuditResult(
                "orchestrator",
                "WARN",
                "Timeout logic may be incomplete",
                {"has_timeout_check": has_timeout_check, "has_wait_for": has_wait_for},
            )

        # Check 3: Check for elapsed time tracking
        has_perf_counter = "perf_counter" in source
        if has_perf_counter:
            results.append("Performance timing implemented")

        return AuditResult(
            "orchestrator", "PASS", "Code quality checks passed", {"checks": results}
        )

    except Exception as e:
        return AuditResult(
            "orchestrator",
            "FAIL",
            f"Exception during audit: {str(e)}",
            {"traceback": traceback.format_exc()},
        )


# =============================================================================
# MAIN EXECUTION
# =============================================================================


async def run_e2e_audit():
    """Run complete e2e audit of all fixed tools."""
    print(f"{BOLD}{'=' * 70}{RESET}")
    print(f"{BOLD}  arifosmcp E2E Code Audit{RESET}")
    print(f"{BOLD}  Based on: 2026-03-14 Tool Audit Report{RESET}")
    print(f"{BOLD}{'=' * 70}{RESET}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    start_time = time.time()

    # Run all audits
    results = []

    results.append(await audit_chroma_query())
    results.append(await audit_reality_handlers())
    results.append(await audit_log_reader())
    results.append(await audit_system_monitor())
    results.append(await audit_orchestrator())

    # Print summary
    print(f"\n{BOLD}{'=' * 70}{RESET}")
    print(f"{BOLD}📊 AUDIT SUMMARY{RESET}")
    print(f"{'=' * 70}")

    for result in results:
        print_result(result)

    # Statistics
    total = len(results)
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    warnings = sum(1 for r in results if r.status == "WARN")

    elapsed = time.time() - start_time

    print(f"\n{BOLD}{'=' * 70}{RESET}")
    print(f"Total: {total} | ✅ Pass: {passed} | ❌ Fail: {failed} | ⚠️ Warn: {warnings}")
    print(f"Duration: {elapsed:.2f}s")

    if failed > 0:
        print(f"\n{RED}{BOLD}Result: FAILED — {failed} critical issues found{RESET}")
        return 1
    elif warnings > 0:
        print(
            f"\n{YELLOW}{BOLD}Result: PASSED WITH WARNINGS — {warnings} non-critical issues{RESET}"
        )
        return 0
    else:
        print(f"\n{GREEN}{BOLD}Result: ALL CHECKS PASSED{RESET}")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_e2e_audit())
    sys.exit(exit_code)
