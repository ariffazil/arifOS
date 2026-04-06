import json
import sys

from core.enforcement.governance_engine import (
    _calculate_tri_witness_consensus,
    _derive_apex_dials,
    _derive_vitality_index,
    _law13_checks,
    wrap_tool_output,
    "status": "INTACT",
    "message": "Chain OK",
    "path": "VAULT999/vault999.jsonl",
    "session_id": "test",
}
tool = "verify_vault_ledger"

law_checks = _law13_checks(tool, result)
apex_dials = _derive_apex_dials(tool, result)
vitality = _derive_vitality_index(result, law_checks, apex_dials)
tri = _calculate_tri_witness_consensus(tool, result)
failed_required = [k for k, v in law_checks.items() if v.get("required") and not v.get("pass")]

print("Failed required laws:", failed_required)
print("Psi score:", vitality.get("psi"))
print("Tri-witness pass:", tri.get("pass"), "w3:", tri.get("w3"))
print("Tool class:", tri.get("tool_class"), "threshold:", tri.get("threshold"))

env = wrap_tool_output(tool, result)
print("Envelope verdict:", env.get("verdict"))
print("Errors:", json.dumps(env.get("errors"), indent=2))
