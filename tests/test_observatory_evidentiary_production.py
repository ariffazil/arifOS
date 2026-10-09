"""tests/test_observatory_evidentiary_production.py — Production regression tests for observatory evidentiary invariants.

Tests call real production functions and verify handling of unmeasured states,
accurate failure classification, and preservation of None vs 0.
"""
from __future__ import annotations

import json
import socket
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

from arifosmcp.runtime.capability_drift import (
    _registered_tools,
    compute_capability_matrix,
)
from arifosmcp.runtime.rest_routes.observatory_routes import (
    _findings_block,
    _probe_arifflow_flow_facts,
    _receipts_block,
)


class TestObservatoryEvidentiaryProduction(unittest.TestCase):

    # 1. Menguji pengeluar resit sebenar (_receipts_block)
    def test_receipts_block_head_present_without_verification(self):
        head_fixture = {
            "seq": 68,
            "verdict": "SEAL",
            "actor": "arif",
            "timestamp": "2026-10-07T07:26:41Z",
        }
        with patch.object(Path, "exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=json.dumps(head_fixture))
        ):
            block = _receipts_block()

            # Invarian: Tuntutan membaca nilai sebenar; status pengesahan kekal None/unknown
            self.assertEqual(block["head_present"]["value"], True)
            self.assertEqual(block["issuer_claim"]["value"], "SEAL")
            self.assertIsNone(block["signature_verified"]["value"])
            self.assertEqual(block["signature_verified"]["confidence"], 0.0)
            self.assertEqual(block["verification_status"]["value"], "NOT_ATTEMPTED")

    # 2. Menguji prob aliran arifFLOW semasa ralat rangkaian/tamat masa
    def test_probe_arifflow_flow_facts_handles_timeout(self):
        with patch("urllib.request.urlopen", side_effect=socket.timeout("probe timed out")):
            facts = _probe_arifflow_flow_facts()

            # Invarian: Ralat rangkaian TIDAK menghasilkan 'TIADA HALANGAN' atau 'FLOWING'
            self.assertIsNone(facts.get("receipts"))
            self.assertIsNone(facts.get("chain"))
            self.assertNotEqual(facts.get("flow_state"), "FLOWING")
            self.assertNotEqual(facts.get("bottleneck"), "TIADA HALANGAN")
            self.assertEqual(facts.get("probe_status"), "PROBE_TIMEOUT")

    # 3. Menguji pengendalian rujukan registry MCP tiada vs kosong
    def test_registered_tools_missing_vs_empty(self):
        # Kes 1: Rujukan tiada (None) -> Mesti pulangkan None (bukan set() yang menghasilkan 0)
        self.assertIsNone(_registered_tools(None))

        # Kes 2: Instans MCP sah tetapi senarai alatan kosong
        mock_mcp_empty = MagicMock()
        mock_mcp_empty._tool_registry = []
        mock_mcp_empty._tool_manager = None
        with patch(
            "arifosmcp.runtime.public_surface.public_tool_names_for_mode", return_value=[]
        ):
            res = _registered_tools(mock_mcp_empty)
            self.assertIsNotNone(res)
            self.assertEqual(len(res), 0)

    # 4. Menguji matriks keupayaan mengekalkan None apabila MCP tiada
    def test_compute_capability_matrix_preserves_none_registered_count(self):
        matrix = compute_capability_matrix(mcp=None, server_json=None)

        # Invarian: registered_count mestilah None, bukan 0
        self.assertIsNone(matrix["registered_count"])

    # 5. Menguji pengguna paparan (_findings_block) tidak menandakan drift palsu jika unmeasured
    def test_findings_block_handles_unmeasured_registered_count(self):
        caps = {
            "declared_count": 8,
            "registered_count": None,  # Unmeasured
            "exposed_count": 8,
        }
        findings = _findings_block(capabilities=caps)
        f001 = next(
            (item for item in findings.get("items", []) if item.get("id") == "F-001"),
            None,
        )

        # Invarian: Jika tiada ukuran, status F-001 mestilah UNMEASURED, bukan OPEN
        if f001:
            self.assertNotEqual(f001["status"], "OPEN")
            self.assertEqual(f001["status"], "UNMEASURED")


if __name__ == "__main__":
    unittest.main()
