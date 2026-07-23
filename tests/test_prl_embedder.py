"""
tests/test_prl_embedder.py — Canonical PRL Ollama embedder contract
════════════════════════════════════════════════════════════════════

Tests the embedder's contract guarantees against the Ollama 0.21.x
``/api/embed`` shape (``{model, input} → {embeddings: [[...]]}``):

  1. Success path returns a 768-dim finite float vector with the exact
     outgoing request payload (``model``, ``input``, ``truncate``,
     ``dimensions``, ``keep_alive``).
  2. Batch mapping is 1:1 with input order; response length MUST equal
     request length.
  3. Timeout / connection failures surface once — no request-path retry.
  4. Malformed responses (bad JSON, missing field) raise / fail-open.
  5. Wrong-dimension responses are rejected.
  6. The circuit breaker opens after consecutive failures and fail-opens.
  7. The reusable module-level ``httpx.Client`` is cached; ``reset_client``
     forces a rebuild.
  8. Approved ``ARIFOS_PRL_*`` env names win; legacy ``PRL_*`` aliases
     remain readable for backward compatibility.

A live Ollama is NOT required — every test monkey-patches ``httpx.Client``
or the module-level state so the suite is hermetic.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from arifosmcp.prl import ollama_embedder as oe


# ── Fixtures ───────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_breaker_and_client():
    """Reset the module-global breaker + reusable client between tests."""
    oe._breaker_force_close()
    oe._fail_open_logged_at = 0.0
    oe.reset_client()
    yield
    oe._breaker_force_close()
    oe._fail_open_logged_at = 0.0
    oe.reset_client()


def _ok_response(payload: dict[str, Any]) -> MagicMock:
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = payload
    resp.text = json.dumps(payload)
    return resp


def _http_error_response(status: int, body: str = "") -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.text = body
    return resp


def _down_client() -> MagicMock:
    """Client whose ``post`` and ``get`` raise a ConnectError every call."""
    client = MagicMock()
    client.__enter__.return_value = client
    client.__exit__.return_value = False
    err = httpx.ConnectError("connection refused", request=MagicMock())
    client.post.side_effect = err
    client.get.side_effect = err
    client.close.return_value = None
    return client


# ── 1. Success path + exact payload shape ────────────────────────────


class TestEmbedderSuccess:
    def test_success_returns_768_dim_finite_vector(self):
        cfg = oe.PrlEmbedderConfig.from_env(
            {
                "ARIFOS_PRL_OLLAMA_URL": "http://ollama.test",
                "ARIFOS_PRL_EMBED_DIM": "768",
            }
        )
        vec = [0.1] * 768
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = _ok_response({"embeddings": [vec]})

        with patch.object(oe, "_get_client", return_value=client):
            result = oe.embed_text("hello", config=cfg, fail_open=True)

        assert isinstance(result, list)
        assert len(result) == 768
        assert all(isinstance(v, float) for v in result)
        assert oe.breaker_snapshot()["consecutive_failures"] == 0

    def test_outgoing_payload_matches_ollama_021_contract(self):
        cfg = oe.PrlEmbedderConfig.from_env(
            {
                "ARIFOS_PRL_OLLAMA_URL": "http://ollama.test",
                "ARIFOS_PRL_OLLAMA_MODEL": "nomic-embed-text",
                "ARIFOS_PRL_EMBED_DIM": "768",
                "ARIFOS_PRL_TRUNCATE": "true",
                "ARIFOS_PRL_KEEP_ALIVE": "30s",
            }
        )
        vec = [0.5] * 768
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = _ok_response({"embeddings": [vec]})

        with patch.object(oe, "_get_client", return_value=client):
            oe.embed_text("hello world", config=cfg, fail_open=True)

        # Inspect the actual outgoing request payload.
        args, kwargs = client.post.call_args
        url_arg = args[0] if args else kwargs["url"]
        json_payload = kwargs["json"]
        assert url_arg == "http://ollama.test/api/embed"
        assert json_payload == {
            "model": "nomic-embed-text",
            "input": "hello world",
            "truncate": True,
            "keep_alive": "30s",
            "dimensions": 768,
        }

    def test_success_via_legacy_embedding_field(self):
        """Legacy /api/embeddings ``embedding`` shape is still accepted."""
        cfg = oe.PrlEmbedderConfig.from_env({"ARIFOS_PRL_OLLAMA_URL": "http://x"})
        vec = [0.5] * 768
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = _ok_response({"embedding": vec})

        with patch.object(oe, "_get_client", return_value=client):
            result = oe.embed_text("hi", config=cfg, fail_open=False)

        assert result == vec


# ── 2. Batch mapping (1:1 alignment + count) ─────────────────────────


class TestEmbedderBatch:
    def test_batch_returns_one_vector_per_input_in_order(self):
        cfg = oe.PrlEmbedderConfig.from_env({"ARIFOS_PRL_OLLAMA_URL": "http://x"})
        v1 = [0.1] * 768
        v2 = [0.2] * 768
        v3 = [0.3] * 768
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = _ok_response(
            {"embeddings": [v1, v2, v3]}
        )

        with patch.object(oe, "_get_client", return_value=client):
            result = oe.embed_texts_batch(
                ["a", "b", "c"], config=cfg, fail_open=False
            )

        assert len(result) == 3
        assert result[0] == v1
        assert result[1] == v2
        assert result[2] == v3

    def test_batch_outgoing_payload_uses_input_list(self):
        cfg = oe.PrlEmbedderConfig.from_env({"ARIFOS_PRL_OLLAMA_URL": "http://x"})
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = _ok_response(
            {"embeddings": [[0.1] * 768, [0.2] * 768]}
        )

        with patch.object(oe, "_get_client", return_value=client):
            oe.embed_texts_batch(["foo", "bar"], config=cfg, fail_open=False)

        args, kwargs = client.post.call_args
        assert kwargs["json"]["input"] == ["foo", "bar"]
        assert kwargs["json"]["model"] == "nomic-embed-text"
        assert kwargs["json"]["dimensions"] == 768
        assert "prompt" not in kwargs["json"]
        assert "truncate" in kwargs["json"]
        assert "keep_alive" in kwargs["json"]

    def test_batch_empty_input_does_not_call_network(self):
        cfg = oe.PrlEmbedderConfig.from_env({"ARIFOS_PRL_OLLAMA_URL": "http://x"})
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        with patch.object(oe, "_get_client", return_value=client):
            result = oe.embed_texts_batch([], config=cfg, fail_open=False)
        assert result == []
        assert client.post.call_count == 0

    def test_batch_response_length_mismatch_fail_opens(self):
        """If Ollama returns fewer vectors than inputs, fail-open the whole batch."""
        cfg = oe.PrlEmbedderConfig.from_env({"ARIFOS_PRL_OLLAMA_URL": "http://x"})
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        # 3 inputs but only 2 embeddings returned.
        client.post.return_value = _ok_response(
            {"embeddings": [[0.1] * 768, [0.2] * 768]}
        )

        with patch.object(oe, "_get_client", return_value=client):
            result = oe.embed_texts_batch(
                ["a", "b", "c"], config=cfg, fail_open=True
            )

        assert result == [None, None, None]
        assert oe.breaker_snapshot()["consecutive_failures"] == 1

    def test_batch_wrong_dim_rejected(self):
        cfg = oe.PrlEmbedderConfig.from_env(
            {"ARIFOS_PRL_OLLAMA_URL": "http://x", "ARIFOS_PRL_EMBED_DIM": "768"}
        )
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = _ok_response(
            {"embeddings": [[0.1] * 768, [0.2] * 1024]}
        )

        with patch.object(oe, "_get_client", return_value=client):
            with pytest.raises(oe.PrlEmbedderError, match="wrong dimension"):
                oe.embed_texts_batch(["a", "b"], config=cfg, fail_open=False)

    def test_batch_fail_open_returns_full_none_list(self):
        cfg = oe.PrlEmbedderConfig.from_env({"ARIFOS_PRL_OLLAMA_URL": "http://x"})
        client = _down_client()
        with patch.object(oe, "_get_client", return_value=client):
            result = oe.embed_texts_batch(
                ["a", "b", "c"], config=cfg, fail_open=True
            )

        assert result == [None, None, None]
        assert oe.breaker_snapshot()["consecutive_failures"] == 1


# ── 3. Timeout / connection failure + no request-path retry ───────────


class TestEmbedderTimeout:
    def test_timeout_fails_open_and_does_not_retry(self):
        cfg = oe.PrlEmbedderConfig.from_env({"ARIFOS_PRL_OLLAMA_URL": "http://down.test"})
        client = _down_client()

        with patch.object(oe, "_get_client", return_value=client):
            result = oe.embed_text("hello", config=cfg, fail_open=True)

        # No retry — single post call surfaces the error.
        assert client.post.call_count == 1
        assert result is None
        assert oe.breaker_snapshot()["consecutive_failures"] == 1

    def test_timeout_with_fail_open_false_raises(self):
        cfg = oe.PrlEmbedderConfig.from_env({"ARIFOS_PRL_OLLAMA_URL": "http://down.test"})
        client = _down_client()

        with patch.object(oe, "_get_client", return_value=client):
            with pytest.raises(oe.PrlEmbedderError):
                oe.embed_text("hello", config=cfg, fail_open=False)

        assert client.post.call_count == 1


# ── 4. Malformed responses ─────────────────────────────────────────────


class TestEmbedderMalformed:
    def test_malformed_json_fails_open(self):
        cfg = oe.PrlEmbedderConfig.from_env({"ARIFOS_PRL_OLLAMA_URL": "http://x"})
        resp = MagicMock()
        resp.status_code = 200
        resp.json.side_effect = ValueError("not json")
        resp.text = "<<not json>>"

        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = resp

        with patch.object(oe, "_get_client", return_value=client):
            assert oe.embed_text("hi", config=cfg, fail_open=True) is None

    def test_missing_embedding_field_fails_open(self):
        cfg = oe.PrlEmbedderConfig.from_env({"ARIFOS_PRL_OLLAMA_URL": "http://x"})
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = _ok_response({"unrelated": "data"})

        with patch.object(oe, "_get_client", return_value=client):
            assert oe.embed_text("hi", config=cfg, fail_open=True) is None

    def test_non_numeric_value_fails_open(self):
        cfg = oe.PrlEmbedderConfig.from_env({"ARIFOS_PRL_OLLAMA_URL": "http://x"})
        bad = [0.0] * 767 + ["oops"]
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = _ok_response({"embeddings": [bad]})

        with patch.object(oe, "_get_client", return_value=client):
            assert oe.embed_text("hi", config=cfg, fail_open=True) is None

    def test_nan_value_fails_open(self):
        cfg = oe.PrlEmbedderConfig.from_env({"ARIFOS_PRL_OLLAMA_URL": "http://x"})
        bad = [0.0] * 767 + [float("nan")]
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = _ok_response({"embeddings": [bad]})

        with patch.object(oe, "_get_client", return_value=client):
            assert oe.embed_text("hi", config=cfg, fail_open=True) is None


# ── 5. Wrong dimension ────────────────────────────────────────────────


class TestEmbedderWrongDim:
    def test_wrong_dim_fails_open(self):
        cfg = oe.PrlEmbedderConfig.from_env(
            {"ARIFOS_PRL_OLLAMA_URL": "http://x", "ARIFOS_PRL_EMBED_DIM": "768"}
        )
        # Return 1024 instead of 768.
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = _ok_response(
            {"embeddings": [[0.1] * 1024]}
        )

        with patch.object(oe, "_get_client", return_value=client):
            assert oe.embed_text("hi", config=cfg, fail_open=True) is None

        # Wrong-dim responses MUST count toward the breaker.
        assert oe.breaker_snapshot()["consecutive_failures"] == 1

    def test_wrong_dim_with_fail_open_false_raises(self):
        cfg = oe.PrlEmbedderConfig.from_env(
            {"ARIFOS_PRL_OLLAMA_URL": "http://x", "ARIFOS_PRL_EMBED_DIM": "768"}
        )
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = _ok_response(
            {"embeddings": [[0.1] * 256]}
        )

        with patch.object(oe, "_get_client", return_value=client):
            with pytest.raises(oe.PrlEmbedderError, match="wrong dimension"):
                oe.embed_text("hi", config=cfg, fail_open=False)


# ── 6. Circuit breaker ────────────────────────────────────────────────


class TestCircuitBreaker:
    def test_breaker_opens_after_threshold_failures(self):
        cfg = oe.PrlEmbedderConfig.from_env(
            {
                "ARIFOS_PRL_OLLAMA_URL": "http://x",
                "ARIFOS_PRL_CB_FAIL_THRESHOLD": "3",
            }
        )
        client = _down_client()
        with patch.object(oe, "_get_client", return_value=client):
            for _ in range(3):
                oe.embed_text("hi", config=cfg, fail_open=True)

        snap = oe.breaker_snapshot()
        assert snap["consecutive_failures"] >= 3
        assert snap["opened_at_monotonic"] > 0.0

    def test_breaker_open_short_circuits_subsequent_calls(self):
        cfg = oe.PrlEmbedderConfig.from_env(
            {
                "ARIFOS_PRL_OLLAMA_URL": "http://x",
                "ARIFOS_PRL_CB_FAIL_THRESHOLD": "2",
                "ARIFOS_PRL_CB_RESET_SECONDS": "60",
            }
        )
        client = _down_client()
        with patch.object(oe, "_get_client", return_value=client):
            # Trip the breaker.
            for _ in range(2):
                oe.embed_text("hi", config=cfg, fail_open=True)
            call_count_after_trip = client.post.call_count

            # Subsequent calls must short-circuit and NOT touch httpx.
            for _ in range(5):
                assert oe.embed_text("hi", config=cfg, fail_open=True) is None

        assert client.post.call_count == call_count_after_trip

    def test_breaker_open_with_fail_open_false_raises(self):
        cfg = oe.PrlEmbedderConfig.from_env(
            {
                "ARIFOS_PRL_OLLAMA_URL": "http://x",
                "ARIFOS_PRL_CB_FAIL_THRESHOLD": "1",
                "ARIFOS_PRL_CB_RESET_SECONDS": "60",
            }
        )
        client = _down_client()
        with patch.object(oe, "_get_client", return_value=client):
            oe.embed_text("hi", config=cfg, fail_open=True)  # trip
            with pytest.raises(oe.PrlEmbedderError, match="circuit"):
                oe.embed_text("hi", config=cfg, fail_open=False)

    def test_breaker_resets_after_success(self):
        cfg = oe.PrlEmbedderConfig.from_env(
            {"ARIFOS_PRL_OLLAMA_URL": "http://x", "ARIFOS_PRL_CB_FAIL_THRESHOLD": "5"}
        )
        client = _down_client()
        with patch.object(oe, "_get_client", return_value=client):
            oe.embed_text("hi", config=cfg, fail_open=True)
            oe.embed_text("hi", config=cfg, fail_open=True)
            assert oe.breaker_snapshot()["consecutive_failures"] == 2

        # Now a success — counter resets, breaker stays closed.
        ok_client = MagicMock()
        ok_client.__enter__.return_value = ok_client
        ok_client.__exit__.return_value = False
        ok_client.post.return_value = _ok_response({"embeddings": [[0.1] * 768]})

        with patch.object(oe, "_get_client", return_value=ok_client):
            oe.embed_text("hi", config=cfg, fail_open=True)

        assert oe.breaker_snapshot()["consecutive_failures"] == 0


# ── 7. Fail-open behaviour ─────────────────────────────────────────────


class TestFailOpen:
    def test_empty_text_fails_open(self):
        cfg = oe.PrlEmbedderConfig.from_env({"ARIFOS_PRL_OLLAMA_URL": "http://x"})
        # Should never reach the network.
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        with patch.object(oe, "_get_client", return_value=client):
            assert oe.embed_text("", config=cfg, fail_open=True) is None
            assert client.post.call_count == 0

    def test_4xx_does_not_trip_breaker(self):
        """Client-side errors are operator-fixable; do NOT trip the breaker."""
        cfg = oe.PrlEmbedderConfig.from_env(
            {"ARIFOS_PRL_OLLAMA_URL": "http://x", "ARIFOS_PRL_CB_FAIL_THRESHOLD": "2"}
        )
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = _http_error_response(400, "bad model")

        with patch.object(oe, "_get_client", return_value=client):
            for _ in range(5):
                assert oe.embed_text("hi", config=cfg, fail_open=True) is None

        assert oe.breaker_snapshot()["consecutive_failures"] == 0

    def test_5xx_trips_breaker(self):
        cfg = oe.PrlEmbedderConfig.from_env(
            {"ARIFOS_PRL_OLLAMA_URL": "http://x", "ARIFOS_PRL_CB_FAIL_THRESHOLD": "2"}
        )
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = _http_error_response(503, "overloaded")

        with patch.object(oe, "_get_client", return_value=client):
            for _ in range(2):
                assert oe.embed_text("hi", config=cfg, fail_open=True) is None

        assert oe.breaker_snapshot()["consecutive_failures"] == 2

    def test_healthcheck_reports_unreachable(self):
        cfg = oe.PrlEmbedderConfig.from_env({"ARIFOS_PRL_OLLAMA_URL": "http://x"})
        client = _down_client()
        with patch.object(oe, "_get_client", return_value=client):
            hc = oe.healthcheck(config=cfg)
        assert hc["reachable"] is False
        assert hc["breaker"] == oe.breaker_snapshot()


# ── 8. Reusable httpx.Client ──────────────────────────────────────────


class TestReusableClient:
    def test_client_is_cached_across_calls(self):
        cfg = oe.PrlEmbedderConfig.from_env(
            {"ARIFOS_PRL_OLLAMA_URL": "http://reuse.test", "ARIFOS_PRL_EMBED_DIM": "768"}
        )
        vec = [0.1] * 768
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.post.return_value = _ok_response({"embeddings": [vec]})

        with patch.object(oe, "_build_client", return_value=client) as build:
            oe.embed_text("a", config=cfg, fail_open=False)
            oe.embed_text("b", config=cfg, fail_open=False)
            oe.embed_text("c", config=cfg, fail_open=False)

        # Only one Client was constructed across all three calls.
        assert build.call_count == 1
        # The same client instance received all three posts.
        assert client.post.call_count == 3

    def test_reset_client_forces_rebuild(self):
        cfg = oe.PrlEmbedderConfig.from_env(
            {"ARIFOS_PRL_OLLAMA_URL": "http://reuse.test", "ARIFOS_PRL_EMBED_DIM": "768"}
        )
        vec = [0.1] * 768
        client_a = MagicMock()
        client_a.__enter__.return_value = client_a
        client_a.__exit__.return_value = False
        client_a.post.return_value = _ok_response({"embeddings": [vec]})

        client_b = MagicMock()
        client_b.__enter__.return_value = client_b
        client_b.__exit__.return_value = False
        client_b.post.return_value = _ok_response({"embeddings": [vec]})

        with patch.object(oe, "_build_client", side_effect=[client_a, client_b]) as build:
            oe.embed_text("a", config=cfg, fail_open=False)
            oe.reset_client()
            oe.embed_text("b", config=cfg, fail_open=False)

        # Two builds: initial + after reset_client.
        assert build.call_count == 2
        assert client_a.close.called
        assert client_b.close.called is False or client_b.close.call_count <= 1

    def test_changing_base_url_rebuilds_client(self):
        """A different ``base_url`` invalidates the cache."""
        cfg_a = oe.PrlEmbedderConfig.from_env(
            {"ARIFOS_PRL_OLLAMA_URL": "http://a.test", "ARIFOS_PRL_EMBED_DIM": "768"}
        )
        cfg_b = oe.PrlEmbedderConfig.from_env(
            {"ARIFOS_PRL_OLLAMA_URL": "http://b.test", "ARIFOS_PRL_EMBED_DIM": "768"}
        )
        vec = [0.1] * 768
        client_a = MagicMock()
        client_a.__enter__.return_value = client_a
        client_a.__exit__.return_value = False
        client_a.post.return_value = _ok_response({"embeddings": [vec]})
        client_b = MagicMock()
        client_b.__enter__.return_value = client_b
        client_b.__exit__.return_value = False
        client_b.post.return_value = _ok_response({"embeddings": [vec]})

        with patch.object(
            oe, "_build_client", side_effect=[client_a, client_b]
        ) as build:
            oe.embed_text("a", config=cfg_a, fail_open=False)
            oe.embed_text("b", config=cfg_b, fail_open=False)

        assert build.call_count == 2


# ── 9. Approved ARIFOS_PRL_* env names win over legacy PRL_* ─────────


class TestEnvContract:
    def test_approved_env_names_take_precedence(self):
        cfg = oe.PrlEmbedderConfig.from_env(
            {
                "ARIFOS_PRL_OLLAMA_URL": "http://approved.test",
                "ARIFOS_PRL_OLLAMA_MODEL": "approved-model",
                "ARIFOS_PRL_EMBED_DIM": "1024",
                "PRL_OLLAMA_URL": "http://legacy.test",
                "PRL_OLLAMA_MODEL": "legacy-model",
                "PRL_EMBED_DIM": "512",
            }
        )
        assert cfg.base_url == "http://approved.test"
        assert cfg.model == "approved-model"
        assert cfg.dim == 1024

    def test_legacy_env_names_still_supported(self):
        cfg = oe.PrlEmbedderConfig.from_env(
            {
                "PRL_OLLAMA_URL": "http://legacy.test",
                "PRL_OLLAMA_MODEL": "legacy-model",
                "PRL_EMBED_DIM": "512",
                "PRL_TRUNCATE": "false",
                "PRL_KEEP_ALIVE": "10s",
            }
        )
        assert cfg.base_url == "http://legacy.test"
        assert cfg.model == "legacy-model"
        assert cfg.dim == 512
        assert cfg.truncate is False
        assert cfg.keep_alive == "10s"

    def test_default_truncate_is_true(self):
        cfg = oe.PrlEmbedderConfig.from_env()
        assert cfg.truncate is True
        assert cfg.keep_alive == "5m"
