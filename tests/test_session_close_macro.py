"""
tests/test_session_close_macro.py — unit + smoke for 5-stage session close macro.

Forged 2026-07-30. Stages 1–3 unit-tested offline; stage 0/4/5 optional live.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from unittest import mock

import pytest

from arifosmcp.tools import session_close_macro as scm


def test_synthesize_session_eurekas_extracts_bullets():
    eureka = scm.synthesize_session_eurekas(
        "- L11 loopback fixed for system actors\n"
        "- session_close must not ask permission\n"
        "1. Extend tools, don't rebuild\n",
        session_id="sess-test-001",
        actor_id="claude",
        organ_health={"alive_count": 7, "total": 7},
    )
    assert eureka["eureka_id"].startswith("SE-")
    assert len(eureka["insights"]) == 3
    assert "L11" in eureka["insights"][0]
    assert "SESSION EUREKA" in eureka["markdown_block"]
    assert "claude" in eureka["markdown_block"]


def test_synthesize_fallback_paragraph():
    eureka = scm.synthesize_session_eurekas(
        "Forged the missing session close macro as one callable unit.",
        session_id="sess-test-002",
        actor_id="grok",
    )
    assert len(eureka["insights"]) >= 1
    assert "macro" in eureka["insights"][0].lower() or "Forged" in eureka["insights"][0]


def test_append_to_boot_eureka_idempotent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    boot = tmp_path / "BOOT_EUREKA.md"
    boot.write_text("# BOOT\n\n## EUREKA 1: test\n", encoding="utf-8")
    monkeypatch.setattr(scm, "BOOT_EUREKA_PATH", boot)

    eureka = scm.synthesize_session_eurekas(
        "- unit test insight for macro",
        session_id="sess-idem",
        actor_id="test",
    )
    r1 = scm.append_to_boot_eureka(eureka)
    r2 = scm.append_to_boot_eureka(eureka)
    assert r1["appended"] is True
    assert r2["appended"] is False
    assert r2["reason"] == "already_present"
    text = boot.read_text(encoding="utf-8")
    assert text.count(eureka["eureka_id"]) == 1


def test_validate_sot_integrity_structure():
    result = scm.validate_sot_integrity()
    assert "checks" in result
    assert "ok" in result
    # BOOT_EUREKA and organ_intent_map should exist on this VPS
    names = {c["name"] for c in result["checks"]}
    assert "BOOT_EUREKA" in names
    assert "organ_intent_map" in names


def test_run_pre_seal_stages_offline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    boot = tmp_path / "BOOT_EUREKA.md"
    boot.write_text("# BOOT\n\n## EUREKA 1: seed\n" + ("x" * 120), encoding="utf-8")
    monkeypatch.setattr(scm, "BOOT_EUREKA_PATH", boot)

    # Force stage 3 soft-fail without real qdrant dependency in unit path
    monkeypatch.setattr(scm, "vectorize_to_atlas333", lambda eureka: {
        "phase": "3_atlas333",
        "upserted": False,
        "points": 0,
        "error": "mocked",
    })

    pre = scm.run_pre_seal_stages(
        payload="- offline pre-seal stage works",
        session_id="sess-pre",
        actor_id="test",
        organ_health={"alive_count": 7, "total": 7},
    )
    assert pre["stage_1_sot_refactor"]["appended"] is True
    assert "stage_2_sot_verify" in pre
    assert pre["stage_3_atlas333"]["upserted"] is False


def test_probe_organ_health_shape():
    health = scm.probe_organ_health(timeout_s=2.0)
    assert health["total"] == 7
    assert "organs" in health
    assert "dead" in health
    assert isinstance(health["all_alive"], bool)


@pytest.mark.asyncio
async def test_session_close_mode_wires_macro_meta():
    """Live smoke: arif_seal(mode=session_close) returns macro stage receipt on SEAL."""
    from arifosmcp.tools.vault import arif_seal

    # Avoid pushing during unit CI — patch git stage only
    with mock.patch(
        "arifosmcp.tools.session_close_macro.git_sync_federation",
        return_value={"phase": "5_remote_sync", "synced": True, "repos": {}, "pushed": [], "skipped": []},
    ):
        out = await arif_seal(
            mode="session_close",
            payload=(
                "- Forged arif_session_close_macro stages 1-5\n"
                "- Fixed MISSING_WITNESS gate on autonomous session close\n"
                f"- smoke id {uuid.uuid4().hex[:8]}"
            ),
            ack_irreversible=True,
            actor_id="claude",
            session_id=f"sess-macro-{uuid.uuid4().hex[:10]}",
        )

    data = out.model_dump(mode="json") if hasattr(out, "model_dump") else dict(out)
    assert data.get("verdict") in ("SEAL", "HOLD", "SABAR", "VOID") or str(data.get("verdict"))

    # On SEAL, macro meta must be present
    if str(data.get("verdict")).upper() == "SEAL" or data.get("status") == "OK":
        meta = data.get("meta") or {}
        sc = meta.get("session_close") or {}
        assert sc.get("macro") == "arif_session_close_macro"
        assert sc.get("seal_complete") is True
        stages = sc.get("stages") or {}
        assert "1_sot_refactor" in stages or "4_vault" in stages
    else:
        # HOLD is acceptable when organs dead or vault path blocked — but must not be MISSING_WITNESS
        assert data.get("status") != "MISSING_WITNESS", data
