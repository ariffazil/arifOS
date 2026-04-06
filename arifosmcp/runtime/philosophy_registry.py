"""
arifosmcp/runtime/philosophy_registry.py — arifOS Philosophy Registry v1

99 wisdom quotes with civilizational diversity.
Deterministic G★ band selection.
Typed for MCP compliance.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
from pathlib import Path
from typing import Any

from arifosmcp.runtime.philosophy_models import (
    PhilosophyQuote,
    PhilosophyRegistry,
    PhilosophyRegistryStats,
    PhilosophySelection,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRY VERSION
# ═══════════════════════════════════════════════════════════════════════════════

PHILOSOPHY_REGISTRY_VERSION = "1.0.0"


# ═══════════════════════════════════════════════════════════════════════════════
# G★ BAND MAPPING (Formal Specification)
# ═══════════════════════════════════════════════════════════════════════════════

# Band → Allowed categories (governance-structured)
G_STAR_BAND_CATEGORIES: dict[int, list[str]] = {
    0: ["void", "paradox"],      # Low G★: entropy edge reflection
    1: ["paradox", "truth"],     # Low-mid G★: uncertainty
    2: ["wisdom", "justice"],    # Mid G★: moral grounding
    3: ["discipline", "power"],  # Mid-high G★: action
    4: ["seal", "power"],        # High G★: authority / seal
}


def map_g_star_to_band(g_star: float) -> int:
    """
    Map G★ ∈ [0, 1] to discrete band B ∈ {0, 1, 2, 3, 4}
    
    Formula: B = floor(5 * G★), with edge correction
    """
    if not 0.0 <= g_star <= 1.0:
        raise ValueError(f"G★ must be in [0, 1], got {g_star}")
    
    band = math.floor(5 * g_star)
    
    # Edge correction: band 5 → 4
    if band >= 5:
        band = 4
    
    return band


# ═══════════════════════════════════════════════════════════════════════════════
# LOAD REGISTRY FROM JSON
# ═══════════════════════════════════════════════════════════════════════════════

def _load_philosophy_registry() -> PhilosophyRegistry:
    """Load the 99 quotes from local corpus with validation."""
    
    # Try multiple paths for flexibility
    possible_paths = [
        Path("/usr/src/project/data/philosophy_registry_v1.json"),
        Path("/usr/src/project/archive/DATA/wisdom_quotes.json"),
        Path(__file__).parent.parent.parent / "data" / "philosophy_registry_v1.json",
        Path(__file__).parent.parent.parent / "archive" / "DATA" / "wisdom_quotes.json",
    ]
    
    for path in possible_paths:
        try:
            if not path.exists():
                continue
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Handle both formats: direct list or {quotes: [...]}
            if isinstance(data, list):
                quotes_data = data
            elif isinstance(data, dict) and "quotes" in data:
                quotes_data = data["quotes"]
            else:
                quotes_data = data.get("quotes", [])
            
            # Convert old format to new if needed
            converted_quotes = []
            for q in quotes_data:
                # Map old 'scar' category to new categories
                old_category = q.get("category", "wisdom")
                category_mapping = {
                    "scar": "truth",
                    "triumph": "power",
                    "love": "justice",
                }
                new_category = category_mapping.get(old_category, old_category)
                
                # Add era if missing
                era = q.get("era", "Modern")
                if "era" not in q:
                    era = "Modern"
                
                # Add civilization if missing
                civilization = q.get("civilization", "Contemporary_Global")
                if "civilization" not in q:
                    civilization = "Contemporary_Global"
                
                converted = {
                    "id": q.get("id", "UNK"),
                    "text": q.get("text", ""),
                    "author": q.get("author", "Unknown"),
                    "civilization": civilization,
                    "era": era,
                    "category": new_category,
                    "tags": q.get("tags", []),
                    "source": q.get("source", "corpus_99"),
                }
                converted_quotes.append(converted)
            
            registry = PhilosophyRegistry(quotes=converted_quotes)
            
            # Validate
            stats = registry.get_stats()
            if stats.is_valid:
                logger.info(
                    f"Loaded {len(registry.quotes)} philosophy entries from {path} "
                    f"(diversity_score={stats.diversity_score:.2f})"
                )
            else:
                logger.warning(f"Registry validation issues: {stats.validation_errors}")
            
            return registry
            
        except Exception as e:
            logger.warning(f"Failed to load from {path}: {e}")
            continue
    
    # Fallback: embedded minimal registry
    logger.warning("Using embedded fallback philosophy registry")
    return _fallback_registry()


def _fallback_registry() -> PhilosophyRegistry:
    """Minimal fallback registry if file not found."""
    fallback_quotes = [
        PhilosophyQuote(
            id="SE-01",
            category="seal",
            author="arifOS Foundry",
            text="DITEMPA, BUKAN DIBERI.",
            civilization="Modern_Political",
            era="Modern",
            tags=["forged", "seal", "motto"]
        ),
        PhilosophyQuote(
            id="AE-01",
            category="wisdom",
            author="Lao Tzu",
            text="The journey of a thousand miles begins with a single step.",
            civilization="Ancient_East",
            era="Ancient",
            tags=["wisdom", "beginning", "tao"]
        ),
        PhilosophyQuote(
            id="AW-01",
            category="truth",
            author="Socrates",
            text="The only true wisdom is in knowing you know nothing.",
            civilization="Ancient_West",
            era="Classical",
            tags=["wisdom", "knowledge", "socratic"]
        ),
    ]
    
    # Pad to 99 with variations
    while len(fallback_quotes) < 99:
        idx = len(fallback_quotes)
        base = fallback_quotes[idx % 3]
        fallback_quotes.append(
            PhilosophyQuote(
                id=f"FB-{idx:02d}",
                category=base.category,
                author=f"{base.author} (variant)",
                text=f"{base.text} [{idx}]",
                civilization=base.civilization,
                era=base.era,
                tags=base.tags + ["fallback"]
            )
        )
    
    return PhilosophyRegistry(quotes=fallback_quotes)


# Global registry (loaded once at module import)
REGISTRY: PhilosophyRegistry = _load_philosophy_registry()


# ═══════════════════════════════════════════════════════════════════════════════
# DETERMINISTIC SELECTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def select_by_g_star(
    g_star: float,
    session_id: str,
    registry: PhilosophyRegistry | None = None,
) -> PhilosophySelection:
    """
    Deterministic selection based on G★ score.
    
    Args:
        g_star: G★ ∈ [0, 1] from envelope.metrics.telemetry.G_star
        session_id: Session ID for deterministic seed
        registry: Optional registry override (uses global if None)
    
    Returns:
        PhilosophySelection with entry and full metadata
    """
    reg = registry or REGISTRY
    
    # Map G★ to band
    band = map_g_star_to_band(g_star)
    
    # Get allowed categories for this band
    allowed_categories = G_STAR_BAND_CATEGORIES.get(band, ["wisdom"])
    
    # Get candidates
    candidates = [
        q for q in reg.quotes 
        if q.category in allowed_categories
    ]
    
    if not candidates:
        # Fallback to all quotes
        candidates = reg.quotes
    
    # Deterministic selection via SHA256(session_id + band)
    seed_input = f"{session_id}:{band}:{PHILOSOPHY_REGISTRY_VERSION}"
    seed_hash = hashlib.sha256(seed_input.encode()).hexdigest()
    index = int(seed_hash, 16) % len(candidates)
    
    entry = candidates[index]
    
    return PhilosophySelection(
        entry=entry,
        selection_reason=f"G★={g_star:.2f} → band={band} → categories={allowed_categories}",
        selection_mode="g_star_band",
        g_star=g_star,
        band=band,
        schema_version="1.0.0",
        registry_version=PHILOSOPHY_REGISTRY_VERSION,
    )


def select_by_verdict(
    verdict: str,
    session_id: str,
    registry: PhilosophyRegistry | None = None,
) -> PhilosophySelection:
    """Deterministic selection based on constitutional verdict."""
    reg = registry or REGISTRY
    
    # Verdict → category mapping
    verdict_categories: dict[str, list[str]] = {
        "SEAL": ["seal", "power"],
        "PARTIAL": ["wisdom", "justice"],
        "VOID": ["void", "paradox"],
        "HOLD": ["paradox", "truth"],
        "SABAR": ["wisdom", "discipline"],
    }
    
    categories = verdict_categories.get(verdict, ["wisdom"])
    
    candidates = [q for q in reg.quotes if q.category in categories]
    if not candidates:
        candidates = reg.quotes
    
    # Deterministic selection
    seed_input = f"{session_id}:{verdict}:{PHILOSOPHY_REGISTRY_VERSION}"
    seed_hash = hashlib.sha256(seed_input.encode()).hexdigest()
    index = int(seed_hash, 16) % len(candidates)
    
    entry = candidates[index]
    
    return PhilosophySelection(
        entry=entry,
        selection_reason=f"verdict={verdict} → categories={categories}",
        selection_mode="verdict_binding",
        g_star=None,
        band=None,
        schema_version="1.0.0",
        registry_version=PHILOSOPHY_REGISTRY_VERSION,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# INJECTION POINT (for _wrap_call)
# ═══════════════════════════════════════════════════════════════════════════════

def inject_philosophy(
    envelope: dict[str, Any],
    session_id: str | None = None,
    g_star: float | None = None,
    verdict: str | None = None,
    stage: str | None = None,
) -> dict[str, Any]:
    """
    Inject philosophy into RuntimeEnvelope.
    
    This is the canonical injection point called from _wrap_call().
    Preserves single-point-of-injection architecture.
    
    Args:
        envelope: The envelope dict to inject into
        session_id: Normalized session ID (defaults to envelope.get('session_id'))
        g_star: Optional G★ from envelope.metrics.telemetry.G_star
        verdict: Optional verdict for verdict-based selection
        stage: Optional stage (000, 111, 333, etc.) for stage-based selection
    
    Returns:
        Envelope with philosophy field added
    """
    try:
        # Get session_id from envelope if not provided
        if session_id is None:
            session_id = envelope.get('session_id', 'default-session')
        
        # Stage-based selection (maps stage to G★ band)
        if stage is not None:
            # Map stage to a deterministic G★ value
            stage_to_g_star = {
                "000": 0.5,  # init - middle
                "111": 0.2,  # sense - lower
                "333": 0.5,  # mind - middle
                "444": 0.6,  # route - upper-middle
                "555": 0.4,  # memory - middle
                "666": 0.7,  # heart - upper
                "777": 0.6,  # ops - upper-middle
                "888": 0.8,  # judge - high
                "999": 0.9,  # vault - very high
            }
            g = stage_to_g_star.get(stage, 0.5)
            selection = select_by_g_star(g, session_id)
        elif g_star is not None:
            selection = select_by_g_star(g_star, session_id)
        elif verdict is not None:
            selection = select_by_verdict(verdict, session_id)
        else:
            # Default: use middle band
            selection = select_by_g_star(0.5, session_id)
        
        envelope["philosophy"] = selection.model_dump()
        
    except Exception as e:
        logger.warning(f"Failed to inject philosophy: {e}")
        # Non-blocking: envelope still valid without philosophy
        envelope["philosophy"] = None
    
    return envelope


# ═══════════════════════════════════════════════════════════════════════════════
# MCP RESOURCE EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

def get_registry_summary() -> dict[str, Any]:
    """Get summary for MCP resource endpoint."""
    stats = REGISTRY.get_stats()
    return {
        "schema_version": "1.0.0",
        "registry_version": PHILOSOPHY_REGISTRY_VERSION,
        "total_quotes": stats.total_quotes,
        "unique_civilizations": stats.unique_civilizations,
        "civilization_distribution": stats.civilization_distribution,
        "category_distribution": stats.category_distribution,
        "era_distribution": stats.era_distribution,
        "diversity_score": stats.diversity_score,
        "is_valid": stats.is_valid,
        "selection_modes": ["g_star_band", "verdict_binding"],
        "g_star_bands": G_STAR_BAND_CATEGORIES,
    }


def get_registry_stats() -> PhilosophyRegistryStats:
    """Get full registry statistics."""
    return REGISTRY.get_stats()


__all__ = [
    "REGISTRY",
    "PHILOSOPHY_REGISTRY_VERSION",
    "G_STAR_BAND_CATEGORIES",
    "map_g_star_to_band",
    "select_by_g_star",
    "select_by_verdict",
    "inject_philosophy",
    "get_registry_summary",
    "get_registry_stats",
    "PhilosophyQuote",
    "PhilosophySelection",
    "PhilosophyRegistry",
    "PhilosophyRegistryStats",
]
