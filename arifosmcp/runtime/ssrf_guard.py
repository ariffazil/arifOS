"""SSRF guard — resolve-then-verify URL egress safety for every fetch path.

Forged 2026-08-25 after an external report (Syed Anas Mohiuddin, private
disclosure): ``_arif_evidence_fetch`` flagged private IPs by URL-string
prefix only, and its RealityHandler fallback re-fetched URLs the primary
path had just blocked (fail-open). Both layers also missed non-dotted IP
notations (``http://2130706433/`` = 127.0.0.1, ``http://0x7f.0.0.1/``,
``http://[::1]/``, ``http://0.0.0.0/``).

This module is the SINGLE source of truth. Every address the resolver
would hand to the socket is checked against ``ipaddress`` classification —
string prefix matching is gone.

Residual (accepted, documented): resolve-at-check vs resolve-at-connect
leaves a DNS-rebinding TOCTOU window. Closing it fully requires pinning
the resolved IP into the transport; the MCP surface is localhost-bound,
so this residual is proportionate for now.
"""

from __future__ import annotations

import ipaddress
import socket
import urllib.parse

_ALLOWED_SCHEMES = ("http", "https")

_BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "local",
        "loopback",
        "ip6-localhost",
        "ip6-loopback",
        "localhost.localdomain",
    }
)

# A blocked URL returns one of these flags; a safe URL returns None.
FLAG_PRIVATE = "private_ip_access"
FLAG_SCHEME = "scheme_blocked"
FLAG_NO_URL = "url_missing"
FLAG_NO_DNS = "dns_unresolvable"
FLAG_DNS_ANOMALY = "dns_resolution_anomaly"


def _hostname_is_blocked(host: str | None) -> bool:
    if not host:
        return True
    h = host.lower().rstrip(".")
    if h in _BLOCKED_HOSTNAMES:
        return True
    return h.endswith((".localhost", ".local", ".internal"))


def _ip_is_blocked(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """True for anything that must never be an egress target."""
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def resolve_blocked(url: str | None) -> str | None:
    """Validate a fetch URL. Returns a risk-flag string if blocked, else None.

    Checks, in order:
      1. scheme is http/https
      2. hostname is not a local name (localhost, *.local, *.internal)
      3. literal IPs classified via ``ipaddress`` (v4/v6, any notation the
         parser accepts)
      4. DNS resolution — EVERY returned address must be public, because
         ``getaddrinfo`` applies the same exotic-notation semantics
         (integer/hex/octal) the real fetch would use
    """
    if not url:
        return FLAG_NO_URL
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError:
        return FLAG_SCHEME
    if parsed.scheme not in _ALLOWED_SCHEMES:
        return FLAG_SCHEME
    host = parsed.hostname
    if host is None or _hostname_is_blocked(host):
        return FLAG_PRIVATE

    # Fast path: literal IP (covers dotted-quad, IPv6, and any integer/hex
    # form ipaddress understands).
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        return FLAG_PRIVATE if _ip_is_blocked(ip) else None

    # Resolve path: verify every address the socket layer would use.
    try:
        port = parsed.port
    except ValueError:
        return FLAG_SCHEME
    if port is None:
        port = 443 if parsed.scheme == "https" else 80
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except (OSError, UnicodeError):
        return FLAG_NO_DNS
    if not infos:
        return FLAG_NO_DNS
    for info in infos:
        addr = str(info[4][0])
        # Strip IPv6 zone index (fe80::1%eth0).
        addr = addr.split("%", 1)[0]
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError:
            return FLAG_DNS_ANOMALY
        if _ip_is_blocked(ip):
            return FLAG_PRIVATE
    return None
