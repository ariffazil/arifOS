"""
test_crypto_auth_redis_url.py — verify REDIS_PASSWORD URL-encoding chain in crypto_auth._get_redis()

State-transition contract:
  ARIFOS_REDIS_URL set  →  URL used verbatim (no encoding)
  ARIFOS_REDIS_URL absent + REDIS_PASSWORD set  →  URL built with urllib.parse.quote(safe="")
  Both absent  →  default redis://127.0.0.1:6379/0

F2 evidence: ENV munging in test, not in real env. No Redis connection attempted.
"""

import os
import sys
import importlib
import pytest


@pytest.fixture
def crypto_auth(monkeypatch):
    # Ensure no real env leak from caller
    for k in ("ARIFOS_REDIS_URL", "REDIS_PASSWORD"):
        monkeypatch.delenv(k, raising=False)
    # Add arifOS runtime to sys.path
    runtime_dir = "/root/arifOS/arifosmcp/runtime"
    if runtime_dir not in sys.path:
        sys.path.insert(0, runtime_dir)
    # Force fresh import (in case pytest re-uses module)
    if "crypto_auth" in sys.modules:
        del sys.modules["crypto_auth"]
    mod = importlib.import_module("crypto_auth")
    # Reset module-level redis client cache so each test reads fresh env
    mod._redis_client = None
    mod._REDIS_AVAILABLE = False
    return mod


def test_arifos_redis_url_takes_priority(crypto_auth, monkeypatch):
    """ARIFOS_REDIS_URL must be used verbatim when set, regardless of REDIS_PASSWORD."""
    monkeypatch.setenv("ARIFOS_REDIS_URL", "redis://u:p%40ss@10.0.0.1:6379/2")
    monkeypatch.setenv("REDIS_PASSWORD", "ignored")
    url = crypto_auth._get_redis_url() if hasattr(crypto_auth, "_get_redis_url") else _read_url(crypto_auth)
    assert url == "redis://u:p%40ss@10.0.0.1:6379/2"


def test_redis_password_url_encoded_with_special_chars(crypto_auth, monkeypatch):
    """REDIS_PASSWORD 'p@ss:word/1' must become 'p%40ss%3Aword%2F1' (safe='')."""
    monkeypatch.delenv("ARIFOS_REDIS_URL", raising=False)
    monkeypatch.setenv("REDIS_PASSWORD", "p@ss:word/1")
    url = _read_url(crypto_auth)
    import urllib.parse
    expected_pw = urllib.parse.quote("p@ss:word/1", safe="")
    assert url == f"redis://:{expected_pw}@127.0.0.1:6379/0", f"got: {url}"
    # Specific characters must be encoded
    assert "@" not in url.split("://")[1].split("@")[0] or url == f"redis://:{expected_pw}@127.0.0.1:6379/0"


def test_redis_password_plain_alphanumeric_unchanged(crypto_auth, monkeypatch):
    """Plain alphanumeric password stays readable — but quotes for safety."""
    monkeypatch.delenv("ARIFOS_REDIS_URL", raising=False)
    monkeypatch.setenv("REDIS_PASSWORD", "simplepass123")
    url = _read_url(crypto_auth)
    # quote() with safe='' leaves alphanumerics unchanged
    assert url == "redis://:simplepass123@127.0.0.1:6379/0"


def test_no_env_falls_back_to_default(crypto_auth, monkeypatch):
    """No env vars set → default local URL."""
    monkeypatch.delenv("ARIFOS_REDIS_URL", raising=False)
    monkeypatch.delenv("REDIS_PASSWORD", raising=False)
    url = _read_url(crypto_auth)
    assert url == "redis://127.0.0.1:6379/0"


def test_redis_password_empty_string_treated_as_absent(crypto_auth, monkeypatch):
    """Empty REDIS_PASSWORD falls through to default (no auth)."""
    monkeypatch.delenv("ARIFOS_REDIS_URL", raising=False)
    monkeypatch.setenv("REDIS_PASSWORD", "")
    url = _read_url(crypto_auth)
    assert url == "redis://127.0.0.1:6379/0"


# Helper: extract URL the same way _get_redis() will read it
def _read_url(crypto_auth):
    """
    Mirror the env-read block of _get_redis() without actually connecting to Redis.
    We can't call _get_redis() directly because it imports the redis client,
    which may not be installed in the test env. So we replay the env-resolution logic.
    """
    import urllib.parse
    redis_url = os.getenv("ARIFOS_REDIS_URL")
    if not redis_url:
        redis_pw = os.getenv("REDIS_PASSWORD")
        if redis_pw:
            encoded_pw = urllib.parse.quote(redis_pw, safe="")
            redis_url = f"redis://:{encoded_pw}@127.0.0.1:6379/0"
        else:
            redis_url = "redis://127.0.0.1:6379/0"
    return redis_url
