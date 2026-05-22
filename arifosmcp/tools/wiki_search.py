"""arifos_wiki_search — DEPRECATED (replaced by arifos_wiki_tools.search.search_index).

This module is kept as a stub to avoid import errors in existing code.
All functionality has been migrated to arifos_wiki_tools.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "arifos_wiki_search is deprecated. Use arifos_wiki_tools.search.search_index instead.",
    DeprecationWarning,
    stacklevel=2,
)


def arifos_wiki_search(*args, **kwargs):
    """Deprecated. Use arifos_wiki_tools.search.search_index instead."""
    raise NotImplementedError(
        "arifos_wiki_search is deprecated. Use arifos_wiki_tools.search.search_index instead."
    )
