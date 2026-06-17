"""
Peer Federation Contract v1 — Canonical Pydantic schema.

Governed P2P capability contract for the arifOS Federation.
P2P is valid only as capability-peering, never authority-peering.
arifOS alone holds judge authority; Arif/F13 veto is absolute and non-delegable.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class AuthorityClass(StrEnum):
    """Constitutional authority class for a federation peer."""

    EVIDENCE = "evidence"
    ADVISORY = "advisory"
    ROUTE = "route"
    EXECUTE = "execute"
    JUDGE = "judge"


class PeerId(BaseModel):
    """Stable identity of a federation peer."""

    organ: str = Field(
        description="Canonical organ name (arifOS, AAA, A-FORGE, GEOX, WEALTH, WELL, ...)"
    )
    instance_id: UUID = Field(description="UUID instance identifier")
    did: str = Field(
        ...,
        pattern=r"^did:arifos:[a-z0-9_-]+$",
        description="Decentralized identifier in did:arifos namespace",
    )
    public_key_fingerprint: str = Field(
        min_length=16,
        description="Fingerprint of the peer's public signing key",
    )


class CapabilityCard(BaseModel):
    """Honest capability card advertised by the peer."""

    schema_hash: str = Field(min_length=8, description="Hash of the contract schema")
    constitution_hash: str | None = Field(
        default=None,
        description="Hash of the constitutional canon the peer binds to",
    )
    tool_manifest_url: HttpUrl = Field(
        description="URL of the peer's canonical tool manifest"
    )
    allowed_action_classes: list[
        Literal["OBSERVE", "PREPARE", "MUTATE", "ATOMIC"]
    ] = Field(min_length=1, description="Action classes the peer may accept")
    max_risk_tier: Literal["T0", "T1", "T2", "T3", "T4", "T5"] = Field(
        description="Maximum risk tier this peer may operate under"
    )
    skills: list[str] = Field(default_factory=list, description="Bound skill names")


class AcceptedInput(BaseModel):
    """Input schema accepted by the peer."""

    schema_id: str = Field(description="Canonical schema identifier")
    schema_url: HttpUrl = Field(description="URL of the schema definition")


class AuditSink(BaseModel):
    """Where peer actions must be logged."""

    vault999_endpoint: HttpUrl = Field(description="VAULT999 seal endpoint")
    receipt_format: Literal["arifos_vault999_v2"] = Field(
        default="arifos_vault999_v2",
        description="Canonical receipt format",
    )
    nats_subject: str | None = Field(
        default=None,
        description="Optional NATS subject for real-time audit events",
    )


class OverridePath(BaseModel):
    """Channel for F13 override."""

    channel: Literal["telegram", "a2a_task", "mcp_tool", "voice"] = Field(
        description="Human override channel"
    )
    endpoint: str = Field(description="Endpoint or route identifier")


class HumanVeto(BaseModel):
    """Human veto configuration — F13 absolute is non-negotiable."""

    f13_absolute: Literal[True] = Field(
        description="F13 sovereign veto is absolute and non-delegable"
    )
    override_paths: list[OverridePath] = Field(
        default_factory=list,
        description="Available human override channels",
    )


class SignedAttestation(BaseModel):
    """Attestation issued by arifOS 888 JUDGE."""

    issuer: Literal["arifOS-888-JUDGE"] = Field(
        description="Only arifOS 888 JUDGE may issue"
    )
    signature: str = Field(description="Ed25519 signature stub pending F13 ratification")
    issued_at: datetime = Field(description="ISO 8601 issuance timestamp")
    expires_at: datetime = Field(description="ISO 8601 expiry timestamp")


class PeerFederationContract(BaseModel):
    """Governed P2P Federation Contract v1."""

    contract_version: Literal["1.0.0"] = Field(
        default="1.0.0",
        description="Contract schema version",
    )
    peer_id: PeerId = Field(description="Peer identity")
    authority_class: AuthorityClass = Field(
        description="Constitutional authority class of this peer"
    )
    capability_card: CapabilityCard = Field(description="Capability card")
    lease_required: bool = Field(
        description="Whether the peer requires a bounded lease to operate"
    )
    reversibility_score: float = Field(
        ge=0.0,
        le=1.0,
        description="0 = irreversible actions possible, 1 = fully reversible",
    )
    accepted_inputs: list[AcceptedInput] = Field(
        default_factory=list,
        description="Input schemas the peer accepts",
    )
    forbidden_actions: list[str] = Field(
        min_length=1,
        description="Actions explicitly forbidden by this peer",
    )
    audit_sink: AuditSink = Field(description="Audit sink configuration")
    human_veto: HumanVeto = Field(description="Human veto configuration")
    trust_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional trust score computed by arifOS",
    )
    signed_attestation: SignedAttestation | None = Field(
        default=None,
        description="arifOS 888 JUDGE attestation",
    )

    @property
    def organ(self) -> str:
        return self.peer_id.organ

    def model_dump_for_hash(self) -> dict[str, Any]:
        """Dump a deterministic, JSON-serializable dict for hashing."""
        return self.model_dump(mode="json", sort_keys=True)


__all__ = [
    "AuthorityClass",
    "PeerId",
    "CapabilityCard",
    "AcceptedInput",
    "AuditSink",
    "OverridePath",
    "HumanVeto",
    "SignedAttestation",
    "PeerFederationContract",
]
