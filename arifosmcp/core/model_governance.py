"""
arifosmcp/core/model_governance.py — F11 Model Governance Loader
================================================================

Loads model_governance.yaml as the single source of truth for
model authority levels, allowed tools, forbidden roles, and
output requirements.

Eureka 4: Every model used by arifOS has a governance card.
"DITEMpa bukan diberi" — governance is forged from evidence,
not declared by the model itself.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

log = logging.getLogger(__name__)

# ── YAML loading (lazy singleton) ───────────────────────────────────────────────

_GOVERNANCE_CACHE: dict[str, Any] | None = None


def _load_governance() -> dict[str, Any]:
    """
    Load model_governance.yaml. Cached after first load.
    File path is resolved relative to this file's directory.
    """
    global _GOVERNANCE_CACHE
    if _GOVERNANCE_CACHE is not None:
        return _GOVERNANCE_CACHE

    yaml_path = Path(__file__).parent / "model_governance.yaml"
    if not yaml_path.exists():
        log.warning("model_governance.yaml not found at %s", yaml_path)
        _GOVERNANCE_CACHE = {"models": {}, "global_constraints": {}}
        return _GOVERNANCE_CACHE

    try:
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        _GOVERNANCE_CACHE = data or {"models": {}, "global_constraints": {}}
        log.debug("Loaded %d model governance cards", len(_GOVERNANCE_CACHE.get("models", {})))
        return _GOVERNANCE_CACHE
    except Exception as exc:
        log.error("Failed to load model_governance.yaml: %s", exc)
        _GOVERNANCE_CACHE = {"models": {}, "global_constraints": {}}
        return _GOVERNANCE_CACHE


# ── Public API ─────────────────────────────────────────────────────────────────


def get_governance_card(model_id: str) -> dict[str, Any]:
    """
    Return the governance card for a specific model.

    If the model is not listed in model_governance.yaml, returns
    the default card: instrument_only + all forbidden roles.

    Args:
        model_id: exact model identifier (e.g. "aisingapore/Qwen-SEA-LION-v4-32B-IT")
    Returns:
        dict with keys: provider, role, authority, allowed_tools,
        forbidden_roles, rate_limit, fallback, output_required
    """
    data = _load_governance()
    models = data.get("models", {})

    # Exact match first
    if model_id in models:
        return models[model_id]

    # Case-insensitive fallback scan
    model_lower = model_id.lower()
    for known, card in models.items():
        if known.lower() == model_lower:
            return card

    # Unknown model — return safe default (F11 F13 conservative fallback)
    log.debug("No governance card for model '%s', using default", model_id)
    return {
        "provider": "unknown",
        "role": "unknown_witness",
        "authority": "instrument_only",
        "allowed_tools": [],
        "forbidden_roles": [
            "sovereign_judge",
            "irreversible_executor",
            "vault_sealer",
        ],
        "rate_limit": "unknown",
        "fallback": [],
        "output_required": [
            "schema_valid",
            "uncertainty",
            "human_decision_required",
            "raw_output_hash",
        ],
    }


def get_global_constraints() -> dict[str, Any]:
    """Return global constraints that apply to all models."""
    data = _load_governance()
    return data.get("global_constraints", {})


def get_evidence_levels() -> dict[str, str]:
    """Return the evidence level ladder."""
    data = _load_governance()
    return data.get("evidence_levels", {})


def model_is_allowed(model_id: str, tool_name: str) -> bool:
    """
    Check if a model is allowed to use a specific tool.
    Returns True if tool is in allowed_tools, False otherwise.
    Unknown models return False (conservative).
    """
    card = get_governance_card(model_id)
    allowed = card.get("allowed_tools", [])
    # Wildcard check
    if "*" in allowed:
        return True
    return tool_name in allowed


def model_forbidden_as(model_id: str, role: str) -> bool:
    """
    Check if a model is forbidden from扮演 a specific role.
    Returns True if the role is in forbidden_roles.
    """
    card = get_governance_card(model_id)
    return role in card.get("forbidden_roles", [])


__all__ = [
    "get_governance_card",
    "get_global_constraints",
    "get_evidence_levels",
    "model_is_allowed",
    "model_forbidden_as",
]
