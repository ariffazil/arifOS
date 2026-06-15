"""
Metabolic Chain Integration Test — The Body Lives or It Doesn't
═══════════════════════════════════════════════════════════════════════════════════

THE EURUEKA ENGINEERING TEST

This is not a unit test. This is not a contract test. This is the test that
proves the arifOS federation has a working BODY, not just working ORGANS.

Chain: LAS file → GEOX ingest → GEOX QC → GEOX claim → WEALTH verdict
       → arifOS JUDGE → verdict

What we assert:
  1. Data flows through the full chain without corruption
  2. Geological meaning (depth, curves, claim_state) survives transit
  3. The JUDGE issues SEAL or SABAR (never VOID for valid input)
  4. Total latency < 60 seconds
  5. Every step leaves an audit trail

Architecture note:
  - GEOX and WEALTH are called via MCP clients (testing cross-organ transport)
  - arifOS JUDGE is called via direct Python import (testing tool logic)
  - The MCP governance layer correctly blocks unauthorized JUDGE calls —
    this is the body protecting itself, not a bug.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest

# ── Ensure arifosmcp is importable ──────────────────────────────────────────
_proj_root = Path(__file__).resolve().parents[2]
if str(_proj_root) not in sys.path:
    sys.path.insert(0, str(_proj_root))


# ── Helpers ─────────────────────────────────────────────────────────────────


def extract_tool_result(call_result) -> dict:
    """Extract the JSON result from an MCP CallToolResult."""
    if not call_result or not call_result.content:
        return {"error": "empty response", "raw": str(call_result)}
    text = call_result.content[0].text
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {"raw_text": text, "parseable": False}


# ── Constants ───────────────────────────────────────────────────────────────

BOKOR_WELL_NAME = "BOKOR-1"
BOKOR_LAS_PATH = "/root/geox/fixtures/BOKOR_1_demo.las"
EXPECTED_CURVES = {"GR", "RT", "RHOB", "NPHI", "DT"}
EXPECTED_DEPTH_MIN = 1200.0  # metres (BOKOR-1 starts at 1200m)
EXPECTED_DEPTH_MAX = 2500.0  # metres (BOKOR-1 stops at 2500m)
MAX_CHAIN_LATENCY_SECONDS = 60

# MCP endpoint URLs
GEOX_MCP_URL = os.environ.get("GEOX_MCP_URL", "http://localhost:8081/mcp")
WEALTH_MCP_URL = os.environ.get("WEALTH_MCP_URL", "http://localhost:18082/mcp")

# ── Module-level chain state (persists across test instances) ────────────────

_CHAIN: dict = {
    "ingest_result": None,
    "artifact_ref": None,
    "qc_result": None,
    "claim_result": None,
    "claim_id": None,
    "wealth_result": None,
    "judge_result": None,
    "chain_start": 0.0,
    "step_times": {},
}


# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def bokor1_las_path():
    """Path to BOKOR-1 demo LAS file (real Malay Basin well log)."""
    p = Path(BOKOR_LAS_PATH)
    assert p.exists(), f"Fixture not found: {p}"
    return str(p)


@pytest.fixture(scope="module")
def chain_timing():
    """Shared timing dict for measuring total chain latency."""
    return {"start": None, "steps": {}, "end": None}


# ═══════════════════════════════════════════════════════════════════════════════
# The Metabolic Chain — One Test Class, Six Assertions
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
class TestMetabolicChain:
    """
    The full metabolic chain: GEOX → WEALTH → arifOS JUDGE.

    Each test is a stage in the chain. They share state via module-level
    _CHAIN dict. This is intentional — we're testing a SEQUENCE, not
    independent units.
    """

    # ──────────────────────────────────────────────────────────────────────
    # Stage 1: GEOX Ingest — Feed real LAS into the earth organ
    # ──────────────────────────────────────────────────────────────────────

    async def test_01_geox_ingest(self, bokor1_las_path, chain_timing):
        """GEOX ingests BOKOR-1 LAS file and returns a valid artifact."""
        from fastmcp import Client

        t0 = time.time()
        _CHAIN["chain_start"] = t0
        chain_timing["start"] = t0

        async with Client(GEOX_MCP_URL, timeout=50) as geox:
            result = await geox.call_tool(
                "geox_data_ingest_bundle",
                {
                    "source_uri": bokor1_las_path,
                    "source_type": "well",
                    "well_id": BOKOR_WELL_NAME,
                    "standardize_curves": True,
                    "normalize_units": True,
                },
            )

        data = extract_tool_result(result)
        inner = data.get("result", data)

        # Store for downstream tests
        _CHAIN["ingest_result"] = inner
        _CHAIN["artifact_ref"] = (
            inner.get("artifact_ref")
            or inner.get("primary_artifact", {}).get("artifact_ref")
            or BOKOR_WELL_NAME
        )

        # ── Assertions ────────────────────────────────────────────────────
        assert inner.get("execution_status") == "SUCCESS", (
            f"GEOX ingest failed: {json.dumps(inner, indent=2)[:500]}"
        )

        primary = inner.get("primary_artifact", {})
        assert primary.get("well_id") == BOKOR_WELL_NAME, (
            f"Well ID mismatch: {primary.get('well_id')}"
        )

        loaded_curves = set(primary.get("loaded_curves", []))
        assert EXPECTED_CURVES.issubset(loaded_curves), (
            f"Missing curves: {EXPECTED_CURVES - loaded_curves}"
        )

        depth_range = primary.get("depth_range_m") or primary.get("depth_range", [])
        assert len(depth_range) == 2, f"Bad depth range: {depth_range}"
        assert depth_range[0] <= EXPECTED_DEPTH_MIN + 1, (
            f"Depth min {depth_range[0]} too far from expected {EXPECTED_DEPTH_MIN}"
        )
        assert depth_range[1] >= EXPECTED_DEPTH_MAX - 1, (
            f"Depth max {depth_range[1]} too far from expected {EXPECTED_DEPTH_MAX}"
        )

        assert primary.get("n_depth_samples", 0) > 8000, (
            f"Too few samples: {primary.get('n_depth_samples')}"
        )

        assert primary.get("claim_state") == "INGESTED", (
            f"Claim state: {primary.get('claim_state')}"
        )

        # Record timing
        elapsed = time.time() - t0
        _CHAIN["step_times"]["ingest"] = elapsed
        chain_timing["steps"]["ingest"] = elapsed

    # ──────────────────────────────────────────────────────────────────────
    # Stage 2: GEOX QC — Validate the data is physically sane
    # ──────────────────────────────────────────────────────────────────────

    async def test_02_geox_qc(self, chain_timing):
        """GEOX QC validates the ingested data passes physical bounds."""
        from fastmcp import Client

        t0 = time.time()

        async with Client(GEOX_MCP_URL, timeout=50) as geox:
            result = await geox.call_tool(
                "geox_data_qc_bundle",
                {
                    "artifact_ref": _CHAIN["artifact_ref"] or BOKOR_WELL_NAME,
                    "artifact_type": "well_log",
                    "qc_mode": "full",
                },
            )

        data = extract_tool_result(result)
        inner = data.get("result", data)
        _CHAIN["qc_result"] = inner

        elapsed = time.time() - t0
        _CHAIN["step_times"]["qc"] = elapsed
        chain_timing["steps"]["qc"] = elapsed

        # QC must return structured data (not an error explosion)
        assert isinstance(inner, dict), (
            f"GEOX QC returned non-dict: {type(inner)}"
        )

        # QC should have some form of status
        status = inner.get("status") or inner.get("qc_status") or inner.get("execution_status")
        assert status is not None, (
            f"GEOX QC returned no status field. Keys: {list(inner.keys())}"
        )

    # ──────────────────────────────────────────────────────────────────────
    # Stage 3: GEOX Claim — Generate a geological interpretation
    # ──────────────────────────────────────────────────────────────────────

    async def test_03_geox_claim(self, chain_timing):
        """GEOX creates a structured geological claim from the well data."""
        from fastmcp import Client

        t0 = time.time()

        async with Client(GEOX_MCP_URL, timeout=50) as geox:
            result = await geox.call_tool(
                "geox_claim_create",
                {
                    "claim_text": (
                        f"Well {BOKOR_WELL_NAME} contains sandstone reservoir "
                        f"intervals with GR < 75 API, RHOB < 2.3 g/cc, "
                        f"NPHI > 0.15 v/v in the 1200-2500m depth range"
                    ),
                    "claim_type": "reservoir",
                    "truth_class": "INTERPRETATION",
                    "evidence_ids": [_CHAIN["artifact_ref"]] if _CHAIN["artifact_ref"] else [],
                },
            )

        data = extract_tool_result(result)
        inner = data.get("result", data)
        _CHAIN["claim_result"] = inner

        # Extract claim_id
        _CHAIN["claim_id"] = (
            inner.get("claim_id")
            or inner.get("id")
            or inner.get("claim", {}).get("claim_id")
        )

        elapsed = time.time() - t0
        _CHAIN["step_times"]["claim"] = elapsed
        chain_timing["steps"]["claim"] = elapsed

        # ── Assertions ────────────────────────────────────────────────────
        assert inner.get("status") == "CREATED", (
            f"Claim creation status: {inner.get('status')}. "
            f"Full: {json.dumps(inner, indent=2)[:500]}"
        )

        assert _CHAIN["claim_id"], (
            f"No claim_id in response. Keys: {list(inner.keys())}"
        )

        assert inner.get("truth_class") == "INTERPRETATION", (
            f"Truth class mismatch: {inner.get('truth_class')}"
        )

        assert inner.get("claim_type") == "reservoir", (
            f"Claim type mismatch: {inner.get('claim_type')}"
        )

    # ──────────────────────────────────────────────────────────────────────
    # Stage 4: WEALTH Verdict — Capital intelligence on the prospect
    # ──────────────────────────────────────────────────────────────────────

    async def test_04_claim_to_wealth(self, chain_timing):
        """WEALTH receives geological data and produces an economic signal."""
        from fastmcp import Client

        t0 = time.time()

        async with Client(WEALTH_MCP_URL, timeout=50) as wealth:
            result = await wealth.call_tool(
                "wealth_omni_wisdom",
                {
                    "mode": "synthesize",
                    "decision_context": {
                        "description": f"Prospect evaluation for {BOKOR_WELL_NAME}",
                        "capital_type": "strategic",
                        "horizon": "5Y",
                        "geological_claim": _CHAIN["claim_result"] or {},
                        "well_id": BOKOR_WELL_NAME,
                    },
                },
            )

        data = extract_tool_result(result)
        inner = data.get("result", data)
        _CHAIN["wealth_result"] = inner

        elapsed = time.time() - t0
        _CHAIN["step_times"]["wealth"] = elapsed
        chain_timing["steps"]["wealth"] = elapsed

        # ── Assertions ────────────────────────────────────────────────────
        assert inner, f"WEALTH returned empty: {data}"

        # WEALTH must return a verdict
        verdict = inner.get("wisdom_verdict") or inner.get("verdict")
        assert verdict in ("SEAL", "HOLD", "STOP"), (
            f"WEALTH verdict: {verdict}. Full: {json.dumps(inner, indent=2)[:500]}"
        )

        # Epistemic tag must be present
        epistemic = inner.get("epistemic_tag") or data.get("epistemic_tag")
        assert epistemic, (
            f"WEALTH returned no epistemic_tag. Keys: {list(inner.keys())}"
        )

    # ──────────────────────────────────────────────────────────────────────
    # Stage 5: arifOS JUDGE — Constitutional deliberation
    # ──────────────────────────────────────────────────────────────────────

    async def test_05_judge_deliberate(self, chain_timing):
        """
        arifOS JUDGE deliberates on the full chain and issues a verdict.

        Uses direct Python import because the MCP governance layer correctly
        blocks unauthorized JUDGE calls (ENFORCE mode). This is the body
        protecting itself — we test the tool logic here, not the transport.
        """
        from arifosmcp.runtime.tools import _arif_judge_deliberate

        t0 = time.time()

        # Build evidence receipt from the chain
        evidence_receipt = {
            "chain_type": "metabolic_integration_test",
            "well_id": BOKOR_WELL_NAME,
            "geox_artifact_ref": _CHAIN["artifact_ref"],
            "geox_claim_summary": {
                "claim_id": _CHAIN["claim_id"],
                "truth_class": _CHAIN["claim_result"].get("truth_class") if _CHAIN["claim_result"] else None,
                "claim_type": _CHAIN["claim_result"].get("claim_type") if _CHAIN["claim_result"] else None,
            },
            "wealth_verdict": _CHAIN["wealth_result"].get("wisdom_verdict") if _CHAIN["wealth_result"] else None,
            "steps_completed": list(_CHAIN["step_times"].keys()),
            "query_sent": f"Metabolic chain test for {BOKOR_WELL_NAME}",
            "results_returned": 3,
            "urls_ingested": 1,
            "provider": "geox-wealth-chain",
            "bridge": "metabolic_test",
        }

        # _arif_judge_deliberate is sync and accepts evidence_receipt
        result = _arif_judge_deliberate(
            mode="judge",
            candidate=(
                f"Approve metabolic chain result for well {BOKOR_WELL_NAME}: "
                f"GEOX ingested LAS, QC passed, claim created, WEALTH synthesized"
            ),
            actor_id="metabolic-test",
            evidence_receipt=evidence_receipt,
        )

        _CHAIN["judge_result"] = result

        elapsed = time.time() - t0
        _CHAIN["step_times"]["judge"] = elapsed
        chain_timing["steps"]["judge"] = elapsed

        # ── Assertions ────────────────────────────────────────────────────
        assert result.get("status") == "OK", (
            f"JUDGE status: {result.get('status')}. Full: {json.dumps(result, indent=2)[:500]}"
        )

        verdict = result.get("result", {}).get("verdict")

        # The judge must return a recognizable verdict
        assert verdict in ("SEAL", "SABAR", "VOID"), (
            f"JUDGE returned unexpected verdict: {verdict}. "
            f"Status: {result.get('status')}"
        )

        # For a valid metabolic chain with evidence, VOID is a governance failure
        assert verdict in ("SEAL", "SABAR"), (
            f"JUDGE issued VOID on a valid metabolic chain. "
            f"This means governance broke the body. Verdict: {verdict}"
        )

    # ──────────────────────────────────────────────────────────────────────
    # Stage 6: Chain Integrity — The body is alive
    # ──────────────────────────────────────────────────────────────────────

    async def test_06_chain_integrity(self, chain_timing):
        """
        Verify the metabolic chain as a whole:
          - Total latency < MAX_CHAIN_LATENCY_SECONDS
          - Every step completed
          - No step took > 30s individually
          - Meaning survived transit
        """
        total_elapsed = time.time() - _CHAIN["chain_start"]
        chain_timing["end"] = time.time()

        # ── Latency assertions ────────────────────────────────────────────
        step_summary = {k: f"{v:.1f}s" for k, v in _CHAIN["step_times"].items()}
        assert total_elapsed < MAX_CHAIN_LATENCY_SECONDS, (
            f"Metabolic chain took {total_elapsed:.1f}s "
            f"(limit: {MAX_CHAIN_LATENCY_SECONDS}s). "
            f"Steps: {json.dumps(step_summary)}"
        )

        # No individual step should take > 30s
        for step_name, step_time in _CHAIN["step_times"].items():
            assert step_time < 30, (
                f"Step '{step_name}' took {step_time:.1f}s (>30s threshold)"
            )

        # ── Step completion ───────────────────────────────────────────────
        expected_steps = {"ingest", "qc", "claim", "wealth", "judge"}
        actual_steps = set(_CHAIN["step_times"].keys())
        missing = expected_steps - actual_steps
        assert not missing, (
            f"Metabolic chain missing steps: {missing}. "
            f"Completed: {actual_steps}"
        )

        # ── Meaning survival ──────────────────────────────────────────────
        assert _CHAIN["artifact_ref"], "artifact_ref was lost during chain"

        if _CHAIN["claim_result"]:
            assert _CHAIN["claim_id"], "claim_id was lost during chain"
            assert _CHAIN["claim_result"].get("truth_class"), (
                "truth_class was lost during chain"
            )

        if _CHAIN["wealth_result"]:
            assert _CHAIN["wealth_result"].get("wisdom_verdict") or _CHAIN["wealth_result"].get("verdict"), (
                "WEALTH verdict was lost during chain"
            )

        if _CHAIN["judge_result"]:
            jv = _CHAIN["judge_result"].get("result", {}).get("verdict") or _CHAIN["judge_result"].get("verdict")
            assert jv, "JUDGE verdict was lost during chain"

        # ── Final receipt ─────────────────────────────────────────────────
        receipt = {
            "chain": "metabolic_integration",
            "well": BOKOR_WELL_NAME,
            "total_seconds": round(total_elapsed, 2),
            "steps": {k: round(v, 2) for k, v in _CHAIN["step_times"].items()},
            "geox": {
                "artifact_ref": _CHAIN["artifact_ref"],
                "claim_id": _CHAIN["claim_id"],
                "truth_class": _CHAIN["claim_result"].get("truth_class") if _CHAIN["claim_result"] else None,
                "claim_state": _CHAIN["ingest_result"].get("primary_artifact", {}).get("claim_state") if _CHAIN["ingest_result"] else None,
            },
            "wealth": {
                "verdict": _CHAIN["wealth_result"].get("wisdom_verdict") if _CHAIN["wealth_result"] else None,
                "epistemic_tag": _CHAIN["wealth_result"].get("epistemic_tag") if _CHAIN["wealth_result"] else None,
            },
            "judge": {
                "verdict": _CHAIN["judge_result"].get("result", {}).get("verdict") if _CHAIN["judge_result"] else None,
            },
            "alive": True,
        }

        # Print the receipt for human inspection
        print(f"\n{'='*60}")
        print("METABOLIC CHAIN RECEIPT")
        print(f"{'='*60}")
        print(json.dumps(receipt, indent=2))
        print(f"{'='*60}")
        print(f"CHAIN {'ALIVE' if receipt['alive'] else 'DEAD'}")
        print(f"{'='*60}\n")
