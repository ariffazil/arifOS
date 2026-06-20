"""
Canonical Swarm Ignition Schemas — Pydantic v2

DITEMPA BUKAN DIBERI — Forged, Not Given.

5 canonical objects for the AGI-level swarm ignition protocol:
  1. BootReceipt          — one agent joining the swarm
  2. SwarmManifest        — whole-federation living state
  3. CapabilityAttestation — organ-attested tool capability
  4. SwarmLease           — time-limited, scope-limited autonomy grant
  5. ReIgnitionReceipt    — cold-start reconstruction record
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from hashlib import sha256
from typing import Any

from pydantic import BaseModel, Field, field_validator

# ── Enums ──────────────────────────────────────────────────────────


class SwarmStatus(str, Enum):
    WARM = "WARM"
    COLD = "COLD"
    DEGRADED = "DEGRADED"
    QUARANTINED = "QUARANTINED"


class ActionClass(str, Enum):
    OBSERVE = "OBSERVE"
    DRAFT = "DRAFT"
    DRY_RUN = "DRY_RUN"
    MUTATE = "MUTATE"
    ATOMIC = "ATOMIC"


class SideEffectClass(str, Enum):
    OBSERVE = "OBSERVE"
    MUTATE = "MUTATE"
    ATOMIC = "ATOMIC"


class ReIgnitionTrigger(str, Enum):
    NEW_AGENT_INIT = "new_agent_init"
    LEASE_EXPIRED = "lease_expired"
    CRASH_DETECTED = "crash_detected"


class BootMode(str, Enum):
    COLD = "cold"
    WARM = "warm"
    RECOVERY = "recovery"
    HANDOFF = "handoff"


class AgentRole(str, Enum):
    SCOUT = "SCOUT"
    MIND = "MIND"
    HEART = "HEART"
    FORGE_HOLDER = "FORGE_HOLDER"
    VAULT_WITNESS = "VAULT_WITNESS"
    GATEWAY_RELAY = "GATEWAY_RELAY"
    JUDGE_PROXY = "JUDGE_PROXY"


# ── Hash utility ──────────────────────────────────────────────────


def stable_hash(payload: dict[str, Any]) -> str:
    """Deterministic SHA-256 hash of a JSON-serializable dict."""
    import json

    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + sha256(encoded).hexdigest()


# ── 1. BootReceipt ────────────────────────────────────────────────


class AgentState(BaseModel):
    """Minimal visible agent state in the swarm."""

    agent_id: str
    status: str = "ACTIVE"
    lease_id: str | None = None
    current_task_hash: str | None = None
    last_receipt_hash: str | None = None
    trusted_because: str = "VAULT999_SEAL"


class BootReceipt(BaseModel):
    """Canonical receipt when one agent joins the swarm."""

    agent_id: str
    session_id: str
    epoch_id: str | None = None
    constitution_hash: str
    boot_mode: BootMode = BootMode.COLD
    agent_role: AgentRole = AgentRole.SCOUT
    joined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    max_action_class: ActionClass = ActionClass.OBSERVE
    lease_ids: list[str] = []
    capability_claims: list[str] = []
    capability_attestations: list[str] = []
    swarm_context_loaded: bool = False
    sovereign_required: bool = True
    boot_hash: str = ""

    @field_validator("boot_hash", mode="before")
    @classmethod
    def _empty_boot_hash(cls, v: str | None) -> str:
        return v if v else "pending"

    def compute_hash(self) -> str:
        payload = self.model_dump(exclude={"boot_hash"})
        return stable_hash(payload)


# ── 2. SwarmManifest ──────────────────────────────────────────────


class OrganState(BaseModel):
    """Visible organ state in the swarm."""

    organ: str
    status: str = "UNKNOWN"
    attested_tools: int = 0
    max_action_class: str = "OBSERVE"
    constitution_hash: str | None = None
    capability_hash: str | None = None
    expires_at: datetime | None = None


class TaskState(BaseModel):
    """Visible task state in the swarm."""

    task_id: str
    description: str = ""
    status: str = "PENDING"
    holder: str | None = None
    last_seal_hash: str | None = None
    created_at: datetime | None = None


class HoldState(BaseModel):
    """Active HOLD conditions in the swarm."""

    hold_id: str
    reason: str = ""
    source: str = ""
    created_at: datetime | None = None


class SwarmManifest(BaseModel):
    """Canonical whole-federation swarm manifest — the living boot object."""

    type: str = "SwarmIgnitionManifest"
    version: str = "VAULT999.swarm.ignite.v1"
    epoch_id: str | None = None
    constitution_hash: str
    federation_hash: str = ""
    last_seal_hash: str | None = None

    swarm_state: dict[str, Any] = Field(
        default_factory=lambda: {
            "status": SwarmStatus.COLD.value,
            "active_agents": [],
            "active_organs": [],
            "active_leases": [],
            "open_tasks": [],
            "blocked_tasks": [],
            "last_known_good_state": None,
        }
    )

    capability_graph: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)

    memory_surface: dict[str, Any] = Field(
        default_factory=lambda: {
            "federation_context_hash": None,
            "visible_to_new_agents": True,
            "private_memory_excluded": True,
        }
    )

    rules: dict[str, Any] = Field(
        default_factory=lambda: {
            "self_authority": False,
            "capability_self_claim_forbidden": True,
            "lease_required_for_action": True,
            "irreversible_action_requires_arif": True,
            "cold_reignition_source": "VAULT999",
        }
    )

    agents: dict[str, AgentState] = Field(default_factory=dict)
    organs: dict[str, OrganState] = Field(default_factory=dict)
    capabilities: list[dict[str, Any]] = Field(default_factory=list)
    leases: list[dict[str, Any]] = Field(default_factory=list)
    tasks: list[dict[str, Any]] = Field(default_factory=list)
    holds: list[dict[str, Any]] = Field(default_factory=list)

    recursive_init: dict[str, Any] = Field(
        default_factory=lambda: {
            "depth": 1,
            "max_depth": 3,
            "gaps": [],
            "next_safe_action": "OBSERVE_ONLY",
        }
    )

    manifest_hash: str = ""

    def compute_hash(self) -> str:
        payload = self.model_dump(exclude={"manifest_hash"})
        return stable_hash(payload)


# ── 3. CapabilityAttestation ──────────────────────────────────────


class CapabilityAttestation(BaseModel):
    """Organ-attested tool capability. Agent self-claim is inadmissible."""

    organ: str
    tool: str
    schema_hash: str | None = None
    implementation_hash: str | None = None
    side_effect_class: SideEffectClass = SideEffectClass.OBSERVE
    roots_required: list[str] = []
    network_required: bool = False
    secret_touching: bool = False
    default_gate: str = "DRY_RUN_FIRST"
    attested_by: str
    valid_until: datetime | None = None


# ── 4. SwarmLease ─────────────────────────────────────────────────


class SwarmLease(BaseModel):
    """Time-limited, scope-limited autonomy grant. Not a right."""

    lease_id: str
    holder: str
    resource: str  # "FORGE", "GATEWAY", "VAULT", "GEOX", "WEALTH", "WELL"
    scope: list[str] = ["observe"]
    ttl_seconds: int = 900
    cannot_delegate: bool = True
    cannot_expand_scope: bool = True
    expires_at: datetime | None = None
    policy: str = "no_parallel_mutation_without_explicit_judge"

    def is_active(self) -> bool:
        if not self.expires_at:
            return False
        now = datetime.now(UTC)
        return self.expires_at > now


# ── 5. ReIgnitionReceipt ──────────────────────────────────────────


class ReIgnitionReceipt(BaseModel):
    """Cold-start reconstruction record. No autonomous mutation."""

    trigger: ReIgnitionTrigger = ReIgnitionTrigger.NEW_AGENT_INIT
    cold_state_detected: bool = False
    source: str = "VAULT999"
    last_known_good_state: str | None = None
    restored_manifest_hash: str | None = None
    mutations_performed: list[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
