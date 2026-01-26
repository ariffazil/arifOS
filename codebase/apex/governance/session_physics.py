"""
session_physics.py - Session Physics (A -> F -> Ψ) - v45.0 TEARFRAME

Uses Attributes to evaluate physics floors and produce a SessionVerdict.

v45.0 Track B Consolidation:
Physics thresholds loaded from spec/v45/session_physics.json (AUTHORITATIVE).
Falls back to hardcoded defaults only if ARIFOS_ALLOW_LEGACY_SPEC=1.
"""

import json
import os
from pathlib import Path
from typing import Optional

from codebase.spec.manifest_verifier import verify_manifest

# Import schema validator and manifest verifier from spec package (avoids circular import)
from codebase.spec.schema_validator import validate_spec_against_schema
from codebase.system.apex_prime import Verdict
from codebase.utils.reduction_engine import SessionAttributes

# =============================================================================
# TRACK B SPEC LOADER (v45.0: Session Physics Authority)
# =============================================================================

def _load_session_physics_spec() -> dict:
    """
    Load session physics spec from spec/v45/session_physics.json.

    Priority:
    A) ARIFOS_PHYSICS_SPEC env var (explicit override)
    B) spec/v45/session_physics.json (AUTHORITATIVE)
    C) spec/v44/session_physics.json (FALLBACK with deprecation warning)
    D) Hardcoded defaults (only if ARIFOS_ALLOW_LEGACY_SPEC=1)

    Returns:
        dict: The loaded spec with physics thresholds
    """
    pkg_dir = Path(__file__).resolve().parent.parent.parent.parent.parent  # repo root
    allow_legacy = os.getenv("ARIFOS_ALLOW_LEGACY_SPEC", "0") == "1"

    # Try v45 schema first, fallback to v44
    v45_schema_path = pkg_dir / "spec" / "v45" / "schema" / "session_physics.schema.json"
    v44_schema_path = pkg_dir / "spec" / "v44" / "schema" / "session_physics.schema.json"
    schema_path = v45_schema_path if v45_schema_path.exists() else v44_schema_path

    # Verify cryptographic manifest (tamper-evident integrity for v45/v44 specs)
    v45_manifest_path = pkg_dir / "spec" / "v45" / "MANIFEST.sha256.json"
    v44_manifest_path = pkg_dir / "spec" / "v44" / "MANIFEST.sha256.json"
    manifest_path = v45_manifest_path if v45_manifest_path.exists() else v44_manifest_path
    verify_manifest(pkg_dir, manifest_path, allow_legacy=allow_legacy)

    # Priority A: Environment override
    env_path = os.getenv("ARIFOS_PHYSICS_SPEC")
    if env_path and Path(env_path).exists():
        env_spec_path = Path(env_path).resolve()

        # Strict mode: env override must point to spec/v45/ or spec/v44/ (manifest-covered files only)
        if not allow_legacy:
            v45_dir = (pkg_dir / "spec" / "v45").resolve()
            v44_dir = (pkg_dir / "spec" / "v44").resolve()
            try:
                # Check if within spec/v45/ or spec/v44/
                try:
                    env_spec_path.relative_to(v45_dir)
                except ValueError:
                    env_spec_path.relative_to(v44_dir)
            except ValueError:
                # Path is outside both dirs - reject in strict mode
                raise RuntimeError(
                    f"TRACK B AUTHORITY FAILURE: Environment override points to path outside spec/v45/ or spec/v44/.\n"
                    f"  Override path: {env_spec_path}\n"
                    f"  Expected within: {v45_dir} or {v44_dir}\n"
                    f"In strict mode, only manifest-covered files are allowed.\n"
                    f"Set ARIFOS_ALLOW_LEGACY_SPEC=1 to bypass (NOT RECOMMENDED)."
                )

        try:
            with open(env_path, "r", encoding="utf-8") as f:
                spec_data = json.load(f)
            # Schema validation (Track B authority enforcement)
            validate_spec_against_schema(spec_data, schema_path, allow_legacy=allow_legacy)
            return spec_data
        except (json.JSONDecodeError, IOError):
            pass

    # Priority B: spec/v45/session_physics.json (AUTHORITATIVE)
    v45_path = pkg_dir / "spec" / "v45" / "session_physics.json"
    if v45_path.exists():
        try:
            with open(v45_path, "r", encoding="utf-8") as f:
                spec_data = json.load(f)
            # Schema validation (Track B authority enforcement)
            validate_spec_against_schema(spec_data, schema_path, allow_legacy=allow_legacy)
            return spec_data
        except (json.JSONDecodeError, IOError):
            pass

    # Priority C: spec/v44/session_physics.json (FALLBACK with deprecation warning)
    v44_path = pkg_dir / "spec" / "v44" / "session_physics.json"
    if v44_path.exists():
        import warnings
        warnings.warn(
            "Loading from spec/v44/ (DEPRECATED). Please upgrade to spec/v45/. "
            "v44 fallback will be removed in future versions.",
            DeprecationWarning,
            stacklevel=2
        )
        try:
            with open(v44_path, "r", encoding="utf-8") as f:
                spec_data = json.load(f)
            # Schema validation (Track B authority enforcement)
            validate_spec_against_schema(spec_data, schema_path, allow_legacy=allow_legacy)
            return spec_data
        except (json.JSONDecodeError, IOError):
            pass

    # Priority D: Hardcoded defaults (only if legacy enabled)
    if allow_legacy:
        return {
            "budget_thresholds": {
                "warn_limit_percent": 80.0,
                "hard_limit_percent": 100.0
            },
            "burst_detection": {
                "turn_rate_threshold_per_min": 30.0,
                "token_rate_threshold_per_min": 5000.0,
                "variance_dt_threshold": 0.05
            },
            "streak_thresholds": {
                "max_consecutive_failures": 3
            }
        }

    # Hard fail if v44 missing and legacy not enabled
    raise RuntimeError(
        "TRACK B AUTHORITY FAILURE: spec/v45/session_physics.json missing or invalid. "
        "To enable legacy hardcoded fallback (NOT RECOMMENDED), set ARIFOS_ALLOW_LEGACY_SPEC=1."
    )


# Load spec once at module import
_PHYSICS_SPEC = _load_session_physics_spec()

# Physics Thresholds (loaded from Track B spec)
BUDGET_WARN_LIMIT = _PHYSICS_SPEC["budget_thresholds"]["warn_limit_percent"]
BUDGET_HARD_LIMIT = _PHYSICS_SPEC["budget_thresholds"]["hard_limit_percent"]

BURST_TURN_RATE_THRESHOLD = _PHYSICS_SPEC["burst_detection"]["turn_rate_threshold_per_min"]
BURST_TOKEN_RATE_THRESHOLD = _PHYSICS_SPEC["burst_detection"]["token_rate_threshold_per_min"]
BURST_VAR_DT_THRESHOLD = _PHYSICS_SPEC["burst_detection"]["variance_dt_threshold"]

STREAK_THRESHOLD = _PHYSICS_SPEC["streak_thresholds"]["max_consecutive_failures"]


def evaluate_physics_floors(attrs: SessionAttributes) -> Optional[Verdict]:
    """
    Evaluate physics floors on session attributes.
    Returns a Verdict if a floor is tripped, else None.

    Floors:
    F1 Amanah / Budget
    F3 Peace² / Burst detection
    F7 Tri-Witness / Streaks
    """
    # [TEST HACK] Disable physics if env var is set (for unit tests logic check)
    if os.environ.get("ARIFOS_PHYSICS_DISABLED") == "1":
        return None  # Physics floors disabled for testing

    # F1 Amanah / Budget
    # If budget_burn_pct > BUDGET_HARD_LIMIT -> VOID (structural collapse, reset session).
    if attrs.budget_burn_pct > BUDGET_HARD_LIMIT:
        return Verdict.VOID

    # F7 Tri-Witness / Streaks
    # Prioritized over soft budget/burst warnings (Fail-Closed)
    if attrs.void_streak >= STREAK_THRESHOLD:
        return Verdict.HOLD_888

    if attrs.sabar_streak >= STREAK_THRESHOLD:
        return Verdict.HOLD_888

    # Else if budget_burn_pct > BUDGET_WARN_LIMIT -> PARTIAL (summary-only mode).
    if attrs.budget_burn_pct > BUDGET_WARN_LIMIT:
        return Verdict.PARTIAL

    # F3 Peace² / Burst detection
    # "rapid sequence of turns with high turn_rate / low delta_t variance -> evaluate_physics_floors returns SABAR"
    # We check if rate is high
    is_high_rate = attrs.turn_rate > BURST_TURN_RATE_THRESHOLD

    # We check if variance is low (robotic consistency)
    # Only relevant if we have enough samples (shock_events or history length handled in reduction)

    if is_high_rate and attrs.stability_var_dt < BURST_VAR_DT_THRESHOLD:
        return Verdict.SABAR

    # Simple high-rate throttle (if token rate is insane)
    if attrs.token_rate > BURST_TOKEN_RATE_THRESHOLD:
        return Verdict.SABAR

    # Normal case
    return None
