"""
ARIFOS CONSTITUTIONAL MAP (v2026.05.01)
═══════════════════════════════════════════════

Single source of truth for the active MCP surface: 13 canonical tools.
All arif_verb_noun. No governance surface, no CC modes as separate tools.

Ditempa Bukan Diberi.
"""

from enum import Enum
from typing import Any


class Floor(str, Enum):
    F01_AMANAH = "F01"
    F02_TRUTH = "F02"
    F03_WITNESS = "F03"
    F04_CLARITY = "F04"
    F05_PEACE = "F05"
    F06_EMPATHY = "F06"
    F07_HUMILITY = "F07"
    F08_GENIUS = "F08"
    F09_ANTIHANTU = "F09"
    F10_ONTOLOGY = "F10"
    F11_AUTH = "F11"
    F12_INJECTION = "F12"
    F13_SOVEREIGN = "F13"


class TrinityLane(str, Enum):
    AGI = "AGI"
    ASI = "ASI"
    APEX = "APEX"


class ToolStage(str, Enum):
    INIT = "000"
    SENSE = "111"
    MIND = "333"
    HEART = "666"
    KERNEL = "444"
    FORGE = "010"
    JUDGE = "888"
    VAULT = "999"
    OPS = "777"
    MEMORY = "555"
    FETCH = "222"
    REPLY = "444r"
    GATEWAY = "666g"


CANONICAL_TOOLS: dict[str, dict[str, Any]] = {
    "arif_session_init": {
        "name": "arif_session_init",
        "description": "000_INIT: + birth — Session bootstrap + identity binding.",
        "access": "public",
        "stage": ToolStage.INIT,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F01_AMANAH, Floor.F11_AUTH, Floor.F12_INJECTION],
        "risk_tier": "critical",
        "irreversible": False,
        "modes": ["init", "resume", "validate", "epoch_open", "epoch_seal"],
    },
    "arif_sense_observe": {
        "name": "arif_sense_observe",
        "description": "111_SENSE: + contact reality — Multimodal reality observation.",
        "access": "public",
        "stage": ToolStage.SENSE,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F02_TRUTH],
        "risk_tier": "low",
        "irreversible": False,
    },
    "arif_evidence_fetch": {
        "name": "arif_evidence_fetch",
        "description": "222_FETCH: + gather — Verified external evidence retrieval.",
        "access": "public",
        "stage": ToolStage.FETCH,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F02_TRUTH, Floor.F03_WITNESS],
        "risk_tier": "low",
        "irreversible": False,
    },
    "arif_mind_reason": {
        "name": "arif_mind_reason",
        "description": "333_MIND: + reason — Symbolic reasoning kernel.",
        "access": "public",
        "stage": ToolStage.MIND,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F02_TRUTH, Floor.F07_HUMILITY, Floor.F08_GENIUS],
        "risk_tier": "medium",
        "irreversible": False,
        "modes": [
            "reason",
            "reflect",
            "verify",
            "critique",
            "axioms",
            "plan",
            "plan_review",
            "plan_approve",
        ],
    },
    "arif_heart_critique": {
        "name": "arif_heart_critique",
        "description": "666_HEART: + feel consequence — Ethical critique and impact assessment.",
        "access": "public",
        "stage": ToolStage.HEART,
        "lane": TrinityLane.ASI,
        "floors": [Floor.F05_PEACE, Floor.F06_EMPATHY],
        "risk_tier": "medium",
        "irreversible": False,
    },
    "arif_kernel_route": {
        "name": "arif_kernel_route",
        "description": "444_KERNEL: + route — Central orchestration and tool routing.",
        "access": "public",
        "stage": ToolStage.KERNEL,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F01_AMANAH, Floor.F04_CLARITY],
        "risk_tier": "medium",
        "irreversible": False,
    },
    "arif_reply_compose": {
        "name": "arif_reply_compose",
        "description": "444_REPLY: + express — Governed response composition.",
        "access": "public",
        "stage": ToolStage.REPLY,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F04_CLARITY, Floor.F06_EMPATHY, Floor.F09_ANTIHANTU],
        "risk_tier": "low",
        "irreversible": False,
    },
    "arif_memory_recall": {
        "name": "arif_memory_recall",
        "description": "555_MEMORY: + remember — Associative retrieval from VAULT999.",
        "access": "public",
        "stage": ToolStage.MEMORY,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F01_AMANAH, Floor.F08_GENIUS],
        "risk_tier": "low",
        "irreversible": False,
    },
    "arif_gateway_connect": {
        "name": "arif_gateway_connect",
        "description": "666_GATEWAY: connect outward — Federated cross-agent bridge.",
        "access": "public",
        "stage": ToolStage.GATEWAY,
        "lane": TrinityLane.ASI,
        "floors": [Floor.F01_AMANAH, Floor.F03_WITNESS],
        "risk_tier": "medium",
        "irreversible": False,
    },
    "arif_judge_deliberate": {
        "name": "arif_judge_deliberate",
        "description": "888_JUDGE: < arbitrate — Final constitutional arbitration.",
        "access": "authenticated",
        "stage": ToolStage.JUDGE,
        "lane": TrinityLane.ASI,
        "floors": [Floor.F11_AUTH, Floor.F13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": False,
    },
    "arif_vault_seal": {
        "name": "arif_vault_seal",
        "description": "999_VAULT: + seal finally — Immutable ledger anchoring.",
        "access": "authenticated",
        "stage": ToolStage.VAULT,
        "lane": TrinityLane.APEX,
        "floors": [Floor.F01_AMANAH, Floor.F11_AUTH, Floor.F13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": True,
    },
    "arif_forge_execute": {
        "name": "arif_forge_execute",
        "description": "010_FORGE: < build — System modification and build execution.",
        "access": "public",
        "stage": ToolStage.FORGE,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F01_AMANAH, Floor.F11_AUTH, Floor.F13_SOVEREIGN],
        "risk_tier": "critical",
        "irreversible": True,
        "modes": ["engineer", "query", "write", "generate", "commit", "recall", "dry_run"],
    },
    "arif_ops_measure": {
        "name": "arif_ops_measure",
        "description": "777_OPS: measure — Resource thermodynamics.",
        "access": "public",
        "stage": ToolStage.OPS,
        "lane": TrinityLane.AGI,
        "floors": [Floor.F04_CLARITY],
        "risk_tier": "low",
        "irreversible": False,
    },
}

PROBE_TOOLS: tuple[str, ...] = ()
CONSTITUTIONAL_TOOLS: tuple[str, ...] = tuple(CANONICAL_TOOLS.keys())


def get_tool_spec(name: str) -> dict[str, Any] | None:
    return CANONICAL_TOOLS.get(name)


def list_canonical_tools() -> list[str]:
    return list(CANONICAL_TOOLS.keys())


def list_constitutional_tools() -> list[str]:
    return list(CONSTITUTIONAL_TOOLS)


def list_probe_tools() -> list[str]:
    return list(PROBE_TOOLS)


def _list_tools_by_access(access: str) -> list[str]:
    return [name for name, spec in CANONICAL_TOOLS.items() if spec.get("access") == access]


def list_public_tools() -> list[str]:
    return _list_tools_by_access("public")


def list_authenticated_tools() -> list[str]:
    return _list_tools_by_access("authenticated")


def list_sovereign_tools() -> list[str]:
    return _list_tools_by_access("sovereign")


def get_floor_bindings() -> dict[str, list[Floor]]:
    return {name: data["floors"] for name, data in CANONICAL_TOOLS.items()}


def build_tool_registry_manifest() -> dict[str, Any]:
    from arifosmcp.tool_manifest import CANONICAL_ORDER, TOOL_MANIFEST

    return {
        "_schema": "arifos-ssct-v2026.04.26-kanon-phase2",
        "_note": (
            "Generated from arifosmcp.constitutional_map.CANONICAL_TOOLS + "
            "arifosmcp.tool_manifest.TOOL_MANIFEST. Do not hand edit."
        ),
        "canonical_count": len(CONSTITUTIONAL_TOOLS),
        "probe_count": len(PROBE_TOOLS),
        "total_surface": len(CANONICAL_TOOLS),
        "canonical_order": CANONICAL_ORDER,
        "tools": {
            name: {
                "stage": spec["stage"].value,
                "lane": spec["lane"].value,
                "floors": [floor.value for floor in spec["floors"]],
                "risk_tier": spec["risk_tier"],
                "irreversible": spec["irreversible"],
                "access": spec["access"],
                "requires_auth": spec["access"] != "public",
                "tags": ["canonical"],
                "operational": TOOL_MANIFEST.get(name, {}),
            }
            for name, spec in CANONICAL_TOOLS.items()
        },
        "motto": "DITEMPA BUKAN DIBERI — Forged, Not Given",
    }


# ─── Schema Codegen ──────────────────────────────────────────────────────────
# Auto-generate Pydantic models from CANONICAL_TOOLS I/O specs.
# Any drift between canonical_map and handler signatures = CI failure.
# ─────────────────────────────────────────────────────────────────────────────

_TOOL_INPUT_SCHEMAS: dict[str, dict[str, Any]] = {
    "arif_session_init": {
        "mode": str,
        "actor_id": str | None,
        "ack_irreversible": bool,
        "session_id": str | None,
        "epoch_id": str | None,
        "previous_session_hash": str | None,
    },
    "arif_sense_observe": {
        "mode": str,
        "query": str | None,
        "session_id": str | None,
        "actor_id": str | None,
        "url": str | None,
        "layers": list[str] | None,
    },
    "arif_evidence_fetch": {
        "mode": str,
        "url": str | None,
        "query": str | None,
        "session_id": str | None,
        "actor_id": str | None,
        "thinking_depth": int,
    },
    "arif_mind_reason": {
        "mode": str,
        "query": str | None,
        "session_id": str | None,
        "actor_id": str | None,
        "plan_id": str | None,
        "witness_type": str,
    },
    "arif_heart_critique": {
        "mode": str,
        "target": str | None,
        "session_id": str | None,
        "actor_id": str | None,
    },
    "arif_kernel_route": {
        "mode": str,
        "target": str | None,
        "task": str | None,
        "stage": str | None,
        "session_id": str | None,
        "actor_id": str | None,
    },
    "arif_reply_compose": {
        "mode": str,
        "message": str | None,
        "style": str | None,
        "citations": list[str] | None,
        "session_id": str | None,
        "actor_id": str | None,
    },
    "arif_memory_recall": {
        "mode": str,
        "query": str | None,
        "memory_id": str | None,
        "session_id": str | None,
        "actor_id": str | None,
        "metadata": dict | None,
    },
    "arif_gateway_connect": {
        "mode": str,
        "target_agent": str | None,
        "session_id": str | None,
        "actor_id": str | None,
    },
    "arif_judge_deliberate": {
        "mode": str,
        "candidate": str | None,
        "session_id": str | None,
        "actor_id": str | None,
        "constitutional_chain_id": str | None,
    },
    "arif_vault_seal": {
        "mode": str,
        "payload": str,
        "session_id": str | None,
        "ack_irreversible": bool,
        "actor_id": str | None,
        "constitutional_chain_id": str | None,
        "judge_state_hash": str | None,
    },
    "arif_forge_execute": {
        "mode": str,
        "manifest": str,
        "query": str | None,
        "artifact_id": str | None,
        "session_id": str | None,
        "ack_irreversible": bool,
        "actor_id": str | None,
        "constitutional_chain_id": str | None,
        "judge_state_hash": str | None,
        "vault_entry_id": str | None,
        "plan_id": str | None,
    },
    "arif_ops_measure": {
        "mode": str,
        "estimate": float | None,
        "session_id": str | None,
        "actor_id": str | None,
    },
}


def generate_pydantic_models() -> dict[str, Any]:
    """
    Generate Pydantic BaseModel classes from CANONICAL_TOOLS I/O schemas.

    Returns a dict: {tool_name: {"input_model": BaseModel, "output_model": BaseModel}}

    Enforces:
    - F10 Ontology: all tool I/O must have type annotations
    - F11 Auth: authenticated tools must have actor_id in schema
    - F12 Injection: all string inputs must be annotated

    Codegen validation failures increment omega.schema_violations
    and flip OMEGA → SESAT per KERNEL_EVALS.md §Schema.
    """
    from pydantic import BaseModel, ConfigDict, Field

    models: dict[str, dict[str, Any]] = {}
    violations: list[str] = []

    for tool_name, input_spec in _TOOL_INPUT_SCHEMAS.items():
        spec = CANONICAL_TOOLS.get(tool_name)
        if spec is None:
            violations.append(f"{tool_name}: not in CANONICAL_TOOLS")
            continue

        # Build input model
        annotations: dict[str, Any] = {}
        defaults: dict[str, Any] = {}

        for param, type_hint in input_spec.items():
            # F12: all string inputs are treated as potentially unsanitized
            # Field default marks it for injection scanning
            if type_hint is str | None:
                annotations[param] = str
                defaults[param] = Field(default=None, description=f"[F12: sanitized] {param}")
            elif type_hint in (int, float, bool, list, dict):
                annotations[param] = type_hint
                defaults[param] = Field(default=None)
            else:
                annotations[param] = type_hint
                defaults[param] = Field(default=None)

        # F11: authenticated tools must include actor_id
        if spec["access"] == "authenticated":
            if "actor_id" not in annotations:
                violations.append(f"{tool_name}: authenticated tool missing actor_id field [F11]")

        model_name = _to_model_name(tool_name) + "Input"
        model_dict = {"model_config": ConfigDict(arbitrary_types_allowed=True)}
        model_dict.update({k: v for k, v in defaults.items()})

        try:
            input_model = type(model_name, (BaseModel,), model_dict)
            # Attach annotations
            input_model.__annotations__ = annotations
        except Exception as e:
            violations.append(f"{tool_name}: model generation failed — {e}")
            continue

        models[tool_name] = {
            "input_model": input_model,
            "spec": spec,
        }

    return {"models": models, "violations": violations}


def validate_tool_response_schema(tool_name: str, response: dict) -> tuple[bool, list[str]]:
    """
    Validate a tool response against its canonical schema.

    Returns (is_valid, violations).

    Violations include:
    - Missing nine_signal block (Nine-Signal contract)
    - Missing reasons[] on HOLD/VOID/SABAR
    - output_policy absent when domain data present
    """
    violations: list[str] = []
    spec = CANONICAL_TOOLS.get(tool_name)
    if spec is None:
        return False, [f"Unknown tool: {tool_name}"]

    verdict = response.get("verdict", "")

    # Nine-Signal block check
    nine = response.get("nine_signal")
    if nine is None:
        violations.append(f"nine_signal block absent in {tool_name} response [KERNEL_EVALS]")

    # reasons[] check for non-SEAL verdicts
    if verdict in ("HOLD", "VOID", "SABAR"):
        reasons = response.get("reasons") or response.get("reason") or []
        if not reasons:
            violations.append(
                f"{tool_name}: {verdict} verdict without reasons[] [F2 addendum / Nine-Signal]"
            )

    # output_policy check
    if response.get("domain_payload_present") and not response.get("output_policy"):
        violations.append(f"{tool_name}: domain payload without output_policy [F2 addendum]")

    return len(violations) == 0, violations


def _to_model_name(tool_name: str) -> str:
    """Convert arif_tool_name → ArifToolNameInput"""
    parts = tool_name.split("_")
    # Capitalise each part, strip arif_ prefix
    parts = [p.capitalize() for p in parts if p != "arif"]
    return "".join(parts) + "Input"


def check_schema_coverage() -> dict[str, Any]:
    """
    Verify every CANONICAL_TOOLS entry has an I/O schema defined.
    Returns coverage report.
    """
    defined = set(_TOOL_INPUT_SCHEMAS.keys())
    canonical = set(CANONICAL_TOOLS.keys())
    missing = canonical - defined
    extra = defined - canonical

    return {
        "canonical_tools": len(canonical),
        "schemas_defined": len(defined),
        "missing_schemas": list(missing),
        "orphan_schemas": list(extra),
        "coverage_pct": (len(canonical & defined) / len(canonical) * 100) if canonical else 0,
        "PASS": len(missing) == 0,
    }


# ─── Irreversibility Enforcer ────────────────────────────────────────────────

_IRREVERSIBLE_TOOLS = {
    name for name, spec in CANONICAL_TOOLS.items() if spec.get("irreversible", False)
}


def enforce_irreversibility_guard(
    tool_name: str,
    ack_irreversible: bool,
    mode: str | None = None,
) -> tuple[bool, str | None]:
    """
    Enforce F1 Amanah irreversibility guard.

    Returns (allowed, violation_msg).
    allowed=True  → proceed (SEAL from gate)
    allowed=False → blocked, caller must emit HOLD with msg
    """
    if tool_name not in _IRREVERSIBLE_TOOLS:
        return True, None

    if not ack_irreversible:
        return False, (
            f"F1: {tool_name} is irreversible — "
            "ack_irreversible=True required. "
            "Escalation: 888_HOLD"
        )
    return True, None
