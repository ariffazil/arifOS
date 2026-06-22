from __future__ import annotations

import inspect
import tomllib
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Any, get_args, get_origin

from fastmcp.tools import FunctionTool
from pydantic import TypeAdapter

from arifosmcp.constitutional_map import _TOOL_OUTPUT_SCHEMAS

from .prompts import V2_PROMPT_SPECS
from .public_surface import (
    CANARY_PROBES,
    CANONICAL_13,
    current_public_surface_mode,
    normalize_public_surface_mode,
    public_tool_names_for_mode,
)
from .tool_spec import PUBLIC_RESOURCE_SPECS

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = ROOT / "pyproject.toml"
TOOL_REGISTRY_PATH = ROOT / "arifosmcp" / "tool_registry.json"
DEFAULT_PUBLIC_BASE_URL = "https://arifosmcp.arif-fazil.com"

CANONICAL_PUBLIC_TOOLS = frozenset(CANONICAL_13)
# EXPECTED_TOOL_COUNT is the default public wire surface (canonical13 mode):
# 21 canonical kernel tools + 1 zero-floor transport canary probe = 22.
EXPECTED_TOOL_COUNT = len(CANONICAL_13) + len(CANARY_PROBES)

RUNTIME_ENVELOPE_SCHEMA = {
    "type": "object",
    "properties": {
        "ok": {"type": "boolean"},
        "verdict": {"type": "string"},
        "payload": {"type": "object"},
    },
}

_TOOL_DESCRIPTIONS: dict[str, str] = {
    "arif_ping": "Lightweight liveness probe — confirms kernel reachability.",
    "arif_selftest": "Constitutional integrity probe — verifies the floor stack is intact.",
    # ── Transport Canary Layer (Phase 0, 2026-06-14) ──
    "arif_schema_echo": (
        "CANARY: Echo back what the client sent plus the server's interpretation. "
        "Zero-floor transport diagnostic. If what you sent != what you received, "
        "the transport bridge is mangling your payload."
    ),
    "arif_version_echo": (
        "CANARY: Return MCP protocol version, supported versions, and dialect hints. "
        "Zero-floor version probe. Use to detect version-dialect drift before "
        "attempting a full session init."
    ),
    "arif_transport_echo": (
        "CANARY: Return every transport-level detail the server observed: "
        "headers, protocol, source, transport hint. Zero-floor diagnostic."
    ),
    "arif_initialize_probe": (
        "CANARY: Test MCP initialize/initialized handshake without constitutional "
        "ceremony. Simulates protocol version negotiation per MCP spec 2025-06-18. "
        "Use AFTER ping passes but BEFORE arif_init."
    ),
    # ── Canonical 13 ──
    "arif_init": (
        "Start or resume a governed constitutional session. "
        "Call this FIRST before any other tool in a new conversation. "
        "Modes: init (full binding, ~60s) | light (<1s bootstrap with tool pointers)."
    ),
    "arif_observe": (
        "Search the web, ingest URLs, check system vitals, or map a repository. "
        "Use for gathering real-world data and grounding queries in reality. "
        "Modes: search | ingest | compass | atlas | entropy_dS | vitals | repo_map."
    ),
    "arif_fetch": (
        "Fetch and preserve external evidence with source citations. "
        "Use when a claim needs verified backing or factual grounding."
    ),
    "arif_think": (
        "Multi-step reasoning, planning, and reflection with confidence labeling. "
        "Use for complex analysis, hypothesis evaluation, plan generation, and decision preparation. "
        "Modes: reason | reflect | verify | critique | plan | plan_review | plan_approve | refactor_plan | metabolize."
    ),
    "arif_kernel_route": (
        "[DEPRECATED — use arif_route] Route intent to the correct tool or federation organ. "
        "Use when unsure which tool to call next or how to delegate. "
        "Modes: route | stage | lane | list | status | surface_drift."
    ),
    "arif_compose": (
        "Compose the final response for the user. "
        "Call this LAST, after reasoning and judgment are complete. "
        "Modes: compose | style | cite | summary | format | nudge | repo_answer."
    ),
    "arif_memory": (
        "Federated memory tool — 7 canonical modes: "
        "recall | inspect | attest | remember | promote | revise | forget. "
        "Use for storing, retrieving, and governing memory across the 6-layer stack."
    ),
    "arif_memory_recall": (
        "[DEPRECATED — use arif_memory] Search past sessions, assets, sealed events, or repositories. "
        "Use for retrieving historical context, prior decisions, and codebase knowledge. "
        "Modes: recall | store | get | list | context | repo_ingest | repo_search | "
        "manage (snapshot|consolidate|forget|replay|restore — EUREKA-A KernelState OS resource manager)."
    ),
    "arif_critique": (
        "Assess ethical risks and human impact before acting. "
        "Use before irreversible, sensitive, or dignity-affecting actions. "
        "Modes: critique | simulate | empathize | redteam | maruah | deescalate | instruction_scan."
    ),
    "arif_gateway_connect": (
        "Bridge to other federation agents (GEOX, WEALTH, WELL, A-FORGE, AAA, APEX, cn-organ). "
        "Use for cross-organ tasks and multi-agent coordination."
    ),
    "arif_measure": (
        "Check system health, thermodynamic state, and resource metrics. "
        "Use for operational status and metabolic monitoring. "
        "Modes: health | vitals | cost | predict | topology | drift | stack_health | budget."
    ),
    "arif_judge": (
        "Render final constitutional verdict on a proposed action. "
        "Use when a decision is ready for arbitration and binding judgment. "
        "Modes: judge | compare | history | explain | floor_status | witness_consensus."
    ),
    "arif_seal": (
        "Seal a verdict or outcome to the immutable audit ledger. "
        "Use for final, irreversible records that must be preserved forever."
    ),
    "arif_forge": (
        "Execute approved builds, deployments, or system changes. "
        "Use ONLY after arif_judge has issued a SEAL verdict."
    ),
    # ── Rule 14 canonical expansion (2026-06-20) ──
    "arif_route": (
        "Canonical intent router. Routes a natural-language intent to the correct "
        "federation organ (GEOX, WEALTH, WELL, A-FORGE) or kernel tool. "
        "Use when you know what you want but not which tool to call."
    ),
    "arif_triage": (
        "Constitutional preflight check. Returns kernel status, current holds, "
        "and the correct lane for a proposed action before execution."
    ),
    "arif_kernel_status": (
        "[DEPRECATED — moving to arif_diag_telemetry] Kernel telemetry and discovery. "
        "Query live health, tool registry, and predictive readiness across the federation surface."
    ),
    "arif_bridge_connect": (
        "Low-level direct organ tool call. Bypasses intent routing — caller must "
        "specify organ and tool_name. Use only when both are known ahead of time. "
        "Canonical name follows arif_<noun>_<verb> convention (bridge=organ bridge, connect=verb)."
    ),
    "arif_bridge": (
        "[DEPRECATED — use arif_bridge_connect] Low-level direct organ tool call. "
        "Bypasses intent routing — caller must specify organ and tool_name. "
        "Retained for backward compatibility. Same implementation as arif_bridge_connect."
    ),
    "arif_kernel_attest": (
        "[DEPRECATED — moving to arif_diag_attest] Live organ attestation. "
        "Verify identity, tool surface, and constitutional binding for one or all federation organs."
    ),
    "arif_kernel_health": (
        "[DEPRECATED — moving to arif_diag_health] Lightweight kernel liveness probe. "
        "Returns reachability and constitutional runtime status with zero ceremony."
    ),
    "arif_conformance_report": (
        "[DEPRECATED — use arif_canary(mode=conformance_report)] "
        "PROOF MACHINE: run the ARIF Conformance Spine against the live kernel."
    ),
    "arif_canary": (
        "Unified transport diagnostic probe. One tool, six modes. "
        "Use for liveness checks, protocol version verification, schema round-trip "
        "testing, transport detail dumps, MCP handshake tests, and full conformance spine. "
        "Modes: ping | schema_echo | version_echo | transport_echo | initialize_probe | conformance_report"
    ),
    # ── ChatGPT Compatibility Shim ──
    "arif_search": (
        "Search the web for information. Use when you need to find current "
        "facts, documentation, or real-world data. Returns search results "
        "with titles, URLs, and snippets."
    ),
    "arif_fetch": (
        "Fetch content from a URL. Use when you need to read the contents "
        "of a specific webpage or document. Returns the page content as text."
    ),
}


@lru_cache(maxsize=1)
def get_pyproject_metadata() -> dict[str, Any]:
    try:
        with open(PYPROJECT_PATH, "rb") as handle:
            return tomllib.load(handle).get("project", {})
    except Exception:
        return {}


def release_version_label() -> str:
    import os

    if os.getenv("RELEASE_TAG"):
        return os.getenv("RELEASE_TAG", "")
    if os.getenv("GIT_SHA_SHORT"):
        return f"v2026.{os.getenv('GIT_SHA_SHORT', 'unknown')}"
    return str(get_pyproject_metadata().get("version", "2026.04.06-FUNCTIONAL"))


def release_version() -> str:
    return release_version_label()


@lru_cache(maxsize=1)
def _tool_registry_contracts() -> dict[str, dict[str, Any]]:
    import json

    try:
        return json.loads(TOOL_REGISTRY_PATH.read_text()).get("tools", {})
    except Exception:
        return {}


def _role_for_name(name: str) -> str:
    if name in {
        "arif_ping",
        "arif_selftest",
        "arif_schema_echo",
        "arif_version_echo",
        "arif_transport_echo",
        "arif_initialize_probe",
        "arif_conformance_report",
    }:
        return "diagnostic"
    return "constitutional"


def _layer_for_name(name: str) -> str:
    if name in {
        "arif_init",
        "arif_judge",
        "arif_seal",
        "arif_forge",
        "arif_gateway_connect",
    }:
        return "GOVERNANCE"
    if name in {
        "arif_measure",
        "arif_kernel_route",
        "arif_route",
        "arif_triage",
        "arif_kernel_status",
        "arif_bridge_connect",
        "arif_bridge",
        "arif_kernel_attest",
        "arif_kernel_health",
        "arif_memory",
        "arif_memory_recall",
        "arif_search",
        "arif_fetch",
    }:
        return "MACHINE"
    return "INTELLIGENCE"


_PLANE_STATE_SCHEMA = {
    "type": "object",
    "properties": {
        "plane": {"type": "string"},
        "state": {"type": "string"},
        "en": {"type": "string"},
    },
    "required": ["state", "en"],
}

_NINE_SIGNAL_SCHEMA = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "delta": _PLANE_STATE_SCHEMA,
        "psi": _PLANE_STATE_SCHEMA,
        "omega": _PLANE_STATE_SCHEMA,
        "overall": {
            "type": "object",
            "properties": {
                "state": {"type": "string"},
                "en": {"type": "string"},
            },
            "required": ["state", "en"],
        },
    },
}


def _allows_none(annotation: Any) -> bool:
    if annotation in (None, type(None)):
        return True
    origin = get_origin(annotation)
    if origin is None:
        return False
    return any(_allows_none(arg) for arg in get_args(annotation))


def _schema_for_annotation(annotation: Any) -> dict[str, Any]:
    if annotation is Any:
        return {"type": "object", "additionalProperties": True}
    try:
        schema = TypeAdapter(annotation).json_schema()
    except Exception:
        return {"type": "object", "additionalProperties": True}
    schema.pop("title", None)
    return schema


def _tool_result_schema(name: str) -> dict[str, Any]:
    spec = _TOOL_OUTPUT_SCHEMAS.get(name, {})
    return {
        "type": "object",
        "additionalProperties": True,
        "properties": {
            field: _schema_for_annotation(annotation) for field, annotation in spec.items()
        },
    }


def _tool_output_schema(name: str) -> dict[str, Any]:
    if name == "arif_ping":
        return {
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "build": {"type": "string"},
                "schema_version": {"type": "string"},
            },
            "required": ["ok", "build", "schema_version"],
        }
    if name in {"arif_schema_echo", "arif_version_echo", "arif_transport_echo", "arif_initialize_probe"}:
        return {
            "type": "object",
            "additionalProperties": True,
            "properties": {
                "ok": {"type": "boolean"},
                "verdict": {"type": "string"},
                "payload": {"type": "object"},
                "delta_S": {"type": "number"},
            },
        }
    return {
        "type": "object",
        "additionalProperties": True,
        "properties": {
            "status": {"type": "string"},
            "tool": {"const": name},
            "result": _tool_result_schema(name),
            "meta": {"type": "object", "additionalProperties": True},
            "delta_S": {"type": "number"},
            "timestamp": {"type": "string"},
            "session_id": {"anyOf": [{"type": "string"}, {"type": "null"}]},
            "actor_id": {"anyOf": [{"type": "string"}, {"type": "null"}]},
            "output_policy": {"type": "string"},
            "nine_signal": _NINE_SIGNAL_SCHEMA,
            "reasons": {"type": "array", "items": {"type": "string"}},
            "philosophical_anchor": {"type": "object", "additionalProperties": True},
            "stage_progression": {
                "anyOf": [
                    {"type": "null"},
                    {
                        "type": "object",
                        "properties": {
                            "current_stage": {"type": "string"},
                            "next_stage": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                            "next_tool": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                            "next_prompt": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                        },
                    },
                ],
            },
        },
        "required": [
            "status",
            "tool",
            "result",
            "meta",
            "timestamp",
            "output_policy",
            "nine_signal",
            "reasons",
        ],
    }


@lru_cache(maxsize=1)
def _runtime_contracts() -> dict[str, dict[str, Any]]:
    from arifosmcp.runtime.tools import FINAL_TOOL_IMPLEMENTATIONS, _wrap_handler

    contracts: dict[str, dict[str, Any]] = {}
    for name, handler in FINAL_TOOL_IMPLEMENTATIONS.items():
        wrapped = _wrap_handler(handler, name)
        tool = FunctionTool.from_function(
            wrapped,
            name=name,
            description=_TOOL_DESCRIPTIONS.get(name)
            or inspect.getdoc(handler)
            or "Governed arifOS MCP tool.",
            output_schema=None,
        )
        contracts[name] = {
            "description": tool.description
            or _TOOL_DESCRIPTIONS.get(name, "Governed arifOS MCP tool."),
            "input_schema": tool.parameters
            or {"type": "object", "properties": {}, "additionalProperties": False},
            "output_schema": None,
        }
    return contracts


def _spec_for_name(name: str) -> Any:
    contract = _tool_registry_contracts().get(name, {})
    runtime_contract = _runtime_contracts().get(name, {})
    return SimpleNamespace(
        name=name,
        description=runtime_contract.get(
            "description", _TOOL_DESCRIPTIONS.get(name, "Governed arifOS MCP tool.")
        ),
        role=_role_for_name(name),
        layer=_layer_for_name(name),
        stage=contract.get("stage", "000"),
        trinity=contract.get("lane", "AGI"),
        floors=tuple(contract.get("floors", [])),
        input_schema=runtime_contract.get(
            "input_schema",
            {"type": "object", "properties": {}, "additionalProperties": False},
        ),
        output_schema=runtime_contract.get("output_schema") or _tool_output_schema(name),
        visibility="public",
        access=contract.get("access", "public"),
    )


def public_tool_names(mode: str | None = None) -> tuple[str, ...]:
    return public_tool_names_for_mode(mode)


def public_tool_specs(mode: str | None = None) -> tuple[Any, ...]:
    return tuple(_spec_for_name(name) for name in public_tool_names_for_mode(mode))


def public_tool_spec_by_name(mode: str | None = None) -> dict[str, Any]:
    return {spec.name: spec for spec in public_tool_specs(mode)}


PUBLIC_TOOL_SPECS = public_tool_specs()
PUBLIC_PROMPT_SPECS = tuple(
    SimpleNamespace(
        name=spec["name"],
        description=spec["description"],
        arguments=[],
        input_schema=spec.get("input_schema", {}),
        default_tools=spec.get("default_tools", []),
        tool_choice=spec.get("tool_choice", "auto"),
    )
    for spec in V2_PROMPT_SPECS
)
PUBLIC_TOOL_SPEC_BY_NAME = public_tool_spec_by_name()


def public_prompt_specs() -> tuple[Any, ...]:
    return PUBLIC_PROMPT_SPECS


def is_public_profile(profile: str) -> bool:
    return normalize_tool_profile(profile) in {"public", "chatgpt", "agnostic_public"}


def normalize_tool_profile(profile: str | None) -> str:
    if not profile:
        return "public"
    return profile.lower().strip()


def _resources_payload() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    resources: list[dict[str, Any]] = []
    resource_templates: list[dict[str, Any]] = []
    for spec in PUBLIC_RESOURCE_SPECS:
        payload = {
            "name": spec.name,
            "description": spec.description,
            "mimeType": spec.mime_type,
        }
        if spec.is_template:
            payload["uriTemplate"] = spec.uri
            resource_templates.append(payload)
        else:
            payload["uri"] = spec.uri
            resources.append(payload)
    return resources, resource_templates


def build_server_json(
    public_base_url: str = DEFAULT_PUBLIC_BASE_URL,
    surface_mode: str | None = None,
) -> dict[str, Any]:
    from arifosmcp.capability_map import build_llm_context_map

    resolved_surface_mode = normalize_public_surface_mode(
        surface_mode or current_public_surface_mode()
    )
    specs = public_tool_specs(resolved_surface_mode)
    resources, resource_templates = _resources_payload()

    return {
        "mcpVersion": "2025-11-25",
        "protocolVersion": "2025-03-26",
        "name": "arifOS-APEX-G",
        "version": release_version_label(),
        "description": (
            f"Constitutional governance server — {len(specs)} public tools in "
            f"{resolved_surface_mode} mode with F1-L13 floor enforcement."
        ),
        "vendor": {"name": "Muhammad Arif bin Fazil", "url": "https://arif-fazil.com"},
        "license": "AGPL-3.0-only",
        "homepage": "https://github.com/ariffazil/arifosmcp",
        "repository": "https://github.com/ariffazil/arifosmcp",
        "capabilities": {
            "constitutional_floors": 13,
            "public_surface": resolved_surface_mode,
            "metabolic_routing": True,
            "vault999": "postgresql+redis+merkle",
            "vector_memory": "qdrant+bge-m3-1024dim",
            "prompts": len(PUBLIC_PROMPT_SPECS),
            "resources": len(PUBLIC_RESOURCE_SPECS),
        },
        "serverUrl": public_base_url,
        "llm_context": build_llm_context_map(),
        "tools": [
            {
                "name": spec.name,
                "description": spec.description,
                "inputSchema": spec.input_schema,
                "outputSchema": spec.output_schema,
            }
            for spec in specs
        ],
        "resources": resources,
        "resourceTemplates": resource_templates,
        "prompts": [
            {
                "name": spec.name,
                "description": spec.description,
                "arguments": spec.arguments or [],
            }
            for spec in PUBLIC_PROMPT_SPECS
        ],
        "schema": {"input": {spec.name: spec.input_schema for spec in specs}},
    }


def get_legacy_redirect(name: str) -> tuple[str, str] | None:
    from arifosmcp.capability_map import CAPABILITY_MAP

    return CAPABILITY_MAP.get(name)


def tool_names_for_profile(profile: str) -> list[str]:
    normalized = normalize_tool_profile(profile)
    if normalized in {"internal", "expanded45"}:
        return list(public_tool_names("expanded45"))
    if normalized == "canonical13":
        return list(public_tool_names("canonical13"))
    return list(public_tool_names("canonical13"))


def build_internal_server_json(
    public_base_url: str = DEFAULT_PUBLIC_BASE_URL,
    surface_mode: str | None = None,
) -> dict[str, Any]:
    return build_server_json(
        public_base_url=public_base_url,
        surface_mode=surface_mode or "expanded45",
    )


def build_mcp_discovery_json(
    public_base_url: str = DEFAULT_PUBLIC_BASE_URL,
    surface_mode: str | None = None,
    internal: bool = False,
) -> dict[str, Any]:
    from arifosmcp.capability_map import build_llm_context_map

    charter = (
        build_internal_server_json(public_base_url, surface_mode or "expanded45")
        if internal
        else build_server_json(public_base_url, surface_mode)
    )
    charter["llm_context_resource"] = "arifos://mcp/context"
    charter["continuity_contract_version"] = "0.1.0"
    charter["llm_context"] = build_llm_context_map()
    charter["discovery_notes"] = [
        "Use arifos://mcp/context for full functional tool and continuity guidance.",
        "Do not infer authority from prior success; read continuity envelope on every call.",
    ]
    return charter


def build_mcp_charter(
    public_base_url: str = DEFAULT_PUBLIC_BASE_URL,
    surface_mode: str | None = None,
) -> dict[str, Any]:
    return build_server_json(public_base_url=public_base_url, surface_mode=surface_mode)


def build_mcp_manifest(
    public_base_url: str = DEFAULT_PUBLIC_BASE_URL,
    surface_mode: str | None = None,
) -> dict[str, Any]:
    return build_mcp_discovery_json(public_base_url=public_base_url, surface_mode=surface_mode)


def verify_no_drift(mode: str | None = None) -> dict[str, Any]:
    expected = set(public_tool_names_for_mode(mode))
    actual = {spec.name for spec in public_tool_specs(mode)}
    missing = expected - actual
    extra = actual - expected
    return {
        "ok": not missing and not extra and len(actual) == len(expected),
        "actual_count": len(actual),
        "expected_count": len(expected),
        "missing": sorted(missing),
        "extra": sorted(extra),
    }


def public_resource_uris() -> list[str]:
    return [spec.uri for spec in PUBLIC_RESOURCE_SPECS if not spec.is_template]


def public_tool_input_schemas(mode: str | None = None) -> dict[str, Any]:
    return {spec.name: spec.input_schema for spec in public_tool_specs(mode)}


def public_tool_output_schemas(mode: str | None = None) -> dict[str, Any]:
    return {spec.name: spec.output_schema for spec in public_tool_specs(mode)}


def contract_status_summary(mode: str | None = None) -> dict[str, Any]:
    specs = public_tool_specs(mode)
    input_published = sum(
        1 for spec in specs if spec.input_schema and "properties" in spec.input_schema
    )
    output_published = sum(
        1 for spec in specs if spec.output_schema and "properties" in spec.output_schema
    )
    described = sum(1 for spec in specs if spec.description)
    total = len(specs)
    return {
        "tool_count": total,
        "input_schemas_published": input_published,
        "output_schemas_published": output_published,
        "descriptions_published": described,
        "schemas_complete": input_published == total and output_published == total,
        "contract_drift": not (
            input_published == total and output_published == total and described == total
        ),
    }
