from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import tomllib

from .prompts import V2_PROMPT_SPECS
from .tool_specs import (
    PUBLIC_RESOURCE_SPECS,
    PUBLIC_TOOL_SPECS,
    ToolSpec,
)

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = ROOT / "pyproject.toml"
DEFAULT_PUBLIC_BASE_URL = "https://arifosmcp.arif-fazil.com"

# Clean public surface: keep internal handler names private where needed.
PUBLIC_TOOL_ALIASES = {
    "arifos_kernel": "arifos_route",
}
PUBLIC_TOOL_EXCLUSIONS = set()


def _public_spec_name(name: str) -> str:
    return PUBLIC_TOOL_ALIASES.get(name, name)


def _transform_public_tool_spec(spec: ToolSpec) -> ToolSpec | None:
    if spec.name in PUBLIC_TOOL_EXCLUSIONS:
        return None
    public_name = _public_spec_name(spec.name)
    if public_name == spec.name:
        return spec
    return ToolSpec(
        name=public_name,
        stage=spec.stage,
        purpose=spec.purpose,
        role=spec.role,
        layer=spec.layer,
        description=spec.description,
        trinity=spec.trinity,
        floors=spec.floors,
        input_schema=spec.input_schema,
        visibility="public",
        default_tier=spec.default_tier,
        default_budget_tier=spec.default_budget_tier,
        min_budget_tier=spec.min_budget_tier,
        max_budget_tier=spec.max_budget_tier,
        overflow_policy=spec.overflow_policy,
        readonly=spec.readonly,
        outputs=spec.outputs,
        read_only_hint=spec.read_only_hint,
        destructive_hint=spec.destructive_hint,
        open_world_hint=spec.open_world_hint,
        idempotent_hint=spec.idempotent_hint,
    )


# Canonical public tool contract derived from tool_specs.py
CANONICAL_PUBLIC_TOOLS = frozenset(
    _public_spec_name(spec.name)
    for spec in PUBLIC_TOOL_SPECS
)
EXPECTED_TOOL_COUNT = 11

# Mandatory schema for resource discovery
RUNTIME_ENVELOPE_SCHEMA = {
    "type": "object",
    "properties": {
        "ok": {"type": "boolean"},
        "verdict": {"type": "string"},
        "payload": {"type": "object"},
    }
}


@lru_cache
def get_pyproject_metadata() -> dict[str, Any]:
    """Load metadata from pyproject.toml."""
    try:
        with open(PYPROJECT_PATH, "rb") as f:
            return tomllib.load(f).get("project", {})
    except Exception:
        return {}


def release_version_label() -> str:
    """Return the canonical version string from pyproject.toml."""
    return str(get_pyproject_metadata().get("version", "2026.04.06-FUNCTIONAL"))


def release_version() -> str:
    return release_version_label()


def public_tool_names() -> tuple[str, ...]:
    """Return the names of all public tools."""
    return tuple(spec.name for spec in public_tool_specs())


def public_tool_specs() -> tuple[ToolSpec, ...]:
    """Return all public tool specifications."""
    return tuple(
        transformed
        for spec in PUBLIC_TOOL_SPECS
        if (transformed := _transform_public_tool_spec(spec)) is not None
    )


def public_tool_spec_by_name() -> dict[str, ToolSpec]:
    """Return a map of tool names to their specifications."""
    return {spec.name: spec for spec in public_tool_specs()}


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
    """Return prompt templates exposed through the public registry."""
    return PUBLIC_PROMPT_SPECS


def is_public_profile(profile: str) -> bool:
    """Return True if the profile is a public-facing profile."""
    return profile.lower() in {"public", "chatgpt", "agnostic_public"}


def normalize_tool_profile(profile: str | None) -> str:
    """Normalize the tool profile string."""
    if not profile:
        return "public"
    return profile.lower().strip()


def build_server_json(public_base_url: str = DEFAULT_PUBLIC_BASE_URL) -> dict[str, Any]:
    """Build the canonical server.json manifest with the live public tool surface."""
    from arifosmcp.capability_map import build_llm_context_map

    public_specs = public_tool_specs()
    tools = []
    for spec in public_specs:
        tools.append(
            {
                "name": spec.name,
                "description": spec.description,
                "inputSchema": spec.input_schema,
            }
        )

    resources = []
    resource_templates = []
    for spec in PUBLIC_RESOURCE_SPECS:
        if spec.is_template:
            resource_templates.append({
                "uriTemplate": spec.uri,
                "name": spec.name,
                "description": spec.description,
                "mimeType": spec.mime_type
            })
        else:
            resources.append({
                "uri": spec.uri,
                "name": spec.name,
                "description": spec.description,
                "mimeType": spec.mime_type
            })

    prompts = []
    for spec in PUBLIC_PROMPT_SPECS:
        prompts.append({
            "name": spec.name,
            "description": spec.description,
            "arguments": spec.arguments or []
        })

    return {
        "mcpVersion": "2025-11-25",
        "name": "arifOS-APEX-G",
        "version": release_version_label(),
        "description": (
            f"Constitutional governance server — {len(public_specs)} functional arifOS tools "
            "with F1-F13 floor enforcement, metabolic routing, prompts, and resources."
        ),
        "vendor": {"name": "Muhammad Arif bin Fazil", "url": "https://arif-fazil.com"},
        "license": "AGPL-3.0-only",
        "homepage": "https://github.com/ariffazil/arifosmcp",
        "repository": "https://github.com/ariffazil/arifosmcp",
        "capabilities": {
            "constitutional_floors": 13,
            "metabolic_routing": True,
            "vault999": "postgresql+redis+merkle",
            "vector_memory": "qdrant+bge-m3-1024dim",
            "prompts": len(PUBLIC_PROMPT_SPECS),
            "resources": len(PUBLIC_RESOURCE_SPECS),
        },
        "serverUrl": public_base_url,
        "llm_context": build_llm_context_map(),
        "tools": tools,
        "resources": resources,
        "resourceTemplates": resource_templates,
        "prompts": prompts,
        "schema": {
            "input": {spec.name: spec.input_schema for spec in public_specs}
        }
    }


def get_legacy_redirect(name: str) -> tuple[str, str] | None:
    """Redirect legacy tool names to the new mega-tool surface (tool, mode)."""
    from arifosmcp.capability_map import CAPABILITY_MAP  # lazy — avoids circular import at module load
    return CAPABILITY_MAP.get(name)


def tool_names_for_profile(profile: str) -> list[str]:
    """Return tool names for a given profile."""
    if is_public_profile(profile):
        return list(public_tool_names())
    return list(public_tool_names())


def build_internal_server_json(public_base_url: str = DEFAULT_PUBLIC_BASE_URL) -> dict[str, Any]:
    """Build the internal profile manifest (includes non-public tools)."""
    return build_server_json(public_base_url=public_base_url)


def build_mcp_discovery_json(public_base_url: str = DEFAULT_PUBLIC_BASE_URL) -> dict[str, Any]:
    """Build MCP discovery manifest for internal profile endpoints."""
    from arifosmcp.capability_map import build_llm_context_map

    manifest = build_internal_server_json(public_base_url=public_base_url)
    manifest["llm_context_resource"] = "arifos://mcp/context"
    manifest["continuity_contract_version"] = "0.1.0"
    manifest["llm_context"] = build_llm_context_map()
    manifest["discovery_notes"] = [
        "Use arifos://mcp/context for full functional tool and continuity guidance.",
        "Do not infer authority from prior success; read continuity envelope on every call.",
    ]
    return manifest


def build_mcp_manifest(public_base_url: str = DEFAULT_PUBLIC_BASE_URL) -> dict[str, Any]:
    """Build the standard MCP manifest (alias for build_server_json)."""
    return build_server_json(public_base_url=public_base_url)


def verify_no_drift() -> dict[str, Any]:
    """Ensure registry matches expectations."""
    actual_names = {spec.name for spec in public_tool_specs()}
    missing = CANONICAL_PUBLIC_TOOLS - actual_names
    extra = actual_names - CANONICAL_PUBLIC_TOOLS
    is_ok = len(actual_names) == EXPECTED_TOOL_COUNT and not missing and not extra
    return {
        "ok": is_ok,
        "actual_count": len(actual_names),
        "expected_count": EXPECTED_TOOL_COUNT,
        "missing": list(missing),
        "extra": list(extra),
    }


def public_resource_uris() -> list[str]:
    return [spec.uri for spec in PUBLIC_RESOURCE_SPECS if not spec.is_template]


def public_tool_input_schemas() -> dict[str, Any]:
    return {spec.name: spec.input_schema for spec in public_tool_specs()}
