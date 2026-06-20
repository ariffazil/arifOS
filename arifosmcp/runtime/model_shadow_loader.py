"""
Model Shadow Loader — Static AAA Registry → Dynamic arifOS Runtime
═══════════════════════════════════════════════════════════════════

Bridges the YAML soul/shadow registry files (in /root/AAA/registries/models/)
into runtime-queryable Python dataclasses.

The static files are the canonical source. This loader reads them at import
time and at session_init, injecting floor_posture, trigger vocabulary,
routing constraints, and hazard profiles into the governance pipeline.

ARCHITECTURE:
  AAA/registries/models/*_soul.yaml   ──┐
  AAA/registries/models/*_shadow.yaml ──┤
  FEDERATION_MODEL.json               ──┤
                                         │
                    ┌────────────────────┘
                    ▼
            ModelShadowLoader
                    │
                    ├── get_model_shadow(model_id) → ShadowProfile
                    ├── get_floor_posture(model_id) → dict
                    ├── get_routing_constraints(model_id) → RoutingConstraints
                    ├── get_trigger_vocabulary(model_id) → list[str]
                    └── list_all_shadows() → list[ShadowProfile]

DITEMPA BUKAN DIBERI — The shadow map is forged, not given.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────
_AAA_REGISTRY = Path("/root/AAA/registries")
_MODELS_DIR = _AAA_REGISTRY / "models"
_FEDERATION_MODEL = _AAA_REGISTRY / "FEDERATION_MODEL.json"

# ── Dataclasses ────────────────────────────────────────────────────


@dataclass
class ShadowEntry:
    """A single shadow/hazard entry from a model's shadow registry."""
    id: str
    name: str
    severity: str  # HIGH | MEDIUM | LOW
    class_: str  # fabrication | overclaim | governance_gap | infrastructure_risk | jurisdiction_risk | culture_mismatch | false_positive | overreach
    pattern: str
    triggers: list[str] = field(default_factory=list)
    floor_posture_delta: dict = field(default_factory=dict)
    mitigation: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    provenance: str = "UNVERIFIED"

    @classmethod
    def from_yaml(cls, data: dict) -> ShadowEntry:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            severity=data.get("severity", "MEDIUM"),
            class_=data.get("class", "unknown"),
            pattern=data.get("pattern", ""),
            triggers=data.get("triggers", []),
            floor_posture_delta=data.get("floor_posture_delta", {}),
            mitigation=data.get("mitigation", []),
            evidence=data.get("evidence", []),
            provenance=data.get("provenance", "UNVERIFIED"),
        )


@dataclass
class ShadowProfile:
    """Complete shadow profile for a model family."""
    model_id: str
    model_family: str
    version: str
    status: str
    shadows: list[ShadowEntry] = field(default_factory=list)
    floor_posture: dict = field(default_factory=dict)
    sources: list[str] = field(default_factory=list)
    lifecycle: dict = field(default_factory=dict)

    @property
    def high_severity_shadows(self) -> list[ShadowEntry]:
        return [s for s in self.shadows if s.severity == "HIGH"]

    @property
    def trigger_vocabulary(self) -> set[str]:
        """Union of all trigger strings across all shadow entries."""
        vocab = set()
        for s in self.shadows:
            for t in s.triggers:
                vocab.add(t)
        return vocab

    def floor_posture_for_model(self, model_id: str) -> dict:
        """Return floor posture adjusted for a specific model variant."""
        posture = dict(self.floor_posture)
        for s in self.shadows:
            for floor, setting in s.floor_posture_delta.items():
                if floor in posture and setting != "standard":
                    posture[floor] = setting
        return posture


@dataclass
class RoutingConstraints:
    """Routing constraints extracted from FEDERATION_MODEL.json."""
    model_key: str
    status: str  # CONFIRMED_CENSORED | NO_CENSORSHIP_DETECTED | HARNESS_MONITORED
    forbidden_topics: list[str] = field(default_factory=list)
    known_false_positive_triggers: list[str] = field(default_factory=list)
    data_retention_days: int | None = None
    zero_retention_available: bool = True
    jurisdiction: str = "UNKNOWN"
    federation_impact: dict = field(default_factory=dict)
    mitigation: str = ""


# ── Loader ─────────────────────────────────────────────────────────


class ModelShadowLoader:
    """Loads and caches model shadow profiles from AAA registry."""

    def __init__(self):
        self._shadows: dict[str, ShadowProfile] = {}
        self._routing: dict[str, RoutingConstraints] = {}
        self._loaded = False

    def load_all(self) -> None:
        """Load all shadow/soul files and federation routing constraints."""
        if self._loaded:
            return

        # Load federation routing constraints
        self._load_federation_routing()

        # Load per-model shadow files
        if _MODELS_DIR.exists():
            for shadow_file in _MODELS_DIR.glob("*_shadow.yaml"):
                try:
                    profile = self._load_shadow_file(shadow_file)
                    self._shadows[profile.model_id] = profile
                    logger.info(f"Loaded shadow: {profile.model_id} v{profile.version} "
                                f"({len(profile.shadows)} entries)")
                except Exception as e:
                    logger.warning(f"Failed to load shadow file {shadow_file}: {e}")

        self._loaded = True
        logger.info(f"ModelShadowLoader: {len(self._shadows)} shadow profiles, "
                    f"{len(self._routing)} routing constraints loaded")

    def _load_shadow_file(self, path: Path) -> ShadowProfile:
        """Parse a single *_shadow.yaml file into a ShadowProfile."""
        with open(path) as f:
            data = yaml.safe_load(f)

        shadows = []
        for entry in data.get("shadow", []):
            shadows.append(ShadowEntry.from_yaml(entry))

        return ShadowProfile(
            model_id=data.get("model_id", path.stem),
            model_family=data.get("model_family", ""),
            version=str(data.get("version", "0.0.0")),
            status=data.get("status", "UNKNOWN"),
            shadows=shadows,
            floor_posture=data.get("floor_posture", {}),
            sources=data.get("sources", []),
            lifecycle=data.get("lifecycle", {}),
        )

    def _load_federation_routing(self) -> None:
        """Parse FEDERATION_MODEL.json for routing constraints."""
        if not _FEDERATION_MODEL.exists():
            logger.warning(f"FEDERATION_MODEL.json not found at {_FEDERATION_MODEL}")
            return

        with open(_FEDERATION_MODEL) as f:
            data = json.load(f)

        registry = data.get("censorship_registry", {})
        for key, entry in registry.items():
            # Map registry keys to model identifiers
            model_key = key.lower().replace("_", "-")

            # Extract data policy
            dp = entry.get("data_policy", {})
            routing = RoutingConstraints(
                model_key=model_key,
                status=entry.get("status", "UNKNOWN"),
                forbidden_topics=entry.get("censored_topics", []),
                known_false_positive_triggers=entry.get("known_false_positive_triggers", []),
                data_retention_days=dp.get("retention_days"),
                zero_retention_available=dp.get("zero_retention_available", True),
                jurisdiction=entry.get("jurisdiction", "UNKNOWN"),
                federation_impact=entry.get("federation_impact", {}),
                mitigation=entry.get("mitigation", ""),
            )
            self._routing[model_key] = routing

    # ── Query API ─────────────────────────────────────────────────

    def get_shadow(self, model_id: str) -> ShadowProfile | None:
        """Get the shadow profile for a model family.

        Args:
            model_id: e.g., 'anthropic_shadow', 'minimax_shadow', 'deepseek_shadow'

        Returns:
            ShadowProfile or None if not found.
        """
        self.load_all()
        # Try exact match first, then fuzzy match
        if model_id in self._shadows:
            return self._shadows[model_id]
        # Try matching by family name
        for key, profile in self._shadows.items():
            if model_id.lower() in key.lower() or key.lower() in model_id.lower():
                return profile
        return None

    def get_floor_posture(self, model_id: str) -> dict:
        """Get the floor posture for a model, with shadow deltas applied.

        Used by session_init to load the right constitutional posture
        for the active model.
        """
        profile = self.get_shadow(model_id)
        if profile is None:
            # Default posture: standard across all floors
            return {
                "F1_AMANAH": "standard", "F2_TRUTH": "standard",
                "F3_WITNESS": "standard", "F4_CLARITY": "standard",
                "F5_PEACE": "standard", "F6_EMPATHY": "standard",
                "F7_HUMILITY": "standard", "F8_GENIUS": "standard",
                "F9_ANTIHANTU": "standard", "F10_ONTOLOGY": "standard",
                "F11_AUTH": "standard", "F12_INJECTION": "standard",
                "F13_SOVEREIGN": "standard",
            }
        return profile.floor_posture_for_model(model_id)

    def get_routing_constraints(self, model_key: str) -> RoutingConstraints | None:
        """Get routing constraints for a model.

        Args:
            model_key: e.g., 'anthropic-claude-fable5', 'minimax-m3'
        """
        self.load_all()
        return self._routing.get(model_key.lower())

    def get_trigger_vocabulary(self, model_id: str) -> set[str]:
        """Get all trigger vocabulary strings for a model's shadow entries."""
        profile = self.get_shadow(model_id)
        if profile is None:
            return set()
        return profile.trigger_vocabulary

    def list_all(self) -> list[ShadowProfile]:
        """List all loaded shadow profiles."""
        self.load_all()
        return list(self._shadows.values())

    def list_routing(self) -> list[RoutingConstraints]:
        """List all routing constraints."""
        self.load_all()
        return list(self._routing.values())

    def reload(self) -> None:
        """Force reload all profiles (e.g., after registry update)."""
        self._shadows.clear()
        self._routing.clear()
        self._loaded = False
        self.load_all()


# ── Singleton ──────────────────────────────────────────────────────

_shadow_loader: ModelShadowLoader | None = None


def get_shadow_loader() -> ModelShadowLoader:
    """Get or create the singleton ModelShadowLoader."""
    global _shadow_loader
    if _shadow_loader is None:
        _shadow_loader = ModelShadowLoader()
        _shadow_loader.load_all()
    return _shadow_loader


def reload_shadows() -> ModelShadowLoader:
    """Force reload all shadow profiles."""
    global _shadow_loader
    if _shadow_loader is not None:
        _shadow_loader.reload()
    else:
        _shadow_loader = ModelShadowLoader()
        _shadow_loader.load_all()
    return _shadow_loader
