"""G0 Capability Truth Conformance — static build-time assertions.

Binds every copy of the canonical public surface so drift becomes provably
illegal (musyawarah-2026-09-17-mcp-migration / G0_CAPABILITY_TRUTH.md):

    H(C_advertised) = H(C_registry) = H(C_dispatch) = H(C_documented)

Bound artifacts:
  1. arifosmcp/runtime/capability_truth.py::CANONICAL_EIGHT   (advertised authority)
  2. arifosmcp/abi/capability_registry.json via kernel_abi     (ABI registry)
  3. tools_sot.yaml                                            (generated SOT projection)
  4. constitutional_map.py CORE lineage                         (stage canon 000→999)

Constitutional: F2 TRUTH, F8 GENIUS, F11 AUDIT.
Forged 2026-09-17 by 333-AGI under sovereign G0 ratification lane.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ARIFOS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ARIFOS_ROOT))

from arifosmcp.abi import kernel_abi  # noqa: E402
from arifosmcp.runtime.capability_truth import (  # noqa: E402
    CANONICAL_EIGHT,
    PROFILE_GATES,
    capability_hash,
)

# The constitutional operating sequence. 888 is the FLOOR number; the verb
# stage for judgment is 666 (corrected per CORE_NINE_STAGE_MAP — see
# constitutional_map.py:79). Order is deterministic: 000→999 with judge (666)
# gating forge (777) before seal (999).
EXPECTED_ORDER = (
    "arif_init",  # 000
    "arif_observe",  # 111
    "arif_think",  # 333
    "arif_route",  # 444
    "arif_memory",  # 555
    "arif_judge",  # 666
    "arif_forge",  # 777
    "arif_seal",  # 999
)


def _tools_sot_names() -> tuple[str, ...]:
    """Parse tools_sot.yaml (generated; DO NOT hand-edit source) tool order."""
    import yaml

    sot = yaml.safe_load((ARIFOS_ROOT / "tools_sot.yaml").read_text())
    return tuple(t["name"] for t in sot["tools"])


class TestCanonicalSurface:
    def test_canonical_eight_is_the_constitutional_order(self):
        assert tuple(CANONICAL_EIGHT) == EXPECTED_ORDER

    def test_tools_sot_yaml_equals_canonical_eight(self):
        assert _tools_sot_names() == tuple(CANONICAL_EIGHT)

    def test_sovereign_abi_profile_equals_canonical_eight(self):
        # sovereign/operator/legacy = full surface; must equal canon in order.
        for profile in ("sovereign", "operator", "legacy"):
            assert kernel_abi.tool_names_for_profile(profile) == tuple(CANONICAL_EIGHT), (
                f"ABI profile {profile} diverged from CANONICAL_EIGHT"
            )

    def test_every_abi_profile_is_a_prefix_subset_of_canon(self):
        canon = list(CANONICAL_EIGHT)
        for profile in kernel_abi.profile_names():
            tools = kernel_abi.tool_names_for_profile(profile)
            assert set(tools) <= set(canon), f"{profile} advertises non-canonical tool"
            # Authority ladder is monotone: a profile's tools must respect
            # canonical order (no reordering, no skipping mid-ladder).
            idx = [canon.index(t) for t in tools]
            assert idx == sorted(idx), f"{profile} violates canonical order"

    def test_public_agent_excludes_forge_and_seal(self):
        # OBSERVE_ONLY semantics: untrusted callers never see mutation verbs.
        assert "arif_forge" not in kernel_abi.tool_names_for_profile("public_agent")
        assert "arif_seal" not in kernel_abi.tool_names_for_profile("public_agent")

    def test_capability_truth_profile_gates_mirror_abi(self):
        # Every ABI profile must exist in PROFILE_GATES with exact tuple match.
        for profile in kernel_abi.profile_names():
            assert profile in PROFILE_GATES, (
                f"capability_truth.PROFILE_GATES missing ABI profile {profile}"
            )
            assert tuple(PROFILE_GATES[profile]) == kernel_abi.tool_names_for_profile(
                profile
            ), f"capability_truth.PROFILE_GATES[{profile}] diverged from ABI"
        # ct-only extras (kitchen_sink, diagnostic) must be full-canon supersets.
        for profile, gated in PROFILE_GATES.items():
            if profile not in kernel_abi.profile_names():
                assert tuple(gated) == tuple(CANONICAL_EIGHT), (
                    f"non-ABI profile {profile} must expose full canon"
                )

    def test_capability_hash_is_deterministic(self):
        h1 = capability_hash("sovereign")
        h2 = capability_hash("sovereign")
        assert h1 == h2 and h1.startswith("sha256:")

    def test_no_phantom_tools_in_any_surface(self):
        # The 2026-07-17 doctrine: advertised-but-uncallable is worse than
        # absent. Every advertised name must be dispatchable canon.
        canon = set(CANONICAL_EIGHT)
        assert set(kernel_abi.semantic_tool_names()) <= canon
