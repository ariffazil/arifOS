"""
arifosmcp/memory/admissibility.py
=================================

SRO v1 read gate — memory admissibility policy engine.

Companion to the WRITE policy (policies.py governs what may be written and
promoted; the Memory Promotion Gate governs what deserves to be remembered).
This module governs the READ side: what may be RECALLED, in which mode, and
with what labels. A store that is written but never gated is an archive; an
archive that answers operational questions is a liar.

Policy SOT: config/memory-admissibility-policy.yaml (versioned in-repo).
Every memory client in the federation consumes the same file so admissibility
semantics never fork:

    kernel vector layer (vector_memory_qdrant)   ← wired
    runtime memory_store.search                  ← open loop, same gate module
    memory/cognitive_memory.graph_query          ← open loop, same gate module
    A-FORGE forge_memory (TS)                    ← open loop, same YAML SOT
    S4 temporal ingestion (Graphiti)             ← future consumer

SRO schema on a Qdrant point (payload.sro):
    sro_version: 1
    supersession: {supersedes, superseded_by, supersession_reason, supersession_date}
    expiry: {expires_at, review_by, status}   # ACTIVE | STALE | EXPIRED | SUPERSEDED
    calibration: {confidence_at_creation, outcome_observed, outcome_date, calibration_error}
    sro_migrated_at: ISO-8601

Uniform schema ≠ uniform truth: an EXPIRED record is structurally valid and
still not admissible for operational recall. This gate is the boundary
between those two statements.

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

POLICY_PATH = Path(__file__).resolve().parents[2] / "config" / "memory-admissibility-policy.yaml"
ENV_OVERRIDE = "MEMORY_ADMISSIBILITY_POLICY"

# Fail-safe defaults — identical semantics to the shipped YAML default mode.
# Used ONLY when the policy file is missing or unparseable, so recall degrades
# to the strictest sensible gate instead of erroring or opening the floodgates.
# A loud logger.error accompanies every fallback (shadow acknowledged, never silent).
_FAILSAFE_POLICY: dict[str, Any] = {
    "api_version": "arifos.memory_admissibility.v1",
    "policy_version": 0,
    "sro_schema_version": 1,
    "status_vocabulary": ["ACTIVE", "STALE", "EXPIRED", "SUPERSEDED"],
    "expiry_defaults_days": {"OBS": 365, "DER": 180, "INT": 90, "SPEC": 30},
    "temporal": {"enforce_expires_at": True},
    "modes": {
        "default": {
            "admit_statuses": ["ACTIVE"],
            "permit_superseded": False,
            "min_confidence": None,
        },
        "historical": {
            "admit_statuses": ["ACTIVE", "STALE", "EXPIRED", "SUPERSEDED"],
            "permit_superseded": True,
            "min_confidence": None,
            "label": "HISTORICAL",
        },
    },
}

_VALID_TRUTH_CLASSES = {"OBS", "DER", "INT", "SPEC"}


@dataclass(frozen=True)
class AdmissibilityDecision:
    """One point's read-gate verdict.

    admitted=False always carries a reason_code from the policy's
    refusal.reason_codes vocabulary; the caller must surface the counts
    (refusal.silent: false — Void Guard).
    """

    admitted: bool
    reason_code: str | None
    effective_status: str | None
    label: str | None


def load_policy(path: str | Path | None = None) -> dict[str, Any]:
    """Load the admissibility policy YAML.

    Resolution order: explicit path → MEMORY_ADMISSIBILITY_POLICY env →
    in-repo config/memory-admissibility-policy.yaml. On missing/unparseable
    file, logs loudly and returns the fail-safe default policy (same
    semantics as the shipped default mode). Recall never raises from policy
    IO; it degrades strict.
    """
    if path is None:
        env = os.environ.get(ENV_OVERRIDE)
        path = Path(env) if env else POLICY_PATH
    p = Path(path)
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.error(
            "admissibility policy NOT FOUND at %s — using fail-safe default policy. "
            "Restore config/memory-admissibility-policy.yaml.", p)
        return dict(_FAILSAFE_POLICY)
    except yaml.YAMLError as exc:
        logger.error(
            "admissibility policy at %s is unparseable (%s) — using fail-safe "
            "default policy. Fix the YAML; do not ignore this.", p, exc)
        return dict(_FAILSAFE_POLICY)
    if not isinstance(raw, dict) or "modes" not in raw or "status_vocabulary" not in raw:
        logger.error(
            "admissibility policy at %s lacks modes/status_vocabulary — using "
            "fail-safe default policy.", p)
        return dict(_FAILSAFE_POLICY)
    return raw


def _parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def compute_sro_block(
    truth_class: str | dict | None = None,
    confidence: float | None = None,
    policy: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Stamp a fresh SRO v1 block at write time (writer-boundary contract).

    Mirrors the shape produced by scripts/sro_schema_migration.py so migrated
    points and new writes are schema-identical. Expiry window comes from the
    policy's expiry_defaults_days keyed by truth class; unknown/absent class
    defaults to INT (conservative middle). Calibration confidence is the
    writer's truth score at creation — outcome fields stay null until the
    future proves the claim right or wrong.
    """
    pol = policy if policy is not None else load_policy()
    now = now or datetime.now(UTC)

    label = truth_class.get("class") if isinstance(truth_class, dict) else truth_class
    days_map = pol.get("expiry_defaults_days", _FAILSAFE_POLICY["expiry_defaults_days"])
    if label not in _VALID_TRUTH_CLASSES:
        label = "INT"
    expires_at = now + timedelta(days=int(days_map.get(label, 90)))
    review_by = expires_at - timedelta(days=30)

    return {
        "supersession": {
            "supersedes": None,
            "superseded_by": None,
            "supersession_reason": None,
            "supersession_date": None,
        },
        "expiry": {
            "expires_at": expires_at.isoformat(),
            "review_by": review_by.isoformat(),
            "status": "ACTIVE",
        },
        "calibration": {
            "confidence_at_creation": confidence,
            "outcome_observed": None,
            "outcome_date": None,
            "calibration_error": None,
        },
        "sro_version": pol.get("sro_schema_version", 1),
        "sro_migrated_at": now.isoformat(),
    }


def evaluate(
    payload: dict[str, Any] | None,
    policy: dict[str, Any] | None = None,
    mode: str = "default",
    now: datetime | None = None,
) -> AdmissibilityDecision:
    """Admit or refuse one memory payload under the policy.

    Evaluation order (fail-closed at every step):
      1. mode must exist in the policy          → MODE_UNKNOWN
      2. payload.sro must be a mapping          → SRO_MISSING
      3. sro.sro_version must match the policy  → SRO_VERSION_MISMATCH
      4. expiry.status must be in vocabulary    → MALFORMED_SRO
      5. effective status: temporal guard — status ACTIVE with a past
         expires_at is effectively EXPIRED (status can lie; time cannot)
      6. supersession: explicit chain beats the status field
      7. effective status must be admissible    → STATUS_NOT_ADMISSIBLE
         (or EXPIRED_BY_TIME when the time guard did the demotion)
      8. calibration threshold (None values pass — cannot evaluate)
    Historical mode admits non-ACTIVE records but labels every one of them.
    """
    pol = policy if policy is not None else load_policy()
    now = now or datetime.now(UTC)

    mode_cfg = pol.get("modes", {}).get(mode)
    if not isinstance(mode_cfg, dict):
        return AdmissibilityDecision(False, "MODE_UNKNOWN", None, None)

    sro = payload.get("sro") if isinstance(payload, dict) else None
    if not isinstance(sro, dict):
        return AdmissibilityDecision(False, "SRO_MISSING", None, None)

    if sro.get("sro_version") != pol.get("sro_schema_version", 1):
        return AdmissibilityDecision(False, "SRO_VERSION_MISMATCH", None, None)

    expiry = sro.get("expiry")
    if not isinstance(expiry, dict):
        return AdmissibilityDecision(False, "MALFORMED_SRO", None, None)

    status = expiry.get("status")
    if status not in set(pol.get("status_vocabulary", [])):
        return AdmissibilityDecision(False, "MALFORMED_SRO", status, None)

    # Temporal guard — effective status may demote ACTIVE to EXPIRED
    effective = status
    if (
        status == "ACTIVE"
        and pol.get("temporal", {}).get("enforce_expires_at", True)
        and (_parse_iso(expiry.get("expires_at")) or now) < now
    ):
        effective = "EXPIRED"

    # Supersession — chain pointer or status, whichever speaks first
    sup = sro.get("supersession")
    superseded_by = sup.get("superseded_by") if isinstance(sup, dict) else None
    was_superseded = bool(superseded_by) or status == "SUPERSEDED" or effective == "SUPERSEDED"
    if was_superseded and not mode_cfg.get("permit_superseded", False):
        return AdmissibilityDecision(False, "SUPERSEDED", "SUPERSEDED", None)

    if effective not in set(mode_cfg.get("admit_statuses", [])):
        if status == "ACTIVE" and effective == "EXPIRED":
            reason = "EXPIRED_BY_TIME"
        else:
            reason = "STATUS_NOT_ADMISSIBLE"
        return AdmissibilityDecision(False, reason, effective, None)

    min_conf = mode_cfg.get("min_confidence")
    calib = sro.get("calibration")
    conf = calib.get("confidence_at_creation") if isinstance(calib, dict) else None
    if isinstance(min_conf, (int, float)) and isinstance(conf, (int, float)) and conf < min_conf:
        return AdmissibilityDecision(False, "LOW_CONFIDENCE", effective, None)

    # Historical mode labels only non-current records; ACTIVE stays unlabeled
    label = None
    if mode_cfg.get("label") and (effective != "ACTIVE" or was_superseded):
        label = str(mode_cfg["label"])

    return AdmissibilityDecision(True, None, effective, label)


def summarize_exclusions(decisions: list[AdmissibilityDecision]) -> dict[str, int]:
    """Count refusal reason codes — the Void Guard block every recall
    response must carry (refusal.silent: false)."""
    counts: dict[str, int] = {}
    for d in decisions:
        if not d.admitted and d.reason_code:
            counts[d.reason_code] = counts.get(d.reason_code, 0) + 1
    return counts
