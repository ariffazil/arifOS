"""
Foundation Layer - Core Utilities

Provides foundational utilities for type safety, validation, and defensive programming.

F1 (Amanah): Type safety prevents crashes and undefined behavior.
F2 (Truth): Safe conversions ensure data integrity.
"""

from .safe_types import safe_float, safe_bool, safe_int

__all__ = ["safe_float", "safe_bool", "safe_int"]
