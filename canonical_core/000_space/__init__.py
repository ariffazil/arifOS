"""
Rooms - Parallel Execution Engines (Trinity Architecture)

AGI Room: HOT PHASE (111-333) - Reasoning
ASI Room: WARM PHASE (555-666) - Empathy/Safety
APEX Room: COLD PHASE (777-999) - Judgment/Sealing
"""

from .asi_room import ASIRoom, get_asi_room, purge_asi_room, list_active_asi_rooms, ASI_FLOORS

__all__ = [
    "ASIRoom",
    "get_asi_room",
    "purge_asi_room",
    "list_active_asi_rooms",
    "ASI_FLOORS",
]
