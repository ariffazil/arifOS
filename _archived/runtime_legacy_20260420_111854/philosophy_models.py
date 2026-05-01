"""
arifos/runtime/philosophy_models.py — Typed Philosophy Models for MCP

Pydantic models for strict schema export and SDK compatibility.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PhilosophyQuote(BaseModel):
    """Single philosophy quote entry with full provenance."""
    
    id: str = Field(..., description="Unique quote identifier (e.g., 'AE-01', 'IW-15')")
    
    text: str = Field(..., min_length=10, max_length=500, description="The quote text")
    
    author: str = Field(..., description="Attributed author")
    
    civilization: str = Field(..., description="Civilization block (e.g., 'Ancient_East', 'Islamic_Golden_Age')")
    
    era: Literal["Ancient", "Classical", "Medieval", "Enlightenment", "Industrial", "Modern", "Contemporary"] = Field(
        ..., description="Historical era"
    )
    
    category: Literal["wisdom", "discipline", "justice", "power", "paradox", "truth", "void", "seal"] = Field(
        ..., description="Governance category"
    )
    
    tags: list[str] = Field(default_factory=list, description="Searchable tags")
    
    source: str = Field(default="corpus_99", description="Source corpus identifier")
    
    @field_validator('id')
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Ensure ID follows civilization-number format."""
        if '-' not in v:
            raise ValueError(f"ID must contain '-': {v}")
        return v


class PhilosophySelection(BaseModel):
    """Philosophy selection result with full metadata for MCP export."""
    
    entry: PhilosophyQuote = Field(..., description="Selected quote")
    
    selection_reason: str = Field(..., description="Human-readable selection rationale")
    
    selection_mode: Literal[
        "verdict_binding",
        "stage_binding", 
        "g_star_band",
        "category_match",
        "deterministic_hash"
    ] = Field(..., description="Selection algorithm used")
    
    g_star: float | None = Field(None, ge=0.0, le=1.0, description="G★ score that influenced selection")
    
    band: int | None = Field(None, ge=0, le=4, description="G★ band (0-4)")
    
    schema_version: str = Field(default="1.0.0", description="Schema version")
    
    registry_version: str = Field(default="1.0.0", description="Registry version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entry": {
                    "id": "SE-01",
                    "text": "DITEMPA, BUKAN DIBERI.",
                    "author": "arifOS Foundry",
                    "civilization": "Modern_Political",
                    "era": "Modern",
                    "category": "seal",
                    "tags": ["forged", "seal", "motto"],
                    "source": "corpus_99"
                },
                "selection_reason": "G★=0.91 → band=4 → seal category",
                "selection_mode": "g_star_band",
                "g_star": 0.91,
                "band": 4,
                "schema_version": "1.0.0",
                "registry_version": "1.0.0"
            }
        }


class PhilosophyRegistryStats(BaseModel):
    """Registry statistics for diversity scoring and validation."""
    
    total_quotes: int = Field(..., description="Total quotes in registry")
    
    unique_civilizations: int = Field(..., description="Number of unique civilizations")
    
    civilization_distribution: dict[str, int] = Field(..., description="Quotes per civilization")
    
    category_distribution: dict[str, int] = Field(..., description="Quotes per category")
    
    era_distribution: dict[str, int] = Field(..., description="Quotes per era")
    
    diversity_score: float = Field(..., ge=0.0, le=1.0, description="Shannon entropy diversity score (D)")
    
    is_valid: bool = Field(..., description="Whether registry passes all constraints")
    
    validation_errors: list[str] = Field(default_factory=list, description="List of validation failures")


class PhilosophyRegistry(BaseModel):
    """Complete philosophy registry with validation."""
    
    schema_version: str = Field(default="1.0.0")
    
    registry_version: str = Field(default="1.0.0")
    
    quotes: list[PhilosophyQuote] = Field(..., min_length=33, max_length=99, description="33-99 quotes (target: 99)")
    
    def get_stats(self) -> PhilosophyRegistryStats:
        """Compute registry statistics."""
        import math
        from collections import Counter
        
        civ_counts = Counter(q.civilization for q in self.quotes)
        cat_counts = Counter(q.category for q in self.quotes)
        era_counts = Counter(q.era for q in self.quotes)
        
        # Shannon entropy diversity score
        n = len(self.quotes)
        probs = [count / n for count in civ_counts.values()]
        h = -sum(p * math.log(p) for p in probs if p > 0)
        h_max = math.log(len(civ_counts)) if civ_counts else 1
        d = h / h_max if h_max > 0 else 0
        
        # Validation
        errors = []
        
        # Check minimum quotes (33 for development, 99 for production)
        if len(self.quotes) < 33:
            errors.append(f"Expected at least 33 quotes, got {len(self.quotes)}")
        
        # Check unique IDs
        ids = [q.id for q in self.quotes]
        if len(ids) != len(set(ids)):
            errors.append("Duplicate IDs found")
        
        # Check civilization cap (15% = ~14.85 → cap at 14)
        for civ, count in civ_counts.items():
            if count > 14:
                errors.append(f"{civ} exceeds 15% cap: {count}")
        
        # Check category minimum (8 per category)
        required_categories = ["wisdom", "discipline", "justice", "power", "paradox", "truth", "void", "seal"]
        for cat in required_categories:
            if cat_counts.get(cat, 0) < 8:
                errors.append(f"Category '{cat}' underrepresented: {cat_counts.get(cat, 0)} < 8")
        
        # Check era minimum (10 per era)
        for era, count in era_counts.items():
            if count < 10:
                errors.append(f"Era '{era}' underrepresented: {count} < 10")
        
        return PhilosophyRegistryStats(
            total_quotes=len(self.quotes),
            unique_civilizations=len(civ_counts),
            civilization_distribution=dict(civ_counts),
            category_distribution=dict(cat_counts),
            era_distribution=dict(era_counts),
            diversity_score=round(d, 4),
            is_valid=len(errors) == 0,
            validation_errors=errors
        )
    
    def validate_strict(self) -> None:
        """Validate registry strictly - raises on failure."""
        stats = self.get_stats()
        if not stats.is_valid:
            raise ValueError(f"Registry validation failed: {stats.validation_errors}")
    
    def get_by_category(self, category: str) -> list[PhilosophyQuote]:
        """Get all quotes in a category."""
        return [q for q in self.quotes if q.category == category]
    
    def get_by_band(self, band: int) -> list[PhilosophyQuote]:
        """Get quotes for a G★ band based on category mapping."""
        # Band → category mapping from formal spec
        band_categories = {
            0: ["void", "paradox"],
            1: ["paradox", "truth"],
            2: ["wisdom", "justice"],
            3: ["discipline", "power"],
            4: ["seal", "power"],
        }
        categories = band_categories.get(band, ["wisdom"])
        return [q for q in self.quotes if q.category in categories]


__all__ = [
    "PhilosophyQuote",
    "PhilosophySelection", 
    "PhilosophyRegistryStats",
    "PhilosophyRegistry",
]
