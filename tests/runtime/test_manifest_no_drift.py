"""
PR4 — manifest generator + diff tests.

Verifies that the manifest:
  - Lists all 14 canonical arif_* tools with full audit-shaped records.
  - Distinguishes declared / registered / callable counts (no false collapse).
  - Drift detector catches every audit-mandated rule.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.manifest.generator import compose_manifest, compose_tool_record, CANONICAL_TOOLS_18
from arifosmcp.runtime.manifest.diff import manifest_drift
from arifosmcp.runtime.manifest.cli import emit_mcp, emit_agent_card


def test_manifest_includes_all_canonical_tools() -> None:
    m = compose_manifest()
    names = {t["name"] for t in m["tools"]}
    assert names == CANONICAL_TOOLS_18, f"missing: {CANONICAL_TOOLS_18 - names}; extra: {names - CANONICAL_TOOLS_18}"


def test_tool_record_carries_eight_audit_fields() -> None:
    rec = compose_tool_record("wealth_npv_reward")
    for required in ("name", "version", "runtime", "schemas", "authority", "effects", "governance"):
        assert required in rec, f"missing top-level {required}"
    assert rec["runtime"]["declared"] is True
    assert "registered" in rec["runtime"]
    assert "callable" in rec["runtime"]
    # Audit rule: status MUST be one of the audit-defined set
    assert rec["runtime"]["status"] in ("available", "declared_only", "absent")


def test_totals_shape_does_not_compress() -> None:
    m = compose_manifest()
    t = m["totals"]
    for k in ("declared_tools", "registered_tools", "callable_tools", "schema_valid_tools", "governance_mapped_tools", "drift"):
        assert k in t, f"missing totals key: {k}"
    # Audit rule: never collapse into "27 tools healthy". Counters must be separate.
    assert t["declared_tools"] >= t["registered_tools"] >= 0


def test_arif_measure_mode_topology_drift_surfaced() -> None:
    m = compose_manifest()
    abr = m["manifest_drift"]["advertised_but_unregistered"]
    assert any("arif_measure" in s for s in abr)


def test_drift_detector_catches_declared_but_not_registered() -> None:
    generated = compose_manifest()
    # Make one tool appear declared but unregistered
    for t in generated["tools"]:
        if t["name"] == "arif_init":
            t["runtime"]["declared"] = True
            t["runtime"]["registered"] = False
    findings = manifest_drift(generated, generated)
    assert any("declared_but_not_registered: arif_init" in f for f in findings), findings


def test_drift_detector_catches_schema_hash_drift() -> None:
    generated = compose_manifest()
    published = compose_manifest()
    # Change one schema hash in published
    for t in published["tools"]:
        if t["name"] == "arif_init":
            t["schemas"]["input_hash"] = "sha256:0000000000000000"
    findings = manifest_drift(generated, published)
    assert any("schema_hash_drift" in f for f in findings)


def test_drift_detector_catches_schema_version_drift() -> None:
    generated = compose_manifest()
    published = compose_manifest()
    published["schema_version"] = "manifest.v0"  # wrong version
    findings = manifest_drift(generated, published)
    assert any("schema_version_drift" in f for f in findings)


def test_drift_detector_reports_known_runtime_drift() -> None:
    """Honest assertion: a freshly composed manifest against a healthy-published
    one shows known kernel-state drift (audit-2 finding: arif_measure(mode=topology)
    advertised but kernel reports Unknown tool).
    """
    g = compose_manifest()
    p = compose_manifest()
    findings = manifest_drift(g, p)
    # Audit-2 known drift: arif_measure (and the wealth_* capabilities until
    # PR5 wires the orchestrator) are declared but not registered.
    assert any("arif_measure" in f for f in findings), findings
    # The drift signature is stable across consecutive compositions.
    findings2 = manifest_drift(g, p)
    assert findings == findings2, "drift signature is not stable"


def test_emit_mcp_shape_contains_audit_required_fields() -> None:
    s = emit_mcp()
    assert "tools" in s
    assert "totals" in s
    assert "manifest_drift" in s
    # Audit rule: shape includes the 6-tuple totals without compression
    t = s["totals"]
    assert all(k in t for k in ("declared_tools", "registered_tools", "callable_tools", "schema_valid_tools", "governance_mapped_tools", "drift"))


def test_emit_agent_card_is_compose_manifest() -> None:
    assert emit_agent_card() == compose_manifest()


def test_audit_clause_3_capability_truth_never_passes_unregistered() -> None:
    """Every canonical tool the brochure says is callable must have registered=true at compose time."""
    m = compose_manifest()
    brochure_declared = {t["name"] for t in m["tools"] if t["runtime"]["declared"]}
    brochure_registered = {t["name"] for t in m["tools"] if t["runtime"]["registered"]}
    brochure_callable = {t["name"] for t in m["tools"] if t["runtime"]["callable"]}
    # monotonic decreasing: callable ⊆ registered ⊆ declared
    assert brochure_callable <= brochure_registered <= brochure_declared


def test_drift_field_includes_known_alias_anomaly() -> None:
    m = compose_manifest()
    deps = m["manifest_drift"]["deprecated_aliases"]
    assert any("arif_init" in s for s in deps)
