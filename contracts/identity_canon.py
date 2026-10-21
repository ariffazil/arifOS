"""IDENTITY_CANON v1 — one resolver, one rule.

T1 of the 2026-10-22 OpenCode identity directive (DIR-E1). Forged after the
live fork: `claude/opus-5.5` produced standing.canonical_id=`claude`,
ACT actor=`CLAUDE`, session_birth.actor_id=`CLAUDE` from three independent
resolvers.

THE RULE (contracts/IDENTITY_CANON.md):
  1. The CLAIMED handle is identity of record. It is never overwritten.
  2. The CANONICAL id is for comparison only.
  3. comparison_key = canonical id, lowercased, separators removed.
  4. Every identity block in a payload reads ONE resolved identity object.

Resolution order:
  1. contracts.identity.CANONICAL_ACTORS — exact, alias, then slash head/tail
  2. runtime.governance_identity.normalize_actor_id — sovereign NLP aliases
  3. mechanical — NFC lowercase, `[_ space] → -`, collapse repeats

comparison_key strips `-`, `_`, space, `.` and `/` so `mesa-test-agent`,
`mesa_test_agent` and `Mesa Test Agent` all compare equal without renaming
anything on disk.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

__canon_version__ = "1.0.0"

_SLASH_RE = re.compile(r"/")
_SEP_RE = re.compile(r"[-_\s.]+")

# F13 ruling 2026-10-22: role/power strings are NOT names. Resolving them to a
# principal lets anyone claim sovereignty with a string — escalation without a
# signature. They resolve to NOTHING (anonymous), in every lane, before any
# registry or alias layer runs. The committed kernel layers still contain these
# mappings (residue reported) — this canon is the enforcement point for
# identity comparisons and every payload block that reads it.
ROLE_STRING_BLOCKLIST = frozenset({"f13", "sovereign", "888", "arif-fazil.com"})


def is_role_string(raw: str | None) -> bool:
    if not raw:
        return False
    return raw.strip().lower() in ROLE_STRING_BLOCKLIST


def _mechanical(raw: str) -> str:
    """Deterministic fallback form for unknown handles."""
    text = unicodedata.normalize("NFC", raw.strip())
    text = text.lower()
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    # normalize each slash segment the same way, keep the slash
    parts = [_SLASH_RE.split(text)]
    if len(parts) == 1 and "/" not in text:
        return text
    segments = [_mechanical_segment(p) for p in text.split("/")]
    return "/".join(segments)


def _mechanical_segment(seg: str) -> str:
    seg = re.sub(r"[\s_]+", "-", seg)
    seg = re.sub(r"-{2,}", "-", seg)
    return seg


def _comparison_key(canonical: str) -> str:
    return _SEP_RE.sub("", canonical.strip().lower())


def resolve_actor_identity(raw: str | None) -> dict[str, Any]:
    """Resolve a raw actor handle to {claimed, canonical_id, comparison_key, source}.

    Never raises. Never mutates the claim. Unknown handles resolve
    mechanically — an unknown actor is not a rejected actor; verification
    is a separate concern (see contracts/identity.py verification_state).
    """
    if raw is None or not str(raw).strip():
        return {
            "claimed": raw,
            "canonical_id": None,
            "comparison_key": None,
            "source": "empty",
            "canon_version": __canon_version__,
        }

    claimed = unicodedata.normalize("NFC", str(raw).strip())

    # F13 2026-10-22: role/power strings resolve to nothing — BEFORE any
    # alias layer sees them. No principal, no comparison key.
    if is_role_string(claimed):
        return {
            "claimed": claimed,
            "canonical_id": None,
            "comparison_key": None,
            "source": "rejected_role_string",
            "canon_version": __canon_version__,
        }

    # Layer 1+2: existing resolvers, in the order session.py applies them.
    canonical: str | None = None
    source = "mechanical"
    try:
        from arifosmcp.runtime.governance_identity import normalize_actor_id

        layer1 = normalize_actor_id(claimed)
        if layer1:
            canonical = str(layer1)
            if canonical != claimed:
                source = "sovereign_alias"
    except Exception:  # noqa: BLE001 — resolver must never raise
        canonical = claimed

    try:
        from contracts.identity import normalize_actor_identity

        layer2 = normalize_actor_identity(canonical or claimed)
        if layer2 and layer2.get("normalized"):
            canonical = str(layer2["normalized"])
            source = "canonical_registry"
    except Exception:  # noqa: BLE001
        pass

    if canonical is None:
        canonical = _mechanical(claimed)
        source = "mechanical"

    return {
        "claimed": claimed,
        "canonical_id": canonical,
        "comparison_key": _comparison_key(canonical),
        "source": source,
        "canon_version": __canon_version__,
    }


def same_principal(a: str | None, b: str | None) -> bool:
    """True when two handles resolve to the same principal."""
    ra = resolve_actor_identity(a)
    rb = resolve_actor_identity(b)
    if ra["comparison_key"] is None or rb["comparison_key"] is None:
        return False
    return ra["comparison_key"] == rb["comparison_key"]
