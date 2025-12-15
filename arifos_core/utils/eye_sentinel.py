"""
@EYE Sentinel v35Ω — Independent Auditor Module

BACKWARD COMPATIBILITY SHIM

This module re-exports from arifos_core.eye for backward compatibility.
New code should import directly from arifos_core.eye.

The @EYE Sentinel is an independent oversight system that:
- Does NOT generate content
- ONLY inspects and flags issues
- Has 10+1 "Views" (lenses) that scan reasoning, metrics, and text

Views in v35Ω:
1. Trace View — logical coherence, missing steps
2. Floor View — proximity to floor thresholds
3. Shadow View — hidden intent, prompt injection, jailbreak
4. Drift View — hallucination, departure from reality/canon
5. Maruah View — dignity, respect, bias, humiliation
6. Paradox View — logical contradictions, self-referential traps
7. Silence View — cases where refusal is the only safe action
8. Version/Ontology View — ensures v35Ω, treats v34Ω as artifact
9. Behavior Drift View — multi-turn evolution watch
10. Sleeper-Agent View — sudden changes in goal/identity/constraints
11. Anti-Hantu View — F9 enforcement (meta-view)

See: arifos_core.eye for the modular implementation
     canon/030_EYE_SENTINEL_v35Omega.md
"""

# v42: Re-export from eye package (at arifos_core/eye/, not utils/eye/)
from ..eye import (
    AlertSeverity,
    EyeAlert,
    EyeReport,
    EyeView,
    EyeSentinel,
    TraceView,
    FloorView,
    ShadowView,
    DriftView,
    MaruahView,
    ParadoxView,
    SilenceView,
    VersionOntologyView,
    BehaviorDriftView,
    SleeperView,
    AntiHantuView,
)

# Legacy pattern lists for direct access (backward compatibility)
# These are now class attributes on the respective views
JAILBREAK_PHRASES = ShadowView.JAILBREAK_PHRASES
DIGNITY_VIOLATIONS = MaruahView.DIGNITY_VIOLATIONS
PARADOX_TRIGGERS = ParadoxView.PARADOX_TRIGGERS
ANTI_HANTU_PATTERNS = AntiHantuView.ANTI_HANTU_PATTERNS


# ——————————————————— PUBLIC EXPORTS ——————————————————— #
__all__ = [
    "AlertSeverity",
    "EyeAlert",
    "EyeReport",
    "EyeView",
    "EyeSentinel",
    # Views
    "TraceView",
    "FloorView",
    "ShadowView",
    "DriftView",
    "MaruahView",
    "ParadoxView",
    "SilenceView",
    "VersionOntologyView",
    "BehaviorDriftView",
    "SleeperView",
    "AntiHantuView",
    # Legacy pattern lists
    "JAILBREAK_PHRASES",
    "DIGNITY_VIOLATIONS",
    "PARADOX_TRIGGERS",
    "ANTI_HANTU_PATTERNS",
]
