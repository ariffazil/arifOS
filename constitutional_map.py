"""Compatibility shim — renamed to constitution.py"""
import warnings
warnings.warn("constitutional_map.py is deprecated — use constitution.py", DeprecationWarning, stacklevel=2)
from constitution import *  # noqa: F401,F403
