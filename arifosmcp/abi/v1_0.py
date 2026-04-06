"""Canonical ABI location.

The refactor branch introduced ABI schemas under the legacy ``arifos_mcp``
package path. ``arifosmcp`` is the canonical package name on ``main``, so this
module re-exports the same schemas from the compatibility location until the
tree is fully consolidated.
"""

from arifos_mcp.abi.v1_0 import *  # noqa: F401,F403
