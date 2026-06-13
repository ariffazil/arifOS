"""
Rasa Contract Wiring Configuration — ARIF_RASA_WIRING_CONFIG_v1

DITEMPA BUKAN DIBERI — Forged, Not Given.

Feature-flagged telemetry and enforcement configuration for the
Rasa Contract kernel wiring. Reads from environment variables
RASA_WIRING_ENABLED and RASA_CONTRACT_MODE.

Two-level gating:
  1. RASA_WIRING_ENABLED  — master kill-switch (default: unset/OFF)
  2. RASA_CONTRACT_MODE   — behavioral mode when enabled

Modes (only active when RASA_WIRING_ENABLED is truthy):
  OFF             — No wiring, no telemetry, zero overhead (default when unset)
  SHADOW          — Hooks run, telemetry emitted, zero output modification
  ENFORCE_CRISIS  — Enforce CRISIS risk band only
  ENFORCE_DISTRESS — Enforce CRISIS + DISTRESS risk bands
  ENFORCE_ALL     — Full pipeline enforcement (CRISIS + DISTRESS + SAFE)

Rollout path:
  OFF → SHADOW (observe) → ENFORCE_CRISIS → ENFORCE_DISTRESS → ENFORCE_ALL

CONSTITUTIONAL BINDING:
  - F1 AMANAH:  Default is OFF (safest, no changes, no overhead)
  - F13 SOVEREIGN: Human must opt-in to all non-OFF modes
  - F9 ANTIHANTU: No consciousness claims in config
  - F10 ONTOLOGY: No soul/feelings claims in config
"""

from __future__ import annotations

import os
from enum import Enum


class RasaContractMode(str, Enum):
    """Feature flag modes for Rasa Contract enforcement."""

    OFF = "off"  # No wiring, no telemetry, zero overhead
    SHADOW = "shadow"  # Hooks run, telemetry emitted, no output change
    ENFORCE_CRISIS = "enforce_crisis"  # Only enforce CRISIS risk band
    ENFORCE_DISTRESS = "enforce_distress"  # Enforce CRISIS + DISTRESS
    ENFORCE_ALL = "enforce_all"  # Full pipeline enforcement


def is_rasa_wiring_enabled() -> bool:
    """Check if rasa wiring is enabled at all (master kill-switch).

    Reads RASA_WIRING_ENABLED env var. Any truthy value
    (1, true, yes, on, enabled) activates the wiring.

    When disabled: zero overhead — no hooks called, no telemetry,
    no imports of rasa modules.

    Returns:
        True if rasa wiring should be active.
    """
    val = os.environ.get("RASA_WIRING_ENABLED", "").strip().lower()
    return val in ("1", "true", "yes", "on", "enabled")


def get_rasa_contract_mode() -> RasaContractMode:
    """Read the effective RasaContractMode.

    Priority:
      0. If RASA_WIRING_ENABLED is falsy → OFF (master kill-switch)
      1. Environment variable RASA_CONTRACT_MODE
      2. Config file /root/arifOS/config/rasa_contract.yaml (mode key)
      3. Default: SHADOW (when enabled but mode unspecified)

    Returns:
        RasaContractMode enum value.
    """
    # 0. Master kill-switch
    if not is_rasa_wiring_enabled():
        return RasaContractMode.OFF

    # 1. Environment variable
    env_val = os.environ.get("RASA_CONTRACT_MODE", "").strip().lower()
    if env_val:
        try:
            return RasaContractMode(env_val)
        except ValueError:
            pass  # Fall through to config file / default

    # 2. Config file fallback
    config_path = "/root/arifOS/config/rasa_contract.yaml"
    try:
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
        mode_val = config.get("mode", "").strip().lower()
        if mode_val:
            try:
                return RasaContractMode(mode_val)
            except ValueError:
                pass
    except Exception:
        pass  # File missing, YAML error, etc. — fall through to default

    # 3. Default when enabled
    return RasaContractMode.SHADOW


def mode_allows_enforcement(mode: RasaContractMode, risk_band_value: str) -> bool:
    """Check if the current mode allows enforcement for a given risk band.

    Args:
        mode: Current RasaContractMode.
        risk_band_value: Risk band string value (safe, distress, crisis).

    Returns:
        True if the mode allows enforcement for this risk band.
    """
    risk_band_lower = risk_band_value.lower()

    if mode in (RasaContractMode.OFF, RasaContractMode.SHADOW):
        return False

    if mode == RasaContractMode.ENFORCE_CRISIS:
        return risk_band_lower == "crisis"

    if mode == RasaContractMode.ENFORCE_DISTRESS:
        return risk_band_lower in ("crisis", "distress")

    if mode == RasaContractMode.ENFORCE_ALL:
        return True  # All risk bands enforced

    return False


def mode_allows_telemetry(mode: RasaContractMode) -> bool:
    """Check if telemetry should be emitted under this mode.

    OFF → no telemetry. All other modes → telemetry active.

    Args:
        mode: Current RasaContractMode.

    Returns:
        True if telemetry should be active.
    """
    return mode != RasaContractMode.OFF


__all__ = [
    "RasaContractMode",
    "is_rasa_wiring_enabled",
    "get_rasa_contract_mode",
    "mode_allows_enforcement",
    "mode_allows_telemetry",
]
