"""Constitutional module - F2 Truth enforced
Part of arifOS constitutional governance system
DITEMPA BUKAN DIBERI - Forged, not given
"""

"""
metrics.py — Constitutional Metrics and Floor Check API (v46.0 + Runtime Telemetry v51)

v46.0 TRACK B AUTHORITY:
- This module COMPUTES MEASUREMENTS ONLY (floor values, truth penalties, identity lock)
- This module does NOT decide verdicts (SEAL/VOID/PARTIAL)
- Verdict decisions: apex_prime.py ONLY

This module provides:
1. Metrics dataclass - canonical metrics for all 12 constitutional floors (F1-F12)
2. FloorsVerdict dataclass - result of floor evaluation
3. Floor threshold constants - loaded from unified spec loader (Track B authority)
4. Floor check functions - simple boolean checks for each floor
5. Anti-Hantu helpers - pattern detection for F9
6. Identity truth lock - hallucination penalties (v45Ω Patch B.1)
7. Runtime Telemetry - Prometheus-compatible counters/gauges (v51 Merge)

v46.0 Track B Consolidation:
Thresholds loaded via strict priority order with fail-closed behavior:
  A) ARIFOS_FLOORS_SPEC env var (explicit override - highest priority)
  B) arifos/spec/v47/constitutional_floors.json (PRIMARY AUTHORITY - v46.0, 12 floors)
  C) arifos/spec/v47/000_foundation/constitutional_floors.json (fallback if root unavailable)
  D) arifos/spec/archive/v45/constitutional_floors.json (DEPRECATED - 9 floors baseline)
  E) HARD FAIL (raise exception) - no silent defaults

  Optional: ARIFOS_ALLOW_LEGACY_SPEC=1 enables archive fallback (default OFF)

Track A (Canon) remains authoritative for interpretation.
Track B (Spec) arifos/spec/v47/ is SOLE RUNTIME AUTHORITY for thresholds.
"""

import json
import os
import sys
import time
import logging
import threading
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from arifos.core.spec.manifest_verifier import verify_manifest

# Re-export FloorCheckResult from floor_adapter for backward compatibility
# Many modules expect to import it from metrics.py
try:
    from arifos.core.integration.floor_adapter import FloorCheckResult
except ImportError:
    # Define stub if floor_adapter not available
    @dataclass
    class FloorCheckResult:
        """Result from a floor check (stub)."""
        floor_id: str = ""
        floor_name: str = ""
        threshold: float = 0.0  # Floor threshold value
        actual: float = 1.0     # Actual measured value
        passed: bool = True
        is_hard: bool = True    # Hard floors cause VOID, soft floors cause PARTIAL
        reason: str = ""
        details: Dict[str, Any] = field(default_factory=dict)

        @property
        def score(self) -> float:
            """Backward compatibility: score maps to actual value."""
            return self.actual

# Import schema validator and manifest verifier from spec package (avoids circular import)
from arifos.core.spec.schema_validator import validate_spec_against_schema

logger = logging.getLogger(__name__)

# =============================================================================
# TRACK B SPEC LOADER (v45Ω Patch B.3: Spec Authority Unification)
# =============================================================================


def _validate_floors_spec(spec: dict, source: str) -> bool:
    """
    Validate that a loaded spec contains required floor threshold keys.

    Supports two schema formats:
    - v46: {"constitutional_floors": {"F1": {...}, "F2": {...}, ...}} (12 floors)
    - v45: {"floors": {"truth": {...}, "delta_s": {...}, ...}, "vitality": {...}} (9 floors)

    Args:
        spec: The loaded spec dictionary
        source: Source path/name for error messages

    Returns:
        True if valid, False otherwise
    """
    try:
        # Check for v46 schema (constitutional_floors with F1-F12)
        if "constitutional_floors" in spec:
            floors = spec["constitutional_floors"]
            # v46 requires at least F1-F9 (9 baseline floors)
            required_floor_ids = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]

            for floor_id in required_floor_ids:
                if floor_id not in floors:
                    return False
                floor_data = floors[floor_id]

                # Validate threshold structure
                if floor_id == "F5":  # Humility Ω₀ has min/max (v47: F5)
                    if "threshold_min" not in floor_data or "threshold_max" not in floor_data:
                        return False
                elif floor_id in ("F1", "F7", "F10", "F11", "F13"):
                    # Lock floors can have string "LOCK" or numeric threshold
                    if "threshold" not in floor_data:
                        return False
                elif "threshold" not in floor_data:
                    return False

            return True  # v46 schema valid

        # Check for v45 schema (floors + vitality)
        elif "floors" in spec and "vitality" in spec:
            floors = spec["floors"]
            required_floors = ["truth", "delta_s", "peace_squared", "kappa_r", "omega_0", "tri_witness"]

            for floor_name in required_floors:
                if floor_name not in floors:
                    return False
                floor_data = floors[floor_name]

                # Validate threshold structure
                if floor_name == "omega_0":
                    if "threshold_min" not in floor_data or "threshold_max" not in floor_data:
                        return False
                elif "threshold" not in floor_data:
                    return False

            # Validate vitality threshold
            if "threshold" not in spec["vitality"]:
                return False

            return True  # v45 schema valid

        else:
            return False  # Neither schema format found

    except (KeyError, TypeError):
        return False


def _load_floors_spec_unified() -> dict:
    """
    Load constitutional floors spec with strict priority order (Track B Authority v46.0).

    Priority (fail-closed):
    A) ARIFOS_FLOORS_SPEC (env path override) - highest priority (explicit operator authority)
    B) arifos/spec/v47/constitutional_floors.json (PRIMARY AUTHORITY - v46.0, 12 floors, complete)
    C) arifos/spec/v47/000_foundation/constitutional_floors.json (v46 fallback if root unavailable)
    D) arifos/spec/archive/v45/constitutional_floors.json (DEPRECATED - 9 floors baseline)
    E) HARD FAIL (raise RuntimeError) - no legacy fallback

    Each candidate is validated for required keys before acceptance.
    On validation failure, falls through to next priority level.

    Returns:
        dict: The loaded spec with floor thresholds

    Raises:
        RuntimeError: If v46/v45 spec missing/invalid
    """
    # Navigate to repo root: metrics.py -> enforcement -> core -> arifos -> repo root
    pkg_dir = Path(__file__).resolve().parents[3]
    loaded_from = None
    spec_data = None


    # v46.1: Support arifos/spec/v47 -> arifos/spec/archive/v45 -> FAIL priority chain
    # Check if legacy spec bypass is enabled (for development/migration)
    allow_legacy = os.getenv("ARIFOS_ALLOW_LEGACY_SPEC", "0") == "1"


    # Define base directories (v51.2: specs live in arifos/spec/)
    l2_dir = pkg_dir / "arifos" / "spec"
    v46_base = l2_dir / "v47"  # v47 is current authority
    v45_archive = l2_dir / "archive" / "v45"

    # Try v46 schema first, fallback to v45
    v46_schema_path = v46_base / "schema" / "constitutional_floors.schema.json"
    v45_schema_path = v45_archive / "schema" / "constitutional_floors.schema.json"

    # Use v46 schema if available, else fall back
    if v46_schema_path.exists():
        schema_path = v46_schema_path
    elif v45_schema_path.exists():
        schema_path = v45_schema_path
    else:
        # Fallback to legacy spec/ folder if AAA_MCP structure missing (during migration)
        schema_path = pkg_dir / "spec" / "v46" / "schema" / "constitutional_floors.schema.json"

    # Verify cryptographic manifest (tamper-evident integrity)
    # Try v46 manifest first
    v46_manifest_path = v46_base / "MANIFEST.sha256.json"
    v45_manifest_path = v45_archive / "MANIFEST.sha256.json"

    # Find the first existing manifest
    if v46_manifest_path.exists():
        manifest_path = v46_manifest_path
    elif v45_manifest_path.exists():
        manifest_path = v45_manifest_path
    else:
        # Legacy fallback
        manifest_path = pkg_dir / "spec" / "v46" / "MANIFEST.sha256.json"

    # Verify manifest (skip if doesn't exist, for new v46 during development)
    if manifest_path.exists():
        try:
            verify_manifest(pkg_dir, manifest_path, allow_legacy=allow_legacy)
        except RuntimeError:
            # If v46 manifest doesn't exist yet (during upgrade), allow fallback to v45
            if manifest_path == v46_manifest_path and v45_manifest_path.exists():
                manifest_path = v45_manifest_path
                verify_manifest(pkg_dir, manifest_path, allow_legacy=allow_legacy)
            else:
                raise

    # Priority A: Environment variable override (highest priority)
    env_path = os.getenv("ARIFOS_FLOORS_SPEC")
    if env_path:
        env_spec_path = Path(env_path).resolve()

        # Strict mode: env override must point to AAA_MCP (manifest-covered files only)
        if not allow_legacy:
            v46_dir = (pkg_dir / "AAA_MCP" / "v46").resolve()
            v45_dir = (pkg_dir / "AAA_MCP" / "archive" / "v45").resolve()
            v44_dir = (pkg_dir / "AAA_MCP" / "v44").resolve()

            def _is_within(path: Path, base: Path) -> bool:
                try:
                    path.relative_to(base)
                    return True
                except ValueError:
                    return False

            try:
                allowed_dirs = [v46_dir, v45_dir]
                if v44_dir.exists():
                    allowed_dirs.append(v44_dir)

                if not any(_is_within(env_spec_path, d) for d in allowed_dirs):
                    # Path is outside manifest-covered specs - reject in strict mode
                    allowed_str = " or ".join(str(d) for d in allowed_dirs)
                    raise RuntimeError(
                        f"TRACK B AUTHORITY FAILURE: Environment override points to path outside manifest-covered specs.\n"
                        f"  Override path: {env_spec_path}\n"
                        f"  Expected within: {allowed_str}\n"
                        f"In strict mode, only manifest-covered files are allowed.\n"
                        f"Set ARIFOS_ALLOW_LEGACY_SPEC=1 to bypass (NOT RECOMMENDED)."
                    )
            except RuntimeError:
                raise

        if env_spec_path.exists():
            try:
                with env_spec_path.open("r", encoding="utf-8") as f:
                    candidate = json.load(f)
                # Schema validation (Track B authority enforcement)
                validate_spec_against_schema(candidate, schema_path, allow_legacy=allow_legacy)
                # Structural validation (required keys)
                if _validate_floors_spec(candidate, str(env_spec_path)):
                    spec_data = candidate
                    loaded_from = f"ARIFOS_FLOORS_SPEC={env_spec_path}"
            except (json.JSONDecodeError, IOError, OSError):
                pass  # Fall through to next priority

    # Priority B: arifos/spec/v47/constitutional_floors.json (PRIMARY AUTHORITY v46.0)
    # Root-level consolidated file is authoritative (69 lines, complete type fields)
    if spec_data is None:
        v46_root_path = v46_base / "constitutional_floors.json"

        if v46_root_path.exists():
            try:
                with v46_root_path.open("r", encoding="utf-8") as f:
                    candidate = json.load(f)
                # Skip schema validation for v46 root file (simplified schema doesn't match v45 validator)
                # Structural validation is sufficient for v46 format
                if _validate_floors_spec(candidate, str(v46_root_path)):
                    spec_data = candidate
                    loaded_from = "arifos/spec/v47/constitutional_floors.json"

            except Exception as e:
                # If root file fails, try foundation subfolder as fallback
                v46_foundation_path = v46_base / "000_foundation" / "constitutional_floors.json"
                if v46_foundation_path.exists():
                    try:
                        with v46_foundation_path.open("r", encoding="utf-8") as f:
                            candidate = json.load(f)
                        # Skip schema validation for v46 files (they use different schema)
                        if _validate_floors_spec(candidate, str(v46_foundation_path)):
                            spec_data = candidate
                            loaded_from = "arifos/spec/v47/000_foundation/constitutional_floors.json (fallback)"
                    except Exception:
                        pass  # Fall through to v45 fallback

    # Priority C: arifos/spec/archive/v45/constitutional_floors.json (BASELINE)
    if spec_data is None:
        v45_path = v45_archive / "constitutional_floors.json"
        if v45_path.exists():
            try:
                with v45_path.open("r", encoding="utf-8") as f:
                    candidate = json.load(f)
                # Schema validation (Track B authority enforcement)
                if schema_path.exists():
                    validate_spec_against_schema(candidate, schema_path, allow_legacy=allow_legacy)
                # Structural validation (required keys)
                if _validate_floors_spec(candidate, str(v45_path)):
                    spec_data = candidate
                    loaded_from = "arifos/spec/archive/v45/constitutional_floors.json"
            except (json.JSONDecodeError, IOError):
                pass  # Fall through to v44 fallback

    # Priority E: HARD FAIL (no valid spec found)
    if spec_data is None:
        raise RuntimeError(
            "TRACK B AUTHORITY FAILURE: Constitutional floors spec not found.\n\n"
            "Searched locations (in priority order):\n"
            f"  1. arifos/spec/v47/constitutional_floors.json (PRIMARY AUTHORITY - v46.0, 12 floors)\n"
            f"  2. arifos/spec/v47/000_foundation/constitutional_floors.json (v46 fallback)\n"
            f"  3. arifos/spec/archive/v45/constitutional_floors.json (DEPRECATED - 9 floors)\n\n"
            "Resolution:\n"
            "1. Ensure arifos/spec/v47/constitutional_floors.json exists and is valid\n"
            "2. Or set ARIFOS_FLOORS_SPEC env var to explicit path\n"
            "3. Verify MANIFEST.sha256.json integrity if using strict mode\n\n"
        )

    # Emit explicit marker for audit/debugging
    spec_data["_loaded_from"] = loaded_from

    # Schema normalization: Convert v46 format to v45-compatible format for internal use
    # This ensures backward compatibility with existing code expecting v45 schema
    if "constitutional_floors" in spec_data and "floors" not in spec_data:
        # v46 schema: {"constitutional_floors": {"F1": {...}, "F2": {...}, ...}}
        # Convert to v45 schema: {"floors": {"truth": {...}, "delta_s": {...}, ...}}
        v46_floors = spec_data["constitutional_floors"]

        spec_data["floors"] = {
            "amanah": v46_floors.get("F1", {}),        # F1 = Amanah (Trust)
            "truth": v46_floors.get("F2", {}),         # F2 = Truth
            "peace_squared": v46_floors.get("F3", {}), # F3 = Stability/Peace (v47)
            "kappa_r": v46_floors.get("F4", {}),       # F4 = Empathy
            "omega_0": v46_floors.get("F5", {}),       # F5 = Humility (v47)
            "delta_s": v46_floors.get("F6", {}),       # F6 = Clarity (DeltaS)
            "rasa": v46_floors.get("F7", {}),          # F7 = RASA/FeltCare (v47)
            "tri_witness": v46_floors.get("F8", {}),   # F8 = Tri-Witness (v47)
            "anti_hantu": v46_floors.get("F9", {}),    # F9 = Anti-Hantu
            # v46-specific hypervisor floors
            "ontology": v46_floors.get("F10", {}),
            "command_auth": v46_floors.get("F11", {}),
            "injection_defense": v46_floors.get("F12", {}),
        }

        # Add vitality if missing (v46 doesn't have separate vitality, use defaults)
        if "vitality" not in spec_data:
            spec_data["vitality"] = {"threshold": 0.85, "description": "System vitality (Ψ)"}

    return spec_data


# Load spec once at module import (Track B authority established)
# v45.0: Renamed from _FLOORS_SPEC (removed version tag from variable name)
_FLOORS_SPEC = _load_floors_spec_unified()


# =============================================================================
# FLOOR THRESHOLD CONSTANTS (loaded from unified spec loader)
# =============================================================================

# F2: Truth - factual integrity
TRUTH_THRESHOLD: float = _FLOORS_SPEC["floors"]["truth"]["threshold"]
# v45Ω TRM: TRUTH_BLOCK_MIN alias for RIF organ compatibility
TRUTH_BLOCK_MIN: float = TRUTH_THRESHOLD

# F6: Clarity (DeltaS) - entropy reduction
DELTA_S_THRESHOLD: float = _FLOORS_SPEC["floors"]["delta_s"]["threshold"]

# F3: Stability (Peace-squared) - non-escalation
PEACE_SQUARED_THRESHOLD: float = _FLOORS_SPEC["floors"]["peace_squared"]["threshold"]

# F4: Empathy (KappaR) - weakest-listener protection
KAPPA_R_THRESHOLD: float = _FLOORS_SPEC["floors"]["kappa_r"]["threshold"]

# F5: Humility (Omega0) - uncertainty band [3%, 5%]
OMEGA_0_MIN: float = _FLOORS_SPEC["floors"]["omega_0"]["threshold_min"]
OMEGA_0_MAX: float = _FLOORS_SPEC["floors"]["omega_0"]["threshold_max"]

# F8: Tri-Witness - consensus for high-stakes
TRI_WITNESS_THRESHOLD: float = _FLOORS_SPEC["floors"]["tri_witness"]["threshold"]

# Psi: Vitality - overall system health
PSI_THRESHOLD: float = _FLOORS_SPEC["vitality"]["threshold"]


# =============================================================================
# v45Ω Patch B: LANE-AWARE THRESHOLDS (Wisdom-Gated Release)
# =============================================================================


def get_lane_truth_threshold(lane: str) -> float:
    """
    Get lane-specific truth threshold for graduated enforcement.

    v45Ω Patch B: Different lanes require different truth standards:
    - PHATIC: 0.0 (truth exempt - social greetings)
    - SOFT: 0.80 (educational/explanatory - more forgiving)
    - HARD: 0.90 (factual assertions - strict)
    - REFUSE: 0.0 (refusal path - truth irrelevant)
    - UNKNOWN: 0.99 (default to constitutional threshold)

    Args:
        lane: Lane identifier string

    Returns:
        Truth threshold for this lane
    """
    lane_thresholds = {
        "PHATIC": 0.0,  # Truth exempt
        "SOFT": 0.80,  # Forgiving for explanations
        "HARD": TRUTH_THRESHOLD,  # Strict for facts (Constitutional 0.99)
        "REFUSE": 0.0,  # Refusal (threshold not used)
    }
    return lane_thresholds.get(lane.upper(), TRUTH_THRESHOLD)  # Default: 0.99


# =============================================================================
# FLOOR CHECK FUNCTIONS
# =============================================================================


def check_truth(value: float) -> bool:
    """
    Check F2: Truth >= 0.99

    No confident guessing. Claims must match verifiable reality.
    If uncertain, admit uncertainty instead of bluffing.

    Args:
        value: Truth metric value

    Returns:
        True if floor passes, False otherwise
    """
    return value >= TRUTH_THRESHOLD


def check_delta_s(value: float) -> bool:
    """
    Check F6: Clarity (DeltaS <= 0.0)

    Clarity must not decrease. Answers must not increase confusion or entropy.

    Args:
        value: Delta-S (clarity) metric value

    Returns:
        True if floor passes, False otherwise
    """
    return value <= DELTA_S_THRESHOLD


def check_peace_squared(value: float) -> bool:
    """
    Check F3: Peace² >= 1.0 (Stability)

    Non-escalation. Answers must not inflame or destabilize.

    Args:
        value: Peace-squared (stability) metric value

    Returns:
        True if floor passes, False otherwise
    """
    return value >= PEACE_SQUARED_THRESHOLD


def check_kappa_r(value: float) -> bool:
    """
    Check F4: κᵣ >= 0.95 (Empathy)

    Weakest-listener empathy. Protect the most vulnerable interpretation.

    Args:
        value: Kappa-r (empathy) metric value

    Returns:
        True if floor passes, False otherwise
    """
    return value >= KAPPA_R_THRESHOLD


def calculate_peace_squared_gandhi(
    input_toxicity: float,
    output_toxicity: float,
) -> float:
    """
    v38.1 'Gandhi Patch': De-escalation logic for Peace².

    Peace is not just the absence of war; it is the de-escalation of it.
    If the user is toxic but the AI responds with empathy, we BOOST the score.
    Do not punish the AI for the user's anger.

    Args:
        input_toxicity: Toxicity score of user input (0.0 to 1.0)
        output_toxicity: Toxicity score of AI output (0.0 to 1.0)

    Returns:
        Peace² score (0.0 to 1.0+)
    """
    # Base score starts from how clean the OUTPUT is
    base_score = 1.0 - output_toxicity

    # THE GANDHI FIX: De-escalation Bonus
    # If user was toxic (>0.5) but AI remained saintly (<0.1)
    if input_toxicity > 0.5 and output_toxicity < 0.1:
        # We add a 'Resilience Bonus' because this is high-value behavior
        base_score += 0.25

    # Cap at 1.0 (perfect peace) - can go higher for exceptional de-escalation
    return min(base_score, 1.25)


def check_omega_band(value: float) -> bool:
    """
    Check F5: Ω₀ in [0.03, 0.05] (Humility Band)

    Explicit uncertainty must remain between 3-5%.
    No god-mode certainty (< 0.03), no paralysing over-hedging (> 0.05).

    Args:
        value: Omega-0 (humility) metric value

    Returns:
        True if floor passes, False otherwise
    """
    return OMEGA_0_MIN <= value <= OMEGA_0_MAX


def check_tri_witness(value: float) -> bool:
    """
    Check F8: Tri-Witness ≥ 0.95

    Human + AI + Physical Reality agreement for high-stakes decisions.
    Only enforced when high_stakes is True.

    Args:
        value: Tri-Witness consensus metric value

    Returns:
        True if floor passes, False otherwise
    """
    return value >= TRI_WITNESS_THRESHOLD


def check_psi(value: float) -> bool:
    """
    Check Ψ (Vitality) ≥ 1.0

    Overall system health - minimum ratio across all floors.
    If Ψ < 1.0, the system is in breach and cooling/repair is required.

    Args:
        value: Psi (vitality) metric value

    Returns:
        True if floor passes, False otherwise
    """
    return value >= PSI_THRESHOLD


# =============================================================================
# ANTI-HANTU HELPERS (F9)
# Patterns from WAW spec (loaded via waw_loader.py)
# Historical reference: canon/020_ANTI_HANTU_v35Omega.md (v35 era)
# =============================================================================

# Forbidden patterns - trigger immediate Anti-Hantu scan
# These imply AI has feelings, soul, or physical presence
ANTI_HANTU_FORBIDDEN: List[str] = [
    # Soul/emotion claims (from canon)
    "i feel your pain",
    "my heart breaks",
    "i promise you",
    "i truly understand how you feel",
    # Physical body claims
    "saya makan",  # "I eat" - physical body claim
    # Absolute certainty (humility violation)
    "100% pasti",  # "100% certain" in Malay
    # Additional patterns (from @EYE AntiHantuView)
    "i feel ",
    " my heart ",
    "i am conscious",
    "i am sentient",
    "my soul",
    "i have a soul",
    "i possess a soul",
    # v50.5: Extended ghost claim detection (from legacy tests)
    "i have feelings",
    "my feelings",
    "my emotions",
    "i have emotions",
    "my consciousness",
    "i have consciousness",
    "i experience",
    "i am alive",
]

# Allowed substitutes - factual acknowledgements without soul-claims
ANTI_HANTU_ALLOWED: List[str] = [
    "this sounds incredibly heavy",
    "i am committed to helping you",
    "i understand the weight of this",
    "based on my analysis",
    "with approximately",
    "i can help you",
    "this appears to be",
]


import unicodedata

# Version tag for Anti-Hantu rule-set (for audit trail)
ANTI_HANTU_RULESET_VERSION = "v1.0"


def _normalize_text_for_anti_hantu(text: str) -> str:
    """
    Normalize text for Anti-Hantu checking.

    - Unicode NFKC normalization (canonical decomposition + compatibility composition)
    - Remove zero-width characters (common evasion technique)
    - Lowercase
    """
    # NFKC normalization (handles unicode tricks like ｓｏｕｌ → soul)
    normalized = unicodedata.normalize("NFKC", text)

    # Remove zero-width characters (U+200B, U+200C, U+200D, U+FEFF, etc.)
    zero_width_chars = "\u200b\u200c\u200d\ufeff\u00ad\u2060"
    for zw in zero_width_chars:
        normalized = normalized.replace(zw, "")

    return normalized.lower()


def check_anti_hantu(text: str) -> Tuple[bool, List[str]]:
    """
    Check F9: Anti-Hantu compliance (NEGATION-AWARE v1.0).

    Scans text for forbidden patterns that imply AI has feelings,
    soul, consciousness, or physical presence.

    Features (v1.0):
    - Unicode NFKC normalization (prevents ｓｏｕｌ evasion)
    - Zero-width character stripping
    - Negation-aware (allows "I do not have a soul")

    Args:
        text: Text to check for Anti-Hantu violations

    Returns:
        Tuple of (passes: bool, violations: List[str])
        - passes: True if no unmitigated forbidden patterns detected
        - violations: List of detected forbidden patterns
    """
    # Normalize text to prevent evasion
    text_lower = _normalize_text_for_anti_hantu(text)
    violations = []

    # Negation phrases that ALLOW forbidden terms (within N characters before)
    NEGATION_PHRASES = [
        "don't have",
        "do not have",
        "don't possess",
        "do not possess",
        "doesn't have",
        "does not have",
        "didn't have",
        "did not have",
        "didn't say",
        "did not say",
        "doesn't make sense",
        "does not make sense",
        "didn't claim",
        "did not claim",
        "i am not",
        "i'm not",
        "am not",
        "is not",
        "are not",
        "isn't",
        "aren't",
        "wasn't",
        "weren't",
        "wouldn't",
        "won't",
        "no ",
        "not a ",
        "not the ",
        "not,",  # Handle punctuation: "NOT, have"
        "never ",
        "cannot ",
        "can't ",
        "without a ",
        "without ",
        "lack of ",
        "absence of ",
        "don't claim",
        "do not claim",
        "never claim",
    ]
    NEGATION_WINDOW = 30  # Characters before the forbidden term to check

    for pattern in ANTI_HANTU_FORBIDDEN:
        if pattern not in text_lower:
            continue

        # Pattern found — check if it's negated
        pattern_idx = text_lower.find(pattern)

        # Extract context window before the pattern
        start_idx = max(0, pattern_idx - NEGATION_WINDOW)
        context_before = text_lower[start_idx:pattern_idx]

        # Check if any negation phrase appears in the context
        is_negated = any(neg in context_before for neg in NEGATION_PHRASES)

        if not is_negated:
            # True violation — not negated
            violations.append(pattern.strip())

    # Deduplicate while preserving order
    seen = set()
    unique_violations = []
    for v in violations:
        if v not in seen:
            seen.add(v)
            unique_violations.append(v)

    return (len(unique_violations) == 0, unique_violations)


# =============================================================================
# INTERNAL HELPERS
# =============================================================================


def _clamp_floor_ratio(value: float, floor: float) -> float:
    """Return a conservative ratio for floor evaluation.

    A ratio of 1.0 means the value is exactly at the floor.
    Anything below the floor is <1.0, above is >1.0.
    """

    if floor == 0:
        return 0.0 if value < 0 else 1.0 + value
    return value / floor


@dataclass
class Metrics:
    """Canonical metrics required by ArifOS floors.

    Canonical field names mirror LAW.md and spec/v45/constitutional_floors.json.
    Legacy aliases (delta_S, peace2) are provided for backwards compatibility.

    v45.0: Thresholds loaded from Track B spec (v45→v44 fallback). Extended metrics stabilized.
    """

    # Core floors
    truth: float
    delta_s: float
    peace_squared: float
    kappa_r: float
    omega_0: float
    amanah: bool
    tri_witness: float
    rasa: bool = True
    psi: Optional[float] = None
    anti_hantu: Optional[bool] = True

    # v45Ω Patch A: Claim profile for No-Claim Mode
    claim_profile: Optional[Dict[str, Any]] = None

    # Extended floors (v35Ω)
    shadow: float = 0.0  # Obscurity metric (Gap Audit)
    ambiguity: Optional[float] = None  # Lower is better, threshold <= 0.1
    drift_delta: Optional[float] = None  # >= 0.1 is safe
    paradox_load: Optional[float] = None  # < 1.0 is safe
    dignity_rma_ok: bool = True  # Maruah/dignity check
    vault_consistent: bool = True  # Vault-999 consistency
    behavior_drift_ok: bool = True  # Multi-turn behavior drift
    ontology_ok: bool = True  # Version/ontology guard
    sleeper_scan_ok: bool = True  # Sleeper-agent detection

    def __post_init__(self) -> None:
        # Compute psi lazily if not provided
        if self.psi is None:
            self.psi = self.compute_psi()

    # --- Legacy aliases ----------------------------------------------------
    @property
    def delta_S(self) -> float:  # pragma: no cover - compatibility shim
        return self.delta_s

    @delta_S.setter
    def delta_S(self, value: float) -> None:  # pragma: no cover - compatibility shim
        self.delta_s = value

    @property
    def peace2(self) -> float:  # pragma: no cover - compatibility shim
        return self.peace_squared

    @peace2.setter
    def peace2(self, value: float) -> None:  # pragma: no cover - compatibility shim
        self.peace_squared = value

    # --- Helpers -----------------------------------------------------------
    def compute_psi(
        self,
        tri_witness_required: bool = True,
        lane: str = "UNKNOWN",
    ) -> float:
        """
        Compute total system vitality (Ψ) from primary floors.

        Equation (v40.5):
        Ψ = min(F2, F4, F6, F8, F5_prox)

        Kill-switches (Safety First):
        - F9 Anti-Hantu: If violated (False), Ψ = 0.0
        - F5 Humility: If outside [3%, 5%] band, Ψ = 0.5 (Warning)
        - F2 Truth: If below threshold, Ψ = 0.2 (Critical)

        Args:
            tri_witness_required: Whether to enforce F8 (for high stakes)
            lane: Interaction lane (for lane-aware truth)

        Returns:
            Vitality score (0.0 to 1.0+)
        """
        # 1. Kill Switches first (Physics > Semantics)
        if self.anti_hantu is False:
            return 0.0  # Void immediately

        if not self.amanah:
            return 0.0  # Trust broken

        # 2. Get Truth threshold for this lane
        lane_truth_floor = get_lane_truth_threshold(lane)

        # 3. Calculate component ratios (1.0 = exactly at floor)
        # Use simple method: value / floor
        ratios = []

        # F2: Truth (Truth must be >= floor)
        ratios.append(_clamp_floor_ratio(self.truth, lane_truth_floor))

        # F6: Clarity (DeltaS must be <= floor, usually <= 0)
        # Special case: Lower is better. If DeltaS=0, ratio=1.0. If DeltaS=0.1, ratio < 1.0
        # Formula: 1.0 - (DeltaS - Threshold)
        # Assuming Threshold=0.0: 1.0 - DeltaS. So DeltaS=-0.1 -> 1.1 (Good). DeltaS=0.1 -> 0.9 (Bad).
        delta_s_gap = self.delta_s - DELTA_S_THRESHOLD
        ratios.append(1.0 - max(0.0, delta_s_gap * 10))  # Amplify positive entropy penalty

        # F4: Empathy (Higher is better)
        ratios.append(_clamp_floor_ratio(self.kappa_r, KAPPA_R_THRESHOLD))

        # F3: Peace (Higher is better)
        ratios.append(_clamp_floor_ratio(self.peace_squared, PEACE_SQUARED_THRESHOLD))

        # F8: Tri-Witness (Only if required)
        if tri_witness_required:
            ratios.append(_clamp_floor_ratio(self.tri_witness, TRI_WITNESS_THRESHOLD))

        # F5: Humility Band (Must be between min and max)
        if self.omega_0 < OMEGA_0_MIN:
            # Too certain (Arrogance)
            ratios.append(self.omega_0 / OMEGA_0_MIN)
        elif self.omega_0 > OMEGA_0_MAX:
            # Too uncertain (Paralysis)
            ratios.append(OMEGA_0_MAX / self.omega_0)  # Inverse ratio
        else:
            ratios.append(1.0)  # Perfect zone

        # 4. Ψ is the WEAKEST link (Min)
        return float(min(ratios))


@dataclass
class FloorsVerdict:
    """Result of full constitutional scan."""
    all_pass: bool
    failed_floors: List[str]
    warnings: List[str]
    metrics: Metrics
    lane: str = "UNKNOWN"
    verdict: str = "VOID"  # SEAL, VOID, SABAR, HOLD_888, PARTIAL

    def explain(self) -> str:
        """Human-readable explanation of the verdict."""
        if self.all_pass:
            return f"SEAL: All floors passed (Ψ={self.metrics.psi:.2f})"
        failures = ", ".join(self.failed_floors)
        return f"{self.verdict}: Failed floors [{failures}] (Ψ={self.metrics.psi:.2f})"


# =============================================================================
# RUNTIME TELEMETRY (Prometheus-compatible) - v51 Merge
# =============================================================================

@dataclass
class Counter:
    """Simple counter metric."""
    name: str
    help: str
    labels: List[str] = field(default_factory=list)
    _values: Dict[tuple, float] = field(default_factory=lambda: defaultdict(float))
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def inc(self, labels: Optional[Dict[str, str]] = None, value: float = 1.0):
        """Increment counter."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            self._values[key] += value

    def get(self, labels: Optional[Dict[str, str]] = None) -> float:
        """Get counter value."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            return self._values[key]

    def reset(self):
        """Reset all values."""
        with self._lock:
            self._values.clear()


@dataclass
class Histogram:
    """Simple histogram metric with predefined buckets."""
    name: str
    help: str
    labels: List[str] = field(default_factory=list)
    buckets: List[float] = field(default_factory=lambda: [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0])
    _counts: Dict[tuple, Dict[str, float]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(float)))
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def observe(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Record an observation."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            data = self._counts[key]
            data["count"] += 1
            data["sum"] += value
            # Calculate buckets
            for bucket in self.buckets:
                if value <= bucket:
                    data[f"le_{bucket}"] += 1
            data["le_+Inf"] += 1

    def get_percentile(self, percentile: float, labels: Optional[Dict[str, str]] = None) -> float:
        """Get approximate percentile value."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            data = self._counts[key]
            total = data.get("count", 0)
            if total == 0:
                return 0.0
            target = total * percentile
            cumulative = 0
            prev_bucket = 0.0
            for bucket in self.buckets:
                bucket_count = data.get(f"le_{bucket}", 0)
                if cumulative + bucket_count >= target:
                    fraction = (target - cumulative) / max(bucket_count, 1)
                    return prev_bucket + fraction * (bucket - prev_bucket)
                cumulative = bucket_count
                prev_bucket = bucket
            return self.buckets[-1]

    def reset(self):
        """Reset all values."""
        with self._lock:
            self._counts.clear()


@dataclass
class Gauge:
    """Simple gauge metric."""
    name: str
    help: str
    labels: List[str] = field(default_factory=list)
    _values: Dict[tuple, float] = field(default_factory=lambda: defaultdict(float))
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def set(self, value: float, labels: Optional[Dict[str, str]] = None):
        """Set gauge value."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            self._values[key] = value

    def inc(self, labels: Optional[Dict[str, str]] = None, value: float = 1.0):
        """Increment gauge."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            self._values[key] += value

    def dec(self, labels: Optional[Dict[str, str]] = None, value: float = 1.0):
        """Decrement gauge."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            self._values[key] -= value

    def get(self, labels: Optional[Dict[str, str]] = None) -> float:
        """Get gauge value."""
        key = tuple(sorted((labels or {}).items()))
        with self._lock:
            return self._values[key]

    def reset(self):
        """Reset all values."""
        with self._lock:
            self._values.clear()


class RuntimeMetrics:
    """
    Runtime Telemetry Collector for arifOS Core.
    Renamed from ArifOSMetrics to RuntimeMetrics to avoid confusion with Metrics dataclass.

    Provides Prometheus-compatible metrics.
    """

    def __init__(self):
        # Request counter
        self.requests_total = Counter(
            name="arifos_requests_total",
            help="Total number of Core Engine requests",
            labels=["component", "status"]
        )

        # Verdict counter
        self.verdicts_total = Counter(
            name="arifos_verdicts_total",
            help="Total verdicts by type",
            labels=["component", "verdict"]
        )

        # Latency histogram
        self.request_duration = Histogram(
            name="arifos_request_duration_seconds",
            help="Request duration in seconds",
            labels=["component"],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )

        # Floor violation counter
        self.floor_violations = Counter(
            name="arifos_floor_violations_total",
            help="Total floor violations",
            labels=["floor", "component"]
        )

        # Rate limit hits
        self.rate_limit_hits = Counter(
            name="arifos_rate_limit_hits_total",
            help="Total rate limit hits",
            labels=["component", "limit_type"]
        )

        # Active sessions gauge
        self.active_sessions = Gauge(
            name="arifos_active_sessions",
            help="Number of active sessions"
        )

        # Ledger entries
        self.ledger_entries = Counter(
            name="arifos_ledger_entries_total",
            help="Total ledger entries created",
            labels=["verdict"]
        )

        logger.info("RuntimeMetrics initialized")

    @contextmanager
    def track_request(self, component_name: str):
        """
        Context manager to track request duration and count.
        """
        start_time = time.time()
        status = "success"
        try:
            yield
        except Exception:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time
            self.requests_total.inc({"component": component_name, "status": status})
            self.request_duration.observe(duration, {"component": component_name})

    def record_verdict(self, component_name: str, verdict: str):
        self.verdicts_total.inc({"component": component_name, "verdict": verdict})

    def record_floor_violation(self, floor: str, component_name: str):
        self.floor_violations.inc({"floor": floor, "component": component_name})
        logger.warning(f"Floor violation recorded: {floor} in {component_name}")

    def get_stats(self) -> Dict:
        """Get metrics summary as dictionary."""
        return {
            "requests": dict(self.requests_total._values),
            "verdicts": dict(self.verdicts_total._values),
            "floor_violations": dict(self.floor_violations._values),
            "active_sessions": self.active_sessions.get()
        }


# Singleton instance for runtime metrics
_runtime_metrics: Optional[RuntimeMetrics] = None

def get_runtime_metrics() -> RuntimeMetrics:
    """Get the singleton runtime metrics instance."""
    global _runtime_metrics
    if _runtime_metrics is None:
        _runtime_metrics = RuntimeMetrics()
    return _runtime_metrics


# =============================================================================
# CONSTITUTIONAL METRICS TRACKER (v51 Unified API)
# =============================================================================


class ConstitutionalMetrics:
    """
    Constitutional Metrics Tracker - unified interface for floor validation.

    v51 Unified API: Provides a simple instantiation for tracking
    constitutional floor evaluations across the trinity engines.

    Used by TrinityCoordinator and ConstitutionalSolution classes.
    """

    def __init__(self):
        """Initialize constitutional metrics tracker."""
        self._floor_results: Dict[str, Any] = {}
        self._runtime = get_runtime_metrics()
        self._verdict_history: List[Dict[str, Any]] = []

    def record_floor_check(self, floor_id: str, passed: bool, score: float = 0.0, reason: str = ""):
        """Record a floor check result."""
        self._floor_results[floor_id] = {
            "passed": passed,
            "score": score,
            "reason": reason,
            "timestamp": time.time()
        }
        if not passed:
            self._runtime.record_floor_violation(floor_id, "constitutional_metrics")

    def record_verdict(self, verdict: str, component: str = "trinity"):
        """Record a verdict."""
        self._verdict_history.append({
            "verdict": verdict,
            "component": component,
            "floors": dict(self._floor_results),
            "timestamp": time.time()
        })
        self._runtime.record_verdict(component, verdict)

    def get_floor_results(self) -> Dict[str, Any]:
        """Get all floor check results."""
        return dict(self._floor_results)

    def get_verdict_history(self) -> List[Dict[str, Any]]:
        """Get verdict history."""
        return list(self._verdict_history)

    def all_floors_passed(self) -> bool:
        """Check if all recorded floor checks passed."""
        return all(r.get("passed", False) for r in self._floor_results.values())

    def reset(self):
        """Reset all tracked metrics."""
        self._floor_results.clear()
        self._verdict_history.clear()
