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
from arifosmcp.constitutional_map import CANONICAL_TOOLS, _TOOL_OUTPUT_SCHEMAS
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
        "KERNEL 000 · Ignite a governed kernel session: binds actor identity, "
        "constitutional floors F1–F13, and the audit chain. Returns the "
        "session_id + session_token that every other arif_* verb requires. "
        "Use mode=preflight to inspect an existing session without re-igniting, "
        "mode=resume to continue one. Modes: init, preflight, resume, validate, "
        "canary, triage, epoch_open, epoch_seal, light, opt_out."
    ),
    # ── 000 TRIAGE (session immune, not intent router) ─────────────────────
    "arif_triage": (
        "KERNEL 000 · Session preflight — reads active stage, holds, and next safe kernel verb."
    ),
    # ── 111 OBSERVE ─────────────────────────────────────────────────────────
    "arif_observe": (
        "KERNEL 111 · Collect evidence — facts and sources with epistemic tags "
        "(OBS) and uncertainty bounds, never conclusions. mode=search queries "
        "the open web/literature; mode=fetch retrieves a URL and records its "
        "provenance; mode=vitals reads kernel machine telemetry. Reason over "
        "what you gathered with arif_think; delegate domain analysis to an "
        "organ with arif_route. Modes: search, fetch, hybrid_discovery, ingest, "
        "compass, atlas, entropy_dS, vitals."
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
        "KERNEL 333 · Structured reasoning pass: decomposes a query and returns "
        "reasoning steps labeled OBS (observed), DER (derived), INT "
        "(interpretation), SPEC (specification) under truth floors. Produces "
        "reasoning records only — no verdicts (those come from arif_judge) and "
        "no state changes. The plan-family modes draft/review/approve execution "
        "plans; simulate and wonder explore counterfactuals. Modes: reason, "
        "reflect, verify, axioms, plan, plan_review, plan_approve, "
        "refactor_plan, metabolize, simulate, wonder, atlas."
    ),
    "arif_mind_reason": ("[alias → arif_think] KERNEL 333 mind. Prefer canonical name arif_think."),
    # ── 444 ROUTE ───────────────────────────────────────────────────────────
    "arif_route": (
        "KERNEL 444 · Intent→organ router: classifies a natural-language intent "
        "and dispatches it to the specialist organ (GEOX geoscience, WEALTH "
        "capital, WELL vitality, A-FORGE execution). Returns the routing "
        "decision only — no organ call — unless organ_tool names the target "
        "tool and arguments carries its inputs. Prefer this over guessing "
        "organs yourself; use arif_think for reasoning you keep in-kernel."
    ),
    "arif_kernel_route": ("[DEPRECATED → arif_route] Legacy KERNEL 444 entry."),
    # ── 444 BRIDGE (internal-ish; agents prefer route) ──────────────────────
    "arif_bridge_connect": (
        "KERNEL 444-direct — low-level organ bridge call requiring session and lease."
    ),
    "arif_bridge": ("[DEPRECATED → arif_bridge_connect] Direct organ bridge."),
    # ── 555 CRITIQUE ────────────────────────────────────────────────────────
    "arif_critique": ("KERNEL 555 · Heart — ethical/dignity/risk stress test before judgment."),
    "arif_heart_critique": ("[alias → arif_critique] KERNEL 555 heart. Prefer arif_critique."),
    # ── MEMORY (cross-cutting governor) ─────────────────────────────────────
    "arif_memory": (
        "KERNEL 555 · Governed memory of the kernel itself: six tiers (L1–L6) "
        "with per-mode gating. recall, inspect, and audit are read paths; "
        "remember, revise, promote, and forget mutate tiers — promote and "
        "forget additionally require human_approval=true. Use for cross-session "
        "lessons, canon, and memory audit; external evidence belongs to "
        "arif_observe and reasoning artifacts to arif_think. Modes: recall, "
        "inspect, attest, remember, promote, revise, forget, audit, metabolize."
    ),
    "arif_memory_recall": ("[alias → arif_memory] Prefer canonical arif_memory."),
    # ── 666 JUDGE ───────────────────────────────────────────────────────────
    "arif_judge": (
        "KERNEL 666 · Binding constitutional arbitration: evaluates a candidate "
        "action or claim and returns SEAL / HOLD / SABAR / VOID with the full "
        "reason chain. Weighs action class, blast radius, reversibility, "
        "entropy pathway, and cooling state; a SEAL verdict here is what "
        "arif_forge requires before it will execute anything. Judge arbitrates "
        "— it does not gather (evidence comes via arif_observe, reasoning via "
        "arif_think) and it does not mutate (execution is arif_forge, "
        "permanence is arif_seal). Modes: judge, intercept, validate, hold, "
        "escalate."
    ),
    "arif_judge_deliberate": ("[alias/internal → arif_judge] Prefer public arif_judge."),
    # ── 777 FORGE ───────────────────────────────────────────────────────────
    "arif_forge": (
        "KERNEL 777 · Governed execution: applies a mutation through A-FORGE "
        "only when carrying a SEAL verdict (seal_verdict_id) from arif_judge "
        "and a live session. The manifest/query defines exactly what changes; "
        "mode=dry_run previews the plan without applying it. This is the only "
        "verb that executes general mutations — kernel memory writes go to "
        "arif_memory and permanent records to arif_seal."
    ),
    "arif_forge_execute": ("[alias → arif_forge] Prefer arif_forge."),
    "arif_act": (
        "[INTERNAL alias → arif_forge] Not on public kernel facade. Call arif_forge after SEAL."
    ),
    # ── 888 COMPOSE ─────────────────────────────────────────────────────────
    "arif_compose": (
        "KERNEL reply — final human-facing composition with citations and tone control."
    ),
    "arif_reply_compose": ("[alias → arif_compose] Prefer arif_compose."),
    # ── 999 SEAL ────────────────────────────────────────────────────────────
    "arif_seal": (
        "KERNEL 999 · Append an entry to VAULT999, the immutable ledger — "
        "accepted entries can never be edited or removed; there is no unseal. "
        "Use for permanent records of verified outcomes, lessons, and session "
        "closure once a verdict exists. ack_irreversible=true is the explicit "
        "acknowledgment of permanence, and judge_state_hash binds the entry to "
        "the verdict that authorized it. Reversible changes belong in "
        "arif_forge under a SEAL. Modes: seal, verify, ledger, changelog, "
        "audit, session_close."
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

# ═══════════════════════════════════════════════════════════════════════════
# PARAMETER DOCS — per-tool per-param descriptions merged into the wire
# input schema (TDQS Parameter Semantics: schemaDescriptionCoverage).
# Merged in _runtime_contracts(); never changes types/defaults — prose only.
# arif_memory / arif_forge carry their docs in the explicit facade schemas
# above (_spec_for_name overrides).
# ═══════════════════════════════════════════════════════════════════════════

_COMMON_PARAM_DOCS: dict[str, str] = {
    "session_id": (
        "Session id returned by arif_init (looks like 'sess-…'). Pass it on every "
        "call after init so the action is attributed to your governed session."
    ),
    "session_token": (
        "Session Continuity Token (SCT) — the credential string arif_init returned "
        "alongside session_id. Pass it back on follow-up calls to prove the session "
        "is yours; without it the kernel treats you as unauthenticated."
    ),
    "actor_id": (
        "Your agent identity, e.g. 'kimi-code/FI-008' or 'claude/sonnet'. Recorded "
        "in the audit log so this action is attributed to you."
    ),
    "_envelope": "Reserved for the transport layer — never fill this in.",
    "nonce": (
        "One-time random string (e.g. a UUID) making this request unique; "
        "protects against replay of the same call."
    ),
    "actor_signature": (
        "Cryptographic signature over the request, if your agent holds a key — "
        "proves the call genuinely came from actor_id. Omit if you have no key."
    ),
    "trace_id": (
        "Correlation id of your choosing (e.g. 'req-8f3a') — lets you find this "
        "call later across kernel logs and organ systems."
    ),
    "idempotency_key": (
        "Client-chosen key (e.g. 'job-42-attempt-1'). Retrying with the same key "
        "will not repeat the effect — safe retries on flaky networks."
    ),
    "seal_purpose": (
        "One sentence saying why this verdict/record must exist, e.g. 'closing "
        "deployment D-17'. Stored permanently alongside the record."
    ),
    "constitutional_chain_id": (
        "Id of the evidence chain this call belongs to (observe→think→judge→seal). "
        "Copy it from the earlier step's response to link the steps together."
    ),
}

_PARAM_DOCS: dict[str, dict[str, str]] = {
    "arif_init": {
        "mode": (
            "What to do: 'init' (default) starts a new governed session; "
            "'preflight' checks an existing session's state without creating one; "
            "'resume' re-attaches to the session in session_id; 'validate' "
            "re-checks credentials; 'canary' is a transport probe; 'triage' reads "
            "session state; 'epoch_open'/'epoch_seal' bracket a long working "
            "window; 'light' is a minimal session; 'opt_out' records a privacy "
            "opt-out."
        ),
        "ack_irreversible": (
            "Set true to acknowledge that session records are permanent audit "
            "artifacts and cannot be deleted afterwards."
        ),
        "epoch_id": (
            "Optional id grouping related sessions into one long-running epoch, "
            "e.g. '2026-H2-ops'."
        ),
        "previous_session_hash": (
            "Hash string returned when your previous session closed; supplying it "
            "chains this session to that one, proving continuity."
        ),
        "declared_model_key": (
            "The model you run on, e.g. 'zai-coding-plan/glm-5.3'. Informational "
            "only — the kernel records but never trusts it."
        ),
        "counterparty": (
            "JSON describing the other party in a two-agent exchange, e.g. "
            '{\"agent_id\": \"hermes/1\", \"role\": \"verifier\"}.'
        ),
        "context": (
            "JSON object of background facts to bind into the session, e.g. "
            '{\"repo\": \"arifOS\", \"task\": \"fix-tests\"}.'
        ),
        "evidence": (
            "JSON list of facts you have already verified, e.g. "
            '[{\"fact\": \"pytest 299 passed\", \"source\": \"CI run\"}] — '
            "carried into the session record."
        ),
        "tooling": (
            "JSON list of the tools you can use, e.g. [\"Bash\", \"Read\"] — "
            "lets the kernel scope what it will permit you."
        ),
        "agent_policy": (
            "JSON constraints on your own behavior, e.g. "
            '{\"autonomy\": \"reversible_only\", \"forbidden\": [\"git push\"]}.'
        ),
        "intent": (
            "Plain-language statement of what this session is for, e.g. "
            "'repair the failing MCP tests'. Recorded for audit."
        ),
        "requested_authority": (
            "The highest class of action you may take: 'OBSERVE_ONLY' (read-only, "
            "default) or a higher governed class granted by your policy."
        ),
        "verbose": "Legacy on/off verbosity ('true'/'false'); prefer verbosity.",
        "verbosity": (
            "How detailed responses should be: 'minimal' (default), 'standard', "
            "or 'full'."
        ),
        "caller_actor_id": (
            "If you are calling on behalf of another agent, that agent's id — "
            "builds a delegation chain for the audit log."
        ),
        "executor_actor_id": (
            "Id of the agent that will actually carry out work under this "
            "session's permissions, if different from actor_id."
        ),
        "sovereign_id": (
            "Identifier of the human principal you act for, when acting under "
            "their explicit delegation."
        ),
        "delegation_mode": (
            "Contract governing delegated calls, e.g. 'read_only' or 'governed'."
        ),
        "payload": (
            "Extra mode-specific data as a JSON object; the mode's response tells "
            "you which fields it expects."
        ),
        "client_capabilities": (
            "JSON declaring what your client supports, e.g. "
            '{\"transports\": [\"http\"], \"protocol\": \"2025-11-25\"}.'
        ),
        "auth_context": (
            "JSON carrying external authentication material, e.g. "
            '{\"token_class\": \"bearer\", \"issuer\": \"github\"} — used for gating.'
        ),
    },
    "arif_observe": {
        "mode": (
            "'search' (default) — web/literature query; 'fetch' — retrieve one "
            "URL with provenance; 'hybrid_discovery' — combine sources; 'ingest' "
            "— absorb a document; 'compass'/'atlas' — guided navigation; "
            "'entropy_dS' — measure system change; 'vitals' — kernel machine "
            "telemetry."
        ),
        "query": (
            "What to look for, in plain language, e.g. 'TDQS scoring rubric MCP'."
        ),
        "url": (
            "Exact URL to retrieve when mode=fetch, e.g. "
            "'https://example.com/report.pdf'."
        ),
        "layers": (
            "Restrict where to look, e.g. [\"web\"] or [\"canon\", \"memory\"]; "
            "omit to search everything available."
        ),
        "result_limit": (
            "Maximum number of results to return in search modes; default 10."
        ),
    },
    "arif_think": {
        "mode": (
            "'reason' (default) — decompose a question; 'reflect' — self-review "
            "of prior reasoning; 'verify' — check a derivation; 'axioms' — "
            "surface hidden assumptions; 'plan'/'plan_review'/'plan_approve'/"
            "'refactor_plan' — execution-plan lifecycle; 'metabolize' — "
            "consolidate past reasoning; 'simulate' — what-if; 'wonder' — open "
            "exploration; 'atlas' — map the problem space."
        ),
        "query": (
            "The question, claim, or problem to reason about, in plain language."
        ),
        "plan_id": (
            "Plan reference from an earlier plan-mode response — needed for the "
            "review/approve/refactor steps."
        ),
        "witness_type": (
            "Who vouches for the reasoning record: 'ai' (default), 'human', or "
            "'external' system."
        ),
    },
    "arif_route": {
        "contract_c_kwargs": (
            "Extra keyword arguments passed through to the organ tool call, as a "
            "JSON object."
        ),
    },
    "arif_judge": {
        "mode": (
            "'judge' (default) — render a verdict on candidate; 'intercept' — "
            "pre-flight gate before an action runs; 'validate' — re-check a prior "
            "verdict; 'hold' — place an action into a cooling period; 'escalate' "
            "— refer the decision to the human owner."
        ),
        "candidate": (
            "The action or claim being judged, stated plainly, e.g. 'delete "
            "table users in prod'."
        ),
        "vault_entry_id": (
            "Id of the permanent-ledger entry this verdict should attach to "
            "(from an earlier arif_seal response)."
        ),
        "cooldown_entry_id": (
            "Id of an existing cooling-period record to consult before this "
            "action may proceed."
        ),
        "action_tier": (
            "How risky the action is: 'standard', 'high', or 'critical' — higher "
            "tiers demand stronger evidence."
        ),
        "heart_critique": (
            "JSON result of an ethics/dignity check, e.g. "
            '{\"coercion\": false, \"dignity\": 0.9} — feeds the verdict.'
        ),
        "niat_params": (
            "JSON intent-calibration settings, e.g. "
            '{\"sincerity\": 0.8, \"stated_goal\": \"verify the claim\"}.'
        ),
        "context_source": (
            "Where the candidate came from: 'session', 'file', or 'memory'."
        ),
        "sovereign_receipt": (
            "Reference to the human owner's explicit approval, for the rare case "
            "where they have already decided directly."
        ),
        "evidence": (
            "The facts the verdict should rest on — a JSON list like "
            '[{\"fact\": \"tests pass\", \"source\": \"CI\"}], or an object.'
        ),
        "key_id": (
            "Which of your registered keys produced actor_signature, e.g. "
            "'key-1'."
        ),
        "reversibility_level": (
            "How hard the action would be to undo: 'reversible', 'hard', or "
            "'irreversible'."
        ),
        "blast_radius": (
            "Who or what the action can affect: 'self', 'session', 'organ', or "
            "'federation'."
        ),
        "authority_effect": (
            "What permission a SEAL verdict would grant, e.g. 'execute forge "
            "plan P-9'."
        ),
        "action_class": (
            "Kind of action under judgment: 'OBSERVE' (read-only), 'DRAFT' "
            "(compose text), 'MUTATE' (change state), 'IRREVERSIBLE' (permanent)."
        ),
        "requested_capability": (
            "The specific capability being requested, e.g. 'forge.execute' — "
            "checked against the capability registry."
        ),
        "domain": (
            "Subject area for claim evaluation, e.g. 'geoscience' or 'finance'."
        ),
        "claim_class": (
            "Epistemic strength of the claim: 'OBS' (directly observed), 'DER' "
            "(derived from observations), 'INT' (interpreted), 'SPEC' "
            "(speculative)."
        ),
        "claim_text": (
            "The exact claim sentence under judgment, e.g. 'uptime exceeded 99% "
            "in August'."
        ),
        "actor_B": (
            "Your calibrated confidence for a prediction, 0.0–1.0 (Brier-style "
            "score component)."
        ),
        "actor_Phi": (
            "JSON map of supporting signals about you, e.g. "
            '{\"consistency\": 0.9, \"track_record\": 0.7}.'
        ),
        "entropy_pathway": (
            "How the action changes system order: 'reduces', 'neutral', or "
            "'increases' complexity."
        ),
        "entropy_receipt": (
            "JSON receipt from an entropy computation, bound to this judgment."
        ),
    },
    "arif_seal": {
        "mode": (
            "'seal' (default) — append a permanent entry; 'verify' — check one "
            "entry; 'ledger' — read the ledger head; 'changelog' — recent "
            "appends; 'audit' — integrity check; 'session_close' — close out a "
            "session into the ledger."
        ),
        "payload": (
            "The content to store forever, as a string (usually JSON-serialized) "
            "— the outcome, lesson, or record itself."
        ),
        "judge_state_hash": (
            "Hash string from the arif_judge SEAL response — ties this entry to "
            "the verdict that authorized it."
        ),
        "witness_type": (
            "Who witnessed the sealed fact: 'ai', 'human', or 'external' system."
        ),
        "drift_events": (
            "JSON list of deviations observed, e.g. "
            '[{\"what\": \"schema drift\", \"where\": \"tools/list\"}] — stored '
            "with the record."
        ),
        "constitutional": (
            "JSON block of governance metadata (floors consulted, chain "
            "references) — normally built by the kernel, not by callers."
        ),
        "ack_irreversible": (
            "Set true to confirm you understand sealed entries are PERMANENT — "
            "they can never be edited or removed."
        ),
    },
}


def _merge_param_docs(tool_name: str, input_schema: dict[str, Any]) -> dict[str, Any]:
    """Merge _PARAM_DOCS prose into a signature-derived input schema.

    Prose only — never touches types, defaults, or enums. Unknown params are
    skipped, so handler-signature drift degrades gracefully instead of
    inventing properties.
    """
    docs = {**_COMMON_PARAM_DOCS, **_PARAM_DOCS.get(tool_name, {})}
    if not docs:
        return input_schema
    props = input_schema.get("properties")
    if not props:
        return input_schema
    merged = dict(input_schema)
    merged_props = dict(props)
    for param, doc in docs.items():
        if param in merged_props and isinstance(merged_props[param], dict):
            merged_props[param] = {**merged_props[param], "description": doc}
    merged["properties"] = merged_props
    return merged


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
            # P0 schema-fix 2026-08-17: state+en are producer-side best-effort
            # signals. Forcing them required broke MCP validation when the
            # kernel emits a derived projection (verbosity=minimal, OBSERVE_ONLY,
            # unmeasured). Schema is lenient; kernel still emits them when measured.
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
            # Producer doctrine (verbosity.py, F2): delta_S is ALWAYS emitted;
            # explicit null = honest UNKNOWN (unmeasured). 2026-08-14 E9 audit:
            # schema must accept that null instead of rejecting the envelope.
            "delta_S": {"anyOf": [{"type": "number"}, {"type": "null"}]},
            "timestamp": {"type": "string"},
            "session_id": {"anyOf": [{"type": "string"}, {"type": "null"}]},
            "actor_id": {"anyOf": [{"type": "string"}, {"type": "null"}]},
            # P0 schema-fix 2026-08-17: output_policy / nine_signal.overall.state+en
            # are producer-side best-effort signals. They CAN be absent when the
            # kernel is OBSERVE_ONLY or when verbosity=minimal strips decorative
            # blocks. Forcing them required previously caused MCP clients to
            # reject every response (the bug that broke arif_init). Schema is
            # now lenient: if present, must be the right type; if absent, the
            # response is still valid (callers fall back to verdict/status).
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
            # output_policy + nine_signal + reasons are producer-side signals.
            # They are emitted when the kernel is SEAL/HOLD/etc., but may be
            # absent for OBSERVE_ONLY / minimal-verbosity paths. Forcing them
            # required broke arif_init on 2026-08-17 — see git log.
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
        # TDQS Parameter Semantics: merge per-param prose docs (no type changes).
        input_schema = _merge_param_docs(name, input_schema)
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
                "mode": {
                    "default": "engineer",
                    "type": "string",
                    "description": (
                        "'engineer' (default) — plan and apply the work; 'dry_run' "
                        "— preview what would happen, nothing is applied; 'query' "
                        "— read-only questions about the workspace; 'write' — "
                        "write files; 'generate' — generate code or content; "
                        "'commit' — commit prepared work; 'recall' — retrieve past "
                        "forge artifacts."
                    ),
                },
                "manifest": {
                    "default": "",
                    "type": "string",
                    "description": (
                        "The work order (usually JSON or markdown) describing "
                        "exactly what to build or change — the more specific, the "
                        "tighter the gate."
                    ),
                },
                "seal_verdict_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "The SEAL verdict id arif_judge returned — without it, "
                        "nothing is executed."
                    ),
                },
                "approved_action_hash": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Hash of the exact action that was judged — execution is "
                        "refused if what you submit differs from it."
                    ),
                },
                "query": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "The task in plain language when no manifest is supplied, "
                        "e.g. 'restart the gateway service'."
                    ),
                },
                "artifact_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Id of an existing artifact (from an earlier forge or "
                        "judge response) that this call operates on."
                    ),
                },
                "session_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Session id returned by arif_init; scopes this execution to "
                        "your governed session."
                    ),
                },
                "session_token": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Session Continuity Token (SCT) returned by arif_init — "
                        "proves the session is yours."
                    ),
                },
                "ack_irreversible": {
                    "default": False,
                    "type": "boolean",
                    "description": (
                        "Set true to confirm you accept this execution cannot be "
                        "undone, when the judged action was irreversible."
                    ),
                },
                "actor_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Your agent identity, e.g. 'kimi-code/FI-008' — recorded in "
                        "the audit log."
                    ),
                },
                "constitutional_chain_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Id of the evidence chain (observe→think→judge) that led to "
                        "the SEAL — copy it from the judge response."
                    ),
                },
                "judge_state_hash": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Hash string from the arif_judge SEAL response — proves the "
                        "verdict has not been tampered with."
                    ),
                },
                "vault_entry_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Id of the permanent-ledger entry linked to this execution, "
                        "when one already exists."
                    ),
                },
                "plan_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Plan id from arif_think's plan mode, when executing an "
                        "approved plan."
                    ),
                },
                "arif_ack_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Acknowledgment id from a prior step, for multi-step "
                        "execution chains."
                    ),
                },
                "_envelope": {
                    "default": None,
                    "title": "Envelope",
                    "description": "Internal transport envelope handle — server-side; omit.",
                },
            },
        }
    if lookup_name == "arif_memory":
        # Public facade: expose only core params. Mode-specific fields
        # (content, structured, truth_class, etc.) go through payload dict.
        # The actual _arif_memory_v5_router still accepts all 59 via **kwargs.
        # Schema-only change — behavior unchanged. (888-APEX SEAL 2026-09-12)
        input_schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "mode": {
                    "type": "string",
                    "default": "recall",
                    # APEX-777 ZEN CLOSURE — public mode enum DERIVED from the
                    # canonical owner (constitutional_map.CANONICAL_TOOLS).
                    "enum": list(CANONICAL_TOOLS["arif_memory"]["modes"]),
                    "description": (
                        "'recall' (default) — semantic search of stored memories; "
                        "'inspect' — read one memory in full; 'attest' — vouch for "
                        "a memory's accuracy; 'remember' — store new text; "
                        "'promote' — move a memory up a tier; 'revise' — replace a "
                        "memory's text; 'forget' — remove a memory (gated); "
                        "'audit' — integrity scan; 'metabolize' — compact and "
                        "consolidate tiers."
                    ),
                },
                "query": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "What to search for, in plain language (mode=recall/audit), "
                        "e.g. 'past deploy rollback steps'."
                    ),
                },
                "memory_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "UUID of the memory entry to inspect/revise/forget — it was "
                        "returned when the memory was created or last listed."
                    ),
                },
                "content": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "The text to store (mode=remember) — write it as a self-"
                        "contained lesson or fact."
                    ),
                },
                "tier": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Which memory tier to target, 'L1'–'L6' (L1 = hot working "
                        "memory, L6 = sealed canon)."
                    ),
                },
                "to_tier": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": "Destination tier when promoting, e.g. 'L4'.",
                },
                "new_content": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Replacement text for the memory (mode=revise) — must "
                        "refer to the same memory_id."
                    ),
                },
                "human_approval": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Set true ONLY when the human owner explicitly approved "
                        "this promote/forget — the gate refuses without it."
                    ),
                },
                "payload": {
                    "anyOf": [{"type": "object"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Extra mode-specific fields as JSON — e.g. "
                        '{\"truth_class\": \"DERIVED\", \"provenance\": \"CI log\"} '
                        "for remember."
                    ),
                },
                "session_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Session id returned by arif_init; attributes this call to "
                        "your governed session."
                    ),
                },
                "session_token": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Session Continuity Token (SCT) returned by arif_init — "
                        "proves the session is yours."
                    ),
                },
                "actor_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Your agent identity, e.g. 'kimi-code/FI-008' — recorded in "
                        "the audit log."
                    ),
                },
                "lease_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Id of a short-lived permission grant (lease) authorizing "
                        "this write, when one was issued to you."
                    ),
                },
                "idempotency_key": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Client-chosen key (e.g. 'memo-42'); retries with the same "
                        "key will not store duplicates."
                    ),
                },
                "trace_id": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": (
                        "Correlation id of your choosing (e.g. 'req-8f3a') to find "
                        "this call later in the logs."
                    ),
                },
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


# Eager computation deferred: circular import with schemas.verdict means
# VerdictOutput.model_rebuild() may not have run yet when this module loads.
# Computed lazily via _lazy_public_tool_specs() / _lazy_public_prompt_specs().
_LAZY_TOOL_SPECS: tuple[Any, ...] | None = None
_LAZY_PROMPT_SPECS: tuple[Any, ...] | None = None
_LAZY_TOOL_SPEC_BY_NAME: dict[str, Any] | None = None


def _lazy_public_tool_specs() -> tuple[Any, ...]:
    global _LAZY_TOOL_SPECS
    if _LAZY_TOOL_SPECS is None:
        _LAZY_TOOL_SPECS = public_tool_specs()
    return _LAZY_TOOL_SPECS


def _lazy_public_prompt_specs() -> tuple[Any, ...]:
    global _LAZY_PROMPT_SPECS
    if _LAZY_PROMPT_SPECS is None:
        _LAZY_PROMPT_SPECS = tuple(
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
    return _LAZY_PROMPT_SPECS


def _lazy_public_tool_spec_by_name() -> dict[str, Any]:
    global _LAZY_TOOL_SPEC_BY_NAME
    if _LAZY_TOOL_SPEC_BY_NAME is None:
        _LAZY_TOOL_SPEC_BY_NAME = public_tool_spec_by_name()
    return _LAZY_TOOL_SPEC_BY_NAME


# PUBLIC_PROMPT_SPECS is data-only (no type resolution needed) — safe to compute eagerly.
PUBLIC_PROMPT_SPECS = _lazy_public_prompt_specs()

# PUBLIC_TOOL_SPECS / PUBLIC_TOOL_SPEC_BY_NAME are deferred via module __getattr__
# to avoid circular import with schemas.verdict (VerdictOutput.model_rebuild hasn't
# run yet when this module loads during the schemas/__init__.py import chain).
_LAZY_ALIASES: dict[str, str] = {
    "PUBLIC_TOOL_SPECS": "_lazy_public_tool_specs",
    "PUBLIC_TOOL_SPEC_BY_NAME": "_lazy_public_tool_spec_by_name",
}


def __getattr__(name: str) -> Any:
    if name in _LAZY_ALIASES:
        fn = globals()[_LAZY_ALIASES[name]]
        return fn()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def public_prompt_specs() -> tuple[Any, ...]:
    return _lazy_public_prompt_specs()


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
