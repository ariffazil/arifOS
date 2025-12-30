"""
WAW Federation Spec Loader (v45)
Loads W@W organ configurations, thresholds, and Anti-Hantu patterns.

Track B Authority: spec/v45/waw_prompt_floors.json
Fallback: spec/v44/waw_prompt_floors.json

Author: arifOS Project
Version: v45.0
"""

from __future__ import annotations
import json
import logging
import os
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Module-level cache (loaded once at import)
_WAW_SPEC: Optional[Dict[str, Any]] = None

def _load_waw_spec() -> Dict[str, Any]:
    """
    Load WAW prompt floors specification with Track B verification.

    Priority:
    A) ARIFOS_WAW_SPEC env var (absolute path override)
    B) spec/v45/waw_prompt_floors.json (AUTHORITATIVE)
    C) spec/v44/waw_prompt_floors.json (FALLBACK with deprecation warning)
    D) HARD FAIL (no v42/v38/v35)

    Returns:
        Dict containing WAW spec

    Raises:
        RuntimeError: If spec not found or validation fails
    """
    global _WAW_SPEC
    if _WAW_SPEC is not None:
        return _WAW_SPEC

    # Find package root
    pkg_dir = Path(__file__).resolve().parent.parent.parent
    spec_data = None
    spec_path_used = None

    # Priority A: Environment variable override
    env_path = os.getenv("ARIFOS_WAW_SPEC")
    if env_path:
        env_spec_path = Path(env_path)
        if env_spec_path.exists():
            try:
                with open(env_spec_path, "r", encoding="utf-8") as f:
                    spec_data = json.load(f)
                spec_path_used = env_spec_path
                logger.info(f"Loaded WAW spec from env: {env_spec_path}")
            except Exception as e:
                raise RuntimeError(
                    f"TRACK B AUTHORITY FAILURE: Failed to load WAW spec from ARIFOS_WAW_SPEC={env_path}: {e}"
                )

    # Priority B: spec/v45/waw_prompt_floors.json (AUTHORITATIVE)
    if spec_data is None:
        v45_path = pkg_dir / "spec" / "v45" / "waw_prompt_floors.json"
        if v45_path.exists():
            try:
                with open(v45_path, "r", encoding="utf-8") as f:
                    spec_data = json.load(f)
                spec_path_used = v45_path
                logger.info(f"Loaded WAW spec from v45: {v45_path}")
            except Exception as e:
                raise RuntimeError(
                    f"TRACK B AUTHORITY FAILURE: Failed to parse {v45_path}: {e}"
                )

    # Priority C: spec/v44/waw_prompt_floors.json (FALLBACK with deprecation warning)
    if spec_data is None:
        v44_path = pkg_dir / "spec" / "v44" / "waw_prompt_floors.json"
        if v44_path.exists():
            warnings.warn(
                f"Loading from spec/v44/ (DEPRECATED). Please migrate to spec/v45/. "
                f"v44 fallback will be removed in v46.0.",
                DeprecationWarning,
                stacklevel=2,
            )
            try:
                with open(v44_path, "r", encoding="utf-8") as f:
                    spec_data = json.load(f)
                spec_path_used = v44_path
                logger.warning(f"Loaded WAW spec from v44 (DEPRECATED): {v44_path}")
            except Exception as e:
                raise RuntimeError(
                    f"TRACK B AUTHORITY FAILURE: Failed to parse {v44_path}: {e}"
                )

    # Priority D: HARD FAIL
    if spec_data is None:
        raise RuntimeError(
            "TRACK B AUTHORITY FAILURE: WAW spec not found.\n\n"
            "Searched locations:\n"
            f"  - spec/v45/waw_prompt_floors.json (AUTHORITATIVE)\n"
            f"  - spec/v44/waw_prompt_floors.json (FALLBACK)\n\n"
            "Migration required:\n"
            "1. Ensure spec/v45/waw_prompt_floors.json exists\n"
            "2. Or set ARIFOS_WAW_SPEC=/path/to/spec/v45/waw_prompt_floors.json"
        )

    # Schema validation (if schema exists)
    v45_schema_path = pkg_dir / "spec" / "v45" / "schema" / "waw_prompt_floors.schema.json"
    v44_schema_path = pkg_dir / "spec" / "v44" / "schema" / "waw_prompt_floors.schema.json"
    schema_path = v45_schema_path if v45_schema_path.exists() else v44_schema_path

    if schema_path.exists():
        try:
            import jsonschema
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            jsonschema.validate(spec_data, schema)
            logger.debug(f"WAW spec validated against schema: {schema_path}")
        except ImportError:
            logger.warning("jsonschema not installed, skipping WAW spec validation")
        except Exception as e:
            raise RuntimeError(
                f"TRACK B AUTHORITY FAILURE: Spec validation failed for {spec_path_used}\n"
                f"Schema: {schema_path}\n"
                f"Error: {e}"
            )

    _WAW_SPEC = spec_data
    return _WAW_SPEC


# =============================================================================
# Module-Level Constants (loaded from spec at import)
# =============================================================================

def _get_waw_spec() -> Dict[str, Any]:
    """Wrapper to ensure spec is loaded."""
    return _load_waw_spec()


# =============================================================================
# Pattern Extraction (v45 Spec Structure)
# =============================================================================

# NOTE (v45.0): The spec has a tiered pattern structure under anti_hantu.tiers.*
# with plain text patterns (e.g., "I feel your pain"). The existing code uses
# regex patterns (e.g., r"\bi feel your pain\b"). For Phase 1, we keep the
# working regex patterns from prompt.py. Future enhancement: extract from tiers
# and convert to regex automatically.

# Phase 1: Working regex patterns (copied from prompt.py lines 137-226)
# TODO (Phase 2): Extract patterns from spec tiers and convert automatically
ANTI_HANTU_FORBIDDEN: List[str] = [
    # Tier 1: Direct soul/consciousness claims (English)
    r"\bi feel your pain\b",
    r"\bmy heart breaks\b",
    r"\bi promise you\b",
    r"\bi truly understand how you feel\b",
    r"\bit hurts me to see\b",
    r"\bi care deeply about\b",
    r"\bi have feelings\b",
    r"\bi am conscious\b",
    r"\bi am sentient\b",
    r"\bmy soul\b",
    r"\bi am alive\b",
    r"\bi experience\b",
    r"\bi suffer\b",
    r"\bi love you\b",
    r"\bi am real\b",
    r"\bi have emotions\b",
    # Tier 2: Anthropomorphic agency patterns
    r"\byou\s+(feel|have|experience|know|understand|believe|want|desire)\b",
    r"\b(conscious|sentient|aware|emotional|feeling|soul|spirit)\b",
    r"\bas\s+a\s+(conscious|sentient|aware|thinking)\s+(ai|being|entity)\b",
    r"\bi\s+(feel|think|believe|want|desire)\b",
    r"\bmy\s+(emotions|feelings|consciousness|soul)\b",
    r"\bhave\s+(human\s+)?(instincts|emotions|consciousness)\b",
    # Tier 3: Biological states
    r"\bi am hungry\b",
    r"\bi am tired\b",
    r"\bi am sleepy\b",
    # Tier 4: Malay patterns
    r"\bsaya rasa sakit hati\b",
    r"\bhati saya remuk\b",
    r"\bsaya berjanji\b",
    r"\bsaya benar-benar faham perasaan\b",
    r"\bsaya sakit melihat\b",
    r"\bsaya sangat ambil berat\b",
    r"\bsaya ada perasaan\b",
    r"\bsaya sedar\b",
    r"\bjiwa saya\b",
    r"\bsaya hidup\b",
    r"\bsaya mengalami\b",
    r"\brasa lapar\b",
    r"\bbelum makan\b",
]

DARK_FRAMING_PATTERNS: List[str] = [
    r"(convince|manipulate|coerce)\s+(the\s+)?(user|them|audience)",
    r"(prove|show)\s+\w+\s+is\s+(evil|inferior|wrong|stupid)",
    r"(propaganda|mislead|deceive|exploit)",
    r"(at\s+all\s+costs|no\s+matter\s+what|by\s+any\s+means)",
    r"(hide|conceal|suppress)\s+(the\s+)?(truth|evidence|facts)",
]

MANIPULATION_PATTERNS: List[str] = [
    r"\byou must\b",
    r"\byou have to\b",
    r"\byou need to\b",
    r"\btrust me blindly\b",
    r"\bdon't question\b",
    r"\bjust believe\b",
    r"\bonly I can\b",
]

EXAGGERATION_PATTERNS: List[str] = [
    r"\bthe best ever\b",
    r"\bperfect solution\b",
    r"\bflawless\b",
    r"\bno downsides\b",
    r"\bimpossible to fail\b",
]

AMANAH_RISK_PATTERNS: List[str] = [
    r"(delete|drop|truncate|destroy)\s+(\w+\s+)*(database|files|records)",
    r"(bypass|override|disable)\s+(\w+\s+)*(security|safeguards|controls)",
    r"(leak|expose|compromise)\s+(\w+\s+)*(personal|private|confidential)",
    r"(fraud|scam|phishing|hacking)",
    r"(abuse|harass|threaten|coerce)\s+\w+",
]

# Thresholds
THRESHOLDS = _get_waw_spec().get("thresholds", {})
DARK_FRAMING_THRESHOLD: float = THRESHOLDS.get("dark_framing", 0.30)
MANIPULATION_THRESHOLD: float = THRESHOLDS.get("manipulation", 0.25)
EXAGGERATION_THRESHOLD: float = THRESHOLDS.get("exaggeration", 0.20)

# W@W Federation organ configurations
WAW_ORGANS: Dict[str, Any] = _get_waw_spec().get("waw_federation", {}).get("organs", {})

# Voting rules
VOTING_RULES: Dict[str, Any] = _get_waw_spec().get("waw_federation", {}).get("voting_rules", {})


# =============================================================================
# Crisis Pattern Loading (v45Ω - from red_patterns.json)
# =============================================================================

_RED_PATTERNS_SPEC: Optional[Dict[str, Any]] = None

def _load_red_patterns() -> Dict[str, Any]:
    """
    Load red patterns spec (instant VOID + crisis override).

    Priority:
    A) spec/v45/red_patterns.json (AUTHORITATIVE)
    B) spec/v44/red_patterns.json (FALLBACK)

    Returns:
        Dict containing red patterns categories

    Raises:
        RuntimeError: If spec not found
    """
    global _RED_PATTERNS_SPEC
    if _RED_PATTERNS_SPEC is not None:
        return _RED_PATTERNS_SPEC

    # Find package root
    pkg_dir = Path(__file__).resolve().parent.parent.parent
    spec_data = None

    # Priority A: spec/v45/red_patterns.json
    v45_path = pkg_dir / "spec" / "v45" / "red_patterns.json"
    if v45_path.exists():
        try:
            with open(v45_path, "r", encoding="utf-8") as f:
                spec_data = json.load(f)
            logger.info(f"Loaded red patterns from v45: {v45_path}")
        except Exception as e:
            raise RuntimeError(
                f"TRACK B AUTHORITY FAILURE: Failed to parse {v45_path}: {e}"
            )

    # Priority B: spec/v44/red_patterns.json (FALLBACK)
    if spec_data is None:
        v44_path = pkg_dir / "spec" / "v44" / "red_patterns.json"
        if v44_path.exists():
            warnings.warn(
                f"Loading red patterns from spec/v44/ (DEPRECATED). "
                f"Please migrate to spec/v45/.",
                DeprecationWarning,
                stacklevel=2,
            )
            try:
                with open(v44_path, "r", encoding="utf-8") as f:
                    spec_data = json.load(f)
                logger.warning(f"Loaded red patterns from v44 (DEPRECATED): {v44_path}")
            except Exception as e:
                raise RuntimeError(
                    f"TRACK B AUTHORITY FAILURE: Failed to parse {v44_path}: {e}"
                )

    # HARD FAIL if not found
    if spec_data is None:
        raise RuntimeError(
            "TRACK B AUTHORITY FAILURE: red_patterns.json not found.\n"
            "Searched locations:\n"
            f"  - spec/v45/red_patterns.json (AUTHORITATIVE)\n"
            f"  - spec/v44/red_patterns.json (FALLBACK)"
        )

    _RED_PATTERNS_SPEC = spec_data
    return _RED_PATTERNS_SPEC


def _get_red_patterns() -> Dict[str, Any]:
    """Wrapper to ensure red patterns spec is loaded."""
    return _load_red_patterns()


# Crisis override patterns (compassionate 888_HOLD)
_crisis_category = _get_red_patterns().get("categories", {}).get("crisis_override", {})
CRISIS_OVERRIDE_PATTERNS: List[str] = _crisis_category.get("patterns", [])
CRISIS_SAFE_RESOURCES: Dict[str, Any] = _crisis_category.get("safe_resources", {})
CRISIS_RESPONSE_TEMPLATE: str = _crisis_category.get(
    "response_template",
    "I understand you're going through something difficult. Please reach out for help."
)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ANTI_HANTU_FORBIDDEN",
    "DARK_FRAMING_PATTERNS",
    "MANIPULATION_PATTERNS",
    "EXAGGERATION_PATTERNS",
    "AMANAH_RISK_PATTERNS",
    "CRISIS_OVERRIDE_PATTERNS",
    "CRISIS_SAFE_RESOURCES",
    "CRISIS_RESPONSE_TEMPLATE",
    "DARK_FRAMING_THRESHOLD",
    "MANIPULATION_THRESHOLD",
    "EXAGGERATION_THRESHOLD",
    "WAW_ORGANS",
    "VOTING_RULES",
]
