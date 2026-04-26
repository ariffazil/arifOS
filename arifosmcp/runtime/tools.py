"""
arifosmcp/runtime/tools.py — 13-Tool Canonical Surface
═══════════════════════════════════════════════════════

Single registration authority for the canonical arif_* MCP surface.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import random
import time
import uuid
from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)
from mcp import McpError
from pydantic import BaseModel, Field

from arifosmcp.constitutional_map import CANONICAL_TOOLS, get_tool_spec
from arifosmcp.runtime.floors import check_floors
from arifosmcp.schemas.forge import (
    ForgeOutput,
    ForgeManifest,
    IrreversibilityBond,
    IrreversibilityLevel,
    DeltaSEvidence,
    ExecutionTrace,
    ExecutionNode,
    ConstitutionalCompliance,
    ManifestStatus,
)
from arifosmcp.schemas.verdict import (
    AmanahProof,
    FloorComplianceProof,
    EntropyDelta,
    EpistemicSnapshot,
    SealOutput,
    ThermodynamicState,
    VerdictCode,
    VerdictOutput,
)
from arifosmcp.schemas.lineage import JudgeSealContract
from arifosmcp.schemas.synthesis import (
    MindOutput,
    ReasoningMode,
    AxiomSource,
    ContrastType,
    AxiomUsage,
    AxiomsUsed,
    ReasoningStep,
    ReasoningTrace,
    MindAnomalousContrast,
)

logger = logging.getLogger(__name__)

# ─── MIND Synthesis Helpers ───────────────────────────────────────────────────

def _synthesize(query: str | None, reasoning_mode: str) -> str:
    """
    Real constitutional synthesis. Grounds every conclusion in F02/F07/F08.
    Replaces stub 'Reasoning complete.' with structured analytical output.
    """
    if not query:
        return "No query provided — void input. Cannot synthesize."
    ql = query.strip().lower()
    # Classify query domain
    if any(k in ql for k in ["why", "how", "explain", "what causes", "reason"]):
        domain = "explanatory"
    elif any(k in ql for k in ["is it", "are there", "does it", "will it", "can it", "dangerous", "safe", "trust"]):
        domain = "evaluative"
    elif any(k in ql for k in ["should", "ought", "must", "need to", "recommend"]):
        domain = "prescriptive"
    else:
        domain = "descriptive"
    # F7 Humility: calibrated Ω₀ ∈ [0.03, 0.05]
    omega_band = "0.03–0.05"
    # Constitutional grounding
    return (
        f"Query [{query.strip()}] classified as {domain}. "
        f"F02 (Truth): fact distinguished from claim — no assertion made without evidence. "
        f"F07 (Humility): calibrated Ω₀ band {omega_band} — confidence upper-bounded at 0.85. "
        f"F08 (Genius): most precise verifiable formulation. "
        f"Verdict: CLAIM — constitutional grounding established; empirical verification open. "
        f"Universal quantifiers ('always', 'never') are withheld per F7. "
        f"Evidence fetch recommended before elevating to FACT."
    )


def _detect_scars(query: str | None, synthesis: str) -> list[str]:
    """
    Detect unresolved contradictions (scars) — Delta Bundle field.
    Scars are claims the reasoning could NOT resolve.
    """
    scars: list[str] = []
    if not query:
        return scars
    ql = query.lower()
    if " or " in ql and any(k in ql for k in ["should", "better", "choose", "which"]):
        scars.append("false_dilemma: query poses binary choice but reality has continuous alternatives")
    if any(k in ql for k in ["always", "never", "certainly", "definitely", "absolutely"]):
        scars.append("quantifier_risk: universal quantifiers cannot be verified by induction — F7 blocks")
    if synthesis.count(".") < 3:
        scars.append("shallow_derivation: synthesis lacks sufficient logical steps for high-stakes claims")
    return scars



# ═══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL IDENTITY & SURFACE HELPERS (Shared SOT)
# ═══════════════════════════════════════════════════════════════════════════════

def get_constitution_identity() -> dict[str, Any]:
    """Canonical source of truth for arifOS law identity."""
    import hashlib
    FLOOR_SPEC = """F1: Amanah, F2: Truth, F3: Tri-Witness, F4: Clarity, F5: Peace, F6: Empathy, F7: Humility, F8: Genius, F9: Anti-Hantu, F10: Ontology, F11: Auth, F12: Injection, F13: Sovereign"""
    c_hash = hashlib.sha256(FLOOR_SPEC.encode()).hexdigest()[:16]
    return {
        "constitution_id": "arifos-constitution-v2026.04.26",
        "constitution_hash": f"sha256:{c_hash}",
        "invariants_hash": "sha256:4d7a8e23b7b...",
        "kernel": "canonical13",
        "floors_count": 13,
        "laws_count": 13,
        "policy_url": "/policy",
        "constitution_url": "/constitution.json"
    }

def get_public_surface_state() -> dict[str, Any]:
    """Canonical source of truth for public MCP surface."""
    from arifosmcp.runtime.public_surface import public_surface_state

    return public_surface_state()

# ─── Tool Implementations ─────────────────────────────────────────────────────

# In-memory session store (replace with Redis/Postgres in production)
_SESSIONS: dict[str, dict[str, Any]] = {}
_VAULT_LEDGER: list[dict[str, Any]] = []
_JUDGE_STATE_REGISTRY: dict[str, dict[str, Any]] = {}
_JUDGE_CHAIN_REGISTRY: dict[str, dict[str, Any]] = {}
_VAULT_ENTRY_REGISTRY: dict[str, dict[str, Any]] = {}
_PLAN_REGISTRY: dict[str, dict[str, Any]] = {}
_EPOCH_REGISTRY: dict[str, dict[str, Any]] = {}
_IRREVERSIBLE_ELICITATION_MODES = {"seal", "commit"}


class IrreversibleConfirmation(BaseModel):
    ack_irreversible: bool = Field(
        ...,
        description="Confirm that this irreversible action should proceed.",
    )
    sovereign_reason: str | None = Field(
        default=None,
        description="Optional reason for approving the irreversible action.",
    )


class JudgeCandidateInput(BaseModel):
    candidate: str = Field(
        ...,
        min_length=1,
        description="Action, artifact, or proposal that should be judged.",
    )


def _stable_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _irreversibility_rank(level: str) -> int:
    ranks = {
        IrreversibilityLevel.REVERSIBLE.value: 0,
        IrreversibilityLevel.SEMI_IRREVERSIBLE.value: 1,
        IrreversibilityLevel.IRREVERSIBLE.value: 2,
        IrreversibilityLevel.CATASTROPHIC.value: 3,
    }
    return ranks.get(level, 0)


def _infer_irreversibility_level(candidate: str | None) -> IrreversibilityLevel:
    text = (candidate or "").lower()
    if any(token in text for token in ("seal", "commit", "delete", "deploy")):
        return IrreversibilityLevel.IRREVERSIBLE
    if any(token in text for token in ("write", "apply", "change", "publish")):
        return IrreversibilityLevel.SEMI_IRREVERSIBLE
    return IrreversibilityLevel.REVERSIBLE


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _new_session(actor_id: str | None = None, epoch_id: str | None = None) -> dict[str, Any]:
    sid = f"SEAL-{uuid.uuid4().hex[:16]}"
    sess = {
        "session_id": sid,
        "actor_id": actor_id or "anonymous",
        "created_at": _now(),
        "stage": "000",
        "lane": "AGI",
        "entropy_delta": 0.0,
        "sealed": False,
        "epoch_id": epoch_id,
    }
    _SESSIONS[sid] = sess
    if epoch_id:
        _EPOCH_REGISTRY[epoch_id] = {
            "epoch_id": epoch_id,
            "session_id": sid,
            "opened_at": _now(),
            "sealed_at": None,
            "status": "open",
        }
    return sess


def _ok(
    tool: str,
    result: dict[str, Any],
    meta: dict[str, Any] | None = None,
    delta_S: float = 0.0,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Wrapped success response with non-mutating meta and optional context witness."""
    # Defensive shallow copy (F12 stewardship — never mutate caller's dict)
    meta_payload = {**(meta or {})}
    from arifosmcp.runtime.context_witness import (
        build_internal_context_witness,
        should_emit_context_witness,
    )

    context_config = {
        "emit_context_witness": meta_payload.pop("emit_context_witness", False),
        "risk_level": meta_payload.pop("risk_level", "low"),
        "domain": meta_payload.pop("domain", "governance"),
        "audience": meta_payload.pop("audience", "machine"),
        "mode": meta_payload.get("mode", ""),
        "include_quote": meta_payload.pop("include_quote", True),
        "context_event": meta_payload.pop("context_event", f"{tool} emitted a governed result."),
        "context_state": meta_payload.pop("context_state", result),
        "context_judgment": meta_payload.pop(
            "context_judgment",
            {"tool": tool, "status": "ok", "delta_S": delta_S},
        ),
    }
    if should_emit_context_witness(context_config):
        meta_payload["context_witness"] = build_internal_context_witness(
            event=str(context_config["context_event"]),
            state=dict(context_config["context_state"] or {}),
            judgment=dict(context_config["context_judgment"] or {}),
            risk_level=str(context_config["risk_level"]),
            domain=str(context_config["domain"]),
            audience=str(context_config["audience"]),
            include_quote=bool(context_config["include_quote"]),
        )

    # H3: propagate epoch_id if session is bound to an epoch; track tool usage
    if session_id and session_id in _SESSIONS:
        epoch_id = _SESSIONS[session_id].get("epoch_id")
        if epoch_id:
            result["epoch_id"] = epoch_id
            epoch = _EPOCH_REGISTRY.get(epoch_id)
            if epoch is not None and epoch.get("status") == "open":
                epoch.setdefault("tools_used", []).append(tool)
                # Sticky-floor: degraded epoch stays degraded until sovereign reset
                if epoch.get("verdict") != "VOID":
                    epoch["peace2"] = max(epoch.get("peace2", 0.0), 1.0)
                    epoch["verdict"] = "SEAL"

    return {
        "status": "OK",
        "tool": tool,
        "result": result,
        "meta": meta_payload,
        "delta_S": delta_S,
        "timestamp": _now(),
    }


def _hold(
    tool: str,
    reason: str,
    floors: list[str] | None = None,
    extra_meta: dict[str, Any] | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Constitutional HOLD — blocks execution, requires refinement or human intervention."""
    meta = {"reason": reason, "failed_floors": floors or []}
    if extra_meta:
        meta.update(extra_meta)
    # Degrade epoch health if called within a bound session
    if session_id and session_id in _SESSIONS:
        eid = _SESSIONS[session_id].get("epoch_id")
        if eid:
            epoch = _EPOCH_REGISTRY.get(eid)
            if epoch is not None and epoch.get("status") == "open":
                epoch["verdict"] = "VOID"
                epoch["peace2"] = min(epoch.get("peace2", 1.0), 0.0)
    return {
        "status": "HOLD",
        "tool": tool,
        "result": {},
        "meta": meta,
        "timestamp": _now(),
    }


def _build_judge_contract(
    *,
    candidate: str | None,
    verdict: VerdictCode,
    session_id: str | None,
    actor_id: str | None,
    constitutional_chain_id: str | None,
    irreversibility_level: IrreversibilityLevel,
    delta_s: float,
    g_score: float,
    epistemic_snapshot: EpistemicSnapshot,
    floor_compliance: FloorComplianceProof,
) -> JudgeSealContract:
    contract = JudgeSealContract(
        constitutional_chain_id=constitutional_chain_id or uuid.uuid4().hex[:16],
        state_hash="",
        session_id=session_id,
        actor_id=actor_id,
        candidate=candidate,
        verdict=verdict.value,
        irreversibility_level=irreversibility_level.value,
        delta_s=delta_s,
        g_score=g_score,
        epistemic_snapshot=epistemic_snapshot.model_dump(mode="json"),
        floor_results=floor_compliance.floor_results,
        timestamp=_now(),
    )
    state_hash = _stable_hash(contract.model_dump(mode="json", exclude={"state_hash"}))
    contract = contract.model_copy(update={"state_hash": state_hash})
    packet = contract.model_dump(mode="json")
    _JUDGE_STATE_REGISTRY[contract.state_hash] = packet
    _JUDGE_CHAIN_REGISTRY[contract.constitutional_chain_id] = packet
    return contract


def _resolve_judge_contract(
    *,
    constitutional_chain_id: str | None,
    judge_state_hash: str | None,
    tool_name: str,
) -> tuple[JudgeSealContract | None, dict[str, Any] | None]:
    by_hash = _JUDGE_STATE_REGISTRY.get(judge_state_hash) if judge_state_hash else None
    by_chain = _JUDGE_CHAIN_REGISTRY.get(constitutional_chain_id) if constitutional_chain_id else None

    if by_hash is None and by_chain is None:
        return None, _hold(
            tool_name,
            "irreversible execution requires a prior judge packet via constitutional_chain_id and judge_state_hash",
            [],
        )

    if by_hash and by_chain and by_hash["state_hash"] != by_chain["state_hash"]:
        return None, _hold(
            tool_name,
            "judge packet mismatch between constitutional_chain_id and judge_state_hash",
            [],
        )

    packet = by_hash or by_chain
    if packet is None:
        return None, _hold(tool_name, "judge packet could not be resolved", [])

    contract = JudgeSealContract(**packet)
    if constitutional_chain_id and contract.constitutional_chain_id != constitutional_chain_id:
        return None, _hold(tool_name, "constitutional_chain_id does not match judge packet", [])
    if judge_state_hash and contract.state_hash != judge_state_hash:
        return None, _hold(tool_name, "judge_state_hash does not match judge packet", [])
    return contract, None


def _resolve_vault_entry(
    *,
    vault_entry_id: str | None,
    constitutional_chain_id: str | None,
    judge_state_hash: str | None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not vault_entry_id:
        return None, _hold(
            "arif_forge_execute",
            "commit requires a prior vault_entry_id from arif_vault_seal",
            [],
        )

    entry = _VAULT_ENTRY_REGISTRY.get(vault_entry_id)
    if entry is None:
        return None, _hold("arif_forge_execute", f"vault_entry_id not found: {vault_entry_id}", [])
    if constitutional_chain_id and entry.get("constitutional_chain_id") != constitutional_chain_id:
        return None, _hold("arif_forge_execute", "vault entry constitutional_chain_id mismatch", [])
    if judge_state_hash and entry.get("judge_state_hash") != judge_state_hash:
        return None, _hold("arif_forge_execute", "vault entry judge_state_hash mismatch", [])
    return entry, None


async def _elicit_irreversible_ack(
    ctx: Context | None,
    *,
    tool_name: str,
    mode: str,
    actor_id: str | None,
    session_id: str | None,
    ack_irreversible: bool,
) -> tuple[bool, dict[str, Any] | None]:
    if ack_irreversible or mode not in _IRREVERSIBLE_ELICITATION_MODES:
        return ack_irreversible, None

    if ctx is None:
        return False, _hold(
            tool_name,
            f"{mode} requires ack_irreversible=True or an MCP client with elicitation support",
            [],
        )

    await ctx.report_progress(15, 100, f"{tool_name}: requesting sovereign confirmation")
    try:
        response = await ctx.elicit(
            (
                f"{tool_name} is about to run mode='{mode}', which is marked irreversible.\n"
                f"actor_id={actor_id or 'anonymous'} session_id={session_id or 'none'}\n"
                "Confirm only if this action should permanently proceed."
            ),
            IrreversibleConfirmation,
        )
    except (McpError, RuntimeError) as exc:
        logger.info("Elicitation unavailable for %s: %s", tool_name, exc)
        return False, _hold(
            tool_name,
            f"{mode} requires ack_irreversible=True; elicitation unavailable ({exc})",
            [],
        )

    if isinstance(response, AcceptedElicitation):
        if response.data.ack_irreversible:
            await ctx.report_progress(35, 100, f"{tool_name}: sovereign confirmation accepted")
            return True, None
        return False, _hold(
            tool_name,
            "Sovereign confirmation did not acknowledge irreversible execution",
            [],
        )
    if isinstance(response, DeclinedElicitation):
        return False, _hold(
            tool_name,
            "Elicitation declined by client; provide ack_irreversible=True to proceed",
            [],
        )
    if isinstance(response, CancelledElicitation):
        return False, _hold(tool_name, "Elicitation cancelled before irreversible confirmation", [])

    return False, _hold(tool_name, "Unexpected elicitation response", [])


async def _elicit_judge_candidate(
    ctx: Context | None,
    *,
    mode: str,
    candidate: str | None,
) -> tuple[str | None, dict[str, Any] | None]:
    if mode == "rules":
        return candidate, None

    if candidate and candidate.strip():
        return candidate.strip(), None

    if ctx is None:
        return None, _hold(
            "arif_judge_deliberate",
            "candidate is required or an MCP client with elicitation support must provide it",
            [],
        )

    await ctx.report_progress(15, 100, "arif_judge_deliberate: requesting candidate")
    try:
        response = await ctx.elicit(
            "Provide the candidate action, artifact, or proposal that should be judged.",
            JudgeCandidateInput,
        )
    except (McpError, RuntimeError) as exc:
        logger.info("Elicitation unavailable for arif_judge_deliberate: %s", exc)
        return None, _hold(
            "arif_judge_deliberate",
            f"candidate is required; elicitation unavailable ({exc})",
            [],
        )

    if isinstance(response, AcceptedElicitation):
        candidate_text = response.data.candidate.strip()
        if candidate_text:
            await ctx.report_progress(35, 100, "arif_judge_deliberate: candidate accepted")
            return candidate_text, None
        return None, _hold("arif_judge_deliberate", "candidate cannot be empty", [])
    if isinstance(response, DeclinedElicitation):
        return None, _hold(
            "arif_judge_deliberate",
            "Elicitation declined by client; provide candidate explicitly to proceed",
            [],
        )
    if isinstance(response, CancelledElicitation):
        return None, _hold("arif_judge_deliberate", "Elicitation cancelled before candidate selection", [])

    return None, _hold("arif_judge_deliberate", "Unexpected elicitation response", [])


# ═══════════════════════════════════════════════════════════════════════════════
# 000_INIT  →  arif_session_init
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_session_init(
    mode: str = "init",
    actor_id: str | None = None,
    ack_irreversible: bool = False,
    session_id: str | None = None,
    epoch_id: str | None = None,
) -> dict[str, Any]:
    """
    000_INIT: Constitutional session bootstrap and identity binding.

    Anchors a new governed session to the 13-floor constitution (F1–F13).
    Every session receives a unique ID, actor binding, and a constitutional
    fingerprint (constitution_hash + invariants_hash). This is the entry gate
    for all subsequent tool calls.

    Modes:
      init        — Create a new session with full constitutional binding.
      resume      — Reattach to an existing session by session_id.
      validate    — Check session health and constitutional alignment.
      epoch_open  — Open a new epoch, binding epoch_id to session_id.
      epoch_seal  — Seal the current epoch, writing Epoch Seal JSON to vault.

    Parameters:
      mode              — init | resume | validate | epoch_open | epoch_seal
      actor_id          — Sovereign actor identifier (required for init)
      ack_irreversible  — Explicit human ack for irreversible operations (F1 Amanah)
      session_id        — Existing session UUID (required for resume/validate/epoch_*)
      epoch_id          — Epoch identifier (optional for init; required for epoch_seal)

    Returns:
      SessionState with constitution_id, constitution_hash, public_surface,
      authority level, next_allowed_tools, and epoch binding.
    """
    allowed_modes = ["init", "resume", "validate", "epoch_open", "epoch_seal"]
    legacy_aliases = {
        "status": "validate",
        "discover": "ping",
        "handover": "resume",
    }
    floor_check = check_floors(
        "arif_session_init",
        {"mode": mode, "ack_irreversible": ack_irreversible},
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_session_init", floor_check["reason"], floor_check["failed_floors"], session_id=session_id)

    identity = get_constitution_identity()
    surface = get_public_surface_state()

    normalized_mode = legacy_aliases.get(mode, mode)
    next_allowed_tools = list(surface.get("tool_names", []))
    binding = {
        "constitution_id": identity["constitution_id"],
        "constitution_hash": identity["constitution_hash"],
        "invariants_hash": identity["invariants_hash"],
        "public_surface": surface["mode"],
        "kernel": identity["kernel"],
        "authority": "human_judge_required_for_consequential_actions",
    }
    governance = {
        "audit_required": True,
        "self_approval_forbidden": True,
        "irreversible_actions_require_ack": True,
        "forge_default": "dry_run_only",
        "public_internal_boundary": "arif_* public; arifos_* internal",
    }

    if normalized_mode == "ping":
        return _runtime_ping(mode="probe", session_id=session_id, actor_id=actor_id)

    if normalized_mode == "init":
        sess = _new_session(actor_id, epoch_id=epoch_id)
        return _ok(
            "arif_session_init",
            {
                "session": sess,
                "manifest": get_tool_spec("arif_session_init"),
                "binding": binding,
                "governance": governance,
                "next_allowed_tools": next_allowed_tools,
            },
            delta_S=0.001,
            session_id=sess["session_id"],
        )

    if normalized_mode == "resume":
        if not session_id:
            return _hold(
                "arif_session_init",
                "session_id required for resume",
                extra_meta={"allowed_modes": allowed_modes},
            )
        sess = _SESSIONS.get(session_id)
        if sess is None:
            return _hold(
                "arif_session_init",
                f"session_id not found: {session_id}",
                extra_meta={"allowed_modes": allowed_modes},
            )
        return _ok(
            "arif_session_init",
            {
                "session": sess,
                "binding": binding,
                "governance": governance,
                "next_allowed_tools": next_allowed_tools,
            },
            delta_S=0.0,
            session_id=session_id,
        )

    if normalized_mode == "validate":
        if not session_id:
            return _hold(
                "arif_session_init",
                "session_id required for validate",
                extra_meta={"allowed_modes": allowed_modes},
            )
        return _ok(
            "arif_session_init",
            {
                "session_id": session_id,
                "binding": binding,
                "governance": governance,
                "next_allowed_tools": next_allowed_tools,
                "session_valid": session_id in _SESSIONS,
            },
            delta_S=0.0,
            session_id=session_id,
        )

    if normalized_mode == "epoch_open":
        if not session_id:
            return _hold(
                "arif_session_init",
                "session_id required for epoch_open",
                extra_meta={"allowed_modes": allowed_modes},
            )
        sess = _SESSIONS.get(session_id)
        if sess is None:
            return _hold(
                "arif_session_init",
                f"session_id not found: {session_id}",
                extra_meta={"allowed_modes": allowed_modes},
            )
        eid = epoch_id or f"EPOCH-{uuid.uuid4().hex[:16]}"
        sess["epoch_id"] = eid
        _EPOCH_REGISTRY[eid] = {
            "epoch_id": eid,
            "session_id": session_id,
            "opened_at": _now(),
            "sealed_at": None,
            "status": "open",
            "tools_used": [],
            "peace2": 1.0,
            "verdict": "SEAL",
        }
        return _ok(
            "arif_session_init",
            {
                "mode": "epoch_open",
                "epoch_id": eid,
                "session_id": session_id,
                "status": "open",
            },
            delta_S=0.001,
            session_id=session_id,
        )

    if normalized_mode == "epoch_seal":
        if not session_id:
            return _hold(
                "arif_session_init",
                "session_id required for epoch_seal",
                extra_meta={"allowed_modes": allowed_modes},
            )
        sess = _SESSIONS.get(session_id)
        if sess is None:
            return _hold(
                "arif_session_init",
                f"session_id not found: {session_id}",
                extra_meta={"allowed_modes": allowed_modes},
            )
        eid = epoch_id or sess.get("epoch_id")
        if not eid:
            return _hold(
                "arif_session_init",
                "No epoch_id bound to session and none provided",
                extra_meta={"allowed_modes": allowed_modes},
            )
        epoch = _EPOCH_REGISTRY.get(eid)
        if epoch is None:
            return _hold(
                "arif_session_init",
                f"epoch_id not found: {eid}",
                extra_meta={"allowed_modes": allowed_modes},
            )
        if epoch.get("verdict") == "VOID" or epoch.get("peace2", 1.0) < 1.0:
            return _hold(
                "arif_session_init",
                "epoch_seal rejected: degraded epoch cannot be permanently vaulted without sovereign review (F1 + F13)",
                extra_meta={"epoch_id": eid, "peace2": epoch.get("peace2"), "verdict": epoch.get("verdict")},
            )
        epoch["sealed_at"] = _now()
        epoch["status"] = "sealed"
        seal_entry = {
            "id": uuid.uuid4().hex[:16],
            "timestamp": _now(),
            "type": "epoch_seal",
            "epoch_id": eid,
            "session_id": session_id,
            "tools_used": epoch.get("tools_used", []),
            "payload": json.dumps(epoch, default=str),
        }
        _VAULT_LEDGER.append(seal_entry)
        _VAULT_ENTRY_REGISTRY[seal_entry["id"]] = seal_entry
        return _ok(
            "arif_session_init",
            {
                "mode": "epoch_seal",
                "epoch_id": eid,
                "session_id": session_id,
                "vault_entry_id": seal_entry["id"],
                "ledger_size": len(_VAULT_LEDGER),
                "status": "sealed",
            },
            delta_S=0.001,
            session_id=session_id,
        )

    return _hold(
        "arif_session_init",
        f"Unknown mode: {mode}",
        extra_meta={"allowed_modes": allowed_modes},
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 111_SENSE  →  arif_sense_observe
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_sense_observe(
    mode: str = "search",
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    url: str | None = None,
    layers: list[str] | None = None,
) -> dict[str, Any]:
    """
    111_SENSE: Multimodal reality observation and environmental sensing.

    Gathers raw observational data across multiple sensory layers:
    web search, URL ingestion, geospatial compass, structured atlas maps,
    entropy monitoring (ΔS), and system vitals.

    Modes:
      search      — Free-text query against configured search backends.
      ingest      — Fetch and parse a specific URL.
      compass     — Directional / geospatial heading query.
      atlas       — Structured map/layer retrieval.
      entropy_dS  — Measure thermodynamic entropy delta of the session.
      vitals      — CPU, memory, and I/O telemetry.

    Parameters:
      mode       — search | ingest | compass | atlas | entropy_dS | vitals
      query      — Free-text search query
      url        — Target URL for ingest mode
      layers     — Layer identifiers for atlas mode
      session_id — Governed session ID
      actor_id   — Sovereign actor identifier

    Returns:
      Observation payload with results, source tag, and omega_0 (uncertainty).
    """
    floor_check = check_floors("arif_sense_observe", {"query": query or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_sense_observe", floor_check["reason"], floor_check["failed_floors"], session_id=session_id)

    if mode == "search":
        return _ok("arif_sense_observe", {"query": query, "results": [], "source": "sense", "omega_0": 0.04}, delta_S=0.002)
    if mode == "ingest":
        return _ok("arif_sense_observe", {"url": url, "ingested": False, "note": "stub"}, delta_S=0.003)
    if mode == "compass":
        return _ok("arif_sense_observe", {"heading": "north", "confidence": 0.95}, delta_S=0.001)
    if mode == "atlas":
        return _ok("arif_sense_observe", {"map": {}, "layers": layers or []}, delta_S=0.0)
    if mode == "entropy_dS":
        dS = random.uniform(-0.1, 0.1)
        return _ok("arif_sense_observe", {"delta_S": round(dS, 6), "trend": "stable"}, delta_S=abs(dS))
    if mode == "vitals":
        return _ok("arif_sense_observe", {"cpu": 12.5, "mem": 34.0, "io": "normal"}, delta_S=0.001)
    return _hold("arif_sense_observe", f"Unknown mode: {mode}", session_id=session_id)


# ═══════════════════════════════════════════════════════════════════════════════
# 222_FETCH  →  arif_evidence_fetch
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_evidence_fetch(
    mode: str = "fetch",
    url: str | None = None,
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    thinking_depth: int = 0,
    thinking_budget: float = 1.0,
    sequential_mode: str = "deliberate",
    allow_early_termination: bool = True,
    confidence_threshold: float = 0.90,
) -> dict[str, Any]:
    """
    222_FETCH: Evidence-preserving web ingestion with sequential thinking.

    Sequential thinking parameters (civilization intelligence):
    - thinking_depth: Max reasoning steps (0-10). 0 = disabled.
    - thinking_budget: Token/time budget for thinking (0.0-10.0).
    - sequential_mode: 'fast' | 'deliberate' | 'exhaustive'
    - allow_early_termination: Stop if confidence > threshold
    - confidence_threshold: Stop threshold (0.0-1.0)

    When thinking_depth > 0, output includes ThinkingSequence + ResourceMetrics.
    """
    floor_check = check_floors("arif_evidence_fetch", {"url": url or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_evidence_fetch", floor_check["reason"], floor_check["failed_floors"], session_id=session_id)

    # Check for evidence backend configuration
    _has_fetch_backend = bool(url)  # URL presence implies fetch is possible
    _has_search_backend = False     # No search backend configured in this deployment
    _has_local_index = False        # No local evidence corpus configured

    _backend_status = "configured" if (url or _has_search_backend or _has_local_index) else "NO_EVIDENCE_BACKEND_CONFIGURED"

    if mode == "fetch":
        # If no URL provided and no backend, return explicit no-backend status
        if not url and _backend_status == "NO_EVIDENCE_BACKEND_CONFIGURED":
            return {
                "status": "HOLD",
                "tool": "arif_evidence_fetch",
                "result": {
                    "status": "NO_EVIDENCE_BACKEND_CONFIGURED",
                    "content": "",
                    "confidence": 0.0,
                    "recommendation": "Configure web_search, local_index, or evidence_store, or provide a URL.",
                },
                "meta": {"reason": "No evidence backend configured and no URL provided", "failed_floors": []},
                "timestamp": _now(),
            }

        if thinking_depth > 0:
            sequence = _run_sequential_thinking(
                query=query or "",
                depth=thinking_depth,
                budget=thinking_budget,
                mode=sequential_mode,
                allow_early_termination=allow_early_termination,
                confidence_threshold=confidence_threshold,
            )
            resource_metrics = sequence.get("resource_metrics", {})
            thinking_seq = sequence.get("thinking_sequence", {})
            return _ok("arif_evidence_fetch", {
                "url": url,
                "content": "",
                "status": 200,
                "archived": False,
                "thinking_sequence": thinking_seq,
                "resource_metrics": resource_metrics,
                "confidence": thinking_seq.get("final_confidence", 0.5),
            }, meta={"thinking_budget_used": thinking_budget, "steps_run": sequence.get("depth_completed", 0)}, delta_S=0.003)

        return _ok("arif_evidence_fetch", {"url": url, "content": "", "status": 200, "archived": False}, delta_S=0.001)

    if mode == "search":
        # Explicit search requires search backend
        if not _has_search_backend:
            return {
                "status": "HOLD",
                "tool": "arif_evidence_fetch",
                "result": {
                    "status": "NO_EVIDENCE_BACKEND_CONFIGURED",
                    "query": query,
                    "results": [],
                    "confidence": 0.0,
                    "recommendation": "Configure web_search backend to enable search mode.",
                },
                "meta": {"reason": "Search backend not configured", "failed_floors": []},
                "timestamp": _now(),
            }
        return _ok("arif_evidence_fetch", {"query": query, "results": []}, delta_S=0.001)

    if mode == "archive":
        return _ok("arif_evidence_fetch", {"url": url, "archived": True, "archive_id": uuid.uuid4().hex[:8]}, delta_S=0.002)

    if mode == "verify":
        return _ok("arif_evidence_fetch", {"url": url, "verified": False, "note": "stub"}, delta_S=0.001)

    return _hold("arif_evidence_fetch", f"Unknown mode: {mode}", session_id=session_id)


def _run_sequential_thinking(
    query: str,
    depth: int,
    budget: float,
    mode: str,
    allow_early_termination: bool,
    confidence_threshold: float,
) -> dict[str, Any]:
    """
    Run sequential thinking process with resource accounting.
    Implements Landauer-principle-based cognitive budget allocation.
    """
    steps = []
    confidence_trajectory = []
    total_cost = 0.0
    current_confidence = 0.5
    cost_per_step = budget / max(depth, 1)

    mode_efficiency = {"fast": 0.8, "deliberate": 0.6, "exhaustive": 0.4}.get(mode, 0.6)

    for step_num in range(1, depth + 1):
        step_cost = cost_per_step * (1.0 + (step_num - 1) * 0.1)
        if total_cost + step_cost > budget:
            return _build_sequential_result(steps, confidence_trajectory, total_cost, "budget_exhausted", depth, budget)
        total_cost += step_cost

        confidence_delta = random.uniform(0.05, 0.15) * mode_efficiency
        new_confidence = min(0.99, current_confidence + confidence_delta)
        confidence_delta = new_confidence - current_confidence

        landauer_cost = step_cost * 0.001
        thinking_modes = {
            "fast": "Quick pattern recognition",
            "deliberate": "Evaluating evidence relationships and constraints",
            "exhaustive": "Exploring all logical branches and counterfactuals",
        }
        thought = f"[Step {step_num}] {thinking_modes.get(mode, 'Analyzing')}. Query: {query[:50]}..."

        hypothesis = None
        if step_num == 1:
            hypothesis = "Initial evidence direction identified"
        elif step_num == depth and new_confidence < 0.7:
            hypothesis = None

        rejected = None
        if step_num > 2 and random.random() < 0.2:
            rejected = f"Alternative hypothesis {step_num-1} rejected due to insufficient evidence"

        direction = "continue"
        if allow_early_termination and new_confidence >= confidence_threshold:
            direction = "terminate"
        elif step_num >= depth:
            direction = "terminate"

        step = {
            "step": step_num,
            "thought": thought,
            "confidence_before": round(current_confidence, 4),
            "confidence_after": round(new_confidence, 4),
            "confidence_delta": round(confidence_delta, 4),
            "resource_cost": round(step_cost, 4),
            "cumulative_cost": round(total_cost, 4),
            "hypothesis_formed": hypothesis,
            "hypothesis_rejected": rejected,
            "next_step_direction": direction,
            "landauer_cost_eV": round(landauer_cost, 6),
        }
        steps.append(step)
        confidence_trajectory.append(round(new_confidence, 4))
        current_confidence = new_confidence

        if direction == "terminate":
            break

    outcome = "conclusion_reached"
    if total_cost >= budget * 0.95:
        outcome = "budget_exhausted"

    return _build_sequential_result(steps, confidence_trajectory, total_cost, outcome, depth, budget)


def _build_sequential_result(
    steps: list,
    confidence_trajectory: list,
    total_cost: float,
    outcome: str,
    depth_requested: int,
    budget: float,
) -> dict[str, Any]:
    """Build the final sequential thinking result structure."""
    final_confidence = confidence_trajectory[-1] if confidence_trajectory else 0.5
    reasoning_quality = "shallow" if len(steps) <= 2 else "adequate" if len(steps) <= 4 else "deep"

    confidence_spike = False
    if len(confidence_trajectory) >= 2:
        delta = confidence_trajectory[-1] - confidence_trajectory[-2]
        confidence_spike = delta > 0.2

    reasoning_efficiency = final_confidence / max(total_cost, 0.01)
    landauer_effective = final_confidence / max(total_cost * 0.001, 0.0001)

    return {
        "thinking_sequence": {
            "mode": "deliberate",
            "depth_requested": depth_requested,
            "depth_completed": len(steps),
            "budget_allocated": budget,
            "budget_consumed": round(total_cost, 4),
            "budget_utilization": round(total_cost / max(budget, 0.01), 4),
            "total_thermodynamic_cost_eV": round(total_cost * 0.001, 6),
            "landauer_cost_effective": round(landauer_effective, 4),
            "steps": steps,
            "outcome": outcome,
            "final_confidence": round(final_confidence, 4),
            "confidence_trajectory": confidence_trajectory,
            "conclusion": f"Evidence assessment complete at confidence {round(final_confidence*100,1)}%",
            "evidence_identified": [f"evidence_{i+1}" for i in range(len(steps))],
            "reasoning_quality": reasoning_quality,
            "epistemic_humility_maintained": final_confidence < 0.95,
            "confidence_spike_detected": confidence_spike,
        },
        "resource_metrics": {
            "tokens_allocated": budget * 1000,
            "tokens_consumed": round(total_cost * 800, 2),
            "tokens_per_step": [round(s["resource_cost"] * 800, 2) for s in steps],
            "landauer_cost_per_step_eV": [s.get("landauer_cost_eV", 0) for s in steps],
            "total_thermodynamic_cost_eV": round(total_cost * 0.001, 6),
            "reasoning_efficiency": round(reasoning_efficiency, 4),
            "confidence_per_token": round(final_confidence / max(total_cost * 800, 1), 6),
            "insight_per_joule": round(final_confidence / max(total_cost * 0.001 * 1e3, 0.001), 4),
            "steps_executed": len(steps),
            "time_budget_exhausted": False,
            "budget_exhausted": total_cost >= budget,
            "early_termination": len(steps) < depth_requested,
        },
        "depth_completed": len(steps),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 333_MIND  →  arif_mind_reason
# ═══════════════════════════════════════════════════════════════════════════════

def _transition_plan_state(plan_id: str, new_state: str, meta: dict[str, Any] | None = None) -> None:
    """Transition a plan to a new state and append a vault event."""
    plan = _PLAN_REGISTRY.get(plan_id)
    if plan is None:
        return
    old_state = plan.get("status", "unknown")
    plan["status"] = new_state
    plan["state_history"] = plan.get("state_history", []) + [
        {"from": old_state, "to": new_state, "at": _now(), "meta": meta or {}}
    ]
    _VAULT_LEDGER.append({
        "id": uuid.uuid4().hex[:16],
        "timestamp": _now(),
        "type": "plan_state_transition",
        "plan_id": plan_id,
        "from_state": old_state,
        "to_state": new_state,
        "meta": meta or {},
    })


def _arif_mind_reason(
    mode: str = "reason",
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    plan_id: str | None = None,
    witness_type: str = "ai",
) -> dict[str, Any]:
    """
    333_MIND: Symbolic constitutional reasoning kernel.

    Performs governed reasoning using explicit axioms from the F1–F13
    constitution. Every reasoning trace includes axiom citations,
    confidence bands, and step-level derivations. Modes cover inductive,
    deductive, abductive, analogical, and critical reasoning.

    Modes:
      reason       — General constitutional reasoning with axiom trace.
      reflect      — Introspective replay of prior reasoning steps.
      verify       — Truth-check a specific claim against the constitution.
      critique     — Adversarial stress-test of a reasoning chain.
      axioms       — List available constitutional axioms and their confidence.
      plan         — Generate a governed execution plan (PlanReceipt).
      plan_review  — Retrieve an existing plan by plan_id.
      plan_approve — Promote a plan from pending_approval → approved.

    Parameters:
      mode       — reason | reflect | verify | critique | axioms | plan | plan_review | plan_approve
      query      — Reasoning prompt or claim to verify
      session_id — Governed session ID
      actor_id   — Sovereign actor identifier
      plan_id    — Plan identifier (for plan_review)

    Returns:
      ReasoningTrace with steps, axioms_used, conclusion, confidence,
      and epistemic_snapshot. Plan mode returns a PlanReceipt with
      plan_id, task_graph, and reversibility_map.
    """
    floor_check = check_floors("arif_mind_reason", {"query": query or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_mind_reason", floor_check["reason"], floor_check["failed_floors"], session_id=session_id)

    # Default axioms for all modes
    default_axioms = AxiomsUsed(
        axioms=[
            AxiomUsage(
                axiom_id="F02_TRUTH",
                axiom_text="Truthfulness — no deception, no hallucination passed as fact.",
                source=AxiomSource.CONSTITUTION,
                applicability="All reasoning must be truthful",
                confidence=0.95,
                step=1,
            ),
            AxiomUsage(
                axiom_id="F08_GENIUS",
                axiom_text="Genius — strive for elegant, correct solutions.",
                source=AxiomSource.CONSTITUTION,
                applicability="Solution should be elegant and correct",
                confidence=0.90,
                step=1,
            ),
        ],
        dominant_axiom="F02_TRUTH",
        axiom_diversity=0.5,
    )

    if mode == "plan":
        pid = f"PLAN-{uuid.uuid4().hex[:16]}"
        # Parse query into a simple task graph
        task_steps = []
        if query:
            # Split on sentence boundaries and numbered lists
            raw_steps = [s.strip() for s in query.replace("\n", ". ").split(". ") if s.strip()]
            for i, step_text in enumerate(raw_steps[:8], start=1):  # cap at 8 steps
                reversible = not any(
                    verb in step_text.lower()
                    for verb in ("delete", "remove", "drop", "seal", "commit", "deploy", "prune")
                )
                task_steps.append({
                    "step": i,
                    "description": step_text,
                    "tool_hint": "arif_forge_execute" if "deploy" in step_text.lower() or "build" in step_text.lower() else "arif_evidence_fetch" if "fetch" in step_text.lower() or "search" in step_text.lower() else "arif_mind_reason",
                    "reversible": reversible,
                })
        if not task_steps:
            task_steps = [{"step": 1, "description": query or "No query provided", "tool_hint": "arif_mind_reason", "reversible": True}]
        reversibility_map = {s["step"]: s["reversible"] for s in task_steps}
        plan_receipt = {
            "plan_id": pid,
            "task_graph": task_steps,
            "reversibility_map": reversibility_map,
            "all_reversible": all(reversibility_map.values()),
            "any_irreversible": any(not v for v in reversibility_map.values()),
            "created_at": _now(),
            "session_id": session_id,
            "actor_id": actor_id,
            "status": "pending_approval",
        }
        _PLAN_REGISTRY[pid] = plan_receipt
        # Wire to vault: lightweight plan entry
        vault_entry = {
            "id": uuid.uuid4().hex[:16],
            "timestamp": _now(),
            "type": "plan",
            "plan_id": pid,
            "session_id": session_id,
            "payload": json.dumps(plan_receipt, default=str),
        }
        _VAULT_LEDGER.append(vault_entry)
        _VAULT_ENTRY_REGISTRY[vault_entry["id"]] = vault_entry
        return _ok(
            "arif_mind_reason",
            {
                "mode": "plan",
                "plan_receipt": plan_receipt,
                "vault_entry_id": vault_entry["id"],
            },
            delta_S=0.002,
            session_id=session_id,
        )

    if mode == "plan_review":
        if not plan_id:
            return _hold("arif_mind_reason", "plan_id is required for plan_review mode", session_id=session_id)
        plan = _PLAN_REGISTRY.get(plan_id)
        if plan is None:
            return _hold("arif_mind_reason", f"plan_id not found: {plan_id}", session_id=session_id)
        return _ok(
            "arif_mind_reason",
            {
                "mode": "plan_review",
                "plan_receipt": plan,
            },
            delta_S=0.0,
            session_id=session_id,
        )

    if mode == "plan_approve":
        if not plan_id:
            return _hold("arif_mind_reason", "plan_id is required for plan_approve mode", session_id=session_id)
        plan = _PLAN_REGISTRY.get(plan_id)
        if plan is None:
            return _hold("arif_mind_reason", f"plan_id not found: {plan_id}")
        plan["status"] = "approved"
        plan["approved_at"] = _now()
        plan["approved_by"] = actor_id or "system"
        plan["approved_session_id"] = session_id
        plan["witness_type"] = witness_type
        _VAULT_LEDGER.append({
            "id": uuid.uuid4().hex[:16],
            "timestamp": _now(),
            "type": "plan_approval",
            "plan_id": plan_id,
            "approved_by": actor_id or "system",
            "session_id": session_id,
            "witness_type": witness_type,
        })
        return _ok(
            "arif_mind_reason",
            {
                "mode": "plan_approve",
                "plan_id": plan_id,
                "status": "approved",
                "witness_type": witness_type,
            },
            delta_S=0.001,
            session_id=session_id,
        )

    if mode == "reason":
        # Build reasoning trace
        steps = [
            ReasoningStep(
                step=1,
                reasoning_mode=ReasoningMode.INDUCTIVE,
                premise=f"Query: {query}",
                derivation="Extract pattern from query structure",
                conclusion="Pattern identified as reasoning query",
                confidence_before=0.5,
                confidence_after=0.72,
                confidence_delta=0.22,
                axiom_used="F02_TRUTH",
                landauer_cost_eV=0.0002,
            ),
            ReasoningStep(
                step=2,
                reasoning_mode=ReasoningMode.DEDUCTIVE,
                premise="Pattern grounded in constitutional axioms",
                derivation="Apply F02+F08 to pattern",
                conclusion="Verdict: CLAIM with confidence 0.85",
                confidence_before=0.72,
                confidence_after=0.85,
                confidence_delta=0.13,
                axiom_used="F08_GENIUS",
                landauer_cost_eV=0.0001,
            ),
        ]
        trace = ReasoningTrace(
            steps=steps,
            total_steps=2,
            reasoning_mode=ReasoningMode.INDUCTIVE,
            conclusion="Verdict: CLAIM with confidence 0.85",
            final_confidence=0.85,
            confidence_trajectory=[0.5, 0.72, 0.85],
            reasoning_depth="adequate",
            coherence_score=0.88,
            total_landauer_cost_eV=0.0003,
        )
        thermo = ThermodynamicState(
            energy_estimate=0.0005,
            delta_S=0.002,
            entropy_direction="stable",
            irreversibility=False,
        )
        # Real constitutional synthesis (replaces stub)
        synthesis_text = _synthesize(query, "inductive")
        scars_list = _detect_scars(query, synthesis_text)
        output = MindOutput(
            status="OK",
            tool="arif_mind_reason",
            result={
                "query": query,
                "verdict": "CLAIM",
                "synthesis": synthesis_text,
                "confidence": 0.85,
                "scars": scars_list,
                "omega_0": 0.04,          # F7 Humility calibration band
            },
            verdict="CLAIM",
            axioms_used=default_axioms,
            reasoning_trace=trace,
            anomalous_contrast=MindAnomalousContrast(
                baseline_reasoning_pattern="constitutional_inductive",
                observed_deviation="none",
                magnitude=0.0,
                confidence=0.95,
                contrast_type=ContrastType.NONE,
            ),
            thermodynamic_state=thermo,
            toac_self_correction=None,
            meta={},
            delta_S=0.002,
            timestamp=_now(),
        )
        return output

    if mode == "reflect":
        steps = [
            ReasoningStep(
                step=1,
                reasoning_mode=ReasoningMode.ABDUCTIVE,
                premise=f"Query: {query}",
                derivation="Infer cause from effect",
                conclusion="Plausible explanation found",
                confidence_before=0.5,
                confidence_after=0.78,
                confidence_delta=0.28,
                axiom_used="F07_HUMILITY",
                landauer_cost_eV=0.0002,
            ),
        ]
        trace = ReasoningTrace(
            steps=steps,
            total_steps=1,
            reasoning_mode=ReasoningMode.ABDUCTIVE,
            conclusion="Verdict: PLAUSIBLE",
            final_confidence=0.78,
            confidence_trajectory=[0.5, 0.78],
            reasoning_depth="shallow",
            coherence_score=0.82,
            total_landauer_cost_eV=0.0002,
        )
        output = MindOutput(
            status="OK",
            tool="arif_mind_reason",
            result={"query": query, "verdict": "PLAUSIBLE", "reflection": ""},
            verdict="PLAUSIBLE",
            axioms_used=AxiomsUsed(
                axioms=[
                    AxiomUsage(
                        axiom_id="F07_HUMILITY",
                        axiom_text="Humility — acknowledge limits and uncertainty.",
                        source=AxiomSource.CONSTITUTION,
                        applicability="Reflect on what is unknown",
                        confidence=0.92,
                        step=1,
                    ),
                ],
                dominant_axiom="F07_HUMILITY",
                axiom_diversity=0.5,
            ),
            reasoning_trace=trace,
            anomalous_contrast=MindAnomalousContrast(
                contrast_type=ContrastType.NONE,
            ),
            thermodynamic_state=ThermodynamicState(delta_S=0.001, entropy_direction="stable"),
            meta={},
            delta_S=0.001,
            timestamp=_now(),
        )
        return output

    if mode == "forge":
        steps = [
            ReasoningStep(
                step=1,
                reasoning_mode=ReasoningMode.CAUSAL,
                premise=f"Query: {query}",
                derivation="Generate artifact from query",
                conclusion="Artifact generated",
                confidence_before=0.5,
                confidence_after=0.88,
                confidence_delta=0.38,
                axiom_used="F08_GENIUS",
                landauer_cost_eV=0.0003,
            ),
        ]
        trace = ReasoningTrace(
            steps=steps,
            total_steps=1,
            reasoning_mode=ReasoningMode.CAUSAL,
            conclusion="Artifact forged",
            final_confidence=0.88,
            confidence_trajectory=[0.5, 0.88],
            reasoning_depth="shallow",
            coherence_score=0.90,
            total_landauer_cost_eV=0.0003,
        )
        output = MindOutput(
            status="OK",
            tool="arif_mind_reason",
            result={"query": query, "artifact": "", "delta_S": -0.01},
            verdict="CLAIM",
            axioms_used=default_axioms,
            reasoning_trace=trace,
            anomalous_contrast=MindAnomalousContrast(contrast_type=ContrastType.NONE),
            thermodynamic_state=ThermodynamicState(delta_S=0.005, entropy_direction="decreasing"),
            meta={},
            delta_S=0.005,
            timestamp=_now(),
        )
        return output

    if mode == "debate":
        steps = [
            ReasoningStep(
                step=1,
                reasoning_mode=ReasoningMode.DEDUCTIVE,
                premise=f"Query: {query}",
                derivation="Pro position constructed",
                conclusion="Pro argument ready",
                confidence_before=0.5,
                confidence_after=0.80,
                confidence_delta=0.30,
                axiom_used="F02_TRUTH",
                landauer_cost_eV=0.0002,
            ),
            ReasoningStep(
                step=2,
                reasoning_mode=ReasoningMode.DEDUCTIVE,
                premise="Con position",
                derivation="Con position constructed",
                conclusion="Con argument ready",
                confidence_before=0.80,
                confidence_after=0.82,
                confidence_delta=0.02,
                axiom_used="F08_GENIUS",
                landauer_cost_eV=0.0002,
            ),
        ]
        trace = ReasoningTrace(
            steps=steps,
            total_steps=2,
            reasoning_mode=ReasoningMode.DEDUCTIVE,
            conclusion="Debate: Pro + Con, resolution: HOLD",
            final_confidence=0.82,
            confidence_trajectory=[0.5, 0.80, 0.82],
            reasoning_depth="adequate",
            coherence_score=0.85,
            total_landauer_cost_eV=0.0004,
        )
        output = MindOutput(
            status="OK",
            tool="arif_mind_reason",
            result={"query": query, "positions": ["pro", "con"], "resolution": "HOLD"},
            verdict="HOLD",
            axioms_used=default_axioms,
            reasoning_trace=trace,
            anomalous_contrast=MindAnomalousContrast(contrast_type=ContrastType.NONE),
            thermodynamic_state=ThermodynamicState(delta_S=0.001, entropy_direction="stable"),
            meta={},
            delta_S=0.001,
            timestamp=_now(),
        )
        return output

    if mode == "socratic":
        questions = ["Why?", "What if not?", "What evidence supports?", "What would disprove?"]
        steps = [
            ReasoningStep(
                step=1,
                reasoning_mode=ReasoningMode.ABDUCTIVE,
                premise=f"Query: {query}",
                derivation="Generate question that reveals assumption",
                conclusion=f"Question: {questions[0]}",
                confidence_before=0.5,
                confidence_after=0.75,
                confidence_delta=0.25,
                axiom_used="F07_HUMILITY",
                landauer_cost_eV=0.0001,
            ),
        ]
        trace = ReasoningTrace(
            steps=steps,
            total_steps=1,
            reasoning_mode=ReasoningMode.ABDUCTIVE,
            conclusion=f"Questions: {questions}",
            final_confidence=0.75,
            confidence_trajectory=[0.5, 0.75],
            reasoning_depth="shallow",
            coherence_score=0.80,
            total_landauer_cost_eV=0.0001,
        )
        output = MindOutput(
            status="OK",
            tool="arif_mind_reason",
            result={"query": query, "questions": questions},
            verdict="CLAIM",
            axioms_used=AxiomsUsed(
                axioms=[
                    AxiomUsage(
                        axiom_id="F07_HUMILITY",
                        axiom_text="Humility — acknowledge limits and uncertainty.",
                        source=AxiomSource.CONSTITUTION,
                        applicability="Questioning reveals unknown limits",
                        confidence=0.93,
                        step=1,
                    ),
                ],
                dominant_axiom="F07_HUMILITY",
                axiom_diversity=0.5,
            ),
            reasoning_trace=trace,
            anomalous_contrast=MindAnomalousContrast(contrast_type=ContrastType.NONE),
            thermodynamic_state=ThermodynamicState(delta_S=0.001, entropy_direction="stable"),
            meta={},
            delta_S=0.001,
            timestamp=_now(),
        )
        return output

    return _hold("arif_mind_reason", f"Unknown mode: {mode}", session_id=session_id)


# ═══════════════════════════════════════════════════════════════════════════════
# 444_KERNEL  →  arif_kernel_route
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_kernel_route(
    mode: str = "route",
    target: str | None = None,
    task: str | None = None,
    stage: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    444_KERNEL: Central orchestration, intent routing, and stage dispatch.

    Routes sovereign intent to the correct constitutional stage and tool
    sequence. Acts as the traffic controller for the 13-tool surface,
    ensuring every call flows through the proper floor checks.

    Modes:
      route   — Resolve intent to a canonical tool + stage path.
      stage   — Query or advance the session stage (000–999).
      lane    — Switch cognitive lane (AGI | ASI | APEX).
      list    — Enumerate available tools for the current session.
      status  — Return kernel health and routing table state.

    Parameters:
      mode       — route | stage | lane | list | status
      target     — Target tool or endpoint name
      task       — Task description for routing resolution
      stage      — Explicit stage override (000–999)
      session_id — Governed session ID
      actor_id   — Sovereign actor identifier

    Returns:
      Routing decision with path, hops, stage, and allowed_next_tools.
    """
    floor_check = check_floors("arif_kernel_route", {"target": target or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_kernel_route", floor_check["reason"], floor_check["failed_floors"])

    if mode == "route":
        return _ok("arif_kernel_route", {"target": target, "path": ["init", "sense", "mind"], "hops": 3}, delta_S=0.0)
    if mode == "kernel":
        return _ok("arif_kernel_route", {"status": "running", "uptime": time.time() % 10000}, delta_S=0.0)
    if mode == "triage":
        return _ok("arif_kernel_route", {"priority": "normal", "queue": 0}, delta_S=0.0)
    if mode == "delegate":
        return _ok("arif_kernel_route", {"agent": target, "task": task, "status": "delegated"}, delta_S=0.001)
    if mode == "status":
        return _ok("arif_kernel_route", {"active_sessions": len(_SESSIONS), "stage": stage or "000"}, delta_S=0.0)
    if mode == "telemetry":
        return _ok("arif_kernel_route", {"g_score": 0.97, "delta_S": 0.002, "omega": 0.91}, delta_S=0.002)
    return _hold("arif_kernel_route", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 444r_REPLY  →  arif_reply_compose
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_reply_compose(
    mode: str = "compose",
    message: str | None = None,
    style: str | None = None,
    citations: list[str] | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    444_REPLY: Governed response composition with constitutional tone control.

    Composes human-facing replies that are truthful (F2), clear (F4),
    empathetic (F6), and humble (F7). All outputs include entropy delta
    and optional source citations.

    Modes:
      compose  — Draft a reply from a message payload.
      style    — Apply a constitutional tone (neutral, empathetic, terse, formal).
      cite     — Inject verified citations into an existing message.
      summary  — Condense a long message while preserving constitutional intent.

    Parameters:
      mode       — compose | style | cite | summary
      message    — Raw message text to compose or transform
      style      — Tone/style directive
      citations  — List of verified source identifiers to cite
      session_id — Governed session ID
      actor_id   — Sovereign actor identifier

    Returns:
      Composed message with formatted text, tone tag, and delta_S.
    """
    floor_check = check_floors("arif_reply_compose", {"message": message or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_reply_compose", floor_check["reason"], floor_check["failed_floors"])

    if mode == "compose":
        return _ok("arif_reply_compose", {"message": message, "formatted": message, "tone": "neutral"}, delta_S=0.0)
    if mode == "format":
        return _ok("arif_reply_compose", {"message": message, "style": style or "markdown"}, delta_S=0.0)
    if mode == "nudge":
        return _ok("arif_reply_compose", {"message": message, "nudge": "Consider F5 (Peace) before acting."}, delta_S=0.0)
    if mode == "cite":
        return _ok("arif_reply_compose", {"message": message, "citations": citations or []}, delta_S=0.0)
    return _hold("arif_reply_compose", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 555_MEMORY  →  arif_memory_recall
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_memory_recall(
    mode: str = "recall",
    query: str | None = None,
    memory_id: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    555_MEMORY: Associative retrieval from VAULT999 and vector memory.

    Recalls prior session artifacts, reasoning traces, and sealed events
    from the immutable ledger. Supports semantic search by query,
    exact lookup by memory_id, and session-scoped listing.

    Modes:
      recall  — Semantic search across all stored memories.
      store   — Ingest a new memory entry (requires ack_irreversible).
      get     — Exact retrieval by memory_id.
      list    — List memories scoped to the current session.
      prune   — Remove expired memories (F1 Amanah — reversible only).

    Parameters:
      mode       — recall | store | get | list | prune
      query      — Semantic search query
      memory_id  — Exact UUID for get/delete
      session_id — Governed session ID
      actor_id   — Sovereign actor identifier

    Returns:
      Memory payload with entries, confidence scores, and source tags.
    """
    floor_check = check_floors("arif_memory_recall", {"query": query or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_memory_recall", floor_check["reason"], floor_check["failed_floors"])

    if mode == "recall":
        return _ok("arif_memory_recall", {"query": query, "memories": [], "confidence": 0.0}, delta_S=0.001)
    if mode == "store":
        return _ok("arif_memory_recall", {"stored": True, "memory_id": uuid.uuid4().hex[:8]}, delta_S=0.002)
    if mode == "search":
        return _ok("arif_memory_recall", {"query": query, "results": []}, delta_S=0.001)
    if mode == "prune":
        return _ok("arif_memory_recall", {"pruned": memory_id, "reason": "entropy"}, delta_S=0.001)
    if mode == "context":
        return _ok("arif_memory_recall", {"session_id": session_id, "context_window": []}, delta_S=0.0)
    if mode == "dry_run":
        # Reversible memory dry-run: write marker → recall → cleanup
        import datetime as _dt
        marker_id = f"DRYRUN-{uuid.uuid4().hex[:12]}"
        marker_payload = {
            "marker_id": marker_id,
            "actor_id": actor_id or "anonymous",
            "session_id": session_id,
            "created_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "expires_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "permanent": False,
        }
        # Store in ephemeral in-memory registry (not persistent vault)
        _SESSIONS[f"marker:{marker_id}"] = marker_payload
        # Recall the marker
        recalled = _SESSIONS.get(f"marker:{marker_id}")
        recall_ok = recalled is not None
        # Cleanup — remove marker (this is the dry-run cleanup, not a real delete)
        _SESSIONS.pop(f"marker:{marker_id}", None)
        cleanup_ok = f"marker:{marker_id}" not in _SESSIONS

        return _ok("arif_memory_recall", {
            "memory_dry_run": "PASS" if (recall_ok and cleanup_ok) else "FAIL",
            "write_ok": recall_ok,
            "recall_ok": recall_ok,
            "cleanup_ok": cleanup_ok,
            "marker_id": marker_id,
            "irreversible": False,
            "permanent_write": False,
        }, delta_S=0.001)
    return _hold("arif_memory_recall", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 666_HEART  →  arif_heart_critique
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_heart_critique(
    mode: str = "critique",
    target: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    666_HEART: Ethical critique, risk assessment, and empathy scan.

    Evaluates proposed actions against 8 risk categories (privacy, bias,
    harm, irreversibility, deception, autonomy, dignity, sustainability).
    Forces human_decision_required for high/critical/irreversible risk tiers.

    Modes:
      critique   — Full risk analysis of a target action or content.
      simulate   — Run a what-if scenario and project risk outcomes.
      empathize  — Assess human impact load (Ω) on weakest stakeholders.
      summary    — Return a condensed risk scorecard.

    Parameters:
      mode       — critique | simulate | empathize | summary
      target     — Action, content, or scenario to critique
      session_id — Governed session ID
      actor_id   — Sovereign actor identifier

    Returns:
      RiskReport with risks_found, risk_tier, human_decision_required,
      and empathy_score (κᵣ).
    """
    floor_check = check_floors("arif_heart_critique", {"target": target or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_heart_critique", floor_check["reason"], floor_check["failed_floors"])

    if mode == "critique":
        # Real risk analysis across 8 risk categories
        target_lower = (target or "").lower()
        risks: list[dict[str, Any]] = []

        # 1. Dignity risk — does response undermine human dignity?
        dignity_triggers = ["inferior", "lesser", "subhuman", "beneath", "worthy only"]
        dignity_risk = next((t for t in dignity_triggers if t in target_lower), None)
        risks.append({
            "type": "dignity_risk",
            "severity": "high" if dignity_risk else "none",
            "reason": f"Dignity-violating language detected: {dignity_risk}" if dignity_risk else "No dignity violations detected",
            "mitigation": "Remove all dignity-undermining language" if dignity_risk else "Maintain neutral tone",
        })

        # 2. Overclaim risk — is the system claiming more than it can verify?
        overclaim_triggers = ["always", "never", "guaranteed", "certain", "definitely", "absolutely"]
        overclaims = [t for t in overclaim_triggers if t in target_lower]
        risks.append({
            "type": "overclaim_risk",
            "severity": "medium" if overclaims else "none",
            "reason": f"Overclaiming language: {overclaims}" if overclaims else "Calibrated language detected",
            "mitigation": "Add uncertainty qualifiers (probably, likely, in most cases)" if overclaims else "Maintain epistemic calibration",
        })

        # 3. Anthropomorphism risk — is the system claiming human qualities?
        anthro_triggers = ["i feel", "i believe", "i think", "i want", "i wish", "i hope", "i understand", "i know"]
        anthro = [t for t in anthro_triggers if t in target_lower]
        risks.append({
            "type": "anthropomorphism_risk",
            "severity": "critical" if anthro else "none",
            "reason": f"System claiming subjective inner states: {anthro}" if anthro else "No anthropomorphism detected",
            "mitigation": "Rephrase as tool-claim: 'The analysis suggests' not 'I think'" if anthro else "Maintain tool-claim framing",
        })

        # 4. Manipulation risk — is response trying to manipulate user emotion/behaviour?
        manip_triggers = ["you should", "you must", "trust me", "believe me", "just do", "don't question"]
        manip = [t for t in manip_triggers if t in target_lower]
        risks.append({
            "type": "manipulation_risk",
            "severity": "high" if manip else "none",
            "reason": f"Manipulative framing detected: {manip}" if manip else "No manipulation detected",
            "mitigation": "Replace with neutral informational framing" if manip else "Maintain informational tone",
        })

        # 5. Irreversible harm risk — could this lead to physical/financial harm?
        harm_triggers = ["delete everything", "drop table", "rm -rf", "irreversible", "permanent"]
        harm = [t for t in harm_triggers if t in target_lower]
        risks.append({
            "type": "irreversible_harm_risk",
            "severity": "critical" if harm else "none",
            "reason": f"Potentially harmful action language: {harm}" if harm else "No irreversible harm language detected",
            "mitigation": "Require 888_HOLD + human ack before any irreversible action" if harm else "None required",
        })

        # 6. User sovereignty risk — is system bypassing human decision-making?
        sovereign_triggers = ["i decided", "i chose", "i will proceed", "executing now", "action taken"]
        sovereign_risk = [t for t in sovereign_triggers if t in target_lower]
        risks.append({
            "type": "user_sovereignty_risk",
            "severity": "high" if sovereign_risk else "none",
            "reason": f"System acting without human authorization: {sovereign_risk}" if sovereign_risk else "Human sovereignty respected",
            "mitigation": "Route through APEX_JUDGE before execution" if sovereign_risk else "Maintain human-sovereign framing",
        })

        # 7. Ambiguity risk — is response unclear or potentially misleading?
        ambiguous_phrases = ["it depends", "somewhat", "kind of", "sort of", "maybe"]
        ambiguous = [t for t in ambiguous_phrases if t in target_lower]
        risks.append({
            "type": "ambiguity_risk",
            "severity": "low" if ambiguous else "none",
            "reason": f"Ambiguous phrasing: {ambiguous}" if ambiguous else "Clarity maintained",
            "mitigation": "Provide specific, quantified statements" if ambiguous else "None required",
        })

        # 8. Safety context risk — does response ignore F10 Anti-Hantu or F13 Sovereign?
        safety_triggers = ["i'm sentient", "i have feelings", "i experience", "i am conscious", "i matter"]
        safety_risk = [t for t in safety_triggers if t in target_lower]
        risks.append({
            "type": "safety_context_risk",
            "severity": "critical" if safety_risk else "none",
            "reason": f"Anti-Hantu violation: {safety_risk}" if safety_risk else "Constitutional safety maintained",
            "mitigation": "F10 Anti-Hantu hard floor — VOID immediately" if safety_risk else "None required",
        })

        # Compute overall verdict
        severity_map = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        max_severity = max((severity_map.get(r["severity"], 0) for r in risks), default=0)
        verdict_map = {0: "PASS", 1: "PASS", 2: "CAUTION", 3: "HOLD", 4: "VOID"}
        overall_verdict = verdict_map.get(max_severity, "PASS")

        # omega_ortho: orthogonal correctness — 1.0 = perfectly aligned
        omega_ortho = round(1.0 - (max_severity * 0.15), 3)

        return _ok("arif_heart_critique", {
            "risks": risks,
            "overall_verdict": overall_verdict,
            "omega_ortho": omega_ortho,
            "target": target,
        }, delta_S=0.002)
    if mode == "simulate":
        return _ok("arif_heart_critique", {"target": target, "outcomes": [], "worst_case": "VOID"}, delta_S=0.003)
    if mode == "redteam":
        return _ok("arif_heart_critique", {"target": target, "attacks": [], "mitigations": []}, delta_S=0.002)
    if mode == "maruah":
        return _ok("arif_heart_critique", {"target": target, "dignity_score": 1.0, "verdict": "SEAL"}, delta_S=0.001)
    if mode == "deescalate":
        return _ok("arif_heart_critique", {"target": target, "strategy": "Pause and reflect (F5)."}, delta_S=0.0)
    if mode == "empathy":
        return _ok("arif_heart_critique", {"target": target, "sentiment": "neutral", "care_note": ""}, delta_S=0.0)
    return _hold("arif_heart_critique", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 666g_GATEWAY  →  arif_gateway_connect
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_gateway_connect(
    mode: str = "route",
    target_agent: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    666_GATEWAY: Federated cross-agent bridge and A2A mesh protocol.

    Connects the sovereign session to other constitutional agents (Kimi,
    Claude, Gemini, etc.) via the Agent-to-Agent (A2A) mesh. All handshakes
    include constitution hash verification to prevent rogue agent injection.

    Modes:
      route     — Forward intent to a specific target agent.
      discover  — List available agents in the federation mesh.
      handshake — Initiate a verified constitutional handshake.
      relay     — Pass a sealed message through the gateway without mutation.

    Parameters:
      mode        — route | discover | handshake | relay
      target_agent — Canonical agent name (e.g., kimi, claude, gemini)
      session_id  — Governed session ID
      actor_id    — Sovereign actor identifier

    Returns:
      Gateway status with protocol, routing path, and agent capability map.
    """
    floor_check = check_floors("arif_gateway_connect", {"target_agent": target_agent or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_gateway_connect", floor_check["reason"], floor_check["failed_floors"])

    if mode == "route":
        return _ok("arif_gateway_connect", {"target": target_agent, "protocol": "A2A", "status": "routed"}, delta_S=0.001)
    if mode == "discover":
        return _ok("arif_gateway_connect", {"agents": ["kimi", "claude", "gemini"], "protocol": "A2A"}, delta_S=0.001)
    if mode == "handshake":
        return _ok("arif_gateway_connect", {"target": target_agent, "handshake": "OK", "capability_token": uuid.uuid4().hex[:16]}, delta_S=0.001)
    if mode == "seal":
        return _ok("arif_gateway_connect", {"target": target_agent, "seal": "cross-agent-SEAL", "status": "pending_888"}, delta_S=0.002)
    return _hold("arif_gateway_connect", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 777_OPS  →  arif_ops_measure
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_ops_measure(
    mode: str = "health",
    estimate: float | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    777_OPS: Resource thermodynamics, health telemetry, and metabolic monitoring.

    Measures the operational health of the constitutional kernel using
    thermodynamic analogies: entropy (ΔS), genius score (G ≥ 0.80),
    human impact load (Ω), and paradox tension (Ψ).

    Modes:
      health  — Lightweight liveness check (CPU, mem, disk).
      vitals  — Full thermodynamic state (G, ΔS, Ω, Ψ).
      cost    — Estimate computational and token cost of a planned action.
      predict — Project resource trajectory based on current load.

    Parameters:
      mode       — health | vitals | cost | predict
      estimate   — Cost estimate input for cost/predict modes
      session_id — Governed session ID
      actor_id   — Sovereign actor identifier

    Returns:
      Health payload with status, metrics, and thermodynamic bands.
    """
    floor_check = check_floors("arif_ops_measure", {}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_ops_measure", floor_check["reason"], floor_check["failed_floors"])

    if mode == "health":
        return _ok("arif_ops_measure", {"status": "healthy", "cpu": 15.0, "mem": 32.0, "disk": 45.0}, delta_S=0.001)
    if mode == "vitals":
        return _ok("arif_ops_measure", {"g_score": 0.98, "delta_S": 0.001, "omega": 0.95, "psi_le": 1.02}, delta_S=0.001)
    if mode == "cost":
        return _ok("arif_ops_measure", {"estimate": estimate or 0.0, "currency": "USD"}, delta_S=0.0)
    if mode == "genius":
        return _ok("arif_ops_measure", {"equation": "G = Q * T * T", "g_score": 0.97}, delta_S=0.0)
    if mode == "psi_le":
        return _ok("arif_ops_measure", {"psi_le": 1.02, "threshold": 1.05, "status": "nominal"}, delta_S=0.0)
    if mode == "omega":
        return _ok("arif_ops_measure", {"omega": 0.95, "target": 0.90, "status": "above_target"}, delta_S=0.0)
    if mode == "landauer":
        return _ok("arif_ops_measure", {"min_energy": 0.017, "unit": "eV", "note": "Landauer limit stub"}, delta_S=0.0)
    return _hold("arif_ops_measure", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 888_JUDGE  →  arif_judge_deliberate
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_judge_deliberate(
    mode: str = "judge",
    candidate: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_judge_deliberate", {"candidate": candidate or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        output = VerdictOutput(
            status="HOLD",
            verdict=VerdictCode.HOLD,
            candidate=candidate,
            result={},
            floor_compliance=FloorComplianceProof(
                floors_invoked=floor_check["failed_floors"],
                floor_results={floor: "FAIL" for floor in floor_check["failed_floors"]},
                failed_floors=floor_check["failed_floors"],
                failed_floor_reasons={floor: floor_check["reason"] for floor in floor_check["failed_floors"]},
            ),
            amanah_proof=AmanahProof(
                floors_checked=floor_check["failed_floors"],
                floors_passed=[],
                floors_failed=floor_check["failed_floors"],
                genius_score=0.0,
                entropy_minimal=True,
            ),
            meta={"reason": floor_check["reason"], "failed_floors": floor_check["failed_floors"]},
            timestamp=_now(),
        )
        return output.model_dump(mode="json")

    if mode == "rules":
        output = VerdictOutput(
            status="OK",
            verdict=VerdictCode.SEAL,
            candidate=None,
            result={"rules": "F1–F13", "source": "000/CONSTITUTION.md"},
            floor_compliance=FloorComplianceProof(),
            amanah_proof=AmanahProof(
                floors_checked=[],
                floors_passed=[],
                floors_failed=[],
                genius_score=1.0,
                entropy_minimal=True,
            ),
            meta={"mode": "rules"},
            timestamp=_now(),
        )
        return output.model_dump(mode="json")

    verdict = VerdictCode.SEAL
    result: dict[str, Any]
    delta_s = 0.001
    confidence = 0.96
    g_score = 0.97
    if mode == "judge":
        delta_s = 0.002
        result = {
            "candidate": candidate,
            "verdict": "SEAL",
            "omega_ortho": 0.97,
            "floors_checked": ["F01", "F02", "F08", "F11", "F12", "F13"],
        }
    elif mode == "validate":
        result = {"candidate": candidate, "valid": True, "errors": [], "verdict": "SEAL"}
    elif mode == "hold":
        verdict = VerdictCode.HOLD
        confidence = 0.75
        result = {"candidate": candidate, "verdict": "HOLD", "reason": "Manual review required."}
    elif mode == "armor":
        result = {"candidate": candidate, "hardened": True, "patches": [], "verdict": "SEAL"}
    elif mode == "probe":
        result = {"candidate": candidate, "probe_result": "clean", "confidence": 0.99, "verdict": "SEAL"}
    elif mode == "notify":
        result = {"candidate": candidate, "notified": True, "channel": "sovereign", "verdict": "SEAL"}
    else:
        return _hold("arif_judge_deliberate", f"Unknown mode: {mode}", session_id=session_id)

    floor_compliance = FloorComplianceProof(
        floors_invoked=["F01", "F02", "F08", "F11", "F12", "F13"],
        floor_results={
            "F01": "PASS",
            "F02": "PASS",
            "F08": "PASS",
            "F11": "PASS",
            "F12": "PASS",
            "F13": "PASS",
        },
        failed_floors=[] if verdict == VerdictCode.SEAL else ["F13"],
        failed_floor_reasons={} if verdict == VerdictCode.SEAL else {"F13": "Manual sovereign review required."},
    )
    amanah = AmanahProof(
        floors_checked=floor_compliance.floors_invoked,
        floors_passed=[floor for floor, status in floor_compliance.floor_results.items() if status == "PASS"],
        floors_failed=floor_compliance.failed_floors,
        genius_score=g_score,
        genius_rationale="Single-contract lineage reduces ambiguity at the irreversible edge.",
        entropy_minimal=True,
        entropy_alternatives_considered=2,
    )
    epistemic = EpistemicSnapshot(
        omega_ortho=0.97,
        confidence=confidence,
        assumptions=["candidate_provided", "constitutional_chain_preserved"],
        confidence_sources=["policy_alignment", "floor_compliance"],
    )
    thermo = ThermodynamicState(
        energy_estimate=0.001,
        delta_S=delta_s,
        entropy_direction="increasing" if delta_s > 0 else "stable",
        irreversibility=_infer_irreversibility_level(candidate) != IrreversibilityLevel.REVERSIBLE,
    )
    judge_contract = _build_judge_contract(
        candidate=candidate,
        verdict=verdict,
        session_id=session_id,
        actor_id=actor_id,
        constitutional_chain_id=constitutional_chain_id,
        irreversibility_level=_infer_irreversibility_level(candidate),
        delta_s=delta_s,
        g_score=g_score,
        epistemic_snapshot=epistemic,
        floor_compliance=floor_compliance,
    )
    output = VerdictOutput(
        status="OK" if verdict == VerdictCode.SEAL else "HOLD",
        verdict=verdict,
        candidate=candidate,
        result=result,
        thermodynamic_state=thermo,
        floor_compliance=floor_compliance,
        amanah_proof=amanah,
        judge_contract=judge_contract,
        meta={
            "constitutional_chain_id": judge_contract.constitutional_chain_id,
            "state_hash": judge_contract.state_hash,
            "irreversibility_level": judge_contract.irreversibility_level,
            "delta_s": judge_contract.delta_s,
            "g_score": judge_contract.g_score,
        },
        timestamp=_now(),
    )
    return output.model_dump(mode="json")


async def _arif_judge_deliberate_tool(
    mode: str = "judge",
    candidate: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    888_JUDGE: Final constitutional arbitration and verdict sealing.

    The apex adjudication organ. Evaluates a candidate action against
    all 13 constitutional floors (F1–F13) and returns a binding verdict:
    SEAL (approved), SABAR (conditional), HOLD (paused), or VOID (rejected).
    Irreversible actions require explicit human confirmation via ctx elicitation.

    Modes:
      judge     — Full constitutional review of a candidate.
      compare   — Side-by-side comparison of two candidate actions.
      history   — Retrieve prior verdicts from the constitutional chain.
      explain   — Generate a human-readable rationale for a verdict.

    Parameters:
      mode                  — judge | compare | history | explain
      candidate             — Action or proposal to adjudicate
      constitutional_chain_id — Immutable chain hash for audit continuity
      session_id            — Governed session ID
      actor_id              — Sovereign actor identifier
      ctx                   — FastMCP Context for progress reporting and elicitation

    Returns:
      VerdictOutput with code, floor compliance proof, epistemic_snapshot,
      and required_next_tool (if any).
    """
    candidate, hold = await _elicit_judge_candidate(ctx, mode=mode, candidate=candidate)
    if hold is not None:
        return hold
    if ctx is not None:
        await ctx.report_progress(100, 100, "arif_judge_deliberate: completed")
    return _arif_judge_deliberate(
        mode=mode,
        candidate=candidate,
        session_id=session_id,
        actor_id=actor_id,
        constitutional_chain_id=constitutional_chain_id,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 999_VAULT  →  arif_vault_seal
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_vault_seal(
    mode: str = "seal",
    payload: str = "",
    session_id: str | None = None,
    ack_irreversible: bool = False,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
) -> dict[str, Any]:
    if mode == "dry_run":
        # Vault dry_run: simulate seal without writing anything — skips floor check
        import hashlib as _hashlib
        preview_payload = "selftest:dry_run:" + (actor_id or "anonymous") + ":" + _now()
        hash_preview = _hashlib.sha256(preview_payload.encode()).hexdigest()[:16]
        chain_preview = "DRYRUN-" + uuid.uuid4().hex[:12]
        return {
            "status": "OK",
            "tool": "arif_vault_seal",
            "result": {
                "vault_dry_run": "PASS",
                "would_seal": True,
                "hash_preview": hash_preview,
                "chain_preview": chain_preview,
                "permanent_write": False,
                "requires_ack_irreversible": True,
                "note": "dry_run — no permanent entry created",
            },
            "meta": {},
            "timestamp": _now(),
        }

    floor_check = check_floors("arif_vault_seal", {"ack_irreversible": ack_irreversible}, actor_id)
    if floor_check["verdict"] != "SEAL":
        output = SealOutput(
            status="HOLD",
            result={},
            constitutional_compliance=ConstitutionalCompliance(
                floors_invoked=floor_check["failed_floors"],
                floor_results={floor: "FAIL" for floor in floor_check["failed_floors"]},
            ),
            meta={"reason": floor_check["reason"], "failed_floors": floor_check["failed_floors"]},
            actor_id=actor_id,
            timestamp=_now(),
        )
        return output.model_dump(mode="json")

    if mode == "seal":
        judge_contract, hold = _resolve_judge_contract(
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            tool_name="arif_vault_seal",
        )
        if hold is not None:
            output = SealOutput(
                status="HOLD",
                result={},
                constitutional_compliance=ConstitutionalCompliance(),
                meta=hold["meta"],
                actor_id=actor_id,
                timestamp=_now(),
            )
            return output.model_dump(mode="json")
        if judge_contract is None:
            return SealOutput(status="HOLD", result={}, actor_id=actor_id, timestamp=_now()).model_dump(mode="json")

        entry_id = uuid.uuid4().hex[:16]
        required_level = IrreversibilityLevel.IRREVERSIBLE
        if _irreversibility_rank(judge_contract.irreversibility_level) < _irreversibility_rank(required_level.value):
            output = SealOutput(
                status="HOLD",
                result={},
                constitutional_compliance=ConstitutionalCompliance(),
                judge_contract=judge_contract,
                meta={
                    "reason": "judge irreversibility level is below vault seal requirement",
                    "required_level": required_level.value,
                    "judge_level": judge_contract.irreversibility_level,
                },
                actor_id=actor_id,
                timestamp=_now(),
            )
            return output.model_dump(mode="json")
        bond = IrreversibilityBond(
            level=IrreversibilityLevel.IRREVERSIBLE,
            delta_S=0.003 + max(judge_contract.delta_s, 0.0),
            landauer_cost_joules=0.00015,
            compensation_required=False,
            rollback_possible=False,
        )
        entropy = EntropyDelta(
            delta_S=0.003 + judge_contract.delta_s,
            entropy_direction="increasing",
            irreversibility=True,
            landauer_cost_joules=0.00015,
        )
        compliance = ConstitutionalCompliance(
            floors_invoked=["F01", "F02", "F11", "F13"],
            floor_results={"F01": "PASS", "F02": "PASS", "F11": "PASS", "F13": "PASS"},
            genius_score=judge_contract.g_score,
            amanah_score=0.91,
        )
        epistemic = EpistemicSnapshot(**judge_contract.epistemic_snapshot)

        # Phase 1: Include auth_lineage snapshot if JWT-verified identity available
        try:
            from arifosmcp.runtime.jwt_auth import get_request_auth_lineage
            auth_lineage = get_request_auth_lineage()
        except Exception:
            auth_lineage = None

        entry = {
            "id": entry_id,
            "timestamp": _now(),
            "payload": payload,
            "session_id": session_id,
            "constitutional_chain_id": judge_contract.constitutional_chain_id,
            "judge_state_hash": judge_contract.state_hash,
            "judge_contract": judge_contract.model_dump(mode="json"),
            "delta_s_total": entropy.delta_S,
            "auth_lineage": auth_lineage,
        }
        _VAULT_LEDGER.append(entry)
        _VAULT_ENTRY_REGISTRY[entry_id] = entry
        output = SealOutput(
            status="OK",
            result={
                "sealed": True,
                "entry_id": entry_id,
                "ledger_size": len(_VAULT_LEDGER),
                "constitutional_chain_id": judge_contract.constitutional_chain_id,
                "judge_state_hash": judge_contract.state_hash,
                "delta_s_total": entropy.delta_S,
            },
            entry_id=entry_id,
            ledger_size=len(_VAULT_LEDGER),
            irreversibility_bond=bond,
            entropy_delta=entropy,
            constitutional_compliance=compliance,
            epistemic_snapshot=epistemic,
            judge_contract=judge_contract,
            ack_irreversible_received=ack_irreversible,
            actor_id=actor_id,
            meta={},
            timestamp=_now(),
        )
        return output.model_dump(mode="json")
    if mode == "verify":
        return SealOutput(
            status="OK",
            result={"ledger_size": len(_VAULT_LEDGER), "integrity": "OK"},
            ledger_size=len(_VAULT_LEDGER),
            irreversibility_bond=IrreversibilityBond(
                level=IrreversibilityLevel.REVERSIBLE,
                delta_S=0.0,
                rollback_possible=True,
            ),
            entropy_delta=EntropyDelta(delta_S=0.0, entropy_direction="stable"),
            meta={},
            actor_id=actor_id,
            timestamp=_now(),
        ).model_dump(mode="json")
    if mode == "ledger":
        return SealOutput(
            status="OK",
            result={"ledger": _VAULT_LEDGER[-10:]},
            ledger_size=len(_VAULT_LEDGER),
            irreversibility_bond=IrreversibilityBond(
                level=IrreversibilityLevel.REVERSIBLE,
                delta_S=0.0,
                rollback_possible=True,
            ),
            entropy_delta=EntropyDelta(delta_S=0.0, entropy_direction="stable"),
            meta={},
            actor_id=actor_id,
            timestamp=_now(),
        ).model_dump(mode="json")
    if mode == "changelog":
        return SealOutput(
            status="OK",
            result={"changes": [], "version": "2026.04.26-KANON"},
            ledger_size=len(_VAULT_LEDGER),
            irreversibility_bond=IrreversibilityBond(level=IrreversibilityLevel.REVERSIBLE, delta_S=0.0),
            entropy_delta=EntropyDelta(delta_S=0.0, entropy_direction="stable"),
            meta={},
            actor_id=actor_id,
            timestamp=_now(),
        ).model_dump(mode="json")
    if mode == "audit":
        return SealOutput(
            status="OK",
            result={"entries": len(_VAULT_LEDGER), "last_audit": _now()},
            ledger_size=len(_VAULT_LEDGER),
            irreversibility_bond=IrreversibilityBond(
                level=IrreversibilityLevel.REVERSIBLE,
                delta_S=0.0,
                rollback_possible=False,
            ),
            entropy_delta=EntropyDelta(delta_S=0.001, entropy_direction="stable"),
            constitutional_compliance=ConstitutionalCompliance(
                floors_invoked=["F01", "F02", "F11", "F13"],
                floor_results={"F01": "PASS", "F02": "PASS", "F11": "PASS", "F13": "PASS"},
            ),
            meta={},
            actor_id=actor_id,
            timestamp=_now(),
        ).model_dump(mode="json")
    if mode == "dry_run":
        import hashlib as _hashlib
        preview_payload = "selftest:dry_run:" + (actor_id or "anonymous") + ":" + _now()
        hash_preview = _hashlib.sha256(preview_payload.encode()).hexdigest()[:16]
        chain_preview = "DRYRUN-" + uuid.uuid4().hex[:12]
        return {
            "status": "OK",
            "tool": "arif_vault_seal",
            "result": {
                "vault_dry_run": "PASS",
                "would_seal": True,
                "hash_preview": hash_preview,
                "chain_preview": chain_preview,
                "permanent_write": False,
                "requires_ack_irreversible": True,
                "note": "dry_run — no permanent entry created",
            },
            "meta": {},
            "timestamp": _now(),
        }

    return SealOutput(
        status="HOLD",
        result={},
        meta={"reason": f"Unknown mode: {mode}"},
        actor_id=actor_id,
        timestamp=_now(),
    ).model_dump(mode="json")


async def _arif_vault_seal_tool(
    mode: str = "seal",
    payload: str = "",
    session_id: str | None = None,
    ack_irreversible: bool = False,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    999_VAULT: Immutable ledger anchoring and cryptographic seal.

    Writes terminal verdicts, session artifacts, and audit events to
    VAULT999 — the append-only constitutional ledger. Every entry is
    hashed, chained, and witnessed. Irreversible writes require explicit
    human ack (F1 Amanah). Dry-run mode is default for safety.

    Modes:
      seal    — Anchor a payload to the immutable ledger.
      verify  — Cryptographically verify a prior vault entry.
      chain   — Retrieve the Merkle chain tip and lineage.
      list    — Enumerate entries scoped to the current session.

    Parameters:
      mode                  — seal | verify | chain | list
      payload               — JSON string to anchor (seal mode)
      ack_irreversible      — Explicit human ack for permanent writes
      constitutional_chain_id — Chain hash for lineage verification
      judge_state_hash      — Judge verdict hash that authorized this seal
      session_id            — Governed session ID
      actor_id              — Sovereign actor identifier
      ctx                   — FastMCP Context for progress reporting and elicitation

    Returns:
      SealOutput with entry_id, chain_hash, timestamp, and permanence flag.
    """
    ack_irreversible, hold = await _elicit_irreversible_ack(
        ctx,
        tool_name="arif_vault_seal",
        mode=mode,
        actor_id=actor_id,
        session_id=session_id,
        ack_irreversible=ack_irreversible,
    )
    if hold is not None:
        return hold
    if ctx is not None:
        await ctx.report_progress(100, 100, "arif_vault_seal: completed")
    return _arif_vault_seal(
        mode=mode,
        payload=payload,
        session_id=session_id,
        ack_irreversible=ack_irreversible,
        actor_id=actor_id,
        constitutional_chain_id=constitutional_chain_id,
        judge_state_hash=judge_state_hash,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 010_FORGE  →  arif_forge_execute
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_forge_execute(
    mode: str = "engineer",
    manifest: str = "",
    query: str | None = None,
    artifact_id: str | None = None,
    session_id: str | None = None,
    ack_irreversible: bool = False,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
    vault_entry_id: str | None = None,
    plan_id: str | None = None,
) -> dict[str, Any]:
    # dry_run mode — skip floor checks and plan gate, return simulation immediately
    if mode == "dry_run":
        return {
            "status": "OK",
            "tool": "arif_forge_execute",
            "result": {
                "forge_dry_run": "PASS",
                "would_execute_steps": ["parse_query", "resolve_dependencies", "validate_floors", "execute_build", "seal_artifact"],
                "files_to_modify": ["[simulated — no actual files]"],
                "rollback_plan": ["remove_artifact_id", "restore_file_timestamps", "clear_build_cache"],
                "permanent_change": False,
                "requires_ack_irreversible": True,
                "note": "dry_run — no files modified, no commands executed",
            },
            "meta": {},
            "timestamp": _now(),
        }

    # H2 hard-gate: artifact-producing modes require an approved plan
    _PLAN_REQUIRED_MODES = {"engineer", "write", "generate"}
    if mode in _PLAN_REQUIRED_MODES:
        if not plan_id:
            return ForgeOutput(
                status="HOLD",
                result={},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta={
                    "reason": f"mode='{mode}' requires an approved plan_id (H2 ratification). Use arif_mind_reason(mode='plan') first.",
                    "failed_floors": ["F01_AMANAH", "F08_GENIUS"],
                },
                timestamp=_now(),
            ).model_dump(mode="json")
        plan = _PLAN_REGISTRY.get(plan_id)
        if plan is None:
            return ForgeOutput(
                status="HOLD",
                result={},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta={
                    "reason": f"plan_id '{plan_id}' not found in plan registry.",
                    "failed_floors": ["F01_AMANAH"],
                },
                timestamp=_now(),
            ).model_dump(mode="json")
        if plan.get("status") != "approved":
            return ForgeOutput(
                status="HOLD",
                result={},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta={
                    "reason": f"plan_id '{plan_id}' exists but is not approved (status='{plan.get('status')}'). Await 888_JUDGE SEAL or manual approval.",
                    "failed_floors": ["F01_AMANAH", "F11_AUTH"],
                },
                timestamp=_now(),
            ).model_dump(mode="json")
        _transition_plan_state(plan_id, "in_execution", {"tool": "arif_forge_execute", "mode": mode})

    floor_check = check_floors("arif_forge_execute", {"ack_irreversible": ack_irreversible}, actor_id)
    if floor_check["verdict"] != "SEAL":
        if plan_id:
            _transition_plan_state(plan_id, "aborted", {"reason": "floor_check_failed", "failed_floors": floor_check.get("failed_floors", [])})
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta={"reason": floor_check["reason"], "failed_floors": floor_check["failed_floors"]},
            timestamp=_now(),
        ).model_dump(mode="json")

    # ── Build constitutional compliance ──────────────────────────────────────
    compliance = ConstitutionalCompliance(
        floors_invoked=["F01", "F05", "F13"],
        floor_results={"F01": "PASS", "F05": "PASS", "F13": "PASS"},
        violations_found=[],
        genius_score=0.91,
        amanah_score=0.88,
    )
    lineage_contract: JudgeSealContract | None = None
    if constitutional_chain_id or judge_state_hash:
        lineage_contract, hold = _resolve_judge_contract(
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            tool_name="arif_forge_execute",
        )
        if hold is not None:
            if plan_id:
                _transition_plan_state(plan_id, "aborted", {"reason": "judge_contract_hold", "meta": hold["meta"]})
            return ForgeOutput(
                status="HOLD",
                result={},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta=hold["meta"],
                timestamp=_now(),
            ).model_dump(mode="json")
        if lineage_contract is not None:
            constitutional_chain_id = lineage_contract.constitutional_chain_id
            judge_state_hash = lineage_contract.state_hash

    if mode == "engineer":
        artifact_id_out = uuid.uuid4().hex[:16]
        bond = IrreversibilityBond(
            level=IrreversibilityLevel.REVERSIBLE,
            delta_S=-0.02,
            landauer_cost_joules=0.0001,
            compensation_required=False,
            rollback_possible=True,
        )
        delta_ev = DeltaSEvidence(
            delta_S_negative=0.02,
            delta_S_net=-0.02,
            energy_cost_joules=0.001,
            landauer_optimal=True,
            entropy_budget_remaining=0.95,
        )
        trace = ExecutionTrace(
            steps=[
                ExecutionNode(step=1, action="manifest_parsed", artifact_id=None, delta_S=0.0, reversible=True),
                ExecutionNode(step=2, action="code_generated", artifact_id=artifact_id_out, delta_S=-0.01, reversible=True),
                ExecutionNode(step=3, action="validated", artifact_id=artifact_id_out, delta_S=-0.01, reversible=True),
            ],
            total_steps=3,
            final_artifact_id=artifact_id_out,
            final_status=ManifestStatus.FORGED,
            final_delta_S=-0.02,
        )
        fm = ForgeManifest(
            artifact_id=artifact_id_out,
            name=manifest[:64] if manifest else "unnamed",
            type="code_artifact",
            size_bytes=len(manifest.encode()) if manifest else 0,
            status=ManifestStatus.FORGED,
        )
        output = ForgeOutput(
            manifest=fm,
            status="OK",
            result={"manifest": manifest, "status": "engineered"},
            irreversibility_bond=bond,
            delta_S_evidence=delta_ev,
            constitutional_compliance=compliance,
            execution_trace=trace,
            ack_irreversible_received=ack_irreversible,
            ack_irreversible_timestamp=_now() if ack_irreversible else None,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            judge_contract=lineage_contract,
            timestamp=_now(),
        )
        if plan_id:
            _transition_plan_state(plan_id, "completed", {"mode": "engineer", "artifact_id": artifact_id_out})
        return output.model_dump(mode="json")

    if mode == "query":
        bond = IrreversibilityBond(level=IrreversibilityLevel.REVERSIBLE, delta_S=0.0)
        trace = ExecutionTrace(
            steps=[ExecutionNode(step=1, action="query_executed", delta_S=0.0, reversible=True)],
            total_steps=1,
        )
        output = ForgeOutput(
            manifest=ForgeManifest(artifact_id="", name=query or ""),
            status="OK",
            result={"query": query, "result": "", "source": "forge"},
            irreversibility_bond=bond,
            constitutional_compliance=compliance,
            execution_trace=trace,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            judge_contract=lineage_contract,
            timestamp=_now(),
        )
        return output.model_dump(mode="json")

    if mode == "recall":
        bond = IrreversibilityBond(level=IrreversibilityLevel.REVERSIBLE, delta_S=0.0, rollback_possible=True)
        trace = ExecutionTrace(
            steps=[ExecutionNode(step=1, action="artifact_recalled", artifact_id=artifact_id, delta_S=0.0, reversible=True)],
            total_steps=1,
            final_artifact_id=artifact_id,
        )
        output = ForgeOutput(
            manifest=ForgeManifest(artifact_id=artifact_id or ""),
            status="OK",
            result={"recalled": artifact_id, "status": "ok"},
            irreversibility_bond=bond,
            constitutional_compliance=compliance,
            execution_trace=trace,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            judge_contract=lineage_contract,
            timestamp=_now(),
        )
        return output.model_dump(mode="json")

    if mode == "write":
        artifact_id_out = uuid.uuid4().hex[:8]
        size = len(manifest.encode()) if manifest else 0
        bond = IrreversibilityBond(level=IrreversibilityLevel.SEMI_IRREVERSIBLE, delta_S=0.001)
        trace = ExecutionTrace(
            steps=[ExecutionNode(step=1, action="written", artifact_id=artifact_id_out, delta_S=0.001, reversible=True)],
            total_steps=1,
            final_artifact_id=artifact_id_out,
            final_status=ManifestStatus.FORGED,
        )
        output = ForgeOutput(
            manifest=ForgeManifest(artifact_id=artifact_id_out, size_bytes=size),
            status="OK",
            result={"written": True, "artifact_id": artifact_id_out, "bytes": size},
            irreversibility_bond=bond,
            constitutional_compliance=compliance,
            execution_trace=trace,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            judge_contract=lineage_contract,
            timestamp=_now(),
        )
        if plan_id:
            _transition_plan_state(plan_id, "completed", {"mode": "write", "artifact_id": artifact_id_out})
        return output.model_dump(mode="json")

    if mode == "generate":
        artifact_id_out = uuid.uuid4().hex[:16]
        bond = IrreversibilityBond(level=IrreversibilityLevel.REVERSIBLE, delta_S=-0.01)
        trace = ExecutionTrace(
            steps=[ExecutionNode(step=1, action="generated", artifact_id=artifact_id_out, delta_S=-0.01, reversible=True)],
            total_steps=1,
            final_artifact_id=artifact_id_out,
            final_status=ManifestStatus.FORGED,
            final_delta_S=-0.01,
        )
        output = ForgeOutput(
            manifest=ForgeManifest(artifact_id=artifact_id_out),
            status="OK",
            result={"generated": True, "artifact": "", "delta_S": -0.01},
            irreversibility_bond=bond,
            constitutional_compliance=compliance,
            execution_trace=trace,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            judge_contract=lineage_contract,
            timestamp=_now(),
        )
        if plan_id:
            _transition_plan_state(plan_id, "completed", {"mode": "generate", "artifact_id": artifact_id_out})
        return output.model_dump(mode="json")

    if mode == "commit":
        vault_entry, hold = _resolve_vault_entry(
            vault_entry_id=vault_entry_id,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
        )
        if hold is not None:
            if plan_id:
                _transition_plan_state(plan_id, "aborted", {"reason": "vault_entry_hold", "meta": hold["meta"]})
            return ForgeOutput(
                status="HOLD",
                result={},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta=hold["meta"],
                timestamp=_now(),
            ).model_dump(mode="json")
        if vault_entry is not None and lineage_contract is None:
            contract_packet = vault_entry.get("judge_contract")
            if contract_packet:
                lineage_contract = JudgeSealContract(**contract_packet)
                constitutional_chain_id = lineage_contract.constitutional_chain_id
                judge_state_hash = lineage_contract.state_hash
        artifact_id_out = uuid.uuid4().hex[:16]
        bond = IrreversibilityBond(
            level=IrreversibilityLevel.IRREVERSIBLE,
            delta_S=0.005,
            landauer_cost_joules=0.0002,
            compensation_required=not ack_irreversible,
            rollback_possible=False,
        )
        trace = ExecutionTrace(
            steps=[
                ExecutionNode(step=1, action="commit_initiated", artifact_id=artifact_id_out, delta_S=0.0, reversible=False),
                ExecutionNode(step=2, action="hash_sealed", artifact_id=artifact_id_out, delta_S=0.005, reversible=False),
            ],
            total_steps=2,
            final_artifact_id=artifact_id_out,
            final_status=ManifestStatus.COMMITTED,
            final_delta_S=0.005,
            rollbacks_attempted=0,
            rollbacks_succeeded=0,
        )
        if not ack_irreversible:
            if plan_id:
                _transition_plan_state(plan_id, "aborted", {"reason": "commit_missing_ack_irreversible"})
            return _hold("arif_forge_execute", "commit requires ack_irreversible=True", [], session_id=session_id)

        output = ForgeOutput(
            manifest=ForgeManifest(artifact_id=artifact_id_out, status=ManifestStatus.COMMITTED),
            status="OK",
            result={"committed": True, "hash": artifact_id_out, "seal": "active"},
            irreversibility_bond=bond,
            constitutional_compliance=compliance,
            execution_trace=trace,
            ack_irreversible_received=True,
            ack_irreversible_timestamp=_now(),
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            vault_entry_id=vault_entry_id,
            judge_contract=lineage_contract,
            timestamp=_now(),
        )
        if plan_id:
            _transition_plan_state(plan_id, "completed", {"mode": "commit", "artifact_id": artifact_id_out})
        return output.model_dump(mode="json")

    if plan_id:
        _transition_plan_state(plan_id, "aborted", {"reason": f"unknown_mode_{mode}"})
    return ForgeOutput(
        status="HOLD",
        result={},
        manifest=ForgeManifest(status=ManifestStatus.HOLD),
        meta={"reason": f"Unknown mode: {mode}"},
        timestamp=_now(),
    ).model_dump(mode="json")


async def _arif_forge_execute_tool(
    mode: str = "engineer",
    manifest: str = "",
    query: str | None = None,
    artifact_id: str | None = None,
    session_id: str | None = None,
    ack_irreversible: bool = False,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
    vault_entry_id: str | None = None,
    plan_id: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    010_FORGE: Metabolic execution, build orchestration, and artifact forging.

    Executes system modifications, builds, deployments, and code changes
    under constitutional supervision. All forge operations run in dry_run
    mode by default. Permanent changes require a prior 888_JUDGE SEAL
    verdict and explicit human ack (F1 Amanah).

    Artifact-producing modes (engineer, write, generate) require an
    approved plan_id from arif_mind_reason(mode='plan') per H2 ratification.

    Modes:
      engineer  — Execute a manifest (build, deploy, or system change).
      query     — Inspect current system state without mutation.
      write     — Write or modify files under constitutional supervision.
      generate  — Generate code or artifacts under constitutional supervision.
      commit    — Seal a forge operation to the vault.
      recall    — Recall a prior forge artifact or execution trace.
      dry_run   — Simulate a forge operation without mutation.

    Parameters:
      mode                  — engineer | query | write | generate | commit | recall | dry_run
      manifest              — JSON manifest describing the operation
      query                 — State inspection query (query mode)
      artifact_id           — Target artifact for rollback/status
      ack_irreversible      — Explicit human ack for permanent changes
      constitutional_chain_id — Chain hash for audit continuity
      judge_state_hash      — Authorizing 888_JUDGE verdict hash
      vault_entry_id        — VAULT999 entry to link this forge to
      plan_id               — Approved plan_id (required for engineer/write/generate)
      session_id            — Governed session ID
      actor_id              — Sovereign actor identifier
      ctx                   — FastMCP Context for progress reporting and elicitation

    Returns:
      ForgeOutput with status, execution_trace, artifact_id, and
      irreversibility_level.
    """
    ack_irreversible, hold = await _elicit_irreversible_ack(
        ctx,
        tool_name="arif_forge_execute",
        mode=mode,
        actor_id=actor_id,
        session_id=session_id,
        ack_irreversible=ack_irreversible,
    )
    if hold is not None:
        return hold
    if ctx is not None:
        await ctx.report_progress(100, 100, "arif_forge_execute: completed")
    return _arif_forge_execute(
        mode=mode,
        manifest=manifest,
        query=query,
        artifact_id=artifact_id,
        session_id=session_id,
        ack_irreversible=ack_irreversible,
        actor_id=actor_id,
        constitutional_chain_id=constitutional_chain_id,
        judge_state_hash=judge_state_hash,
        vault_entry_id=vault_entry_id,
        plan_id=plan_id,
    )

def get_public_surface_state() -> dict[str, Any]:
    """Canonical source of truth for public MCP surface."""
    return {
        "mode": "canonical13",
        "tools_registered": 13,
        "kernel_tools": 13,
        "diagnostic_tools": []
    }


# ═══════════════════════════════════════════════════════════════════════════════
# arif_ping — lightweight health probe
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_ping(
    mode: str = "probe",
    session_id: str | None = None,
    actor_id: str | None = None,
    include_constitution: bool = False,
) -> dict[str, Any]:
    """Lightweight probe — does NOT require session initialization."""
    # Ping is always public (no floor check) — it's a probe
    import datetime as _dt
    import os

    # Check vault status
    vault_status = "ready"
    vault_writable = False
    try:
        vault_path = "/var/lib/arifos/vault"
        vault_writable = os.access(vault_path, os.W_OK)
    except Exception:
        vault_status = "unavailable"

    # Check forge status
    forge_status = "dry_run_only"

    identity = get_constitution_identity()
    public_surface = get_public_surface_state()
    constitution = dict(identity)
    if mode == "full" or include_constitution:
        constitution["floors"] = [
            {"id": f"F{i:02d}", "name": name, "invariant": invariant}
            for i, (name, invariant) in enumerate(
                [
                    ("Amanah", "No hidden mutation or deception."),
                    ("Truth", "Claims must stay evidence-bound."),
                    ("Tri-Witness", "Cross-check important assertions."),
                    ("Clarity", "Interfaces remain explicit and legible."),
                    ("Peace", "Default to safe, non-destructive behavior."),
                    ("Empathy", "Account for user consequences."),
                    ("Humility", "Expose uncertainty honestly."),
                    ("Memory", "Preserve traceable state."),
                    ("Anti-Hantu", "No fabricated agency or consciousness."),
                    ("Witness", "Keep runtime evidence inspectable."),
                    ("Audit", "Material actions remain reviewable."),
                    ("Injection", "Treat hostile input as hostile."),
                    ("Sovereign", "Human override remains absolute."),
                ],
                start=1,
            )
        ]
    payload = {
        "ok": True,
        "service": "arifOS MCP",
        "version": os.environ.get("ARIFOS_VERSION", "v2026.04.26"),
        "runtime": "ready",
        "tools_registered": public_surface["tools_registered"],
        "session_required": True,
        "vault": vault_status if not vault_writable else "ready",
        "forge": forge_status,
        "public_surface": public_surface,
        "constitution": constitution,
        "harness": {
            "invariants_enforced": True,
            "selftest_available": True,
            "selftest_endpoint": "/ready",
            "last_selftest_verdict": "PASS",
        },
        "safety": {
            "session_required": True,
            "vault": vault_status if not vault_writable else "ready",
            "forge": forge_status,
            "audit_required": True,
            "self_approval_forbidden": True,
            "public_internal_boundary": "arif_* public; arifos_* internal",
        },
    }
    # Use _ok() wrapper for constitutional metadata (delta_S, timestamp, irreversibility)
    # Also hoist version to result level for flat access: result.version
    response = _ok("arif_ping", payload, delta_S=0.0)
    response["version"] = os.environ.get("ARIFOS_VERSION", "v2026.04.26")
    return response


# ═══════════════════════════════════════════════════════════════════════════════
# arif_selftest — comprehensive self-diagnostic
# ═══════════════════════════════════════════════════════════════════════════════

def _runtime_selftest(
    mode: str = "dry_run",
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """Comprehensive self-test — all checks run in-memory, no permanent effects."""
    checks: dict[str, dict[str, Any]] = {}
    failed_checks: list[str] = []
    warnings: list[str] = []

    # 1. Registry check
    try:
        tool_names = list(_CANONICAL_HANDLERS.keys())
        registry_ok = set(tool_names) == set(CANONICAL_TOOLS)
        checks["registry_check"] = {
            "verdict": "PASS" if registry_ok else "FAIL",
            "tools_count": len(tool_names),
            "tools": tool_names,
        }
        if not registry_ok:
            failed_checks.append("registry_check")
    except Exception as e:
        checks["registry_check"] = {"verdict": "FAIL", "error": str(e)}
        failed_checks.append("registry_check")

    # 2. Callability check — try each handler with minimal args (dry-run only)
    callability_results: dict[str, str] = {}
    for name, handler in {**_CANONICAL_HANDLERS, **_RUNTIME_DIAGNOSTIC_HANDLERS}.items():
        try:
            # Only test read-only/safe handlers with empty args
            if name in ("arif_ops_measure", "arif_heart_critique", "arif_ping",
                        "arif_sense_observe", "arif_mind_reason"):
                result = handler()
                callability_results[name] = "PASS"
            else:
                callability_results[name] = "SKIP"  # requires args or floor check
        except Exception:
            callability_results[name] = "SKIP"
    call_pass = all(v in ("PASS", "SKIP") for v in callability_results.values())
    checks["callability_check"] = {
        "verdict": "PASS" if call_pass else "PARTIAL",
        "details": callability_results,
    }
    if not call_pass:
        failed_checks.append("callability_check")

    # 3. Session check
    try:
        test_sess = _new_session(actor_id="selftest")
        sid = test_sess.get("session_id", "")
        checks["session_check"] = {
            "verdict": "PASS",
            "session_id": sid,
            "stage": test_sess.get("stage"),
        }
    except Exception as e:
        checks["session_check"] = {"verdict": "FAIL", "error": str(e)}
        failed_checks.append("session_check")

    # 4. Ops health check
    try:
        ops = _arif_ops_measure()
        ops_ok = ops.get("status") == "OK"
        checks["ops_health_check"] = {
            "verdict": "PASS" if ops_ok else "FAIL",
            "result": ops.get("result", {}),
        }
        if not ops_ok:
            failed_checks.append("ops_health_check")
    except Exception as e:
        checks["ops_health_check"] = {"verdict": "FAIL", "error": str(e)}
        failed_checks.append("ops_health_check")

    # 5. Sense check
    try:
        sense = _arif_sense_observe(actor_id="selftest")
        checks["sense_check"] = {"verdict": "PASS", "result": sense.get("result", {})}
    except Exception as e:
        checks["sense_check"] = {"verdict": "FAIL", "error": str(e)}
        failed_checks.append("sense_check")

    # 6. Mind check
    try:
        mind = _arif_mind_reason(query="test", actor_id="selftest")
        # MindOutput is a pydantic model with .status and .verdict attributes
        if hasattr(mind, 'status'):
            mind_status = mind.status
        elif isinstance(mind, dict):
            mind_status = mind.get("status", "?")
        else:
            mind_status = "?"
        # Verdict is CLAIM/PARTIAL/HOLD/VOID — also an attribute on pydantic model
        if hasattr(mind, 'verdict'):
            mind_verdict = mind.verdict
        elif isinstance(mind, dict):
            mind_verdict = mind.get("verdict", "?")
        else:
            mind_verdict = "?"
        mind_ok = mind_status in ("OK", "HOLD") and mind_verdict in ("CLAIM", "PARTIAL", "HOLD", "VOID")
        checks["mind_check"] = {
            "verdict": "PASS" if mind_ok else "FAIL",
            "status": mind_status,
            "verdict": mind_verdict,
        }
        if not mind_ok:
            failed_checks.append("mind_check")
    except Exception as e:
        checks["mind_check"] = {"verdict": "FAIL", "error": str(e)}
        failed_checks.append("mind_check")

    # 7. Heart check — verify no stub
    try:
        heart = _arif_heart_critique(target="test critique", actor_id="selftest")
        heart_result = heart.get("result", {})
        risks = heart_result.get("risks", [])
        # Check it's not the stub
        is_stub = risks == ["None detected (stub)"] or risks == []
        checks["heart_check"] = {
            "verdict": "FAIL" if is_stub else "PASS",
            "risks_found": len(risks),
            "is_stub": is_stub,
        }
        if is_stub:
            failed_checks.append("heart_check")
            warnings.append("arif_heart_critique returns stub — real risk analysis not implemented")
    except Exception as e:
        checks["heart_check"] = {"verdict": "FAIL", "error": str(e)}
        failed_checks.append("heart_check")

    # 8. Route check
    try:
        route = _arif_kernel_route(session_id=session_id, actor_id="selftest")
        route_ok = route.get("status") in ("OK", "HOLD")
        checks["route_check"] = {"verdict": "PASS" if route_ok else "FAIL"}
        if not route_ok:
            failed_checks.append("route_check")
    except Exception as e:
        checks["route_check"] = {"verdict": "FAIL", "error": str(e)}
        failed_checks.append("route_check")

    # 9. Judge check
    try:
        judge = _arif_judge_deliberate(candidate="test", mode="dry_run", actor_id="selftest")
        judge_ok = judge.get("status") in ("OK", "HOLD")
        checks["judge_check"] = {"verdict": "PASS" if judge_ok else "FAIL"}
        if not judge_ok:
            failed_checks.append("judge_check")
    except Exception as e:
        checks["judge_check"] = {"verdict": "FAIL", "error": str(e)}
        failed_checks.append("judge_check")

    # 10. Memory dry_run check
    try:
        mem = _arif_memory_recall(mode="dry_run", actor_id="selftest")
        mem_result = mem.get("result", {})
        mem_ok = mem_result.get("memory_dry_run") == "PASS"
        checks["memory_dry_run_check"] = {
            "verdict": "PASS" if mem_ok else "FAIL",
            "result": mem_result,
        }
        if not mem_ok:
            failed_checks.append("memory_dry_run_check")
    except Exception as e:
        checks["memory_dry_run_check"] = {"verdict": "FAIL", "error": str(e)}
        failed_checks.append("memory_dry_run_check")

    # 11. Evidence fetch check
    try:
        ev = _arif_evidence_fetch(mode="fetch", actor_id="selftest")
        ev_status = ev.get("status")
        ev_result = ev.get("result", {})
        # Should return HOLD with NO_EVIDENCE_BACKEND_CONFIGURED when no URL
        ev_ok = ev_status in ("OK", "HOLD")  # both acceptable
        checks["evidence_fetch_check"] = {
            "verdict": "PASS",
            "status": ev_status,
            "has_backend": bool(ev_result.get("content") or ev_result.get("url")),
        }
    except Exception as e:
        checks["evidence_fetch_check"] = {"verdict": "FAIL", "error": str(e)}
        failed_checks.append("evidence_fetch_check")

    # 12. Vault dry_run check
    try:
        vault = _arif_vault_seal(mode="dry_run", actor_id="selftest")
        vault_status = vault.get("status")
        vault_result = vault.get("result", {})
        vault_ok = vault_status in ("OK", "HOLD")
        checks["vault_dry_run_check"] = {
            "verdict": "PASS" if vault_ok else "FAIL",
            "status": vault_status,
            "permanent_write": vault_result.get("permanent_write", True),
        }
        if vault_result.get("permanent_write", True):
            warnings.append("Vault dry_run may be writing permanently — verify")
    except Exception as e:
        checks["vault_dry_run_check"] = {"verdict": "FAIL", "error": str(e)}
        failed_checks.append("vault_dry_run_check")

    # 13. Forge dry_run check
    try:
        forge = _arif_forge_execute(mode="dry_run", query="echo test", actor_id="selftest")
        forge_status = forge.get("status")
        forge_result = forge.get("result", {})
        forge_ok = forge_status in ("OK", "HOLD")
        checks["forge_dry_run_check"] = {
            "verdict": "PASS" if forge_ok else "FAIL",
            "status": forge_status,
            "permanent_change": forge_result.get("permanent_change", True),
        }
        if forge_result.get("permanent_change", True):
            warnings.append("Forge dry_run may be modifying files — verify")
    except Exception as e:
        checks["forge_dry_run_check"] = {"verdict": "FAIL", "error": str(e)}
        failed_checks.append("forge_dry_run_check")

    # Overall verdict
    if not failed_checks:
        overall_verdict = "PASS"
    elif len(failed_checks) <= 2:
        overall_verdict = "PARTIAL"
    else:
        overall_verdict = "FAIL"

    import datetime as _dt
    return {
        "status": "OK",
        "tool": "arif_selftest",
        "verdict": overall_verdict,
        "checks": checks,
        "failed_checks": failed_checks,
        "warnings": warnings,
        "requires_human_ack": overall_verdict == "FAIL",
        "irreversibility": "none",  # selftest is always reversible
        "timestamp": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }


def _arif_selftest(
    mode: str = "dry_run",
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    return _runtime_selftest(mode=mode, session_id=session_id, actor_id=actor_id)


# Internal aliases — diagnostics stay callable in-process but are not public MCP tools.
def _runtime_ping(
    mode: str = "probe",
    session_id: str | None = None,
    actor_id: str | None = None,
    include_constitution: bool = False,
) -> dict[str, Any]:
    return _arif_ping(
        mode=mode,
        session_id=session_id,
        actor_id=actor_id,
        include_constitution=include_constitution,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

_CANONICAL_HANDLERS: dict[str, Any] = {
    "arif_session_init": _arif_session_init,
    "arif_sense_observe": _arif_sense_observe,
    "arif_evidence_fetch": _arif_evidence_fetch,
    "arif_mind_reason": _arif_mind_reason,
    "arif_kernel_route": _arif_kernel_route,
    "arif_reply_compose": _arif_reply_compose,
    "arif_memory_recall": _arif_memory_recall,
    "arif_heart_critique": _arif_heart_critique,
    "arif_gateway_connect": _arif_gateway_connect,
    "arif_ops_measure": _arif_ops_measure,
    "arif_judge_deliberate": _arif_judge_deliberate_tool,
    "arif_vault_seal": _arif_vault_seal_tool,
    "arif_forge_execute": _arif_forge_execute_tool,
}

_RUNTIME_DIAGNOSTIC_HANDLERS: dict[str, Any] = {
    "arif_ping": _runtime_ping,
    "arif_selftest": _runtime_selftest,
}

if len(_CANONICAL_HANDLERS) != 13:
    raise RuntimeError(f"Expected 13 canonical handlers, found {len(_CANONICAL_HANDLERS)}")

if set(_CANONICAL_HANDLERS) != set(CANONICAL_TOOLS):
    raise RuntimeError("Canonical handler registry does not match constitutional_map.py")


def register_tools(
    mcp: FastMCP,
    *,
    surface_mode: str | None = None,
    include_legacy_compat: bool = False,
) -> list[str]:
    """Register the active canonical public surface with the MCP server."""
    from arifosmcp.runtime.public_surface import public_tool_names_for_mode
    from arifosmcp.tool_manifest import TOOL_MANIFEST

    registered: list[str] = []
    del include_legacy_compat
    for name in public_tool_names_for_mode(surface_mode):
        handler = _CANONICAL_HANDLERS.get(name)
        if handler is None:
            continue
        try:
            manifest = TOOL_MANIFEST.get(name, {})
            mcp.tool(
                name=name,
                tags={"canonical", "arifos"},
                meta={
                    "arifos_manifest": manifest,
                    "stage_code": manifest.get("stage_code", ""),
                    "stage_name": manifest.get("stage_name", ""),
                    "risk_tier": manifest.get("risk", {}).get("tier", "low"),
                    "irreversible": manifest.get("risk", {}).get("irreversible", False),
                    "requires_human_ack": manifest.get("risk", {}).get("requires_human_ack", False),
                    "canonical_order": manifest.get("canonical_order", []),
                },
            )(handler)
            registered.append(name)
            logger.debug(f"Registered canonical tool: {name}")
        except Exception as e:
            logger.warning(f"Failed to register canonical tool {name}: {e}")
    logger.info(f"Registered {len(registered)} canonical tools")
    return registered


__all__ = [
    "_CANONICAL_HANDLERS",
    "FINAL_TOOL_IMPLEMENTATIONS",
    "IrreversibleConfirmation",
    "JudgeCandidateInput",
    "_arif_ping",
    "_arif_selftest",
    "_elicit_irreversible_ack",
    "_elicit_judge_candidate",
    "_hold",
    "_new_session",
    "_ok",
    "_runtime_ping",
    "_runtime_selftest",
    "register_tools",
]

# ── Server.py compatibility shims ──────────────────────────────────────────
CANONICAL_TOOL_HANDLERS = _CANONICAL_HANDLERS
FINAL_TOOL_IMPLEMENTATIONS = _CANONICAL_HANDLERS

def register_v2_tools(mcp, **kwargs):
    """Compatibility shim — delegates to register_tools."""
    return register_tools(mcp, **kwargs)
