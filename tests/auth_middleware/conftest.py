"""
Fixtures for SCTMiddleware test suite.

Transport awareness (FastMCP 3.4.5 → 4 migration note):
  - Client(transport=mcp) uses InMemoryTransport — get_http_headers() returns {}
  - This naturally tests "no auth header" scenarios
  - Scenarios requiring specific headers MUST mock get_http_headers()
  - Integration tests (streamable-http with ASGITransport) test real HTTP auth flow
  - When migrating to FastMCP 4: verify get_http_headers() still returns {} on
    non-HTTP transport (FastMCP 4 may change this behavior)
"""

from __future__ import annotations

import pytest


@pytest.fixture
def valid_sct_token() -> str:
    """A syntactically valid SCT (not cryptographically valid — for middleware testing)."""
    return (
        "sct_v1.eyJhY3RvciI6InRlc3QtYWdlbnQiLCJzaWQiOiJURVNULXNlc3Npb24iLC"
        "JhdXRoIjoiTElNSVRFRF9NVVRBVEUiLCJleHAiOjk5OTk5OTk5OTl9.dummy_hmac"
    )
