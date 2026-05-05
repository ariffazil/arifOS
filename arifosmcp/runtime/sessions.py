"""
Compatibility shim — sessions.py renamed to session.py
This file will be removed after one sprint.
"""

import warnings  # noqa: E402

warnings.warn(  # noqa: E402
    "sessions.py is deprecated — use session.py instead", DeprecationWarning, stacklevel=2
)
from arifosmcp.runtime.session import *  # noqa: F401,F403,E402
from arifosmcp.runtime.session import (  # noqa: F401,E402
    _normalize_session_id,
    _resolve_canonical_actor,
    _resolve_session_id,
)
