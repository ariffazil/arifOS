from __future__ import annotations

import inspect
import tomllib
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Any, get_args, get_origin

from fastmcp.tools import FunctionTool
from pydantic import TypeAdapter

from arifosmcp.abi.kernel_abi import capability_ids, normalize_profile, validate_abi
from arifosmcp.constitutional_map import _TOOL_OUTPUT_SCHEMAS
from arifosmcp.registry import get_prompt_specs_for_charter as _get_prompt_specs_for_charter

from .public_surface import (
    KERNEL_ABI_8,
    PUBLIC_AGENT_6,
    current_public_surface_mode,
    normalize_public_surface_mode,
    public_tool_names_for_mode,
)
from .tool_spec import PUBLIC_RESOURCE_SPECS

V2_PROMPT_SPECS = _get_prompt_specs_for_charter()  # sourced from single-source-of-truth registry

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = ROOT / "pyproject.toml"
TOOL_REGISTRY_PATH = ROOT / "arifosmcp" / "tool_registry.json"
DEFAULT_PUBLIC_BASE_URL = "https://mcp.arif-fazil.com/mcp"

CANONICAL_PUBLIC_TOOLS = frozenset(PUBLIC_AGENT_6)
EXPECTED_TOOL_COUNT = len(PUBLIC_AGENT_6)

RUNTIME_ENVELOPE_SCHEMA = {
    "type": "object",
    "properties": {
        "ok": {"type": "boolean"},
        "verdict": {"type": "string"},
        "payload": {"type": "object"},
    },
}

_TOOL_DESCRIPTIONS: dict[str, str] = {
    # ═══════════════════════════════════════════════════════════════════════
    # arifOS KERNEL VERBS (MCP "tools" = transport envelope only)
    # These are constitutional stages of the kernel metabolic loop — not
    # general-purpose plugins. Visibility on MCP ≠ authority to mutate.
    # Pattern: KERNEL stage · what · authority · select · returns · skip
    # Public wire = 12 verbs (CANONICAL-12). Order agents: init → triage/
    # observe → route → think/critique → judge → forge → seal → compose.
    # ═══════════════════════════════════════════════════════════════════════
    # ── Diagnostic Probes ──────────────────────────────────────────────────
    "arif_ping": (
        "KERNEL probe · transport liveness only (not a session). "
        "Select when another kernel call failed on connection. "
        "Returns build + schema + ok. Prefer arif_init(mode=ping) for constitutional probe."
    ),
    "arif_selftest": (
        "KERNEL probe · floor-stack integrity. "
        "Select after deploy or suspected floor drift. Returns per-floor pass/fail."
    ),
    # ── Transport Canary Layer (Phase 0, 2026-06-14) ──
    "arif_schema_echo": (
        "KERNEL canary · payload round-trip. Zero floors. "
        "Select when schema validation errors suggest transport mangling."
    ),
    "arif_version_echo": (
        "KERNEL canary · MCP protocol version negotiation. "
        "Use before full arif_init if client/server dialect drift is suspected."
    ),
    "arif_transport_echo": ("KERNEL canary · observed headers/protocol/source. Zero floors."),
    "arif_initialize_probe": (
        "KERNEL canary · MCP initialize handshake without constitutional ceremony. "
        "After ping, before arif_init."
    ),
    # ── 000 INIT ────────────────────────────────────────────────────────────
    "arif_init": (
        "KERNEL 000 · Session ignition — not a helper app. Binds actor, floors, and audit "
        "before any other arif_* verb can govern. Without session_id, kernel treats you as "
        "anonymous (OBSERVE_ONLY / SYUBHAH). "
        "Authority: pre-session open; light/init mint session_id + authority band. "
        "Modes: ping | light | init | resume | validate | epoch_open | epoch_seal | canary | "
        "preflight | triage. "
        "Returns: session_id, actor_verified, authority, allowed_next_verbs, next_tool. "
        "Skip when live session already bound → arif_triage; pure facts only → arif_observe."
    ),
    # ── 000 TRIAGE (session immune, not intent router) ─────────────────────
    "arif_triage": (
        "KERNEL 000 · Session preflight / immune status — not intent routing. "
        "Select to read active session stage, holds, priority, next safe kernel verb. "
        "Authority: L0 with session. Modes: status | preflight | triage. "
        "Do NOT use for organ choice — that is arif_route. "
        "Returns: active_sessions, stage, next_safe_action."
    ),
    # ── 111 OBSERVE ─────────────────────────────────────────────────────────
    "arif_observe": (
        "KERNEL 111 · Sense reality into evidence (not reasoning, not judgment). "
        "Web/URL/vitals/repo/entropy with epistemic tags. "
        "Authority: L0 OBSERVE. Modes: search | fetch | ingest | compass | atlas | "
        "entropy_dS | vitals | repo_map | hybrid_discovery. "
        "Returns: evidence + sources + uncertainty. "
        "Skip when pure reasoning → arif_think; domain compute → arif_route to GEOX/WEALTH/WELL."
    ),
    "arif_sense_observe": (
        "[alias → arif_observe] KERNEL 111 sense. Prefer canonical name arif_observe."
    ),
    # ── 222 EVIDENCE (folded; keep mode=fetch on observe) ───────────────────
    "arif_fetch": (
        "KERNEL evidence fetch (prefer arif_observe mode=fetch). "
        "URL/source retrieval with provenance. Not a general browser tool."
    ),
    "arif_evidence_fetch": (
        "[alias → arif_fetch / arif_observe] Evidence preserve. Prefer arif_observe."
    ),
    # ── 333 THINK ───────────────────────────────────────────────────────────
    "arif_think": (
        "KERNEL 333 · Mind — structure reasoning under F2/F7 (not a chat model, not a verdict). "
        "Plan, reflect, verify, synthesize with OBS/DER/INT/SPEC labels. "
        "Authority: L0–L1. Modes: reason | reflect | verify | plan | plan_review | "
        "plan_approve | refactor_plan | metabolize | axioms. "
        "Returns: structured reasoning + confidence + next_safe_action. "
        "Ethical/maruah risk → arif_critique. Binding decision → arif_judge. Facts → arif_observe."
    ),
    "arif_mind_reason": ("[alias → arif_think] KERNEL 333 mind. Prefer canonical name arif_think."),
    # ── 444 ROUTE ───────────────────────────────────────────────────────────
    "arif_route": (
        "KERNEL 444 · Intent→organ router (default path to GEOX/WEALTH/WELL/A-FORGE). "
        "Select when you know the goal but not which organ/verb. "
        "Optional organ_tool+arguments = governed bridge call (prefer this over "
        "arif_bridge_connect). Authority: L0. Returns: organ, port, tool_prefix, suggested_tools. "
        "Not session preflight (use arif_triage). Not a free shell."
    ),
    "arif_kernel_route": ("[DEPRECATED → arif_route] Legacy KERNEL 444 entry."),
    # ── 444 BRIDGE (internal-ish; agents prefer route) ──────────────────────
    "arif_bridge_connect": (
        "KERNEL 444-direct · Calls a pre-authorized organ tool directly after "
        "server-side authorization and policy validation. Requires organ + tool_name. "
        "Agents should prefer arif_route (same reach, safer default). "
        "Only federation organs under kernel envelope; not a generic proxy."
    ),
    "arif_bridge": ("[DEPRECATED → arif_bridge_connect] Direct organ bridge."),
    # ── 555 CRITIQUE ────────────────────────────────────────────────────────
    "arif_critique": (
        "KERNEL 555 · Heart — ethical/dignity/risk stress before judgment (not SEAL). "
        "Select when blast_radius MEDIUM+, human/dignity impact, or irreversible risk. "
        "Requires non-empty target (proposal/plan text). "
        "Authority: L1. Modes: critique | redteam | maruah | deescalate | empathize | "
        "simulate | instruction_scan. Returns: risk, floors, human impact. "
        "Skip pure technical with zero human stake. Binding verdict → arif_judge."
    ),
    "arif_heart_critique": ("[alias → arif_critique] KERNEL 555 heart. Prefer arif_critique."),
    # ── MEMORY (cross-cutting governor) ─────────────────────────────────────
    "arif_memory": (
        "KERNEL memory governor · L1–L6 stack under F1/F2/F4/F11 (not a free notepad). "
        "Recall/inspect free-ish; remember/promote/revise/forget are J-space mutations. "
        "Authority: recall L0; writes gated. Modes: recall | inspect | attest | remember | "
        "promote | revise | forget. Skip ephemeral one-off facts."
    ),
    "arif_memory_recall": ("[alias → arif_memory] Prefer canonical arif_memory."),
    # ── 666 JUDGE ───────────────────────────────────────────────────────────
    "arif_judge": (
        "KERNEL 888 · Constitutional verdict — only organ that SEAL/HOLD/SABAR/VOIDs. "
        "Not advice; binding arbitration of floors + authority. "
        "Authority: 888_HOLD / SOVEREIGN session required for real adjudicate. "
        "REQUIRES: actor, intent, domain, reversibility_level, blast_radius (+ evidence). "
        "Modes: judge | compare | history | explain | floor_status | witness_consensus. "
        "Skip if evidence incomplete → arif_observe; plan incomplete → arif_think; "
        "reversible low-risk advisory only."
    ),
    "arif_judge_deliberate": ("[alias/internal → arif_judge] Prefer public arif_judge."),
    # ── 777 FORGE ───────────────────────────────────────────────────────────
    "arif_forge": (
        "KERNEL 777 · Execution gate via A-FORGE (hands, not law). "
        "Mutates only after arif_judge SEAL + lease/chain IDs — no self-authorize. "
        "Authority: 888_HOLD without SEAL. Modes include dry_run | engineer | query | write. "
        "Public execution verb (arif_act is internal alias only). "
        "Skip while still planning (arif_think) or without judge SEAL."
    ),
    "arif_forge_execute": ("[alias → arif_forge] Prefer arif_forge."),
    "arif_act": (
        "[INTERNAL alias → arif_forge] Not on public kernel facade. Call arif_forge after SEAL."
    ),
    # ── 888 COMPOSE ─────────────────────────────────────────────────────────
    "arif_compose": (
        "KERNEL reply · Final human-facing composition (citations, tone, ΔS≤0). "
        "Call LAST after observe/think/judge — not mid-pipeline. "
        "Authority: L0–L1. Modes: compose | summarize | cite | tone_shift | style | format. "
        "Not a substitute for arif_judge or arif_seal."
    ),
    "arif_reply_compose": ("[alias → arif_compose] Prefer arif_compose."),
    # ── 999 SEAL ────────────────────────────────────────────────────────────
    "arif_seal": (
        "KERNEL 999 · VAULT999 immutable append — civilizational memory, irreversible. "
        "Authority: 888_HOLD / SOVEREIGN + ack_irreversible for seal mode. "
        "Modes: seal | verify | chain | list | dry_run | seal_card | render. "
        "Seal only after SEAL verdict path; HOLD/SABAR/VOID do not seal. "
        "Testing → dry_run. Kernel judges; vault seals; Arif owns F13 veto."
    ),
    "arif_vault_seal": ("[alias → arif_seal] Prefer arif_seal."),
    # ── Gateway / measure (non-public helpers) ──────────────────────────────
    "arif_gateway_connect": (
        "KERNEL federation gateway (legacy). Prefer arif_route for organ selection."
    ),
    "arif_measure": (
        "KERNEL ops measure (internal). Prefer arif_observe(mode=vitals) on public surface."
    ),
    "arif_ops_measure": ("[alias → arif_measure] Internal ops measure."),
    "arif_kernel_status": (
        "[DEPRECATED] Kernel telemetry. Prefer arif_triage / arif_observe(mode=vitals)."
    ),
    "arif_kernel_attest": ("[DEPRECATED] Organ attestation diagnostic."),
    "arif_kernel_health": ("[DEPRECATED] Kernel liveness. Prefer arif_init(mode=ping)."),
    "arif_conformance_report": (
        "[DEPRECATED → arif_canary mode=conformance_report] Conformance spine."
    ),
    "arif_canary": (
        "KERNEL transport diagnostic (not constitutional work). "
        "Modes: ping | schema_echo | version_echo | transport_echo | initialize_probe | "
        "conformance_report. Zero floors."
    ),
    # ── ChatGPT Compatibility Shim ──
    "arif_search": ("Compat search → prefer KERNEL arif_observe(mode=search)."),
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
    if name in {
        "arif_schema_echo",
        "arif_version_echo",
        "arif_transport_echo",
        "arif_initialize_probe",
    }:
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
            or "Governed arifOS kernel verb (MCP transport envelope).",
            output_schema=None,
        )
        input_schema = tool.parameters
        if input_schema is None:
            input_schema = {"type": "object", "properties": {}, "additionalProperties": False}
        elif isinstance(input_schema, dict):
            input_schema = {**input_schema, "additionalProperties": False}
        contracts[name] = {
            "description": tool.description
            or _TOOL_DESCRIPTIONS.get(
                name, "Governed arifOS kernel verb (MCP transport envelope)."
            ),
            "input_schema": input_schema,
            "output_schema": None,
        }
    return contracts


def _spec_for_name(name: str) -> Any:
    lookup_name = name.replace("arifos_", "arif_") if name.startswith("arifos_") else name
    contract = _tool_registry_contracts().get(lookup_name, {})
    runtime_contract = _runtime_contracts().get(lookup_name, {})
    input_schema = runtime_contract.get(
        "input_schema",
        {"type": "object", "properties": {}, "additionalProperties": False},
    )
    if lookup_name == "arif_forge":
        # Public facade advertises the verdict-gated execution contract, not the
        # full internal wrapper parameter surface.
        input_schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "mode": {"default": "engineer", "type": "string"},
                "manifest": {"default": "", "type": "string"},
                "seal_verdict_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                },
                "approved_action_hash": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                },
                "query": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
                "artifact_id": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
                "session_id": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
                "session_token": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": "SCT from arif_init — continuity for ChatGPT multi-call path",
                },
                "ack_irreversible": {"default": False, "type": "boolean"},
                "actor_id": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
                "constitutional_chain_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                },
                "judge_state_hash": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                },
                "vault_entry_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                },
                "plan_id": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
                "arif_ack_id": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
                "_envelope": {"default": None, "title": "Envelope"},
            },
        }
    return SimpleNamespace(
        name=name,
        description=runtime_contract.get(
            "description", _TOOL_DESCRIPTIONS.get(lookup_name, "Governed arifOS MCP tool.")
        ),
        role=_role_for_name(lookup_name),
        layer=_layer_for_name(lookup_name),
        stage=contract.get("stage", "000"),
        trinity=contract.get("lane", "AGI"),
        floors=tuple(contract.get("floors", [])),
        input_schema=input_schema,
        output_schema=runtime_contract.get("output_schema") or _tool_output_schema(lookup_name),
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
    return normalize_profile(profile) == "public_agent"


def normalize_tool_profile(profile: str | None) -> str:
    return normalize_profile(profile)


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
    project = get_pyproject_metadata()
    urls = project.get("urls", {}) if isinstance(project, dict) else {}
    specs = public_tool_specs(resolved_surface_mode)
    resources, resource_templates = _resources_payload()

    return {
        "mcpVersion": "2025-11-25",
        "protocolVersion": "2025-11-25",
        "name": "arifOS-APEX-G",
        "version": release_version_label(),
        "description": (
            f"Constitutional governance server — {len(specs)} public tools in "
            f"{resolved_surface_mode} mode with F1-L13 floor enforcement."
        ),
        "vendor": {"name": "Muhammad Arif bin Fazil", "url": "https://arif-fazil.com"},
        "license": "AGPL-3.0-only",
        "homepage": urls.get("Homepage", "https://arifos.arif-fazil.com"),
        "repository": urls.get("Repository", "https://github.com/ariffazil/arifos"),
        "capabilities": {
            "kernel_abi": {
                "version": "1.0.0",
                "semantic_capabilities": list(capability_ids()),
                "canonical_count": len(KERNEL_ABI_8),
            },
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
    return list(public_tool_names(normalize_tool_profile(profile)))


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
    abi = validate_abi()
    return {
        "ok": not missing and not extra and len(actual) == len(expected) and abi["ok"],
        "actual_count": len(actual),
        "expected_count": len(expected),
        "missing": sorted(missing),
        "extra": sorted(extra),
        "abi": abi,
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
