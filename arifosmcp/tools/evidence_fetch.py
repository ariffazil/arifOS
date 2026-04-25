"""
Compatibility shim — renamed to evidence.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("evidence_fetch.py is deprecated — use evidence.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.evidence import *  # noqa: F401,F403
