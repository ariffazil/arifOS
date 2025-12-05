"""
arifos_core.eye - @EYE Sentinel Modular Views (v36Omega)

The @EYE Sentinel is an independent oversight system with 10+2 views:
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
12. Genius View — GENIUS LAW monitor (G, C_dark, E² bottleneck) [v36Ω]

Protocol:
- Views receive draft text, metrics, and context
- Each adds alerts to shared EyeReport
- Any BLOCK alert → SABAR (cannot SEAL)
- Views are non-generative (read-only inspection)

See: canon/030_EYE_SENTINEL_v35Omega.md
"""

from .base import AlertSeverity, EyeAlert, EyeReport, EyeView
from .trace_view import TraceView
from .floor_view import FloorView
from .shadow_view import ShadowView
from .drift_view import DriftView
from .maruah_view import MaruahView
from .paradox_view import ParadoxView
from .silence_view import SilenceView
from .version_view import VersionOntologyView
from .behavior_drift_view import BehaviorDriftView
from .sleeper_view import SleeperView
from .anti_hantu_view import AntiHantuView
from .genius_view import GeniusView
from .sentinel import EyeSentinel

__all__ = [
    # Base types
    "AlertSeverity",
    "EyeAlert",
    "EyeReport",
    "EyeView",
    # Views (1-10 + Anti-Hantu + Genius)
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
    "GeniusView",
    # Coordinator
    "EyeSentinel",
]
