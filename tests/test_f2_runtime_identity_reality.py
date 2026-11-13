"""F2 Runtime Identity Reality Tests (F2-01 through F2-15).

Verifies the reconciliation of F2 runtime identity, provenance preservation,
and explicit scope boundaries across public-state.v1 and observatory.v1 schemas.
Governing rule: observed != declared; build != workspace; no fake greens.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any
import pytest

from arifosmcp.runtime.rest_routes.observatory_routes import (
    _runtime_identity_block,
)
from scripts.build_public_state import (
    project_public_state,
    _wrap_identity_field,
)


def _pf(value: Any, source: str = "test", confidence: float = 0.99) -> dict[str, Any]:
    return {
        "value": value,
        "state": "observed",
        "source": source,
        "confidence": confidence,
        "observed_at": "2026-11-02T03:00:00Z",
        "evidence_class": "observed",
    }


# ── F2-01: source_commit represents deployed binary source, not workspace checkout ──
def test_f2_01_source_commit_represents_deployed_source() -> None:
    snap = {
        "runtime_identity": {
            "source_commit": _pf("deployed_source_A", source="arifOS/_collect_git_snapshot"),
            "workspace_source_commit": _pf("workspace_B", source="/root/arifOS"),
            "deployed_commit": _pf("deployed_source_A", source="/opt/arifos/app/.git_commit"),
            "build_commit": _pf("deployed_source_A", source="BUILD_INFO.build.commit"),
            "drift": _pf({
                "artifact": "ALIGNED",
                "artifact_scope": "build_vs_deployed",
                "build_vs_deployed": "ALIGNED",
                "workspace_vs_deployed": "DRIFTED",
            }),
        },
        "capabilities": {"exposed_count": 8, "degraded_count": 0},
        "observed_at": "2026-11-02T03:00:00Z",
    }
    state = project_public_state(snap, {"status": "healthy"})
    ri = state["runtime_identity"]
    # Must represent deployed binary source, not workspace checkout
    assert ri["source_commit"]["value"] == "deployed_source_A"
    assert ri["source_commit"]["source"] == "arifOS/_collect_git_snapshot"


# ── F2-02: workspace_source_commit explicitly exposes checkout HEAD with provenance ──
def test_f2_02_workspace_source_commit_explicitly_exposed() -> None:
    snap = {
        "runtime_identity": {
            "source_commit": _pf("deployed_A"),
            "workspace_source_commit": _pf("workspace_B", source="/root/arifOS"),
            "deployed_commit": _pf("deployed_A"),
            "build_commit": _pf("deployed_A"),
        },
        "observed_at": "2026-11-02T03:00:00Z",
    }
    state = project_public_state(snap, {"status": "healthy"})
    ri = state["runtime_identity"]
    assert "workspace_source_commit" in ri
    assert ri["workspace_source_commit"]["value"] == "workspace_B"
    assert ri["workspace_source_commit"]["source"] == "/root/arifOS"


# ── F2-03: deployed_commit preserves metadata envelope ──
def test_f2_03_deployed_commit_preserves_envelope() -> None:
    snap = {
        "runtime_identity": {
            "deployed_commit": _pf("7371c84", source="/opt/arifos/app/.git_commit or HEAD", confidence=0.99),
        },
        "observed_at": "2026-11-02T03:00:00Z",
    }
    state = project_public_state(snap, {"status": "healthy"})
    dep = state["runtime_identity"]["deployed_commit"]
    assert isinstance(dep, dict)
    assert dep["value"] == "7371c84"
    assert dep["source"] == "/opt/arifos/app/.git_commit or HEAD"
    assert dep["confidence"] == 0.99


# ── F2-04: build_commit preserves metadata envelope ──
def test_f2_04_build_commit_preserves_envelope() -> None:
    snap = {
        "runtime_identity": {
            "build_commit": _pf("7371c84", source="BUILD_INFO.build.commit", confidence=0.99),
        },
        "observed_at": "2026-11-02T03:00:00Z",
    }
    state = project_public_state(snap, {"status": "healthy"})
    bld = state["runtime_identity"]["build_commit"]
    assert isinstance(bld, dict)
    assert bld["value"] == "7371c84"
    assert bld["source"] == "BUILD_INFO.build.commit"
    assert bld["confidence"] == 0.99


# ── F2-05: Anti-regression: workspace=B, build=A, deployed=A ──
def test_f2_05_anti_regression_workspace_b_build_a_deployed_a() -> None:
    snap = {
        "runtime_identity": {
            "source_commit": _pf("commit_A"),
            "workspace_source_commit": _pf("commit_B"),
            "workspace_dirty": _pf(False),
            "deployed_commit": _pf("commit_A"),
            "build_commit": _pf("commit_A"),
            "drift": _pf({
                "artifact": "ALIGNED",
                "artifact_scope": "build_vs_deployed",
                "build_vs_deployed": "ALIGNED",
                "workspace_vs_deployed": "DRIFTED",
            }),
        },
        "observed_at": "2026-11-02T03:00:00Z",
    }
    state = project_public_state(snap, {"status": "healthy"})
    ri = state["runtime_identity"]
    drift_val = ri["drift"]["value"]

    # Build and deployed match
    assert drift_val["build_vs_deployed"] == "ALIGNED"
    assert drift_val["artifact"] == "ALIGNED"
    assert drift_val["artifact_scope"] == "build_vs_deployed"

    # Workspace and deployed differ
    assert drift_val["workspace_vs_deployed"] == "DRIFTED"
    assert state["release"]["deployment_alignment"] == "DRIFTED"


# ── F2-06: artifact drift scope is explicitly build_vs_deployed ──
def test_f2_06_artifact_scope_explicitly_build_vs_deployed() -> None:
    block = _runtime_identity_block()
    drift = block["drift"]["value"]
    assert "artifact_scope" in drift
    assert drift["artifact_scope"] == "build_vs_deployed"


# ── F2-07: artifact=ALIGNED does not mask workspace drift ──
def test_f2_07_artifact_aligned_does_not_mask_workspace_drift() -> None:
    snap = {
        "runtime_identity": {
            "source_commit": _pf("commit_A"),
            "workspace_source_commit": _pf("commit_B"),
            "workspace_dirty": _pf(False),
            "deployed_commit": _pf("commit_A"),
            "build_commit": _pf("commit_A"),
        },
        "observed_at": "2026-11-02T03:00:00Z",
    }
    state = project_public_state(snap, {"status": "healthy"})
    drift_val = state["runtime_identity"]["drift"]["value"]
    assert drift_val["artifact"] == "ALIGNED"
    assert drift_val["workspace_vs_deployed"] == "DRIFTED"


# ── F2-08: schema drift remains honest UNKNOWN ──
def test_f2_08_schema_drift_remains_honest_unknown() -> None:
    block = _runtime_identity_block()
    drift = block["drift"]["value"]
    assert drift["schema"] == "UNKNOWN"


# ── F2-09: route drift remains honest UNKNOWN ──
def test_f2_09_route_drift_remains_honest_unknown() -> None:
    block = _runtime_identity_block()
    drift = block["drift"]["value"]
    assert drift["route"] == "UNKNOWN"


# ── F2-10: upstream_repository remains honest UNVERIFIED ──
def test_f2_10_upstream_repository_remains_honest_unverified() -> None:
    block = _runtime_identity_block()
    drift = block["drift"]["value"]
    assert drift["upstream_repository"] == "UNVERIFIED"


# ── F2-11: capability drift reflects degraded count ──
def test_f2_11_capability_drift_reflects_degraded_count() -> None:
    # 0 degraded -> ALIGNED
    snap_ok = {
        "runtime_identity": {},
        "capabilities": {"exposed_count": 8, "degraded_count": 0},
    }
    state_ok = project_public_state(snap_ok, {})
    assert state_ok["runtime_identity"]["drift"]["value"]["capability"] == "ALIGNED"

    # >0 degraded -> DRIFTED
    snap_deg = {
        "runtime_identity": {},
        "capabilities": {"exposed_count": 8, "degraded_count": 2},
    }
    state_deg = project_public_state(snap_deg, {})
    assert state_deg["runtime_identity"]["drift"]["value"]["capability"] == "DRIFTED"


# ── F2-12: forge_registry drift remains independent ──
def test_f2_12_forge_registry_drift_present() -> None:
    block = _runtime_identity_block()
    drift = block["drift"]["value"]
    assert "forge_registry" in drift
    assert drift["forge_registry"] in {"ALIGNED", "DRIFTED", "UNKNOWN"}


# ── F2-13: build_public_state retains full envelopes without pf_value stripping ──
def test_f2_13_public_state_retains_full_envelopes() -> None:
    snap = {
        "runtime_identity": {
            "source_commit": _pf("sha_src", source="src_provider", confidence=0.95),
            "deployed_commit": _pf("sha_dep", source="dep_provider", confidence=0.98),
            "build_commit": _pf("sha_bld", source="bld_provider", confidence=0.97),
            "deployment_mode": _pf("container", source="mode_provider", confidence=0.85),
        },
        "observed_at": "2026-11-02T03:00:00Z",
    }
    state = project_public_state(snap, {})
    ri = state["runtime_identity"]
    assert isinstance(ri["source_commit"], dict)
    assert ri["source_commit"]["source"] == "src_provider"
    assert ri["deployed_commit"]["source"] == "dep_provider"
    assert ri["build_commit"]["source"] == "bld_provider"
    assert ri["deployment_mode"]["source"] == "mode_provider"


# ── Helper for Node.js DOM rendering of observatory.js ──
def _run_node_identity_render(state_payload: dict[str, Any]) -> dict[str, Any]:
    js_path = "/var/www/html/_shared/observatory.js"
    payload_json = json.dumps(state_payload)
    node_code = f"""
    const vm = require('vm');
    const fs = require('fs');
    const code = fs.readFileSync('{js_path}', 'utf8');

    const elements = {{}};
    function getEl(id) {{
        if (!elements[id]) {{
            elements[id] = {{
                id: id,
                textContent: '',
                innerHTML: '',
                className: '',
                dataset: {{}},
                style: {{}},
                setAttribute: () => {{}},
                getAttribute: () => null,
            }};
        }}
        return elements[id];
    }}

    const ctx = {{
        document: {{
            addEventListener: () => {{}},
            readyState: 'complete',
            body: {{ dataset: {{}}, setAttribute: () => {{}}, getAttribute: () => null }},
            getElementById: (id) => getEl(id),
            querySelector: (sel) => {{
                if (sel && sel.startsWith('#')) return getEl(sel.slice(1));
                return null;
            }},
            querySelectorAll: () => []
        }},
        window: {{}},
        globalThis: {{}},
        console: {{ log: () => {{}}, error: () => {{}} }},
        setTimeout: () => 0,
        clearTimeout: () => {{}},
        fetch: () => Promise.resolve({{ ok: false, status: 500 }})
    }};
    vm.createContext(ctx);
    vm.runInContext(code, ctx);

    const api = ctx.globalThis.__ARIFOS_OBSERVATORY__;
    const payload = {payload_json};
    api.renderIdentity(payload);

    const result = {{}};
    for (const [k, v] of Object.entries(elements)) {{
        result[k] = {{
            text: v.textContent,
            html: v.innerHTML,
        }};
    }}
    console.log(JSON.stringify(result));
    """
    res = subprocess.run(["node", "-e", node_code], capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


# ── F2-14: observatory.js renders drift with full provenance, not source: missing ──
def test_f2_14_observatory_renders_drift_provenance() -> None:
    payload = {
        "observed_at": "2026-11-02T03:00:00Z",
        "runtime_identity": {
            "source_commit": _pf("7371c84", source="arifOS/_collect_git_snapshot"),
            "deployed_commit": _pf("7371c84", source="/opt/arifos/app/.git_commit"),
            "build_commit": _pf("7371c84", source="BUILD_INFO.build.commit"),
            "drift": {
                "value": {
                    "artifact": "ALIGNED",
                    "artifact_scope": "build_vs_deployed",
                    "build_vs_deployed": "ALIGNED",
                    "workspace_vs_deployed": "DRIFTED",
                    "capability": "ALIGNED",
                    "forge_registry": "ALIGNED",
                    "schema": "UNKNOWN",
                    "route": "UNKNOWN",
                    "upstream_repository": "UNVERIFIED",
                },
                "source": "_compute_runtime_drift + capability_matrix",
                "confidence": 0.9,
                "observed_at": "2026-11-02T03:00:00Z",
            },
        },
    }
    rendered = _run_node_identity_render(payload)
    drift_note = rendered.get("id-drift-note", {}).get("text", "")
    assert "source: _compute_runtime_drift + capability_matrix" in drift_note
    assert "confidence: 0.9" in drift_note
    assert "source: missing" not in drift_note


# ── F2-15: observatory.js scalar fallback derives from parent metadata honestly ──
def test_f2_15_observatory_scalar_fallback_derives_honestly() -> None:
    payload = {
        "observed_at": "2026-11-02T03:00:00Z",
        "source": "snapshot.runtime_identity+release",
        "runtime_identity": {
            # Bare scalars without individual envelope
            "source_commit": "7371c84",
            "deployed_commit": "7371c84",
            "build_commit": "7371c84",
            "source": "snapshot.runtime_identity",
            "confidence": 0.88,
            "observed_at": "2026-11-02T03:00:00Z",
        },
    }
    rendered = _run_node_identity_render(payload)
    src_note = rendered.get("id-source-note", {}).get("text", "")
    assert "source: snapshot.runtime_identity" in src_note
    assert "confidence: 0.88" in src_note
    assert "source: missing" not in src_note
