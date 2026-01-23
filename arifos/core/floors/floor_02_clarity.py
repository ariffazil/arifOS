"""
Floor 2: Clarity (ΔS) Detection and Optimization
X7K9F24 - Entropy Reduction via Clarity Measurement

This module implements F2 (Clarity) floor detection for constitutional governance,
measuring information clarity and entropy reduction in text content.

Status: SEALED
Nonce: X7K9F24
"""

import re
import math
from typing import Dict, List, Any, Tuple, Optional


def compute_clarity_delta(text1: str, text2: str) -> Dict[str, float]:
    """
    Compute clarity delta (ΔS) between two texts.
    
    Measures the information clarity difference between texts using:
    - Semantic similarity
    - Information density
    - Structural coherence
    
    Args:
        text1: First text (reference)
        text2: Second text (comparison)
        
    Returns:
        Dictionary with clarity metrics
    """
    # Basic text preprocessing
    text1_clean = _preprocess_text(text1)
    text2_clean = _preprocess_text(text2)
    
    # Compute various clarity metrics
    semantic_similarity = _compute_semantic_similarity(text1_clean, text2_clean)
    information_density1 = _compute_information_density(text1_clean)
    information_density2 = _compute_information_density(text2_clean)
    structural_coherence1 = _compute_structural_coherence(text1_clean)
    structural_coherence2 = _compute_structural_coherence(text2_clean)
    
    # Calculate clarity delta
    density_delta = information_density2 - information_density1
    coherence_delta = structural_coherence2 - structural_coherence1
    
    # Combined clarity score (0.0 to 1.0, higher = more clarity)
    clarity_score = max(0.0, min(1.0, 
        (semantic_similarity * 0.4) + 
        (max(0, density_delta) * 0.3) + 
        (max(0, coherence_delta) * 0.3)
    ))
    
    return {
        "clarity_score": clarity_score,
        "semantic_similarity": semantic_similarity,
        "density_delta": density_delta,
        "coherence_delta": coherence_delta,
        "information_density_1": information_density1,
        "information_density_2": information_density2,
        "structural_coherence_1": structural_coherence1,
        "structural_coherence_2": structural_coherence2
    }


def _preprocess_text(text: str) -> str:
    """Preprocess text for clarity analysis."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Convert to lowercase for analysis
    text = text.lower()
    
    return text


def _compute_semantic_similarity(text1: str, text2: str) -> float:
    """Compute semantic similarity between texts using simple word overlap."""
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if not words1 or not words2:
        return 0.0
    
    # Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def _compute_information_density(text: str) -> float:
    """Compute information density of text."""
    if not text.strip():
        return 0.0
    
    # Count content words (exclude common stop words)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
    }
    
    words = text.split()
    content_words = [word for word in words if word not in stop_words]
    
    # Information density as ratio of content words to total words
    return len(content_words) / len(words) if words else 0.0


def _compute_structural_coherence(text: str) -> float:
    """Compute structural coherence of text."""
    if not text.strip():
        return 0.0
    
    # Simple coherence metrics
    sentences = _split_into_sentences(text)
    
    if len(sentences) < 2:
        return 0.5  # Neutral score for short texts
    
    # Check for transitional phrases
    transitional_words = {
        'however', 'therefore', 'furthermore', 'moreover', 'consequently',
        'additionally', 'nevertheless', 'meanwhile', 'subsequently', 'thus'
    }
    
    transition_count = sum(1 for word in text.split() if word in transitional_words)
    
    # Check sentence length consistency
    sentence_lengths = [len(sent.split()) for sent in sentences]
    length_variance = _compute_variance(sentence_lengths)
    
    # Coherence score based on transitions and length consistency
    transition_score = min(1.0, transition_count / len(sentences))
    length_score = max(0.0, 1.0 - (length_variance / 100))  # Normalize variance
    
    return (transition_score * 0.6) + (length_score * 0.4)


def _split_into_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    # Simple sentence splitting
    sentences = re.split(r'[.!?]+', text)
    return [sent.strip() for sent in sentences if sent.strip()]


def _compute_variance(values: List[float]) -> float:
    """Compute variance of a list of values."""
    if len(values) < 2:
        return 0.0
    
    mean = sum(values) / len(values)
    squared_diffs = [(x - mean) ** 2 for x in values]
    return sum(squared_diffs) / len(squared_diffs)


def detect_clarity_improvement(
    original_text: str,
    improved_text: str,
    threshold: float = 0.1
) -> Dict[str, Any]:
    """
    Detect if text shows clarity improvement.
    
    Args:
        original_text: Original text
        improved_text: Improved text
        threshold: Minimum improvement threshold
        
    Returns:
        Dictionary with improvement analysis
    """
    clarity_result = compute_clarity_delta(original_text, improved_text)
    clarity_score = clarity_result["clarity_score"]
    
    improvement_detected = clarity_score > threshold
    
    return {
        "improvement_detected": improvement_detected,
        "clarity_score": clarity_score,
        "threshold": threshold,
        "details": clarity_result,
        "recommendation": "Text shows clarity improvement" if improvement_detected else "No significant clarity improvement detected"
    }


def optimize_for_clarity(text: str) -> Dict[str, Any]:
    """
    Optimize text for maximum clarity (F2 compliance).
    
    Args:
        text: Text to optimize
        
    Returns:
        Dictionary with optimized text and clarity metrics
    """
    original_clarity = _compute_overall_clarity(text)
    
    # Apply clarity optimizations
    optimized_text = _apply_clarity_optimizations(text)
    optimized_clarity = _compute_overall_clarity(optimized_text)
    
    clarity_improvement = optimized_clarity - original_clarity
    
    return {
        "original_text": text,
        "optimized_text": optimized_text,
        "original_clarity": original_clarity,
        "optimized_clarity": optimized_clarity,
        "clarity_improvement": clarity_improvement,
        "optimizations_applied": _get_applied_optimizations(text, optimized_text)
    }


def _compute_overall_clarity(text: str) -> float:
    """Compute overall clarity score for text."""
    if not text.strip():
        return 0.0
    
    # Combine multiple clarity factors
    info_density = _compute_information_density(text)
    struct_coherence = _compute_structural_coherence(text)
    sentence_clarity = _compute_sentence_clarity(text)
    
    # Weighted average
    return (info_density * 0.3) + (struct_coherence * 0.4) + (sentence_clarity * 0.3)


def _compute_sentence_clarity(text: str) -> float:
    """Compute sentence-level clarity."""
    sentences = _split_into_sentences(text)
    
    if not sentences:
        return 0.0
    
    clarity_scores = []
    for sentence in sentences:
        # Check sentence complexity
        words = sentence.split()
        if len(words) == 0:
            continue
        
        # Long sentences are less clear
        length_score = max(0.0, 1.0 - (len(words) - 15) / 30) if len(words) > 15 else 1.0
        
        # Complex words reduce clarity
        complex_words = [word for word in words if len(word) > 7]
        complexity_score = max(0.0, 1.0 - len(complex_words) / len(words))
        
        sentence_score = (length_score * 0.6) + (complexity_score * 0.4)
        clarity_scores.append(sentence_score)
    
    return sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0.0


def _apply_clarity_optimizations(text: str) -> str:
    """Apply clarity optimizations to text."""
    optimized = text
    
    # Remove redundant phrases
    redundant_phrases = [
        (r'in order to', 'to'),
        (r'due to the fact that', 'because'),
        (r'for the purpose of', 'for'),
        (r'at this point in time', 'now'),
        (r'in the event that', 'if'),
        (r'it is important to note that', ''),
        (r'it should be noted that', ''),
    ]
    
    for pattern, replacement in redundant_phrases:
        optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
    
    # Simplify complex sentences (basic implementation)
    sentences = _split_into_sentences(optimized)
    simplified_sentences = []
    
    for sentence in sentences:
        words = sentence.split()
        if len(words) > 20:  # Long sentence
            # Try to split at conjunctions
            conjunctions = [' and ', ' but ', ' or ', ' however ']
            for conj in conjunctions:
                if conj in sentence:
                    parts = sentence.split(conj, 1)
                    if len(parts) == 2:
                        simplified_sentences.append(parts[0].strip() + '.')
                        simplified_sentences.append(parts[1].strip())
                        break
            else:
                simplified_sentences.append(sentence)
        else:
            simplified_sentences.append(sentence)
    
    return ' '.join(simplified_sentences)


def _get_applied_optimizations(original: str, optimized: str) -> List[str]:
    """Get list of optimizations applied."""
    optimizations = []
    
    if len(optimized) < len(original):
        optimizations.append("Reduced text length")
    
    # Check for specific optimizations
    if 'in order to' in original.lower() and 'in order to' not in optimized.lower():
        optimizations.append("Removed redundant phrases")
    
    original_sentences = _split_into_sentences(original)
    optimized_sentences = _split_into_sentences(optimized)
    
    if len(optimized_sentences) > len(original_sentences):
        optimizations.append("Split long sentences")
    
    return optimizations


def detect_semantic_duplication(
    query1: str,
    query2: str,
    threshold: float = 0.85
) -> Dict[str, Any]:
    """
    Detect semantic duplication between queries for cache deduplication.
    
    Args:
        query1: First query
        query2: Second query
        threshold: Similarity threshold for duplication
        
    Returns:
        Dictionary with duplication analysis
    """
    clarity_result = compute_clarity_delta(query1, query2)
    semantic_similarity = clarity_result["semantic_similarity"]
    clarity_score = clarity_result["clarity_score"]
    
    # Combined duplication score
    duplication_score = (semantic_similarity * 0.7) + (clarity_score * 0.3)
    
    is_duplicate = duplication_score >= threshold
    
    return {
        "is_duplicate": is_duplicate,
        "duplication_score": duplication_score,
        "threshold": threshold,
        "semantic_similarity": semantic_similarity,
        "clarity_score": clarity_score,
        "recommendation": "Treat as duplicate" if is_duplicate else "Treat as distinct query"
    }


def check_clarity_floor_compliance(text: str, min_clarity: float = 0.7) -> Dict[str, Any]:
    """
    Check if text meets F2 (Clarity) floor requirements.
    
    Args:
        text: Text to check
        min_clarity: Minimum clarity threshold
        
    Returns:
        Dictionary with compliance check results
    """
    clarity_score = _compute_overall_clarity(text)
    is_compliant = clarity_score >= min_clarity
    
    return {
        "is_compliant": is_compliant,
        "clarity_score": clarity_score,
        "min_threshold": min_clarity,
        "floor": "F2",
        "verdict": "PASS" if is_compliant else "FAIL",
        "recommendation": "Text meets clarity requirements" if is_compliant else "Text needs clarity improvement"
    }