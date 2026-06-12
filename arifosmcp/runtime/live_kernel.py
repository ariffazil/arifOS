"""
arifosmcp/runtime/live_kernel.py
═══════════════════════════════════════════════════════════════════
Live Sovereign AGI Kernel transport layer.

Turns MCP from a tool bus into a governed state bus.
Every kernel-grade call must carry identity, attestation, lease,
memory provenance, risk, and audit continuity.

Implements the contract in contracts/arifos_live_kernel_envelope.v1.json.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# Core models
# ═══════════════════════════════════════════════════════════════════════════════


class KernelIdentity(BaseModel):
    kernel_id: str = "arifOS"
    constitution_id: str = "arifos-constitution-v2026.05.05-SSCT"
    constitution_hash: str = "sha256:pending"
    session_id: str = ""
    epoch_id: str = "EPOCH-LIVE-1"
    actor_id: str = ""
    actor_verified: bool = False
    sovereign: str = "ARIF_FAZIL"


class OrganAttestation(BaseModel):
    organ_id: str
    organ_role: str
    organ_version: str
    tool_name: str
    tool_schema_hash: str = "sha256:pending"
    attestation_status: str = "UNATTESTED"


class AuthorityLease(BaseModel):
    action_class: str = "OBSERVE"
    lease_id: str = "LEASE-NONE"
    lease_scope: list[str] = Field(default_factory=list)
    mutation_allowed: bool = False
    external_side_effect_allowed: bool = False
    irreversible_allowed: bool = False


class StateProvenance(BaseModel):
    input_hash: str = "sha256:0"
    memory_refs: list[str] = Field(default_factory=list)
    prior_state_hash: str = "sha256:0"
    current_state_hash: str = "sha256:0"


class RiskProfile(BaseModel):
    reversibility_score: float = 1.0
    blast_radius: str = "LOW"
    secret_touching: bool = False
    human_ack_required: bool = False


class AuditReceipt(BaseModel):
    vault_required: bool = False
    audit_pointer: str | None = None
    seal_mode: str = "observe"


class LiveKernelEnvelope(BaseModel):
    """Mandatory envelope for a kernel-grade MCP call/response."""

    kernel: KernelIdentity
    organ: OrganAttestation
    authority: AuthorityLease
    state: StateProvenance
    risk: RiskProfile
    audit: AuditReceipt
    verdict: str = "OBSERVE_ONLY"


class OrganHeartbeat(BaseModel):
    """Periodic self-report from a federation organ."""

    event_type: str = "ORGAN_HEARTBEAT"
    organ_id: str
    status: str = "ALIVE"
    version: str = "0.0.0"
    schema_hash: str = "sha256:pending"
    constitution_hash: str = "sha256:pending"
    tool_count: int = 0
    heartbeat_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_vault_seal: str = "sha256:0"
    degraded: bool = False
    reason: str | None = None
    load: dict[str, Any] = Field(default_factory=dict)


class LeaseGrant(BaseModel):
    """A bounded authority lease issued by arifOS to an organ/agent."""

    lease_id: str
    issued_by: str = "arifOS"
    sovereign: str = "ARIF_FAZIL"
    organ_id: str
    scope: list[str] = Field(default_factory=list)
    forbidden: list[str] = Field(default_factory=list)
    expires_at: str
    max_action_class: str = "OBSERVE"
    vault_required: bool = True


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


def _load_constitution_hash() -> str:
    """Best-effort hash of the canonical constitution file."""
    candidates = [
        "/root/arifOS/GENESIS/000_KERNEL_CANON.md",
        "/opt/arifos/app/GENESIS/000_KERNEL_CANON.md",
    ]
    for p in candidates:
        if os.path.exists(p):
            return _sha256_of_file(p)
    return "sha256:missing"


def _load_envelope_schema_hash() -> str:
    candidates = [
        "/root/arifOS/contracts/arifos_live_kernel_envelope.v1.json",
        "/opt/arifos/app/contracts/arifos_live_kernel_envelope.v1.json",
    ]
    for p in candidates:
        if os.path.exists(p):
            return _sha256_of_file(p)
    return "sha256:missing"


def build_kernel_envelope(
    tool_name: str,
    response: dict[str, Any],
    session_id: str | None = None,
    actor_id: str | None = None,
    organ_id: str = "arifOS",
    organ_role: str = "constitutional_kernel",
    organ_version: str = "v2026.05.05-SSCT",
    action_class: str = "OBSERVE",
    lease_id: str = "LEASE-NONE",
    lease_scope: list[str] | None = None,
    mutation_allowed: bool = False,
    external_side_effect_allowed: bool = False,
    irreversible_allowed: bool = False,
    prior_state_hash: str = "sha256:0",
    memory_refs: list[str] | None = None,
    vault_required: bool = False,
    seal_mode: str = "observe",
    audit_pointer: str | None = None,
) -> LiveKernelEnvelope:
    """
    Build a conservative live-kernel envelope around any tool response.

    Default posture is OBSERVE_ONLY / mutation=false. Actual authority is
    upgraded only by explicit lease or governance pipeline decision.
    """
    constitution_hash = _load_constitution_hash()
    envelope_schema_hash = _load_envelope_schema_hash()

    response_json = json.dumps(response, sort_keys=True, default=str)
    current_state_hash = _sha256_of_text(response_json)
    input_hash = _sha256_of_text(tool_name)

    verdict = str(response.get("verdict", response.get("status", "OBSERVE_ONLY")))
    if verdict not in ("SEAL", "DEGRADED", "OBSERVE_ONLY", "HOLD", "DENY"):
        verdict = "OBSERVE_ONLY"

    risk_blast = "LOW"
    reversibility = 1.0
    if verdict in ("HOLD", "DENY"):
        risk_blast = "MEDIUM"
        reversibility = 0.0
    elif verdict == "DEGRADED":
        risk_blast = "MEDIUM"
        reversibility = 0.5

    return LiveKernelEnvelope(
        kernel=KernelIdentity(
            session_id=session_id or "",
            actor_id=actor_id or "",
            constitution_hash=constitution_hash,
        ),
        organ=OrganAttestation(
            organ_id=organ_id,
            organ_role=organ_role,
            organ_version=organ_version,
            tool_name=tool_name,
            tool_schema_hash=envelope_schema_hash,
            attestation_status="ALIVE" if verdict == "SEAL" else "DEGRADED_CLAIM",
        ),
        authority=AuthorityLease(
            action_class=action_class,
            lease_id=lease_id,
            lease_scope=lease_scope or [],
            mutation_allowed=mutation_allowed,
            external_side_effect_allowed=external_side_effect_allowed,
            irreversible_allowed=irreversible_allowed,
        ),
        state=StateProvenance(
            input_hash=input_hash,
            memory_refs=memory_refs or [],
            prior_state_hash=prior_state_hash,
            current_state_hash=current_state_hash,
        ),
        risk=RiskProfile(
            reversibility_score=reversibility,
            blast_radius=risk_blast,
            secret_touching=False,
            human_ack_required=verdict in ("HOLD", "DENY") or irreversible_allowed,
        ),
        audit=AuditReceipt(
            vault_required=vault_required,
            audit_pointer=audit_pointer,
            seal_mode=seal_mode,
        ),
        verdict=verdict,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# arifOS self-attestation
# ═══════════════════════════════════════════════════════════════════════════════


def arif_os_attest(
    actor_id: str | None = None,
    session_id: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    arifOS organ.attest() implementation.

    Returns live attestation of the kernel: constitution hash, schema hash,
    tool surface, health, and active lease state. If attestation fails,
    status becomes DEGRADED_CLAIM and authority is revoked.
    """
    now = datetime.now(UTC).isoformat()

    # Gather registered tools from runtime surface if available
    tool_count = 0
    tool_names: list[str] = []
    try:
        from arifosmcp.constitutional_map import list_canonical_tools

        tool_names = sorted(list_canonical_tools())
        tool_count = len(tool_names)
    except Exception:
        pass

    # Constitution and envelope hashes
    constitution_hash = _load_constitution_hash()
    envelope_schema_hash = _load_envelope_schema_hash()

    # Health probe: identity file present and service active
    identity_ok = os.path.exists("/root/arifOS/identity.toml") or os.path.exists(
        "/opt/arifos/app/identity.toml"
    )

    status = "ALIVE"
    reason: str | None = None
    degraded = False

    if not identity_ok:
        status = "DEGRADED_CLAIM"
        reason = "Kernel identity file missing"
        degraded = True
    elif tool_count == 0:
        status = "DEGRADED_CLAIM"
        reason = "No canonical tools surfaced"
        degraded = True
    elif constitution_hash == "sha256:missing":
        status = "DEGRADED_CLAIM"
        reason = "Constitution file unavailable"
        degraded = True

    heartbeat = OrganHeartbeat(
        organ_id="arifOS",
        status=status,
        version=os.getenv("ARIFOS_DEPLOY_VERSION", "v2026.05.05-SSCT"),
        schema_hash=envelope_schema_hash,
        constitution_hash=constitution_hash,
        tool_count=tool_count,
        heartbeat_at=now,
        last_vault_seal="sha256:pending",  # Filled by vault organ
        degraded=degraded,
        reason=reason,
        load={
            "active_leases": 0,  # Placeholder until lease registry is wired
            "queued_tasks": 0,
            "failed_calls_5m": 0,
        },
    )
    try:
        from arifosmcp.runtime.heartbeat_registry import record_heartbeat

        record_heartbeat(
            organ_id="arifOS",
            status=status,
            version=heartbeat.version,
            schema_hash=envelope_schema_hash,
            constitution_hash=constitution_hash,
            tool_count=tool_count,
            degraded=degraded,
            reason=reason,
            load=heartbeat.load,
        )
    except Exception:
        pass

    envelope = LiveKernelEnvelope(
        kernel=KernelIdentity(
            session_id=session_id or "",
            actor_id=actor_id or "",
            constitution_hash=constitution_hash,
        ),
        organ=OrganAttestation(
            organ_id="arifOS",
            organ_role="constitutional_kernel",
            organ_version=heartbeat.version,
            tool_name="arif_os_attest",
            tool_schema_hash=envelope_schema_hash,
            attestation_status=status,
        ),
        authority=AuthorityLease(
            lease_id="LEASE-SELF-ATTEST",
            lease_scope=["attest", "observe"],
            action_class="OBSERVE",
        ),
        state=StateProvenance(
            input_hash=_sha256_of_text(
                json.dumps({"actor_id": actor_id, "session_id": session_id})
            ),
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
        verdict="SEAL" if not degraded else "DEGRADED",
    )

    return {
        "status": "OK" if not degraded else "DEGRADED",
        "tool": "arif_os_attest",
        "verdict": envelope.verdict,
        "result": {
            "heartbeat": heartbeat.model_dump(mode="json"),
            "envelope": envelope.model_dump(mode="json"),
        },
    }


__all__ = [
    "KernelIdentity",
    "OrganAttestation",
    "AuthorityLease",
    "StateProvenance",
    "RiskProfile",
    "AuditReceipt",
    "LiveKernelEnvelope",
    "OrganHeartbeat",
    "LeaseGrant",
    "arif_os_attest",
    "build_kernel_envelope",
]
