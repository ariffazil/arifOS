from typing import Any

try:
    from fastmcp.tools.function_tool import FunctionTool
except ImportError:
    from fastmcp.tools.tool import FunctionTool

from arifos.prompts import PROMPTS
from arifos.resources import RESOURCES
from arifos.tools import (
    forge,
    gateway,
    heart_666,
    init_000,
    judge_888,
    kernel_444,
    memory_555,
    mind_333,
    ops_777,
    sabar,
    sense_111,
    search_112,
    vault_999,
    witness_222,
)


def register_all(server: Any) -> None:
    # ── Canonical 13 tools ──────────────────────────────────────────────────
    server.tool(name="arifos_000_init")(init_000)

    # arifos_111_sense — explicit schema with constitutional constraints
    _register_sense_111(server)

    server.tool(name="arifos_112_search")(search_112)

    # arifos_222_witness — explicit schema with honest witness protocol
    _register_witness_222(server)
    server.tool(name="arifos_333_mind")(mind_333)
    server.tool(name="arifos_444_kernel")(kernel_444)
    server.tool(name="arifos_555_memory")(memory_555)
    server.tool(name="arifos_666_heart")(heart_666)
    server.tool(name="arifos_777_ops")(ops_777)
    server.tool(name="arifos_888_judge")(judge_888)
    server.tool(name="arifos_999_vault")(vault_999)
    server.tool(name="arifos_forge")(forge)
    server.tool(name="arifos_gateway")(gateway)
    server.tool(name="arifos_sabar")(sabar)

    # ── Prompts ─────────────────────────────────────────────────────────────
    for name, template in PROMPTS.items():

        def _make_prompt(text: str):
            def prompt_fn() -> str:
                return text

            return prompt_fn

        server.prompt(name=name)(_make_prompt(template))

    # ── Resources ───────────────────────────────────────────────────────────
    for uri, resource_fn in RESOURCES.items():
        server.resource(uri)(resource_fn)


def _register_witness_222(server: Any) -> None:
    """
    Register arifos_222_witness with an explicit inputSchema.

    Fixes:
      - required: ["query"] enforced at schema level
      - default: null for optional params (removes 'Option 2' UI label)
      - mode enum: ["fuse", "search"] with honest descriptions
      - Organ evidence fields: geox_evidence, wealth_evidence, well_evidence
      - if/then: search mode enables search_query field
    """
    ft = FunctionTool.from_function(
        witness_222,
        name="arifos_222_witness",
        description=(
            "Reality Verification & Consensus. "
            "Modes: fuse (default — best-available witness synthesis across GEOX/WEALTH/WELL organs) | "
            "search (external Earth witness via MiniMax web_search bridge). "
            "All tri-witness scores are honest — missing organs default to 0.5 (unknown), not phantom 0.99."
        ),
    )
    ft.parameters = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["query"],
        "properties": {
            "query": {
                "type": "string",
                "minLength": 1,
                "maxLength": 5000,
                "description": "Normalized query or claim to verify — ideally from 111_SENSE output.",
            },
            "claim": {
                "type": ["string", "null"],
                "default": None,
                "description": "Explicit claim to verify. If provided, overrides query for consensus evaluation.",
            },
            "mode": {
                "type": "string",
                "enum": ["fuse", "search", "tri-witness", "web_search"],
                "default": "fuse",
                "description": "fuse=best-available witness synthesis, search|web_search=external Earth witness via MiniMax web_search bridge, tri-witness=strict Quad-Witness consensus (GEOX/WEALTH/WELL/WEB).",
            },
            "search_query": {
                "type": ["string", "null"],
                "default": None,
                "description": "Override query for search mode. If omitted, uses query.",
            },
            "witness_required": {
                "type": "integer",
                "default": 3,
                "minimum": 1,
                "maximum": 4,
                "description": "Minimum number of witness organs required for consensus (1-4). Default 3 = tri-witness. Set 4 for full Quad-Witness (GEOX+WEALTH+WELL+WEB).",
            },
            "depth": {
                "type": "string",
                "enum": ["basic", "deep"],
                "default": "basic",
                "description": "Search depth: basic=top-3 results, deep=top-5 with snippet extraction and cross-validation.",
            },
            "geox_evidence": {
                "type": ["object", "null"],
                "default": None,
                "description": "Optional GEOX earth evidence. Fields: claim (string), confidence (number 0-1), source (string).",
            },
            "wealth_evidence": {
                "type": ["object", "null"],
                "default": None,
                "description": "Optional WEALTH economic evidence. Fields: claim (string), confidence (number), source (string).",
            },
            "well_evidence": {
                "type": ["object", "null"],
                "default": None,
                "description": "Optional WELL biological readiness evidence. Fields: claim (string), readiness_score (number 0-1), source (string).",
            },
            "session_id": {
                "type": ["string", "null"],
                "default": None,
                "description": "Active arifOS session ID for continuity.",
            },
            "operator_id": {
                "type": ["string", "null"],
                "default": None,
                "description": "Identity of the operator initiating this witness operation.",
            },
        },
        "if": {
            "properties": {"mode": {"enum": ["search", "web_search"]}},
            "required": ["mode"],
        },
        "then": {
            "properties": {
                "search_query": {
                    "type": ["string", "null"],
                    "description": "Search query for web_search mode (defaults to query/claim if null).",
                }
            }
        },
    }
    server.add_tool(ft)


def _register_sense_111(server: Any) -> None:
    """
    Register arifos_111_sense with an explicit inputSchema.

    Fixes:
      - required: ["query"] enforced at schema level
      - default: null for optional params (removes 'Option 2' UI label)
      - if/then: visual mode requires image_url
      - domain_evidence passthrough for GEOX/WELL organ integration
    """
    ft = FunctionTool.from_function(
        sense_111,
        name="arifos_111_sense",
        description=(
            "Constitutional sensing and intent classification. "
            "Modes: grounded (default — classify intent, check grounding needs) | "
            "visual (image understanding via MiniMax MCP, F2 visual grounding). "
            "All output passes through F9 Anti-Hantu governance."
        ),
    )
    ft.parameters = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["query"],
        "properties": {
            "query": {
                "type": "string",
                "minLength": 1,
                "maxLength": 5000,
                "description": "Raw user query or search prompt to ground in physical reality.",
            },
            "mode": {
                "type": "string",
                "enum": ["grounded", "visual"],
                "default": "grounded",
                "description": "Sensing mode: grounded=text-based perception (Encoder), visual=image understanding via MiniMax VLM (Encoder+Metabolizer).",
            },
            "image_url": {
                "type": ["string", "null"],
                "default": None,
                "description": "Required when mode='visual'. Must be a publicly reachable HTTPS URL.",
            },
            "snr_threshold": {
                "type": "number",
                "default": 0.85,
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Minimum Signal-to-Noise Ratio threshold for perceptual acceptance. Below this triggers SABAR cooling.",
            },
            "intent_class": {
                "type": ["string", "null"],
                "default": None,
                "description": "Optional pre-classified intent hint (constructive_execution, verification_audit, information_acquisition, strategic_design, defensive_operation).",
            },
            "domain_evidence": {
                "type": ["object", "null"],
                "default": None,
                "description": "Optional governed earth/domain evidence packet from GEOX/WELL/WELL organs.",
            },
            "session_id": {
                "type": ["string", "null"],
                "default": None,
                "description": "Active arifOS session ID for continuity.",
            },
            "operator_id": {
                "type": ["string", "null"],
                "default": None,
                "description": "Identity of the operator initiating this sensing operation.",
            },
        },
        "if": {
            "properties": {"mode": {"const": "visual"}},
            "required": ["mode"],
        },
        "then": {
            "required": ["query", "image_url"],
        },
    }
    server.add_tool(ft)
