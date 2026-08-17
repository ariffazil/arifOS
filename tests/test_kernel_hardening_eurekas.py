"""
tests/test_kernel_hardening_eurekas.py
═══════════════════════════════════════════════════════════════════════════════
Unit tests for the 4 Eureka Margin Kernel Hardening gates:
1. Model Capability Floor Gate (Silent Demotion Trap)
2. H5 Scar Firewall (One-Way Metabolic Digest)
3. Merkle Epoch Lock (Anti-Race Condition)
4. Proof-Before-Prompt (Reversed Receipt Doctrine)
"""

import pytest
import os
import shutil
from pathlib import Path

from arifosmcp.runtime.kernel_hardening_eurekas import (
    clamp_model_autonomy,
    ingest_h5_scar_digest,
    check_merkle_epoch_lock,
    generate_proof_before_prompt_receipt,
    PRIVATE_SCAR_VAULT_DIR,
)


def test_eureka1_model_capability_floor_clamp():
    # High-tier models (>= 0.80) retain mutation privileges
    v_sonnet = clamp_model_autonomy("claude-3-7-sonnet", "T1")
    assert not v_sonnet.demoted
    assert v_sonnet.clamped_tier == "T1"

    v_gemini = clamp_model_autonomy("gemini-2.5-pro", "T2")
    assert not v_gemini.demoted
    assert v_gemini.clamped_tier == "T2"

    # Fallen-back or small models (< 0.80) MUST be clamped to T0 / OBSERVE
    v_small = clamp_model_autonomy("qwen-2.5-7b", "T1")
    assert v_small.demoted
    assert v_small.clamped_tier == "T0"

    v_local = clamp_model_autonomy("ollama-local-small", "EXECUTE_REVERSIBLE")
    assert v_local.demoted
    assert v_local.clamped_tier == "OBSERVE"

    v_unknown = clamp_model_autonomy("unverified-tiny-fallback", "IRREVERSIBLE")
    assert v_unknown.demoted
    assert v_unknown.clamped_tier == "OBSERVE"


def test_eureka2_h5_scar_firewall_metabolic_digest(tmp_path):
    test_scar_id = "SCAR-TEST-20260816"
    raw_narrative = "Private personal event detail that must never leak to prompt injection or agent context."
    boundary_rule = "DO_NOT_ENGAGE_HIGH_LEVERAGE_COUNTERPARTY_X"

    digest = ingest_h5_scar_digest(
        scar_id=test_scar_id,
        raw_narrative=raw_narrative,
        boundary_rule_summary=boundary_rule,
        sovereign_ref="F13_ARIF",
    )

    # 1. Private vault file exists and is mode 0600
    vault_file = Path(digest.private_vault_path)
    assert vault_file.exists()
    file_mode = oct(vault_file.stat().st_mode & 0o777)
    assert file_mode == "0o600"

    # 2. Sanitized vector payload contains NO raw narrative
    payload = digest.sanitized_vector_payload
    assert "raw_narrative" not in payload
    assert payload["boundary_rule"] == boundary_rule
    assert payload["raw_narrative_redacted"] is True
    assert payload["memory_type"] == "H5_METABOLIC_CONSTRAINT"

    # Cleanup test scar
    try:
        vault_file.unlink(missing_ok=True)
    except Exception:
        pass


def test_eureka3_merkle_epoch_lock():
    # 1. HEAD matches parent -> PASS
    v_match = check_merkle_epoch_lock(
        parent_seal_hash="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
        current_head_hash="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
    )
    assert v_match.status == "PASS"
    assert v_match.code == "EPOCH_LOCKED"

    # 2. HEAD has moved while agent was thinking -> STALE_EPOCH_RETRY
    v_stale = check_merkle_epoch_lock(
        parent_seal_hash="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
        current_head_hash="9999999999999999999999999999999999999999999999999999999999999999",
    )
    assert v_stale.status == "STALE_EPOCH_RETRY"
    assert v_stale.code == "STALE_EPOCH_RETRY"
    assert "concurrent mutation" in v_stale.message.lower()

    # 3. Initial/Genesis epoch -> PASS
    v_genesis = check_merkle_epoch_lock(
        parent_seal_hash=None,
        current_head_hash="GENESIS",
    )
    assert v_genesis.status == "PASS"


def test_eureka4_proof_before_prompt_receipt():
    # T0 Read-only -> AUTO_DO, no veto window, no human interrupt
    r_t0 = generate_proof_before_prompt_receipt(
        action_name="read_port_health",
        tier="T0",
        rollback_script="",
        tests_passed=True,
    )
    assert r_t0.status == "AUTO_DO"
    assert not r_t0.human_interrupt_required
    assert r_t0.veto_window_seconds == 0

    # T1 Local edits -> AUTO_DO when tests green
    r_t1_pass = generate_proof_before_prompt_receipt(
        action_name="apply_file_edit",
        tier="T1",
        rollback_script="git checkout HEAD -- file.py",
        tests_passed=True,
    )
    assert r_t1_pass.status == "AUTO_DO_VERIFIED"
    assert not r_t1_pass.human_interrupt_required

    r_t1_fail = generate_proof_before_prompt_receipt(
        action_name="apply_file_edit",
        tier="T1",
        rollback_script="git checkout HEAD -- file.py",
        tests_passed=False,
    )
    assert r_t1_fail.status == "TESTS_FAILED_HOLD"

    # T2 Production Deploy / Restart -> 10s veto announcement
    r_t2 = generate_proof_before_prompt_receipt(
        action_name="restart_service",
        tier="T2",
        rollback_script="systemctl restart backup_service",
        tests_passed=True,
    )
    assert r_t2.status == "ANNOUNCE_10S_VETO"
    assert r_t2.veto_window_seconds == 10
    assert not r_t2.human_interrupt_required

    # T3 Irreversible (F13 Sovereign Boundary) -> 888_HOLD
    r_t3 = generate_proof_before_prompt_receipt(
        action_name="drop_database_table",
        tier="T3",
        rollback_script="restore_from_cold_storage.sh",
        tests_passed=True,
    )
    assert r_t3.status == "888_HOLD_F13_REQUIRED"
    assert r_t3.human_interrupt_required
