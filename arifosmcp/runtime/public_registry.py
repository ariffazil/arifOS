from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import tomllib

from .prompts import V2_PROMPT_SPECS
from .tool_specs import PUBLIC_RESOURCE_SPECS
from .public_surface import (
    CANONICAL_15,
    current_public_surface_mode,
    normalize_public_surface_mode,
    public_tool_names_for_mode,
)

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = ROOT / "pyproject.toml"
TOOL_REGISTRY_PATH = ROOT / "arifosmcp" / "tool_registry.json"
DEFAULT_PUBLIC_BASE_URL = "https://arifosmcp.arif-fazil.com"

CANONICAL_PUBLIC_TOOLS = frozenset(CANONICAL_15)
EXPECTED_TOOL_COUNT = len(CANONICAL_15)

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
    "arif_session_init": "Start a governed session and bind identity/context.",
    "arif_sense_observe": "Observe live signals from the environment and runtime.",
    "arif_evidence_fetch": "Fetch evidence from external or local sources with traceability.",
    "arif_mind_reason": "Run governed reasoning over evidence and active context.",
    "arif_kernel_route": "Route work through the constitutional kernel and routing policy.",
    "arif_reply_compose": "Compose a governed response aligned to active mandate and evidence.",
    "arif_memory_recall": "Recall relevant prior context and anchored memory.",
    "arif_heart_critique": "Critique a candidate action against values, risk, and floors.",
    "arif_gateway_connect": "Bridge into federated capability lanes through governed routing.",
    "arif_ops_measure": "Measure operational state, economics, and execution thermodynamics.",
    "arif_judge_deliberate": "Deliberate on a candidate action and return a verdict path.",
    "arif_vault_seal": "Record the governed outcome into the audit trail.",
    "arif_forge_execute": "Execute an approved action through the forge lane.",
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
    if name in {"arif_ping", "arif_selftest"}:
        return "diagnostic"
    return "constitutional"


def _layer_for_name(name: str) -> str:
    if name in {
        "arif_ping",
        "arif_selftest",
        "arif_session_init",
        "arif_judge_deliberate",
        "arif_vault_seal",
        "arif_forge_execute",
        "arif_gateway_connect",
    }:
        return "GOVERNANCE"
    if name in {"arif_ops_measure", "arif_kernel_route"}:
        return "MACHINE"
    return "INTELLIGENCE"


def _spec_for_name(name: str) -> Any:
    contract = _tool_registry_contracts().get(name, {})
    return SimpleNamespace(
        name=name,
        description=_TOOL_DESCRIPTIONS.get(name, "Governed arifOS MCP tool."),
        role=_role_for_name(name),
        layer=_layer_for_name(name),
        stage=contract.get("stage", "000"),
        trinity=contract.get("lane", "AGI"),
        floors=tuple(contract.get("floors", [])),
        input_schema={},
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
        "name": "arifOS-APEX-G",
        "version": release_version_label(),
        "description": (
            f"Constitutional governance server — {len(specs)} public tools in "
            f"{resolved_surface_mode} mode with F1-F13 floor enforcement."
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
    return list(public_tool_names("canonical15"))


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

    manifest = (
        build_internal_server_json(public_base_url, surface_mode or "expanded45")
        if internal
        else build_server_json(public_base_url, surface_mode)
    )
    manifest["llm_context_resource"] = "arifos://mcp/context"
    manifest["continuity_contract_version"] = "0.1.0"
    manifest["llm_context"] = build_llm_context_map()
    manifest["discovery_notes"] = [
        "Use arifos://mcp/context for full functional tool and continuity guidance.",
        "Do not infer authority from prior success; read continuity envelope on every call.",
    ]
    return manifest


def build_mcp_manifest(
    public_base_url: str = DEFAULT_PUBLIC_BASE_URL,
    surface_mode: str | None = None,
) -> dict[str, Any]:
    return build_server_json(public_base_url=public_base_url, surface_mode=surface_mode)


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
