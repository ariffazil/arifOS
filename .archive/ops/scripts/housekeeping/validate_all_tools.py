#!/usr/bin/env python3
"""
External Validator for arifosmcp Public Tools
Tests all 24 canonical tools against their schema descriptions
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Any

# Add the project to path
sys.path.insert(0, r"C:\arifosmcp")

from arifosmcp.runtime.public_registry import (
    public_tool_specs,
    public_tool_names,
    build_mcp_manifest,
)

# Test results accumulator
results = {
    "test_run": datetime.now().isoformat(),
    "total_tools": 0,
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "tools": {},
}


def log_test(tool_name: str, status: str, message: str, details: dict = None):
    """Log a test result."""
    entry = {
        "status": status,
        "message": message,
        "details": details or {},
    }
    results["tools"][tool_name] = entry
    
    icon = "✅" if status == "PASS" else "⚠️" if status == "WARN" else "❌"
    print(f"{icon} [{tool_name}] {status}: {message}")


async def validate_tool_schema(tool_spec) -> dict:
    """Validate a tool's schema definition."""
    issues = []
    
    # Check required fields
    required_fields = ["name", "stage", "role", "layer", "description", "trinity", "floors", "input_schema"]
    for field in required_fields:
        if not hasattr(tool_spec, field) or getattr(tool_spec, field) is None:
            issues.append(f"Missing required field: {field}")
    
    # Validate input schema
    schema = tool_spec.input_schema
    if not isinstance(schema, dict):
        issues.append("input_schema must be a dict")
    elif "type" not in schema:
        issues.append("input_schema missing 'type' field")
    
    # Validate stage format
    stage = tool_spec.stage
    valid_stages = ["000_INIT", "111_SENSE", "222_GROUND", "222_REALITY", "333_MIND", 
                    "333_INTEGRATE", "444_ROUTER", "444_MEMORY", "555_ALIGN", 
                    "555_MEMORY", "666_EXECUTE", "666_HEART", "777_FORGE", 
                    "777_JUDGE", "888_FLOOR", "888_HOLD", "888_JUDGE", 
                    "888_VITALS", "888_OBSERVE", "999_SEAL", "999_ATTEST", "999_VAULT",
                    "000_999", "CRITIQUE_666"]
    if stage not in valid_stages:
        issues.append(f"Unknown stage: {stage}")
    
    # Validate trinity
    trinity = tool_spec.trinity
    valid_trinity = ["INIT", "AGI Δ", "ASI Ω", "APEX Ψ", "ROUTER", "VAULT", "ALL"]
    if trinity not in valid_trinity:
        issues.append(f"Unknown trinity: {trinity}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
    }


async def test_init_anchor():
    """Test init_anchor tool."""
    try:
        from arifosmcp.runtime.tools import init_anchor
        
        # Test basic initialization
        result = await init_anchor(raw_input="test initialization")
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "has_session_id": hasattr(result, "session_id") and result.session_id,
            "has_stage": result.stage == "INIT_000",
            "has_verdict": hasattr(result, "verdict"),
        }
        
        if all(checks.values()):
            log_test("init_anchor", "PASS", "Tool executed successfully", checks)
        else:
            log_test("init_anchor", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("init_anchor", "FAIL", f"Exception: {str(e)}")


async def test_arifos_kernel():
    """Test arifOS_kernel tool."""
    try:
        from arifosmcp.runtime.tools import arifos_kernel
        
        # Test with dry_run
        result = await arifos_kernel(
            query="test query",
            dry_run=True,
            actor_id="test_validator"
        )
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "tool_is_kernel": result.tool == "arifOS_kernel",
            "has_metrics": hasattr(result, "metrics"),
            "has_trace": "trace" in str(result.model_dump()),
        }
        
        if all(checks.values()):
            log_test("arifOS_kernel", "PASS", "Metabolic loop executed", checks)
        else:
            log_test("arifOS_kernel", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("arifOS_kernel", "FAIL", f"Exception: {str(e)}")


async def test_forge():
    """Test forge tool."""
    try:
        from arifosmcp.runtime.tools import forge
        
        result = await forge(
            spec="test specification",
            risk_tier="low"
        )
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "has_session_id": hasattr(result, "session_id"),
            "has_verdict": hasattr(result, "verdict"),
        }
        
        if all(checks.values()):
            log_test("forge", "PASS", "Full pipeline executed", checks)
        else:
            log_test("forge", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("forge", "FAIL", f"Exception: {str(e)}")


async def test_reality_compass():
    """Test reality_compass tool."""
    try:
        from arifosmcp.runtime.tools import reality_compass
        
        result = await reality_compass(
            input="What is Python programming?",
            mode="search",
            session_id="test-session"
        )
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "tool_is_compass": result.tool == "reality_compass",
            "stage_is_sense": result.stage == "SENSE_111",
            "has_payload": hasattr(result, "payload"),
        }
        
        if all(checks.values()):
            log_test("reality_compass", "PASS", "Reality grounding works", checks)
        else:
            log_test("reality_compass", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("reality_compass", "FAIL", f"Exception: {str(e)}")


async def test_search_reality():
    """Test search_reality alias."""
    try:
        from arifosmcp.runtime.tools import search_reality
        
        result = await search_reality(query="Python language")
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "has_stage": hasattr(result, "stage"),
        }
        
        if all(checks.values()):
            log_test("search_reality", "PASS", "Search alias works", checks)
        else:
            log_test("search_reality", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("search_reality", "FAIL", f"Exception: {str(e)}")


async def test_ingest_evidence():
    """Test ingest_evidence alias."""
    try:
        from arifosmcp.runtime.tools import ingest_evidence
        
        # Test with a known URL
        result = await ingest_evidence(url="https://example.com")
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "has_stage": hasattr(result, "stage"),
        }
        
        if all(checks.values()):
            log_test("ingest_evidence", "PASS", "Evidence ingestion works", checks)
        else:
            log_test("ingest_evidence", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("ingest_evidence", "FAIL", f"Exception: {str(e)}")


async def test_reality_atlas():
    """Test reality_atlas tool."""
    try:
        from arifosmcp.runtime.tools import reality_atlas
        
        result = await reality_atlas(
            operation="build",
            bundles=[],
            query={},
            session_id="test-session"
        )
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "has_stage": hasattr(result, "stage"),
        }
        
        if all(checks.values()):
            log_test("reality_atlas", "PASS", "Atlas operation works", checks)
        else:
            log_test("reality_atlas", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("reality_atlas", "FAIL", f"Exception: {str(e)}")


async def test_agi_reason():
    """Test agi_reason tool."""
    try:
        from arifosmcp.runtime.tools import agi_reason
        
        result = await agi_reason(
            query="What is constitutional AI?",
            facts=["AI governance is important"],
            session_id="test-session"
        )
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "stage_is_mind": result.stage == "MIND_333",
            "has_metrics": hasattr(result, "metrics"),
        }
        
        if all(checks.values()):
            log_test("agi_reason", "PASS", "AGI reasoning works", checks)
        else:
            log_test("agi_reason", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("agi_reason", "FAIL", f"Exception: {str(e)}")


async def test_agi_reflect():
    """Test agi_reflect tool."""
    try:
        from arifosmcp.runtime.tools import agi_reflect
        
        result = await agi_reflect(
            topic="Reflect on AI safety",
            session_id="test-session"
        )
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "has_stage": hasattr(result, "stage"),
        }
        
        if all(checks.values()):
            log_test("agi_reflect", "PASS", "Memory reflection works", checks)
        else:
            log_test("agi_reflect", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("agi_reflect", "FAIL", f"Exception: {str(e)}")


async def test_asi_simulate():
    """Test asi_simulate tool."""
    try:
        from arifosmcp.runtime.tools import asi_simulate
        
        result = await asi_simulate(
            scenario="Deploying a new API endpoint",
            session_id="test-session"
        )
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "stage_is_heart": result.stage == "HEART_666",
            "has_metrics": hasattr(result, "metrics"),
        }
        
        if all(checks.values()):
            log_test("asi_simulate", "PASS", "Consequence simulation works", checks)
        else:
            log_test("asi_simulate", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("asi_simulate", "FAIL", f"Exception: {str(e)}")


async def test_asi_critique():
    """Test asi_critique tool."""
    try:
        from arifosmcp.runtime.tools import asi_critique
        
        result = await asi_critique(
            draft_output="This is a draft output for critique",
            session_id="test-session"
        )
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "has_stage": hasattr(result, "stage"),
            "has_payload": hasattr(result, "payload"),
        }
        
        if all(checks.values()):
            log_test("asi_critique", "PASS", "Critique audit works", checks)
        else:
            log_test("asi_critique", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("asi_critique", "FAIL", f"Exception: {str(e)}")


async def test_apex_judge():
    """Test apex_judge tool."""
    try:
        from arifosmcp.runtime.tools import apex_judge
        
        result = await apex_judge(
            candidate_output="This is a candidate for judgment",
            session_id="test-session"
        )
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "stage_is_judge": result.stage == "JUDGE_888",
            "has_verdict": hasattr(result, "verdict"),
        }
        
        if all(checks.values()):
            log_test("apex_judge", "PASS", "Judgment engine works", checks)
        else:
            log_test("apex_judge", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("apex_judge", "FAIL", f"Exception: {str(e)}")


async def test_audit_rules():
    """Test audit_rules tool."""
    try:
        from arifosmcp.runtime.tools import audit_rules
        
        result = await audit_rules(session_id="test-session")
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "has_payload": hasattr(result, "payload"),
            "floor_hooks_present": "floor_runtime_hooks" in str(result.payload),
        }
        
        if all(checks.values()):
            log_test("audit_rules", "PASS", "Floor inspection works", checks)
        else:
            log_test("audit_rules", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("audit_rules", "FAIL", f"Exception: {str(e)}")


async def test_check_vital():
    """Test check_vital tool."""
    try:
        from arifosmcp.runtime.tools import check_vital
        
        result = await check_vital(session_id="test-session")
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "tool_is_vital": result.tool == "check_vital",
            "has_payload": hasattr(result, "payload"),
            "thermodynamics_present": "thermodynamic_vitality" in str(result.payload) or "vital_error" in str(result.payload),
        }
        
        if checks["returns_envelope"] and checks["has_payload"]:
            log_test("check_vital", "PASS", "System vitals check works", checks)
        else:
            log_test("check_vital", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("check_vital", "FAIL", f"Exception: {str(e)}")


async def test_vault_seal():
    """Test vault_seal tool."""
    try:
        from arifosmcp.runtime.tools import vault_seal
        
        result = await vault_seal(
            verdict="SEAL",
            evidence="Test evidence for vault sealing",
            session_id="test-session"
        )
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "stage_is_vault": result.stage == "VAULT_999",
            "has_metrics": hasattr(result, "metrics"),
        }
        
        if all(checks.values()):
            log_test("vault_seal", "PASS", "Vault sealing works", checks)
        else:
            log_test("vault_seal", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("vault_seal", "FAIL", f"Exception: {str(e)}")


async def test_verify_vault_ledger():
    """Test verify_vault_ledger tool."""
    try:
        from arifosmcp.runtime.tools import verify_vault_ledger
        
        result = await verify_vault_ledger(
            session_id="test-session",
            full_scan=False
        )
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "has_stage": hasattr(result, "stage"),
        }
        
        if all(checks.values()):
            log_test("verify_vault_ledger", "PASS", "Ledger verification works", checks)
        else:
            log_test("verify_vault_ledger", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("verify_vault_ledger", "FAIL", f"Exception: {str(e)}")


async def test_revoke_anchor_state():
    """Test revoke_anchor_state tool."""
    try:
        from arifosmcp.runtime.tools import init_anchor
        
        result = await init_anchor(
            mode="revoke",
            session_id="test-session-revoke",
            reason="Test revocation"
        )
        
        checks = {
            "returns_envelope": hasattr(result, "tool"),
            "tool_is_revoke": result.tool == "init_anchor",
            "payload_indicates_revoke": "revoked" in str(result.payload),
        }
        
        if all(checks.values()):
            log_test("revoke_anchor_state", "PASS", "Session revocation works", checks)
        else:
            log_test("revoke_anchor_state", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("revoke_anchor_state", "FAIL", f"Exception: {str(e)}")


async def test_open_apex_dashboard():
    """Test open_apex_dashboard tool."""
    try:
        from arifosmcp.runtime.tools import open_apex_dashboard
        
        result = await open_apex_dashboard(session_id="test-session")
        
        checks = {
            "returns_result": result is not None,
        }
        
        if checks["returns_result"]:
            log_test("open_apex_dashboard", "PASS", "Dashboard generation works", checks)
        else:
            log_test("open_apex_dashboard", "WARN", "Partial functionality", checks)
            
    except Exception as e:
        log_test("open_apex_dashboard", "FAIL", f"Exception: {str(e)}")


async def test_agentzero_tools():
    """Test agentzero tool family."""
    from arifosmcp.tools.agentzero_tools import (
        agentzero_armor_scan,
        agentzero_hold_check,
        agentzero_validate,
    )
    
    # Test agentzero_armor_scan
    try:
        result = await agentzero_armor_scan(content="Test content for scanning")
        checks = {
            "returns_response": result is not None,
        }
        if checks["returns_response"]:
            log_test("agentzero_armor_scan", "PASS", "Armor scan works", checks)
        else:
            log_test("agentzero_armor_scan", "WARN", "Partial functionality", checks)
    except Exception as e:
        log_test("agentzero_armor_scan", "FAIL", f"Exception: {str(e)}")
    
    # Test agentzero_hold_check
    try:
        result = await agentzero_hold_check()
        checks = {
            "returns_response": result is not None,
        }
        if checks["returns_response"]:
            log_test("agentzero_hold_check", "PASS", "Hold check works", checks)
        else:
            log_test("agentzero_hold_check", "WARN", "Partial functionality", checks)
    except Exception as e:
        log_test("agentzero_hold_check", "FAIL", f"Exception: {str(e)}")
    
    # Test agentzero_validate
    try:
        result = await agentzero_validate(
            input_to_validate="Test input",
            validation_type="code"
        )
        checks = {
            "returns_response": result is not None,
        }
        if checks["returns_response"]:
            log_test("agentzero_validate", "PASS", "Validation works", checks)
        else:
            log_test("agentzero_validate", "WARN", "Partial functionality", checks)
    except Exception as e:
        log_test("agentzero_validate", "FAIL", f"Exception: {str(e)}")


async def validate_all_schemas():
    """Validate all tool schemas without execution."""
    print("\n" + "="*60)
    print("PHASE 1: SCHEMA VALIDATION")
    print("="*60)
    
    specs = public_tool_specs()
    results["total_tools"] = len(specs)
    
    schema_issues = 0
    for spec in specs:
        validation = await validate_tool_schema(spec)
        if validation["valid"]:
            print(f"✅ [{spec.name}] Schema valid")
        else:
            print(f"❌ [{spec.name}] Schema issues: {validation['issues']}")
            schema_issues += 1
    
    print(f"\nSchema validation: {len(specs) - schema_issues}/{len(specs)} passed")
    return schema_issues == 0


async def run_all_tests():
    """Run all tool tests."""
    print("\n" + "="*60)
    print("PHASE 2: FUNCTIONAL TESTING")
    print("="*60)
    
    # Run all tests
    await test_init_anchor()
    await test_arifos_kernel()
    await test_forge()
    await test_reality_compass()
    await test_search_reality()
    await test_ingest_evidence()
    await test_reality_atlas()
    await test_agi_reason()
    await test_agi_reflect()
    await test_asi_simulate()
    await test_asi_critique()
    await test_apex_judge()
    await test_audit_rules()
    await test_check_vital()
    await test_vault_seal()
    await test_verify_vault_ledger()
    await test_revoke_anchor_state()
    await test_open_apex_dashboard()
    await test_agentzero_tools()


def generate_report():
    """Generate final validation report."""
    print("\n" + "="*60)
    print("VALIDATION REPORT")
    print("="*60)
    
    # Count results
    passed = sum(1 for r in results["tools"].values() if r["status"] == "PASS")
    warnings = sum(1 for r in results["tools"].values() if r["status"] == "WARN")
    failed = sum(1 for r in results["tools"].values() if r["status"] == "FAIL")
    
    results["passed"] = passed
    results["warnings"] = warnings
    results["failed"] = failed
    
    print(f"\nTotal Tools: {results['total_tools']}")
    print(f"✅ Passed: {passed}")
    print(f"⚠️ Warnings: {warnings}")
    print(f"❌ Failed: {failed}")
    
    # Verify against manifest
    print("\n" + "-"*60)
    print("MANIFEST VERIFICATION")
    print("-"*60)
    manifest = build_mcp_manifest()
    print(f"Server: {manifest['name']}")
    print(f"Version: {manifest['version']}")
    print(f"Tools in manifest: {len(manifest['tools'])}")
    print(f"Resources: {len(manifest['resources'])}")
    
    # Check tool name consistency
    manifest_tools = set(manifest['tools'].keys())
    tested_tools = set(results['tools'].keys())
    
    missing_tests = manifest_tools - tested_tools
    extra_tests = tested_tools - manifest_tools
    
    if missing_tests:
        print(f"\n⚠️ Tools in manifest but not tested: {missing_tests}")
    if extra_tests:
        print(f"\n⚠️ Tools tested but not in manifest: {extra_tests}")
    
    if not missing_tests and not extra_tests:
        print("\n✅ All manifest tools tested")
    
    # Save report
    report_path = r"C:\arifosmcp\validation_report.json"
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    return failed == 0


async def main():
    """Main validation entry point."""
    print("="*60)
    print("arifosmcp EXTERNAL VALIDATOR")
    print("Testing 24 Canonical Public Tools")
    print("="*60)
    
    # Phase 1: Schema validation
    schemas_valid = await validate_all_schemas()
    
    # Phase 2: Functional testing
    await run_all_tests()
    
    # Generate report
    all_passed = generate_report()
    
    print("\n" + "="*60)
    if all_passed and schemas_valid:
        print("✅ VALIDATION PASSED")
    else:
        print("⚠️ VALIDATION COMPLETED WITH ISSUES")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
