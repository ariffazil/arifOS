from __future__ import annotations

import math


def shannon_entropy(text: str) -> dict[str, float]:
    if not text:
        return {"entropy": 0.0, "normalized_entropy": 0.0}
    counts = {}
    for char in text:
        counts[char] = counts.get(char, 0) + 1
    total = len(text)
    entropy = -sum((count / total) * math.log2(count / total) for count in counts.values())
    max_entropy = math.log2(len(counts)) if len(counts) > 1 else 1.0
    return {"entropy": entropy, "normalized_entropy": min(1.0, entropy / max_entropy)}


def coherence_score(
    contradiction_ratio: float = 0.0, drift_from_baseline: float = 0.0
) -> dict[str, float]:
    coherence = max(0.0, 1.0 - contradiction_ratio - drift_from_baseline)
    return {"coherence": coherence}


def landauer_limit(bits_erased: float = 0.0) -> dict[str, float]:
    return {"energy_joules": max(0.0, bits_erased) * 2.9e-21}
