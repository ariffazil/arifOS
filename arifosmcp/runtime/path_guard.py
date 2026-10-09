"""
path_guard.py — filesystem containment for URI-path-derived reads.

Forged 2026-09-22 after tracing the 2026-09-15 external report class
(Syed Anas Mohiuddin): fastmcp matches URI templates *before* percent-decoding,
so ``%2F`` / ``%2e%2e`` smuggle ``../`` past a ``[^/]+`` segment guard. Any
resource that turns a URI path parameter into a filesystem path MUST resolve
the candidate against its root and refuse anything that escapes it. A bare
``.endswith(".md")`` or character blocklist is a content-type convention, not a
boundary — ``sovereign://{file}`` shipped with only that convention and read
``/etc/hostname`` via ``_read_file("/etc/hostname")`` → ``OK`` (reproduced
2026-09-22).

This module is the SINGLE source of truth for the check. Call sites:

  - ``sovereign://{file}``  (resources/sovereign.py)          — wired 2026-09-22
  - ``arifos://atlas333/scar/{id}`` (resources/atlas333.py)   — inline equivalent
  - ``skill://{name}/SKILL.md``     (server.py)               — inline equivalent
  - ``tree777://*`` (resources/tree777.py, ``_within_wiki_root``) — inline equivalent

The three inline equivalents predate this module, are correct, and are
candidates for consolidation — not urgent fixes. New filesystem reads keyed on
a URI path parameter import from here; that is the whole point.

The check resolves symlinks too, so a link inside the root pointing out is
caught the same as ``../``.
"""

from __future__ import annotations

from pathlib import Path


def contained_path(root: str | Path, *parts: str) -> Path:
    """Return ``root / parts`` resolved, or raise ``ValueError`` if it escapes ``root``.

    Fail-closed: anything that is not strictly inside ``root`` raises. Callers
    that have an envelope contract should catch the ``ValueError`` and return a
    ``REJECTED`` envelope; callers that want a loud boundary should let it
    propagate (mirrors ``_prop_key`` in ``l5_sovereign_forge.py``).
    """
    root_p = Path(root).resolve()
    candidate = (Path(root) / Path(*parts)).resolve()
    if root_p != candidate and root_p not in candidate.parents:
        raise ValueError(
            f"path escapes resource root {str(root_p)!r}: {str(candidate)!r} "
            "(URI path parameters must stay within their resource root)"
        )
    return candidate
