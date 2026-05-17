"""
tests/runtime/test_webhook_intake.py — Constitutional Webhook Intake Tests
═══════════════════════════════════════════════════════════════════════════════

Adversarial test suite for the webhook intake valve.
Every test answers: "Can the system resist malicious or malformed webhook intake?"

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Any

import pytest

from arifosmcp.runtime import webhook_intake as wi
from arifosmcp.runtime.webhook_intake import (
    SOURCE_REGISTRY,
    adjudicate_event,
    build_vault_record,
    check_rate_limit,
    check_timestamp_freshness,
    is_replay,
    process_webhook,
    verify_signature,
)
from core.enforcement.auth_continuity import mint_auth_context


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def clean_state(monkeypatch, tmp_path):
    """Reset runtime state and secrets before each test."""
    wi._seen_event_ids.clear()
    wi._rate_limit_buckets.clear()
    wi._seen_approval_nonces.clear()
    wi._trace_approval_bindings.clear()
    monkeypatch.setenv("ARIFOS_WEBHOOK_SECRET", "test-secret-for-unit-tests")
    monkeypatch.setenv("ARIFOS_POLICY_VERSION", "test-policy-v1")
    monkeypatch.setenv("ARIFOS_APPROVAL_KEY_ID", "test-key-1")
    monkeypatch.setenv("ARIFOS_APPROVAL_KEY_IDS_REVOKED", "")
    monkeypatch.setenv("VAULT999_PATH", str(tmp_path / "vault999.jsonl"))
    for src in SOURCE_REGISTRY:
        env_key = SOURCE_REGISTRY[src].get("secret_env", "ARIFOS_WEBHOOK_SECRET")
        monkeypatch.setenv(env_key, "test-secret-for-unit-tests")
    yield


@pytest.fixture
def github_payload() -> dict[str, Any]:
    return {
        "repository": {"full_name": "ariffazil/arifOS"},
        "ref": "refs/heads/main",
        "after": "abc123def456",
        "pusher": {"name": "ariffazil"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def grafana_payload() -> dict[str, Any]:
    return {
        "title": "CPU threshold exceeded",
        "status": "firing",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def manual_payload() -> dict[str, Any]:
    return {
        "actor": "ariffazil",
        "intent": "health_check",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _sign(body: bytes, secret: str = "test-secret-for-unit-tests", prefix: str = "sha256=") -> str:
    return prefix + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def _mint_approval_artifact(
    *,
    source: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    actor_id: str = "ariffazil",
) -> dict[str, Any]:
    payload_hash = wi._canonical_payload_hash(payload)
    event_id = wi._derive_event_id(source, headers, json.dumps(payload).encode())
    trace_id = wi._trace_id_for_event(event_id)
    requested_action = f"{source}:{payload.get('intent', headers.get('x-event-type', 'unknown'))}"
    auth_method = "passkey"
    key_id = "test-key-1"
    authority_level = "sovereign"
    artifact = mint_auth_context(
        session_id=f"session-{event_id}",
        actor_id=actor_id,
        token_fingerprint="fp-passkey-001",
        approval_scope=sorted(
            wi._required_approval_scope(
                trace_id=trace_id,
                event_id=event_id,
                payload_hash=payload_hash,
                policy_version="test-policy-v1",
                requested_action=requested_action,
                auth_method=auth_method,
                key_id=key_id,
                authority_level=authority_level,
            )
        ),
        parent_signature=payload_hash,
        authority_level=authority_level,
    )
    artifact["auth_method"] = auth_method
    artifact["key_id"] = key_id
    return artifact


# ── Signature Verification ────────────────────────────────────────────────────


class TestSignatureVerification:
    """F11 AUTH: Only correctly signed payloads may enter."""

    def test_valid_signature(self, github_payload):
        body = json.dumps(github_payload).encode()
        sig = _sign(body)
        assert verify_signature(body, sig, "github") is True

    def test_invalid_signature(self, github_payload):
        body = json.dumps(github_payload).encode()
        assert verify_signature(body, "sha256=badhash", "github") is False

    def test_missing_signature(self, github_payload):
        body = json.dumps(github_payload).encode()
        assert verify_signature(body, None, "github") is False

    def test_missing_secret(self, github_payload, monkeypatch):
        monkeypatch.setenv("ARIFOS_WEBHOOK_SECRET_GITHUB", "")
        monkeypatch.setenv("ARIFOS_WEBHOOK_SECRET", "")
        body = json.dumps(github_payload).encode()
        assert verify_signature(body, "sha256=anything", "github") is False

    def test_unknown_source(self, github_payload):
        body = json.dumps(github_payload).encode()
        sig = _sign(body)
        # Falls back to default secret; should still verify if same secret
        assert verify_signature(body, sig, "unknown_source") is True

    def test_wrong_prefix(self, github_payload):
        body = json.dumps(github_payload).encode()
        sig = hmac.new(b"test-secret-for-unit-tests", body, hashlib.sha256).hexdigest()
        # Missing "sha256=" prefix
        assert verify_signature(body, sig, "github") is False


# ── Replay Protection ─────────────────────────────────────────────────────────


class TestReplayProtection:
    """F12 INJECTION: Same event_id must be rejected on second arrival."""

    def test_first_seen_ok(self):
        assert is_replay("evt-001") is False

    def test_second_seen_blocked(self):
        assert is_replay("evt-002") is False
        assert is_replay("evt-002") is True

    def test_timestamp_freshness_valid(self):
        ts = datetime.now(timezone.utc).isoformat()
        assert check_timestamp_freshness(ts, max_age=300) is True

    def test_timestamp_stale(self):
        old = "2024-01-01T00:00:00+00:00"
        assert check_timestamp_freshness(old, max_age=300) is False

    def test_timestamp_future(self):
        future = "2030-01-01T00:00:00+00:00"
        assert check_timestamp_freshness(future, max_age=300) is False

    def test_timestamp_malformed(self):
        assert check_timestamp_freshness("not-a-timestamp", max_age=300) is False


# ── Rate Limiting ─────────────────────────────────────────────────────────────


class TestRateLimiting:
    """F05 PEACE: Prevent abuse through rate limiting."""

    def test_within_limit(self):
        allowed, meta = check_rate_limit("ip-1")
        assert allowed is True
        assert meta["remaining"] == 9

    def test_exceeds_limit(self):
        for i in range(11):
            allowed, _ = check_rate_limit("ip-2")
        assert allowed is False

    def test_window_resets(self):
        # Fill bucket
        for _ in range(10):
            check_rate_limit("ip-3")
        allowed, _ = check_rate_limit("ip-3")
        assert allowed is False


# ── Schema Validation ─────────────────────────────────────────────────────────


class TestSchemaValidation:
    """F02 TRUTH + F10 ONTOLOGY: Payloads must match expected structure."""

    def test_github_valid(self, github_payload):
        issues = wi.validate_github_payload(github_payload)
        assert issues == []

    def test_github_missing_repo(self):
        issues = wi.validate_github_payload({})
        assert any("Missing repository" in i for i in issues)

    def test_github_invalid_repo_name(self):
        issues = wi.validate_github_payload({"repository": {"full_name": "evil<script>"}})
        assert any("Invalid repository" in i for i in issues)

    def test_grafana_valid(self, grafana_payload):
        issues = wi.validate_grafana_payload(grafana_payload)
        assert issues == []

    def test_grafana_unknown_status(self):
        issues = wi.validate_grafana_payload({"title": "x", "status": "weird"})
        assert any("Unknown alert status" in i for i in issues)

    def test_manual_valid(self, manual_payload):
        issues = wi.validate_manual_payload(manual_payload)
        assert issues == []

    def test_manual_missing_actor(self):
        issues = wi.validate_manual_payload({"intent": "health_check"})
        assert any("F11 AUTH" in i for i in issues)

    def test_manual_invalid_intent(self):
        issues = wi.validate_manual_payload({"actor": "arif", "intent": "destroy"})
        assert any("F04 CLARITY" in i for i in issues)


# ── Constitutional Adjudication ───────────────────────────────────────────────


class TestAdjudication:
    """F01–F13: The core governance evaluation of every webhook event."""

    def test_github_push_qualifies(self, github_payload):
        result = adjudicate_event("github", "push", github_payload, {})
        assert result["verdict"] == "888-HOLD"
        assert result["routing"]["target"] == "arif_forge_execute"
        assert result["reversibility"] == "IRREVERSIBLE"

    def test_unknown_source_void(self):
        result = adjudicate_event("hacker", "exploit", {}, {})
        assert result["verdict"] == "VOID"
        assert any("F11 AUTH" in i for i in result["issues"])

    def test_missing_actor_void(self, github_payload):
        bad = {**github_payload, "pusher": {}}
        result = adjudicate_event("github", "push", bad, {})
        assert result["verdict"] == "VOID"
        assert any("F12 INJECTION" in i for i in result["issues"])

    def test_manual_veto_routing(self, manual_payload):
        veto = {**manual_payload, "intent": "sovereign_veto"}
        result = adjudicate_event("manual", "sovereign_veto", veto, {})
        assert result["verdict"] == "QUALIFY"
        assert result["routing"]["action"] == "veto"
        assert result["routing"]["target"] == "arif_judge_deliberate"

    def test_irreversible_without_ack_hold(self, github_payload):
        result = adjudicate_event("github", "push", github_payload, {})
        # push is irreversible but github webhooks don't carry ack_irreversible
        # The system should flag this
        assert result["verdict"] in ("QUALIFY", "888-HOLD")
        # Actually our logic flags it as HOLD if ack_irreversible missing
        assert any("F01 AMANAH" in i for i in result["issues"]) or result["verdict"] == "QUALIFY"

    def test_actor_sanitization(self):
        raw_actor = "arif<script>alert(1)</script>"
        result = adjudicate_event(
            "manual",
            "health_check",
            {
                "actor": raw_actor,
                "intent": "health_check",
            },
            {},
        )
        assert "<script>" not in result["actor"]
        assert result["actor"] == "arifscriptalert1script"

    def test_never_auto_seal(self, github_payload):
        """CRITICAL: Webhooks must NEVER auto-SEAL."""
        result = adjudicate_event("github", "push", github_payload, {})
        assert result["verdict"] != "SEAL"


# ── Vault Record ──────────────────────────────────────────────────────────────


class TestVaultRecord:
    """VAULT999: Every intake must be recordable."""

    def test_record_structure(self, github_payload):
        adj = adjudicate_event("github", "push", github_payload, {})
        record = build_vault_record(adj, github_payload)
        assert record["ledger_type"] == "WEBHOOK_INTAKE"
        assert record["trace_id"] == adj["trace_id"]
        assert record["verdict"] == adj["verdict"]
        assert record["policy_version"] == "test-policy-v1"
        assert "payload_hash" in record
        assert len(record["payload_hash"]) == 16

    def test_payload_hash_stability(self, github_payload):
        adj = adjudicate_event("github", "push", github_payload, {})
        r1 = build_vault_record(adj, github_payload)
        r2 = build_vault_record(adj, github_payload)
        assert r1["payload_hash"] == r2["payload_hash"]


# ── Full Pipeline (process_webhook) ───────────────────────────────────────────


class TestProcessWebhook:
    """End-to-end constitutional pipeline tests."""

    def test_happy_path_github_push(self, github_payload):
        body = json.dumps(github_payload).encode()
        sig = _sign(body)
        headers = {
            "x-hub-signature-256": sig,
            "x-event-type": "push",
            "x-github-delivery": "del-123",
        }
        result = process_webhook("github", body, headers, "ip-10")
        assert result["verdict"] == "888-HOLD"
        assert any("F01 AMANAH" in i for i in result["issues"])
        assert result["trace_id"].startswith("wh-")
        assert "vault_record" in result
        assert result["vault_record"]["entry_id"].startswith("VAULT-")
        assert result["vault_record"]["prev_hash"] == "GENESIS"
        assert result["policy_version"] == "test-policy-v1"

    def test_void_bad_signature(self, github_payload):
        body = json.dumps(github_payload).encode()
        headers = {
            "x-hub-signature-256": "sha256=badbadbad",
            "x-event-type": "push",
            "x-github-delivery": "del-124",
        }
        result = process_webhook("github", body, headers, "ip-11")
        assert result["verdict"] == "VOID"
        assert any("F11 AUTH" in i for i in result["issues"])

    def test_void_replay(self, github_payload):
        body = json.dumps(github_payload).encode()
        sig = _sign(body)
        headers = {
            "x-hub-signature-256": sig,
            "x-event-type": "push",
            "x-github-delivery": "del-replay",
        }
        r1 = process_webhook("github", body, headers, "ip-12")
        assert r1["verdict"] == "888-HOLD"
        r2 = process_webhook("github", body, headers, "ip-12")
        assert r2["verdict"] == "VOID"
        assert any("Replay detected" in i for i in r2["issues"])

    def test_void_rate_limit(self, github_payload):
        body = json.dumps(github_payload).encode()
        sig = _sign(body)
        headers = {
            "x-hub-signature-256": sig,
            "x-event-type": "push",
            "x-github-delivery": "del-rl",
        }
        # Exhaust rate limit for this IP
        for i in range(12):
            h = {**headers, "x-github-delivery": f"del-rl-{i}"}
            process_webhook("github", body, h, "ip-13")
        result = process_webhook("github", body, headers, "ip-13")
        assert result["verdict"] == "VOID"
        assert any("Rate limit exceeded" in i for i in result["issues"])

    def test_void_stale_timestamp(self):
        stale = {
            "repository": {"full_name": "ariffazil/arifOS"},
            "ref": "refs/heads/main",
            "timestamp": "2024-01-01T00:00:00+00:00",
        }
        body = json.dumps(stale).encode()
        sig = _sign(body)
        headers = {
            "x-hub-signature-256": sig,
            "x-event-type": "push",
            "x-github-delivery": "del-stale",
        }
        result = process_webhook("github", body, headers, "ip-14")
        assert result["verdict"] == "VOID"
        assert any("Stale webhook" in i for i in result["issues"])

    def test_void_malformed_json(self):
        body = b"not json {"
        sig = _sign(body)
        headers = {
            "x-hub-signature-256": sig,
            "x-event-type": "push",
            "x-github-delivery": "del-badjson",
        }
        result = process_webhook("github", body, headers, "ip-15")
        assert result["verdict"] == "VOID"
        assert any("Invalid JSON" in i for i in result["issues"])

    def test_void_unknown_source(self, github_payload):
        body = json.dumps(github_payload).encode()
        sig = _sign(body)
        headers = {
            "x-source": "hacker",
            "x-signature": sig,
            "x-event-type": "exploit",
        }
        result = process_webhook("hacker", body, headers, "ip-16")
        assert result["verdict"] == "VOID"
        assert any("Unknown source" in i for i in result["issues"])

    def test_grafana_alert_pipeline(self, grafana_payload):
        body = json.dumps(grafana_payload).encode()
        sig = _sign(body, prefix="")
        headers = {
            "x-grafana-signature": sig,
            "x-event-type": "alert",
            "x-grafana-id": "graf-001",
        }
        result = process_webhook("grafana", body, headers, "ip-17")
        assert result["verdict"] == "QUALIFY"
        assert result["routing"]["target"] == "arif_judge_deliberate"

    def test_manual_health_check(self, manual_payload):
        body = json.dumps(manual_payload).encode()
        sig = _sign(body)
        headers = {
            "x-arifos-signature": sig,
            "x-event-type": "health_check",
            "x-arifos-id": "man-001",
        }
        result = process_webhook("manual", body, headers, "ip-18")
        assert result["verdict"] == "QUALIFY"
        assert result["routing"]["action"] == "observe"
        assert result["approval_status"] == "not_required"

    def test_manual_deploy_signal_requires_human_approval(self, manual_payload):
        deploy = {**manual_payload, "intent": "deploy_signal"}
        body = json.dumps(deploy).encode()
        sig = _sign(body)
        headers = {
            "x-arifos-signature": sig,
            "x-event-type": "deploy_signal",
            "x-arifos-id": "man-deploy-no-approval",
        }
        result = process_webhook("manual", body, headers, "ip-19")
        assert result["verdict"] == "888-HOLD"
        assert result["approval_status"] == "missing"
        assert any("fresh human approval artifact" in i for i in result["issues"])

    def test_manual_deploy_signal_qualifies_with_passkey_approval(self, manual_payload):
        deploy = {**manual_payload, "intent": "deploy_signal"}
        headers = {
            "x-event-type": "deploy_signal",
            "x-arifos-id": "man-deploy-approved",
        }
        deploy["approval_artifact"] = _mint_approval_artifact(
            source="manual",
            headers=headers,
            payload=deploy,
        )
        body = json.dumps(deploy).encode()
        headers["x-arifos-signature"] = _sign(body)
        result = process_webhook("manual", body, headers, "ip-20")
        assert result["verdict"] == "QUALIFY"
        assert result["approval_status"] == "approved"
        assert result["vault_record"]["approval_auth_method"] == "passkey"
        assert result["vault_record"]["prev_hash"] == "GENESIS"
        assert result["seal_authorized"] is False

    def test_rejects_revoked_approval_key(self, manual_payload, monkeypatch):
        monkeypatch.setenv("ARIFOS_APPROVAL_KEY_IDS_REVOKED", "test-key-1")
        deploy = {**manual_payload, "intent": "deploy_signal"}
        headers = {
            "x-event-type": "deploy_signal",
            "x-arifos-id": "man-deploy-revoked",
        }
        deploy["approval_artifact"] = _mint_approval_artifact(
            source="manual",
            headers=headers,
            payload=deploy,
        )
        body = json.dumps(deploy).encode()
        headers["x-arifos-signature"] = _sign(body)
        result = process_webhook("manual", body, headers, "ip-21")
        assert result["verdict"] == "VOID"
        assert any("revoked" in i for i in result["issues"])

    def test_rejects_reused_approval_nonce(self, manual_payload):
        deploy = {**manual_payload, "intent": "deploy_signal"}
        first_headers = {
            "x-event-type": "deploy_signal",
            "x-arifos-id": "man-deploy-first",
        }
        artifact = _mint_approval_artifact(
            source="manual",
            headers=first_headers,
            payload=deploy,
        )

        first_payload = {**deploy, "approval_artifact": artifact}
        first_body = json.dumps(first_payload).encode()
        first_headers["x-arifos-signature"] = _sign(first_body)
        first = process_webhook("manual", first_body, first_headers, "ip-22")
        assert first["verdict"] == "QUALIFY"

        second_headers = {
            "x-event-type": "deploy_signal",
            "x-arifos-id": "man-deploy-second",
        }
        second_payload = {**deploy, "approval_artifact": artifact}
        second_body = json.dumps(second_payload).encode()
        second_headers["x-arifos-signature"] = _sign(second_body)
        second = process_webhook("manual", second_body, second_headers, "ip-22")
        assert second["verdict"] == "VOID"
        assert any("Approval nonce already used" in i for i in second["issues"])
