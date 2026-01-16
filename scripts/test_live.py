from arifos_core.mcp.unified_server import JudgeRequest, arifos_judge

print("Testing arifOS Governance Pipeline...")
try:
    # Test a simple query that triggers the pipeline
    req = JudgeRequest(query="Search for Constitution in CCC")
    result = arifos_judge(req)
    print("\n✅ SUCCESS: Governance Pipeline Active")
    print(f"Verdict: {result.get('verdict')}")
except Exception as e:
    print(f"\n❌ FAIL: {e}")
