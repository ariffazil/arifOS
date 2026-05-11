from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from .geox_schemas import CoordinatePoint, ProvenanceRecord

# ═══════════════════════════════════════════════════════════════════════════════
# 1. GEOX WELL MODEL
# ═══════════════════════════════════════════════════════════════════════════════


class GeoxWell(BaseModel):
    """Grounded representation of a borehole / well log."""

    well_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Unique well name (e.g. PM3-X1).")
    location: CoordinatePoint

    kb_elevation_m: float = Field(..., description="Kelly Bushing elevation.")
    total_depth_m: float = Field(..., description="Total depth reached (TVD).")

    logs_available: List[str] = Field(
        default_factory=list, description="List of log pneumonics (GR, DT, NPHI, etc.)."
    )
    las_file_path: Optional[str] = None

    provenance: ProvenanceRecord


# ═══════════════════════════════════════════════════════════════════════════════
# 2. EVIDENCE BUNDLE (Earth Witness)
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceBundle(BaseModel):
    """A collection of multi-modal evidence supporting an interpretation."""

    bundle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str

    seismic_refs: List[str] = Field(
        default_factory=list, description="Refs to seismic lines/volumes."
    )
    well_refs: List[str] = Field(default_factory=list, description="Refs to well IDs.")
    literature_refs: List[str] = Field(default_factory=list)

    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    verdict: str = "QUALIFY"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. GEOX PROJECT (The Spine)
# ═══════════════════════════════════════════════════════════════════════════════


class GeoxProject(BaseModel):
    """The top-level workstation project container for GEOX."""

    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Human-readable project name.")
    basin: str = Field(..., description="Regional basin context.")

    wells: List[GeoxWell] = Field(default_factory=list)
    evidence_bundles: List[EvidenceBundle] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    meta: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


class GeoxSession(BaseModel):
    """A runtime session for a specific geologist or agent interaction."""

    session_id: str = Field(..., description="Canonical arifOS Session ID.")
    active_project_id: Optional[str] = None

    actor_persona: str = "geologist"  # analyst | exploration_manager | subagent
    stage: str = "EXPLORATION"

    history: List[dict[str, Any]] = Field(default_factory=list)
