#!/usr/bin/env python3
"""Test MCP tool imports to find which one fails"""
import sys
import traceback

print("Testing MCP tool imports...")

tools_to_test = [
    ("mcp_111_sense", "from arifos.core.mcp.tools.mcp_111_sense import mcp_111_sense"),
    ("mcp_222_reflect", "from arifos.core.mcp.tools.mcp_222_reflect import mcp_222_reflect"),
    ("sequential", "from arifos.core.mcp.tools.sequential import SequentialThinking"),
    ("recall", "from arifos.core.mcp.tools.recall import arifos_recall"),
    ("codex_skills", "from arifos.core.mcp.tools.codex_skills import CodexConstitutionalSkills"),
    ("executor", "from arifos.core.mcp.tools.executor import arifos_executor"),
    ("mcp_555_empathize", "from arifos.core.mcp.tools.mcp_555_empathize import mcp_555_empathize"),
    ("mcp_666_align", "from arifos.core.mcp.tools.mcp_666_align import mcp_666_align"),
    ("validate_full", "from arifos.core.mcp.tools.validate_full import arifos_validate_full"),
    ("meta_select", "from arifos.core.mcp.tools.meta_select import arifos_meta_select"),
    ("fag_list", "from arifos.core.mcp.tools.fag_list import arifos_fag_list"),
    ("fag_read", "from arifos.core.mcp.tools.fag_read import arifos_fag_read"),
    ("fag_stats", "from arifos.core.mcp.tools.fag_stats import arifos_fag_stats"),
    ("fag_write", "from arifos.core.mcp.tools.fag_write import arifos_fag_write"),
    ("tempa_list", "from arifos.core.mcp.tools.tempa_list import fag_list"),
    ("tempa_read", "from arifos.core.mcp.tools.tempa_read import tempa_read"),
    ("tempa_stats", "from arifos.core.mcp.tools.tempa_stats import fag_stats"),
    ("tempa_write", "from arifos.core.mcp.tools.tempa_write import fag_write"),
    ("mcp_444_evidence", "from arifos.core.mcp.tools.mcp_444_evidence import mcp_444_evidence"),
    ("mcp_777_forge", "from arifos.core.mcp.tools.mcp_777_forge import mcp_777_forge"),
    ("mcp_888_judge", "from arifos.core.mcp.tools.mcp_888_judge import mcp_888_judge"),
    ("judge", "from arifos.core.mcp.tools.judge import arifos_judge"),
    ("audit", "from arifos.core.mcp.tools.audit import arifos_audit"),
    ("apex_llama", "from arifos.core.mcp.tools.apex_llama import apex_llama"),
    ("mcp_889_proof", "from arifos.core.mcp.tools.mcp_889_proof import mcp_889_proof"),
    ("mcp_000_gate", "from arifos.core.mcp.tools.mcp_000_gate import mcp_000_gate"),
    ("mcp_000_reset", "from arifos.core.mcp.tools.mcp_000_reset import mcp_000_reset"),
    ("mcp_999_seal", "from arifos.core.mcp.tools.mcp_999_seal import mcp_999_seal"),
    ("memory_vault", "from arifos.core.mcp.tools.memory_vault import memory_get_vault"),
    ("memory_phoenix", "from arifos.core.mcp.tools.memory_phoenix import memory_list_phoenix"),
    ("memory_propose", "from arifos.core.mcp.tools.memory_propose import memory_propose_entry"),
]

failed_imports = []

for name, import_statement in tools_to_test:
    try:
        exec(import_statement)
        print(f"OK {name}")
    except Exception as e:
        print(f"FAIL {name}: {type(e).__name__}: {str(e)}")
        failed_imports.append((name, e))
        traceback.print_exc()

if failed_imports:
    print(f"\n{len(failed_imports)} imports failed!")
    sys.exit(1)
else:
    print("\nAll imports successful!")
    sys.exit(0)
