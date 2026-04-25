"""
Compatibility shim — governance_identities.py renamed to governance_identity.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("governance_identities.py is deprecated — use governance_identity.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.runtime.governance_identity import *  # noqa: F401,F403
