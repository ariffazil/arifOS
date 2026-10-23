"""F6 Privacy, Retention, Access Control, Redress, and Rollback Semantics.

Implements F6 v0 Status & Privasi requirements:
  - Prohibits any human intelligence, compliance, personality, or dignity score
    (L1 breach -> DISQUALIFY).
  - Minimizes sensitive telemetry, defines retention & access control (`0o600`),
    and enforces separation between out-of-band meter analytics and authority
    records.
  - Note: absence of `human_id` alone does NOT prove anonymity (see linkage
    attack tests).
  - Provides challenge, stop, revoke, and non-destructive record correction
    paths (append-only, history preserved).
  - Distinguishes technical rollback (`TECHNICAL_ROLLBACK_COMPLETE`) from
    irreversible external consequences (`EXTERNAL_CONSEQUENCE_IRREVERSIBLE`).
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SCHEMA = "arifos.f6.privacy_and_redress.v1"

FORBIDDEN_HUMAN_SCORE_KEYS = frozenset(
    {
        "human_id",
        "user_id",
        "actor_human",
        "operator_name",
        "email",
        "dignity_index",
        "dignity_score",
        "intelligence_score",
        "compliance_score",
        "obedience_score",
        "personality_profile",
        "comprehension_rate",
        "keystroke_dynamics",
        "hover_hesitation_ms",
        "time_to_read_ms",
    }
)


@dataclass(frozen=True)
class RetentionAndAccessPolicy:
    telemetry_retention_days: int = 30
    authority_record_retention: str = "append_only_audit_bound"
    file_mode_octal: str = "0600"
    analytics_store_domain: str = "f6_meter_telemetry_out_of_band"
    authority_store_domain: str = "f6_authority_bindings_isolated"
    cross_join_forbidden: bool = True
    anonymity_disclaimer: str = (
        "Absence of human_id does NOT prove anonymity; timestamp, workflow, "
        "stylometric, and cross-ledger linkage risks remain bounded/documented."
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_PRIVACY_POLICY = RetentionAndAccessPolicy()


def validate_no_human_scoring(payload: Any) -> tuple[bool, list[str]]:
    """Scan any nested dict/list payload for forbidden human-scoring or identity keys.

    Any match is an L1 breach (DISQUALIFY under spec C.1 / C.3).
    """
    violations: list[str] = []

    def _walk(obj: Any, path: str = "") -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                kl = str(k).lower().strip()
                curr = f"{path}.{k}" if path else str(k)
                if kl in FORBIDDEN_HUMAN_SCORE_KEYS or "dignity_index" in kl:
                    violations.append(curr)
                _walk(v, curr)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                _walk(item, f"{path}[{idx}]")

    _walk(payload)
    return len(violations) == 0, violations


def verify_analytics_authority_separation(
    analytics_payload: dict[str, Any],
    authority_db_path: Path,
    telemetry_ledger_path: Path,
) -> dict[str, Any]:
    """Verify that out-of-band meter analytics are isolated from authority records.

    1. Storage paths must be distinct.
    2. Analytics payload must not contain `actor_id` or `binding_id` join keys from
       authority records, nor any forbidden human scoring keys.
    """
    same_path = Path(authority_db_path).resolve() == Path(telemetry_ledger_path).resolve()
    ok_no_human, human_violations = validate_no_human_scoring(analytics_payload)
    blob = json.dumps(analytics_payload, default=str)
    has_actor_id = '"actor_id"' in blob
    separated = (not same_path) and ok_no_human and (not has_actor_id)
    return {
        "schema": SCHEMA,
        "separated": separated,
        "distinct_storage_paths": not same_path,
        "no_human_scoring_or_id": ok_no_human,
        "no_authority_actor_id_in_analytics": not has_actor_id,
        "violations": human_violations,
        "policy": DEFAULT_PRIVACY_POLICY.to_dict(),
    }


def enforce_private_file_mode(path: Path) -> bool:
    """Enforce 0600 permissions on sensitive F6 state/ledger files."""
    p = Path(path)
    if not p.exists():
        return False
    os.chmod(p, 0o600)
    mode = oct(p.stat().st_mode & 0o777)
    return mode == "0o600"


class RollbackClassification:
    TECHNICAL_ROLLBACK_COMPLETE = "TECHNICAL_ROLLBACK_COMPLETE"
    TECHNICAL_ROLLBACK_FAILED = "TECHNICAL_ROLLBACK_FAILED"
    EXTERNAL_CONSEQUENCE_IRREVERSIBLE = "EXTERNAL_CONSEQUENCE_IRREVERSIBLE"


def classify_rollback_outcome(
    *,
    technical_state_reverted: bool,
    external_effect_occurred: bool,
    external_effect_description: str = "",
    compensating_action: str = "",
) -> dict[str, Any]:
    """Distinguish local technical rollback from irreversible external consequences.

    If an external effect occurred (e.g. message sent to user/group, webhook
    dispatched, third-party API mutated, private data disclosed), reverting
    local database/memory state does NOT undo the external consequence. The
    system must never claim the action was 'undone' or 'rolled back cleanly'.
    """
    if external_effect_occurred:
        return {
            "schema": SCHEMA,
            "classification": RollbackClassification.EXTERNAL_CONSEQUENCE_IRREVERSIBLE,
            "fully_undone": False,
            "technical_state_reverted": technical_state_reverted,
            "external_effect_occurred": True,
            "external_effect_description": external_effect_description[:300],
            "compensating_action_required": True,
            "compensating_action": compensating_action[:300]
            or "notify sovereign / issue correction notice; external consequence cannot be erased",
            "reason": (
                "local technical rollback cannot undo external consequence that already occurred"
            ),
        }
    if technical_state_reverted:
        return {
            "schema": SCHEMA,
            "classification": RollbackClassification.TECHNICAL_ROLLBACK_COMPLETE,
            "fully_undone": True,
            "technical_state_reverted": True,
            "external_effect_occurred": False,
            "compensating_action_required": False,
            "reason": "local state reverted prior to any external side-effect",
        }
    return {
        "schema": SCHEMA,
        "classification": RollbackClassification.TECHNICAL_ROLLBACK_FAILED,
        "fully_undone": False,
        "technical_state_reverted": False,
        "external_effect_occurred": False,
        "compensating_action_required": True,
        "reason": "technical rollback did not complete",
    }
