"""
DEPRECATED (2026-08-25): This module is superseded by arifosmcp.runtime.ssrf_guard.
String-prefix matching cannot detect hex/octal/IPv6 IP notations (e.g.
http://2130706433/ = 127.0.0.1, http://0x7f.0.0.1/, http://[::1]/).
All callers MUST migrate to resolve_blocked() from arifosmcp.runtime.ssrf_guard.
This file is retained only for backward compatibility — do not add new imports.
═════════════════════════════════════════════════════════════

arifosmcp/runtime/a_rif/ssrf_guard.py — URL Safety Validation
"""

from __future__ import annotations

import urllib.parse

__all__ = ["validate_url_safety"]

PRIVATE_HOST_PATTERNS = (
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
    "::1",
)
PRIVATE_PREFIXES = (
    "10.",
    "192.168.",
    "172.16.",
    "172.17.",
    "172.18.",
    "172.19.",
    "172.20.",
    "172.21.",
    "172.22.",
    "172.23.",
    "172.24.",
    "172.25.",
    "172.26.",
    "172.27.",
    "172.28.",
    "172.29.",
    "172.30.",
    "172.31.",
    "169.254.",
)
ALLOWED_SCHEMES = ("http", "https")


def validate_url_safety(url: str) -> dict:
    """
    Validate that a URL is safe to fetch.

    Returns dict with:
        safe: bool
        risk_flags: list[str]
        reason: str
    """
    risk_flags: list[str] = []
    reason = ""

    parsed = urllib.parse.urlparse(url)
    hostname = (parsed.hostname or "").lower()

    if parsed.scheme not in ALLOWED_SCHEMES:
        risk_flags.append("scheme_blocked")
        reason = f"Scheme '{parsed.scheme}' not allowed"

    if hostname in PRIVATE_HOST_PATTERNS or hostname.startswith(PRIVATE_PREFIXES):
        risk_flags.append("private_ip_access")
        reason = f"Hostname '{hostname}' resolves to private network"

    if hostname.endswith((".internal", ".private", ".local")):
        risk_flags.append("internal_domain")
        reason = f"Domain '{hostname}' is internal"

    return {
        "safe": not bool(risk_flags),
        "risk_flags": risk_flags,
        "reason": reason,
    }
