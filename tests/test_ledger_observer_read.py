"""FIX 2026-11-02 — civilization-fork audit blockers (Arif directive, same day).

Blocker #1: arif_seal mode=ledger must be L0_OBSERVE; sessionless callers get
head_hash + entry_count ONLY (non-execution provable without session, no
content exposure). Content requires a REGISTERED session.

Remediation honesty: capability://arifos/init remediation must not claim
side_effect_class READ_ONLY — arif_init creates a permanent session audit
record (WRITE_SAFE / PERSISTENT_AUDIT_WRITE).
"""
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _real_vault(monkeypatch):
    """Hermetic vault state: force a fresh load from the production path.

    Other test modules pollute tools module state at collection time
    (_VAULT_LOADED=True with an empty/stale ledger -> vault_chain=MISSING ->
    degraded-dominance gate suppresses seal-family reads). Restore a real
    load for these tests only; monkeypatch restores env afterwards.
    """
    from arifosmcp.runtime import tools as T

    for ev in ("ARIFOS_VAULT_PATH", "VAULT999_PATH", "ARIFOS_VAULT_DIR"):
        monkeypatch.delenv(ev, raising=False)
    T._VAULT_LOADED = False
    T._ensure_vault_loaded()
    yield


def test_init_remediation_side_effect_write_safe():
    src = (REPO / "arifosmcp/contracts/four_plane_contract.py").read_text()
    assert '"side_effect_class": "READ_ONLY"' not in src
    assert src.count('"side_effect_class": "WRITE_SAFE"') == 2
    assert src.count('"persistence_class": "PERSISTENT_AUDIT_WRITE"') == 2


def test_agency_map_ledger_is_observe():
    from arifosmcp.runtime.tools import get_full_affordance

    afford = get_full_affordance("arif_seal")
    levels = afford["mode_agency_levels"]
    assert levels["ledger"] == "L0_OBSERVE"
    read_modes = (
        "verify",
        "chain",
        "list",
        "verify_chain",
        "chain_status",
        "audit",
        "changelog",
        "ledger",
    )
    for m in read_modes:
        assert "L5" not in str(levels[m]), f"read mode {m} must not be L5"


def test_ledger_sessionless_metadata_only():
    from arifosmcp.runtime.tools import _arif_vault_seal

    out = _arif_vault_seal(mode="ledger", session_id=None, actor_id="audit-probe")
    assert out["status"] == "OK"
    res = out["result"]
    assert res["content_disclosed"] is False
    assert "ledger" not in res, "sessionless read must not disclose entries"
    assert isinstance(res["entry_count"], int)
    assert "head_hash" in res
    if res["entry_count"] > 0:
        assert res["head_hash"], "head_hash must be present when ledger non-empty"
    assert "Sessionless observer read" in res["note"]


def test_ledger_registered_session_discloses_content():
    from arifosmcp.runtime import tools as T

    sid = "test-ledger-observer-sess"
    T._SESSIONS[sid] = {"actor_id": "audit-probe"}
    try:
        out = T._arif_vault_seal(mode="ledger", session_id=sid, actor_id="audit-probe")
    finally:
        T._SESSIONS.pop(sid, None)
    assert out["status"] == "OK"
    res = out["result"]
    assert res["content_disclosed"] is True
    assert "ledger" in res
    assert res["head_hash"] is not None or res["entry_count"] == 0


def test_seal_tool_ledger_bypasses_session_gate():
    src = (REPO / "arifosmcp/runtime/tools.py").read_text()
    assert 'and mode != "ledger"' in src, "async wrapper must exempt ledger from L11 gate"
    assert '"audit", "ledger")' in src, "ledger must join the read-only ack set"
