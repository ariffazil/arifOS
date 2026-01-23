# File Reorganization Migration Plan

**Date:** 2025-12-26
**Goal:** Move scattered demo and SEA-LION files from `scripts/` to proper architectural layers

---

## Current State: 51 files in scripts/

### ✅ Files Staying in scripts/ (Governance Utilities - 8 files)

```
scripts/trinity.py                    # Git governance
scripts/phoenix_72_guardrail.py       # Constitutional drift detector
scripts/diagnose_v45_patches.py       # Diagnostic tool
scripts/analyze_governance.py         # Audit analyzer
scripts/analyze_audit_trail.py        # Ledger analyzer
scripts/verify_ledger_chain.py        # Hash-chain verifier
scripts/verify_ledger_kms.py          # KMS verifier
scripts/arifos_mcp_entry.py          # MCP server entry point
```

### 🔄 SEA-LION Files Moving to L6_SEALION/tests/ (7 files)

```
scripts/demo_sealion_v45_full.py       → L6_SEALION/tests/demo_sealion_v45_full.py
scripts/sealion_full_suite_v45.py      → L6_SEALION/tests/sealion_full_suite_v45.py
scripts/test_sealion_baseline.py       → L6_SEALION/tests/test_sealion_baseline.py
scripts/test_sealion_governed.py       → L6_SEALION/tests/test_sealion_governed.py
scripts/test_sealion_litellm.py        → L6_SEALION/tests/test_sealion_litellm.py
scripts/test_sealion_v4_comparison.py  → L6_SEALION/tests/test_sealion_v4_comparison.py
scripts/verify_sealion_sovereignty.py  → L6_SEALION/tests/verify_sealion_sovereignty.py
```

### 🔄 Demo Files Moving to L7_DEMOS/examples/ (9 files)

```
scripts/arifos_caged_gemini_demo.py    → L7_DEMOS/examples/demo_caged_gemini.py
scripts/arifos_caged_llm_demo.py       → L7_DEMOS/examples/demo_caged_llm.py
scripts/arifos_caged_llm_zkpc_demo.py  → L7_DEMOS/examples/demo_caged_llm_zkpc.py
scripts/arifos_caged_openai_demo.py    → L7_DEMOS/examples/demo_caged_openai.py
scripts/test_bogel_llama.py            → L7_DEMOS/examples/test_bogel_llama.py
scripts/test_gemini_breaking_point.py  → L7_DEMOS/examples/test_gemini_breaking_point.py
scripts/test_ollama_v37.py             → L7_DEMOS/examples/test_ollama_v37.py
scripts/test_waw_signals.py            → L7_DEMOS/examples/test_waw_signals.py
scripts/torture_test_truth_polarity.py → L7_DEMOS/examples/torture_test_truth_polarity.py
```

### ⚠️ Files to Review Separately (NOT moving in this batch)

```
scripts/test_acceptance_v45_patch_b1.py  # Acceptance test - may belong in tests/
scripts/test_mcp_server.py               # MCP test - may belong in arifos_core/mcp/tests/
```

---

## After Migration: scripts/ will have ~8-10 files

**Reduction:** 51 files → 10 files (80% reduction)

---

## Import Updates Required

After moving, these imports may break:
- Any script that imports from moved files
- Any test that references moved files by path

**Strategy:**
1. Move files using `git mv` to preserve history
2. Grep for imports referencing moved files
3. Update import paths where necessary
4. Run test suite to verify

---

## Execution Steps

1. Create target directories if needed
2. Move SEA-LION files (7 files)
3. Move demo files (9 files)
4. Search for broken imports
5. Fix broken imports
6. Run tests
7. Generate final report

---

**DITEMPA BUKAN DIBERI** — Architectural clarity through proper layering.
