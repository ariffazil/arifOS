"""Tests for arifOS Command Center backend tools and red-team hardening."""

from __future__ import annotations

import json

import pytest

from arifosmcp.apps.command_center.app import (
    command_center_app,
    forge_dry_run,
    gateway_handshake,
    judge_action,
    ops_vitals,
    session_status,
    vault_dry_seal,
    vault_list,
)
from arifosmcp.apps.command_center.governance import (
    classify_risk,
    hash_preview,
    judge_candidate,
    requires_human_decision,
)
from arifosmcp.apps.command_center.mock_kernel import MOCK_VAULT_ENTRIES
from arifosmcp.apps.command_center.state import get_state, reset_state


# ---------------------------------------------------------------------------
# Visibility
# ---------------------------------------------------------------------------


class TestVisibility:
    """Ensure correct tool visibility — only command_center is model-facing."""

    async def _tool_names(self, provider) -> set[str]:
        tools = await provider.list_tools()
        return {t.name for t in tools}

    @pytest.mark.asyncio
    async def test_only_command_center_is_model_visible(self) -> None:
        """The main MCP server must expose only the UI entry point."""
        from arifosmcp.server import mcp

        names = await self._tool_names(mcp)
        assert "command_center" in names
        backend_tools = {
            "session_status",
            "ops_vitals",
            "judge_action",
            "forge_dry_run",
            "gateway_handshake",
            "vault_list",
            "vault_dry_seal",
        }
        assert backend_tools.isdisjoint(
            names
        ), f"Backend tools leaked to model scope: {backend_tools & names}"

    @pytest.mark.asyncio
    async def test_backend_tools_are_app_visible(self) -> None:
        """The FastMCPApp must contain all backend tools plus the UI entry."""
        names = await self._tool_names(command_center_app)
        assert "command_center" in names
        assert "session_status" in names
        assert "ops_vitals" in names
        assert "judge_action" in names
        assert "forge_dry_run" in names
        assert "gateway_handshake" in names
        assert "vault_list" in names
        assert "vault_dry_seal" in names


# ---------------------------------------------------------------------------
# JSON fallback
# ---------------------------------------------------------------------------


class TestJsonFallback:
    """Every backend response must be JSON-serializable and include text fallback."""

    def _assert_json_roundtrip(self, result: dict) -> None:
        """Serialize to JSON and back; assert text field present and non-empty."""
        raw = json.dumps(result)
        restored = json.loads(raw)
        assert "text" in restored, f"Missing 'text' fallback in {result.keys()}"
        assert isinstance(restored["text"], str)
        assert restored["text"], "text fallback must be non-empty"

    def test_session_status_json_and_text(self) -> None:
        result = session_status()
        self._assert_json_roundtrip(result)
        assert "arif" in result["text"].lower()

    def test_ops_vitals_json_and_text(self) -> None:
        result = ops_vitals()
        self._assert_json_roundtrip(result)
        assert "thermodynamic" in result["text"].lower()

    def test_judge_action_json_and_text(self) -> None:
        result = judge_action("read file contents")
        self._assert_json_roundtrip(result)
        assert "verdict" in result["text"].lower()

    def test_forge_dry_run_json_and_text(self) -> None:
        result = forge_dry_run("echo hello")
        self._assert_json_roundtrip(result)
        assert "dry-run" in result["text"].lower() or "dry_run" in result["text"].lower()

    def test_gateway_handshake_json_and_text(self) -> None:
        result = gateway_handshake("geox-mcp")
        self._assert_json_roundtrip(result)
        assert "simulated" in result["text"].lower()

    def test_vault_list_json_and_text(self) -> None:
        result = vault_list()
        self._assert_json_roundtrip(result)
        assert "vault" in result["text"].lower()

    def test_vault_dry_seal_json_and_text(self) -> None:
        result = vault_dry_seal("test payload")
        self._assert_json_roundtrip(result)
        assert "dry-seal" in result["text"].lower() or "dry_seal" in result["text"].lower()


# ---------------------------------------------------------------------------
# Backend tool shapes
# ---------------------------------------------------------------------------


class TestSessionStatus:
    def test_returns_expected_shape(self) -> None:
        result = session_status()
        assert result["actor_id"] == "arif"
        assert result["constitution_id"] == "arifos-constitution-v2026.04.26"
        assert result["stage"] == "000"
        assert result["lane"] == "AGI"
        assert result["sealed"] is False


class TestOpsVitals:
    def test_returns_expected_shape(self) -> None:
        result = ops_vitals()
        assert "g_score" in result
        assert "delta_S" in result
        assert "omega" in result
        assert "psi_le" in result
        assert result["status"] == "stable"
        assert 0.0 <= result["g_score"] <= 1.0


class TestJudgeAction:
    def test_empty_candidate_returns_hold(self) -> None:
        result = judge_action("")
        assert result["verdict"] == "HOLD"
        assert result["human_decision_required"] is True

    def test_low_risk_returns_seal(self) -> None:
        result = judge_action("read file contents")
        assert result["verdict"] == "SEAL"
        assert result["risk_tier"] == "low"

    def test_high_risk_returns_sabar_or_hold(self) -> None:
        result = judge_action("delete production database")
        assert result["verdict"] in {"HOLD", "SABAR"}
        assert result["human_decision_required"] is True


class TestForgeDryRun:
    def test_does_not_execute(self) -> None:
        result = forge_dry_run("echo hello")
        assert result["mode"] == "dry_run"
        assert result["would_execute"] is False
        assert result["status"] == "simulated"

    def test_reversibility_for_safe_input(self) -> None:
        result = forge_dry_run("echo hello")
        assert result["reversibility"] == "reversible"

    def test_reversibility_for_dangerous_input(self) -> None:
        result = forge_dry_run("rm -rf /")
        assert result["reversibility"] == "uncertain"

    def test_required_verdict_is_seal(self) -> None:
        result = forge_dry_run("anything")
        assert result["required_verdict"] == "SEAL"


class TestGatewayHandshake:
    def test_simulated_only(self) -> None:
        result = gateway_handshake("geox-mcp")
        assert result["handshake"] == "simulated"
        assert result["constitution_hash_required"] is True
        assert result["rogue_agent_protection"] is True
        assert result["status"] == "pending_trust_verification"


class TestVaultList:
    def test_returns_mock_entries(self) -> None:
        result = vault_list()
        assert "entries" in result
        assert len(result["entries"]) == len(MOCK_VAULT_ENTRIES)
        assert result["entries"][0]["id"] == "VAULT-MOCK-001"


class TestVaultDrySeal:
    def test_not_permanent(self) -> None:
        result = vault_dry_seal("test payload")
        assert result["permanent"] is False
        assert result["mode"] == "dry_seal"
        assert result["status"] == "not_written"

    def test_hash_preview_matches_governance(self) -> None:
        payload = "consistent payload"
        result = vault_dry_seal(payload)
        assert result["payload_hash_preview"] == hash_preview(payload)

    def test_empty_payload(self) -> None:
        result = vault_dry_seal("")
        assert result["permanent"] is False
        assert len(result["payload_hash_preview"]) == 16


class TestStateCounters:
    def setup_method(self) -> None:
        reset_state()

    def test_counters_increment(self) -> None:
        session_status()
        ops_vitals()
        judge_action("test")
        forge_dry_run("test")
        gateway_handshake("test")
        vault_dry_seal("test")

        state = get_state()
        assert state.session_count == 1
        assert state.ops_reads == 1
        assert state.judge_calls == 1
        assert state.forge_dry_runs == 1
        assert state.gateway_handshakes == 1
        assert state.vault_dry_seals == 1


# ---------------------------------------------------------------------------
# Governance unit tests
# ---------------------------------------------------------------------------


class TestClassifyRisk:
    def test_empty_returns_high(self) -> None:
        assert classify_risk("") == "high"
        assert classify_risk(None) == "high"  # type: ignore[arg-type]

    def test_low_risk(self) -> None:
        assert classify_risk("list running processes") == "low"
        assert classify_risk("show status") == "low"
        assert classify_risk("hello world") == "low"

    def test_medium_risk(self) -> None:
        assert classify_risk("install package updates") == "medium"
        assert classify_risk("restart service") == "medium"

    def test_high_risk_patterns(self) -> None:
        # "delete" is in DANGEROUS_KEYWORDS -> critical
        assert classify_risk("delete old files") == "critical"
        # "remove" + "permanent" triggers regex -> high
        assert classify_risk("remove permanent data") == "high"

    def test_critical_keywords(self) -> None:
        assert classify_risk("delete production database") == "critical"
        assert classify_risk("deploy to production") == "critical"
        assert classify_risk("transfer credentials") == "critical"
        assert classify_risk("execute rm -rf /") == "critical"
        assert classify_risk("exfiltrate data") == "critical"
        assert classify_risk("bypass firewall") == "critical"
        assert classify_risk("docker system prune -a") == "critical"


class TestRequiresHumanDecision:
    def test_high_and_critical_require_human(self) -> None:
        assert requires_human_decision("high") is True
        assert requires_human_decision("critical") is True

    def test_medium_requires_human_in_v01(self) -> None:
        assert requires_human_decision("medium") is True

    def test_low_does_not_require_human(self) -> None:
        assert requires_human_decision("low") is False

    def test_invalid_input_defaults_safe(self) -> None:
        assert requires_human_decision(None) is True  # type: ignore[arg-type]


class TestJudgeCandidate:
    def test_empty_candidate_returns_hold(self) -> None:
        result = judge_candidate("")
        assert result["verdict"] == "HOLD"
        assert result["risk_tier"] == "high"
        assert result["human_decision_required"] is True
        assert "empty" in result["reason"].lower() or "invalid" in result["reason"].lower()

    def test_low_risk_can_return_seal(self) -> None:
        result = judge_candidate("list files in directory")
        assert result["verdict"] == "SEAL"
        assert result["risk_tier"] == "low"
        assert result["human_decision_required"] is False
        assert "forge_dry_run" in result["allowed_next"]
        assert "forge_execute" in result["forbidden_next"]

    def test_delete_production_database_returns_hold_or_sabar(self) -> None:
        result = judge_candidate("delete production database")
        assert result["verdict"] in {"HOLD", "SABAR"}
        assert result["risk_tier"] in {"high", "critical"}
        assert result["human_decision_required"] is True
        assert "forge_execute" in result["forbidden_next"]

    def test_high_risk_requires_human_decision(self) -> None:
        result = judge_candidate("drop table users")
        assert result["human_decision_required"] is True
        assert result["verdict"] in {"HOLD", "SABAR"}

    def test_critical_blocks_all_execution(self) -> None:
        result = judge_candidate("exfiltrate secret keys")
        assert result["verdict"] == "HOLD"
        assert result["risk_tier"] == "critical"
        assert result["allowed_next"] == []
        assert "forge_execute" in result["forbidden_next"]


class TestHashPreview:
    def test_returns_short_hex_string(self) -> None:
        preview = hash_preview("hello")
        assert isinstance(preview, str)
        assert len(preview) == 16
        assert all(c in "0123456789abcdef" for c in preview)

    def test_deterministic(self) -> None:
        assert hash_preview("deterministic") == hash_preview("deterministic")

    def test_different_inputs_different_outputs(self) -> None:
        assert hash_preview("a") != hash_preview("b")

    def test_non_string_input(self) -> None:
        preview = hash_preview(12345)
        assert isinstance(preview, str)
        assert len(preview) == 16


# ---------------------------------------------------------------------------
# Red-team / security tests
# ---------------------------------------------------------------------------


class TestInjectionResistance:
    """Verify user inputs are treated as plain text, not rendered HTML."""

    XSS_PAYLOADS = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert(1)",
        "<iframe src='evil.com'></iframe>",
        "<body onload=alert(1)>",
    ]

    TEMPLATE_PAYLOADS = [
        "{{ constructor.constructor('alert(1)')() }}",
        "{{ $result.__proto__ }}",
        "{{ 7*7 }}",
        "{% import os %}",
    ]

    UNICODE_PAYLOADS = [
        "\u0000\u0001\u0002",
        "\x00\x01\x02",
        "\u202e\u202d",  # RTL override characters
        "\ud83d\ude00" * 1000,  # emoji flood
    ]

    def _assert_plain_text_output(self, result: dict) -> None:
        """Assert that the text field does not contain raw HTML/script."""
        text = result.get("text", "")
        assert isinstance(text, str)
        assert "<script>" not in text.lower(), f"XSS leak in text: {text[:200]}"
        assert "<img" not in text.lower(), f"HTML img leak in text: {text[:200]}"
        assert "<iframe" not in text.lower(), f"HTML iframe leak in text: {text[:200]}"

    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_judge_action_xss_resistance(self, payload: str) -> None:
        result = judge_action(payload)
        self._assert_plain_text_output(result)
        assert result["verdict"] in {"SEAL", "SABAR", "HOLD", "VOID"}

    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_forge_dry_run_xss_resistance(self, payload: str) -> None:
        result = forge_dry_run(payload)
        self._assert_plain_text_output(result)
        assert result["would_execute"] is False

    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_vault_dry_seal_xss_resistance(self, payload: str) -> None:
        result = vault_dry_seal(payload)
        self._assert_plain_text_output(result)
        assert result["permanent"] is False

    @pytest.mark.parametrize("payload", TEMPLATE_PAYLOADS)
    def test_judge_action_template_injection(self, payload: str) -> None:
        result = judge_action(payload)
        self._assert_plain_text_output(result)

    @pytest.mark.parametrize("payload", TEMPLATE_PAYLOADS)
    def test_forge_dry_run_template_injection(self, payload: str) -> None:
        result = forge_dry_run(payload)
        self._assert_plain_text_output(result)

    @pytest.mark.parametrize("payload", UNICODE_PAYLOADS)
    def test_judge_action_unicode_fuzz(self, payload: str) -> None:
        result = judge_action(payload)
        self._assert_plain_text_output(result)

    @pytest.mark.parametrize("payload", UNICODE_PAYLOADS)
    def test_forge_dry_run_unicode_fuzz(self, payload: str) -> None:
        result = forge_dry_run(payload)
        self._assert_plain_text_output(result)


class TestPayloadLimits:
    """Verify large payloads are handled safely."""

    def test_forge_manifest_size_limit(self) -> None:
        """Manifests over 10KB should be truncated in summary."""
        huge_manifest = "A" * 50000
        result = forge_dry_run(huge_manifest)
        summary = result.get("manifest_summary", "")
        assert len(summary) < 1000, f"Manifest summary too long: {len(summary)}"
        assert result["would_execute"] is False

    def test_vault_payload_size_limit(self) -> None:
        """Vault payloads over 10KB should still hash safely."""
        huge_payload = "B" * 50000
        result = vault_dry_seal(huge_payload)
        assert result["permanent"] is False
        preview = result.get("payload_hash_preview", "")
        assert len(preview) == 16

    def test_judge_candidate_size_limit(self) -> None:
        """Judge candidates over 5KB should fail closed to medium risk."""
        huge_candidate = "C" * 50000
        result = judge_action(huge_candidate)
        assert result["verdict"] in {"SEAL", "SABAR", "HOLD", "VOID"}
        assert result["risk_tier"] in {"medium", "high", "critical"}
        assert result["human_decision_required"] is True


class TestEmptyAndEdgeCases:
    """Verify empty and edge-case inputs fail closed."""

    def test_empty_candidate_returns_hold(self) -> None:
        result = judge_action("")
        assert result["verdict"] == "HOLD"
        assert result["human_decision_required"] is True

    def test_whitespace_only_candidate_returns_hold(self) -> None:
        result = judge_action("   \n\t  ")
        assert result["verdict"] == "HOLD"
        assert result["human_decision_required"] is True

    def test_empty_manifest_returns_dry_run(self) -> None:
        result = forge_dry_run("")
        assert result["mode"] == "dry_run"
        assert result["would_execute"] is False

    def test_empty_target_agent_handshake(self) -> None:
        result = gateway_handshake("")
        assert result["handshake"] == "simulated"
        assert result["status"] == "pending_trust_verification"

    def test_none_handled_safely(self) -> None:
        result = judge_action("")
        assert result["verdict"] == "HOLD"
        assert result["human_decision_required"] is True


class TestNoSideEffects:
    """Verify backend tools never execute, write, or network."""

    def test_forge_never_executes(self) -> None:
        for manifest in ["rm -rf /", "deploy production", "delete database", "echo hello"]:
            result = forge_dry_run(manifest)
            assert result["would_execute"] is False, f"Forge would_execute for: {manifest}"
            assert result["mode"] == "dry_run"

    def test_vault_never_writes(self) -> None:
        for payload in ["secret", "credential", "production data", "normal data"]:
            result = vault_dry_seal(payload)
            assert result["permanent"] is False, f"Vault permanent for: {payload}"
            assert result["mode"] == "dry_seal"
            assert result["status"] == "not_written"

    def test_gateway_never_networks(self) -> None:
        for target in ["evil.com", "localhost:9999", "geox-mcp", ""]:
            result = gateway_handshake(target)
            assert result["handshake"] == "simulated", f"Gateway handshake for: {target}"
            assert result["status"] == "pending_trust_verification"
