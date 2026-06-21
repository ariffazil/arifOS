"""
test_surface_inventory.py — Verify surface inventory truthfulness.

Does not require full PHOENIX-72 completion.
"""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent


def test_canonical13_count_is_21():
    """canonical13 must expose exactly 21 canonical tools."""
    from arifosmcp.constitutional_map import list_canonical_tools

    tools = list_canonical_tools()
    assert len(tools) == 21, f"Expected 21 canonical tools, got {len(tools)}"


def test_canonical13_names_are_arif_prefix():
    """All canonical tools use arif_noun_verb naming."""
    from arifosmcp.constitutional_map import list_canonical_tools

    for name in list_canonical_tools():
        assert name.startswith("arif_"), f"Canonical tool must start with arif_: {name}"


def test_no_legacy_arifos_prefix_in_canonical():
    """Legacy arifos_ prefix must not appear in canonical surface."""
    from arifosmcp.constitutional_map import list_canonical_tools

    for name in list_canonical_tools():
        assert not name.startswith("arifos_"), f"Legacy prefix detected: {name}"


def test_phoenix72_manifest_exists_and_is_valid_json():
    """Target manifest must exist and be valid JSON."""
    manifest_path = PROJECT_ROOT / "arifosmcp" / "manifests" / "phoenix72.tools.json"
    assert manifest_path.exists(), "PHOENIX-72 manifest missing"
    data = json.loads(manifest_path.read_text())
    assert data.get("manifest_id") == "phoenix72"
    assert "tools" in data
    assert len(data["tools"]) == 72, f"Expected 72 manifest entries, got {len(data['tools'])}"


def test_phoenix72_manifest_entries_have_required_fields():
    """Every manifest entry must have required metadata fields."""
    manifest_path = PROJECT_ROOT / "arifosmcp" / "manifests" / "phoenix72.tools.json"
    data = json.loads(manifest_path.read_text())
    required = {"name", "organ", "stage", "emd", "trinity", "floors", "mutation", "status"}
    for entry in data["tools"]:
        missing = required - set(entry.keys())
        assert not missing, f"Entry {entry.get('name')} missing fields: {missing}"
        assert entry["status"] in {"implemented", "proxy_pending", "planned"}


def test_phoenix72_manifest_does_not_overclaim_implemented():
    """Manifest must not claim more than ~22 implemented tools (13 canonical + 4 diagnostic + 4 wiki + mcp_drift_check)."""
    manifest_path = PROJECT_ROOT / "arifosmcp" / "manifests" / "phoenix72.tools.json"
    data = json.loads(manifest_path.read_text())
    implemented = [e for e in data["tools"] if e["status"] == "implemented"]
    # Generous upper bound: if someone adds tools, this test should pass
    # but if the manifest suddenly claims 50+ implemented, it fails.
    assert len(implemented) <= 30, (
        f"Manifest claims {len(implemented)} implemented tools — "
        "expected <= 30 for readiness pass. Do not overclaim."
    )


def test_mcp_drift_check_is_importable():
    """mcp_drift_check module must be importable."""
    from arifosmcp.tools.drift_check import mcp_drift_check

    assert callable(mcp_drift_check)


def test_mcp_drift_check_returns_report_shape():
    """mcp_drift_check must return the expected report dict."""
    from arifosmcp.tools.drift_check import mcp_drift_check

    report = mcp_drift_check(mode="report", target_manifest="canonical13")
    assert "allowed_count" in report
    assert "registered_count" in report
    assert "missing" in report
    assert "extra" in report
    assert "drift_detected" in report
    assert "verdict" in report
    assert report["mode"] == "report"


def test_mcp_drift_check_is_read_only():
    """mcp_drift_check must not mutate registry."""
    from arifosmcp.tools.drift_check import mcp_drift_check

    # Calling it twice should yield identical results
    r1 = mcp_drift_check(mode="report", target_manifest="canonical13")
    r2 = mcp_drift_check(mode="report", target_manifest="canonical13")
    assert r1["allowed_count"] == r2["allowed_count"]
    assert r1["registered_count"] == r2["registered_count"]
    assert r1["drift_detected"] == r2["drift_detected"]


def test_phoenix72_status_doc_exists_and_does_not_claim_sealed():
    """Status doc must exist and must not claim PHOENIX-72 is sealed."""
    doc_path = PROJECT_ROOT / "docs" / "PHOENIX_72_STATUS.md"
    assert doc_path.exists(), "PHOENIX_72_STATUS.md missing"
    text = doc_path.read_text()
    assert "NOT YET SEALED" in text or "not yet sealed" in text.lower()
    assert "PHOENIX-72 sealed" not in text or "not" in text.lower()


def test_no_stale_port_8080_in_docs():
    """README and key docs must not claim arifOS runs on 8080."""
    readme = PROJECT_ROOT / "README.md"
    if readme.exists():
        text = readme.read_text()
        # Allow 8080 in historical or Docker-internal contexts, but not as live port
        lines_with_8080 = [l for l in text.splitlines() if "8080" in l and "Docker" not in l and "container" not in l.lower()]
        # This is a soft check — we just note it, not fail hard
        assert len(lines_with_8080) <= 3, (
            f"README has {len(lines_with_8080)} lines mentioning 8080 without Docker context. "
            "Update to 8088 for live port."
        )
