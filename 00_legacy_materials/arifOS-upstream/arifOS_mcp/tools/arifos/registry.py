"""
arifOS 13-Tool MCP Surface Registry
DITEMPA BUKAN DIBERI — 999 SEAL

This registry maps the 13 canonical tools to their implementation modules.
All organ dependencies (GEOX, WEALTH, WELL) are accessed through internal
adapters — no external MCP calls, no import2.
"""

from fastmcp import FastMCP

from .control_plane.init_000 import init_000
from .control_plane.sense_111 import sense_111
from .witness_plane.witness_222 import witness_222
from .compute_plane.mind_333 import mind_333
from .control_plane.kernel_444 import kernel_444
from .compute_plane.memory_555 import memory_555
from .compute_plane.heart_666 import heart_666
from .compute_plane.ops_777 import ops_777
from .compute_plane.judge_888 import judge_888
from .execution_plane.vault_999 import vault_999
from .execution_plane.forge import forge
from .control_plane.gateway import gateway
from .control_plane.sabar import sabar


def register_arifos_tools(server: FastMCP) -> None:
    """Register all 13 canonical arifOS tools with FastMCP server."""

    # Control Plane (000, 111, 444, gateway, sabar)
    server.tool(name="arifos_000_init")(init_000)
    server.tool(name="arifos_111_sense")(sense_111)
    server.tool(name="arifos_444_kernel")(kernel_444)
    server.tool(name="arifos_gateway")(gateway)
    server.tool(name="arifos_sabar")(sabar)

    # Witness Plane (222)
    server.tool(name="arifos_222_witness")(witness_222)

    # Compute Plane (333, 555, 666, 777, 888)
    server.tool(name="arifos_333_mind")(mind_333)
    server.tool(name="arifos_555_memory")(memory_555)
    server.tool(name="arifos_666_heart")(heart_666)
    server.tool(name="arifos_777_ops")(ops_777)
    server.tool(name="arifos_888_judge")(judge_888)

    # Execution Plane (999, forge)
    server.tool(name="arifos_999_vault")(vault_999)
    server.tool(name="arifos_forge")(forge)


def register_arifos_prompts(server: FastMCP) -> None:
    """Register 11 metabolic prompts as string templates via wrapper functions."""
    from .prompts import (
        p000_init,
        p111_sense,
        p222_witness,
        p333_mind,
        p444_kernel,
        p555_memory,
        p666_heart,
        p777_ops,
        p888_judge,
        p999_vault,
        pforge,
    )

    def _make_prompt_fn(template: str):
        def prompt_fn() -> str:
            return template

        return prompt_fn

    server.prompt(name="metabolic_000_init")(_make_prompt_fn(p000_init))
    server.prompt(name="metabolic_111_sense")(_make_prompt_fn(p111_sense))
    server.prompt(name="metabolic_222_witness")(_make_prompt_fn(p222_witness))
    server.prompt(name="metabolic_333_mind")(_make_prompt_fn(p333_mind))
    server.prompt(name="metabolic_444_kernel")(_make_prompt_fn(p444_kernel))
    server.prompt(name="metabolic_555_memory")(_make_prompt_fn(p555_memory))
    server.prompt(name="metabolic_666_heart")(_make_prompt_fn(p666_heart))
    server.prompt(name="metabolic_777_ops")(_make_prompt_fn(p777_ops))
    server.prompt(name="metabolic_888_judge")(_make_prompt_fn(p888_judge))
    server.prompt(name="metabolic_999_vault")(_make_prompt_fn(p999_vault))
    server.prompt(name="metabolic_forge")(_make_prompt_fn(pforge))


def register_arifos_resources(server: FastMCP) -> None:
    """Register 3 organ context resources."""
    from .resources import (
        geox_context_resource,
        wealth_context_resource,
        well_context_resource,
    )

    server.add_resource(geox_context_resource)
    server.add_resource(wealth_context_resource)
    server.add_resource(well_context_resource)
