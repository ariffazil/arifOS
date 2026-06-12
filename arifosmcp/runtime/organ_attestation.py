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

logger = logging.getLogger("arifosmcp.organ_attestation")


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
    constitution_hash: str = "sha256:missing"
    status: str = "UNATTESTED"  # ALIVE | DEGRADED_CLAIM | DEGRADED | UNATTESTED | REVOKED
    reason: str | None = None
    heartbeat_at: float = field(default_factory=time.time)
    raw_health: dict[str, Any] = field(default_factory=dict)
    raw_tools: list[dict[str, Any]] = field(default_factory=list)


_ORGAN_REGISTRY: dict[str, OrganAttestationRecord] = {}


# Known federation organs and their local bridge modules
_ORGAN_CONFIG: dict[str, dict[str, Any]] = {
    "GEOX": {
        "role": "earth_intelligence",
        "health_module": "arifosmcp.runtime.geox_bridge",
        "health_fn": "geox_health_check",
        "list_fn": "list_geox_tools",
        "constitution_candidates": [
            "/root/geox/GENESIS/000_KERNEL_CANON.md",
            "/opt/geox/app/GENESIS/000_KERNEL_CANON.md",
        ],
    },
    "WEALTH": {
        "role": "capital_intelligence",
        "health_module": "arifosmcp.runtime.wealth_bridge",
        "health_fn": "wealth_health_check",
        "list_fn": "list_wealth_tools",
        "constitution_candidates": [
            "/root/WEALTH/canon/000_KERNEL_CANON.md",
            "/opt/wealth/app/canon/000_KERNEL_CANON.md",
        ],
    },
    "WELL": {
        "role": "human_readiness",
        "health_module": "arifosmcp.runtime.well_bridge",
        "health_fn": "get_biological_readiness",  # synchronous fallback
        "list_fn": None,
        "constitution_candidates": [
            "/root/WELL/GENESIS/000_KERNEL_CANON.md",
            "/opt/well/app/GENESIS/000_KERNEL_CANON.md",
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


def _load_organ_constitution_hash(organ_id: str) -> str:
    cfg = _ORGAN_CONFIG.get(organ_id, {})
    for p in cfg.get("constitution_candidates", []):
        if __import__("os").path.exists(p):
            return _sha256_of_file(p)
    return "sha256:missing"


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
    constitution_hash = _load_organ_constitution_hash(organ_id)

    status = "ALIVE"
    reason = None
    degraded = False

    if health.get("status") not in ("healthy", "OK", True):
        status = "DEGRADED_CLAIM"
        reason = f"Health probe returned: {health.get('status', 'unknown')}"
        degraded = True
    elif not tools:
        status = "DEGRADED_CLAIM"
        reason = "Tool surface empty or unreachable"
        degraded = True
    elif constitution_hash == "sha256:missing":
        status = "DEGRADED_CLAIM"
        reason = "Constitution file unavailable"
        degraded = True

    record = OrganAttestationRecord(
        organ_id=organ_id,
        role=cfg["role"] if cfg else "unknown",
        version=health.get("version") or health.get("schema_version") or "unknown",
        tool_count=len(tools),
        schema_hash=schema_hash,
        constitution_hash=constitution_hash,
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
        constitution_hash=constitution_hash,
        tool_count=len(tools),
        heartbeat_at=now,
        degraded=degraded,
        reason=reason,
        load={"health_status": health.get("status", "unknown")},
    )
    _record_heartbeat(
        organ_id=organ_id,
        status=status,
        version=record.version,
        schema_hash=schema_hash,
        constitution_hash=constitution_hash,
        tool_count=len(tools),
        degraded=degraded,
        reason=reason,
        load={"health_status": health.get("status", "unknown")},
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

    return {
        "status": "OK" if not degraded else "DEGRADED",
        "tool": "arif_organ_attest",
        "verdict": envelope.verdict,
        "result": {
            "heartbeat": heartbeat.model_dump(mode="json"),
            "envelope": envelope.model_dump(mode="json"),
            "tools_observed": len(tools),
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
    candidates = [
        "/root/arifOS/GENESIS/000_KERNEL_CANON.md",
        "/opt/arifos/app/GENESIS/000_KERNEL_CANON.md",
    ]
    for p in candidates:
        if __import__("os").path.exists(p):
            return _sha256_of_file(p)
    return "sha256:missing"


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
    """Attest every known federation organ plus arifOS itself."""
    from arifosmcp.runtime.live_kernel import arif_os_attest

    results: dict[str, Any] = {"arifOS": arif_os_attest(actor_id, session_id)}
    degraded: list[str] = []
    if results["arifOS"].get("verdict") != "SEAL":
        degraded.append("arifOS")

    for organ_id in _ORGAN_CONFIG:
        res = await attest_organ(organ_id, actor_id, session_id)
        results[organ_id] = res
        if res.get("verdict") != "SEAL":
            degraded.append(organ_id)

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
