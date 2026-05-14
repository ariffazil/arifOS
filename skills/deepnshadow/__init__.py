"""deepnshadow skill — DEPRECATED.

Moved to internal protocol: arifosmcp.protocols.deepnshadow
No longer registered as a public skill. Use existing arif_* tools
with deepnshadow mode instead.
"""

import warnings

warnings.warn(
    "skills.deepnshadow is deprecated. Use arifosmcp.protocols.deepnshadow instead.",
    DeprecationWarning,
    stacklevel=2,
)

from .handler import DeepnShadowSkill, execute

__all__ = ["DeepnShadowSkill", "execute"]
