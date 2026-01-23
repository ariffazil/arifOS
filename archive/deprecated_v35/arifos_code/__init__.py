# File: arifos_code/__init__.py
"""
arifOS Code: Constitutional Governance for Claude Code

Wraps Anthropic's Claude Code with arifOS ΔΩΨ constitutional enforcement.

Components:
- PreExecutionTEARFRAME: File existence validation (000→777)
- ClaudeCodeClient: Native Anthropic API wrapper
- ClaudeCodeMetricsComputer: AST-based Truth verification + floor metrics (888)
- GovernedClaudeCode: Complete governed execution loop
- ASTTruthVerifier: Earth Witness for mathematical proof

Usage:
    from arifos_code import GovernedClaudeCode
    from pathlib import Path

    governed_claude = GovernedClaudeCode(
        api_key="your-anthropic-api-key",
        workspace_root=Path.cwd(),
        ledger_path=Path("arifos_code_ledger.jsonl")
    )

    result = governed_claude.execute_governed_request(
        user_request="Fix the bug in auth.py line 42",
        context={"job_id": "security-fix"}
    )

    print(f"Verdict: {result['verdict']}")
    print(f"Metrics: {result['metrics']}")
"""

from .governed_client import GovernedClaudeCode, ClaudeCodeClient
from .metrics_computer import ClaudeCodeMetricsComputer
from .pre_execution import PreExecutionTEARFRAME
from .ast_verifier import ASTCodebaseAnalyzer, ASTTruthVerifier

__version__ = "0.1.0-alpha"
__author__ = "arifOS Core Team"

__all__ = [
    # Main API
    "GovernedClaudeCode",

    # Components (for advanced usage)
    "ClaudeCodeClient",
    "ClaudeCodeMetricsComputer",
    "PreExecutionTEARFRAME",
    "ASTCodebaseAnalyzer",
    "ASTTruthVerifier",
]
