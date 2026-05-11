from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import tomllib

from .prompts import V2_PROMPT_SPECS
from .public_surface import (
    CANONICAL_13,
    current_public_surface_mode,
    normalize_public_surface_mode,
    public_tool_names_for_mode,
)
from .tool_specs import PUBLIC_RESOURCE_SPECS

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = ROOT / "pyproject.toml"
TOOL_REGISTRY_PATH = ROOT / "arifosmcp" / "tool_registry.json"
DEFAULT_PUBLIC_BASE_URL = "https://arifosmcp.arif-fazil.com"

CANONICAL_PUBLIC_TOOLS = frozenset(CANONICAL_13)
EXPECTED_TOOL_COUNT = len(CANONICAL_13)

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
    "arif_session_init": (
        "000_INIT: Constitutional session bootstrap and identity binding. "
        "Initializes a governed session anchored to the 13-floor constitution. "
        "Modes: init (new session), status (health check), discover (list canonical tools), "
        "handover (transfer session), revoke (close session), refresh (extend TTL). "
        "F11 AUTH identity binding, F12 INJECTION sanitization, F13 SOVEREIGN veto enforced."
    ),
    "arif_sense_observe": (
        "111_SENSE: Multimodal reality observation and environmental sensing. "
        "Grounds queries in physical reality via PARSE → CLASSIFY → DECIDE → PLAN → RETRIEVE → "
        "NORMALIZE → GATE → HANDOFF protocol. Gathers raw observational data across sensory. "
        "Modes: governed (full constitutional pipeline), search (live web retrieval), "
        "ingest (store observation), compass (heading), atlas (geospatial), time (temporal). "
        "F2 TRUTH, F3 WITNESS, F4 CLARITY, F10 ONTOLOGY enforced."
    ),
    "arif_evidence_fetch": (
        "222_FETCH: Evidence-preserving web ingestion with sequential thinking. "
        "Fetches verified external evidence with full traceability chain. "
        "Supports thinking_depth (0–10), thinking_budget (0.0–10.0), sequential modes "
        "(fast/deliberate/exhaustive), and confidence_threshold early termination. "
        "Outputs ThinkingSequence + ResourceMetrics when thinking_depth > 0. "
        "F2 TRUTH source citation, F3 WITNESS verifiable evidence required."
    ),
    "arif_mind_reason": (
        "333_MIND: Symbolic constitutional reasoning kernel. "
        "Performs governed reasoning using explicit axioms from F1–F13. "
        "Modes: reason (standard AGI pipeline), sequential (multi-step constitutional chain), "
        "step/branch/merge (branching), review (export session), reflect (self-critique). "
        "Sequential thinking enforces F1–F13 at each step. "
        "Produces narrow decision_packet (operator) + full audit_packet (vault). "
        "F2 TRUTH, F4 CLARITY, F7 HUMILITY, F8 GENIUS enforced."
    ),
    "arif_kernel_route": (
        "444_KERNEL: Central orchestration, intent routing, and stage dispatch. "
        "Routes sovereign intent to the correct constitutional stage. "
        "Modes: kernel (route to metabolic lane), status (routing decision without execution). "
        "Evaluates risk_tier to determine accessible lanes. "
        "F4 CLARITY transparent intent, F11 AUTH identity verification."
    ),
    "arif_reply_compose": (
        "444_REPLY: Governed response composition with constitutional tone control. "
        "Composes human-facing replies that are truthful, clear, empathetic, and peace-preserving. "
        "Modes: compose (governed reply), rewrite (re-tone existing), analyze (tone audit). "
        "F2 TRUTH no fabrication, F5 PEACE human dignity, F6 EMPATHY consequence awareness."
    ),
    "arif_memory_recall": (
        "555_MEMORY: Associative retrieval from VAULT999 and vector memory. "
        "Recalls prior session artifacts, reasoning traces, and sealed events. "
        "Modes: vector_query (semantic search), vector_store (store), engineer (engineering), "
        "asset_store/asset_query (GEOX asset-scoped). "
        "F2 TRUTH no fabrication, F10 ONTOLOGY structural coherence, F11 AUTH identity."
    ),
    "arif_heart_critique": (
        "666_HEART: Ethical critique, risk assessment, and empathy scan. "
        "Evaluates proposed actions against 8 risk categories and F5/F6/F9. "
        "Modes: critique (identify risks/violations), simulate (predict downstream consequences). "
        "Prevents F9 ANTIHANTU manipulation, F5 PEACE dignity violations, F6 EMPATHY blindness."
    ),
    "arif_gateway_connect": (
        "666_GATEWAY: Federated cross-agent bridge and A2A mesh protocol. "
        "Connects to other constitutional agents (WEALTH, GEOX) through governed routing. "
        "Modes: connect (establish bridge), status (connection health), disconnect (close). "
        "F4 CLARITY transparent intent, F11 AUTH verified identity, F13 SOVEREIGN veto preserved."
    ),
    "arif_ops_measure": (
        "777_OPS: Resource thermodynamics, health telemetry, and metabolic monitoring. "
        "Measures operational health using entropy, Landauer limits, G-score, and ΔS. "
        "Modes: cost (Landauer gate), health (system gauge), vitals (metabolic telemetry), "
        "entropy (information-theoretic), economic_audit (WELL thermodynamic), "
        "metabolism (F1–F13 metabolic dashboard). "
        "F4 CLARITY transparent capacity, F5 PEACE resource stewardship."
    ),
    "arif_judge_deliberate": (
        "888_JUDGE: Final constitutional arbitration and verdict sealing. "
        "The apex adjudication organ. Evaluates against all 13 floors. "
        "Outputs: SEAL (proceed), PARTIAL (conditional), VOID (halt), HOLD (escalate). "
        "Four-axis: orthogonality (Ω_ortho ≥ 0.95), floor compliance, risk tier, "
        "irreversibility+entropy. F1 AMANAH, F2 TRUTH, F3 WITNESS, F9 ANTIHANTU, "
        "F10 ONTOLOGY, F12 INJECTION, F13 SOVEREIGN enforced."
    ),
    "arif_vault_seal": (
        "999_VAULT: Immutable ledger anchoring and cryptographic seal. "
        "Writes terminal verdicts to VAULT999 with Merkle-hashed integrity. "
        "Modes: append (write verdict record), read (query ledger). "
        "Filters: verdict type, session_id, since/until timestamp. "
        "F1 AMANAH accountability, F13 SOVEREIGN human veto preserved. Append-only — immutable."
    ),
    "arif_forge_execute": (
        "010_FORGE: Metabolic execution, build orchestration, and artifact forging. "
        "Executes approved actions under constitutional supervision. "
        "NEVER executes without prior arif_judge_deliberate SEAL. "
        "Modes: shell (command), api_call (REST/GraphQL), contract (smart contract), "
        "compute (distributed). "
        "Constitutional guarantees: no execution without SEAL, no self-authorization, "
        "all actions logged to vault, separation of powers preserved. "
        "F1 AMANAH, F2 TRUTH, F7 HUMILITY, F13 SOVEREIGN enforced."
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
    if name in {"arif_ping", "arif_selftest"}:
        return "diagnostic"
    return "constitutional"


def _layer_for_name(name: str) -> str:
    if name in {
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
        "protocolVersion": "2025-03-26",
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
