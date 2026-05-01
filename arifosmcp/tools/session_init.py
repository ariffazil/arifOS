"""
Compatibility shim — renamed to session.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("session_init.py is deprecated — use session.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.session import *  # noqa: F401,F403
