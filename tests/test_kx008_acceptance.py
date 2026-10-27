"""KX-008 Acceptance Test Suite — Contract & Ingress Validation (2026-10-27).

REFERENCE: ARIFOS::KX-008_EXECUTION::2026-10-27
AUTHORITY: ARIF (F13 Sovereign)
TICKET: KX-008 ONLY

Acceptance criteria:
  KX008-AT1: url absent, null and empty follow one documented invalid-input contract.
  KX008-AT2: An invalid url is never listed among valid/usable received fields.
  KX008-AT3: Caller-supplied session_id cannot become the runtime handle.
  KX008-AT4: Changing client_ref cannot change authority, evidence result or verdict.
  KX008-AT5: client_ref is echoed exactly once.
  KX008-AT6: A syntactically valid but unknown handle is rejected.
  KX008-AT7: A handle cannot substitute for actor identity.
  KX008-AT8: The live F8 contradiction for KX-008 disappears after the fix.
  KX008-AT9: KX-007 regression remains green.
  KX008-AT10: KX-002 scoped fields remain live on wire.
  KX008-AT11: Known reversibility failures are verified baseline and not attributed to patch.
  KX008-AT12: No new unratified identity, authority or verdict aliases in public schema.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arifosmcp.runtime.input_contract import enforce, missing_params
try:
    from arifosmcp.runtime.input_contract import normalize_request_fields
except ImportError:
    normalize_request_fields = None
from arifosmcp.runtime.tools import _SESSIONS
from arifosmcp.tools.session import arif_init


# ── KX008-AT1: url absent, null and empty follow one contract ──────────────


def test_kx008_at1_url_absent_null_empty_consistency():
    """url absent, explicit null, and empty string must all produce the same
    rejection and missing_params classification."""
    cases = [
        {"mode": "ingest", "query": "target-claim"},
        {"mode": "ingest", "query": "target-claim", "url": None},
        {"mode": "ingest", "query": "target-claim", "url": "   "},
    ]
    for kw in cases:
        missing = missing_params("arif_observe", kw)
        assert "url" in missing, f"Expected 'url' in missing_params for {kw}"
        msg = enforce("arif_observe", kw)
        assert msg is not None, f"Expected rejection message for {kw}"
        assert "requires url" in msg, f"Message should specify 'requires url': {msg}"


# ── KX008-AT2: invalid url never listed among received fields ─────────────


def test_kx008_at2_invalid_url_never_in_received_fields():
    """An explicit null or empty url must NEVER appear under 'Params received'."""
    for bad_url in (None, "", "   "):
        kw = {
            "mode": "ingest",
            "query": "active query",
            "url": bad_url,
            "session_id": "SEAL-test1234",
            "actor_id": "hermes",
        }
        msg = enforce("arif_observe", kw)
        assert msg is not None
        assert "Params received: [" in msg
        received_str = msg.split("Params received: [")[1].split("]")[0]
        assert "'url'" not in received_str, f"url listed as received when {bad_url!r}: {received_str}"
        assert "'query'" in received_str

        # Also verify structured field classification
        norm = normalize_request_fields(kw)
        assert "query" in norm["valid_fields"]
        assert "url" in norm["invalid_fields"]
        assert "url" not in norm["valid_fields"]


# ── KX008-AT3: caller session_id cannot become runtime handle ──────────────


def test_kx008_at3_caller_session_id_cannot_become_runtime_handle():
    """Caller-supplied session_id cannot become the server-minted handle."""
    client_custom_sid = "caller-attempted-handle-9999"
    res = arif_init(
        mode="init",
        actor_id="test_actor",
        intent="test session handle isolation",
        session_id=client_custom_sid,
    )
    result = res.result if hasattr(res, "result") else res
    res_dict = result if isinstance(result, dict) else (res if isinstance(res, dict) else {})

    # Server must mint its own handle
    handle = res_dict.get("handle") or res_dict.get("session_id")
    assert handle != client_custom_sid, "Caller-supplied session_id was adopted as runtime handle!"
    assert str(handle).startswith("SEAL-") or str(handle).startswith("hdl_")

    # Storage key in _SESSIONS must be the server-minted handle, not client string
    assert client_custom_sid not in _SESSIONS, "Client-supplied session_id exists as key in _SESSIONS"


# ── KX008-AT4: changing client_ref cannot change authority or verdict ─────


def test_kx008_at4_client_ref_cannot_alter_authority():
    """Varying client_ref has zero impact on granted authority or verdict."""
    res1 = arif_init(
        mode="init",
        actor_id="warga_test",
        intent="deterministic test A",
        client_ref="ref-AAA",
    )
    res2 = arif_init(
        mode="init",
        actor_id="warga_test",
        intent="deterministic test A",
        client_ref="ref-BBB",
    )
    d1 = res1.result if hasattr(res1, "result") else res1
    d2 = res2.result if hasattr(res2, "result") else res2

    assert d1.get("authority") == d2.get("authority") == "OBSERVE_ONLY"
    assert d1.get("verdict") == d2.get("verdict")
    assert d1.get("actor_verified") == d2.get("actor_verified") == False


# ── KX008-AT5: client_ref is echoed exactly once ──────────────────────────


def test_kx008_at5_client_ref_echoed_exactly_once():
    """client_ref is stored and echoed back to the caller for correlation."""
    res = arif_init(
        mode="init",
        actor_id="warga_echo",
        intent="correlation test",
        client_ref="correlation-token-42",
    )
    d = res.result if hasattr(res, "result") else res
    assert d.get("client_ref") == "correlation-token-42"

    # Compatibility: passing legacy session_id populates client_ref
    res_compat = arif_init(
        mode="init",
        actor_id="warga_compat",
        intent="legacy session_id compat",
        session_id="legacy-corr-77",
    )
    dc = res_compat.result if hasattr(res_compat, "result") else res_compat
    assert dc.get("client_ref") == "legacy-corr-77"


# ── KX008-AT6: syntactically valid but unknown handle is rejected ─────────


def test_kx008_at6_unknown_handle_rejected():
    """An unknown handle passed to resume or validate must return HOLD/rejected."""
    fake_handle = "SEAL-0000000000000000"
    res = arif_init(
        mode="resume",
        session_id=fake_handle,
        handle=fake_handle,
    )
    d = res.result if hasattr(res, "result") else res
    status = getattr(res, "status", None) or d.get("status")
    verdict = getattr(res, "verdict", None) or d.get("verdict")
    assert status == "HOLD" or verdict in ("HOLD", "VOID"), f"Unknown handle was not held: {res}"


# ── KX008-AT7: handle cannot substitute for actor identity ────────────────


def test_kx008_at7_handle_cannot_substitute_for_actor_identity():
    """A valid handle created by an unverified actor cannot grant sovereign
    authority if another actor passes it."""
    # Create an initial session
    res_init = arif_init(
        mode="init",
        actor_id="unverified_agent",
        intent="base session",
    )
    d_init = res_init.result if hasattr(res_init, "result") else res_init
    real_handle = d_init.get("handle") or d_init.get("session_id")

    # Another caller attempts to use this handle while claiming another identity
    res_probe = arif_init(
        mode="validate",
        session_id=real_handle,
        actor_id="arif",  # attempting to claim sovereign identity via existing handle
    )
    d_probe = res_probe.result if hasattr(res_probe, "result") else res_probe
    assert d_probe.get("authority") != "SOVEREIGN"
    assert d_probe.get("actor_verified") is not True


# ── KX008-AT8: live contradiction register reflects resolved status ───────


def test_kx008_at8_contradiction_register_closed():
    """In the contradiction register, KX-008 is marked resolved."""
    reg_path = Path("/var/lib/arifos/contradiction_register.json")
    if not reg_path.exists():
        pytest.skip("Contradiction register not found on this host")
    data = json.loads(reg_path.read_text())
    kx008 = next((e for e in data.get("entries", []) if e.get("id") == "KX-008"), None)
    assert kx008 is not None, "KX-008 not found in register"
    assert kx008.get("status") == "resolved", f"KX-008 is {kx008.get('status')}, expected resolved"
    assert kx008.get("resolution_evidence"), "KX-008 missing resolution_evidence"


# ── KX008-AT9: KX-007 regression remains green ───────────────────────────


def test_kx008_at9_kx007_regression_green():
    """Verify check_judge_postcondition surfaces UNKNOWN items."""
    from arifosmcp.runtime.judge_postcondition import check_judge_postcondition

    evidence = {
        "value": [
            {"fact": "PHP 8.4.27 released", "tag": "OBS"},
            {"fact": "CVSS 9.2", "tag": "UNKNOWN"},
        ]
    }
    res = check_judge_postcondition(
        mode="judge",
        candidate="composite claim",
        evidence=evidence,
        verdict_str="SEAL",
        effective_verdict="SEAL",
    )
    assert len(res["unwitnessed_evidence"]) == 1
    assert "unwitnessed_evidence_items" in res["missing_evidence"]
    assert res["verdict"] == "SABAR"


# ── KX008-AT10: KX-002 scoped fields remain live on wire ──────────────────


def test_kx008_at10_kx002_scoped_fields_live():
    """Verify rest_routes _build_governance_status_payload exports the 4 scoped G fields."""
    from arifosmcp.runtime.rest_routes.rest_routes import _build_governance_status_payload

    gov = _build_governance_status_payload()
    scalars = gov.get("apex_scalars", {})
    for expected in ("g_task_verdict", "g_well_state", "g_authorization", "g_metabolism"):
        assert expected in scalars, f"Scoped field {expected} missing from apex_scalars"
        assert scalars[expected].get("status") == "MEASURED"
        assert scalars[expected].get("scope") == expected


# ── KX008-AT11: verify baseline reversibility tests are preserved ─────────


def test_kx008_at11_reversibility_baseline_preserved():
    """Verify action classifier reversibility rules are operational."""
    from arifosmcp.runtime.__advisory__.arif_action_classifier import (
        Action,
        ActionClass,
        ArifOSMetabolism,
        Gate,
    )

    metabolism = ArifOSMetabolism()
    action = Action(
        name="burn_draft",
        description="test draft burn",
        action_class=ActionClass.PREPARE,
        reversibility=0.4,
        blast_radius=0.1,
        uncertainty=0.1,
    )
    verdict = metabolism.classify_gate(action)
    # Low reversibility on PREPARE prevents automatic execution
    assert verdict.may_execute is False


# ── KX008-AT12: no new unratified aliases in public schema ─────────────────


def test_kx008_at12_no_unratified_verdict_aliases():
    """Public schema only exports canonical verdicts."""
    from arifosmcp.runtime.verdict import CANONICAL_VERDICTS

    allowed = {"SEAL", "PARTIAL", "SABAR", "HOLD", "888_HOLD", "OBSERVE_ONLY", "VOID"}
    assert CANONICAL_VERDICTS.issubset(allowed)
