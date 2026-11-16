"""test_f6_seam_closure_20261111 - regression guards for F13 SEAL c2f5a175.
Runnable: python -m pytest this-file  OR  python this-file (main block)."""
import ast
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RR = REPO / "arifosmcp" / "runtime" / "rest_routes" / "rest_routes.py"
VAULT = REPO / "arifosmcp" / "tools" / "vault.py"

def test_p1_first_class_state_wired():
    src = RR.read_text()
    assert "def _f6_first_class_state" in src
    assert 'resolved_floors["F6"] = _f6_score' in src
    assert 'floor_provenance["F6"] = str(' not in src
    ast.parse(src)

def test_p2_failure_visibility_wired():
    src = VAULT.read_text()
    assert "_f6_log_emit_failure" in src
    assert "f6_incomplete_transition" in src
    ast.parse(src)

def test_h_no_secret_leak_in_log_format():
    src = VAULT.read_text()
    i = src.index("maruah_emit_failed")
    stmt = src[i : i + 300].split("\n)")[0]
    for forbidden in ("str(_f6_exc)", "blast_radius", "payload"):
        assert forbidden not in stmt, forbidden

def test_d_emitter_conductor_if_arifos():
    """Conductor: sudo -u arifos ARIFOS_F6_TEST_SINK=/tmp/x.jsonl python this-file"""
    sink = os.environ.get("ARIFOS_F6_TEST_SINK")
    if not sink:
        print("SKIP conductor (env ARIFOS_F6_TEST_SINK unset)")
        return
    import arifosmcp.runtime.f6.meters as M
    M.MARUAH_EVENTS_PATH = Path(sink)
    r = M.emit_tier3_maruah_event(
        decision_id="TEST-D-" + str(os.getuid()), tool_name="conductor",
        blast_radius="none", ack_irreversible=True, witness_type="human", mode="test",
    )
    assert r.get("emitted") is True, r
    row = json.loads(Path(sink).read_text().strip().splitlines()[-1])
    assert row["schema"] == "arifos.f6.maruah_event.v2"
    assert row["restatement_provided"] is True
    # idempotency by decision_id is a Node-side contract; python emits once per seal call.
    print("CONDUCTOR PASS uid=%s" % os.getuid())

if __name__ == "__main__":
    test_p1_first_class_state_wired()
    test_p2_failure_visibility_wired()
    test_h_no_secret_leak_in_log_format()
    test_d_emitter_conductor_if_arifos()
    print("ALL TESTS PASS")
