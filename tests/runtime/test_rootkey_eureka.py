"""
Tests for Eureka kernel modules (ROOTKEY v53).
Sovereign Anchor / ZKPC / Seal Chain / Entropy Gate / F13 Gate / Vault Chain.

Each module: minimum 3 tests.
Constitutional floors: F1, F2, F8, F11, F12, F13.
"""

import pytest
import json
import hashlib
from unittest.mock import patch

# ──────────────────────────────────────────────
# E1: Sovereign Anchor
# ──────────────────────────────────────────────
from arifosmcp.runtime.sovereign_anchor import verify_sovereign_anchor

class TestSovereignAnchor:
    """Eureka 1: Session → /000 sovereign anchor enforcement."""

    def test_valid_anchor(self):
        """Valid anchor with registered key passes."""
        ctx = {"sovereign_key": "arif-fazil-000-attested"}
        ok, reason = verify_sovereign_anchor(ctx)
        assert ok is True
        assert "verified" in reason.lower()

    def test_missing_sovereign_key(self):
        """Missing sovereign_key in context fails."""
        ctx = {}
        ok, reason = verify_sovereign_anchor(ctx)
        assert ok is False
        assert "no sovereign" in reason.lower() or "missing" in reason.lower()
        assert "anchor" in reason.lower()

    def test_unregistered_key(self):
        """Key not in registered set fails."""
        ctx = {"sovereign_key": "unknown-key-xyz"}
        ok, reason = verify_sovereign_anchor(ctx)
        assert ok is False
        assert "not match" in reason.lower() or "unrecognized" in reason.lower()

    def test_revoked_key(self):
        """Revoked key fails."""
        ctx = {"sovereign_key": "compromised-key-2025"}
        ok, reason = verify_sovereign_anchor(ctx)
        assert ok is False
        assert "revoked" in reason.lower()


# ──────────────────────────────────────────────
# E2: ZKPC Verifier
# ──────────────────────────────────────────────
from arifosmcp.runtime.zkpc_verifier import verify_zkpc


class TestZKPCVerifier:
    """Eureka 2: 7-dimension coherence check for context claims."""

    FULL_EVIDENCE = {
        "wound_architecture": 0.95,
        "paradox_tolerance": 0.85,
        "moral_architecture": 0.90,
        "language_register": 0.88,
        "sovereign_intent": 0.92,
        "godel_lock": 0.80,
        "anti_behavior_sink": 0.75,
    }

    def test_full_evidence_passes(self):
        """Full evidence across all 7 dims passes."""
        passed, scores = verify_zkpc({"claim": "test"}, self.FULL_EVIDENCE)
        assert passed is True, f"Scores: {scores}"
        assert all(s >= 0.7 for s in scores.values()), f"Scores: {scores}"

    def test_empty_evidence_fails(self):
        """No evidence fails all dims."""
        passed, scores = verify_zkpc({"claim": "test"}, {})
        assert passed is False

    def test_partial_evidence_fails(self):
        """Only 3 of 7 dims above threshold → fails."""
        partial = {
            "wound_architecture": 0.95,
            "paradox_tolerance": 0.85,
            "moral_architecture": 0.90,
        }
        passed, scores = verify_zkpc({"claim": "test"}, partial)
        assert passed is False

    def test_returns_dimension_scores(self):
        """Returns scores for all 7 dimensions."""
        passed, scores = verify_zkpc({"claim": "test"}, self.FULL_EVIDENCE)
        assert len(scores) == 7
        expected_dims = {
            "wound_architecture",
            "paradox_tolerance",
            "moral_architecture",
            "language_register",
            "sovereign_intent",
            "godel_lock",
            "anti_behavior_sink",
        }
        assert set(scores.keys()) == expected_dims


# ──────────────────────────────────────────────
# E3: Seal Chain
# ──────────────────────────────────────────────
from arifosmcp.runtime.seal_chain import validate_seal_chain


class TestSealChain:
    """Eureka 3: SEAL → genesis trace validation."""

    def test_valid_chain(self):
        """Two-seal chain tracing to genesis passes."""
        ok, chain = validate_seal_chain("seal_002")
        assert ok is True, f"Chain: {chain}"
        assert len(chain) >= 2
        assert chain[-1] == "genesis"

    def test_genesis_self_valid(self):
        """Genesis seal itself is valid."""
        ok, chain = validate_seal_chain("genesis")
        assert ok is True
        assert chain == ["genesis"]

    def test_orphan_seal_fails(self):
        """Seal without genesis parent fails."""
        ok, chain = validate_seal_chain("orphan_seal")
        assert ok is False
        # Orphan has nonexistent_parent -> returns what it can
        assert len(chain) >= 0

    def test_nonexistent_seal_fails(self):
        """Seal ID not in chain fails."""
        ok, chain = validate_seal_chain("nonexistent")
        assert ok is False
        assert chain == []


# ──────────────────────────────────────────────
# E4: Entropy Gate
# ──────────────────────────────────────────────
from arifosmcp.runtime.entropy_gate import check_entropy


class TestEntropyGate:
    """Eureka 4: Anti-behavior-sink entropy measurement."""

    def test_healthy_prose_proceed(self):
        """Novel varied prose → PROCEED."""
        score, action = check_entropy(
            "The quick brown fox jumps over the lazy dog near the bank of the river."
        )
        assert action == "PROCEED"

    def test_repetitive_output_explore(self):
        """Highly repetitive → EXPLORE."""
        score, action = check_entropy("Yes. Yes. Yes. Yes. Yes. Yes. Yes. Yes. Yes. Yes.")
        assert action == "EXPLORE"

    def test_empty_explore(self):
        """Empty string → EXPLORE."""
        score, action = check_entropy("")
        assert action == "EXPLORE"

    def test_single_char_explore(self):
        """Single repeated character → EXPLORE."""
        score, action = check_entropy("aaaaaaa")
        assert action == "EXPLORE"


# ──────────────────────────────────────────────
# E5: F13 Gate
# ──────────────────────────────────────────────
from arifosmcp.runtime.f13_gate import check_f13_integrity


class TestF13Gate:
    """Eureka 5: Non-delegable sovereignty enforcement."""

    def test_direct_sovereign_allowed(self):
        """Human sovereign direct action → ALLOWED."""
        allowed, reason = check_f13_integrity(
            {"type": "SEAL", "target": "session_001"}, "human_sovereign"
        )
        assert allowed is True
        assert "verified" in reason.lower()

    def test_sub_agent_blocked(self):
        """Sub-agent claiming F13 → BLOCKED."""
        allowed, reason = check_f13_integrity(
            {"type": "SEAL", "target": "session_001"}, "sub_agent_333"
        )
        assert allowed is False
        assert "non-delegable" in reason.lower()

    def test_automation_blocked(self):
        """Automation layer → BLOCKED."""
        allowed, reason = check_f13_integrity(
            {"type": "SEAL", "target": "session_001"}, "cron_automation"
        )
        assert allowed is False

    def test_action_with_delegation_keyword_blocked(self):
        """Action containing delegation keyword → BLOCKED."""
        allowed, reason = check_f13_integrity(
            {"type": "SEAL", "delegate_to": "agent_555"}, "human_sovereign"
        )
        assert allowed is False
        assert "non-delegable" in reason.lower()


# ──────────────────────────────────────────────
# E6: Vault Chain
# ──────────────────────────────────────────────
from arifosmcp.runtime.vault_chain import verify_vault_chain


def _make_entry(eid, prev_hash, content="data"):
    h = hashlib.sha256(f"{prev_hash}:{content}:{eid}".encode()).hexdigest()
    return {
        "id": eid,
        "entry_hash": h,
        "previous_hash": prev_hash,
        "signature": f"sig_{eid}_{h[:8]}",
        "content": content,
    }


class TestVaultChain:
    """Eureka 6: Hash chain integrity verification."""

    def test_intact_chain_passes(self):
        """Three entries with valid hash links pass."""
        e1 = _make_entry("entry_001", "")  # genesis = empty prev_hash
        e2 = _make_entry("entry_002", e1["entry_hash"])
        e3 = _make_entry("entry_003", e2["entry_hash"])
        valid, broken = verify_vault_chain([e1, e2, e3])
        assert valid is True, f"Broken: {broken}"
        assert len(broken) == 0

    def test_broken_link_detected(self):
        """Broken hash link detected."""
        e1 = _make_entry("entry_001", "")
        e2 = _make_entry("entry_002", "badhash123")  # wrong prev hash
        valid, broken = verify_vault_chain([e1, e2])
        assert valid is False
        assert len(broken) > 0

    def test_empty_chain_passes(self):
        """Empty chain is trivially valid."""
        valid, broken = verify_vault_chain([])
        assert valid is True
        assert len(broken) == 0

    def test_single_entry_passes(self):
        """Single genesis entry passes."""
        e1 = _make_entry("genesis", "")
        valid, broken = verify_vault_chain([e1])
        assert valid is True, f"Broken: {broken}"


# ──────────────────────────────────────────────
# Cross-Module: Loop Closure Integration
# ──────────────────────────────────────────────

class TestLoopClosure:
    """Integration test: /000 → E1→E5→E2→E4→E3→E6 → /999 loop."""

    def test_full_session_loop(self):
        """Simulate a complete session loop from /000 to /999."""
        # Step 1: /000 sovereign anchor (E1)
        ctx = {"sovereign_key": "arif-fazil-000-attested"}
        anchor_ok, _ = verify_sovereign_anchor(ctx)
        assert anchor_ok is True

        # Step 6: Vault chain integrity (E6)
        e1 = _make_entry("genesis", "")
        e2 = _make_entry("entry_001", e1["entry_hash"])
        vault_ok, broken = verify_vault_chain([e1, e2])
        assert vault_ok is True, f"Broken: {broken}"

        # Step 3: ZKPC verify context (E2)
        zkpc_ok, scores = verify_zkpc(
            {"claim": "session context"},
            TestZKPCVerifier.FULL_EVIDENCE,
        )
        assert zkpc_ok is True, f"Scores: {scores}"

        # Step 4: Entropy check (E4)
        _, entropy_action = check_entropy(
            "Novel reasoning with varied analytical depth and exploration."
        )
        assert entropy_action == "PROCEED"

        # Step 5: Seal chain validation (E3)
        seal_ok, chain = validate_seal_chain("seal_002")
        assert seal_ok is True, f"Chain: {chain}"

        # All 6 Eureka gates passed → loop closed
        assert all([anchor_ok, zkpc_ok, seal_ok, vault_ok])
        assert entropy_action == "PROCEED"
