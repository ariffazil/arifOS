"""Constitutional Reality schema — L2 verified state of F1-F13 implementation.

This schema models the gap between what the 000_CONSTITUTION.md claims and
what can be verified on the live system. It is intentionally mechanical:
no consciousness, no feelings, no hantu. Just claims, evidence, and deltas.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvidenceRef(BaseModel):
    """A pointer to a piece of evidence plus how it was checked."""

    path: str
    "Filesystem path, URL, or command that produced the evidence."
    method: str
    "How the evidence was obtained: read, curl, grep, sha256sum, journalctl, ..."
    value: str | None = None
    "Key extracted value, hash, or short snippet."
    verified_at: str | None = None
    "ISO timestamp of verification."


class FloorReality(BaseModel):
    """Implementation status of one constitutional floor."""

    floor_id: str
    "Canonical id: F01, F02, ..., F13 or L01-L13."
    name: str
    "Human-readable name, e.g. AMANAH, TRUTH, SOVEREIGN."
    type: str
    "HARD | SOFT | DERIVED."
    constitutional_claim: str
    "What the constitution says this floor guarantees."
    enforcement_code: list[str] = Field(default_factory=list)
    "Functions/classes that implement the check."
    evidence: list[EvidenceRef] = Field(default_factory=list)
    "Evidence that the floor exists in code or config."
    spec_value: str | None = None
    "The threshold/spec from the constitution."
    measured_value: str | None = None
    "What live probes actually measure."
    status: str
    "IMPLEMENTED | PARTIAL | GAP | UNVERIFIED | NOT_APPLICABLE."
    notes: str = ""
    "Human-readable delta explanation."


class OrganReality(BaseModel):
    """Observed state of one federation organ."""

    organ_id: str
    role: str
    localhost_url: str | None = None
    public_url: str | None = None
    expected_tools: int | None = None
    live_tools: int | None = None
    health_status: str | None = None
    reachable: bool | None = None
    latency_ms: float | None = None
    verdict: str
    "PASS | DEGRADED | FAIL | UNKNOWN."
    notes: str = ""


class CrossCheck(BaseModel):
    """A single claim-versus-reality contrast."""

    id: str
    claim: str
    source: str
    measured: str
    status: str
    "MATCH | MISMATCH | PARTIAL | UNVERIFIED."
    floors: list[str] = Field(default_factory=list)
    "Related floor ids."


class ConstitutionalGap(BaseModel):
    """A delta between constitutional intent and operational reality."""

    id: str
    severity: str
    "critical | high | medium | low."
    domain: str
    description: str
    related_floors: list[str] = Field(default_factory=list)
    evidence: list[EvidenceRef] = Field(default_factory=list)


class ConstitutionalRealityReport(BaseModel):
    """Top-level report: constitution intent versus verified reality."""

    report_id: str
    generated_at: str
    generator: str
    constitution_source: EvidenceRef
    "The constitution file that is the source of truth."
    overall_verdict: str
    "GREEN | GREEN_WITH_GAPS | YELLOW | RED."
    summary: str = ""
    floors: list[FloorReality] = Field(default_factory=list)
    organs: list[OrganReality] = Field(default_factory=list)
    cross_checks: list[CrossCheck] = Field(default_factory=list)
    gaps: list[ConstitutionalGap] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "forbid"}
