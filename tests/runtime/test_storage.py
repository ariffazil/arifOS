from unittest.mock import patch

from arifosmcp.runtime.storage import get_storage


def test_get_storage_defaults_to_memory_when_redis_not_configured(monkeypatch):
    monkeypatch.delenv("ARIFOS_STORAGE_BACKEND", raising=False)
    monkeypatch.delenv("REDIS_HOST", raising=False)
    monkeypatch.delenv("ARIFOS_MINIMAL_STDIO", raising=False)

    assert get_storage() is None


def test_get_storage_prefers_explicit_backend(monkeypatch):
    monkeypatch.setenv("ARIFOS_STORAGE_BACKEND", "redis")
    monkeypatch.delenv("REDIS_HOST", raising=False)
    monkeypatch.delenv("ARIFOS_MINIMAL_STDIO", raising=False)

    with patch("arifosmcp.runtime.storage.build_encrypted_redis_store", return_value="redis-store") as mock_build:
        assert get_storage() == "redis-store"

    mock_build.assert_called_once_with()


def test_get_storage_uses_redis_when_host_is_configured(monkeypatch):
    monkeypatch.delenv("ARIFOS_STORAGE_BACKEND", raising=False)
    monkeypatch.setenv("REDIS_HOST", "127.0.0.1")
    monkeypatch.delenv("ARIFOS_MINIMAL_STDIO", raising=False)

    with patch("arifosmcp.runtime.storage.build_encrypted_redis_store", return_value="redis-store") as mock_build:
        assert get_storage() == "redis-store"

    mock_build.assert_called_once_with()


def test_get_storage_prefers_memory_for_minimal_stdio(monkeypatch):
    monkeypatch.delenv("ARIFOS_STORAGE_BACKEND", raising=False)
    monkeypatch.setenv("REDIS_HOST", "127.0.0.1")
    monkeypatch.setenv("ARIFOS_MINIMAL_STDIO", "1")

    with patch("arifosmcp.runtime.storage.build_encrypted_redis_store") as mock_build:
        assert get_storage() is None

    mock_build.assert_not_called()
