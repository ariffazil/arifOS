"""
test_output_formatter_schema.py
Regression test for MCP required fields in format_output().

Tests that all platform branches emit the required schema fields:
  - tool
  - stage
  - status
  - result

Prevents transport-layer schema drift (the root cause of the arifos_init
'tool is a required property' error that Arif encountered).
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class MockEnvelope:
    """Minimal mock of RuntimeEnvelope for schema testing."""

    def __init__(self, tool: str = "arifos_init", ok: bool = True):
        self.canonical_tool_name = tool
        self.tool = tool
        self.platform_context = None
        self.ok = ok
        self.status = "SUCCESS" if ok else "ERROR"
        self.verdict = "SEAL" if ok else "VOID"
        self.stage = "000_INIT"
        self.detail = "test detail"
        self.hint = None
        self.code = None
        self.authority = MockAuthority()
        self.risk_class = MockRiskClass()
        self.trace_id = "test-trace"
        self.trace = {}
        self.handoff = {}
        self.metrics = MockMetrics()
        self.payload = {"test": "payload"}
        self.operator_summary = {}
        self.state = {}
        self.state_origin = {}
        self.transitions = []
        self.diagnostics = {}
        self.verdict_detail = MockVerdictDetail()


class MockAuthority:
    level = MockLevel()
    claim_status = "verified"
    actor_id = "arif"
    approval_scope = []


class MockLevel:
    value = "operator"


class MockRiskClass:
    value = "medium"


class MockMetrics:
    class MockTelemetry:
        G_star = 0.0
        confidence = 0.8

    telemetry = MockTelemetry()
    witness = MockWitness()
    tokens_used = 100


class MockWitness:
    ai = 0.0
    earth = 0.0


class MockVerdictDetail:
    code = None
    message = None


def test_chatgpt_apps_has_tool_field():
    """chatgpt_apps platform must include 'tool' field."""
    from arifosmcp.runtime.output_formatter import format_output

    envelope = MockEnvelope(tool="arifos_init")
    envelope.platform_context = "chatgpt_apps"

    output = format_output(envelope)

    assert "tool" in output, f"Missing 'tool' in output: {output.keys()}"
    assert output["tool"] == "arifos_init", f"Wrong tool value: {output['tool']}"
    print("✅ chatgpt_apps has tool field")


def test_chatgpt_apps_has_status_field():
    """chatgpt_apps platform must include 'status' field."""
    from arifosmcp.runtime.output_formatter import format_output

    envelope = MockEnvelope(tool="arifos_init", ok=True)
    envelope.platform_context = "chatgpt_apps"

    output = format_output(envelope)

    assert "status" in output, f"Missing 'status' in output: {output.keys()}"
    print("✅ chatgpt_apps has status field")


def test_all_required_fields_present():
    """All platforms must emit tool, stage, status, result."""
    from arifosmcp.runtime.output_formatter import format_output

    required = ["tool", "stage", "status", "result"]

    for platform in ["chatgpt_apps", "mcp"]:
        envelope = MockEnvelope(tool="arifos_init")
        envelope.platform_context = platform

        output = format_output(envelope)

        for field in required:
            assert field in output, f"Platform {platform} missing required field '{field}'"

        print(f"✅ Platform '{platform}' has all required fields: {required}")


def test_tool_field_fallback():
    """tool field should use canonical_tool_name, then tool, then 'unknown'."""
    from arifosmcp.runtime.output_formatter import format_output

    envelope = MockEnvelope(tool="arifos_init")
    envelope.canonical_tool_name = None
    envelope.tool = None
    envelope.platform_context = "chatgpt_apps"

    output = format_output(envelope)

    assert "tool" in output
    assert output["tool"] == "unknown", f"Expected 'unknown' fallback, got: {output['tool']}"
    print("✅ tool field fallback to 'unknown' works")


if __name__ == "__main__":
    print("Running output_formatter schema regression tests...\n")

    try:
        test_chatgpt_apps_has_tool_field()
        test_chatgpt_apps_has_status_field()
        test_all_required_fields_present()
        test_tool_field_fallback()
        print("\n✅ All tests passed — no schema drift detected.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
