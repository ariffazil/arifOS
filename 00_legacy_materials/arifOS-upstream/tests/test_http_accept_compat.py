from __future__ import annotations

from arifosmcp.runtime.fastmcp_ext.transports import _ensure_json_accept_header


def test_adds_json_accept_when_missing():
    headers = [(b"content-type", b"application/json")]

    result = _ensure_json_accept_header(headers)

    assert (b"accept", b"application/json") in result


def test_preserves_existing_json_accept():
    headers = [(b"accept", b"application/json, text/event-stream")]

    result = _ensure_json_accept_header(headers)

    assert result == headers


def test_appends_json_accept_to_wildcard():
    headers = [(b"accept", b"*/*")]

    result = _ensure_json_accept_header(headers)

    assert any(
        name.lower() == b"accept" and b"*/*" in value and b"application/json" in value
        for name, value in result
    )
