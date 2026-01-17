"""
Paradox Engine: Formal Contradiction Resolution

Constitutional Integration:
- Detects logical contradictions in reasoning
- Creates ScarPackets with PP/PS/Psi/Phi metrics
- Implements "Ditempa Bukan Diberi" at the logical level
"""
from arifos_core.engines.paradox.paradox_detector import ParadoxDetector, ScarPacket
from arifos_core.engines.paradox.metrics_tracker import ParadoxMetrics

__all__ = [
    "ParadoxDetector",
    "ParadoxMetrics",
    "ScarPacket",
]
