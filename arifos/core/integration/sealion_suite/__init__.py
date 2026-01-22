"""
sealion_suite - Comprehensive Live Evaluation Harness for arifOS v45Ω

Full coverage testing for SEA-LION v4 (Qwen 32B IT) with:
- Lane routing (PHATIC/SOFT/HARD/REFUSE)
- Constitutional floors (F1-F9)
- Verdict rendering (SEAL/PARTIAL/VOID/SABAR)
- Ψ lane-scoped enforcement
- REFUSE short-circuit validation
- Identity truth lock
- Claim detection
- Memory gating
- Ledger integrity
- W@W federation (if wired)
- API routes (if available)

Author: arifOS Project
Version: v45Ω Patch B.1
"""

__version__ = "45.0.0-patch-b1"

__all__ = [
    "run_smoke_test",
    "run_core_suite",
    "run_memory_suite",
    "run_ledger_suite",
    "run_api_suite",
    "run_waw_suite",
    "run_all_suites",
]
