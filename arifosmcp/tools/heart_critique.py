"""
Compatibility shim — renamed to heart.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("heart_critique.py is deprecated — use heart.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.heart import *  # noqa: F401,F403
