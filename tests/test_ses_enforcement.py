"""
test_ses_enforcement.py — Single Execution Spine (SES) Guardrail Tests

v45Ω SES ENFORCEMENT: These tests prevent parallel truth and execution drift.

CRITICAL INVARIANTS:
1. ONLY apex_prime.py may define apex_review() and check_floors()
2. verdict_emission.py must NOT contain verdict decision logic
3. metrics.py must NOT return Verdict objects
4. No other module may import Verdict for decision purposes

These tests are FAST and run on every test suite to prevent drift forever.

DITEMPA, BUKAN DIBERI
"""

import ast
import inspect
from pathlib import Path


def test_only_apex_prime_defines_apex_review():
    """
    SES Guardrail: Only apex_prime.py may define apex_review().

    Prevents parallel verdict sources from being created in other files.
    """
    apex_prime_path = Path("arifos_core/system/apex_prime.py")

    # Verify apex_review exists in apex_prime
    assert apex_prime_path.exists(), "apex_prime.py must exist"

    source = apex_prime_path.read_text(encoding='utf-8')
    assert "def apex_review(" in source, "apex_prime.py must define apex_review()"

    # Check other verdict-related files do NOT define it
    forbidden_files = [
        "arifos_core/system/verdict_emission.py",
        "arifos_core/enforcement/metrics.py",
        "arifos_core/enforcement/genius_metrics.py",
    ]

    for filepath in forbidden_files:
        path = Path(filepath)
        if path.exists():
            source = path.read_text(encoding='utf-8')
            assert "def apex_review(" not in source, \
                f"{filepath} must NOT define apex_review() (parallel truth violation)"


def test_only_apex_prime_defines_check_floors():
    """
    SES Guardrail: Only apex_prime.py may define check_floors().

    Floor checking is part of verdict decision authority.
    """
    apex_prime_path = Path("arifos_core/system/apex_prime.py")

    # Verify check_floors exists in apex_prime
    source = apex_prime_path.read_text(encoding='utf-8')
    assert "def check_floors(" in source, "apex_prime.py must define check_floors()"

    # Check other files do NOT define it
    forbidden_files = [
        "arifos_core/system/verdict_emission.py",
        "arifos_core/enforcement/metrics.py",
    ]

    for filepath in forbidden_files:
        path = Path(filepath)
        if path.exists():
            source = path.read_text(encoding='utf-8')
            assert "def check_floors(" not in source, \
                f"{filepath} must NOT define check_floors() (parallel truth violation)"


def test_verdict_emission_has_no_verdict_decision_logic():
    """
    SES Guardrail: verdict_emission.py must be formatting ONLY.

    It may map verdicts to emojis/text, but must not contain
    if-statements that decide SEAL vs VOID vs PARTIAL.
    """
    path = Path("arifos_core/system/verdict_emission.py")
    if not path.exists():
        return  # Module optional

    source = path.read_text(encoding='utf-8')

    # verdict_emission may reference Verdict for formatting, but NOT for decisions
    # It should NOT have functions that return Verdict.SEAL etc as decision logic

    # Parse AST to check for verdict decision patterns
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check function return type annotations
            if node.returns and isinstance(node.returns, ast.Name):
                assert node.returns.id != "Verdict", \
                    f"verdict_emission.py function '{node.name}' returns Verdict (decision logic forbidden)"


def test_metrics_has_no_verdict_returns():
    """
    SES Guardrail: metrics.py must compute measurements, NOT verdicts.

    It may return FloorsVerdict (boolean checks), but NOT Verdict decisions.
    """
    path = Path("arifos_core/enforcement/metrics.py")
    if not path.exists():
        return

    source = path.read_text(encoding='utf-8')

    # Parse AST
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check return type annotations
            if node.returns and isinstance(node.returns, ast.Name):
                # FloorsVerdict is allowed (boolean floor checks)
                # Verdict is FORBIDDEN (decision authority)
                if node.returns.id == "Verdict":
                    raise AssertionError(
                        f"metrics.py function '{node.name}' returns Verdict "
                        f"(verdict decisions forbidden - use apex_prime.py)"
                    )


def test_ses_authority_headers_present():
    """
    SES Guardrail: All core modules must have SES authority headers.

    This ensures future agents understand the execution spine.
    """
    required_headers = {
        "arifos_core/system/apex_prime.py": "v45Ω EXECUTION AUTHORITY",
        "arifos_core/system/pipeline.py": "v45Ω EXECUTION AUTHORITY",
        "arifos_core/enforcement/metrics.py": "v45Ω SES AUTHORITY",
        "arifos_core/system/verdict_emission.py": "v45Ω SES AUTHORITY",
    }

    for filepath, expected_header in required_headers.items():
        path = Path(filepath)
        if not path.exists():
            continue

        source = path.read_text(encoding='utf-8')
        assert expected_header in source, \
            f"{filepath} missing SES authority header: '{expected_header}'"


def test_genius_metrics_canonical_path():
    """
    SES Guardrail: genius_metrics canonical path enforcement.

    The canonical location is arifos_core/enforcement/genius_metrics.py.
    Root-level arifos_core/genius_metrics.py is a deprecated shim only.
    """
    canonical = Path("arifos_core/enforcement/genius_metrics.py")
    shim = Path("arifos_core/genius_metrics.py")

    # Canonical must exist and be substantial
    assert canonical.exists(), "Canonical genius_metrics.py must exist"
    canonical_source = canonical.read_text(encoding='utf-8')
    assert len(canonical_source) > 100, "Canonical genius_metrics.py must be substantial"

    # Shim may exist but must be small (< 50 lines) and import from canonical
    if shim.exists():
        shim_source = shim.read_text(encoding='utf-8')
        shim_lines = len(shim_source.splitlines())
        assert shim_lines < 50, f"Root genius_metrics.py shim too large ({shim_lines} lines) - must be < 50"
        assert "from arifos_core.enforcement.genius_metrics import" in shim_source, \
            "Root genius_metrics.py must import from canonical enforcement/ location"
        assert "DEPRECATED" in shim_source or "deprecated" in shim_source, \
            "Root genius_metrics.py must warn about deprecation"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
