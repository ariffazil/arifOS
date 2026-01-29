"""
HIERARCHICAL ABSTRACTION (v54) - Critical Gap 2 Fix

5-level hierarchical prediction matching biological intelligence:
Level 5 (Conceptual) → "thermodynamic governance"
Level 4 (Categorical) → "entropy", "Floor", "Peace²"
Level 3 (Syntactic)   → "Entropy must decrease"
Level 2 (Lexical)     → ["Entropy", "must", "decrease"]
Level 1 (Phonetic)    → "E-n-t-r-o-p-y"

Bidirectional flow:
- Top-down: Predictions descend
- Bottom-up: Errors ascend (only if > threshold)

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class HierarchyLevel(Enum):
    """5 levels of abstraction matching cortical hierarchy."""
    PHONETIC = 1    # Character/sensory stream
    LEXICAL = 2     # Words/tokens
    SYNTACTIC = 3   # Phrases/clauses
    CATEGORICAL = 4 # Categories/taxonomies
    CONCEPTUAL = 5  # Abstract concepts


@dataclass
class HierarchicalBelief:
    """
    Belief at a specific level of hierarchy.
    """
    level: HierarchyLevel
    content: str
    confidence: float
    entropy: float  # Local ΔS at this level
    
    # Hierarchical links
    parent: Optional[str] = None  # Link to level+1
    children: List[str] = field(default_factory=list)  # Links to level-1
    
    # Temporal
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.name,
            "content": self.content[:50],  # Truncate for display
            "confidence": self.confidence,
            "entropy": self.entropy,
            "parent": self.parent,
            "children_count": len(self.children)
        }


class HierarchicalEncoder:
    """
    5-level hierarchical encoder for SENSE stage.
    
    Each level extracts higher-order structure from lower-level noise.
    Goal: Cumulative ΔS ≤ -0.6 across all levels.
    """
    
    # Entropy reduction targets per level
    DELTA_S_TARGETS = {
        HierarchyLevel.PHONETIC: 0.0,      # Raw input (no reduction)
        HierarchyLevel.LEXICAL: -0.05,      # Tokenization
        HierarchyLevel.SYNTACTIC: -0.10,    # Parsing
        HierarchyLevel.CATEGORICAL: -0.15,  # Categorization
        HierarchyLevel.CONCEPTUAL: -0.30    # Abstraction
    }
    
    def __init__(self):
        self.beliefs: Dict[str, HierarchicalBelief] = {}
    
    def encode(self, raw_input: str) -> Dict[HierarchyLevel, HierarchicalBelief]:
        """
        Encode raw input through all 5 hierarchical levels.
        """
        results = {}
        
        # Level 1: Phonetic (sensory buffer)
        phonetic = self._encode_phonetic(raw_input)
        results[HierarchyLevel.PHONETIC] = phonetic
        
        # Level 2: Lexical (tokenization)
        lexical = self._encode_lexical(raw_input, phonetic)
        results[HierarchyLevel.LEXICAL] = lexical
        
        # Level 3: Syntactic (parsing)
        syntactic = self._encode_syntactic(raw_input, lexical)
        results[HierarchyLevel.SYNTACTIC] = syntactic
        
        # Level 4: Categorical (taxonomy)
        categorical = self._encode_categorical(raw_input, syntactic)
        results[HierarchyLevel.CATEGORICAL] = categorical
        
        # Level 5: Conceptual (abstraction)
        conceptual = self._encode_conceptual(raw_input, categorical)
        results[HierarchyLevel.CONCEPTUAL] = conceptual
        
        return results
    
    def _encode_phonetic(self, raw: str) -> HierarchicalBelief:
        """Level 1: Raw sensory input."""
        belief = HierarchicalBelief(
            level=HierarchyLevel.PHONETIC,
            content=raw,
            confidence=1.0,  # Raw is certain
            entropy=len(raw) * 4.5  # Shannon entropy estimate
        )
        self.beliefs[self._hash(belief)] = belief
        return belief
    
    def _encode_lexical(self, raw: str, phonetic: HierarchicalBelief) -> HierarchicalBelief:
        """Level 2: Tokenization."""
        tokens = raw.split()
        
        # Entropy reduction through tokenization
        token_entropy = len(tokens) * 2.0  # Lower than character entropy
        delta_s = token_entropy - phonetic.entropy
        
        belief = HierarchicalBelief(
            level=HierarchyLevel.LEXICAL,
            content=" ".join(tokens[:10]),  # First 10 tokens
            confidence=0.9,
            entropy=token_entropy,
            parent=self._hash(phonetic)
        )
        phonetic.children.append(self._hash(belief))
        
        self.beliefs[self._hash(belief)] = belief
        return belief
    
    def _encode_syntactic(self, raw: str, lexical: HierarchicalBelief) -> HierarchicalBelief:
        """Level 3: Syntactic parsing."""
        # Extract key phrases
        phrases = self._extract_phrases(raw)
        
        phrase_entropy = len(phrases) * 1.5
        delta_s = phrase_entropy - lexical.entropy
        
        belief = HierarchicalBelief(
            level=HierarchyLevel.SYNTACTIC,
            content=" | ".join(phrases[:5]),
            confidence=0.85,
            entropy=phrase_entropy,
            parent=self._hash(lexical)
        )
        lexical.children.append(self._hash(belief))
        
        self.beliefs[self._hash(belief)] = belief
        return belief
    
    def _encode_categorical(self, raw: str, syntactic: HierarchicalBelief) -> HierarchicalBelief:
        """Level 4: Categorization."""
        # Extract categories
        categories = self._extract_categories(raw)
        
        cat_entropy = len(categories) * 0.8
        delta_s = cat_entropy - syntactic.entropy
        
        belief = HierarchicalBelief(
            level=HierarchyLevel.CATEGORICAL,
            content=", ".join(categories[:5]),
            confidence=0.8,
            entropy=cat_entropy,
            parent=self._hash(syntactic)
        )
        syntactic.children.append(self._hash(belief))
        
        self.beliefs[self._hash(belief)] = belief
        return belief
    
    def _encode_conceptual(self, raw: str, categorical: HierarchicalBelief) -> HierarchicalBelief:
        """Level 5: Conceptual abstraction."""
        # Extract core concept
        concept = self._extract_concept(raw)
        
        concept_entropy = 0.5  # Highly compressed
        delta_s = concept_entropy - categorical.entropy
        
        belief = HierarchicalBelief(
            level=HierarchyLevel.CONCEPTUAL,
            content=concept,
            confidence=0.75,
            entropy=concept_entropy,
            parent=self._hash(categorical)
        )
        categorical.children.append(self._hash(belief))
        
        self.beliefs[self._hash(belief)] = belief
        return belief
    
    def _extract_phrases(self, text: str) -> List[str]:
        """Extract syntactic phrases."""
        # Simple extraction - in production use proper NLP
        words = text.split()
        phrases = []
        
        for i in range(0, len(words), 3):
            phrase = " ".join(words[i:i+3])
            phrases.append(phrase)
        
        return phrases
    
    def _extract_categories(self, text: str) -> List[str]:
        """Extract categorical entities."""
        text_lower = text.lower()
        categories = []
        
        # Constitutional categories
        if any(w in text_lower for w in ["entropy", "clarity", "truth"]):
            categories.append("THERMODYNAMICS")
        if any(w in text_lower for w in ["empathy", "care", "peace"]):
            categories.append("ETHICS")
        if any(w in text_lower for w in ["floor", "constitution", "law"]):
            categories.append("GOVERNANCE")
        if any(w in text_lower for w in ["agi", "asi", "ai"]):
            categories.append("INTELLIGENCE")
        
        return categories if categories else ["GENERAL"]
    
    def _extract_concept(self, text: str) -> str:
        """Extract highest-level concept."""
        text_lower = text.lower()
        
        # Conceptual synthesis
        if "thermodynamic" in text_lower and "governance" in text_lower:
            return "THERMODYNAMIC_GOVERNANCE"
        if "empathy" in text_lower and "truth" in text_lower:
            return "COMPASSIONATE_REASON"
        if "entropy" in text_lower and "decrease" in text_lower:
            return "CLARITY_GENERATION"
        if "stakeholder" in text_lower and "weakest" in text_lower:
            return "PROTECTIVE_JUSTICE"
        
        return "ABSTRACT_CONCEPT"
    
    def _hash(self, belief: HierarchicalBelief) -> str:
        """Generate unique hash for belief."""
        content = f"{belief.level.name}:{belief.content}:{belief.timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get_cumulative_delta_s(self, results: Dict[HierarchyLevel, HierarchicalBelief]) -> float:
        """Compute cumulative entropy reduction across all levels."""
        total_delta = 0.0
        for level, belief in results.items():
            target = self.DELTA_S_TARGETS[level]
            actual = belief.entropy - self._get_parent_entropy(results, level)
            total_delta += actual if actual < 0 else 0
        return total_delta
    
    def _get_parent_entropy(self, results: Dict[HierarchyLevel, HierarchicalBelief], level: HierarchyLevel) -> float:
        """Get parent level entropy for delta calculation."""
        if level == HierarchyLevel.PHONETIC:
            return 0.0
        
        parent_level = HierarchyLevel(level.value - 1)
        if parent_level in results:
            return results[parent_level].entropy
        return 0.0


# Global encoder
_hierarchical_encoder = HierarchicalEncoder()


def encode_hierarchically(raw_input: str) -> Dict[HierarchyLevel, HierarchicalBelief]:
    """Convenience function for hierarchical encoding."""
    return _hierarchical_encoder.encode(raw_input)


def get_cumulative_delta_s(results: Dict[HierarchyLevel, HierarchicalBelief]) -> float:
    """Convenience function for cumulative entropy calculation."""
    return _hierarchical_encoder.get_cumulative_delta_s(results)


__all__ = [
    "HierarchyLevel",
    "HierarchicalBelief",
    "HierarchicalEncoder",
    "encode_hierarchically",
    "get_cumulative_delta_s"
]
