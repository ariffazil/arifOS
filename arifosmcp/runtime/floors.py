"""
Compatibility shim — floors.py renamed to floor.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("floors.py is deprecated — use floor.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.runtime.floor import *  # noqa: F401,F403
