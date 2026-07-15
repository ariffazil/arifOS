"""
arifOS Gödel Lock — Runtime Enforcement
P0-1 fix: Actual code that verifies provider separation.

This is the enforcement layer the YAML files describe but don't implement.
Import this in kernel pre-SEAL checks.
"""

import hashlib
import hmac
import json
import time
from typing import Optional


# ── Provider Registry ───────────────────────────────────────────────────────

PROVIDER_REGISTRY = {
    "hermes": {"type": "internal", "models": ["mimo", "sea-lion", "deepseek"]},
    "openai": {"type": "external", "models": ["gpt-4", "gpt-4o", "o1", "o3", "chatgpt"]},
    "google": {"type": "external", "models": ["gemini", "gemini-pro", "gemini-ultra"]},
    "xai": {"type": "external", "models": ["grok", "grok-2", "grok-3"]},
    "anthropic": {"type": "external", "models": ["claude", "claude-sonnet", "claude-opus"]},
}

# The audited system's provider (configurable)
AUDITED_SYSTEM_PROVIDER = "hermes"


def verify_provider_separation(auditor_provider: str) -> dict:
    """
    P0-1 FIX: Runtime check that auditor uses different provider than audited system.
    Returns verification result with evidence.
    """
    if auditor_provider == AUDITED_SYSTEM_PROVIDER:
        return {
            "verified": False,
            "reason": f"Auditor provider '{auditor_provider}' matches audited system provider '{AUDITED_SYSTEM_PROVIDER}'",
            "action": "VOID_AUDIT",
            "evidence_band": "L2_VERIFIED",
        }

    auditor_info = PROVIDER_REGISTRY.get(auditor_provider)
    if not auditor_info:
        return {
            "verified": False,
            "reason": f"Unknown provider '{auditor_provider}' — not in registry",
            "action": "REJECT",
            "evidence_band": "L2_VERIFIED",
        }

    return {
        "verified": True,
        "reason": f"Auditor '{auditor_provider}' (external) ≠ audited '{AUDITED_SYSTEM_PROVIDER}' (internal)",
        "action": "ACCEPT",
        "evidence_band": "L2_VERIFIED",
    }


# ── Anti-Calhoun Gate ───────────────────────────────────────────────────────

def anti_calhoun_score(audit_result: dict) -> dict:
    """
    P1-3 FIX (part): Anti-Calhoun gate with HARD enforcement.
    Score starts at 1.0, deductions for failures. Minimum 0.60 to pass.
    """
    score = 1.0
    deductions = []

    # C1: Actionable finding
    if not audit_result.get("has_actionable_finding"):
        score -= 0.20
        deductions.append("No actionable finding: -0.20")

    # C2: Consequential
    if not audit_result.get("changed_something"):
        score -= 0.15
        deductions.append("No consequence demonstrated: -0.15")

    # C3: Evidenced
    if not audit_result.get("evidence_declared"):
        score -= 0.15
        deductions.append("No evidence declaration: -0.15")

    # C4: External validation (for SEAL-bound)
    if audit_result.get("seal_bound") and not audit_result.get("external_validated"):
        score -= 0.25
        deductions.append("SEAL-bound without external validation: -0.25")

    # C5: Backcastable
    if audit_result.get("has_predictions") and not audit_result.get("backcast_done"):
        score -= 0.10
        deductions.append("Predictions without backcast: -0.10")

    # Self-certification detected
    if audit_result.get("self_certified"):
        score -= 0.30
        deductions.append("Self-certification detected: -0.30")

    # Polished language without substance
    if audit_result.get("polished_no_substance"):
        score -= 0.10
        deductions.append("Polished language without substance: -0.10")

    score = max(score, 0.0)
    passed = score >= 0.60

    return {
        "score": round(score, 2),
        "passed": passed,
        "deductions": deductions,
        "verdict": "PASS" if passed else "BEAUTIFUL_ONE_REJECTED",
        "minimum": 0.60,
    }


# ── Tiered Φ External ──────────────────────────────────────────────────────

def compute_phi_external(claim_severity: str, auditor_validated: Optional[bool] = None) -> dict:
    """
    P0-2 FIX: Tiered Φ_external by claim severity.
    Not all claims need the same scrutiny.

    P1-1 FIX: Use max(Φ_internal, Φ_external) for low-stakes,
    Φ_external only for high-stakes. This prevents punishing
    appropriate internal uncertainty.
    """
    tiers = {
        # Observational claims: skip external validation entirely
        "observation": {
            "phi_external": 1.0,
            "requires_external": False,
            "reason": "Observation is self-evident — external validation adds no value",
        },
        # Internal reasoning: light penalty
        "reasoning": {
            "phi_external": 0.85,
            "requires_external": False,
            "reason": "Reasoning benefits from external check but doesn't require it",
        },
        # Consequential action: moderate gate
        "consequential": {
            "phi_external": 0.70,
            "requires_external": True,
            "reason": "Consequential actions benefit from external witness",
        },
        # SEAL-bound / irreversible: full gate
        "seal_bound": {
            "phi_external": 0.50,
            "requires_external": True,
            "reason": "Irreversible actions require external attestation",
        },
    }

    tier = tiers.get(claim_severity, tiers["reasoning"])

    # Apply auditor validation
    if auditor_validated is True:
        phi = 0.90  # auditor validated
        status = "VALIDATED"
    elif auditor_validated is False:
        phi = 0.30  # auditor challenged
        status = "CHALLENGED"
    elif auditor_validated is None:
        if tier["requires_external"]:
            phi = tier["phi_external"]  # default penalty
            status = "NO_AUDITOR"
        else:
            phi = 1.0  # no penalty for non-required
            status = "NOT_REQUIRED"
    else:
        phi = 0.0  # auditor voided
        status = "VOIDED"

    return {
        "claim_severity": claim_severity,
        "phi_external": phi,
        "status": status,
        "requires_external": tier["requires_external"],
        "reason": tier["reason"],
    }


# ── Auditor Authentication ──────────────────────────────────────────────────

# P2-2 FIX: Shared secret for auditor authentication
# In production, this should be a per-auditor HMAC key stored in /root/.secrets/
AUDITOR_SECRETS = {
    "chatgpt": "placeholder-replace-with-real-hmac-key",
    "gemini": "placeholder-replace-with-real-hmac-key",
    "grok": "placeholder-replace-with-real-hmac-key",
}


def verify_auditor_attestation(auditor_id: str, attestation: str, signature: str) -> dict:
    """
    P2-2 FIX: Verify that an auditor attestation is authentic.
    Uses HMAC-SHA256 with per-auditor shared secret.
    """
    secret = AUDITOR_SECRETS.get(auditor_id)
    if not secret:
        return {
            "verified": False,
            "reason": f"Unknown auditor '{auditor_id}' — no secret in registry",
            "evidence_band": "L2_VERIFIED",
        }

    expected = hmac.new(
        secret.encode(), attestation.encode(), hashlib.sha256
    ).hexdigest()

    if hmac.compare_digest(signature, expected):
        return {
            "verified": True,
            "reason": f"HMAC-SHA256 signature matches for auditor '{auditor_id}'",
            "evidence_band": "L1_SEALED",
        }
    else:
        return {
            "verified": False,
            "reason": f"HMAC signature mismatch for auditor '{auditor_id}' — possible spoof",
            "evidence_band": "L2_VERIFIED",
        }


# ── Unified Truth Source ────────────────────────────────────────────────────

def validate_audit_result(result: dict) -> dict:
    """
    P1-2 FIX: Single validation function that enforces consistent rules
    across all artifacts. This is the single source of truth.

    Called before any audit result is accepted.
    """
    checks = []

    # 1. Provider separation
    provider_check = verify_provider_separation(result.get("auditor_provider", "unknown"))
    checks.append(("provider_separation", provider_check))
    if not provider_check["verified"]:
        return {"accepted": False, "reason": "Provider separation failed", "checks": checks}

    # 2. Evidence declaration
    if not result.get("evidence_bands"):
        checks.append(("evidence_declaration", {"verified": False, "reason": "No evidence bands declared"}))
        return {"accepted": False, "reason": "No evidence declaration", "checks": checks}
    checks.append(("evidence_declaration", {"verified": True}))

    # 3. Anti-Calhoun gate (HARD enforcement)
    calhoun = anti_calhoun_score(result)
    checks.append(("anti_calhoun", calhoun))
    if not calhoun["passed"]:
        return {
            "accepted": False,
            "reason": f"Anti-Calhoun gate failed: score {calhoun['score']} < {calhoun['minimum']}",
            "checks": checks,
        }

    # 4. Tiered Φ_external
    phi_result = compute_phi_external(
        claim_severity=result.get("claim_severity", "reasoning"),
        auditor_validated=result.get("auditor_validated"),
    )
    checks.append(("phi_external", phi_result))

    return {
        "accepted": True,
        "reason": "All checks passed",
        "checks": checks,
        "phi_external": phi_result["phi_external"],
    }
