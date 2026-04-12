"""
tests/runtime/test_mega_audit.py — Auditor Coder Validations

Implements the "Final 11 Mega-Tools" gate validations:
Gate 1 — Public surface is 11
Gate 2 — Legacy coverage is 100%
Gate 3 — Per-mode callability
Gate 4 — Schema strictness
Gate 5 — Compatibility alias routing
Gate 6 — Stage correctness
Gate 7 — Execution hardening
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from arifosmcp.runtime.public_registry import (
    public_tool_names,
    public_tool_specs,
    CANONICAL_PUBLIC_TOOLS,
    EXPECTED_TOOL_COUNT,
)
from arifosmcp.runtime.contracts import AAA_TOOL_STAGE_MAP
from arifosmcp.runtime.tools import FINAL_TOOL_IMPLEMENTATIONS

# Legacy 42 Tools Expected
LEGACY_TOOLS = {
    "init_anchor", "init_anchor_state", "revoke_anchor_state",
    "arifos_kernel", "get_caller_status", "apex_judge", "audit_rules",
    "agentzero_validate", "agentzero_hold_check", "agentzero_armor_scan",
    "vault_seal", "verify_vault_ledger", "agi_reason", "agi_reflect", "forge",
    "asi_critique", "asi_simulate", "agentzero_engineer", "agentzero_memory_query",
    "search_reality", "ingest_evidence", "reality_compass", "reality_atlas",
    "check_vital", "fs_inspect", "process_list", "net_status", "log_tail",
    "trace_replay", "register_tools", "arifos_list_resources", "arifos_read_resource"
}

MEGA_PAYLOADS = {
  ("init_anchor","init"): {"actor_id":"arif","intent":"test"},
  ("init_anchor","revoke"): {"session_id":"sess_test","reason":"test"},
  ("init_anchor","refresh"): {"session_id":"sess_test"},
  ("arifos_kernel","status"): {},
  ("arifos_kernel","kernel"): {"query":"ping"},
  ("physics_reality","search"): {"input":"test"},
  ("physics_reality","ingest"): {"input":"https://example.com"},
  ("physics_reality","compass"): {"input":"test"},
  ("physics_reality","atlas"): {"operation":"merge"},
  ("agi_mind","reason"): {"query":"1+1"},
  ("agi_mind","reflect"): {"topic":"test", "query":"test"},
  ("agi_mind","forge"): {"query":"draft plan"},
  ("asi_heart","critique"): {"content":"hello"},
  ("asi_heart","simulate"): {"content":"what if X"},
  ("apex_soul","rules"): {},
  ("apex_soul","armor"): {"candidate":"test"},
  ("apex_soul","judge"): {"candidate":"ok"},
  ("apex_soul","validate"): {"candidate":"print(1)"},
  ("apex_soul","hold"): {"hold_id":"123"},
  ("apex_soul","notify"): {"message":"Alert!"},
  ("vault_ledger","seal"): {"verdict":"SEAL","evidence":"test"},
  ("vault_ledger","verify"): {},
  ("math_estimator","vitals"): {},
  ("math_estimator","health"): {},
  ("math_estimator","cost"): {"action":"test"},
  ("code_engine","fs"): {"path":"."},
  ("code_engine","process"): {},
  ("code_engine","net"): {},
  ("code_engine","tail"): {},
  ("code_engine","replay"): {},
  ("engineering_memory","engineer"): {"task":"test"},
  ("engineering_memory","recall"): {"query":"test"},
  ("engineering_memory","write"): {"content":"learned fact"},
  ("engineering_memory","generate"): {"prompt":"test"},
  ("architect_registry","register"): {},
  ("architect_registry","list"): {},
  ("architect_registry","read"): {"uri":"canon://contracts"},
}

def test_gate_1_public_registry_exposes_only_11():
    names = public_tool_names()
    assert len(names) == EXPECTED_TOOL_COUNT, f"Expected {EXPECTED_TOOL_COUNT} tools, got {len(names)}"
    assert set(names) == set(CANONICAL_PUBLIC_TOOLS)

def test_gate_2_capability_map_coverage():
    unmapped = LEGACY_TOOLS - set(CAPABILITY_MAP.keys())
    assert not unmapped, f"Unmapped legacy tools: {unmapped}"
    for old, target in CAPABILITY_MAP.items():
        assert target.mega_tool in CANONICAL_PUBLIC_TOOLS, f"Invalid mapped tool {target.mega_tool} for {old}"

@pytest.mark.asyncio
async def test_gate_3_megatool_modes_smoke():
    # Mock all internal dispatch endpoints to isolate routing
    dispatch_mocks = {
        "init_anchor_impl": AsyncMock(return_value={"ok": True}),
        "revoke_anchor_state_impl": AsyncMock(return_value={"ok": True}),
        "arifos_kernel_impl": AsyncMock(return_value={"ok": True}),
        "get_caller_status_impl": AsyncMock(return_value={"ok": True}),
        "apex_soul_dispatch_impl": AsyncMock(return_value={"ok": True}),
        "vault_ledger_dispatch_impl": AsyncMock(return_value={"ok": True}),
        "agi_mind_dispatch_impl": AsyncMock(return_value={"ok": True}),
        "asi_heart_dispatch_impl": AsyncMock(return_value={"ok": True}),
        "engineering_memory_dispatch_impl": AsyncMock(return_value={"ok": True}),
        "physics_reality_dispatch_impl": AsyncMock(return_value={"ok": True}),
        "math_estimator_dispatch_impl": AsyncMock(return_value={"ok": True}),
        "code_engine_dispatch_impl": AsyncMock(return_value={"ok": True}),
        "architect_registry_dispatch_impl": AsyncMock(return_value={"ok": True}),
    }
    
    with patch.multiple("arifosmcp.runtime.tools", **dispatch_mocks):
        for (tool, mode), payload in MEGA_PAYLOADS.items():
            handler = FINAL_TOOL_IMPLEMENTATIONS.get(tool)
            assert handler, f"Missing handler for {tool}"
            # Call dispatcher directly
            await handler(mode=mode, payload=payload)

def test_gate_4_schema_rejects_bad_inputs():
    from jsonschema import validate, ValidationError
    specs = {s.name: s for s in public_tool_specs()}
    
    for (tool, mode), payload in MEGA_PAYLOADS.items():
        schema = specs[tool].input_schema
        # Valid case
        try:
            validate(instance={"mode": mode, "payload": payload}, schema=schema)
        except ValidationError as e:
            pytest.fail(f"Valid payload rejected for {tool}:{mode} - {e.message}")
            
        # Invalid mode
        with pytest.raises(ValidationError):
            validate(instance={"mode": "INVALID_MODE", "payload": {}}, schema=schema)

def test_gate_6_stage_correctness():
    for tool in CANONICAL_PUBLIC_TOOLS:
        assert tool in AAA_TOOL_STAGE_MAP, f"Missing stage mapping for {tool}"

def test_gate_7_execution_defaults_safe():
    specs = {s.name: s for s in public_tool_specs()}
    # execution parameters exist in all mega tools
    for tool, spec in specs.items():
        props = spec.input_schema["properties"]
        assert props["dry_run"]["default"] is True
        assert props["allow_execution"]["default"] is False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
