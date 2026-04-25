"""
Compatibility shim — sessions.py renamed to session.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("sessions.py is deprecated — use session.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.runtime.session import *  # noqa: F401,F403
