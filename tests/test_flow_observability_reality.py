"""Tests reconciling FLOW PLANE / arifFLOW :7073 observability path with runtime reality.

Verifies invariants A through H:
A. missing source remains UNKNOWN
B. missing timestamp cannot yield fake freshness
C. declared endpoint cannot appear observed
D. stale fleet data cannot masquerade as fresh
E. fleet denominator/scope is explicit
F. receipt existence does not imply verification
G. TCP reachability does not imply application health
H. frontend faithfully renders evidence state without upgrading it
"""

import subprocess
from pathlib import Path

from arifosmcp.runtime.rest_routes.observatory_routes import (
    _pf,
    build_snapshot,
)
from scripts.build_public_state import project_public_state

JS_PATH = Path("/var/www/html/_shared/observatory.js")


def _run_node_test(js_snippet: str) -> None:
    cmd = [
        "node",
        "-e",
        f"""
        const vm = require('vm');
        const fs = require('fs');
        const code = fs.readFileSync('{JS_PATH}', 'utf8');
        const ctx = {{
            document: {{
                addEventListener: () => {{}},
                readyState: 'complete',
                body: {{ dataset: {{}}, setAttribute: () => {{}}, getAttribute: () => null }},
                getElementById: () => null,
                querySelector: () => null,
                querySelectorAll: () => []
            }},
            window: {{}},
            globalThis: {{}},
            console: {{ log: () => {{}}, error: () => {{}} }},
            setTimeout: () => 0,
            clearTimeout: () => {{}}
        }};
        vm.createContext(ctx);
        vm.runInContext(code, ctx);
        const api = ctx.globalThis.__ARIFOS_OBSERVATORY__;
        {js_snippet}
        """,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Node check failed: {res.stderr}"


# ── Invariant A: missing source remains UNKNOWN ──────────────────────────────────
def test_invariant_a_missing_source_remains_unknown():
    env = _pf("test_val", source="")
    assert env["source"] == ""
    _run_node_test("""
        const meta = api.metadataLine({ value: 123 });
        if (!meta.includes('source: missing')) process.exit(1);
        if (!meta.includes('confidence: unknown')) process.exit(2);
    """)


# ── Invariant B: missing timestamp cannot yield fake freshness ───────────────────
def test_invariant_b_missing_timestamp_cannot_yield_fake_freshness():
    env = _pf("test_val", source="test_src")
    assert env["age_seconds"] is None, "age_seconds must be null when observed_epoch is omitted"

    _run_node_test("""
        const meta = api.metadataLine({ value: 123, source: 'test' });
        if (!meta.includes('freshness: unavailable')) process.exit(1);
        if (meta.includes('0s old')) process.exit(2);
    """)


# ── Invariant C: declared endpoint cannot appear observed ────────────────────────
def test_invariant_c_declared_endpoint_cannot_appear_observed():
    s = JS_PATH.read_text()
    assert "confidence: 'DECLARED'" in s or 'confidence: "DECLARED"' in s
    assert "state: 'declared'" in s or 'state: "declared"' in s
    assert "evidence_class: 'declared'" in s or 'evidence_class: "declared"' in s
    assert "[DECLARED]" in s


# ── Invariant D: stale fleet data cannot masquerade as fresh ─────────────────────
def test_invariant_d_stale_fleet_data_cannot_masquerade_as_fresh():
    s = JS_PATH.read_text()
    assert "preview.observed_at || preview.generated_at" not in s
    assert "render time is not observation time" in s


# ── Invariant E: fleet denominator/scope is explicit ─────────────────────────────
def test_invariant_e_fleet_denominator_scope_is_explicit():
    dummy_snap = {"organs": {}, "observed_at": "2026-11-02T03:00:00Z"}
    dummy_health = {}
    dummy_extra = {
        "fleet_actors_tracked": 26,
        "fleet_held": 0,
        "fleet_held_actors": [],
        "fleet_held_reason": None,
        "ariflow_observed_at": "2026-11-02T03:00:00Z",
    }
    state = project_public_state(dummy_snap, dummy_health, extra=dummy_extra)
    assert "scope" in state["fleet"]
    assert "6 core organs" in state["fleet"]["scope"]

    snap = build_snapshot(None, registered_tools=set())
    assert "fleet" in snap
    assert snap["fleet"] is not None
    assert "scope" in snap["fleet"]
    assert "8 federation nodes" in snap["fleet"]["scope"]


# ── Invariant F: receipt existence does not imply verification ───────────────────
def test_invariant_f_receipt_existence_does_not_imply_verification():
    dummy_snap = {"organs": {}, "observed_at": "2026-11-02T03:00:00Z"}
    dummy_extra = {
        "ariflow_receipts": 1000,
        "ariflow_observed_at": "2026-11-02T03:00:00Z",
    }
    state = project_public_state(dummy_snap, {}, extra=dummy_extra)
    rcpt = state["ariflow"]["receipts"]
    assert isinstance(rcpt, dict)
    assert rcpt["value"] == 1000
    assert rcpt["verification_state"] == "NOT_ATTEMPTED"

    snap = build_snapshot(None, registered_tools=set())
    arifflow_organ = snap["organs"]["arifflow"]
    assert arifflow_organ["receipts"]["verification_state"] == "NOT_ATTEMPTED"


# ── Invariant G: TCP reachability does not imply application health ──────────────
def test_invariant_g_tcp_reachability_does_not_imply_application_health():
    snap = build_snapshot(None, registered_tools=set())
    arifflow_organ = snap["organs"]["arifflow"]
    assert arifflow_organ["transport"]["value"] in ("up", "unreachable")
    assert "tcp_probe" in arifflow_organ["transport"]["source"]
    assert arifflow_organ["status"]["source"].startswith("GET 127.0.0.1:7073/health")
    assert arifflow_organ["status"]["value"] == "ok-v3-vector"
    assert arifflow_organ["transport"]["source"] != arifflow_organ["status"]["source"]


# ── Invariant H: frontend faithfully renders evidence state without upgrading it ─
def test_invariant_h_frontend_faithfully_renders_evidence_state():
    _run_node_test("""
        if (api.semanticState('unknown') !== 'unknown') process.exit(1);
        if (api.semanticState('unavailable') !== 'unknown') process.exit(2);
        if (api.semanticState('missing') !== 'unknown') process.exit(3);

        const meta = api.metadataLine({
            value: 1000,
            source: 'GET 127.0.0.1:7073/health',
            confidence: 0.9,
            observed_at: '2026-11-02T03:00:00Z',
            verification_state: 'NOT_ATTEMPTED'
        });
        if (!meta.includes('verification: NOT_ATTEMPTED')) process.exit(4);
    """)
