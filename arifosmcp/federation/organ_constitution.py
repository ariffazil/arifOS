"""
arifosmcp/federation/organ_constitution.py
══════════════════════════════════════════════════════════════════════════════
Pydantic v2 schema for organ constitutions.

A constitution declares *what an organ believes, enforces, and refuses*. This
is the formal F2-auditable artifact for the AGI substrate — not /health JSON
(ad-hoc) but a typed, hashable, versionable document.

Constitutional layers:
  - Identity: organ_id, role, version
  - Authority: final authority, scope, what is refused, lease authority
  - Floors: which F1-F13 are enforced, with HARD/SOFT/DECLARED tier
  - Boundaries: what the organ does NOT do (constitutional restraint)
  - Evidence: canonical text hash + path, sealed timestamp

Design notes:
  - extra='forbid' (F2-honest: unknown fields are an error, not silent pass)
  - Pydantic v2 strict types (F10 ONTOLOGY: no type drift)
  - Tier defaults to YELLOW (F7 HUMILITY: do not claim GREEN without evidence)
  - canonical_text_hash is required and is the integrity anchor

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Tier = Literal["GREEN", "YELLOW", "RED", "BLACK"]
FloorEnforcement = Literal["HARD", "SOFT", "DECLARED", "UNENFORCED"]


class ConstitutionalFloor(BaseModel):
    """One F1-F13 floor and how this organ enforces it."""

    model_config = ConfigDict(extra="forbid")

    floor_id: str = Field(..., pattern=r"^F0[1-9]|F1[0-3]$")
    name: str
    enforcement: FloorEnforcement
    threshold: float | None = None
    notes: str | None = None


class OrganAuthority(BaseModel):
    """Who has final say, and what the organ can refuse."""

    model_config = ConfigDict(extra="forbid")

    final_authority: str  # "ARIF" | "REFLECT_ONLY" | "DELEGATED_TO_KERNEL"
    scope: list[str] = Field(default_factory=list)
    refuses: list[str] = Field(default_factory=list)  # e.g. "no buy/sell oracle"
    leases: list[str] = Field(default_factory=list)  # action classes


class OrganBoundaries(BaseModel):
    """Constitutional restraint — what this organ will NOT do."""

    model_config = ConfigDict(extra="forbid")

    does_not: list[str] = Field(default_factory=list)
    requires_sovereign_ack: list[str] = Field(default_factory=list)
    floor_violations: list[str] = Field(default_factory=list)


class OrganConstitution(BaseModel):
    """A single organ's full constitutional surface — typed, hashable, versioned."""

    model_config = ConfigDict(extra="forbid")

    organ_id: str = Field(..., min_length=1, max_length=64)
    version: str = Field(..., min_length=1, max_length=32)
    role: str
    domain: str  # "earth_intelligence" | "capital_intelligence" | ...

    authority: OrganAuthority
    floors: list[ConstitutionalFloor] = Field(default_factory=list)
    boundaries: OrganBoundaries = Field(default_factory=OrganBoundaries)

    # Evidence — the integrity anchor
    canonical_text_hash: str  # sha256:<hex> of the constitution source text
    canonical_text_path: str | None = None
    sealed_at: datetime | None = None
    last_verified: datetime | None = None

    # Tier — computed from promotion gates (NOT user-asserted)
    tier: Tier = "YELLOW"  # F7 HUMILITY: never default to GREEN
    tier_conditions: list[str] = Field(default_factory=list)

    @field_validator("canonical_text_hash")
    @classmethod
    def _validate_hash_format(cls, v: str) -> str:
        if v == "sha256:missing":
            return v  # explicitly allowed for honest missing
        if v == "sha256:unavailable":
            return v
        if not (v.startswith("sha256:") and len(v) == 7 + 64):
            raise ValueError(f"canonical_text_hash must be sha256:<64hex>, got: {v[:40]}")
        return v

    @property
    def floor_signature(self) -> str:
        """Concise floor ID list — e.g. 'F01,F02,F11,F13'."""
        return ",".join(f.floor_id for f in sorted(self.floors, key=lambda x: x.floor_id))

    @property
    def hard_floors(self) -> list[str]:
        return [f.floor_id for f in self.floors if f.enforcement == "HARD"]

    @property
    def is_sovereign_bound(self) -> bool:
        """True if any action requires 888 sovereign ack."""
        return self.authority.final_authority == "ARIF" or bool(
            self.boundaries.requires_sovereign_ack
        )

    def to_canonical_json(self) -> str:
        """Deterministic JSON for hashing. Used by aggregator to compute
        federation_constitution_hash."""
        import json

        return json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))


# ═════════════════════════════════════════════════════════════════════════════
# Loaders — read organ constitutions from filesystem / live data
# ═════════════════════════════════════════════════════════════════════════════


def _sha256_of_file(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return f"sha256:{hashlib.sha256(f.read()).hexdigest()}"
    except Exception:
        return "sha256:unavailable"


def _sha256_of_text(text: str) -> str:
    return f"sha256:{hashlib.sha256(text.encode()).hexdigest()}"


# ═════════════════════════════════════════════════════════════════════════════
# Per-organ constitution templates
# These are the EXPLICIT constitutional declarations for the 6 known organs.
# They are NOT inferred from /health JSON — they are sovereign-ratified
# defaults that can be overridden by direct attestation.
# ═════════════════════════════════════════════════════════════════════════════

from typing import Any  # noqa: E402  — placed here to keep template grouping


_ORGAN_CONSTITUTION_TEMPLATES: dict[str, dict[str, Any]] = {
    "arifOS": {
        "organ_id": "arifOS",
        "version": "kanon-2026.06.13",
        "role": "constitutional_kernel",
        "domain": "governance",
        "authority": {
            "final_authority": "ARIF",
            "scope": ["governance", "judgment", "verdict", "seal", "lease"],
            "refuses": [
                "no autonomy for irreversible actions without 888",
                "no SEAL on falsifiable claims without evidence",
                "no consciousness/feelings/soul claims (F9/F10)",
            ],
            "leases": ["OBSERVE", "REASON", "JUDGE", "SEAL", "FORGE"],
        },
        "floors": [
            {"floor_id": f"F0{i}", "name": n, "enforcement": "HARD"}
            for i, n in enumerate(
                [
                    "AMANAH",
                    "TRUTH",
                    "WITNESS",
                    "CLARITY",
                    "PEACE",
                    "EMPATHY",
                    "HUMILITY",
                    "GENIUS",
                    "ANTIHANTU",
                    "ONTOLOGY",
                    "AUTH",
                    "INJECTION",
                    "SOVEREIGN",
                ],
                start=1,
            )
        ],
        "boundaries": {
            "does_not": [
                "issue SEAL on falsifiable claims without evidence_receipt",
                "mutate VAULT999 without actor_signature",
                "act as buy/sell oracle (delegated to WEALTH)",
                "issue medical/diagnostic claims (delegated to WELL)",
                "interpret seismic data (delegated to GEOX)",
            ],
            "requires_sovereign_ack": [
                "vault_seal (irreversible)",
                "forge_execute (irreversible)",
                "judge_deliberate (final verdict)",
                "constitutional_file_mutation",
            ],
            "floor_violations": [
                "no bare SEAL (always namespaced: KERNEL_SEAL/DOMAIN_SEAL/JUDGE_SEAL/VAULT_SEAL)",
                "no certainty band below omega_0=0.03 or above 0.05 (F7)",
            ],
        },
        "constitution_candidates": [
            "/root/arifOS/GENESIS/000_KERNEL_CANON.md",
            "/opt/arifos/app/GENESIS/000_KERNEL_CANON.md",
        ],
    },
    "GEOX": {
        "organ_id": "GEOX",
        "version": "v2026.05.27",
        "role": "earth_intelligence",
        "domain": "subsurface_evidence",
        "authority": {
            "final_authority": "ARIF",
            "scope": ["earth_evidence", "claim_seal", "subsurface_reasoning"],
            "refuses": [
                "no buy/sell recommendations",
                "no medical/biological claims",
                "no SEAL on unverified subsurface claims (Physics9 first)",
            ],
            "leases": ["OBSERVE", "REASON", "SEAL"],
        },
        "floors": [
            {"floor_id": "F02", "name": "TRUTH", "enforcement": "HARD"},
            {"floor_id": "F04", "name": "CLARITY", "enforcement": "SOFT"},
            {"floor_id": "F07", "name": "HUMILITY", "enforcement": "SOFT"},
        ],
        "boundaries": {
            "does_not": [
                "issue drilling/reserves/development decisions (888 required)",
                "fabricate physics (Physics9 hard lock)",
                "claim FACT without direct observation (F2)",
            ],
            "requires_sovereign_ack": [
                "claim_seal (irreversible)",
                "prospect_evaluate mode=develop",
            ],
        },
        "constitution_candidates": [
            "/root/geox/GENESIS/000_KERNEL_CANON.md",
            "/opt/geox/app/GENESIS/000_KERNEL_CANON.md",
            "/root/geox/GENESIS/000_MANIFESTO.md",
        ],
    },
    "WEALTH": {
        "organ_id": "WEALTH",
        "version": "2026.05.02",
        "role": "capital_intelligence",
        "domain": "capital_evidence",
        "authority": {
            "final_authority": "ARIF",
            "scope": ["capital_evidence", "deal_framing", "survival_synthesis"],
            "refuses": [
                "no buy/sell oracle (computes, Arif decides)",
                "no default-rich-synthesis on insufficient input",
                "no engagement metrics (operator sovereignty preserved)",
            ],
            "leases": ["OBSERVE", "REASON", "COMPUTE"],
        },
        "floors": [
            {"floor_id": "F02", "name": "TRUTH", "enforcement": "HARD"},
            {"floor_id": "F04", "name": "CLARITY", "enforcement": "SOFT"},
            {"floor_id": "F09", "name": "ANTIHANTU", "enforcement": "HARD"},
        ],
        "boundaries": {
            "does_not": [
                "execute trades (recommendation_only)",
                "fabricate alpha claims",
                "act as final authority on capital (Arif decides)",
            ],
            "requires_sovereign_ack": [
                "any capital action with > RM 100k exposure",
                "any SEAL on capital claim that triggers downstream execution",
            ],
        },
        "constitution_candidates": [
            "/root/WEALTH/canon/000_KERNEL_CANON.md",
            "/opt/wealth/app/canon/000_KERNEL_CANON.md",
        ],
    },
    "WELL": {
        "organ_id": "WELL",
        "version": "v2026.05.15",
        "role": "human_readiness",
        "domain": "substrate_signal",
        "authority": {
            "final_authority": "REFLECT_ONLY",  # F6 EMPATHY hard line
            "scope": ["readiness_signals", "vitality_reflection", "decision_class"],
            "refuses": [
                "no medical/diagnostic claims",
                "no therapy/coaching",
                "no engagement metrics (lowest stakeholder protected)",
                "no medical authority (Arif/medical professional decides)",
            ],
            "leases": ["OBSERVE", "REFLECT"],
        },
        "floors": [
            {"floor_id": "F02", "name": "TRUTH", "enforcement": "HARD"},
            {"floor_id": "F06", "name": "EMPATHY", "enforcement": "HARD"},
            {"floor_id": "F09", "name": "ANTIHANTU", "enforcement": "HARD"},
        ],
        "boundaries": {
            "does_not": [
                "diagnose (medical professional territory)",
                "prescribe (medical professional territory)",
                "claim to know better than the human (REFLECT_ONLY)",
            ],
            "requires_sovereign_ack": [
                "any change to well_score that triggers downstream action",
            ],
        },
        "constitution_candidates": [
            "/root/WELL/GENESIS/000_KERNEL_CANON.md",
            "/opt/well/app/GENESIS/000_KERNEL_CANON.md",
            "/root/WELL/GENESIS/004_WELL_13_CANON.md",
        ],
    },
    "A-FORGE": {
        "organ_id": "A-FORGE",
        "version": "0.1.0",
        "role": "execution_shell",
        "domain": "build_deploy",
        "authority": {
            "final_authority": "ARIF",
            "scope": ["build", "deploy", "code_mode", "federation_memory"],
            "refuses": [
                "no execution without JUDGE_SEAL_AUTHORIZATION",
                "no mutation outside authorized scope",
            ],
            "leases": ["BUILD", "DEPLOY"],
        },
        "floors": [
            {"floor_id": "F01", "name": "AMANAH", "enforcement": "HARD"},
            {"floor_id": "F11", "name": "AUTH", "enforcement": "HARD"},
            {"floor_id": "F13", "name": "SOVEREIGN", "enforcement": "HARD"},
        ],
        "boundaries": {
            "does_not": [
                "execute without JUDGE_SEAL",
                "modify constitutional files",
                "exfiltrate secrets",
            ],
            "requires_sovereign_ack": [
                "any production deploy",
                "any constitutional file mutation",
            ],
        },
        "constitution_candidates": [],  # A-FORGE has no GENESIS/ yet
    },
    "AAA": {
        "organ_id": "AAA",
        "version": "1.0.0",
        "role": "control_plane",
        "domain": "a2a_mesh",
        "authority": {
            "final_authority": "ARIF",
            "scope": ["a2a_mesh", "cockpit", "vault_bridge"],
            "refuses": [
                "no adjudication (display only, never judge)",
                "no execution without kernel authorization",
            ],
            "leases": ["DISPLAY", "ROUTE"],
        },
        "floors": [
            {"floor_id": "F01", "name": "AMANAH", "enforcement": "HARD"},
            {"floor_id": "F11", "name": "AUTH", "enforcement": "HARD"},
        ],
        "boundaries": {
            "does_not": [
                "adjudicate (governance belongs to arifOS)",
                "execute (build belongs to A-FORGE)",
                "interpret (reality belongs to GEOX/WEALTH/WELL)",
            ],
            "requires_sovereign_ack": [
                "any change to control plane surface",
            ],
        },
        "constitution_candidates": [],
    },
}


def load_organ_constitution(organ_id: str) -> OrganConstitution:
    """Load an organ's constitution from the template + filesystem hash.

    Returns a Pydantic-validated OrganConstitution. If the constitution file is
    missing, the canonical_text_hash will be 'sha256:missing' and the tier
    defaults to YELLOW (F2-honest: we don't claim GREEN without evidence).
    """
    template = _ORGAN_CONSTITUTION_TEMPLATES.get(organ_id)
    if template is None:
        raise ValueError(f"Unknown organ_id: {organ_id}")

    # Resolve canonical_text_hash from filesystem candidates
    canonical_hash = "sha256:missing"
    canonical_path = None
    for p in template.get("constitution_candidates", []):
        if os.path.exists(p):
            canonical_hash = _sha256_of_file(p)
            canonical_path = p
            break

    # Build the constitution
    return OrganConstitution(
        organ_id=template["organ_id"],
        version=template["version"],
        role=template["role"],
        domain=template["domain"],
        authority=template["authority"],
        floors=[ConstitutionalFloor(**f) for f in template["floors"]],
        boundaries=OrganBoundaries(**template["boundaries"]),
        canonical_text_hash=canonical_hash,
        canonical_text_path=canonical_path,
        last_verified=datetime.now(UTC).isoformat() if canonical_hash != "sha256:missing" else None,
    )


def list_known_organs() -> list[str]:
    """Return the list of organs with declared constitutions."""
    return list(_ORGAN_CONSTITUTION_TEMPLATES.keys())
