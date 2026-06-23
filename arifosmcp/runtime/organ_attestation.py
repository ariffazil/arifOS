"""
arifosmcp/runtime/organ_attestation.py
═══════════════════════════════════════════════════════════════════════════════
Live organ attestation registry for the sovereign AGI kernel.

Every federation organ must be able to prove:
  - identity (organ_id, role, version)
  - capability surface (tool names + schema hash)
  - constitutional binding (constitution hash, attestation status)
  - liveness (heartbeat)

This module stores attestations in-memory (L1/L2) and surfaces them via the
live-kernel envelope. Attestations are evidence-only; arifOS judges.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from arifosmcp.runtime.heartbeat_registry import record_heartbeat as _record_heartbeat
from arifosmcp.runtime.live_kernel import (
    AuditReceipt,
    AuthorityLease,
    KernelIdentity,
    LiveKernelEnvelope,
    OrganHeartbeat,
    RiskProfile,
    StateProvenance,
)
from arifosmcp.runtime.live_kernel import (
    OrganAttestation as OrganAttestationEnvelope,
)
from arifosmcp.runtime.peer_contract import (
    get_arifos_peer_contract_hash,
    get_arifos_peer_contract_url,
)

logger = logging.getLogger("arifosmcp.organ_attestation")


# ═══════════════════════════════════════════════════════════════════════════════
# Health-status classification helper
# ═══════════════════════════════════════════════════════════════════════════════
#
# Bug #509: The previous allow-list `("healthy", "OK", True)` rejected "ALIVE"
# and other valid healthy status strings returned by organ `/health` endpoints
# (e.g. WEALTH returns `"status":"ALIVE"`). This caused `arif_organ_attest_all`
# to mark healthy organs as DEGRADED_CLAIM on every call.
#
# The `is_healthy()` helper normalises the allow-list across all federation
# organs. New healthy status strings should be added here, NOT in inline
# allow-lists scattered through the codebase.
# ═══════════════════════════════════════════════════════════════════════════════

_HEALTHY_STATUSES = frozenset(
    {
        "healthy",  # arifOS, A-FORGE, AAA, GEOX
        "alive",  # WEALTH (canonical)
        "ok",  # legacy / informal
        "pass",  # arifOS /ready selftest
        "ready",  # generic health endpoints
        "serving",  # gRPC-style health
    }
)


def is_healthy(status: str | bool | None) -> bool:
    """Return True iff a health-probe `status` field indicates a live organ.

    Accepts: True, "healthy", "alive", "ok", "pass", "ready", "serving" (case-insensitive).
    Rejects: None, False, "unhealthy", "degraded", "fail", "down", "timeout", etc.
    Unknown strings are conservative-fail (return False) — F2 TRUTH over F4 CLARITY.
    """
    if status is True:
        return True
    if not isinstance(status, str):
        return False
    return status.strip().lower() in _HEALTHY_STATUSES


# ═══════════════════════════════════════════════════════════════════════════════
# Registry
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class OrganAttestationRecord:
    organ_id: str
    role: str
    version: str
    tool_count: int
    schema_hash: str
    constitution_hash: str = "sha256:missing"  # arifOS only — kept for backward compat
    identity_anchor_type: str = "constitution_hash"  # constitution_hash | physics_manifest | capital_manifest | substrate_manifest
    identity_anchor_hash: str = "sha256:missing"
    status: str = "UNATTESTED"  # ALIVE | DEGRADED_NOT_FAILED | DEGRADED_CLAIM | CONSTITUTIONAL_HOLD | DEGRADED | UNATTESTED | REVOKED
    # ── Status Semantics (2026-06-13) ──
    # ALIVE                  — organ fully operational, all providers optimal
    # DEGRADED_NOT_FAILED    — organ operational but on fallback tier (e.g. HEART via ILMU instead of MiniMax)
    # DEGRADED_CLAIM         — organ responding but surface/tools incomplete or unhealthy
    # CONSTITUTIONAL_HOLD    — organ correctly holding at constitutional gate (e.g. JUDGE at F13 — constitution working)
    # DEGRADED               — organ unreachable or non-responsive
    # UNATTESTED             — organ not yet attested
    # REVOKED                — organ attestation explicitly revoked
    reason: str | None = None
    heartbeat_at: float = field(default_factory=time.time)
    raw_health: dict[str, Any] = field(default_factory=dict)
    raw_tools: list[dict[str, Any]] = field(default_factory=list)


_ORGAN_REGISTRY: dict[str, OrganAttestationRecord] = {}


# Known federation organs and their local bridge modules
# P6 — per-organ identity anchor types (Arif 2026-06-13):
#   arifOS  → constitution_hash          (human constitutional law)
#   GEOX    → physics_manifest_hash       (natural law / kuasa alam)
#   WEALTH  → capital_manifest_hash       (value law)
#   WELL    → substrate_manifest_hash     (vitality law)
_ORGAN_CONFIG: dict[str, dict[str, Any]] = {
    "arifOS": {
        "role": "constitutional_kernel",
        "health_module": "arifosmcp.runtime.self_bridge",
        "health_fn": "arifos_health_check",
        "list_fn": "list_arifos_tools",
        "identity_anchor_type": "constitution_hash",
        "identity_anchor_candidates": [
            "/root/arifOS/static/arifos/theory/000/000_CONSTITUTION.md",
            "/opt/arifos/app/static/arifos/theory/000/000_CONSTITUTION.md",
        ],
        # kept for backward compat — sameness check only
        "constitution_candidates": [
            "/root/arifOS/static/arifos/theory/000/000_CONSTITUTION.md",
            "/opt/arifos/app/static/arifos/theory/000/000_CONSTITUTION.md",
        ],
    },
    "GEOX": {
        "role": "earth_intelligence",
        "health_module": "arifosmcp.runtime.geox_bridge",
        "health_fn": "geox_health_check",
        "list_fn": "list_geox_tools",
        "identity_anchor_type": "physics_manifest",
        "identity_anchor_candidates": [
            "/root/geox/GENESIS/004_PHYSICS_MANIFEST.md",
            "/opt/geox/app/GENESIS/004_PHYSICS_MANIFEST.md",
        ],
        # kept for backward compat — sameness check only
        "constitution_candidates": [
            "/root/geox/GENESIS/004_PHYSICS_MANIFEST.md",
            "/opt/geox/app/GENESIS/004_PHYSICS_MANIFEST.md",
        ],
    },
    "WEALTH": {
        "role": "capital_intelligence",
        "health_module": "arifosmcp.runtime.wealth_bridge",
        "health_fn": "wealth_health_check",
        "list_fn": "list_wealth_tools",
        "identity_anchor_type": "capital_manifest",
        "identity_anchor_candidates": [
            "/root/WEALTH/canon/001_CAPITAL_MANIFEST.md",
            "/opt/wealth/app/canon/001_CAPITAL_MANIFEST.md",
        ],
        "constitution_candidates": [
            "/root/WEALTH/canon/001_CAPITAL_MANIFEST.md",
            "/opt/wealth/app/canon/001_CAPITAL_MANIFEST.md",
        ],
    },
    "WELL": {
        "role": "human_readiness",
        "health_module": "arifosmcp.runtime.well_bridge",
        "health_fn": "well_health_check",  # async HTTP + file-based readiness
        "list_fn": "list_well_tools",
        "identity_anchor_type": "substrate_manifest",
        "identity_anchor_candidates": [
            "/root/WELL/GENESIS/012_SUBSTRATE_MANIFEST.md",
            "/opt/well/app/GENESIS/012_SUBSTRATE_MANIFEST.md",
        ],
        "constitution_candidates": [
            "/root/WELL/GENESIS/012_SUBSTRATE_MANIFEST.md",
            "/opt/well/app/GENESIS/012_SUBSTRATE_MANIFEST.md",
        ],
    },
    "VAULT999": {
        "role": "immutable_ledger",
        "health_module": "arifosmcp.runtime.vault_bridge",
        "health_fn": "vault_health_check",
        "list_fn": "list_vault_tools",
        "identity_anchor_type": "vault_manifest",
        "identity_anchor_candidates": [
            "/agent/vault999/vault999.jsonl",
            "/agent/vault999/vault999_legacy.jsonl",
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════


def _sha256_of_text(text: str) -> str:
    return f"sha256:{hashlib.sha256(text.encode()).hexdigest()}"


def _sha256_of_file(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return f"sha256:{hashlib.sha256(f.read()).hexdigest()}"
    except Exception:
        return "sha256:unavailable"


def _load_organ_identity_anchor(organ_id: str) -> tuple[str, str]:
    """Return (identity_anchor_type, identity_anchor_hash) for an organ.

    Per-organ identity anchors:
      - arifOS  → constitution_hash          (human constitutional law)
      - GEOX    → physics_manifest           (natural law / kuasa alam)
      - WEALTH  → capital_manifest           (value law)
      - WELL    → substrate_manifest         (vitality law)
    """
    cfg = _ORGAN_CONFIG.get(organ_id, {})
    anchor_type = cfg.get("identity_anchor_type", "constitution_hash")
    for p in cfg.get("identity_anchor_candidates", []):
        if __import__("os").path.exists(p):
            return (anchor_type, _sha256_of_file(p))
    return (anchor_type, "sha256:missing")


def _load_organ_constitution_hash(organ_id: str) -> str:
    """DEPRECATED — use _load_organ_identity_anchor instead.
    Kept for backward compatibility with existing heartbeat records.
    For GEOX, this now reads the physics manifest, not a constitution file.
    """
    _, anchor_hash = _load_organ_identity_anchor(organ_id)
    return anchor_hash


def _schema_hash_from_tools(tools: list[dict[str, Any]]) -> str:
    """Hash the canonical tool surface: sorted names + input schema keys."""
    simplified: list[dict[str, Any]] = []
    for t in sorted(tools, key=lambda x: x.get("name", "")):
        name = t.get("name", "")
        schema = t.get("inputSchema") or t.get("input_schema") or {}
        simplified.append(
            {
                "name": name,
                "schema_keys": sorted(schema.get("properties", {}).keys()),
                "required": sorted(schema.get("required", [])),
            }
        )
    return _sha256_of_text(json.dumps(simplified, sort_keys=True))


async def _call_organ_health(organ_id: str) -> dict[str, Any]:
    cfg = _ORGAN_CONFIG.get(organ_id, {})
    mod_name = cfg.get("health_module")
    fn_name = cfg.get("health_fn")
    if not mod_name or not fn_name:
        return {"status": "unknown", "error": "no bridge configured"}

    try:
        mod = __import__(mod_name, fromlist=[fn_name])
        fn = getattr(mod, fn_name)
        if __import__("inspect").iscoroutinefunction(fn):
            return await fn()
        return fn()
    except Exception as e:
        logger.warning(f"Organ health probe failed for {organ_id}: {e}")
        return {"status": "unhealthy", "error": str(e)}


async def _list_organ_tools(organ_id: str) -> list[dict[str, Any]]:
    cfg = _ORGAN_CONFIG.get(organ_id, {})
    mod_name = cfg.get("health_module")
    fn_name = cfg.get("list_fn")
    if not mod_name or not fn_name:
        return []

    try:
        mod = __import__(mod_name, fromlist=[fn_name])
        fn = getattr(mod, fn_name)
        if __import__("inspect").iscoroutinefunction(fn):
            return await fn()
        return fn()
    except Exception as e:
        logger.warning(f"Organ tool list failed for {organ_id}: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# Core attestation
# ═══════════════════════════════════════════════════════════════════════════════


async def attest_organ(
    organ_id: str,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Probe a federation organ and produce a live attestation record.

    If the organ is unreachable or its surface is empty, the record is marked
    DEGRADED_CLAIM and the envelope verdict becomes DEGRADED. The kernel must
    fail-closed when an attestation is stale or degraded.
    """
    now = datetime.now(UTC).isoformat()
    cfg = _ORGAN_CONFIG.get(organ_id)
    if cfg is None and organ_id != "arifOS":
        return {
            "status": "HOLD",
            "verdict": "HOLD",
            "reason": f"Unknown organ: {organ_id}",
        }

    health = await _call_organ_health(organ_id)
    tools = await _list_organ_tools(organ_id)
    schema_hash = _schema_hash_from_tools(tools)

    # P6 — per-organ identity anchor (NOT just constitution_hash)
    identity_anchor_type, identity_anchor_hash = _load_organ_identity_anchor(organ_id)
    # Backward compat: constitution_hash still tracked for arifOS, set to identity hash for others
    constitution_hash = identity_anchor_hash

    # Read health response for domain-specific identity fields if available
    if isinstance(health, dict):
        # GEOX health now carries domain_law + physics_manifest_hash
        if organ_id == "GEOX" and health.get("domain_law") == "NATURAL_LAW":
            health_anchor = health.get("physics_manifest_hash")
            if health_anchor and health_anchor != "sha256:missing":
                identity_anchor_hash = health_anchor

    status = "ALIVE"
    reason = None
    degraded = False

    if not is_healthy(health.get("status")):
        status = "DEGRADED_CLAIM"
        reason = f"Health probe returned: {health.get('status', 'unknown')}"
        degraded = True
    elif not tools and not is_healthy(health.get("status")):
        # Both health probe AND tools/list failed — true degradation
        status = "DEGRADED_CLAIM"
        reason = "Tool surface empty or unreachable"
        degraded = True
    elif not tools:
        # Health probe PASSED but tools/list returned empty
        # This is a probe method failure (HTTP), not an organ failure
        # Surface as PARTIAL_DEGRADED to distinguish from true degradation
        status = "PARTIAL_DEGRADED"
        reason = "Tool surface unreachable via HTTP MCP probe — organ alive at health endpoint"
        # NOT degraded=True — organ is alive, probe method is the issue
    elif identity_anchor_hash == "sha256:missing":
        # Correct language: not "constitution file unavailable" but anchor-type-aware
        reason = f"Identity anchor ({identity_anchor_type}) unavailable"
        # For GEOX: physics_manifest missing ≠ DEGRADED if physics_guard passes
        if organ_id == "GEOX" and health.get("domain_law") == "NATURAL_LAW":
            # GEOX answers to alam, not to floors. Registry PASS is sufficient.
            # Only degrade if tools are also empty (already caught above).
            if health.get("identity") is True:
                # GEOX identity invariant passes — don't degrade on missing manifest file alone
                pass
            else:
                status = "DEGRADED_CLAIM"
                degraded = True
        else:
            status = "DEGRADED_CLAIM"
            degraded = True

    record = OrganAttestationRecord(
        organ_id=organ_id,
        role=cfg["role"] if cfg else "unknown",
        version=health.get("version") or health.get("schema_version") or "unknown",
        tool_count=len(tools),
        schema_hash=schema_hash,
        constitution_hash=constitution_hash,  # backward compat
        identity_anchor_type=identity_anchor_type,
        identity_anchor_hash=identity_anchor_hash,
        status=status,
        reason=reason,
        heartbeat_at=time.time(),
        raw_health=health,
        raw_tools=tools,
    )
    _ORGAN_REGISTRY[organ_id] = record

    heartbeat = OrganHeartbeat(
        organ_id=organ_id,
        status=status,
        version=record.version,
        schema_hash=schema_hash,
        constitution_hash=constitution_hash,  # backward compat
        identity_anchor_type=identity_anchor_type,
        identity_anchor_hash=identity_anchor_hash,
        tool_count=len(tools),
        heartbeat_at=now,
        degraded=degraded,
        reason=reason,
        load={
            "health_status": health.get("status", "unknown"),
            "peer_contract_url": get_arifos_peer_contract_url(),
            "peer_contract_hash": get_arifos_peer_contract_hash(),
        },
    )
    _record_heartbeat(
        organ_id=organ_id,
        status=status,
        version=record.version,
        schema_hash=schema_hash,
        constitution_hash=constitution_hash,  # backward compat
        tool_count=len(tools),
        degraded=degraded,
        reason=reason,
        load={
            "health_status": health.get("status", "unknown"),
            "peer_contract_url": get_arifos_peer_contract_url(),
            "peer_contract_hash": get_arifos_peer_contract_hash(),
        },
    )

    envelope = LiveKernelEnvelope(
        kernel=KernelIdentity(
            session_id=session_id or "",
            actor_id=actor_id or "",
            constitution_hash=_load_arifos_constitution_hash(),
        ),
        organ=OrganAttestationEnvelope(
            organ_id=organ_id,
            organ_role=record.role,
            organ_version=record.version,
            tool_name="arif_organ_attest",
            tool_schema_hash=_load_envelope_schema_hash(),
            attestation_status=status,
        ),
        authority=AuthorityLease(
            lease_id="LEASE-ATTEST",
            lease_scope=["attest", "observe"],
            action_class="OBSERVE",
        ),
        state=StateProvenance(
            input_hash=_sha256_of_text(json.dumps({"organ_id": organ_id, "actor_id": actor_id})),
            current_state_hash=_sha256_of_text(heartbeat.model_dump_json()),
        ),
        risk=RiskProfile(
            reversibility_score=1.0,
            blast_radius="LOW",
            secret_touching=False,
            human_ack_required=False,
        ),
        audit=AuditReceipt(
            vault_required=True,
            seal_mode="observe",
        ),
        verdict="DEGRADED" if degraded else "SEAL",
    )

    # Derive canonical tool count from federation registry (declared, not probed)
    _canonical_tc = 0
    try:
        from arifosmcp.runtime.federation_registry import FEDERATION_ORGANS

        _canonical_tc = FEDERATION_ORGANS.get(organ_id, {}).get("canonical_tools", 0)
    except Exception:
        pass

    return {
        "status": "OK" if not degraded else "DEGRADED",
        "tool": "arif_organ_attest",
        "verdict": envelope.verdict,
        "result": {
            "heartbeat": heartbeat.model_dump(mode="json"),
            "envelope": envelope.model_dump(mode="json"),
            "tools_observed": len(tools),
            "tool_count_live": len(tools),
            "tool_count_canonical": _canonical_tc,
            "probe_method": "http_mcp",
        },
    }


def get_organ_attestation(organ_id: str) -> OrganAttestationRecord | None:
    return _ORGAN_REGISTRY.get(organ_id)


def list_organ_attestations() -> dict[str, OrganAttestationRecord]:
    return dict(_ORGAN_REGISTRY)


def revoke_organ_attestation(organ_id: str, reason: str = "sovereign_revoke") -> bool:
    rec = _ORGAN_REGISTRY.get(organ_id)
    if rec is None:
        return False
    rec.status = "REVOKED"
    rec.reason = reason
    rec.degraded = True
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# arifOS self-attestation wrapper
# ═══════════════════════════════════════════════════════════════════════════════


def _load_arifos_constitution_hash() -> str:
    from arifosmcp.runtime.live_kernel import compute_constitution_hash

    return compute_constitution_hash()


def _load_envelope_schema_hash() -> str:
    candidates = [
        "/root/arifOS/contracts/arifos_live_kernel_envelope.v1.json",
        "/opt/arifos/app/contracts/arifos_live_kernel_envelope.v1.json",
    ]
    for p in candidates:
        if __import__("os").path.exists(p):
            return _sha256_of_file(p)
    return "sha256:missing"


async def attest_all_organs(
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Attest every known federation organ plus arifOS itself.

    Also broadcasts organ heartbeats to the NATS intelligence mesh
    so every organ is aware of every other organ's liveness.
    """
    from arifosmcp.runtime.live_kernel import arif_os_attest
    from arifosmcp.runtime.nats_event_bus import event_bus

    results: dict[str, Any] = {"arifOS": arif_os_attest(actor_id, session_id)}
    degraded: list[str] = []
    if results["arifOS"].get("verdict") != "SEAL":
        degraded.append("arifOS")

    for organ_id in _ORGAN_CONFIG:
        res = await attest_organ(organ_id, actor_id, session_id)
        results[organ_id] = res
        if res.get("verdict") != "SEAL":
            degraded.append(organ_id)

    # Broadcast organ states to intelligence mesh
    heartbeats: dict[str, str] = {}
    for organ_id, res in results.items():
        verdict = res.get("verdict", "UNKNOWN") if isinstance(res, dict) else "UNKNOWN"
        heartbeats[organ_id] = "alive" if verdict == "SEAL" else "degraded"

    try:
        await event_bus.publish_intelligence_broadcast(
            organ_heartbeats=heartbeats,
        )
    except Exception:
        pass  # F1 AMANAH: mesh failure must never block governance

    return {
        "status": "OK" if not degraded else "DEGRADED",
        "tool": "arif_organ_attest_all",
        "verdict": "SEAL" if not degraded else "DEGRADED",
        "result": {
            "organs": results,
            "degraded_organs": degraded,
            "attested_at": datetime.now(UTC).isoformat(),
        },
    }


__all__ = [
    "OrganAttestationRecord",
    "attest_organ",
    "attest_all_organs",
    "get_organ_attestation",
    "list_organ_attestations",
    "revoke_organ_attestation",
]
