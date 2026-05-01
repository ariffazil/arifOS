"""
Compatibility shim — renamed to ops.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("ops_measure.py is deprecated — use ops.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.ops import *  # noqa: F401,F403
