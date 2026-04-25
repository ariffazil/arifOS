"""
Compatibility shim — renamed to memory.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("memory_recall.py is deprecated — use memory.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.memory import *  # noqa: F401,F403
