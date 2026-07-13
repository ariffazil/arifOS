from __future__ import annotations

import base64
import hashlib

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def test_runtime_attestation_is_complete_and_self_consistent():
    from arifosmcp.runtime.build import get_runtime_attestation

    att = get_runtime_attestation()
    required = {
        "release_id", "source_commit", "wheel_hash", "runtime_manifest_hash",
        "service_pid", "service_started_at", "critical_module_hashes",
    }
    assert required <= att.keys()
    assert att["runtime_manifest_hash"].startswith("sha256:")
    assert len(att["critical_module_hashes"]) >= 4


def test_valid_ed25519_ceremony_capability_consumption_and_replay(monkeypatch, tmp_path):
    from arifosmcp.runtime import crypto_auth
    from arifosmcp.runtime.forge_session_runtime import (
        consume_capability,
        issue_seal_capability,
    )

    private = Ed25519PrivateKey.generate()
    public_path = tmp_path / "arif_public.pem"
    public_path.write_bytes(private.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ))
    monkeypatch.setattr(crypto_auth, "_PUBLIC_KEY_PATH", str(public_path))

    nonce = crypto_auth.issue_actor_challenge("arif")
    signature = base64.b64encode(private.sign(f"arif:{nonce}".encode())).decode()
    verified, reason = crypto_auth.verify_init_identity("arif", nonce, signature)
    assert verified, reason

    payload_hash = hashlib.sha256(b"bounded-proof-action").hexdigest()
    cap = issue_seal_capability("proof-session", "arif", payload_hash)
    assert cap is not None
    ok, reason = consume_capability(cap.capability_id, cap.action, payload_hash)
    assert (ok, reason) == (True, "consumed")
    replay_ok, replay_reason = consume_capability(cap.capability_id, cap.action, payload_hash)
    assert replay_ok is False
    assert replay_reason in ("capability_not_found", "already_consumed")
    nonce_ok, nonce_reason = crypto_auth.verify_init_identity("arif", nonce, signature)
    assert nonce_ok is False
    assert nonce_reason == "challenge_replayed"


def test_cooling_recursion_is_structurally_bounded():
    from arifosmcp.runtime.cooling_verbs import create_cycle

    root = create_cycle("failure-1")
    nested = create_cycle(
        "failure-2", origin="cooling.verify", cooling_depth=1,
        parent_cooling_id=root.cycle_id,
    )
    assert nested.cooling_depth == 1
    with pytest.raises(ValueError, match="recursive cooling is blocked"):
        create_cycle("failure-3", cooling_depth=2, parent_cooling_id=nested.cycle_id)


def test_epistemic_claim_never_exceeds_session_authority():
    from arifosmcp.tools.session import _project_light

    components = {
        "alignment_profile": {"loaded": True},
        "adversarial_profile": {"loaded": True},
        "belief": {"intent_model": {"status": "ok"}},
        "next": {"recommended_next": "arif_observe"},
    }
    header = _project_light(
        components, sid="proof", actor_id="anonymous",
        constitution_hash="sha256:test", actor_verified=False,
    )
    claim = header.get("_epistemic", {}).get("authority_claim", "ADVISORY")
    assert not (header["authority"] == "OBSERVE_ONLY" and claim == "EXECUTIVE")


def test_live_health_endpoint_surfaces_software_release_attestation():
    """P0 invariant — /health must publicly surface runtime attestation block.

    Locks the audit's P0 requirement: independent observers must be able to bind
    delivery report → deployed wheel → current process via the public health endpoint.
    Fail-closed: if attestation block is absent, the federation claim is unverifiable.
    """
    import json
    import urllib.request

    resp = urllib.request.urlopen("http://localhost:8088/health", timeout=5)
    payload = json.loads(resp.read())
    assert "software_release" in payload, (
        "P0 invariant violated: /health does not expose software_release block. "
        "Live runtime cannot be bound to a deployed artifact."
    )
    att = payload["software_release"]
    required = {
        "release_id", "source_commit", "wheel_hash", "runtime_manifest_hash",
        "service_pid", "service_started_at", "critical_module_hashes",
    }
    missing = required - att.keys()
    assert not missing, f"P0 invariant violated: software_release missing fields: {missing}"
    assert att["runtime_manifest_hash"].startswith("sha256:")
    assert att["wheel_hash"].startswith("sha256:")
    assert len(att["critical_module_hashes"]) >= 4
    # Source-commit consistency — /health source_commit must match attestation source_commit
    assert payload.get("source_commit") == att["source_commit"], (
        f"source_commit drift: /health={payload.get('source_commit')} "
        f"vs software_release={att['source_commit']}"
    )


def test_live_arif_init_surfaces_software_release_attestation():
    """P0 invariant — arif_init response must include software_release block.

    Locks the audit's P0 requirement at the session-creation surface. Without this,
    every governance action downstream is unauditable.
    """
    import json
    import urllib.request

    body = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {
            "name": "arif_init",
            "arguments": {
                "intent": "proof-epoch-live-envelope-check",
                "actor_id": "proof-epoch-probe",
            },
        },
    }).encode()
    req = urllib.request.Request(
        "http://localhost:8088/mcp",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=5)
    raw = resp.read().decode()
    # Handle SSE framing if present
    if raw.startswith("data: "):
        raw = raw[len("data: "):]
    payload = json.loads(raw)
    result = payload.get("result", {})
    content = result.get("content", [])
    if content:
        text = content[0].get("text", "{}")
        try:
            text = json.loads(text)
        except (TypeError, json.JSONDecodeError):
            pass
    else:
        text = result
    inner_result = text.get("result", text) if isinstance(text, dict) else text
    assert "software_release" in inner_result, (
        "P0 invariant violated: arif_init response lacks software_release. "
        f"Got keys: {sorted(inner_result.keys()) if isinstance(inner_result, dict) else 'not-dict'}"
    )
    att = inner_result["software_release"]
    assert att["runtime_manifest_hash"].startswith("sha256:")
    assert att["wheel_hash"].startswith("sha256:")


def test_kernel_epoch_semantics_are_not_ambiguous():
    """P0 invariant — kernel_epoch semantic must be explicit, not conflated with build date.

    Locks the audit's critique that kernel_epoch=2026-07-03 was treated as a build date.
    The attestation block must declare what kernel_epoch means.
    """
    from arifosmcp.runtime.build import get_runtime_attestation

    att = get_runtime_attestation()
    semantics = att.get("attestation_semantics", {})
    assert "kernel_epoch" in semantics, (
        "P0 invariant violated: attestation_semantics.kernel_epoch missing. "
        "Public observers cannot distinguish constitutional epoch from build date."
    )
    # Must not be ambiguous
    assert "not" in semantics["kernel_epoch"].lower() or "epoch" in semantics["kernel_epoch"].lower()
