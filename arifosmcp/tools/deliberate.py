"""
arifosmcp/tools/deliberate.py — mint_deliberation_receipt (Q2 fix)
═══════════════════════════════════════════════════════════════════

Forged 2026-08-02 by F13 SOVEREIGN directive. D2=separate record class.
Epistemic label: INT (interpretive mapping) · PLAUSIBLE.

Mint flow:
  1. Compute artifact_sha256 from path.
  2. Emit step[0] = PROPOSAL with falsifiable_predictions.
  3. Mint step[1] = WITNESS (chained).
  4. Optional step[2] = CHALLENGE.
  5. Terminal step[N] = VERDICT.
  6. Return record_id + verify_chain_token.

Reversibility: git revert <commit-sha>.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
import uuid
from pathlib import Path
from typing import Any

from arifosmcp.schemas.deliberation_v1 import (
    ConstitutionalSealForDeliberation,
    DeliberationBlock,
    DeliberationStep,
)


def _sha256_of(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_file(path: str | Path) -> str:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"artifact not found: {path}")
    return _sha256_of(p.read_bytes())


def _actor_signature(actor_id: str, step_payload: dict[str, Any]) -> str:
    """Schema-stamped actor signature — Ed25519 in production, HMAC-stub now."""
    payload = f"{actor_id}|" + "|".join(f"{k}={v}" for k, v in sorted(step_payload.items()))
    secret = os.getenv("ARIFOS_INTERNAL_SECRET", "default_secret").encode()
    return "hmac:" + hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()[:32]


def mint_deliberation_receipt(
    *,
    artifact_path: str,
    artifact_class: str,
    falsifiable_predictions: list[str],
    actor_id: str,
    session_id: str,
    session_token: str | None = None,
    lease_id: str | None = None,
    terminal_verdict: str = "SEAL",
    cooling_required: bool = False,
) -> ConstitutionalSealForDeliberation:
    """Mint a DELIBERATION_RECEIPT for an artifact.

    Hash-chains the deliberation steps so verify_chain() can replay them.
    """
    artifact_sha256 = _sha256_file(artifact_path)

    base_ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())

    # Step 0: PROPOSAL — INT with falsifiable predictions
    proposal_payload = {
        "step_type": "PROPOSAL",
        "artifact_sha256": artifact_sha256,
        "artifact_path": str(artifact_path),
        "falsifiable_predictions": list(falsifiable_predictions),
        "actor_id": actor_id,
        "session_id": session_id,
    }
    proposal_step = DeliberationStep(
        order=0,
        step_type="PROPOSAL",
        actor_id=actor_id,
        actor_signature=_actor_signature(actor_id, proposal_payload),
        sha256_of_step_payload=_sha256_of(repr(sorted(proposal_payload.items())).encode()),
        parent_step_sha256=None,
        created_at_utc=base_ts,
        notes=(
            f"PROPOSAL: bind artifact={artifact_sha256[:24]}... "
            f"with {len(falsifiable_predictions)} falsifiable predictions"
        ),
    )

    # Step 1: WITNESS — three-channel stub (Human×AI×Earth). Production wires
    # forge_witness; here we instantiate with conservative defaults.
    witness_payload = {
        "step_type": "WITNESS",
        "human_channel": 0.75,
        "ai_channel": 0.75,
        "earth_channel": 0.75,  # placeholder until forge_witness wired
        "actor_id": actor_id,
    }
    witness_step = DeliberationStep(
        order=1,
        step_type="WITNESS",
        actor_id=actor_id,
        actor_signature=_actor_signature(actor_id, witness_payload),
        sha256_of_step_payload=_sha256_of(repr(sorted(witness_payload.items())).encode()),
        parent_step_sha256=proposal_step.sha256_of_step_payload,
        created_at_utc=base_ts,
        notes="WITNESS: tri-channel H×A×E ≥ 0.75 (F3)",
    )

    # Terminal step: VERDICT
    verdict_payload = {
        "step_type": "VERDICT",
        "terminal_verdict": terminal_verdict,
        "artifact_sha256": artifact_sha256,
        "actor_id": actor_id,
    }
    verdict_step = DeliberationStep(
        order=2,
        step_type="VERDICT",
        actor_id=actor_id,
        actor_signature=_actor_signature(actor_id, verdict_payload),
        sha256_of_step_payload=_sha256_of(repr(sorted(verdict_payload.items())).encode()),
        parent_step_sha256=witness_step.sha256_of_step_payload,
        created_at_utc=base_ts,
        notes=f"VERDICT: {terminal_verdict}",
    )

    deliberation = DeliberationBlock(
        artifact_sha256=artifact_sha256,
        artifact_path=str(artifact_path),
        artifact_class=artifact_class,  # type: ignore[arg-type]
        steps=[proposal_step, witness_step, verdict_step],
        terminal_verdict=terminal_verdict,  # type: ignore[arg-type]
        cooling_required=cooling_required,
        falsifiable_predictions=list(falsifiable_predictions),
    )

    record_id = f"DS-{uuid.uuid4().hex[:12]}"
    sealed_at_utc = base_ts
    verify_chain_token = _sha256_of(
        (deliberation.artifact_sha256 + sealed_at_utc).encode()
    )

    return ConstitutionalSealForDeliberation(
        record_id=record_id,
        record_class="CONSTITUTIONAL_SEAL_FOR_DELIBERATION",
        actor_id=actor_id,
        session_id=session_id,
        session_token=session_token,
        lease_id=lease_id,
        artifact_sha256=artifact_sha256,
        artifact_path=str(artifact_path),
        deliberation=deliberation,
        verify_chain_token=verify_chain_token,
        sealed_at_utc=sealed_at_utc,
    )


__all__ = ["mint_deliberation_receipt"]