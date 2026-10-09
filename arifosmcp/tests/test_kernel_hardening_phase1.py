"""
Fasa 1 Kernel Immutable Floor — ujian pengukuhan (G1 VAULT999-SIG, G4 ASI fail-close).

Run: python3 -m pytest arifosmcp/tests/test_kernel_hardening_phase1.py -v

Nota: sengaja TIDAK mengimport arifosmcp.memory (test_organ_forge_smoke.py
rosak pra-wujud disebab ImportError WriteRequest — bukan skop fasa ini).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from arifosmcp.runtime import pre_execution_gate as peg
from arifosmcp.runtime.canonical_vault_chain import (
    SIG_KEY_ID,
    SIG_PREFIX,
    append_receipt,
    verify_chain,
)
from arifosmcp.schemas.kernel_envelope import ActionClass, GateVerdict, KernelEnvelope
from arifosmcp.schemas.kernel_envelope import OrganIdentity

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_TOOL = REPO_ROOT / "tools" / "audit_verify.py"

TEST_KEY = "test-vault-hmac-key-phase1-do-not-use-in-prod"
OTHER_KEY = "attacker-different-key"


# ── G4: ASI firewall fail-closed ────────────────────────────────────────────


def _envelope():
    return KernelEnvelope.observe_only(organ=OrganIdentity(tool_name="arif_test"))


def test_g4_asi_firewall_unavailable_holds_mutation(monkeypatch):
    monkeypatch.setattr(peg, "_ASI_FIREWALL_AVAILABLE", False)
    result = peg._asi_firewall_check(_envelope(), ActionClass.MUTATE)
    assert result is not None
    assert result.verdict == GateVerdict.HOLD
    assert "ASI_FIREWALL_UNAVAILABLE" in result.violations
    assert result.required_human_ack is True


def test_g4_asi_firewall_unavailable_holds_irreversible(monkeypatch):
    monkeypatch.setattr(peg, "_ASI_FIREWALL_AVAILABLE", False)
    result = peg._asi_firewall_check(_envelope(), ActionClass.IRREVERSIBLE)
    assert result is not None and result.verdict == GateVerdict.HOLD


def test_g4_asi_firewall_unavailable_allows_observe(monkeypatch):
    monkeypatch.setattr(peg, "_ASI_FIREWALL_AVAILABLE", False)
    assert peg._asi_firewall_check(_envelope(), ActionClass.OBSERVE) is None
    assert peg._asi_firewall_check(_envelope(), ActionClass.ANALYZE) is None


def test_g4_asi_firewall_available_path_unchanged(monkeypatch):
    """Classifier present → normal classification flow (AGI proceeds)."""
    monkeypatch.setattr(peg, "_ASI_FIREWALL_AVAILABLE", True)
    monkeypatch.setattr(
        peg,
        "_classify_cognitive_tier",
        lambda intent, target="": {"tier": "AGI", "reason": "instrumental"},
    )
    assert peg._asi_firewall_check(_envelope(), ActionClass.MUTATE) is None


def test_g4_asi_firewall_asi_tier_holds(monkeypatch):
    monkeypatch.setattr(peg, "_ASI_FIREWALL_AVAILABLE", True)
    monkeypatch.setattr(
        peg,
        "_classify_cognitive_tier",
        lambda intent, target="": {"tier": "ASI", "reason": "recursive self-improvement"},
    )
    result = peg._asi_firewall_check(_envelope(), ActionClass.MUTATE)
    assert result is not None and result.verdict == GateVerdict.HOLD
    assert "ASI_FIREWALL" in result.violations


# ── G1: VAULT999-SIG ────────────────────────────────────────────────────────


def _no_key(monkeypatch):
    monkeypatch.delenv("ARIFOS_VAULT_HMAC_KEY", raising=False)
    monkeypatch.delenv("ARIFOS_VAULT_HMAC_KEY_FILE", raising=False)
    monkeypatch.delenv("ARIFOS_VAULT_SIG_ENFORCE", raising=False)


def _with_key(monkeypatch, key: str = TEST_KEY, enforce: str = ""):
    monkeypatch.setenv("ARIFOS_VAULT_HMAC_KEY", key)
    monkeypatch.delenv("ARIFOS_VAULT_HMAC_KEY_FILE", raising=False)
    monkeypatch.setenv("ARIFOS_VAULT_SIG_ENFORCE", enforce)


def test_g1_append_unsigned_when_no_key(monkeypatch, tmp_path):
    _no_key(monkeypatch)
    res = append_receipt(actor_id="tester", vault_dir=tmp_path)
    assert res.ok
    assert res.receipt["signature"] == ""
    assert res.receipt["sig_key_id"] == ""


def test_g1_append_signs_with_key(monkeypatch, tmp_path):
    _with_key(monkeypatch)
    res = append_receipt(actor_id="tester", vault_dir=tmp_path)
    assert res.ok
    sig = res.receipt["signature"]
    assert sig.startswith(SIG_PREFIX)
    assert len(sig) == len(SIG_PREFIX) + 64  # full 256-bit HMAC
    assert res.receipt["sig_key_id"] == SIG_KEY_ID
    v = verify_chain(tmp_path)
    assert v.verified, f"gaps: {[g.to_dict() for g in v.gaps]}"
    assert v.signed_entries == 1
    assert v.cutover_seq == res.receipt["sequence"]


def test_g1_tampered_body_breaks_hash_and_signature(monkeypatch, tmp_path):
    """Attacker rewrites the body AND recomputes receipt_hash (link-consistent).
    The HMAC signature over the original receipt_hash is what stops them."""
    from arifosmcp.runtime.canonical_vault_chain import compute_receipt_hash

    _with_key(monkeypatch)
    res = append_receipt(actor_id="tester", vault_dir=tmp_path)
    chain = tmp_path / "seal_chain.jsonl"
    entry = json.loads(chain.read_text().splitlines()[0])
    entry["actor_id"] = "attacker"
    body = {k: entry.get(k) for k in (
        "sequence", "previous_hash", "timestamp", "actor_id", "session_id",
        "trace_id", "operation_id", "tool_name", "input_hash", "authority_state",
        "decision_reference", "result_hash", "reversibility", "software_release",
        "epoch_id")}
    entry["receipt_hash"] = compute_receipt_hash(body)  # attacker fixes the hash
    entry["this_hash"] = entry["receipt_hash"]
    chain.write_text(json.dumps(entry, sort_keys=True) + "\n")
    v = verify_chain(tmp_path)
    assert not v.verified
    classes = {g.gap_class for g in v.gaps}
    assert "HASH_MISMATCH" not in classes  # attacker fixed the link layer…
    assert "SIGNATURE_FAIL" in classes     # …but cannot forge the signature


def test_g1_tampered_body_without_rehash_detected(monkeypatch, tmp_path):
    """Lazy tamper (body only) is caught by the hash recompute layer."""
    _with_key(monkeypatch)
    append_receipt(actor_id="tester", vault_dir=tmp_path)
    chain = tmp_path / "seal_chain.jsonl"
    entry = json.loads(chain.read_text().splitlines()[0])
    entry["actor_id"] = "attacker"
    chain.write_text(json.dumps(entry, sort_keys=True) + "\n")
    v = verify_chain(tmp_path)
    assert not v.verified
    assert "HASH_MISMATCH" in {g.gap_class for g in v.gaps}


def test_g1_signature_only_forgery_detected(monkeypatch, tmp_path):
    """Body intact, signature replaced with valid-looking garbage → SIGNATURE_FAIL."""
    _with_key(monkeypatch)
    res = append_receipt(actor_id="tester", vault_dir=tmp_path)
    chain = tmp_path / "seal_chain.jsonl"
    entry = json.loads(chain.read_text().splitlines()[0])
    entry["signature"] = SIG_PREFIX + ("0" * 64)
    chain.write_text(json.dumps(entry, sort_keys=True) + "\n")
    v = verify_chain(tmp_path)
    assert not v.verified
    assert "SIGNATURE_FAIL" in {g.gap_class for g in v.gaps}


def test_g1_wrong_key_detected(monkeypatch, tmp_path):
    _with_key(monkeypatch)
    append_receipt(actor_id="tester", vault_dir=tmp_path)
    _with_key(monkeypatch, key=OTHER_KEY)
    v = verify_chain(tmp_path)
    assert not v.verified
    assert "SIGNATURE_FAIL" in {g.gap_class for g in v.gaps}


def test_g1_verify_without_key_counts_unverifiable(monkeypatch, tmp_path):
    _with_key(monkeypatch)
    append_receipt(actor_id="tester", vault_dir=tmp_path)
    _no_key(monkeypatch)
    v = verify_chain(tmp_path)
    assert v.verified  # link integrity green; signature layer honest
    assert v.signed_unverifiable == 1
    assert v.signed_entries == 0


def test_g1_enforce_mode_refuses_unsigned_append(monkeypatch, tmp_path):
    _no_key(monkeypatch)
    monkeypatch.setenv("ARIFOS_VAULT_SIG_ENFORCE", "1")
    res = append_receipt(actor_id="tester", vault_dir=tmp_path)
    assert not res.ok
    assert res.failure_class == "SIG_ENFORCE_NO_KEY"


def test_g1_enforce_mode_flags_unsigned_after_cutover(monkeypatch, tmp_path):
    _with_key(monkeypatch)
    append_receipt(actor_id="tester", vault_dir=tmp_path)  # signed cutover
    # Simulate an unsigned post-cutover entry (bypasses append guard):
    chain = tmp_path / "seal_chain.jsonl"
    signed = json.loads(chain.read_text().splitlines()[0])
    forged = dict(signed)
    forged["sequence"] = signed["sequence"] + 1
    forged["receipt_id"] = "rcpt-forgedunsigned0001"
    forged["previous_hash"] = signed["receipt_hash"]
    forged["prev_hash"] = signed["receipt_hash"]  # wire alias must agree
    body = {k: forged.get(k) for k in (
        "sequence", "previous_hash", "timestamp", "actor_id", "session_id",
        "trace_id", "operation_id", "tool_name", "input_hash", "authority_state",
        "decision_reference", "result_hash", "reversibility", "software_release",
        "epoch_id")}
    from arifosmcp.runtime.canonical_vault_chain import compute_receipt_hash
    forged["receipt_hash"] = compute_receipt_hash(body)
    forged["this_hash"] = forged["receipt_hash"]
    forged["signature"] = ""
    forged["sig_key_id"] = ""
    with open(chain, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(forged, sort_keys=True) + "\n")

    # warn mode: counted, chain stays green
    _with_key(monkeypatch, enforce="")
    v = verify_chain(tmp_path)
    assert v.verified
    assert v.unsigned_after_cutover == 1

    # enforce mode: SIGNATURE_FAIL gap, chain red
    _with_key(monkeypatch, enforce="1")
    v = verify_chain(tmp_path)
    assert not v.verified
    assert "SIGNATURE_FAIL" in {g.gap_class for g in v.gaps}


# ── G1: Offline auditor verifier (subprocess on a COPY) ────────────────────


def _make_signed_chain(monkeypatch, tmp_path) -> Path:
    _with_key(monkeypatch)
    append_receipt(actor_id="auditor-test", vault_dir=tmp_path)
    copy = tmp_path / "copy_chain.jsonl"
    copy.write_text((tmp_path / "seal_chain.jsonl").read_text())
    return copy


def test_g1_audit_tool_green_on_copy(monkeypatch, tmp_path):
    copy = _make_signed_chain(monkeypatch, tmp_path)
    keyfile = tmp_path / "key.txt"
    keyfile.write_text(TEST_KEY)
    proc = subprocess.run(
        [sys.executable, str(AUDIT_TOOL), "--chain", str(copy), "--key-file", str(keyfile)],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    assert "VERIFIED" in proc.stdout


def test_g1_audit_tool_red_on_tampered_copy(monkeypatch, tmp_path):
    copy = _make_signed_chain(monkeypatch, tmp_path)
    entry = json.loads(copy.read_text().splitlines()[0])
    entry["result_hash"] = "sha256:" + ("f" * 64)
    copy.write_text(json.dumps(entry, sort_keys=True) + "\n")
    keyfile = tmp_path / "key.txt"
    keyfile.write_text(TEST_KEY)
    proc = subprocess.run(
        [sys.executable, str(AUDIT_TOOL), "--chain", str(copy), "--key-file", str(keyfile)],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 1
    assert "SIGNATURE_FAIL" in proc.stdout or "HASH_MISMATCH" in proc.stdout


def test_g1_audit_tool_no_key_warns_but_links_verified(monkeypatch, tmp_path):
    copy = _make_signed_chain(monkeypatch, tmp_path)
    import os
    env = {k: v for k, v in os.environ.items() if k != "ARIFOS_VAULT_HMAC_KEY"}
    proc = subprocess.run(
        [sys.executable, str(AUDIT_TOOL), "--chain", str(copy), "--key-env", "ARIFOS_VAULT_HMAC_KEY"],
        capture_output=True, text=True, timeout=60, env=env,
    )
    # Links verified, signatures unverifiable → still green on link layer,
    # warning emitted on stderr.
    assert proc.returncode == 0
    assert "no key supplied" in proc.stderr


# ── G2: ACT/Session HMAC 256-bit penuh (dwi-panjang) ───────────────────────


def _session_secret(monkeypatch):
    monkeypatch.setenv("ARIFOS_SESSION_SECRET", "phase1-test-session-secret")


def test_g2_session_token_full_length_sig(monkeypatch):
    _session_secret(monkeypatch)
    from arifosmcp.runtime.session import _sign_session_payload, _verify_session_token

    payload = {"actor": "arif", "auth": "SOVEREIGN", "exp": 9999999999}
    token = _sign_session_payload(payload)
    sig = token.split(".", 1)[1]
    assert len(sig) == 64  # full 256-bit — bukan 16 hex legasi
    claims = _verify_session_token(token)
    assert claims is not None and claims["actor"] == "arif"


def test_g2_session_token_legacy_16char_still_verifies(monkeypatch):
    """Token legasi (pra-naik taraf, dijana semasa tetingkap TTL) masih sah."""
    import base64 as b64
    import hashlib
    import hmac as _hmac

    _session_secret(monkeypatch)
    from arifosmcp.runtime.session import _verify_session_token

    payload = {"actor": "arif", "exp": 9999999999}
    dump = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    b64_payload = b64.urlsafe_b64encode(dump.encode()).decode().rstrip("=")
    legacy_sig = _hmac.new(
        b"phase1-test-session-secret", b64_payload.encode(), hashlib.sha256
    ).hexdigest()[:16]
    claims = _verify_session_token(f"{b64_payload}.{legacy_sig}")
    assert claims is not None and claims["actor"] == "arif"


def test_g2_session_token_tampered_rejected(monkeypatch):
    _session_secret(monkeypatch)
    from arifosmcp.runtime.session import _sign_session_payload, _verify_session_token

    token = _sign_session_payload({"actor": "arif", "exp": 9999999999})
    b64_payload, sig = token.split(".", 1)
    forged = ("f" * 64) if len(sig) == 64 else ("f" * 16)
    assert _verify_session_token(f"{b64_payload}.{forged}") is None
    # Ganti satu aksara pun mesti gagal
    tampered = ("0" if sig[0] != "0" else "1") + sig[1:]
    assert _verify_session_token(f"{b64_payload}.{tampered}") is None


def test_g2_act_token_full_length_sig_roundtrip(monkeypatch):
    _session_secret(monkeypatch)
    from arifosmcp.runtime.act_token import mint_sct, verify_sct

    token, claims = mint_sct(sid="sess-g2", actor="333-agi", auth="LIMITED_MUTATE", av=True)
    parts = token.split(".")
    assert len(parts) == 3
    assert len(parts[2]) == 64  # full HMAC
    verified = verify_sct(token, expected_actor="333-agi")
    assert verified is not None and verified.get("actor") == "333-agi"


def test_g2_act_token_legacy_16char_still_verifies(monkeypatch):
    """SCT legasi pra-naik taraf (sig dipotong) kekal diterima dalam tetingkap TTL."""
    _session_secret(monkeypatch)
    from arifosmcp.runtime.act_token import _b64url_encode, mint_sct, verify_sct
    import hashlib
    import hmac as _hmac

    token, _claims = mint_sct(sid="sess-g2-legacy", actor="333-agi", auth="OBSERVE_ONLY", av=False)
    prefix, payload_b64, _full_sig = token.split(".")
    legacy_sig = _hmac.new(
        b"phase1-test-session-secret", payload_b64.encode("ascii"), hashlib.sha256
    ).hexdigest()[:16]
    legacy_token = f"{prefix}.{payload_b64}.{legacy_sig}"
    verified = verify_sct(legacy_token, expected_actor="333-agi")
    assert verified is not None


def test_g2_act_token_tampered_rejected(monkeypatch):
    _session_secret(monkeypatch)
    from arifosmcp.runtime.act_token import mint_sct, verify_sct

    token, _ = mint_sct(sid="sess-g2-t", actor="arif", auth="SOVEREIGN", av=True)
    prefix, payload_b64, sig = token.split(".")
    assert verify_sct(f"{prefix}.{payload_b64}.{'a' * 64}", expected_actor="arif") is None
    bad = ("0" if sig[0] != "0" else "1") + sig[1:]
    assert verify_sct(f"{prefix}.{payload_b64}.{bad}", expected_actor="arif") is None


# ── G7: Kernel enforcement-freeze (Gate 8.5) ────────────────────────────────


def _clear_freeze_env(monkeypatch):
    for var in (
        "ARIFOS_KERNEL_FREEZE_PIN",
        "ARIFOS_KERNEL_FREEZE_ENFORCE",
        "ARIFOS_KERNEL_FREEZE_PIN_FILE",
    ):
        monkeypatch.delenv(var, raising=False)


def test_g7_freeze_digest_stable_and_pinned():
    from arifosmcp.runtime.kernel_freeze import compute_freeze_digest

    a = compute_freeze_digest()
    b = compute_freeze_digest()
    assert a["digest"] == b["digest"]  # deterministik dalam sesi
    assert len(a["digest"]) == 64
    assert a["unavailable"] == 0  # semua modul enforcement boleh dihash


def test_g7_freeze_check_ok_without_pin(monkeypatch):
    _clear_freeze_env(monkeypatch)
    from arifosmcp.runtime.kernel_freeze import check_freeze

    r = check_freeze()
    assert r["ok"] is True and r["drift"] is False and r["pin_configured"] is False


def test_g7_freeze_check_drift_on_mismatched_pin(monkeypatch):
    _clear_freeze_env(monkeypatch)
    monkeypatch.setenv("ARIFOS_KERNEL_FREEZE_PIN", "f" * 64)
    from arifosmcp.runtime.kernel_freeze import check_freeze

    r = check_freeze()
    assert r["drift"] is True and r["ok"] is False


def test_g7_freeze_check_ok_on_matching_pin(monkeypatch):
    _clear_freeze_env(monkeypatch)
    from arifosmcp.runtime.kernel_freeze import compute_freeze_digest

    monkeypatch.setenv("ARIFOS_KERNEL_FREEZE_PIN", compute_freeze_digest()["digest"])
    from arifosmcp.runtime.kernel_freeze import check_freeze

    r = check_freeze()
    assert r["ok"] is True and r["drift"] is False


def test_g7_gate_holds_mutation_on_drift_when_enforced(monkeypatch):
    _clear_freeze_env(monkeypatch)
    monkeypatch.setenv("ARIFOS_KERNEL_FREEZE_PIN", "f" * 64)
    monkeypatch.setenv("ARIFOS_KERNEL_FREEZE_ENFORCE", "1")
    from arifosmcp.schemas.kernel_envelope import (
        AuthorityBlock,
        KernelIdentity,
        OrganIdentity,
    )
    from arifosmcp.runtime import pre_execution_gate as peg_mod
    from arifosmcp.schemas.kernel_envelope import ActionClass, GateVerdict

    envelope = KernelEnvelope(
        kernel=KernelIdentity(actor_verified=True, constitution_hash="sha256:" + "a" * 64),
        organ=OrganIdentity(tool_name="arif_test_freeze"),
        authority=AuthorityBlock(action_class=ActionClass.MUTATE),
    )
    # Route to the freeze gate only: run Gate 8.5 via check + assert mapping,
    # to avoid needing the full gate pipeline fixtures (manifest, leases…).
    from arifosmcp.runtime.kernel_freeze import check_freeze

    freeze = check_freeze()
    assert freeze["drift"] and freeze["enforced"]
    # And the gate function itself must short-circuit with HOLD:
    # temporarily neuter the manifest lookup so earlier gates pass through.
    monkeypatch.setattr(peg_mod, "CANONICAL_TOOL_MANIFEST", {})
    result = peg_mod.pre_execution_gate(envelope, ActionClass.MUTATE)
    assert result.verdict == GateVerdict.HOLD
    assert "KERNEL_FREEZE_DRIFT" in (result.violations or [])


def test_g7_gate_allows_when_pin_matches(monkeypatch):
    _clear_freeze_env(monkeypatch)
    from arifosmcp.runtime.kernel_freeze import compute_freeze_digest

    monkeypatch.setenv("ARIFOS_KERNEL_FREEZE_PIN", compute_freeze_digest()["digest"])
    monkeypatch.setenv("ARIFOS_KERNEL_FREEZE_ENFORCE", "1")
    from arifosmcp.schemas.kernel_envelope import (
        ActionClass,
        AuthorityBlock,
        GateVerdict,
        KernelEnvelope,
        KernelIdentity,
        OrganIdentity,
    )
    from arifosmcp.runtime import pre_execution_gate as peg_mod

    monkeypatch.setattr(peg_mod, "CANONICAL_TOOL_MANIFEST", {})
    envelope = KernelEnvelope(
        kernel=KernelIdentity(actor_verified=True, constitution_hash="sha256:" + "a" * 64),
        organ=OrganIdentity(tool_name="arif_test_freeze_ok"),
        authority=AuthorityBlock(action_class=ActionClass.MUTATE),
    )
    result = peg_mod.pre_execution_gate(envelope, ActionClass.MUTATE)
    # Bukan HOLD sebab freeze drift (mungkin SABAR/SEAL dari gate lain —
    # yang penting TIADA violation KERNEL_FREEZE_DRIFT).
    assert "KERNEL_FREEZE_DRIFT" not in (result.violations or [])
