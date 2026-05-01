"""
Compatibility shim — renamed to vault.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("vault_seal.py is deprecated — use vault.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.vault import *  # noqa: F401,F403
