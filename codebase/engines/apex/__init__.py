"""
codebase.engines.apex — APEX (Soul) Judicial Engine

Stages 444-888: Trinity Sync, Judicial Judgment
"""

from .apex_engine import APEXRoom, get_apex_room, purge_apex_room, list_active_apex_rooms
from .kernel import APEXJudicialCore

__all__ = [
    "APEXRoom",
    "get_apex_room",
    "purge_apex_room", 
    "list_active_apex_rooms",
    "APEXJudicialCore"
]
