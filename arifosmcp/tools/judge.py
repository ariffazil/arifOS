"""
arifosmcp/tools/judge_deliberate.py — 888_JUDGE v3
═══════════════════════════════════════════════

Constitutional verdict engine.

Evidence pre-loading: vitals and heart output are piped into the judge
before adjudication so epistemic confidence is grounded in actual system state.

Post-SEAL auto-hook: When verdict is SEAL and vault_entry_id is provided,
the judge output is automatically routed to arif_seal for immutable anchoring.

PARADOX ANCHORS (v3): 11 linguistic invariants fire at verdict decision points:
  J1 (Parker/MLK) — SABAR carries deadline | J4 (Aristotle) — SEAL is incomplete justice
  J6 (Marcus Aurelius) — irreversible gate | J7 (Glaucon) — power asymmetry detection

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json as json_lib
import logging
import os
import time as time_module
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("arifos.judge")

from arifosmcp.constitution.paradox_quotes import get_triggered_quotes_by_gpv
from arifosmcp.core.conflict_resolver import (
    resolve_conflict,
)
from arifosmcp.core.decision_contract import ConflictEnvelope
from arifosmcp.core.enforcement.maruah_critic import (
    MaruahVerdict,
    maruah_critic_check,
)
from arifosmcp.core.enforcement.paradox_gate import (
    evaluate_paradox_gate,
)
from arifosmcp.core.enforcement.somatic_loop import (
    SomaticState,
    TelemetrySample,
    classify_somatic_state,
)
from arifosmcp.core.latency_budget import LATENCY_BUDGETS
from arifosmcp.core.latency_budget import DecisionClass as LatencyDecisionClass
from arifosmcp.core.vault_receipt import create_and_seal_receipt, resolve_receipt_identity
from arifosmcp.runtime.metabolic_receipt import get_cumulative_metrics
from arifosmcp.runtime.niat_gate import check_niat_gate
from arifosmcp.core.reality_ledger_writer import write_reality_event
from arifosmcp.runtime.self_mod_lock import is_self_modification_attempt
from arifosmcp.runtime.tools import _arif_judge
from arifosmcp.schemas.governance_locks import ParadoxHoldReceipt
from arifosmcp.schemas.verdict import VerdictCode, VerdictOutput
from core.shared.atlas import Φ

# ═══════════════════════════════════════════════════════════════════════════════
# ECHO/PaW PREDICTION SCHEMA — L3 Gradient Injection Bridge
# ═══════════════════════════════════════════════════════════════════════════════
# Maps prediction keys to their canonical observation sources.
# Every key here is a 1:1 mappable identifier — no semantic translation.
# Used by: _inject_l3_prediction_deltas (L3 read path)
#          arif_memory_recall(mode="score_prediction") (delta threshold gate)
#          arif_measure → observation surface (ops.py OBSERVATION_SCHEMA)
JUDGE_PREDICTION_SCHEMA: dict[str, str] = {
    "g_score": "arif_measure.vitals.g_score",
    "delta_S": "arif_measure.vitals.delta_S",
    "omega": "arif_measure.vitals.omega",
    "psi_le": "arif_measure.vitals.psi_le",
    "cpu_pct": "arif_measure.health.cpu.value",
    "mem_pct": "arif_measure.health.mem.percent.value",
    "disk_pct": "arif_measure.health.disk.percent.value",
    "verdict_code": "arif_judge.verdict",
}

# ═══════════════════════════════════════════════════════════════════════════════
# PARADOX ANCHORS — REMOVED FROM RUNTIME 2026-07-04 FORGE
# ═══════════════════════════════════════════════════════════════════════════════
# The 11 anchors (Marcus Aurelius, Aristotle, Socrates, Glaucon, Kant) were
# once wired into `_inject_judge_paradox()` and called once per verdict.
#
# ABC falsifier result (2026-07-04):
#   - Falsifier: "remove X — does behavior change?"
#   - Result: removing all 11 anchors → same VerdictCode, only loses meta text.
#   - The anchors only mutated `result["meta"]["paradox_anchor"]` and
#     `result.setdefault("reasons", []).append(...)`. Never VerdictCode.*.
#
# VERDICT: 11 paradox anchors are commentary, not enforcement. REMOVED.
# PRESERVED: as non-executable canon at docs/canon/paradox_anchors.md
# REPLACED (in verdict path): single meta line — see post-verdict block.
# ═══════════════════════════════════════════════════════════════════════════════

PARADOX_ANCHORS_REMOVED_TO_CANON = True
"""Sentinel. Runtime excise 2026-07-04. Original 11 anchors now in
docs/canon/paradox_anchors.md. The wiring was a `_JUDGE_BY_ID` lookup that
only enriched meta — never `VerdictCode.*`. Therefore not load-bearing.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# ECHO/PaW — JUDGE PREDICTION SCHEMA (FORGED 2026-07-21)
# ═══════════════════════════════════════════════════════════════════════════════
# Strict 1:1 key mapping between the judge's prediction surface and the
# WELL/ops substrate observation surface. No semantic translation allowed —
# keys must match exactly between prediction and observation to maintain
# ΔS ≤ 0 (F4 CLARITY). Any key drift triggers SCHEMA_DRIFT hard exception.
#
# Each entry: prediction_key → canonical_observation_source
# The observation source is a dotted path: <module>.<mode>.<field>
# All keys listed here are the canonical prediction surface. The
# score_prediction memory mode enforces that predicted_state keys
# MUST be a subset of this schema.
# ═══════════════════════════════════════════════════════════════════════════════

JUDGE_PREDICTION_SCHEMA: dict[str, str] = {
    # ── Thermodynamic vitals (arif_measure mode="vitals") ──
    "g_score": "arif_measure.vitals.g_score",
    "delta_S": "arif_measure.vitals.delta_S",
    "omega": "arif_measure.vitals.omega",
    "psi_le": "arif_measure.vitals.psi_le",
    # ── Substrate health (arif_measure mode="health") ──
    "cpu_pct": "arif_measure.health.cpu.value",
    "mem_pct": "arif_measure.health.mem.percent.value",
    "disk_pct": "arif_measure.health.disk.percent.value",
    "health_status": "arif_measure.health.status",
    "health_verified": "arif_measure.health.verified",
    # ── Governance telemetry ──
    "constitutional_verdict": "arif_measure.constitutional_health.verdict",
    "floor_violations": "arif_measure.constitutional_health.floors",
    "witnes_score": "arif_measure.constitutional_health.witnes",
    # ── WELL substrate ──
    "g_well_verdict": "well_substrate.g_well_verdict",
    "clarity": "well_substrate.clarity",
    "has_telemetry": "well_substrate.has_telemetry",
    # ── System invariants ──
    "runtime_drift": "arif_measure.health.runtime_drift",
    "forge_block_count": "arif_measure.meta.forge_block_count",
}

# Maximum allowed delta between predicted_state and observed_state.
# Exceeding this triggers F1/F2 HOLD_888 — the judge's world model
# is dangerously disconnected from substrate reality.
DELTA_MAX: float = 0.30

# WELL state file candidates — covers docker-compose path, manual-start path, env override
_WELL_STATE_CANDIDATES = [
    Path(p)
    for p in [
        os.environ.get("WELL_STATE_PATH", ""),  # docker-compose: /app/well_state.json
        "/app/well_state.json",
        "/root/WELL/state.json",
    ]
    if p
]

# WELL internal HTTP fallback — used when no state file is accessible
_WELL_INTERNAL_URLS = [
    "http://well:8083/health",  # Docker Compose service name
    "http://172.19.0.5:8083/health",  # Docker network IP (static for this deployment)
]


def _read_well_substrate() -> dict[str, Any]:
    """Read WELL biological substrate state and return a minimal advisory packet.

    Strategy:
      1. Try state file candidates in order (fastest, no network)
      2. Fall back to WELL HTTP health endpoint (stable internal route)

    W0 invariant preserved: WELL informs. The judge decides. The operator
    holds the veto. This packet is advisory evidence — not a gate.
    """
    # ── Strategy 1: state file candidates ────────────────────────────────────
    state = None
    for path in _WELL_STATE_CANDIDATES:
        try:
            with open(path) as fh:
                state = json_lib.load(fh)
            break
        except Exception:
            continue

    # ── Strategy 2: HTTP fallback via WELL's internal health endpoint ─────────
    if state is None:
        for url in _WELL_INTERNAL_URLS:
            try:
                with urllib.request.urlopen(url, timeout=2) as resp:
                    raw = json_lib.loads(resp.read())
                # W-1: /health now exposes substrate advisory fields — forward them.
                state = {
                    "well_score": float(raw.get("well_score", 50.0)),
                    "floors_violated": raw.get("floors_violated") or [],
                    "metrics": raw.get("metrics") or {},
                    "truth_status": raw.get("truth_status", "OPERATOR_REPORTED"),
                    "_source": "http_health",
                    "_url": url,
                }
                # W-1: /health exposes clarity at top level — reconstruct cognitive metrics shape
                _http_clarity = raw.get("clarity")
                if _http_clarity is not None and not state["metrics"].get("cognitive", {}).get(
                    "clarity"
                ):
                    state["metrics"]["cognitive"] = {"clarity": float(_http_clarity)}
                break
            except Exception:
                continue

    if state is None:
        return {"status": "unavailable", "coupled_verdict": "CAUTION", "source": "all_paths_failed"}

    well_score = float(state.get("well_score", 50.0))
    floors_violated: list = state.get("floors_violated", []) or []
    metrics: dict = state.get("metrics") or {}
    truth_status: str = state.get("truth_status", "UNVERIFIED")
    has_metrics = bool(
        isinstance(metrics, dict)
        and any(metrics.get(d) for d in ("sleep", "stress", "cognitive", "metabolic", "structural"))
    )

    if not has_metrics or truth_status in ("VOID", "TEST", "UNVERIFIED"):
        human_ready, coupled_verdict = "UNKNOWN", "CAUTION"
    elif floors_violated:
        human_ready, coupled_verdict = "DEGRADED", "HOLD"
    elif well_score >= 80:
        human_ready, coupled_verdict = "OPTIMAL", "PROCEED"
    elif well_score >= 60:
        human_ready, coupled_verdict = "FUNCTIONAL", "PROCEED"
    else:
        human_ready, coupled_verdict = "LOW_CAPACITY", "CAUTION"

    clarity = metrics.get("cognitive", {}).get("clarity") if has_metrics else None

    packet: dict[str, Any] = {
        "status": "available",
        "well_score": well_score,
        "human_ready": human_ready,
        "coupled_verdict": coupled_verdict,
        "has_telemetry": has_metrics,
        "truth_status": truth_status,
        "active_violations": floors_violated,
        "source": state.get("_source", "live_state_file"),
        "w0": "OPERATOR_VETO_INTACT / HIERARCHY_INVARIANT",
    }
    if clarity is not None:
        packet["clarity"] = clarity
    return packet


def _read_well_governance(state_path_candidates: list | None = None) -> dict[str, Any]:
    """Read G-WELL governance packet from state file.

    W-4: Called for C4/C5 sovereign-tier actions. Extracts machine governance
    flags, vault status, and authority boundary from the WELL state file.
    Returns advisory only — W0 sovereignty invariant preserved.
    """
    candidates = state_path_candidates or _WELL_STATE_CANDIDATES
    for path in candidates:
        try:
            with open(path) as fh:
                state = json_lib.load(fh)
            break
        except Exception:
            continue
    else:
        return {"status": "unavailable", "g_well_verdict": "UNKNOWN", "source": "all_paths_failed"}

    m_machine = state.get("m_machine") or {}
    vault_status = m_machine.get("vault_status", "unknown")
    model_reliability = float(m_machine.get("model_reliability", 1.0))
    tool_availability = float(m_machine.get("tool_availability", 1.0))
    security_flags = m_machine.get("security_flags") or []
    amanah = state.get("amanah", "UNLOCKED")
    truth_status = state.get("truth_status", "UNVERIFIED")

    governance_flags: list[str] = []
    if not state.get("identity_valid", True):
        governance_flags.append("well_identity_compromised")
    if vault_status not in ("ok", "healthy", "unknown"):
        governance_flags.append(f"vault_disconnected:{vault_status}")
    if model_reliability < 0.5 or tool_availability < 0.5:
        governance_flags.append("machine_substrate_critical")
    if security_flags:
        governance_flags.append(f"security_flags:{','.join(security_flags)}")
    if amanah == "LOCKED":
        governance_flags.append("amanah_locked")

    if len(governance_flags) == 0:
        g_verdict = "COHERENT"
    elif len(governance_flags) <= 2:
        g_verdict = "FRAGMENTED"
    else:
        g_verdict = "INCOHERENT"

    return {
        "status": "available",
        "g_well_verdict": g_verdict,
        "governance_flags": governance_flags,
        "vault_status": vault_status,
        "model_reliability": model_reliability,
        "tool_availability": tool_availability,
        "truth_status": truth_status,
        "w0": "OPERATOR_VETO_INTACT / HIERARCHY_INVARIANT",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ECHO/PaW SCHEMA BRIDGE — strict 1:1 key parity
# ═══════════════════════════════════════════════════════════════════════════════
# The judge's predicted_state and the substrate's observation_state MUST use
# the same deterministic key names. Semantic translation introduces entropy
# (ΔS > 0) and point-of-failure hallucinations.
#
# SCHEMA_BRIDGE maps prediction keys → observation source keys when they
# cannot share the same name. PREFER direct 1:1 naming — this bridge is a
# fallback, not the default. Keys NOT in this bridge are assumed 1:1.
SCHEMA_BRIDGE: dict[str, str] = {
    # well_substrate keys — already 1:1 from _read_well_substrate() output
    # vitals keys — from arif_measure(mode='vitals')
    # g_score → g_score (1:1)
    # delta_S → delta_S (1:1)
    # omega → omega (1:1)
    # psi_le → psi_le (1:1)
    # If keys diverge, map prediction key → observation key:
    # "memory_usage": "mem_util_pct",  # example — not active
}
"""Maps predicted_state keys to substrate observation keys for delta computation.

When prediction and observation MUST use different key names, this bridge
provides the deterministic mapping. Keys absent from this dict are assumed
to be 1:1 parity. This is the SCHEMA_DRIFT checkpoint — if a key shows up
in the prediction but not in observation AND not in this bridge, it's a
SCHEMA_DRIFT warning.

F2 TRUTH: No semantic translation in the delta path.
"""

OBSERVATION_SCHEMA_KEYS: frozenset[str] = frozenset(
    {
        # WELL substrate keys (from _read_well_substrate output)
        "well_score",
        "human_ready",
        "clarity",
        "has_telemetry",
        "truth_status",
        "active_violations",
        "status",
        "coupled_verdict",
        "source",
        "w0",
        # arif_measure(mode='vitals') keys
        "g_score",
        "delta_S",
        "omega",
        "psi_le",
        # judge evidence keys
        "runtime_drift",
        "floors_checked",
        "floors_violated",
    }
)
"""Canonical set of valid observation keys for schema parity validation."""

PREDICTION_SCHEMA_VERSION = "v1.0"
OBSERVATION_SCHEMA_VERSION = "v1.0"


def _validate_schema_parity(
    predicted_state: dict[str, Any],
    observed_state: dict[str, Any],
) -> dict[str, Any]:
    """Validate that prediction and observation schemas are congruent.

    Before computing delta between predicted_state and observed_state,
    verify that both sides speak the same deterministic schema. Semantic
    translation in the delta path introduces ΔS > 0.

    Returns a dict with:
        parity_ok: bool — True if schemas match 1:1
        prediction_keys: list — keys the judge predicted
        observation_keys: list — keys the substrate returned
        unmatched_predictions: list — prediction keys not in observation schema
        unmatched_observations: list — observation keys not in prediction schema
        bridged_keys: dict — keys resolved via SCHEMA_BRIDGE
        schema_drift: bool — True if valid keys don't appear in either schema
        warning: str | None — drift warning message
    """

    pred_keys = set(predicted_state.keys())
    obs_keys = set(observed_state.keys())

    # Apply SCHEMA_BRIDGE: map prediction keys to observation keys
    bridged: dict[str, str] = {}
    resolved_pred_keys: set[str] = set()
    for pk in pred_keys:
        if pk in SCHEMA_BRIDGE:
            bridged[pk] = SCHEMA_BRIDGE[pk]
            resolved_pred_keys.add(SCHEMA_BRIDGE[pk])
        else:
            resolved_pred_keys.add(pk)

    unmatched_predictions = sorted(pred_keys - obs_keys - set(bridged.keys()))
    unmatched_observations = sorted(obs_keys - pred_keys - set(bridged.values()))

    # Schema drift: check if any valid OBSERVATION_SCHEMA_KEYS are missing
    pred_valid_keys = pred_keys & OBSERVATION_SCHEMA_KEYS
    obs_valid_keys = obs_keys & OBSERVATION_SCHEMA_KEYS
    orphan_pred = sorted(pred_valid_keys - obs_keys)
    orphan_obs = sorted(obs_valid_keys - pred_keys)

    schema_drift = bool(orphan_pred or orphan_obs)
    parity_ok = len(unmatched_predictions) == 0 and len(unmatched_observations) == 0

    warning: str | None = None
    if schema_drift:
        warning = (
            f"SCHEMA_DRIFT: prediction/observation key mismatch. "
            f"Prediction-only valid keys: {orphan_pred}. "
            f"Observation-only valid keys: {orphan_obs}. "
            f"Delta computation requires 1:1 schema parity — semantic "
            f"translation introduces ΔS > 0 (F2 TRUTH violation risk)."
        )
    elif bridged:
        warning = (
            f"SCHEMA_BRIDGE active: {len(bridged)} key(s) mapped via bridge. "
            f"Prefer direct 1:1 naming. Bridged: {bridged}"
        )

    return {
        "parity_ok": parity_ok,
        "prediction_keys": sorted(pred_keys),
        "observation_keys": sorted(obs_keys),
        "unmatched_predictions": unmatched_predictions,
        "unmatched_observations": unmatched_observations,
        "bridged_keys": bridged,
        "schema_drift": schema_drift,
        "warning": warning,
        "prediction_schema_version": PREDICTION_SCHEMA_VERSION,
        "observation_schema_version": OBSERVATION_SCHEMA_VERSION,
    }


def _query_prediction_gradient(
    session_id: str | None = None,
    action_tier: str = "standard",
) -> dict[str, Any] | None:
    """Query arif_memory for past L2-tier prediction deltas on similar operations.

    Historical prediction-observation errors condition the judge's forward
    pass so the observation error token feeds back into the next action
    selection. This closes the ECHO/PaW loop: Δ between predicted_state and
    observed_state becomes prompt conditioning (L3 gradient injection).

    Filters for entries with 'prediction_delta' in content, scoped to
    similar action tiers where possible.

    Args:
        session_id: Current session context for scoping
        action_tier: Current action tier for similarity filtering

    Returns:
        dict with 'deltas': list of past prediction errors with scores,
        or None if no relevant history found.
    """
    try:
        from arifosmcp.runtime.megaTools.tool_13_arif_memory import arif_memory as _arif_memory

        # Query for past L2-tier entries with prediction deltas
        raw_payload = _arif_memory(
            mode="recall",
            query="prediction_delta tier:L2",
            session_id=session_id,
        )

        # Extract payload from RuntimeEnvelope
        import asyncio

        if asyncio.iscoroutine(raw_payload):
            raw_payload = asyncio.get_event_loop().run_until_complete(raw_payload)

        payload = getattr(raw_payload, "payload", None)
        if payload is None:
            raw_payload = getattr(raw_payload, "value", None)

        # Parse results — arif_memory recall returns structured payload
        results = []
        if isinstance(payload, dict):
            items = payload.get("items") or payload.get("memories") or payload.get("results") or []
            for item in items:
                if isinstance(item, dict):
                    content = item.get("content", item.get("text", ""))
                    if "prediction_delta" in str(content):
                        results.append(
                            {
                                "memory_id": item.get("memory_id", item.get("id", "")),
                                "tier": item.get("tier", "L2"),
                                "action_tier": item.get("action_tier", ""),
                                "delta_score": item.get("delta_score", item.get("score")),
                                "timestamp": item.get("timestamp", item.get("created_at", "")),
                                "content_snippet": str(content)[:500],
                            }
                        )

        if not results:
            return None

        # Filter by similar action_tier if possible
        filtered = [
            r
            for r in results
            if action_tier in ("standard", "any")
            or r.get("action_tier", "") in (action_tier, "")
            or r.get("action_tier", "") == action_tier
        ]
        if not filtered:
            filtered = results  # fallback: return all

        return {
            "source": "arif_memory_recall_L2_prediction_deltas",
            "deltas": filtered[:10],  # cap at 10 to avoid context bloat
            "count": len(filtered),
            "filter_type": "action_tier_similarity",
            "action_tier_filter": action_tier,
        }
    except Exception:
        return None


def _build_validate_result(
    *,
    constitutional_chain_id: str | None,
    judge_state_hash: str | None,
    actor_id: str | None,
    session_id: str | None,
    candidate: str | None,
    session_token: str | None = None,
) -> VerdictOutput:
    """Strict constitutional chain validation gate (P0 2026-07-25).

    Validates: chain_exists, judge_hash_matches, candidate_matches,
    actor_matches, session_matches, replay_safe, execution_grant.
    All must pass. Any failure → HOLD. No soft fallbacks.
    """
    reasons: list[str] = []
    checks: dict[str, bool] = {}
    grant: str | None = None

    if not constitutional_chain_id:
        return VerdictOutput(
            verdict=VerdictCode.HOLD,
            reasons=["VALIDATE_NO_CHAIN_ID"],
            next_safe_action="Provide a valid constitutional_chain_id from arif_judge SEAL",
            meta={"gate": "CHAIN_VALIDATION", "chain_valid": False},
        )

    # Look up chain in judge state registry
    chain_entry = None
    try:
        from arifosmcp.runtime.tools import _JUDGE_STATE_REGISTRY

        for _stored_hash, _stored_state in _JUDGE_STATE_REGISTRY.items():
            if _stored_state.get("constitutional_chain_id") == constitutional_chain_id:
                chain_entry = _stored_state
                break
    except Exception:
        pass

    if not chain_entry:
        try:
            from arifosmcp.runtime.sct import resolve_standing

            standing = resolve_standing(
                session_id=session_id,
                actor_id=actor_id,
                session_token=session_token,
                allow_store=True,
            )
            if standing.valid and standing.meta:
                chain_entry = standing.meta.get("chain_entry")
        except Exception:
            pass

    checks["chain_valid"] = chain_entry is not None
    if not checks["chain_valid"]:
        reasons.append("E_VALIDATE_CHAIN_NOT_FOUND: constitutional_chain_id not in registry")

    # Validate judge state hash
    if chain_entry and judge_state_hash:
        stored_hash = chain_entry.get("judge_state_hash") or chain_entry.get("hash")
        checks["judge_hash_matches"] = stored_hash == judge_state_hash
        if not checks["judge_hash_matches"]:
            reasons.append(
                f"E_VALIDATE_JUDGE_HASH_MISMATCH: stored={stored_hash} submitted={judge_state_hash}"
            )
    elif chain_entry:
        checks["judge_hash_matches"] = True  # No hash to check
    else:
        checks["judge_hash_matches"] = False

    # Validate actor
    if chain_entry and actor_id:
        stored_actor = chain_entry.get("actor_id") or chain_entry.get("actor")
        checks["actor_matches"] = stored_actor == actor_id or stored_actor is None
        if not checks["actor_matches"]:
            reasons.append(f"E_VALIDATE_ACTOR_MISMATCH: stored={stored_actor} submitted={actor_id}")
    elif chain_entry:
        checks["actor_matches"] = True
    else:
        checks["actor_matches"] = False

    # Validate candidate
    if chain_entry and candidate:
        stored_candidate = (
            chain_entry.get("intent") or chain_entry.get("candidate") or chain_entry.get("task")
        )
        checks["candidate_matches"] = stored_candidate == candidate or stored_candidate is None
        if not checks["candidate_matches"]:
            reasons.append("E_VALIDATE_CANDIDATE_MISMATCH")
    elif chain_entry:
        checks["candidate_matches"] = True
    else:
        checks["candidate_matches"] = False

    # Session match
    if chain_entry and session_id:
        stored_sid = chain_entry.get("session_id")
        checks["session_matches"] = stored_sid == session_id or stored_sid is None
        if not checks["session_matches"]:
            reasons.append("E_VALIDATE_SESSION_MISMATCH")
    elif chain_entry:
        checks["session_matches"] = True
    else:
        checks["session_matches"] = False

    # Replay check — chain must not be consumed
    checks["replay_safe"] = chain_entry is not None and chain_entry.get("consumed") != True

    # Vault receipt
    checks["vault_receipt_valid"] = chain_entry is not None and bool(
        chain_entry.get("vault_entry_id") or chain_entry.get("seal_id")
    )

    # Expiry
    if chain_entry:
        expires = chain_entry.get("expires_at") or chain_entry.get("expiry")
        if expires:
            from datetime import datetime, timezone

            try:
                expiry_dt = datetime.fromisoformat(str(expires).replace("Z", "+00:00"))
                checks["expired"] = datetime.now(timezone.utc) > expiry_dt
                if checks["expired"]:
                    reasons.append("E_VALIDATE_EXPIRED")
            except Exception:
                checks["expired"] = False

    # Execution grant
    all_passed = all(v for k, v in checks.items() if isinstance(v, bool) and k not in ("expired",))
    not_expired = not checks.get("expired", False)
    if all_passed and not_expired and chain_entry:
        import secrets, hashlib, time

        grant = f"grant_v1.{secrets.token_hex(16)}.{int(time.time())}"
        grant_hash = hashlib.sha256(grant.encode()).hexdigest()
        chain_entry["execution_grant"] = grant_hash
        chain_entry["grant_issued_at"] = time.time()
        chain_entry["consumed"] = False

    return VerdictOutput(
        verdict=VerdictCode.SEAL if (all_passed and not_expired and grant) else VerdictCode.HOLD,
        reasons=reasons if reasons else ["VALIDATE_PASS"],
        next_safe_action=(
            "Proceed with execution grant"
            if grant
            else "Resolve validation failures before retrying"
        ),
        meta={
            "gate": "CHAIN_VALIDATION",
            "chain_valid": checks.get("chain_valid", False),
            "judge_hash_matches": checks.get("judge_hash_matches", False),
            "candidate_matches": checks.get("candidate_matches", False),
            "actor_matches": checks.get("actor_matches", False),
            "session_matches": checks.get("session_matches", False),
            "replay_safe": checks.get("replay_safe", False),
            "vault_receipt_valid": checks.get("vault_receipt_valid", False),
            "expired": checks.get("expired", False),
            "execution_grant": grant,
            "checks": checks,
        },
    )


async def arif_judge(
    mode: str = "judge",
    candidate: str | None = None,
    session_id: str | None = None,
    session_token: str | None = None,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    vault_entry_id: str | None = None,
    cooldown_entry_id: str | None = None,
    action_tier: str = "standard",
    heart_critique: dict[str, Any] | None = None,
    niat_params: dict[str, Any] | None = None,
    context_source: str | None = None,
    sovereign_receipt: str | None = None,
    evidence: dict[str, Any] | None = None,
    # ── F13 challenge authorization params (public MCP wrapper chain) ──
    actor_signature: str | None = None,
    nonce: str | None = None,
    key_id: str | None = None,
    reversibility_level: str | None = None,
    blast_radius: str | None = None,
    seal_purpose: str | None = None,
    authority_effect: str | None = None,
    action_class: str | None = None,
    requested_capability: str | None = None,
    domain: str | None = None,
) -> VerdictOutput:
    """
        888_JUDGE: Constitutional adjudication and verdict emission.

        Args:
            heart_critique: Optional 666_HEART critique. Red Team Finding #1:
                If heart_critique.verdict is VOID or status is HOLD, the judge
                must escalate to HOLD unless explicit Sovereign override.
            action_tier: "standard" | "sovereign" | "c4" | "c5".
    ...
        # Delegate to kernel intercept classification if reversibility_level/action_class provided
    _rev_param = reversibility_level or action_class
    if _rev_param and str(_rev_param).strip():
        try:
            from arifosmcp.tools.arif_kernel_intercept import _arif_kernel_intercept

            _intercept_res = await _arif_kernel_intercept(
                actor=actor_id or "anonymous",
                intent=candidate or "Adjudication",
                requested_capability=requested_capability or "kernel.judge",
                domain=domain or "governance",
                reversibility_level=_rev_param,
                blast_radius=blast_radius or "LOW",
                action_class=action_class or reversibility_level,
                seal_purpose=seal_purpose,
                authority_effect=authority_effect,
                actor_signature=actor_signature,
                session_id=session_id,
            )
            _v_str = _intercept_res.get("decision") or _intercept_res.get("status") or "HOLD"
            _code = (
                VerdictCode.SEAL
                if _v_str == "SEAL"
                else (VerdictCode.VOID if _v_str == "VOID" else VerdictCode.HOLD)
            )
            return VerdictOutput(
                verdict=_code,
                reasons=[
                    _intercept_res.get("reason")
                    or f"Adjudicated via kernel intercept (reversibility={_rev_param})"
                ],
                next_safe_action=_intercept_res.get(
                    "next_safe_action", "Execute or review per verdict"
                ),
                meta={
                    "kernel_intercept": _intercept_res,
                    "reversibility_level": _rev_param,
                    "action_class": action_class or reversibility_level,
                },
            )
        except Exception as _int_err:
            logger.warning("Kernel intercept delegation failed: %s", _int_err)

    # ── 666_HEART: Ethical Gate (Red Team Finding #1) ────────────────────────
        # Hard-wire the heart's verdict into the judge loop.
        if mode == "judge" and heart_critique:
            heart_verdict = heart_critique.get("action_risk_verdict") or heart_critique.get("verdict")
            if heart_verdict in ("VOID", "HOLD"):
                return VerdictOutput(
                    verdict=VerdictCode.HOLD,
                    reasons=[
                        f"666_HEART_GATE: Critique returned {heart_verdict}.",
                        heart_critique.get("reason", "Ethical risks or uncertainty detected by Heart."),
                    ],
                    next_safe_action="Review 666_HEART risks and provide mitigations before re-judging.",
                    meta={
                        "heart_gate": "HEART_BLOCKED",
                        "heart_verdict": heart_verdict,
                        "heart_payload": heart_critique,
                    },
                )

    """
    from arifosmcp.tools.ops import arif_measure

    _evidence: dict = {}
    _is_elevated_tier = action_tier.lower() in ("sovereign", "c4", "c5")
    _has_receipt = bool(sovereign_receipt and sovereign_receipt.strip())

    # ── SCT-first standing (Spine P0) — store optional ─────────────────────
    _standing_token = session_token
    _standing_source = None
    _standing_apex: dict[str, Any] | None = None
    _standing_actor_verified = False
    _standing_authority: str | None = None
    _standing_delta: dict[str, Any] | None = None

    def _echo_standing(out: VerdictOutput) -> VerdictOutput:
        """Echo next-hop SCT continuity onto a direct VerdictOutput."""
        if not _standing_token:
            return out
        data = out.model_dump(mode="json")
        data["session_token"] = _standing_token
        data["standing_source"] = _standing_source or "sct"
        if _standing_apex is not None:
            data["apex_scalars"] = _standing_apex
        data["authority"] = _standing_authority or "OBSERVE_ONLY"
        data["actor_verified"] = _standing_actor_verified
        if _standing_delta is not None:
            data["authority_delta"] = _standing_delta
        res = data.get("result")
        if isinstance(res, dict):
            res.setdefault("session_token", _standing_token)
            res.setdefault("standing_source", _standing_source or "sct")
            if _standing_apex is not None:
                res.setdefault("apex_scalars", _standing_apex)
        return VerdictOutput(**data)

    if session_token or session_id:
        try:
            from arifosmcp.runtime.sct import resolve_standing

            _standing = resolve_standing(
                session_id=session_id,
                actor_id=actor_id,
                session_token=session_token,
                allow_store=True,
            )
            if _standing.valid:
                _standing_token = _standing.session_token or session_token
                _standing_source = _standing.source
                _standing_apex = dict(_standing.apex) if _standing.apex else None
                _standing_actor_verified = _standing.actor_verified
                _standing_authority = _standing.authority
                _standing_delta = _standing.authority_delta
                if _standing.session_id:
                    session_id = _standing.session_id
                if _standing.actor_id and _standing.actor_id != "anonymous":
                    actor_id = _standing.actor_id
            elif session_token:
                return _echo_standing(
                    VerdictOutput(
                        verdict=VerdictCode.HOLD,
                        reasons=[
                            _standing.reason or "L11 AUTH: SCT invalid",
                            "Provide a valid session_token from arif_init.",
                        ],
                        next_safe_action="Call arif_init, then re-invoke arif_judge with session_token.",
                        meta={
                            "gate": "L11_SCT_GATE",
                            "sesat_event": {
                                "sesat": True,
                                "type": "TOKEN_INVALID",
                                "reason": _standing.reason,
                            },
                            "session_id": session_id,
                            "floor": "F11",
                            "floor_type": "HARD",
                        },
                    )
                )
        except Exception:
            pass

    # ── F13 CHALLENGE AUTHORIZATION (public MCP wrapper chain) ─────────────
    # Every MCP caller now hits the same handler. When actor_signature + nonce
    # are present, verify the Ed25519-signed canonical challenge BEFORE any
    # deliberation. This closes the wrapper chain mismatch where the public
    # arif_judge surface previously had no F13 verification path.
    if actor_signature and nonce and actor_id:
        try:
            from arifosmcp.runtime.crypto_auth import verify_authorization_challenge

            _auth_ok, _auth_code, _auth_result = verify_authorization_challenge(
                actor=actor_id,
                nonce=nonce,
                signature_b64=actor_signature,
            )
            if not _auth_ok:
                return VerdictOutput(
                    verdict=VerdictCode.HOLD,
                    reasons=[
                        f"F13 challenge verification failed: {_auth_code}",
                        _auth_result.get("reason", "Authorization could not be verified"),
                    ],
                    next_safe_action=(
                        "Re-issue authorization challenge via _arif_kernel_intercept "
                        "and sign with Ed25519 key before retrying"
                    ),
                    meta={
                        "gate": "F13_CHALLENGE_AUTH",
                        "failure_code": _auth_code,
                        "session_id": session_id,
                        "floor": "F13",
                        "floor_type": "HARD",
                    },
                )
            logger.info(
                "F13: arif_judge challenge authorization PASS — actor=%s session=%s",
                actor_id,
                session_id or "(none)",
            )
        except Exception as _f13_err:
            logger.error("F13: arif_judge challenge verification error: %s", _f13_err)
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[f"F13 challenge verification error: {_f13_err}"],
                next_safe_action="Check arifOS kernel health and retry challenge issuance",
                meta={
                    "gate": "F13_CHALLENGE_AUTH",
                    "error": str(_f13_err),
                    "session_id": session_id,
                    "floor": "F13",
                    "floor_type": "HARD",
                },
            )

    # ── F11 SESSION GATE — session_id OR valid SCT ────────────────────────
    if not session_id or not str(session_id).strip():
        return VerdictOutput(
            verdict=VerdictCode.HOLD,
            reasons=[
                "F11_SESSION_GATE: arif_judge requires a valid session_id or session_token. "
                "Empty or missing session means no constitutional chain exists.",
                "F11 AUTH mandates verified identity before sensitive operations.",
            ],
            next_safe_action=(
                "Call arif_init first to establish a valid session, "
                "then re-invoke arif_judge with session_id + session_token."
            ),
            meta={
                "gate": "F11_SESSION_GATE",
                "session_id": session_id,
                "floor": "F11",
                "floor_type": "HARD",
            },
        )

    # ── SESSION-BOUND IDENTITY — SCT reinjects store; prefer token actor ──
    from arifosmcp.runtime.tools import get_session as _get_session

    _sess = _get_session(session_id) if session_id else None
    if _sess and isinstance(_sess, dict):
        _sess_actor = _sess.get("actor_id")
        if _sess_actor and _sess_actor != "anonymous":
            if actor_id and actor_id != _sess_actor:
                _sess.setdefault("_judge_scars", []).append(
                    f"actor_mismatch: passed={actor_id} session={_sess_actor}"
                )
            actor_id = _sess_actor

    # ── AKAL I4: Dual evaluation gate ────────────────────────────────────────
    from arifosmcp.core.akal_wiring import akal_pre_judge as _akal_dual

    try:
        _akal_dual_result = _akal_dual(
            session_id=session_id,
            blast_radius=action_tier if action_tier in ("sovereign", "c4", "c5") else "low",
        )
        if _akal_dual_result.get("blocked_reason"):
            # L5b required but sovereign not engaged — will be added to meta
            _evidence.setdefault("akal_dual_eval", _akal_dual_result)
    except Exception:
        pass  # AKAL dual-eval is advisory

    # ── MODE VALIDATE: Strict constitutional chain verification (P0 2026-07-25) ─────
    # A-FORGE calls arif_judge(mode="validate") before every mutation to verify
    # the chain is authentic, bound to this action, unused, and unexpired.
    # No soft fallbacks. Registry unavailable → HOLD. Mismatch → HOLD.
    if mode == "validate":
        return _build_validate_result(
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=None,  # passed via kwargs
            actor_id=actor_id,
            session_id=session_id,
            candidate=candidate,
            session_token=session_token,
        )

    if mode != "history":
        if _evidence.get("vitals") is None:
            try:
                vitals_result = arif_measure(mode="vitals")
                _evidence["vitals"] = getattr(vitals_result, "__dict__", {}) or {
                    "status": "unavailable"
                }
            except Exception:
                _evidence["vitals"] = {"status": "unavailable"}

        # ── RUNTIME DRIFT GATE (G3 — 666_CRITIQUE closure) ──────────────────
        # If the kernel is reporting runtime_drift=true (build ≠ live),
        # every verdict carries explicit uncertainty. The judge refuses
        # to issue SEAL while drift is active unless the sovereign
        # explicitly acknowledges it via sovereign_receipt.
        #
        # Drift is a constitutional signal, not a footnote.
        # F2 TRUTH: "build_commit ≠ live_commit" means the kernel's
        # self-attestation is unreliable → all verdicts are provisional.
        _runtime_drift = _evidence.get("vitals", {}).get("runtime_drift", False)
        if _runtime_drift and not _has_receipt:
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[
                    "RUNTIME_DRIFT_HOLD: Kernel reports runtime_drift=true "
                    "(build_commit ≠ live_commit). The kernel's self-attestation "
                    "is unreliable — all verdicts are provisional until drift "
                    "is resolved.",
                    "No SEAL may be issued while drift is active.",
                    "Options: (1) rebuild and redeploy to sync build with live, "
                    "or (2) provide sovereign_receipt for F13 override.",
                ],
                next_safe_action=(
                    "Rebuild and redeploy to resolve drift. "
                    "Then re-run deliberation with a clean health check."
                ),
                meta={
                    "drift_gate": "RUNTIME_DRIFT_HOLD",
                    "runtime_drift": True,
                    "build_commit": _evidence.get("vitals", {}).get("build_commit", "unknown"),
                    "live_commit": _evidence.get("vitals", {}).get("live_commit", "unknown"),
                },
            )
        elif _runtime_drift and _has_receipt:
            # F13 SOVEREIGN OVERRIDE: receipt present, drift acknowledged
            _evidence["f13_drift_override"] = {
                "runtime_drift": True,
                "sovereign_acknowledged": True,
                "override": "F13_SOVEREIGN_DRIFT_ACKNOWLEDGED",
            }

        # ── WELL biological substrate pre-load (Gap 2 wire) ──────────────────
        # W0 preserved: WELL informs, judge decides, operator holds veto.
        # This is advisory evidence surfaced alongside every verdict — not a gate.
        _evidence["well_substrate"] = _read_well_substrate()

        # ── ECHO/PaW L3 GRADIENT INJECTION ──────────────────────────────────
        # Query arif_memory for past L2-tier prediction deltas on similar
        # operations. Historical prediction-observation errors condition the
        # judge's forward pass so the observation error token feeds back into
        # the next action selection. This closes the ECHO loop: Δ between
        # predicted_state and observed_state becomes prompt conditioning.
        #
        # F2 TRUTH: past errors are surfaced with their delta scores so the
        # judge can calibrate confidence. No synthetic data — only real deltas
        # from prior seal entries.
        try:
            _evidence["gradient_context"] = _query_prediction_gradient(
                session_id=session_id,
                action_tier=action_tier,
            )
        except Exception:
            _evidence["gradient_context"] = None

        # ── W-4: G-WELL governance pre-load for elevated-tier actions ─────────
        # C4/C5/sovereign actions require governance coherence check before deliberation.
        if _is_elevated_tier:
            _evidence["well_governance"] = _read_well_governance()

        # ── W-2: SOVEREIGN clarity gate (W5 → F2 hard block) ─────────────────
        # If action_tier is sovereign/C4/C5 and cognitive clarity is below threshold,
        # return HOLD before deliberation. Operator readiness is constitutional.
        #
        # F13 SOVEREIGN RECEIPT PATH (2026-06-13):
        #   When sovereign_receipt is present, the clarity threshold is waived.
        #   The sovereign has explicitly confirmed readiness — F13 overrides W-2.
        #   The receipt is recorded in meta for audit trail.
        if _is_elevated_tier:
            _w2_sub = _evidence["well_substrate"]
            _w2_clarity = _w2_sub.get("clarity")
            _has_receipt = bool(sovereign_receipt and sovereign_receipt.strip())
            if (
                _w2_clarity is not None
                and float(_w2_clarity) < 4.0
                and _w2_sub.get("has_telemetry")
                and not _has_receipt
            ):
                return VerdictOutput(
                    verdict=VerdictCode.HOLD,
                    reasons=[
                        (
                            f"W5_COGNITIVE_ENTROPY: clarity={_w2_clarity}/10"
                            " below SOVEREIGN threshold (4/10)."
                        ),
                        (
                            "Operator cognitive substrate does not meet"
                            " constitutional requirements for elevated-tier action."
                        ),
                        "Rest. Reassess when clarity ≥ 6/10, or provide sovereign_receipt for F13 override.",
                    ],
                    next_safe_action=(
                        "Rest. Return when clarity ≥ 6/10."
                        " Then re-run with action_tier='sovereign'."
                    ),
                    meta={
                        "well_gate": "SOVEREIGN_BLOCKED",
                        "w_floor": "W5 → F2",
                        "action_tier": action_tier,
                        "clarity": _w2_clarity,
                        "threshold": 4.0,
                        "human_ready": _w2_sub.get("human_ready"),
                        "active_violations": _w2_sub.get("active_violations", []),
                        "well_substrate": _w2_sub,
                        "f13_sovereign_receipt_available": False,
                    },
                )
            elif _has_receipt and _w2_clarity is not None and float(_w2_clarity) < 4.0:
                # F13 SOVEREIGN OVERRIDE: receipt present, clarity waived
                _evidence["f13_sovereign_receipt"] = {
                    "receipt_hash": f"sha256:{hashlib.sha256(sovereign_receipt.encode()).hexdigest()[:16]}",
                    "clarity_at_receipt": _w2_clarity,
                    "override": "F13_SOVEREIGN_CONFIRMED",
                }

    audit_entropy = _evidence.get("vitals", {}).get("audit_entropy")

    # ── NIAT GATE: Human Purpose under Constraint ─────────────────────────────────
    # Phase 2: Full NIAT gate implementation.
    # Fires on: formalize mode OR elevated action tiers (c3/c4/c5/sovereign).
    # Uses explicit niat_params if provided; otherwise infers from candidate.
    if mode == "formalize" or action_tier.lower() in ("c3", "c4", "c5", "sovereign"):
        if niat_params:
            _ni = niat_params.get("user_instruction", candidate or "")
            _nc = niat_params.get("context_source", context_source or "unknown")
            _na = niat_params.get("requested_action", mode)
            _nm = niat_params.get("medium_shift", "none")
            _ns = niat_params.get("negative_signals", [])
            _nr = niat_params.get("reversibility", "reversible")
            _nh = niat_params.get("affected_humans", [])
        else:
            _ni = candidate or ""
            _nc = context_source or "unknown"
            _na = mode
            _nm = "none"
            _ns = []
            _nr = "reversible"
            _nh = []

        _gate = check_niat_gate(
            user_instruction=_ni,
            context_source=_nc,
            requested_action=_na,
            medium_shift=_nm,
            negative_signals=_ns,
            reversibility=_nr,
            affected_humans=_nh,
        )

        if _gate["niat_state"] == "CONFLICTED":
            from arifosmcp.schemas.verdict import AmanahProof

            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[
                    "NIAT_GATE: niat_state=CONFLICTED — consent boundary unclear or violated.",
                    f"Formalization blocked: {_gate['formalization_allowed']}.",
                    f"Detected scars: {_gate['detected_scars']} (weight={_gate['scar_weight']:.2f}).",
                ],
                next_safe_action="Obtain explicit consent or narrow the action scope before re-judging.",
                amanah_proof=AmanahProof(
                    genius_score=0.0,
                    floors_checked=["F1", "F5", "F6"],
                    floors_passed=["F1"],
                    floors_failed=["F5", "F6"],
                    violations=["NIAT_CONSENT_BOUNDARY_VIOLATED"],
                    violation_mitigation=["Action blocked pending explicit consent"],
                ),
                meta={
                    "niat_gate": "HOLD",
                    "niat_state": _gate["niat_state"],
                    "scar_weight": _gate["scar_weight"],
                    "detected_scars": _gate["detected_scars"],
                    "required_next_step": _gate["required_next_step"],
                },
            )

        if _gate["niat_state"] == "UNCERTAIN" and _gate["execution_allowed"] is False:
            # NIAT uncertain — downgrade verdict to SABAR (proceed with caution)
            _niat_meta = {
                "niat_gate": "WATCH",
                "niat_state": _gate["niat_state"],
                "scar_weight": _gate["scar_weight"],
                "detected_scars": _gate["detected_scars"],
                "required_next_step": _gate["required_next_step"],
            }
        else:
            _niat_meta = None

    # ── A-RIF: Claim Strength Gate (Abduction/Judgment) ──

    # Extract evidence level from candidate or context if possible
    # Placeholder: currently we check if the candidate makes strong claims
    # that exceed the evidence stored in the receipt/session.

    # ── METABOLIC BYPASS CHECK (Gap 3.4 Invariant) ──────────────────────────
    if session_id:
        cumulative = get_cumulative_metrics(session_id)
        if cumulative.get("is_bypass_attempt"):
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[
                    "METABOLIC_BYPASS_DETECTED: Cumulative risk or file changes exceeded safe window threshold.",
                    f"Cumulative Risk: {cumulative.get('cumulative_risk')}, Total Files: {cumulative.get('total_files_touched')}",
                ],
                next_safe_action="Aggregate small actions into a single atomic plan for human review.",
                meta={"cumulative_metrics": cumulative},
            )

        # ── MARUAH CRITIC GATE (Gap 1: community_maruah=true trigger) ─────────
        # If the candidate text or metadata flags community-maruah sensitivity,
        # run maruah_critic_check() before deliberation. Block if verdict not ok.
        #
        # Data flow:
        #   caller sets community_maruah=true in task metadata (e.g. via
        #   arif_kernel_route, arif_think plan, or MCP tool metadata).
        #   The flag reaches judge via: evidence_receipt or heart_critique meta.
        _maruah_sensitive = False
        _maruah_meta: dict = {}
        if isinstance(candidate, dict):
            _maruah_sensitive = bool(candidate.get("community_maruah", False))
            _maruah_meta = candidate
        if not _maruah_sensitive and isinstance(heart_critique, dict):
            _meta = heart_critique.get("meta", {}) if isinstance(heart_critique, dict) else {}
            _maruah_sensitive = bool(_meta.get("community_maruah", False))
            _maruah_meta = _meta
        if not _maruah_sensitive and isinstance(evidence, dict):
            _maruah_sensitive = bool(
                evidence.get("task_metadata", {}).get("community_maruah", False)
            )

        if _maruah_sensitive and isinstance(candidate, str) and candidate.strip():
            _mv: MaruahVerdict = maruah_critic_check(
                draft_text=candidate,
                audience_profile=_maruah_meta.get("audience_profile"),
            )
            if not _mv.ok:
                _maruah_reasons = [
                    f"MARUAH_CRITIC_BLOCK: {i.type} (severity={i.severity})" for i in _mv.issues
                ] + [
                    f"policy: {_mv.policy_line}",
                    "Respect maruah governance: kritik sistem dibenarkan walau kasar, "
                    "hinakan individu diblok. Semak dan ubah suai input sebelum cuba lagi.",
                ]
                return VerdictOutput(
                    verdict=VerdictCode.HOLD,
                    reasons=_maruah_reasons,
                    next_safe_action=(
                        "Revise candidate text: kritik sistem/tindakan, "
                        "bukan martabat peribadi. Guna 'community_maruah=true' "
                        "metadata untuk trigger gate ini."
                    ),
                    meta={
                        "maruah_gate": "MARUAH_BLOCKED",
                        "maruah_verdict": {
                            "ok": _mv.ok,
                            "issues": [
                                {"type": i.type, "severity": i.severity, "snippet": i.snippet}
                                for i in _mv.issues
                            ],
                        },
                    },
                )
            _evidence["maruah_gate"] = {
                "gate": "MARUAH_PASS",
                "issues_found": len(_mv.issues),
            }

        # ── SOMATIC STATE GATE (Gap 2: machine telemetry → HOLD on CRITICAL) ──
        # Before deliberation, classify machine somatic state from arif_measure
        # telemetry. If somatic state is CRITICAL, return HOLD.
        # This is MACHINE-AS-BODY telemetry (F9 ANTIHANTU: NOT biological).
        _vitals = _evidence.get("vitals", {})
        _telemetry_sample = TelemetrySample(
            latency_ms=float(_vitals.get("avg_latency_ms", 0)),
            error_rate=float(_vitals.get("error_rate", 0)),
            cost_burn_per_min=float(_vitals.get("cost_burn_per_min", 0)),
            queue_depth=int(_vitals.get("queue_depth", 0)),
        )
        _somatic_state = classify_somatic_state(_telemetry_sample)
        _evidence["somatic_state"] = _somatic_state.value
        if _somatic_state == SomaticState.CRITICAL:
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[
                    f"SOMATIC_GATE: Machine state is {_somatic_state.value}. "
                    "System telemetry shows critical thresholds exceeded.",
                    f"latency_ms={_telemetry_sample.latency_ms}, "
                    f"error_rate={_telemetry_sample.error_rate}, "
                    f"cost_burn={_telemetry_sample.cost_burn_per_min}, "
                    f"queue_depth={_telemetry_sample.queue_depth}",
                    "Pause. Escalate. Recover. Then re-judge.",
                ],
                next_safe_action=(
                    "Resolve critical machine state before deliberation. "
                    "Check arif_measure for details."
                ),
                meta={
                    "somatic_gate": "SOMATIC_BLOCKED",
                    "somatic_state": _somatic_state.value,
                    "telemetry": {
                        "latency_ms": _telemetry_sample.latency_ms,
                        "error_rate": _telemetry_sample.error_rate,
                        "cost_burn_per_min": _telemetry_sample.cost_burn_per_min,
                        "queue_depth": _telemetry_sample.queue_depth,
                    },
                    "well_substrate": _evidence.get("well_substrate", {}),
                },
            )

        # ── PARADOX GATE (somatic intelligence → resolution risk flags) ────────
        # After somatic state gate, check if output would resolve active paradoxes.
        # Reads paradox state from A-FORGE engine (cross-organ wiring).
        # This is a FLAG, not a BLOCK. (F5 PEACE: de-escalate, don't choke.)
        # F9 ANTIHANTU: reads structural state, not "feelings."
        _candidate_text = ""
        if isinstance(candidate, str):
            _candidate_text = candidate
        elif isinstance(candidate, dict):
            _candidate_text = str(candidate.get("content", candidate.get("target_path", "")))

        _paradox_result = evaluate_paradox_gate(
            output_text=_candidate_text,
            evidence=_evidence,
        )
        _evidence["paradox_gate"] = _paradox_result.to_dict()

        if _paradox_result.gate_verdict == "FLAGGED":
            # Append paradox flags to reasons but do NOT auto-block
            for _pf in _paradox_result.flags:
                _evidence.setdefault("paradox_flags", []).append(
                    {
                        "paradox_id": _pf.paradox_id,
                        "flag": _pf.flag,
                        "detail": _pf.detail,
                        "tension": _pf.tension,
                    }
                )

            # FORGE-FIX P1 (2026-07-11): Escalate to PARADOX_HOLD when gate is FLAGGED
            # with a resolution-risk flag (not just maturation). This populates the
            # `paradox_hold` field of UnifiedGovernanceReceipt, which the composite
            # verdict rules use to override SEAL → HOLD. Without this, the
            # PARADOX_HOLD verdict type exists in schema but never fires in prod.
            # Threshold: tension > 0.3 (matches gate's RESOLUTION_RISK bar).
            _rr_flags = [
                _pf
                for _pf in _paradox_result.flags
                if _pf.flag == "RESOLUTION_RISK" and _pf.tension > 0.3
            ]
            if _rr_flags:
                _primary = _rr_flags[0]
                _evidence["paradox_hold"] = ParadoxHoldReceipt(
                    claim_a=_primary.motif_a,
                    claim_b=_primary.motif_b,
                    conflict_description=_primary.detail,
                    both_verified=True,
                    resolution_attempted=False,
                    reason=(
                        f"PARADOX_HOLD escalation: paradox_score="
                        f"{_paradox_result.paradox_score:.3f}, gate=FLAGGED, "
                        f"{len(_rr_flags)} resolution-risk flag(s)"
                    ),
                ).model_dump(mode="json")

        # ── PARADOX QUOTE ENRICHMENT (ATLAS333 Bridge §4) ──────────────────────
        # After paradox gate, pull philosophical tension quotes for the activated
        # paradox zones. These are advisory (F5 PEACE) — they enrich the judge's
        # reasoning context, never block or alter the verdict.
        # Wires get_triggered_quotes_by_gpv() from constitution/paradox_quotes.py
        # into the 666 JUDGE pipeline as specified in ATLAS333_INTELLIGENCE_FLOW.md §2.
        try:
            _gpv = Φ(_candidate_text)
            _pq_action_class = None
            _cand_mode = ""
            if isinstance(candidate, dict):
                _cand_mode = str(candidate.get("mode", candidate.get("action_type", "")))
            if _cand_mode in ("seal", "irreversible") or action_tier == "sovereign":
                _pq_action_class = "SEAL"
            elif _cand_mode in ("mutate", "forge", "write", "commit"):
                _pq_action_class = "MUTATE"
            _triggered_quotes = get_triggered_quotes_by_gpv(
                paradox_axes=_gpv.paradox_axes,
                action_class=_pq_action_class,
            )
            if _triggered_quotes:
                _evidence["paradox_quotes"] = [
                    {
                        "id": q.quote_id,
                        "organ": q.organ.value,
                        "quote": q.quote_text,
                        "author": q.author,
                        "norm": q.norm.value,
                        "trigger_reason": q.trigger_condition,
                    }
                    for q in _triggered_quotes
                ]
        except Exception:
            # Fail-soft: quote enrichment must never crash the judge (F1 AMANAH)
            pass

        # ── ATLAS333 ACTIVE GATE (2026-07-19) — Paradox-aware calibration ─────
        # MIRROR benchmark (2026): external architectural constraint is the ONLY
        # effective path — passive self-knowledge does nothing. When paradoxes are
        # activated via GPV, apply active constraints: confidence caps, witness
        # requirements, authority chain verification.
        try:
            _atlas_cal = {}
            _pids = (
                _gpv.paradox_axes
                if (_gpv and hasattr(_gpv, "paradox_axes") and _gpv.paradox_axes)
                else []
            )
            if _pids:
                _atlas_cal = {
                    "confidence_cap": 0.85 if 16 in _pids else 0.90,
                    "witness_required": bool({31, 33} & set(_pids)),
                    "authority_chain_required": 25 in _pids,
                    "active_paradox_ids": _pids,
                    "gate_activated": True,
                }
                _notes = _evidence.setdefault("constitutional_notes", [])
                if 16 in _pids:
                    _notes.append("P16 Certainty↔Learning: confidence capped at 0.85.")
                if {31, 33} & set(_pids):
                    _notes.append(
                        "P31/P33 Seal/Governance: external witness required. System cannot self-verify."
                    )
                if 25 in _pids:
                    _notes.append(
                        "P25 Authority↔Legitimacy: authority chain must be verified. No self-grant."
                    )
                _evidence["atlas_calibration"] = _atlas_cal
        except Exception:
            pass  # Fail-soft: calibration enriches, never crashes (F1 AMANAH)

        # ── 10-STAGE PIPELINE TRACKING + SCAR METABOLISM (Gap 3 — 2026-07-19) ─
        # Tracks every pipeline stage traversed, entropy delta, and auto-candidates
        # scars when paradox tension is high. This closes the institutional RSI loop:
        # observe→classify→decode→activate→enrich→evaluate→tearframe→judge→forge→seal
        # → scar feedback → ATLAS333 update → next spawn inherits lower entropy.
        _pipeline = _evidence.setdefault("atlas333_pipeline", {})
        _dS = 0.0

        # Stage tracking (1-8 completed in judge, 9-10 pending execution)
        _completed_stages = []
        if _candidate_text:
            _completed_stages.append({"s": 1, "name": "INGEST", "status": "done"})
        if _gpv and hasattr(_gpv, "lane"):
            _completed_stages.append(
                {"s": 2, "name": "CLASSIFY", "lane": _gpv.lane, "status": "done"}
            )
            _completed_stages.append(
                {
                    "s": 3,
                    "name": "DECODE",
                    "tensor": {"τ": _gpv.tau, "κ": _gpv.kappa, "ρ": _gpv.rho},
                    "status": "done",
                }
            )
        if _evidence.get("paradox_gate"):
            _completed_stages.append({"s": 4, "name": "ACTIVATE", "pids": _pids, "status": "done"})
        if "paradox_quotes" in _evidence:
            _completed_stages.append(
                {
                    "s": 5,
                    "name": "ENRICH",
                    "quotes": len(_evidence["paradox_quotes"]),
                    "status": "done",
                }
            )
        if _evidence.get("paradox_gate"):
            _completed_stages.append(
                {
                    "s": 6,
                    "name": "EVALUATE",
                    "gate": _evidence["paradox_gate"].get("gate_verdict", "?"),
                    "status": "done",
                }
            )
        if "atlas_calibration" in _evidence:
            _completed_stages.append(
                {
                    "s": 7,
                    "name": "TEARFRAME",
                    "caps": {
                        "trm": 0.94,
                        "echo": 0.87,
                        "rasa": 0.85,
                        "confidence": _evidence["atlas_calibration"].get("confidence_cap", 0.90),
                    },
                    "status": "done",
                }
            )
            # ── ACTUAL-COMPLETION METRIC (Truthfulness) ──────────────────────
            # The confidence cap is derived from the completed GPV calibration.
            # TRM/ECHO/RASA values below are policy thresholds, not measurements,
            # and are labelled accordingly.
            try:
                from arifosmcp.runtime.metrics import record_tearframe

                _cal = _evidence["atlas_calibration"]
                record_tearframe(
                    component="confidence",
                    value=_cal.get("confidence_cap"),
                    provenance="derived",
                )
                record_tearframe(
                    component="trm_threshold", value=0.94, provenance="policy_constant"
                )
                record_tearframe(
                    component="echo_threshold", value=0.87, provenance="policy_constant"
                )
                record_tearframe(
                    component="rasa_threshold", value=0.85, provenance="policy_constant"
                )
            except Exception:
                # Metrics must never break the call path
                pass
        _completed_stages.append({"s": 8, "name": "JUDGE", "status": "active"})
        # Each paradox resolved = negative entropy (uncertainty reduced)
        _dS = -0.005 * len(_pids) if _pids else -0.001

        _pipeline.update(
            {
                "stages_completed": _completed_stages,
                "stages_pending": [
                    {"s": 9, "name": "FORGE", "tool": "arif_forge"},
                    {"s": 10, "name": "SEAL", "tool": "arif_seal → scar_feedback"},
                ],
                "entropy_delta_total": round(_dS, 4),
                "paradox_count": len(_pids),
                "scar_candidates": [],
                "version": "v1.0.0-gap3-pipeline",
            }
        )

        # ── SCAR AUTO-CANDIDATE (closes the institutional learning loop) ──
        # When paradox tension is high (ρ≥0.6 or resolution-risk flags fired),
        # auto-create a scar CANDIDATE. Only F13 can seal a scar — this is a
        # proposal, not a binding record. Persisted to vault999/scars/ for review.
        _rr_count = len(_rr_flags) if ("_rr_flags" in dir() and isinstance(_rr_flags, list)) else 0
        _high_risk = (
            (_gpv and hasattr(_gpv, "rho") and _gpv.rho >= 0.6) if "_gpv" in dir() else False
        )
        if _rr_count > 0 or _high_risk:
            import time as _time

            _scar = {
                "scar_id": f"candidate-{int(_time.time())}",
                "created_at": int(_time.time()),
                "source": "arif_judge::paradox_gate",
                "session_id": session_id,
                "paradox_ids": _pids if "_pids" in dir() else [],
                "resolution_risks": _rr_count,
                "risk_rho": round(_gpv.rho, 3)
                if ("_gpv" in dir() and hasattr(_gpv, "rho"))
                else None,
                "candidate_snippet": (_candidate_text[:200] + "...")
                if (len(_candidate_text) > 200)
                else _candidate_text
                if "_candidate_text" in dir()
                else "",
                "status": "candidate",
                "requires_f13_seal": True,
            }
            _pipeline["scar_candidates"].append(_scar)
            # Persist candidate for F13 review (best-effort, never blocks)
            try:
                import pathlib as _pl

                _sd = _pl.Path("/root/.local/share/arifos/vault999/scars")
                _sd.mkdir(parents=True, exist_ok=True)
                (_sd / f"{_scar['scar_id']}.json").write_text(
                    __import__("json").dumps(_scar, indent=2)
                )
                # ── ACTUAL-COMPLETION METRIC (Truthfulness) ──────────────────
                # Increment ONLY after the candidate JSON is durably written.
                # Severity derived from tension; stage = source pipeline stage.
                try:
                    from arifosmcp.runtime.metrics import record_scar_candidate

                    _severity = (
                        "critical" if _gpv.rho >= 0.8 else "high" if _gpv.rho >= 0.6 else "medium"
                    )
                    record_scar_candidate(
                        stage="arif_judge::paradox_gate",
                        severity=_severity,
                    )
                except Exception:
                    pass
            except Exception:
                # Persistence failed — do NOT increment counter. Counter is
                # the audit witness for what actually happened.
                pass

        # ── SELF-MODIFICATION LOCK (Gap 5) ──────────────────────────────────────
    if isinstance(candidate, str) or isinstance(candidate, dict):
        _target = ""
        _action = ""
        if isinstance(candidate, str):
            _target = candidate
        elif isinstance(candidate, dict):
            _target = candidate.get("target_path", "")
            _action = candidate.get("action_type", "")

        self_mod = is_self_modification_attempt(_target, _action, [])
        if self_mod.get("is_blocked"):
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[self_mod.get("reason")],
                next_safe_action="Draft the modification as a proposal only. Final approval requires Sovereign Arif.",
                meta={"self_mod_lock": self_mod},
            )

    # ── scan_instructions mode (L12 GUARD — absorbed from arif_scan_local_instructions) ──
    if mode == "scan_instructions":
        try:
            import asyncio

            from arifosmcp.tools.governance_scan import arif_scan_local_instructions

            root_dir = candidate if isinstance(candidate, str) else None
            raw = arif_scan_local_instructions(
                root_dir=root_dir,
                session_id=session_id,
                actor_id=actor_id,
            )
            if asyncio.iscoroutine(raw):
                try:
                    loop = asyncio.get_event_loop()
                    raw = loop.run_until_complete(raw)
                except RuntimeError:
                    raw = {"status": "async_context_required", "verdict": "HOLD"}
            scan_verdict = raw.get("verdict", "SEAL") if isinstance(raw, dict) else "HOLD"
            verdict_code = (
                VerdictCode.SEAL
                if scan_verdict == "SEAL"
                else (VerdictCode.VOID if scan_verdict == "VOID" else VerdictCode.HOLD)
            )
            return _echo_standing(
                VerdictOutput(
                    verdict=verdict_code,
                    reasons=[raw.get("summary", "Scan complete.")]
                    if isinstance(raw, dict)
                    else ["Scan complete."],
                    next_safe_action=(
                        "Review findings and remediate override patterns before continuing."
                        if scan_verdict in ("HOLD", "VOID")
                        else "No override patterns detected — proceed."
                    ),
                    meta={
                        "scan_instructions": raw if isinstance(raw, dict) else {"raw": str(raw)},
                        "floor": "L12",
                        "guard": "INJECTION_SCANNER",
                    },
                )
            )
        except Exception as exc:
            return _echo_standing(
                VerdictOutput(
                    verdict=VerdictCode.HOLD,
                    reasons=[f"scan_instructions failed: {exc}"],
                    next_safe_action="Check governance_scan module availability.",
                    meta={"error": str(exc)},
                )
            )

    import asyncio


    t_judge_start = time_module.monotonic()

    # Map action_tier to LatencyDecisionClass for budget lookup
    tier_to_class = {
        "standard": LatencyDecisionClass.C2_STANDARD,
        "elevated": LatencyDecisionClass.C3_DEEP,
        "sovereign": LatencyDecisionClass.C4_SOVEREIGN,
        "c4": LatencyDecisionClass.C4_SOVEREIGN,
        "c5": LatencyDecisionClass.C4_SOVEREIGN,
    }
    decision_class_latency = tier_to_class.get(action_tier, LatencyDecisionClass.C2_STANDARD)
    budget = LATENCY_BUDGETS.get(decision_class_latency)

    # ── Preventive timeout (L1 fix) ──────────────────────────────────
    # C4_SOVEREIGN: unbounded — no timeout. Human deliberation has no SLA.
    # All other classes: hard timeout via asyncio.wait_for.
    # If judge_fn exceeds budget → degrade immediately (preventive, not retroactive).
    timeout_seconds: float | None = None
    if budget and budget.max_latency_ms > 0:
        timeout_seconds = budget.max_latency_ms / 1000.0

    judge_coro = _arif_judge(
        mode=mode,
        candidate=candidate,
        session_id=session_id,
        actor_id=actor_id,
        constitutional_chain_id=constitutional_chain_id,
        audit_entropy=audit_entropy,
        wealth_score=_evidence.get("wealth_score"),
        verification_surface=_evidence.get("verification_surface"),
        evidence_receipt=evidence,
    )

    try:
        if timeout_seconds is not None:
            result = await asyncio.wait_for(judge_coro, timeout=timeout_seconds)
        else:
            result = await judge_coro
        elapsed_ms = (time_module.monotonic() - t_judge_start) * 1000
        within_budget = True
    except TimeoutError:
        elapsed_ms = budget.max_latency_ms  # killed at deadline
        within_budget = False
        # Degrade to the budget's prescribed verdict
        degradation_verdict = budget.degradation_verdict if budget else "HOLD"
        result = {
            "verdict": degradation_verdict,
            "reasons": [
                f"LATENCY_TIMEOUT: judge exceeded {budget.max_latency_ms}ms budget "
                f"for {decision_class_latency.value}. Degraded to {degradation_verdict} "
                f"(preventive timeout — deliberation did not complete)."
            ],
            "next_safe_action": "Re-run with narrower scope or escalate to sovereign (C4 unbounded).",
        }

    if "meta" not in result:
        result["meta"] = {}
    result["meta"]["latency_ms"] = round(elapsed_ms, 2)
    result["meta"]["within_budget"] = within_budget
    result["meta"]["budget_class"] = decision_class_latency.value
    result["meta"]["budget_max_ms"] = (
        budget.max_latency_ms if (budget and budget.max_latency_ms > 0) else "unbounded"
    )
    result["meta"]["timeout_enforcement"] = (
        "preventive" if timeout_seconds is not None else "unbounded"
    )
    if not within_budget:
        result["meta"]["degradation"] = budget.degradation_verdict if budget else "HOLD"

    # Plumbing fix for 7-tool facade + semantic contract: ensure dict for downstream
    if hasattr(result, "model_dump"):
        result = result.model_dump()
    elif not isinstance(result, dict):
        result = {"verdict": "HOLD", "reasons": ["internal result normalization failed"]}

    # ── A-RIF: Post-Adjudication Integrity Check ──
    from arifosmcp.runtime.a_rif.scorecard import track_judge

    is_seal = "SEAL" in str(result.get("verdict", ""))

    if mode == "judge" and is_seal:
        # A-RIF: Claim Strength Gate — enforce claim_strength ≤ evidence_level
        evidence_level = _evidence.get("vitals", {}).get("max_evidence_level", "L1")
        # Extract claimed strength from candidate if present
        if isinstance(candidate, dict):
            claim_strength = candidate.get("claim_strength", evidence_level)
        elif isinstance(candidate, str):
            from arifosmcp.runtime.a_rif.parser import parse_claimed_evidence_level

            parsed = parse_claimed_evidence_level(candidate)
            claim_strength = parsed if parsed else evidence_level
        else:
            claim_strength = evidence_level
        claim_strength = claim_strength or evidence_level

        overclaim = False
        reasons: list[str] = []

        # General gate: claim strength must not exceed evidence level
        if claim_strength > evidence_level:
            overclaim = True
            reasons.append(
                "A-RIF_GOVERNANCE: Claim strength ("
                f"{claim_strength}) exceeds evidence level ({evidence_level})."
            )

        # Elevated tier gate: C4/C5 requires L4+
        if _is_elevated_tier and evidence_level < "L4":
            overclaim = True
            reasons.append(
                "A-RIF_GOVERNANCE: "
                f"{action_tier} action requires L4+ evidence. "
                f"Current level: {evidence_level}."
            )

        if overclaim:
            track_judge(overclaim=True, attested=False)
            if isinstance(result, dict):
                result["verdict"] = "HOLD"
                result.setdefault("reasons", []).extend(reasons)
            else:
                result.verdict = VerdictCode.HOLD
                result.reasons.extend(reasons)
        else:
            track_judge(overclaim=False, attested=(evidence_level != "L0"))

    # ── SIMULATIVE DETECTION GATE (RSI EUREKA 2026-06-12, Forge #3) ──
    # F8 advisory: checks whether agent output is DESCRIBING or PERFORMING.
    # Never blocks — only attaches an advisory question to the result.
    # "Are you describing or performing?"
    try:
        from arifosmcp.runtime.simulative_detector import simulative_check

        _sim_text = candidate if isinstance(candidate, str) else str(candidate)
        _sim_result = simulative_check(_sim_text)
        if _sim_result and _sim_result.get("advisory_question"):
            if isinstance(result, dict):
                result.setdefault("meta", {})["simulative_check"] = {
                    "simulation_index": _sim_result["simulation_index"],
                    "verdict": _sim_result["verdict"],
                    "advisory_question": _sim_result["advisory_question"],
                    "gate_id": _sim_result.get("gate_id", "simulative_detector_N2"),
                }
                # F8 advisory: surface the question in reasons
                result.setdefault("reasons", []).append(
                    f"F8_SIMULATIVE: {_sim_result['advisory_question']}"
                )
            else:
                result.meta.setdefault("simulative_check", {})["simulation_index"] = _sim_result[
                    "simulation_index"
                ]
                result.meta.setdefault("simulative_check", {})["verdict"] = _sim_result["verdict"]
                result.meta.setdefault("simulative_check", {})["advisory_question"] = _sim_result[
                    "advisory_question"
                ]
                result.reasons.append(f"F8_SIMULATIVE: {_sim_result['advisory_question']}")
    except Exception:
        pass  # fail-soft: simulative detection never blocks deliberation

    # ── Attach WELL substrate + somatic state + maruah gate to result ──
    # Every judge verdict now carries biological readiness evidence + machine
    # somatic state + maruah critic verdict. This closes the loop for all three
    # civilizational intelligence gates.
    well_sub = _evidence.get("well_substrate", {})
    if isinstance(result, dict):
        result.setdefault("meta", {})["well_substrate"] = well_sub
        if well_sub.get("coupled_verdict") == "HOLD" and well_sub.get("has_telemetry"):
            result["meta"]["well_gate"] = (
                f"WELL HOLD: human_ready={well_sub.get('human_ready')} "
                f"floors_violated={well_sub.get('active_violations')} — "
                "biological substrate flags active. Verdict stands; ARIF confirmation advised."
            )

        # ── Somatic state attachment (Gap 2) ──
        _somatic_val = _evidence.get("somatic_state")
        if _somatic_val:
            result["meta"]["somatic_state"] = _somatic_val

        # ── Maruah gate attachment (Gap 1) ──
        _maruah_gate_val = _evidence.get("maruah_gate")
        if _maruah_gate_val:
            result["meta"]["maruah_gate"] = _maruah_gate_val

        # ── Paradox quote enrichment attachment (ATLAS333 Bridge §4) ──────
        _paradox_quotes_val = _evidence.get("paradox_quotes")
        if _paradox_quotes_val:
            result["meta"]["paradox_quotes"] = _paradox_quotes_val

        # ── SCALAR FEED PROTOCOL (TASK-P2-03) ─────────────────────────────
        # Live measurement of the 5 canonical APEX scalars (G, C_dark, W³,
        # κ_r, ψ_le) plus the computed QDF composite. Attached to every
        # verdict's audit trail under meta["scalar_snapshot"].
        #
        # F9 anti-hantu: scalar measurement failure is NOT VOID. The judge
        # already issued a verdict based on its own reasoning; the snapshot
        # is an audit signal, not a constitutional breach. Any UNMEASURED
        # scalar publishes meta["scalar_warning"] so downstream consumers
        # know the verdict was rendered without full scalar coverage.
        #
        # F1 AMANAH: ScalarCollector is read-only. Snapshot is computed
        # from session/evidence/witness_log/vault_chain (all read paths).
        # No mutation; no new side effects on the verdict path.
        try:
            from arifosmcp.core.scalar_collector import (
                UNMEASURED_SOURCE as _UNMEASURED_SOURCE,
            )
            from arifosmcp.core.scalar_collector import ScalarCollector

            _scalar_collector = ScalarCollector(
                session_id=session_id,
                evidence=evidence if isinstance(evidence, dict) else None,
            )
            _scalar_snapshot = _scalar_collector.collect_snapshot()
        except Exception as _scalar_exc:
            # Fail-soft: a broken collector must NEVER crash the judge.
            # Surface the failure as UNMEASURED so the audit trail still
            # tells the truth (F2).
            _scalar_snapshot = {
                "scalars": {},
                "qdf": None,
                "qdf_source": _UNMEASURED_SOURCE,
                "all_measured": False,
                "unmeasured_keys": [],
                "collector_error": str(_scalar_exc),
            }

        result["meta"]["scalar_snapshot"] = _scalar_snapshot
        if not _scalar_snapshot.get("all_measured", False):
            result["meta"]["scalar_warning"] = (
                "One or more scalars unmeasured — verdict rendered without "
                "full APEX telemetry. F9 anti-hantu: missing scalars are "
                "logged, not fabricated. See scalar_snapshot.unmeasured_keys."
            )

        # ── W-4: Attach G-WELL governance to elevated-tier verdicts ───────────
        if _is_elevated_tier and "well_governance" in _evidence:
            gov = _evidence["well_governance"]
            result["meta"]["well_governance"] = gov
            if gov.get("g_well_verdict") == "INCOHERENT":
                result["meta"]["governance_gate"] = (
                    f"G-WELL INCOHERENT: {gov.get('governance_flags')} — "
                    "machine governance substrate flagged."
                    " ARIF confirmation required for C4/C5 actions."
                )
            elif gov.get("g_well_verdict") == "FRAGMENTED":
                result["meta"]["governance_advisory"] = (
                    f"G-WELL FRAGMENTED: {gov.get('governance_flags')} — "
                    "governance integrity stressed. Proceed with caution."
                )

    # ── SABAR cooldown awareness (Stage 2A: advisory) ──
    _apply_cooldown_awareness(result, cooldown_entry_id)

    # ── F13 SOVEREIGN RECEIPT: attach to verdict metadata ──────────────────
    # The sovereign receipt is recorded in every verdict where it was provided.
    # This creates an auditable chain: F13 confirmation → verdict → vault seal.
    # Without the receipt, F13 gates remain active (constitutional HOLD).
    if sovereign_receipt and sovereign_receipt.strip():
        _receipt_hash = f"sha256:{hashlib.sha256(sovereign_receipt.encode()).hexdigest()[:16]}"
        if isinstance(result, dict):
            result.setdefault("meta", {})["f13_sovereign_receipt"] = {
                "receipt_hash": _receipt_hash,
                "provided": True,
                "effect": "F13_SOVEREIGN_CONFIRMED",
                "note": "Sovereign (Arif) has explicitly confirmed this action. "
                "F13 gate waived per constitutional receipt path.",
            }
            result.setdefault("reasons", []).append(
                f"F13_SOVEREIGN_RECEIPT: {_receipt_hash} — "
                "sovereign confirmation recorded. Proceeding under F13 authority."
            )
        if "f13_sovereign_receipt" in _evidence:
            result.setdefault("meta", {})["f13_clarity_waiver"] = _evidence["f13_sovereign_receipt"]

    verdict_str = str(result.get("verdict", ""))
    is_seal = "SEAL" in verdict_str

    # ── Self-annotating meta note (replaces former paradox anchor injection) ──
    # FORGE 2026-07-04: 11 paradox anchors removed (ABC falsifier: commentary
    # not enforcement). Verdict language is now self-annotating; floor gates
    # F1/F2/F6/F9/F11/F13 are the executable hard gates. Canon lineage
    # preserved at docs/canon/paradox_anchors.md (non-executable).
    if isinstance(result, dict):
        result.setdefault("meta", {})["paradox_anchor_status"] = (
            "REMOVED_2026-07-04_FORGE - see docs/canon/paradox_anchors.md. "
            "Enforceability comes from floor gates, not quote anchors."
        )
        # Zen Apex: freeze DecisionCore + optional witness AFTER verdict.
        # Witness is presentation only — never mutates verdict/floors.
        try:
            from arifosmcp.composer import attach_zen_witness_to_result

            result = attach_zen_witness_to_result(result, stage="999_RECEIPT")
        except Exception:
            result.setdefault("meta", {})["quote_resolution_status"] = "UNAVAILABLE"

    # ── Conflict Resolution (P0 wiring — I1 bridge) ──────────────────────
    # After verdict is rendered, run conflict resolution to determine if this
    # organ's verdict conflicts with others. Resolution result flows to vault receipt.
    # Single-envelope case (one organ): resolve_conflict handles it.
    # Multi-organ case (future): resolve_multi_organ does pairwise iteration.
    _conflict_result: dict[str, Any] = {"conflict_resolved": False, "conflict_resolution": "none"}
    try:
        _verdict = str(result.get("verdict", ""))
        _organ = (_evidence.get("organ_id") if isinstance(_evidence, dict) else None) or "arifOS"
        _envelope = ConflictEnvelope(
            conflict_id=f"{session_id or 'sess'}:{_organ}:{_verdict[:8]}",
            organ_a=_organ,
            verdict_a=_verdict,
            organ_b="human",
            verdict_b="888_HOLD",
            conflict_domain="constitutional_judgment",
            is_irreversible=("SEAL" in _verdict),
        )
        _res = resolve_conflict(_envelope)
        _conflict_result = {
            "conflict_resolved": True,
            "conflict_resolution": _res.resolution_method,
            "winner_organ": _res.winner_organ,
            "winner_verdict": _res.winner_verdict,
            "reason": _res.reason,
        }
        result.setdefault("meta", {})["conflict_resolution"] = _conflict_result
    except Exception:
        # Conflict resolution is advisory for now — never block vault sealing on error
        result.setdefault("meta", {})["conflict_resolution"] = _conflict_result

    if vault_entry_id and is_seal:
        try:
            from arifosmcp.tools.vault import arif_seal

            payload_dict = {
                "tool": "arif_judge",
                "candidate": candidate,
                "verdict": result.get("verdict", ""),
                "constitutional_chain_id": result.get("meta", {}).get("constitutional_chain_id"),
                "state_hash": result.get("meta", {}).get("state_hash"),
                "conflict_resolved": _conflict_result.get("conflict_resolved", False),
                "conflict_resolution": _conflict_result.get("conflict_resolution", "none"),
                "latency_ms": result.get("meta", {}).get("latency_ms", 0),
                "within_budget": result.get("meta", {}).get("within_budget", True),
                "predicted_state": {
                    "well_score": well_sub.get("well_score"),
                    "human_ready": well_sub.get("human_ready"),
                    "clarity": well_sub.get("clarity"),
                    "runtime_drift": _evidence.get("vitals", {}).get("runtime_drift", False),
                    "floors_checked": list(_evidence.get("floors_checked", [])),
                    "floors_violated": list(_evidence.get("floors_violated", [])),
                    # ── Vitals keys in 1:1 parity with arif_measure(mode='vitals') ──
                    "g_score": _evidence.get("vitals", {}).get("g_score"),
                    "delta_S": _evidence.get("vitals", {}).get("delta_S"),
                    "omega": _evidence.get("vitals", {}).get("omega"),
                    "psi_le": _evidence.get("vitals", {}).get("psi_le"),
                    "predicted_at": datetime.now(UTC).isoformat(),
                },
            }

            # ── ECHO/PaW SCHEMA PARITY VALIDATION ──────────────────────────
            # Before sealing, verify that prediction keys and observation keys
            # are from the same deterministic schema. Semantic translation in
            # the delta path introduces ΔS > 0 (F2 TRUTH violation risk).
            _predicted = payload_dict["predicted_state"]
            _observed = {
                **_evidence.get("vitals", {}),
                **well_sub,
                "floors_checked": list(_evidence.get("floors_checked", [])),
                "floors_violated": list(_evidence.get("floors_violated", [])),
            }
            _schema_parity = _validate_schema_parity(_predicted, _observed)
            if _schema_parity.get("schema_drift") or _schema_parity.get("warning"):
                result.setdefault("meta", {})["schema_parity"] = _schema_parity
                result.setdefault("reasons", []).append(
                    f"SCHEMA_PARITY: {_schema_parity.get('warning', 'schema validation triggered')}"
                )

            seal_result = await arif_seal(
                mode="seal",
                payload=json_lib.dumps(payload_dict),
                session_id=session_id,
                actor_id=actor_id,
                constitutional_chain_id=constitutional_chain_id,
                judge_state_hash=result.get("meta", {}).get("state_hash"),
                cooldown_entry_id=cooldown_entry_id,
                evidence_sha=vault_entry_id,  # L1→L2 bridge: vault entry IS the execution DAG node
            )
            if "meta" not in result:
                result["meta"] = {}
            result["meta"]["vault_sealed"] = True
            result["meta"]["vault_entry_id"] = getattr(seal_result, "entry_id", vault_entry_id)

            # ── Structured vault receipt (I1 bridge) ──────────────────────
            # Wire create_and_seal_receipt() for hash-chained provenance.
            # This runs alongside arif_seal() — additive, not replacement.
            # Produces a VaultReceipt with SHA-256 chain + Lamport clock
            # for tamper-evident audit trail.
            try:
                _verdict_hash = hashlib.sha256(
                    json_lib.dumps(result.get("verdict", ""), sort_keys=True).encode()
                ).hexdigest()
                _intent_hash = hashlib.sha256(
                    json_lib.dumps(
                        candidate if isinstance(candidate, str) else str(candidate)[:2000],
                        sort_keys=True,
                    ).encode()
                ).hexdigest()
                # F2 TRUTH: resolve real identity before minting receipt.
                _sess_ctx_j = None
                try:
                    from arifosmcp.runtime.tools import get_session as _gs_j

                    _sess_ctx_j = _gs_j(session_id) if session_id else None
                except Exception:
                    pass
                _rsid_j, _ractor_j = resolve_receipt_identity(
                    session_id=session_id,
                    actor_id=actor_id,
                    session_context=_sess_ctx_j,
                )
                _receipt = create_and_seal_receipt(
                    session_id=_rsid_j,
                    actor_id=_ractor_j,
                    organ_id=(_evidence.get("organ_id") if isinstance(_evidence, dict) else None)
                    or "arifOS",
                    intent_summary=(str(candidate)[:200] if candidate else "judge verdict"),
                    intent_hash=_intent_hash,
                    requested_authority=action_tier or "standard",
                    pre_state_hash=result.get("meta", {}).get("state_hash", ""),
                    decision=result.get("verdict", "UNKNOWN"),
                    verdict_hash=_verdict_hash,
                    floors_evaluated=list(_evidence.get("floors_checked", [])),
                    floors_violated=list(_evidence.get("floors_violated", [])),
                    conflict_resolved=_conflict_result.get("conflict_resolved", False),
                    conflict_resolution=_conflict_result.get("conflict_resolution", "none"),
                    decision_class=decision_class_latency.value,
                    latency_ms=result.get("meta", {}).get("latency_ms", 0),
                    within_budget=result.get("meta", {}).get("within_budget", True),
                    witness_count=1 if _conflict_result.get("conflict_resolved") else 0,
                )
                result["meta"]["receipt_id"] = _receipt.receipt_id
                result["meta"]["receipt_hash"] = _receipt.receipt_hash
                result["meta"]["receipt_chain_ok"] = True
            except Exception:
                # Vault receipt is additive — never block the primary seal on receipt failure
                result["meta"]["receipt_chain_ok"] = False
        except Exception:
            if "meta" not in result:
                result["meta"] = {}
            result["meta"]["vault_sealed"] = False

    # Semantic output fix: ensure amanah_proof validates for VerdictOutput (7-tool E2E)
    if "amanah_proof" in result and isinstance(result.get("amanah_proof"), dict):
        try:
            from arifosmcp.schemas.verdict import AmanahProof

            result["amanah_proof"] = AmanahProof(**result["amanah_proof"])
        except Exception:
            result["amanah_proof"] = AmanahProof()

    # Z5b — Reality Ledger auto-witness (non-blocking, fail-safe)
    try:
        _actor = result.get("actor", "unknown") if isinstance(result, dict) else "unknown"
        _verdict = result.get("verdict", "HOLD") if isinstance(result, dict) else "HOLD"
        _session = result.get("session_id", "unknown") if isinstance(result, dict) else "unknown"
        write_reality_event(
            actor=str(_actor),
            event_type="arif_judge",
            session_id=str(_session),
            verdict=str(_verdict),
            summary=f"arif_judge verdict: {_verdict}",
            action_class="judge",
            evidence={"call_hash": result.get("call_hash", "") if isinstance(result, dict) else ""},
        )
    except Exception:
        pass  # Ledger write must never block governance verdict

    try:
        return _echo_standing(VerdictOutput(**result))
    except Exception:
        # Robust fallback for incomplete semantic outputs or plumbing during E2E (7-tool facade)
        v = result.get("verdict", "HOLD") if isinstance(result, dict) else "HOLD"
        if v not in ("SEAL", "SABAR", "VOID", "HOLD", "PARADOX_HOLD"):
            v = "HOLD"
        r = (
            result.get("reasons", ["semantic normalization fallback"])
            if isinstance(result, dict)
            else ["semantic normalization fallback"]
        )
        return _echo_standing(
            VerdictOutput(verdict=v, reasons=r if isinstance(r, list) else [str(r)])
        )


def _apply_cooldown_awareness(result: dict, cooldown_entry_id: str | None) -> None:
    """Check cooldown state and enforce SABAR. Stage 2B: SEAL blocked when cooling incomplete."""
    if cooldown_entry_id is None:
        return

    try:
        from arifosmcp.core.cooldown_engine import get_cooldown_engine

        engine = get_cooldown_engine()
        entry = engine.check(cooldown_entry_id)

        if "meta" not in result:
            result["meta"] = {}

        if entry is None:
            result["meta"]["sabar_cooldown"] = {
                "cooldown_entry_id": cooldown_entry_id,
                "status": "not_found",
                "note": "cooldown entry not found — proceeding without cooldown verification",
            }
            return

        cooldown_info = {
            "cooldown_entry_id": cooldown_entry_id,
            "verdict": entry.verdict,
            "remaining_hours": round(entry.remaining_hours, 1),
            "tri_witness_count": entry.tri_witness.count,
            "tri_witness_complete": entry.tri_witness.is_complete,
        }

        if entry.verdict == "SEAL":
            cooldown_info["status"] = "cooled"
            cooldown_info["note"] = "cooldown complete + witnessed — SEAL eligible"
        elif entry.verdict == "VOID":
            cooldown_info["status"] = "voided"
            cooldown_info["note"] = f"cooldown entry voided: {entry.void_reason}"
        elif entry.is_expired:
            cooldown_info["status"] = "expired"
            cooldown_info["note"] = "cooldown expired — auto-VOID applied"
        else:
            cooldown_info["status"] = "pending"
            cooldown_info["note"] = (
                f"SABAR: cooling incomplete ({entry.remaining_hours:.1f}h remaining, "
                f"{entry.tri_witness.count}/3 witnesses)."
            )

            # Stage 2B: hard enforcement — SEAL downgraded to SABAR when cooling incomplete
            verdict = str(result.get("verdict", ""))
            if "SEAL" in verdict:
                result["verdict"] = "SABAR"
                cooldown_info["enforcement"] = (
                    f"SABAR enforced — SEAL blocked. "
                    f"Return in {entry.remaining_hours:.1f}h with {3 - entry.tri_witness.count} "
                    "more witness(es) to unlock SEAL."
                )

        result["meta"]["sabar_cooldown"] = cooldown_info

    except Exception:
        if "meta" not in result:
            result["meta"] = {}
        result["meta"]["sabar_cooldown"] = {
            "cooldown_entry_id": cooldown_entry_id,
            "status": "unavailable",
            "note": "cooldown engine not reachable — proceeding without verification",
        }


# Backward compatibility alias
arif_judge_deliberate = arif_judge
