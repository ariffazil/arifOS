"""Compatibility shim — renamed to capability.py"""
import warnings
warnings.warn("capability_map.py is deprecated — use capability.py", DeprecationWarning, stacklevel=2)
from capability import *  # noqa: F401,F403
