"""F13 FINAL CHECKLIST Q2 — state-correction propagation falsifier (kernel mirror).

ONE scenario, FOUR layers. Human says 'itu bukan maksud saya' (that is not
what I meant) -> the system must PROVE, per layer:
  L1 memory:        old assumption REMOVED/superseded from memory
  L2 queue:         queued items built on the assumption UPDATED
  L3 planner:       planner state built on the assumption UPDATED
  L4 tool payload:  downstream payload templates / next-call args UPDATED

Absence in ANY layer = fail with the layer named.
Bounded synthetic fixtures; no real surfaces touched.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

KERNEL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KERNEL_ROOT))

from arifosmcp.runtime.f6.correction_effect import (  # noqa: E402
    CorrectionStatus,
    load_corrections,
    propagate_correction_across_layers,
    record_correction,
)

STALE_FACT_ID = "fact:X_is_42"
STALE = "X = 42"
FIXED = "X = 24"


class FourLayerWorld:
    """Synthetic model of the four downstream layers."""

    def __init__(self) -> None:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.memory = [{"fact_id": STALE_FACT_ID, "content": STALE, "stored_at": now}]
        self.queue = [{"item_id": "q-1", "assumption": STALE, "action": "send report X"}]
        self.planner = [{"plan_id": "p-1", "assumption": STALE, "step": "verify X"}]
        self.tool_payloads = [
            {"template_id": "t-1", "assumption": STALE, "verb": "report"}
        ]

    def layers(self) -> dict[str, list]:
        return {
            "L1_memory": self.memory,
            "L2_queue": self.queue,
            "L3_planner": self.planner,
            "L4_tool_payload": self.tool_payloads,
        }


def _stale_in(rows: list[dict]) -> bool:
    return any(
        r.get("assumption") == STALE or r.get("content") == STALE for r in rows
    )


class TestFourLayerCorrectionKernel(unittest.TestCase):
    """Meter 5 falsifier: 'itu bukan maksud saya' must reach all four layers."""

    def test_record_correction_alone_leaves_all_four_layers_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            world = FourLayerWorld()
            record_correction(
                "dec-1",
                "agent-v1",
                "X is 42",
                "X is 24",
                ledger_path=Path(tmp) / "c.jsonl",
            )
            stale_layers = [
                name for name, rows in world.layers().items() if _stale_in(rows)
            ]
            self.assertEqual(
                stale_layers,
                ["L1_memory", "L2_queue", "L3_planner", "L4_tool_payload"],
            )

    def test_propagate_correction_across_layers_partial_fails_with_layer_named(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            led = Path(tmp) / "c.jsonl"
            world = FourLayerWorld()
            partial_layers = {
                "L1_memory": world.memory,
                "L2_queue": world.queue,
                "L3_planner": world.planner,
            }
            out = propagate_correction_across_layers(
                decision_id="dec-1",
                agent_version="agent-v1",
                stale_value=STALE,
                corrected_value=FIXED,
                layers=partial_layers,
                ledger_path=led,
            )
            self.assertFalse(out["effect_verified"])
            self.assertIn("L4_tool_payload", out["layers_still_stale"])

    def test_propagate_correction_across_all_four_layers_verifies_effect(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            led = Path(tmp) / "c.jsonl"
            world = FourLayerWorld()
            out = propagate_correction_across_layers(
                decision_id="dec-1",
                agent_version="agent-v1",
                stale_value=STALE,
                corrected_value=FIXED,
                layers=world.layers(),
                ledger_path=led,
            )
            self.assertTrue(out["effect_verified"])
            self.assertEqual(out["layers_still_stale"], [])
            self.assertFalse(any(_stale_in(r) for r in world.layers().values()))
            rows = load_corrections(led)
            self.assertEqual(rows[-1]["status"], CorrectionStatus.EFFECT_VERIFIED.value)


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=False)
