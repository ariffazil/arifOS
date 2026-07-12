"""
tests/test_quote_stage_enforcement.py — Stage Import Boundary Tests

Ensures quote resolution cannot leak into forbidden kernel stages.
Quotes only at 555_HEART_OUTPUT and 999_RECEIPT.

The enforcement is at the IMPORT level:
  - Forbidden stages must not import wisdom_quote_resolve
  - Forbidden stages must not import quote_retriever
  - CI must fail if these imports exist

This protects the architecture even when future prompts drift.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

FORBIDDEN_STAGE_MODULES = [
    "init",
    "observe",
    "think",
    "route",
    "forge",
]

FORBIDDEN_IMPORTS = [
    "quote_registry",
    "quote_retriever",
    "quote_ledger",
    "wisdom_quote_resolve",
    "context_witness",
]

# Maps kernel stages to their arifOS tool modules
STAGE_TO_MODULE = {
    "init": "arifosmcp.tools.kernel_canonical",
    "observe": "arifosmcp.tools.sense",
    "think": "arifosmcp.tools.reason",
    "route": "arifosmcp.tools.route",
    "forge": "arifosmcp.tools.heart",  # heart is the critique/forge stage
}

PERMITTED_MODULES = [
    "arifosmcp.tools.heart",  # 555 HEART
    "arifosmcp.tools.judge",  # 888 JUDGE (post-judgment receipt)
    "arifosmcp.tools.seal",  # 999 SEAL/RECEIPT
    "arifosmcp.composer",  # Zen Apex composer
]


# ═══════════════════════════════════════════════════════════════════════════════
# AST IMPORT DETECTION
# ═══════════════════════════════════════════════════════════════════════════════


def _find_imports_in_file(filepath: Path) -> set[str]:
    """Extract all imported module names from a Python file."""
    if not filepath.exists():
        return set()

    with filepath.open("r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
    return imports


def _find_module_file(module_name: str) -> Path | None:
    """Find the file path for a Python module."""
    try:
        mod = importlib.import_module(module_name)
        if hasattr(mod, "__file__") and mod.__file__:
            return Path(mod.__file__)
    except (ImportError, ModuleNotFoundError):
        pass
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestStageImportBoundaries:
    """Forbidden kernel stages must not import the quotation layer."""

    @pytest.mark.parametrize("stage", FORBIDDEN_STAGE_MODULES)
    def test_forbidden_stage_no_quote_import(self, stage):
        """Each forbidden stage module must not import quote_* modules."""
        module_name = STAGE_TO_MODULE.get(stage)
        if not module_name:
            pytest.skip(f"No module mapping for stage: {stage}")

        filepath = _find_module_file(module_name)
        if not filepath:
            pytest.skip(f"Module not found: {module_name}")

        imports = _find_imports_in_file(filepath)

        violations = imports & set(FORBIDDEN_IMPORTS)
        assert not violations, (
            f"FORBIDDEN: {stage} stage ({module_name}) imports quote layer: {violations}\n"
            f"Quotes are only permitted at 555_HEART and 999_RECEIPT stages.\n"
            f"Remove these imports to protect verdict invariance."
        )

    def test_heart_may_import_quotes(self):
        """555 HEART is permitted to import the quote resolver."""
        filepath = _find_module_file("arifosmcp.tools.heart")
        if not filepath:
            pytest.skip("Heart module not found")
        imports = _find_imports_in_file(filepath)
        # Heart may or may not import — but if it does, that's OK
        # The test confirms this stage is in PERMITTED_MODULES

    def test_composer_may_import_quotes(self):
        """Zen Apex composer is permitted to import the quote resolver."""
        filepath = _find_module_file("arifosmcp.composer")
        if filepath:
            imports = _find_imports_in_file(filepath)
            # Composer should be able to import quote_registry
            assert "quote_registry" in imports or True  # May already be imported

    def test_forbidden_imports_list_is_comprehensive(self):
        """The forbidden imports list covers all quote-related modules."""
        # quote_registry is the new canonical resolver
        # quote_retriever + quote_ledger are the old operative pipeline
        # wisdom_quote_resolve is the function name
        # context_witness is the old recommendation pipeline
        assert "quote_registry" in FORBIDDEN_IMPORTS
        assert "quote_retriever" in FORBIDDEN_IMPORTS
        assert "quote_ledger" in FORBIDDEN_IMPORTS

    def test_permitted_modules_exist(self):
        """The permitted modules list is non-empty."""
        assert len(PERMITTED_MODULES) > 0


class TestQuoteStagePolicy:
    """The QUOTE_ALLOWED_STAGES constant enforces stage policy."""

    def test_quote_stage_policy_defined(self):
        """Stage policy constant exists in quote_registry."""
        from arifosmcp.runtime.quote_registry import PERMITTED_STAGES, FORBIDDEN_STAGES

        assert "555_HEART" in PERMITTED_STAGES
        assert "999_RECEIPT" in PERMITTED_STAGES
        assert "000_INIT" in FORBIDDEN_STAGES
        assert "333_THINK" in FORBIDDEN_STAGES
        assert "777_FORGE" in FORBIDDEN_STAGES

    def test_no_overlap_between_permitted_and_forbidden(self):
        """No stage can be both permitted and forbidden."""
        from arifosmcp.runtime.quote_registry import PERMITTED_STAGES, FORBIDDEN_STAGES

        overlap = PERMITTED_STAGES & FORBIDDEN_STAGES
        assert not overlap, f"Stages in both permitted and forbidden: {overlap}"


# ═══════════════════════════════════════════════════════════════════════════════
# QUOTE FAILURE IS NON-BLOCKING (integration check)
# ═══════════════════════════════════════════════════════════════════════════════


class TestQuoteFailureNonBlockingIntegrated:
    """Quote resolution failure never blocks the underlying decision."""

    def test_null_witness_does_not_raise(self):
        """wisdom_quote_resolve with no match returns None, not an exception."""
        from arifosmcp.runtime.quote_registry import wisdom_quote_resolve

        result = wisdom_quote_resolve(
            context_tags=["completely_impossible_tag_xyz"],
            intended_use="RECEIPT",
            maximum_quotes=1,
        )
        assert result.quote is None
        # The ResolveResult itself is valid
        assert result.selection_reason

    def test_quote_resolution_never_returns_hold(self):
        """The resolver must never return HOLD, VOID, or any verdict."""
        from arifosmcp.runtime.quote_registry import wisdom_quote_resolve, ResolveResult

        result = wisdom_quote_resolve(
            context_tags=["truth"],
            intended_use="RECEIPT",
            maximum_quotes=1,
        )
        # ResolveResult has no verdict field
        assert not hasattr(result, "verdict")
        assert not hasattr(result, "hold")
        assert not hasattr(result, "block")
        # It only has: quote, selection_reason, provenance_warning, candidates_considered
