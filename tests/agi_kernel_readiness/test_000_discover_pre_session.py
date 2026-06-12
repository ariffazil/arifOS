from arifosmcp.tools.session import arif_session_init

def test_000_discover_pre_session():
    manifest = arif_session_init(mode="discover", actor_id="tester")
    assert manifest.status == "OK"
    assert manifest.mode == "discover"
    assert manifest.result["stage"] == "000"
    assert manifest.result["pre_session"] is True
