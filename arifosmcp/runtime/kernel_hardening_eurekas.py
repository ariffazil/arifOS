"""
arifosmcp/runtime/kernel_hardening_eurekas.py
═══════════════════════════════════════════════════════════════════════════════
4 EUREKA MARGIN DISCOVERIES — KERNEL HARDENING SPHERE
Ratified: 2026-08-16 | F13 SOVEREIGN Governance

1. EUREKA 1: Model Capability Floor Gate (The Silent Model Demotion Trap)
   - Clamps fallen-back or low-capacity models (<0.80 benchmark) to T0 (Read-Only).
   - Prevents unverified small models from holding mutation tokens without independent judge.

2. EUREKA 2: H5 Scar Firewall (One-Way Metabolic Digest)
   - Protects human trauma/scars (H5) against prompt injection.
   - Raw narrative stored only in /root/.private/scars (chmod 0600).
   - Extracts and indexes invariant boundary rules only into agent vector memory.

3. EUREKA 3: Merkle Epoch Lock (Anti-Race Condition)
   - Validates parent_seal_hash in arif_seal transactions against VAULT999 HEAD.
   - Emits STALE_EPOCH_RETRY if HEAD advanced during reasoning, forcing arif_observe re-anchoring.

4. EUREKA 4: Proof-Before-Prompt (Reversed Receipt Doctrine)
   - Replaces cognitive HITL ("Can I proceed?") with proof-before-prompt.
   - Requires verified green tests + rollback receipt before T2 action execution.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("arifosmcp.kernel_hardening")

# ═══════════════════════════════════════════════════════════════════════════════
# EUREKA 1: MODEL CAPABILITY FLOOR GATE
# ═══════════════════════════════════════════════════════════════════════════════

MODEL_CAPABILITY_BENCHMARK: dict[str, float] = {
    # Tier 1 Sovereign / Apex Models (>= 0.90)
    "claude-3-7-sonnet": 0.96,
    "claude-3-5-sonnet": 0.95,
    "gemini-2.5-pro": 0.95,
    "gemini-2.0-flash": 0.91,
    "gpt-4o": 0.92,
    "qwen-2.5-72b": 0.89,
    "deepseek-r1": 0.93,
    "deepseek-v3": 0.90,
    # Mid-Tier Models (0.75 - 0.85)
    "qwen-2.5-32b": 0.82,
    "mistral-large": 0.84,
    "llama-3.3-70b": 0.86,
    # Low-Tier / Small Local Fallbacks (< 0.80) -> MUST CLAMP TO T0
    "qwen-2.5-7b": 0.62,
    "qwen-2.5-3b": 0.45,
    "qwen-2.5-1.5b": 0.35,
    "llama-3.2-3b": 0.42,
    "llama-3.2-1b": 0.28,
    "ollama-local-small": 0.40,
    "fallback-unknown": 0.30,
}

CAPABILITY_MIN_MUTATION_THRESHOLD = 0.80  # Minimum score required for T1/T2/T3 mutations


@dataclass
class ModelFloorVerdict:
    model_id: str
    capability_score: float
    original_tier: str
    clamped_tier: str
    demoted: bool
    reason: str


def clamp_model_autonomy(
    model_id: str | None,
    requested_action_class: str = "OBSERVE",
) -> ModelFloorVerdict:
    """Clamp fallen-back or low-tier models to T0 (Read-Only / OBSERVE) to prevent silent drift."""
    normalized_id = (model_id or "fallback-unknown").lower().strip()
    score = MODEL_CAPABILITY_BENCHMARK.get(normalized_id)
    if score is None:
        # Check substring match
        for known_model, known_score in MODEL_CAPABILITY_BENCHMARK.items():
            if known_model in normalized_id:
                score = known_score
                break
        if score is None:
            score = 0.50  # Default unknown score

    # Action classes that mutate state:
    mutation_classes = {
        "T1",
        "T2",
        "T3",
        "EXECUTE_REVERSIBLE",
        "EXECUTE_HIGH_IMPACT",
        "IRREVERSIBLE",
        "MUTATE",
    }

    if requested_action_class in mutation_classes and score < CAPABILITY_MIN_MUTATION_THRESHOLD:
        clamped = "OBSERVE" if requested_action_class.startswith("EXECUTE") or requested_action_class in {"IRREVERSIBLE", "MUTATE"} else "T0"
        return ModelFloorVerdict(
            model_id=normalized_id,
            capability_score=score,
            original_tier=requested_action_class,
            clamped_tier=clamped,
            demoted=True,
            reason=(
                f"Model '{normalized_id}' capacity score {score:.2f} < {CAPABILITY_MIN_MUTATION_THRESHOLD:.2f}. "
                f"Autonomy clamped from {requested_action_class} to {clamped} (Eureka 1 Model Floor)."
            ),
        )

    return ModelFloorVerdict(
        model_id=normalized_id,
        capability_score=score,
        original_tier=requested_action_class,
        clamped_tier=requested_action_class,
        demoted=False,
        reason="Model capability satisfies action class floor.",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EUREKA 2: H5 SCAR FIREWALL (ONE-WAY METABOLIC DIGEST)
# ═══════════════════════════════════════════════════════════════════════════════

PRIVATE_SCAR_VAULT_DIR = Path("/root/.private/scars")


@dataclass
class H5ScarDigestResult:
    scar_id: str
    private_vault_path: str
    boundary_rule: str
    digest_hash: str
    sanitized_vector_payload: dict[str, Any]
    status: str


def ingest_h5_scar_digest(
    scar_id: str,
    raw_narrative: str,
    boundary_rule_summary: str,
    sovereign_ref: str = "F13_ARIF",
) -> H5ScarDigestResult:
    """Store raw emotional narrative into /root/.private/scars (0600) and emit ONLY invariant rule."""
    PRIVATE_SCAR_VAULT_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    raw_file = PRIVATE_SCAR_VAULT_DIR / f"{scar_id}.scar"

    raw_payload = {
        "scar_id": scar_id,
        "raw_narrative": raw_narrative,
        "boundary_rule": boundary_rule_summary,
        "sovereign_ref": sovereign_ref,
        "sealed_at": time.time(),
    }

    # Write and lock 0600
    raw_file.write_text(json.dumps(raw_payload, indent=2), encoding="utf-8")
    try:
        os.chmod(raw_file, 0o600)
    except Exception as e:
        logger.warning("Could not set mode 0600 on %s: %s", raw_file, e)

    digest_hash = hashlib.sha256(raw_narrative.encode("utf-8")).hexdigest()

    # The sanitized payload that is safe for Qdrant/Agent vector memory
    sanitized_vector_payload = {
        "scar_id": scar_id,
        "memory_type": "H5_METABOLIC_CONSTRAINT",
        "boundary_rule": boundary_rule_summary,
        "digest_hash": f"sha256:{digest_hash[:16]}",
        "raw_narrative_redacted": True,
        "sovereign_sealed": True,
        "epistemic_tag": "H5_SCAR_INVARIANT",
    }

    return H5ScarDigestResult(
        scar_id=scar_id,
        private_vault_path=str(raw_file),
        boundary_rule=boundary_rule_summary,
        digest_hash=digest_hash,
        sanitized_vector_payload=sanitized_vector_payload,
        status="SEALED_IN_FIREWALL",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EUREKA 3: MERKLE EPOCH LOCK (ANTI-RACE CONDITION)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class MerkleEpochVerdict:
    status: str  # "PASS" | "STALE_EPOCH_RETRY" | "INITIAL_EPOCH"
    code: str
    expected_parent_hash: str | None
    current_head_hash: str
    message: str


def check_merkle_epoch_lock(
    parent_seal_hash: str | None,
    current_head_hash: str,
) -> MerkleEpochVerdict:
    """Validate that the agent's observed parent seal hash matches the current VAULT999 HEAD."""
    if not current_head_hash or current_head_hash in ("GENESIS", "0" * 64, ""):
        return MerkleEpochVerdict(
            status="PASS",
            code="INITIAL_EPOCH",
            expected_parent_hash=parent_seal_hash,
            current_head_hash=current_head_hash or "GENESIS",
            message="Initial epoch or genesis head.",
        )

    if parent_seal_hash is None:
        # Advisory / permissive if not specified, but tracked
        return MerkleEpochVerdict(
            status="PASS",
            code="UNSPECIFIED_PARENT",
            expected_parent_hash=None,
            current_head_hash=current_head_hash,
            message="No parent_seal_hash specified; proceeding under standard seal.",
        )

    # Normalize hash strings
    clean_parent = parent_seal_hash.replace("sha256:", "").strip()
    clean_head = current_head_hash.replace("sha256:", "").strip()

    if clean_parent != clean_head:
        return MerkleEpochVerdict(
            status="STALE_EPOCH_RETRY",
            code="STALE_EPOCH_RETRY",
            expected_parent_hash=clean_parent,
            current_head_hash=clean_head,
            message=(
                f"VAULT999 HEAD has advanced from {clean_parent[:12]} to {clean_head[:12]}. "
                "Concurrent mutation detected. Agent must arif_observe current state before resealing."
            ),
        )

    return MerkleEpochVerdict(
        status="PASS",
        code="EPOCH_LOCKED",
        expected_parent_hash=clean_parent,
        current_head_hash=clean_head,
        message="Merkle epoch verified. HEAD matches parent.",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EUREKA 4: PROOF-BEFORE-PROMPT (REVERSED RECEIPT DOCTRINE)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ProofBeforePromptReceipt:
    action_name: str
    tier: str  # T0, T1, T2, T3
    rollback_script: str
    tests_passed: bool
    veto_window_seconds: int
    receipt_id: str
    status: str
    human_interrupt_required: bool


def generate_proof_before_prompt_receipt(
    action_name: str,
    tier: str,
    rollback_script: str,
    tests_passed: bool,
) -> ProofBeforePromptReceipt:
    """Generate a structured rollback-ready receipt before executing or announcing."""
    receipt_id = f"RCPT-{hashlib.sha256((action_name + str(time.time())).encode()).hexdigest()[:12].upper()}"

    if tier in ("T0", "T0_READ_ONLY"):
        return ProofBeforePromptReceipt(
            action_name=action_name,
            tier=tier,
            rollback_script="# Read only - no mutation",
            tests_passed=True,
            veto_window_seconds=0,
            receipt_id=receipt_id,
            status="AUTO_DO",
            human_interrupt_required=False,
        )

    if tier == "T1":
        return ProofBeforePromptReceipt(
            action_name=action_name,
            tier=tier,
            rollback_script=rollback_script,
            tests_passed=tests_passed,
            veto_window_seconds=0,
            receipt_id=receipt_id,
            status="AUTO_DO_VERIFIED" if tests_passed else "TESTS_FAILED_HOLD",
            human_interrupt_required=False,
        )

    if tier == "T2":
        return ProofBeforePromptReceipt(
            action_name=action_name,
            tier=tier,
            rollback_script=rollback_script,
            tests_passed=tests_passed,
            veto_window_seconds=10,
            receipt_id=receipt_id,
            status="ANNOUNCE_10S_VETO" if tests_passed else "TESTS_FAILED_HOLD",
            human_interrupt_required=False,
        )

    # T3 (F13 Sovereign Boundary)
    return ProofBeforePromptReceipt(
        action_name=action_name,
        tier=tier,
        rollback_script=rollback_script,
        tests_passed=tests_passed,
        veto_window_seconds=0,
        receipt_id=receipt_id,
        status="888_HOLD_F13_REQUIRED",
        human_interrupt_required=True,
    )
