"""
arifosmcp/tests/test_deliberation_chain.py — DELIBERATION_RECEIPT tests
═════════════════════════════════════════════════════════════════════════

Forged 2026-08-02 by F13 SOVEREIGN directive.
Epistemic label: INT (interpretive mapping) · PLAUSIBLE.

Test gate for Q2 fix — DELIBERATION_RECEIPT layer that audit flagged
as missing. Covers:
  - artifact hash binding (F2 TRUTH)
  - hash-chain integrity (F11 AUDITABILITY)
  - WITNESS step presence (F3 TRI-WITNESS)
  - terminal_verdict in {SEAL, HOLD, VOID, SABAR}
  - canonical_only mode routes non-deliberation records correctly

Reversibility: git revert <commit-sha>.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arifosmcp.schemas.deliberation_v1 import (
    ConstitutionalSealForDeliberation,
    DeliberationBlock,
    DeliberationStep,
)
from arifosmcp.tools.deliberate import mint_deliberation_receipt
from arifosmcp.tools.verify_chain import verify_chain


ARTIFACT_PATH = "/root/arifOS/arifosmcp/constitution/quranic_runtime_map.json"


class TestDeliberationMint:
    def test_mint_returns_canonical_record(self):
        rec = mint_deliberation_receipt(
            artifact_path=ARTIFACT_PATH,
            artifact_class="constitutional_map",
            falsifiable_predictions=["kernel will refuse intent claims"],
            actor_id="arif",
            session_id="test-session",
        )
        assert rec.record_class == "CONSTITUTIONAL_SEAL_FOR_DELIBERATION"
        assert rec.artifact_path == ARTIFACT_PATH
        assert rec.deliberation.terminal_verdict == "SEAL"
        assert len(rec.deliberation.steps) == 3

    def test_mint_computes_artifact_sha256(self):
        rec = mint_deliberation_receipt(
            artifact_path=ARTIFACT_PATH,
            artifact_class="constitutional_map",
            falsifiable_predictions=[],
            actor_id="arif",
            session_id="test",
        )
        expected = "sha256:" + __import__("hashlib").sha256(
            Path(ARTIFACT_PATH).read_bytes()
        ).hexdigest()
        assert rec.artifact_sha256 == expected


class TestVerifyChain:
    def test_minted_record_verifies_true(self):
        rec = mint_deliberation_receipt(
            artifact_path=ARTIFACT_PATH,
            artifact_class="constitutional_map",
            falsifiable_predictions=["A", "B"],
            actor_id="arif",
            session_id="test",
        )
        result = verify_chain(rec, canonical_only=True)
        assert result["verified"] is True
        assert result["broken_step"] == -1

    def test_canonical_only_skips_non_deliberation(self):
        rec = mint_deliberation_receipt(
            artifact_path=ARTIFACT_PATH,
            artifact_class="constitutional_map",
            falsifiable_predictions=[],
            actor_id="arif",
            session_id="test",
        )
        # Force record_class to non-canonical
        rec.record_class = "SESSION_RECEIPT"  # type: ignore[assignment]
        result = verify_chain(rec, canonical_only=True)
        assert result["verified"] is False
        assert "non-canonical" in result["reason"]

    def test_amendment_without_anchor_breaks_chain(self):
        """If step[2] = AMENDMENT changes artifact_sha256 but no anchor
        exists, chain must break."""
        # Build a chain manually with PROPOSAL → WITNESS → AMENDMENT
        # where the amendment's parent doesn't match witness's hash.
        proposal = DeliberationStep(
            order=0,
            step_type="PROPOSAL",
            actor_id="arif",
            actor_signature="sig0",
            sha256_of_step_payload="sha256:step0hash",
            parent_step_sha256=None,
            created_at_utc="2026-08-02T00:00:00",
        )
        witness = DeliberationStep(
            order=1,
            step_type="WITNESS",
            actor_id="arif",
            actor_signature="sig1",
            sha256_of_step_payload="sha256:step1hash",
            parent_step_sha256="sha256:step0hash",
            created_at_utc="2026-08-02T00:00:01",
        )
        # AMENDMENT with WRONG parent (not step1hash)
        amendment = DeliberationStep(
            order=2,
            step_type="AMENDMENT",
            actor_id="arif",
            actor_signature="sig2",
            sha256_of_step_payload="sha256:step2hash",
            parent_step_sha256="sha256:wrong_parent",  # broken link
            created_at_utc="2026-08-02T00:00:02",
        )
        block = DeliberationBlock(
            artifact_sha256="sha256:test",
            artifact_path=ARTIFACT_PATH,
            artifact_class="constitutional_map",
            steps=[proposal, witness, amendment],
            terminal_verdict="SEAL",
            cooling_required=False,
            falsifiable_predictions=[],
        )
        rec = ConstitutionalSealForDeliberation(
            record_id="DS-test-broken",
            record_class="CONSTITUTIONAL_SEAL_FOR_DELIBERATION",
            actor_id="arif",
            session_id="test",
            session_token=None,
            lease_id=None,
            artifact_sha256="sha256:test",
            artifact_path=ARTIFACT_PATH,
            deliberation=block,
            verify_chain_token="sha256:token",
            sealed_at_utc="2026-08-02T00:00:00",
        )
        result = verify_chain(rec, canonical_only=True)
        assert result["verified"] is False
        assert result["broken_step"] == 2

    def test_no_witness_step_breaks_chain(self):
        """If no WITNESS step exists, F3 TRI-WITNESS contract is violated."""
        proposal = DeliberationStep(
            order=0,
            step_type="PROPOSAL",
            actor_id="arif",
            actor_signature="sig0",
            sha256_of_step_payload="sha256:step0hash",
            parent_step_sha256=None,
            created_at_utc="2026-08-02T00:00:00",
        )
        verdict = DeliberationStep(
            order=1,
            step_type="VERDICT",
            actor_id="arif",
            actor_signature="sig1",
            sha256_of_step_payload="sha256:step1hash",
            parent_step_sha256="sha256:step0hash",
            created_at_utc="2026-08-02T00:00:01",
        )
        block = DeliberationBlock(
            artifact_sha256="sha256:test",
            artifact_path=ARTIFACT_PATH,
            artifact_class="constitutional_map",
            steps=[proposal, verdict],
            terminal_verdict="SEAL",
            cooling_required=False,
            falsifiable_predictions=[],
        )
        rec = ConstitutionalSealForDeliberation(
            record_id="DS-test-nowitness",
            record_class="CONSTITUTIONAL_SEAL_FOR_DELIBERATION",
            actor_id="arif",
            session_id="test",
            session_token=None,
            lease_id=None,
            artifact_sha256="sha256:test",
            artifact_path=ARTIFACT_PATH,
            deliberation=block,
            verify_chain_token="sha256:token",
            sealed_at_utc="2026-08-02T00:00:00",
        )
        result = verify_chain(rec, canonical_only=True)
        assert result["verified"] is False
        assert "WITNESS" in result["reason"]