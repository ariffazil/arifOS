"""
L4_MCP Floors Package - Constitutional Floor Checks (F1-F9).

All floor semantics are CANONICAL (bound to L1_THEORY):
- F1: Amanah (Trust/No Harm)
- F2: Truth (≥0.99)
- F3: Tri-Witness
- F4: Clarity (ΔS)
- F5: Peace² (Vitality)
- F6: κᵣ (Empathy/Resonance)
- F7: Ω₀ (Humility, 0.03-0.05)
- F8: Genius (G)
- F9: Anti-Hantu (C_dark)
"""

from .evaluate import evaluate_floors, FloorEvalResult

__all__ = ["evaluate_floors", "FloorEvalResult"]
