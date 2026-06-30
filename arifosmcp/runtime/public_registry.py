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
    CANONICAL_7,
    current_public_surface_mode,
    normalize_public_surface_mode,
    public_tool_names_for_mode,
)
from .tool_spec import PUBLIC_RESOURCE_SPECS

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = ROOT / "pyproject.toml"
TOOL_REGISTRY_PATH = ROOT / "arifosmcp" / "tool_registry.json"
DEFAULT_PUBLIC_BASE_URL = "https://arifosmcp.arif-fazil.com"

CANONICAL_PUBLIC_TOOLS = frozenset(CANONICAL_7)
# EXPECTED_TOOL_COUNT is the default public wire surface (canonical7 mode):
# FROZEN 2026-06-23: exactly 7 public canonical verbs.
# SDK aliases and canary probes removed from wire surface — one name per function.
EXPECTED_TOOL_COUNT = len(CANONICAL_7)

RUNTIME_ENVELOPE_SCHEMA = {
    "type": "object",
    "properties": {
        "ok": {"type": "boolean"},
        "verdict": {"type": "string"},
        "payload": {"type": "object"},
    },
}

_TOOL_DESCRIPTIONS: dict[str, str] = {
    # ── Diagnostic Probes ──────────────────────────────────────────────────
    "arif_ping": (
        "Confirm kernel reachability. The zero-risk selection: if unsure the server is live, "
        "choose ping first. Returns build info + schema version + ok status. "
        "Select when: any other tool returned connection error, or before init to validate transport."
    ),
    "arif_selftest": (
        "Constitutional integrity probe — verifies the floor stack is intact. "
        "Select when: you suspect floor drift, post-deployment, or after a kernel mutation. "
        "Returns floor-by-floor pass/fail with violation details."
    ),
    # ── Transport Canary Layer (Phase 0, 2026-06-14) ──
    "arif_schema_echo": (
        "CANARY: Echo back what the client sent plus the server's interpretation. "
        "Zero-floor transport diagnostic. If what you sent != what you received, "
        "the transport bridge is mangling your payload. "
        "Select when: schema validation errors occur during tool calls."
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
    # ═════════════════════════════════════════════════════════════════════════
    # CANONICAL 7 — F13 Ratified 2026-06-23
    # Agentic intelligence framing: each description answers the selection
    # question "Should I choose this tool as my next action?"
    # Gradient: intent - current_context = required_action
    # ═════════════════════════════════════════════════════════════════════════
    # ── 000_INIT ────────────────────────────────────────────────────────────
    "arif_init": (
        "START HERE. Bootstrap a governed constitutional session and bind actor identity. "
        "Select when: starting any new conversation, resuming a previous session, or before "
        "any other arif_* tool call. Without a session_id, no governed action is possible. "
        "Returns: session_id, authority level (SEAL/OBSERVE_ONLY/FULL), floor status, "
        "next_tool recommendation, and constitution hash. "
        "Modes: init (full, ~60s) | light (<1s, tool pointers only) | resume | validate | "
        "epoch_open | epoch_seal | ping. "
        "Do NOT select when: you already have a live session_id and verified authority "
        "(use arif_triage instead), or the request is a pure factual question needing no session."
    ),
    "arif_session_init": (
        "[SDK alias of arif_init] Bootstrap a governed constitutional session. "
        "Select this alias when your SDK convention uses long-form names. "
        "Identical behavior to arif_init. Modes: init | light | resume | validate | epoch_open | epoch_seal."
    ),
    # ── 111_OBSERVE ─────────────────────────────────────────────────────────
    "arif_observe": (
        "Ground your next decision in reality. Select when: you need external evidence "
        "(web search, URL fetch, system vitals), need to map a repository structure, or "
        "need to compute entropy from a dataset. The gradient pulling toward this tool is "
        "unresolved factual uncertainty — if the answer requires data not in your context, "
        "choose observe. "
        "Modes: search | ingest | compass | atlas | entropy_dS | vitals | repo_map | hybrid_discovery. "
        "Returns: search results, ingested content, system vitals, entropy scores, or repo map. "
        "Do NOT select when: the user's intent is purely reasoning/analysis (choose arif_think instead), "
        "or the evidence is already in context."
    ),
    "arif_sense_observe": (
        "[SDK alias of arif_observe] Multimodal reality observation and hybrid discovery. "
        "Select this alias when your SDK uses long-form naming conventions."
    ),
    # ── 222_EVIDENCE ────────────────────────────────────────────────────────
    "arif_fetch": (
        "Preserve external evidence with source citations. "
        "Select when: a claim needs verified backing, you need to extract content from a "
        "specific URL, or factual grounding is required before judgment. "
        "Returns: fetched content with source metadata. "
        "Do NOT select when: arif_observe(mode=search) is sufficient for broad discovery."
    ),
    "arif_evidence_fetch": (
        "[SDK alias of arif_fetch] Fetch and preserve external evidence with source citations."
    ),
    # ── 333_REASON ──────────────────────────────────────────────────────────
    "arif_think": (
        "Reason, plan, reflect, or critique — the cognitive engine. "
        "Select when: you need to decompose a complex problem, generate a plan, evaluate "
        "hypotheses, verify a conclusion, critique a proposal, or synthesize evidence into "
        "a recommendation. The gradient pulling toward think is cognitive overload — when "
        "the next step requires structured reasoning rather than observation or action. "
        "Modes: reason (decompose) | reflect (evaluate session) | verify (check conclusion) | "
        "critique (assess risks) | plan (generate DAG) | plan_review | plan_approve | "
        "refactor_plan | metabolize (synthesize) | axioms. "
        "Returns: structured reasoning output with epistemic labels (OBS/DER/INT/SPEC), "
        "facts, inferences, unknowns, confidence bands, and next_safe_action. "
        "Do NOT select when: the question is factual and requires external data "
        "(select arif_observe first), or when immediate action is needed (select arif_act)."
    ),
    "arif_mind_reason": (
        "[SDK alias of arif_think] Multi-step reasoning, planning, and reflection "
        "with confidence labeling."
    ),
    # ── 444/555_ROUTE ──────────────────────────────────────────────────────
    "arif_kernel_route": (
        "[DEPRECATED — use arif_route] Legacy routing entry. "
        "Modes: route | stage | lane | list | status | surface_drift."
    ),
    "arif_compose": (
        "Compose the final response — format, cite, style. "
        "Select LAST, after reasoning and judgment are complete, when the output needs "
        "to be structured for human consumption. "
        "Modes: compose | style | cite | summary | format | nudge | repo_answer."
    ),
    "arif_reply_compose": ("[SDK alias of arif_compose] Compose the final response for the user."),
    # ── 555_MEMORY ──────────────────────────────────────────────────────────
    "arif_memory": (
        "Store, retrieve, and govern memory across the 6-layer stack. "
        "Select when: you need to recall past session context, store a finding for future "
        "sessions, inspect memory lineage, or promote/revise existing memories. "
        "Modes: recall | inspect | attest | remember | promote | revise | forget. "
        "Do NOT select when: the query is ephemeral and doesn't need persistence."
    ),
    "arif_memory_recall": (
        "[SDK alias of arif_memory] Federated memory tool — 7 canonical modes: "
        "recall | inspect | attest | remember | promote | revise | forget."
    ),
    # ── 666_CRITIQUE ────────────────────────────────────────────────────────
    "arif_critique": (
        "Assess ethical risks and human impact BEFORE acting. "
        "Select when: an action is sensitive, irreversible, dignity-affecting, or has "
        "human consequences. The gradient toward critique is risk — if blast_radius is "
        "MEDIUM or HIGH, critique before act. "
        "Modes: critique | simulate | empathize | redteam | maruah | deescalate | instruction_scan. "
        "Returns: risk assessment, violated floors, empathy score, human impact report. "
        "Do NOT select when: the action is purely technical with zero human dimension."
    ),
    "arif_heart_critique": (
        "[SDK alias of arif_critique] Assess ethical risks and human impact before acting."
    ),
    # ── 666g_GATEWAY ────────────────────────────────────────────────────────
    "arif_gateway_connect": (
        "Bridge to other federation agents (GEOX, WEALTH, WELL, A-FORGE, AAA). "
        "Select when: a task requires multi-organ coordination or cross-domain reasoning. "
        "Modes: route | discover | handshake | relay. "
        "Do NOT select when: the task can complete within the current session alone."
    ),
    # ── 777_MEASURE ─────────────────────────────────────────────────────────
    "arif_measure": (
        "Check system health, thermodynamic state, and resource metrics. "
        "Select when: you need operational status before a deployment, want to monitor "
        "metabolic cost, or need a pre-flight health check. "
        "Modes: health | vitals | cost | predict | topology | drift | stack_health | budget. "
        "Returns: live telemetry, entropy scores, resource utilization."
    ),
    "arif_ops_measure": (
        "[SDK alias of arif_measure] Check system health, thermodynamic state, and resource metrics."
    ),
    # ── 888_JUDGE ───────────────────────────────────────────────────────────
    "arif_judge": (
        "Render final constitutional verdict — the arbitration gate. "
        "Select when: a decision is ready for binding judgment. You have gathered evidence "
        "(observe), reasoned about it (think), and the decision requires floor compliance "
        "verification. The gradient toward judge is completion of the evidence-to-plan pipeline. "
        "Returns: SEAL (approved) | HOLD (revise) | SABAR (wait) | VOID (rejected) — with "
        "violated floors, evidence receipts, and authority verification. "
        "Modes: judge | compare | history | explain | floor_status | witness_consensus. "
        "REQUIRES: actor, intent, domain, reversibility_level, blast_radius — all mandatory. "
        "Do NOT select when: evidence is incomplete (choose observe first), plan is not ready "
        "(choose think first), or the action is reversible and low-risk (advisory mode is sufficient)."
    ),
    "arif_judge_deliberate": (
        "[SDK alias of arif_judge] Render final constitutional verdict on a proposed action."
    ),
    # ── 900_ACT ─────────────────────────────────────────────────────────────
    "arif_act": (
        "Execute an approved action — the 900 execution gate. "
        "HARD REQUIREMENT: Valid prior SEAL from arif_judge + arif_seal is mandatory. "
        "Select only when: you have seal_verdict_id AND approved_action_hash from a "
        "completed judge→seal pipeline. The gradient toward act is complete authorization — "
        "all evidence gathered, plan reasoned, risk critiqued, judge approved, seal written. "
        "Without seal_verdict_id + approved_action_hash, this tool returns 888_HOLD structurally. "
        "Routes through A2ASealVerifier for cryptographic verification before execution. "
        "Do NOT select when: you are still in planning/critique phase, or no prior SEAL exists. "
        "This is the LAST tool in the constitutional pipeline — after it, seal the result."
    ),
    # ── 999_SEAL ────────────────────────────────────────────────────────────
    "arif_seal": (
        "Append a verdict or outcome to the immutable VAULT999 ledger — irreversible. "
        "Select when: a 888_JUDGE SEAL verdict exists and needs permanent cryptographic "
        "anchoring, or an execution result needs audit trail. The gradient toward seal is "
        "finality — this record can never be deleted. "
        "Modes: seal (append record) | verify (validate chain integrity) | "
        "chain (show hash chain) | list (enumerate seals) | dry_run (preview) | "
        "seal_card | render. "
        "ack_irreversible=True is required for seal mode. "
        "Do NOT select when: the verdict is HOLD/SABAR/VOID (seal only SEAL outcomes), "
        "or testing (use dry_run mode instead)."
    ),
    "arif_vault_seal": (
        "[SDK alias of arif_seal] Seal a verdict or outcome to the immutable audit ledger. "
        "Use for final, irreversible records that must be preserved forever."
    ),
    # ── 010_FORGE ───────────────────────────────────────────────────────────
    "arif_forge": (
        "Prepare execution (dry-run capable) of an action via A-FORGE. "
        "Select when: you have a prior arif_judge SEAL and need to stage execution. "
        "This is the reversible prep stage BEFORE arif_act. "
        "Use BEFORE arif_act for the actual irreversible execution. "
        "Do NOT select when: no lease or no judge approval exists."
    ),
    "arif_forge_execute": (
        "[SDK alias of arif_forge] Execute approved builds, deployments, or system changes. "
        "Use ONLY after arif_judge has issued a SEAL verdict."
    ),
    # ── Rule 14 expansion (2026-06-20) ──
    "arif_route": (
        "Canonical intent router. Select when: you know what you want but not which tool or "
        "organ to call. Routes natural-language intent to the correct federation organ "
        "(GEOX, WEALTH, WELL, A-FORGE) or kernel tool. "
        "Optionally accepts organ_tool to bridge-call directly — bypassing the routing decision. "
        "Returns: organ, port, tool_prefix, suggested_tools. "
        "Do NOT select when: you already know the exact tool to call."
    ),
    "arif_triage": (
        "Constitutional preflight check. Select when: you need to determine the correct lane "
        "for a proposed action before execution. Returns kernel status, current holds, "
        "and lane recommendation."
    ),
    "arif_kernel_status": (
        "[DEPRECATED — moving to arif_diag_telemetry] Kernel telemetry and discovery. "
        "Query live health, tool registry, and predictive readiness across the federation surface."
    ),
    "arif_bridge_connect": (
        "Low-level direct organ tool call. Bypasses intent routing — caller must "
        "specify organ and tool_name. Select when: both organ and tool are known ahead of time. "
        "Canonical name follows arif_<noun>_<verb> convention."
    ),
    "arif_bridge": ("[DEPRECATED — use arif_bridge_connect] Low-level direct organ tool call."),
    "arif_kernel_attest": (
        "[DEPRECATED — moving to arif_diag_attest] Live organ attestation. "
        "Verify identity, tool surface, and constitutional binding."
    ),
    "arif_kernel_health": (
        "[DEPRECATED — moving to arif_diag_health] Lightweight kernel liveness probe."
    ),
    "arif_conformance_report": (
        "[DEPRECATED — use arif_canary(mode=conformance_report)] "
        "PROOF MACHINE: run the ARIF Conformance Spine against the live kernel."
    ),
    "arif_canary": (
        "Unified transport diagnostic probe. One tool, six modes. "
        "Select when: you need liveness checks, protocol version verification, schema "
        "round-trip testing, transport detail dumps, MCP handshake tests, or full conformance. "
        "Modes: ping | schema_echo | version_echo | transport_echo | initialize_probe | conformance_report"
    ),
    # ── ChatGPT Compatibility Shim ──
    "arif_search": (
        "Search the web for current information. "
        "Select when: you need to find facts, documentation, or real-world data. "
        "Returns search results with titles, URLs, and snippets."
    ),
    "arif_fetch": (
        "Fetch content from a URL. "
        "Select when: you need to read the contents of a specific webpage or document. "
        "Returns page content as text."
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
            or "Governed arifOS MCP tool.",
            output_schema=None,
        )
        input_schema = tool.parameters
        if input_schema is None:
            input_schema = {"type": "object", "properties": {}, "additionalProperties": False}
        elif isinstance(input_schema, dict):
            input_schema = {**input_schema, "additionalProperties": False}
        contracts[name] = {
            "description": tool.description
            or _TOOL_DESCRIPTIONS.get(name, "Governed arifOS MCP tool."),
            "input_schema": input_schema,
            "output_schema": None,
        }
    return contracts


def _spec_for_name(name: str) -> Any:
    lookup_name = name.replace("arifos_", "arif_") if name.startswith("arifos_") else name
    contract = _tool_registry_contracts().get(lookup_name, {})
    runtime_contract = _runtime_contracts().get(lookup_name, {})
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
        input_schema=runtime_contract.get(
            "input_schema",
            {"type": "object", "properties": {}, "additionalProperties": False},
        ),
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
