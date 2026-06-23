"""
ART Schema — Agentic Reliability & Trust (contract surface)

Pure Pydantic v2 contracts for the ART governed runtime bridge.
No behavior. No runtime imports. No execution path mutation.

These are the TARGET/ASPIRATIONAL contracts. Not all fields are
yet wired to runtime/art.py. Where a schema value has no current
runtime implementation, it is marked explicitly.

DITEMPA BUKAN DIBERI — Contracts are forged, not configured.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from arifosmcp.schemas.kernel_envelope import ActionClass

# ═══════════════════════════════════════════════════════════════════════
# TRUST BAND — confidence tier for tool reliability
# ═══════════════════════════════════════════════════════════════════════


class TrustBand(StrEnum):
    """Confidence tier for a tool's current reliability.

    Wired to: runtime/art.py ArtVerdict (trust_level field).
    """

    TRUST_HIGH = "TRUST_HIGH"
    TRUST_MEDIUM = "TRUST_MEDIUM"
    TRUST_LOW = "TRUST_LOW"
    TRUST_CRITICAL = "TRUST_CRITICAL"


# ═══════════════════════════════════════════════════════════════════════
# TOOL LIFECYCLE — state machine for tool trust over time
# ═══════════════════════════════════════════════════════════════════════


class ToolLifecycle(StrEnum):
    """TARGET/ASPIRATIONAL contract — NOT yet wired to runtime/art.py ToolState.

    Federation currently uses runtime/art.py ToolState with 5 values:
        UNTRUSTED → OBSERVED → TRUSTED → FALLBACK → ABANDONED

    This enum ADDS DEGRADED (6th state) as a migration target.
    DEGRADED awaits 888_HOLD ratification before wiring into
    pre_execution_gate.py. Until then, runtime/art.py ToolState
    is the authoritative lifecycle enumerator.

    Do NOT import from runtime in this module.
    Do NOT wire DEGRADED into gate logic without F13 approval.
    """

    UNTRUSTED = "UNTRUSTED"
    OBSERVED = "OBSERVED"
    TRUSTED = "TRUSTED"
    DEGRADED = "DEGRADED"  # TARGET — not yet in runtime/art.py ToolState
    FALLBACK = "FALLBACK"
    ABANDONED = "ABANDONED"


# ═══════════════════════════════════════════════════════════════════════
# ART VERDICT — what the reflex decides
# ═══════════════════════════════════════════════════════════════════════


class ArtVerdict(StrEnum):
    """Single reflex decision on a tool call.

    PROCEED — green, call the tool
    SABAR   — amber, proceed with caution (canary, dry-run required)
    HOLD    — yellow, pause for human review
    REJECT  — red, block the call
    """

    PROCEED = "PROCEED"
    SABAR = "SABAR"
    HOLD = "HOLD"
    REJECT = "REJECT"


# ═══════════════════════════════════════════════════════════════════════
# ART TOOL STATE — snapshot of a tool's trust posture
# ═══════════════════════════════════════════════════════════════════════


class ArtToolState(BaseModel):
    """Live trust snapshot for one tool.

    action_class uses the canonical ActionClass from kernel_envelope.py
    (OBSERVE / ANALYZE / DRAFT / SIMULATE / MUTATE /
     EXTERNAL_SIDE_EFFECT / IRREVERSIBLE).

    This is NOT BlastRadius (NONE / LOCAL / SYSTEM / INFRASTRUCTURE /
    CIVILIZATIONAL / UNKNOWN). Two axes, two purposes. BlastRadius
    quantifies scope-of-damage; ActionClass quantifies permission-level.
    ART consumes both through pre_execution_gate.py.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    tool_name: str
    provider: str | None = None
    version: str | None = None
    schema_hash: str | None = None

    lifecycle: ToolLifecycle
    trust_score: float = Field(ge=0.0, le=1.0)
    trust_band: TrustBand
    action_class: ActionClass

    success_90d: int = Field(default=0, ge=0)
    failure_90d: int = Field(default=0, ge=0)
    hold_90d: int = Field(default=0, ge=0)
    rollback_90d: int = Field(default=0, ge=0)

    last_failure_code: str | None = None
    last_verified_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════
# ART PRECHECK RESULT — what the reflex returns
# ═══════════════════════════════════════════════════════════════════════


class ArtPrecheckResult(BaseModel):
    """Result of one ART reflex invocation.

    required_act_pattern is a string matching ActPatternName values:
        "DEFAULT_DEPLOY" | "DANGEROUS_MIGRATION" | "HUMAN_IN_LOOP_CHANGE"
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    verdict: ArtVerdict
    tool_state: ArtToolState
    required_act_pattern: str

    reasons: list[str] = Field(default_factory=list)
    required_human_gate: bool = False
    required_canary: bool = False
    required_dry_run: bool = True
