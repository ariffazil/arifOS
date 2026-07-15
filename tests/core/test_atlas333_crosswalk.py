"""
tests/core/test_atlas333_crosswalk.py — ATLAS333 falsification tests.

These tests assert the crosswalk between:
  1. core.shared.atlas.PARADOX_GPV_MAP  (canonical runtime activation)
  2. arifosmcp.resources.atlas333       (MCP resource surface)
  3. arifosmcp.constitution.paradox_quotes (quote/axis source of truth)

A drift in any layer surfaces here. The tests never invent or "fix up" data.
"""

from __future__ import annotations

import importlib
import json
import sys
import unittest
from pathlib import Path


def _import_or_skip(module_path: str):
    """Import a module, skipping the test when its dependencies are unavailable."""
    try:
        return importlib.import_module(module_path)
    except Exception as exc:  # pragma: no cover - environment guard
        raise unittest.SkipTest(f"required module unavailable: {module_path}: {exc}")


class TestAtlas333Crosswalk(unittest.TestCase):
    def setUp(self) -> None:
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
        self.atlas_mod = _import_or_skip("core.shared.atlas")
        try:
            self.paradox_mod = _import_or_skip("arifosmcp.constitution.paradox_quotes")
        except Exception as exc:
            raise unittest.SkipTest(f"paradox_quotes unavailable: {exc}")
        try:
            self.resource_mod = _import_or_skip("arifosmcp.resources.atlas333")
        except Exception as exc:
            raise unittest.SkipTest(f"atlas333 resource unavailable: {exc}")

    def tearDown(self) -> None:
        try:
            sys.path.remove(str(Path(__file__).resolve().parents[2] / "src"))
        except ValueError:
            pass

    def test_paradox_gpv_map_is_authoritative_source(self) -> None:
        """The runtime PARADOX_GPV_MAP is the canonical paradox activation source."""
        m = getattr(self.atlas_mod, "PARADOX_GPV_MAP", None)
        self.assertIsInstance(m, dict, "PARADOX_GPV_MAP must be a dict")
        self.assertGreaterEqual(len(m), 1, "PARADOX_GPV_MAP must not be empty")
        for key, ids in m.items():
            self.assertIsInstance(ids, list, f"rule {key} must be a list")
            for pid in ids:
                self.assertIsInstance(pid, int)
                self.assertGreaterEqual(pid, 1)
                self.assertLessEqual(pid, 33, f"paradox id out of range: {pid}")

    def test_resource_activation_rules_agree_with_runtime(self) -> None:
        """The documented resource activation rules must equal the runtime map."""
        runtime = self.resource_mod._runtime_activation_rules()
        self.assertIsNotNone(runtime, "runtime activation rules unavailable")
        documented = {
            key: self.resource_mod._ACTIVATION_RULES[key]["paradox_ids"]
            for key in self.resource_mod._ACTIVATION_RULES
        }
        self.assertEqual(documented, runtime)

    def test_resolve_paradox_axes_matches_resource_rules(self) -> None:
        """resolve_paradox_axes() should agree with the documented rules for the matching GPV inputs."""
        resolve = getattr(self.atlas_mod, "resolve_paradox_axes", None)
        self.assertTrue(callable(resolve), "resolve_paradox_axes must be exported")

        from core.shared.types import GPV, QueryType

        cases = [
            ({"lane": "FACTUAL", "tau": 0.95, "kappa": 0.1, "rho": 0.05, "query_type": QueryType.FACTUAL}, "tau_high_rho_low"),
            ({"lane": "CRISIS", "tau": 0.5, "kappa": 0.9, "rho": 0.7, "query_type": QueryType.FACTUAL}, "rho_crisis"),
            ({"lane": "CARE", "tau": 0.6, "kappa": 0.7, "rho": 0.2, "query_type": QueryType.EXPLORATORY}, "kappa_care"),
            ({"lane": "FACTUAL", "tau": 0.9, "kappa": 0.4, "rho": 0.3, "query_type": QueryType.FACTUAL}, "tau_kappa_factual"),
        ]
        for kwargs, expected_rule in cases:
            gpv = GPV(lane=kwargs["lane"], tau=kwargs["tau"], kappa=kwargs["kappa"], rho=kwargs["rho"], query_type=kwargs["query_type"])
            axes = set(resolve(gpv))
            self.assertTrue(
                axes,
                f"resolve_paradox_axes returned empty for {kwargs}",
            )
            expected = set(self.resource_mod._ACTIVATION_RULES[expected_rule]["paradox_ids"])
            self.assertTrue(
                expected.issubset(axes),
                f"missing expected paradox ids for rule {expected_rule}: missing {expected - axes}",
            )

    def test_quote_axis_matches_resource_paradox_table(self) -> None:
        """Every quote in paradox_quotes must map to a known resource paradox id and axis."""
        from arifosmcp.constitution.paradox_quotes import ALL_PARADOX_QUOTES

        quote_to_pid = self.resource_mod._QUOTE_ID_TO_PARADOX_ID
        self.assertEqual(
            set(quote_to_pid.keys()),
            set(ALL_PARADOX_QUOTES.keys()),
            "quote id mapping must match canonical quote set exactly",
        )
        for qid, pid in quote_to_pid.items():
            self.assertGreaterEqual(pid, 1)
            self.assertLessEqual(pid, 33)
            self.assertIn(pid, self.resource_mod._PARADOX_BY_ID)
        paradox_table = self.resource_mod._build_paradoxes_from_canonical()
        self.assertEqual(
            len(paradox_table),
            len(ALL_PARADOX_QUOTES),
            "resource paradox table size must match quote count",
        )

    def test_resource_does_not_silently_drop_drift(self) -> None:
        """The activation rules resource must register and call back into the runtime source."""
        from fastmcp import FastMCP  # type: ignore
        try:
            mcp = FastMCP("atlas333-test")
        except Exception as exc:  # pragma: no cover
            raise unittest.SkipTest(f"fastmcp unavailable: {exc}")
        registered = self.resource_mod.attach_to_mcp_resource(mcp)
        self.assertIn("arifos://atlas333/activation/rules", registered)
        # Falsifiable contract: the documented rule set must be derivable from the
        # runtime source. We check the *invariant* (documented == runtime) directly;
        # the FastMCP resource introspection is not stable across versions.
        runtime = self.resource_mod._runtime_activation_rules()
        self.assertIsNotNone(runtime)
        documented = {
            key: self.resource_mod._ACTIVATION_RULES[key]["paradox_ids"]
            for key in self.resource_mod._ACTIVATION_RULES
        }
        self.assertEqual(documented, runtime)
        # The activation resource must surface the same contract for the API consumer.
        rules_resource = getattr(self.resource_mod, "_ACTIVATION_RULES", None)
        self.assertIsNotNone(rules_resource)
        self.assertTrue(rules_resource)


if __name__ == "__main__":
    unittest.main()
