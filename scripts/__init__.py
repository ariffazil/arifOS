"""
arifOS Scripts Package

Command-line utilities and diagnostic tools for arifOS governance kernel.

Modules:
  - analyze_governance: Telemetry analyzer for cooling ledger
  - verify_ledger_chain: Ledger integrity verification
  - propose_canon_from_receipt: 888 Judge tool for canon proposals
  - seal_proposed_canon: Phoenix-72 SEAL tool for canon finalization
  - build_ledger_hashes: SHA-256 hash chain rebuilder
  - compute_merkle_root: Merkle root computation
  - show_merkle_proof: Merkle proof display utility
  - verify_v36_stub: v36Ω cooling ledger stub verification
  - torture_test_truth_polarity: Truth polarity red-team tests
  - test_waw_signals: W@W federation signal probe
  - arifos_caged_llm_demo: Vanilla vs governed LLM harness
  - arifos_caged_llm_zkpc_demo: Full pipeline with zkPC receipt
  - eval_telemetry_harness: Core vs eval telemetry comparison

For usage, see README_TELEMETRY.md in this directory.

License: Apache-2.0
"""

__version__ = "36.3.0"
__all__ = [
    "analyze_governance",
    "verify_ledger_chain",
    "propose_canon_from_receipt",
    "seal_proposed_canon",
    "build_ledger_hashes",
    "compute_merkle_root",
    "show_merkle_proof",
]
