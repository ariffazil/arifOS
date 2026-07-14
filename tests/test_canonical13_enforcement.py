"""Migration lock: numeric canon names cannot resurrect old public verbs."""

from __future__ import annotations

from arifosmcp.constitutional_map import CANONICAL_TOOLS
from arifosmcp.runtime.public_surface import (
    CANONICAL_7,
    CANONICAL_9,
    CANONICAL_12,
    CANONICAL_13,
    KERNEL_ABI_8,
)


def test_kernel_abi_provider_set_is_locked_to_eight() -> None:
    assert len(KERNEL_ABI_8) == 8
    assert set(KERNEL_ABI_8) == {
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_memory",
        "arif_judge",
        "arif_forge",
        "arif_seal",
    }


def test_deprecated_numeric_constants_resolve_to_the_abi() -> None:
    assert CANONICAL_7 == CANONICAL_9 == CANONICAL_12 == CANONICAL_13 == KERNEL_ABI_8


def test_only_abi_bindings_are_non_internal_kernel_tools() -> None:
    discoverable = {name for name, spec in CANONICAL_TOOLS.items() if spec.get("access") != "internal_only"}
    assert discoverable == set(KERNEL_ABI_8)


def test_absorbed_verbs_are_internal_stages() -> None:
    for name in {
        "arif_bridge_connect",
        "arif_critique",
        "arif_compose",
        "arif_verify",
        "arif_entropy_observe",
        "arif_j_state_assess",
        "arif_correction_probe",
        "arif_consequence_trace",
        "arif_entropy_route",
        "arif_j_gate",
    }:
        assert CANONICAL_TOOLS[name]["access"] == "internal_only"
        assert CANONICAL_TOOLS[name]["expose"] is False
