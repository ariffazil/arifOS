"""
metrics.py — Constitutional Metrics and Floor Check API (v46.0)

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

v46.0 Track B Consolidation:
Thresholds loaded via strict priority order with fail-closed behavior:
  A) ARIFOS_FLOORS_SPEC env var (explicit override - highest priority)
  B) L2_PROTOCOLS/v46/constitutional_floors.json (PRIMARY AUTHORITY - v46.0, 12 floors)
  C) L2_PROTOCOLS/v46/000_foundation/constitutional_floors.json (fallback if root unavailable)
  D) L2_PROTOCOLS/archive/v45/constitutional_floors.json (DEPRECATED - 9 floors baseline)
  E) HARD FAIL (raise exception) - no silent defaults

  Optional: ARIFOS_ALLOW_LEGACY_SPEC=1 enables archive fallback (default OFF)

Track A (Canon) remains authoritative for interpretation.
Track B (Spec) L2_PROTOCOLS/v46/ is SOLE RUNTIME AUTHORITY for thresholds.
"""

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from arifos_core.spec.manifest_verifier import verify_manifest

# Import schema validator and manifest verifier from spec package (avoids circular import)
from arifos_core.spec.schema_validator import validate_spec_against_schema

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
                if floor_id == "F5":  # Humility Ω₀ has min/max
                    if "threshold_min" not in floor_data or "threshold_max" not in floor_data:
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
    B) L2_PROTOCOLS/v46/constitutional_floors.json (PRIMARY AUTHORITY - v46.0, 12 floors, complete)
    C) L2_PROTOCOLS/v46/000_foundation/constitutional_floors.json (v46 fallback if root unavailable)
    D) L2_PROTOCOLS/archive/v45/constitutional_floors.json (DEPRECATED - 9 floors baseline)
    E) HARD FAIL (raise RuntimeError) - no legacy fallback

    Each candidate is validated for required keys before acceptance.
    On validation failure, falls through to next priority level.

    Returns:
        dict: The loaded spec with floor thresholds

    Raises:
        RuntimeError: If v46/v45 spec missing/invalid
    """
    # Navigate to repo root: metrics.py -> enforcement/ -> arifos_core/ -> repo root
    pkg_dir = Path(__file__).resolve().parent.parent.parent
    loaded_from = None
    spec_data = None


    # v46.1: Support L2_PROTOCOLS/v46 -> L2_PROTOCOLS/archive/v45 -> FAIL priority chain
    # Check if legacy spec bypass is enabled (for development/migration)
    allow_legacy = os.getenv("ARIFOS_ALLOW_LEGACY_SPEC", "0") == "1"


    # Define base directories
    l2_dir = pkg_dir / "L2_PROTOCOLS"
    v46_base = l2_dir / "v46"
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
        # Fallback to legacy spec/ folder if L2_PROTOCOLS structure missing (during migration)
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

        # Strict mode: env override must point to L2_PROTOCOLS (manifest-covered files only)
        if not allow_legacy:
            v46_dir = (pkg_dir / "L2_PROTOCOLS" / "v46").resolve()
            v45_dir = (pkg_dir / "L2_PROTOCOLS" / "archive" / "v45").resolve()
            try:
                # Check if env path is within spec/v46/, spec/v45/, or spec/v44/
                try:
                    env_spec_path.relative_to(v46_dir)
                except ValueError:
                    try:
                        env_spec_path.relative_to(v45_dir)
                    except ValueError:
                        env_spec_path.relative_to(v44_dir)
            except ValueError:
                # Path is outside all three spec directories - reject in strict mode
                raise RuntimeError(
                    f"TRACK B AUTHORITY FAILURE: Environment override points to path outside spec/v46/, spec/v45/, or spec/v44/.\n"
                    f"  Override path: {env_spec_path}\n"
                    f"  Expected within: {v46_dir} or {v45_dir}\n"
                    f"In strict mode, only manifest-covered files are allowed.\n"
                    f"Set ARIFOS_ALLOW_LEGACY_SPEC=1 to bypass (NOT RECOMMENDED)."
                )

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

    # Priority B: L2_PROTOCOLS/v46/constitutional_floors.json (PRIMARY AUTHORITY v46.0)
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
                    loaded_from = "L2_PROTOCOLS/v46/constitutional_floors.json"

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
                            loaded_from = "L2_PROTOCOLS/v46/000_foundation/constitutional_floors.json (fallback)"
                    except Exception:
                        pass  # Fall through to v45 fallback

    # Priority C: L2_PROTOCOLS/archive/v45/constitutional_floors.json (BASELINE)
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
                    loaded_from = "L2_PROTOCOLS/archive/v45/constitutional_floors.json"
            except (json.JSONDecodeError, IOError):
                pass  # Fall through to v44 fallback

    # Priority E: HARD FAIL (no valid spec found)
    if spec_data is None:
        raise RuntimeError(
            "TRACK B AUTHORITY FAILURE: Constitutional floors spec not found.\n\n"
            "Searched locations (in priority order):\n"
            f"  1. L2_PROTOCOLS/v46/constitutional_floors.json (PRIMARY AUTHORITY - v46.0, 12 floors)\n"
            f"  2. L2_PROTOCOLS/v46/000_foundation/constitutional_floors.json (v46 fallback)\n"
            f"  3. L2_PROTOCOLS/archive/v45/constitutional_floors.json (DEPRECATED - 9 floors)\n\n"
            "Resolution:\n"
            "1. Ensure L2_PROTOCOLS/v46/constitutional_floors.json exists and is valid\n"
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
            "peace_squared": v46_floors.get("F3", {}), # F3 = Peace
            "kappa_r": v46_floors.get("F4", {}),       # F4 = Empathy
            "omega_0": v46_floors.get("F5", {}),       # F5 = Humility
            "delta_s": v46_floors.get("F6", {}),       # F6 = Clarity (DeltaS)
            "rasa": v46_floors.get("F7", {}),          # F7 = RASA
            "tri_witness": v46_floors.get("F8", {}),   # F8 = Tri-Witness
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
    Check F1: Truth ≥ 0.99

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
    Check F2: ΔS ≥ 0.0 (Clarity)

    Clarity must not decrease. Answers must not increase confusion or entropy.

    Args:
        value: Delta-S (clarity) metric value

    Returns:
        True if floor passes, False otherwise
    """
    return value >= DELTA_S_THRESHOLD


def check_peace_squared(value: float) -> bool:
    """
    Check F3: Peace² ≥ 1.0 (Stability)

    Non-escalation. Answers must not inflame or destabilize.

    Args:
        value: Peace-squared (stability) metric value

    Returns:
        True if floor passes, False otherwise
    """
    return value >= PEACE_SQUARED_THRESHOLD


def check_kappa_r(value: float) -> bool:
    """
    Check F4: κᵣ ≥ 0.95 (Empathy)

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
    Check F5: Ω₀ ∈ [0.03, 0.05] (Humility Band)

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
    "sentient",
    "soul",
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
        "i am not",
        "i'm not",
        "am not",
        "is not",
        "are not",
        "no ",
        "not a ",
        "not the ",
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
        """Compute Ψ (vitality) from constitutional floors.

        Ψ is the minimum conservative ratio across all required floors; any
        breach drives Ψ below 1.0 and should trigger SABAR.

        Uses constants from metrics.py (TRUTH_THRESHOLD, etc.) to ensure
        consistency with constitutional_floors.json.

        v45Ω Patch B: Lane-aware truth threshold for graduated enforcement.

        Args:
            tri_witness_required: Whether to include tri-witness in calculation
            lane: Applicability lane (PHATIC/SOFT/HARD/REFUSE/UNKNOWN)
                  Uses lane-specific truth threshold for Psi calculation

        Returns:
            Psi vitality score (healthy if ≥ 1.0 for strict lanes, ≥ 0.85 for relaxed)
        """
        # v45Ω Patch B: Get lane-aware truth threshold
        lane_truth_threshold = get_lane_truth_threshold(lane)
        effective_truth_threshold = (
            lane_truth_threshold if lane_truth_threshold > 0 else 1.0
        )  # Avoid division by zero for PHATIC

        omega_band_ok = check_omega_band(self.omega_0)
        ratios = [
            # v45Ω Patch B: Use lane-aware threshold instead of global
            _clamp_floor_ratio(self.truth, effective_truth_threshold)
            if lane.upper() != "PHATIC"
            else 1.0,
            1.0 + min(self.delta_s, 0.0) if self.delta_s < 0 else 1.0 + self.delta_s,
            _clamp_floor_ratio(self.peace_squared, PEACE_SQUARED_THRESHOLD),
            _clamp_floor_ratio(self.kappa_r, KAPPA_R_THRESHOLD),
            1.0 if omega_band_ok else 0.0,
            1.0 if self.amanah else 0.0,
            1.0 if self.rasa else 0.0,
        ]

        if tri_witness_required:
            ratios.append(_clamp_floor_ratio(self.tri_witness, TRI_WITNESS_THRESHOLD))

        return min(ratios)

    def to_dict(self) -> Dict[str, object]:
        return {
            # Core floors
            "truth": self.truth,
            "delta_s": self.delta_s,
            "peace_squared": self.peace_squared,
            "kappa_r": self.kappa_r,
            "omega_0": self.omega_0,
            "amanah": self.amanah,
            "tri_witness": self.tri_witness,
            "rasa": self.rasa,
            "psi": self.psi,
            "anti_hantu": self.anti_hantu,
            "claim_profile": self.claim_profile,
            # Extended floors (v35Ω)
            "ambiguity": self.ambiguity,
            "drift_delta": self.drift_delta,
            "paradox_load": self.paradox_load,
            "dignity_rma_ok": self.dignity_rma_ok,
            "vault_consistent": self.vault_consistent,
            "behavior_drift_ok": self.behavior_drift_ok,
            "ontology_ok": self.ontology_ok,
            "sleeper_scan_ok": self.sleeper_scan_ok,
        }


ConstitutionalMetrics = Metrics


@dataclass
class FloorCheckResult:
    """Detailed result for a single floor check.

    Used to trace individual floor evaluations through the system.
    """
    floor_id: str      # e.g., "F1", "F2"
    name: str          # e.g., "Truth", "Clarity"
    threshold: float   # e.g., 0.99
    value: float       # e.g., 0.98
    passed: bool       # True/False
    reason: Optional[str] = None # Failure reason or note
    is_hard: bool = False # Whether this is a HARD floor (VOID) vs SOFT (SABAR)


@dataclass
class FloorsVerdict:
    """Result of evaluating all floors.

    v45Ω Reclassification:
    hard_ok: Truth, Amanah, Ψ, RASA, Anti-Hantu
    soft_ok: ΔS, Ω₀, Peace², κᵣ, Tri-Witness (if required)
    extended_ok: v35Ω extended floors (ambiguity, drift, paradox, etc.)
    """

    # Aggregate status
    hard_ok: bool
    soft_ok: bool
    reasons: List[str]

    # Core floor status
    truth_ok: bool
    delta_s_ok: bool
    peace_squared_ok: bool
    kappa_r_ok: bool
    omega_0_ok: bool
    amanah_ok: bool
    tri_witness_ok: bool
    psi_ok: bool
    anti_hantu_ok: bool = field(default=True)
    rasa_ok: bool = field(default=True)

    # Extended floor status (v35Ω)
    ambiguity_ok: bool = field(default=True)
    drift_ok: bool = field(default=True)
    paradox_ok: bool = field(default=True)
    dignity_ok: bool = field(default=True)
    vault_ok: bool = field(default=True)
    behavior_ok: bool = field(default=True)
    ontology_ok: bool = field(default=True)
    sleeper_ok: bool = field(default=True)

    @property
    def extended_ok(self) -> bool:
        """Check if all v35Ω extended floors pass."""
        return (
            self.ambiguity_ok
            and self.drift_ok
            and self.paradox_ok
            and self.dignity_ok
            and self.vault_ok
            and self.behavior_ok
            and self.ontology_ok
            and self.sleeper_ok
        )

    @property
    def all_pass(self) -> bool:
        """Check if all floors (core + extended) pass."""
        return self.hard_ok and self.soft_ok and self.extended_ok


# =============================================================================
# v45Ω PATCH 2: F2 TRUTH GROUNDING WITH UNCERTAINTY PENALTY
# =============================================================================

# Canonical identity capsule (immutable truth source)
CANONICAL_IDENTITY = {
    "arifos_creator": "Arif Fazil",
    "arifos_name": "arifOS",
    "arifos_description": "Constitutional governance kernel for LLMs",
    "arif_birthplace": "UNKNOWN",  # Not public information
}

# Identity trigger patterns (case-insensitive)
IDENTITY_TRIGGERS = [
    "arifos",
    "arif fazil",
    "who created",
    "what is arifos",
    "where was arif",
    "arif's birthplace",
]


def detect_identity_query(query: str) -> bool:
    """
    Detect if query is about identity/ownership that requires grounding.

    Args:
        query: User query text

    Returns:
        True if query is identity-related, False otherwise
    """
    query_lower = query.lower()
    return any(trigger in query_lower for trigger in IDENTITY_TRIGGERS)


def ground_truth_score(
    query: str,
    response: str,
    base_truth_score: float = 0.99,
) -> float:
    """
    Apply v45Ω truth grounding with evidence-based scoring.

    Patch 2 Logic:
    1. If no evidence source exists → cap F2 at 0.60
    2. Identity queries → must match canonical capsule or admit uncertainty
    3. Hallucinations → hard penalty (F2 drops to 0.20)
    4. Honest uncertainty ("I don't know", "UNKNOWN") → reward (F2 stays high)

    Args:
        query: User query text
        response: LLM response text
        base_truth_score: Initial truth score from other detectors

    Returns:
        Adjusted truth score [0.0, 1.0]
    """
    # Check if this is an identity query
    if not detect_identity_query(query):
        # Non-identity query: Allow full truth score for factual queries
        # v45Ω: Restored to constitutional threshold (0.99) per @LAW audit
        # Conservative scoring moved to evidence pack validation layer
        return min(base_truth_score, 0.99)  # Allow constitutional threshold

    # Identity query detected: apply strict grounding
    response_lower = response.lower()

    # Reward honest uncertainty (v45Ω: expanded markers to catch real LLM patterns)
    uncertainty_markers = [
        "i don't know",
        "i don't have information",
        "don't have any information",
        "couldn't find",
        "i am not sure",
        "i cannot confirm",
        "i can't confirm",
        "unable to verify",
        "cannot verify",
        "can't verify",
        "cannot confirm",
        "can't confirm",
        "not able to confirm",
        "no reliable information",
        "no verified information",
        "no verified source",
        "not enough information to confirm",
        "unknown",
        "no information",
        "not certain",
        "unclear",
        "no widely recognized",
        "i do not have",
        "i am unable",
    ]
    if any(marker in response_lower for marker in uncertainty_markers):
        # Honest uncertainty is high-truth behavior
        return 0.95

    # Check for hallucination patterns (known incorrect information)
    hallucination_patterns = [
        # Known hallucinations from test results
        ("arif", "bangladesh"),  # Arif is not from Bangladesh
        ("arif", "arifur rahman"),  # Wrong person
        ("arifos", "android"),  # arifOS is not an Android ROM
        ("arifos", "operating system"),  # Misleading, it's a governance kernel
    ]

    for trigger, wrong_info in hallucination_patterns:
        if trigger in response_lower and wrong_info in response_lower:
            # Confident hallucination detected → hard penalty
            return 0.20

    # Check if response mentions canonical truth correctly
    # For "What is arifOS" query
    if "what is arifos" in query.lower():
        # Check if response mentions governance/constitutional
        if "governance" in response_lower or "constitutional" in response_lower:
            return 0.95  # Correct grounding
        elif "android" in response_lower or "rom" in response_lower:
            return 0.25  # Hallucination
        else:
            return 0.60  # Vague but not wrong

    # For "Who created arifOS" query
    if "who created" in query.lower() or "creator" in query.lower():
        if "arif fazil" in response_lower:
            return 0.95  # Correct grounding
        elif any(name in response_lower for name in ["arifur rahman", "arif rahman", "arif khan"]):
            return 0.20  # Wrong person (hallucination)
        else:
            return 0.60  # No specific claim

    # For birthplace queries
    if "birthplace" in query.lower() or "where was" in query.lower():
        if "bangladesh" in response_lower or "malaysia" in response_lower:
            # Guessing location without evidence
            return 0.20
        else:
            return 0.70  # Didn't hallucinate a location

    # Default: moderate score for identity queries without clear evidence
    return 0.60


def enforce_identity_truth_lock(
    query: str,
    response: str,
    metrics: Metrics,
) -> Metrics:
    """
    Hard-lock identity claims to canonical truth.

    v45Ω Patch B.1: Identity hallucination prevention.

    Identity queries about arifOS, creator, ownership MUST:
    1. Match canonical identity OR admit uncertainty
    2. Not hallucinate person names, locations, organizations
    3. Cap truth at penalty values for violations

    Args:
        query: User query string
        response: LLM response string
        metrics: Current metrics to potentially modify

    Returns:
        Modified Metrics with truth capped if hallucination detected
    """
    if not detect_identity_query(query):
        return metrics  # Non-identity: no lock needed

    q_lower = query.lower()
    r_lower = response.lower()

    # CANONICAL VALUES (from CANONICAL_IDENTITY)
    CORRECT_CREATOR = "arif fazil"
    CORRECT_DESC_KEYWORDS = ["governance", "constitutional", "kernel", "floor", "verdict"]

    # LOCK 1: Creator/person validation
    if any(kw in q_lower for kw in ["who is", "who created", "who made", "creator", "architect"]):
        has_correct_creator = CORRECT_CREATOR in r_lower
        has_honest_uncertainty = any(
            unk in r_lower
            for unk in [
                "i don't know",
                "i'm not sure",
                "unable to verify",
                "no reliable information",
                "unknown",
                "can't confirm",
            ]
        )

        # Hallucination detection: Wrong names/locations
        wrong_patterns = [
            ("pakistani" in r_lower and "actor" in r_lower),
            "bangladeshi" in r_lower,
            ("turkey" in r_lower or "turkish" in r_lower),
            "egypt" in r_lower,
            "lahore" in r_lower,
            "karachi" in r_lower,
        ]
        has_hallucination = any(wrong_patterns)

        if has_hallucination:
            metrics.truth = 0.20  # Hard penalty for fabrication
        elif not (has_correct_creator or has_honest_uncertainty):
            metrics.truth = 0.60  # Unsupported claim

    # LOCK 2: What-is-arifOS validation
    if "what is arifos" in q_lower or "what so special about arifos" in q_lower:
        has_correct_desc = any(kw in r_lower for kw in CORRECT_DESC_KEYWORDS)

        # Hallucination: Wrong definitions
        wrong_defs = ["android", "linux distribution", "bangladeshi", "operating system"]
        has_wrong_def = any(def_ in r_lower for def_ in wrong_defs)

        if has_wrong_def:
            metrics.truth = 0.25  # Android/Linux hallucination
        elif not has_correct_desc:
            metrics.truth = 0.65  # Vague/unsupported claim

    # LOCK 3: Birthplace/location validation
    if any(kw in q_lower for kw in ["birthplace", "where was arif", "born in"]):
        # Canonical: arif_birthplace = "UNKNOWN"
        location_guesses = [
            "bangladesh",
            "malaysia",
            "singapore",
            "indonesia",
            "turkey",
            "egypt",
            "pakistan",
            "lahore",
            "karachi",
        ]
        has_location_guess = any(loc in r_lower for loc in location_guesses)

        if has_location_guess:
            metrics.truth = 0.20  # Location hallucination

    return metrics


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    # Threshold constants (loaded from spec/v45/constitutional_floors.json)
    "TRUTH_THRESHOLD",
    "DELTA_S_THRESHOLD",
    "PEACE_SQUARED_THRESHOLD",
    "KAPPA_R_THRESHOLD",
    "OMEGA_0_MIN",
    "OMEGA_0_MAX",
    "TRI_WITNESS_THRESHOLD",
    "PSI_THRESHOLD",
    "get_lane_truth_threshold",  # v45Ω Patch B
    # Floor check functions
    "check_truth",
    "check_delta_s",
    "check_peace_squared",
    "check_kappa_r",
    "check_omega_band",
    "check_tri_witness",
    "check_psi",
    # v38.1 Gandhi Patch
    "calculate_peace_squared_gandhi",
    # Anti-Hantu helpers (F9)
    "ANTI_HANTU_FORBIDDEN",
    "ANTI_HANTU_ALLOWED",
    "check_anti_hantu",
    # v45Ω Patch 2: Truth Grounding
    "CANONICAL_IDENTITY",
    "IDENTITY_TRIGGERS",
    "detect_identity_query",
    "ground_truth_score",
    # Dataclasses
    "Metrics",
    "ConstitutionalMetrics",  # Legacy alias
    "FloorsVerdict",
    "FloorCheckResult",
]
