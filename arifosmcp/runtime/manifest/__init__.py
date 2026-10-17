"""
arifOS Runtime Manifest Package.

Build-time / runtime surface comparison for the observatory.
DITEMPA BUKAN DIBERI.
"""

# Legacy public API (2026-10-16): the manifest/ package shadowed the old
# manifest.py module, making these unimportable. Moved to legacy.py and
# re-exported here so callers and the test contract keep working.
from arifosmcp.runtime.manifest.legacy import (  # noqa: F401
    BuildManifest,
    RuntimeManifest,
    generate_build_manifest,
    gather_runtime_manifest,
)
from arifosmcp.runtime.manifest.legacy import (  # noqa: F401
    ALIGNED,
    DRIFT,
    UNKNOWN,
    _kernel_reachable,
)
from arifosmcp.runtime.manifest.legacy import (  # noqa: F401
    DriftReport,
    compare_manifests,
)
from arifosmcp.runtime.manifest.legacy import CANONICAL_STATES  # noqa: F401
