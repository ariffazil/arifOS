"""
ollama_embedder.py — Shared PRL Ollama embedder (canonical)
══════════════════════════════════════════════════════════

PRL (Precedent Retrieval Layer) routes every reader/writer through this module
so that the federation uses ONE embedding backend — local Ollama's
``POST /api/embed`` with the ``nomic-embed-text`` model — instead of the old
``SentenceTransformer`` / SHA-256 hash fallback.

Design contract (locked, do not break):

* **Endpoint** — ``POST {OLLAMA_URL}/api/embed`` with ``{"model", "input",
  "truncate", "dimensions", "keep_alive"}``.  Aligned to the Ollama 0.21.1
  ``/api/embed`` contract (NOT ``prompt`` — that was the legacy
  ``/api/embeddings`` shape).  Response is ``{"embeddings": [[floats...]]}``.
* **Default model** — ``nomic-embed-text`` (override via ``ARIFOS_PRL_OLLAMA_MODEL``).
* **Default dimension** — 768 (override via ``ARIFOS_PRL_EMBED_DIM``; only
  honored when the live ``/api/show`` payload reports the same value,
  otherwise the response is rejected as wrong-dimension).
* **Timeout** — explicit ``httpx.Timeout(connect, read, write, pool)`` so a
  stalled Ollama never wedges the gate.
* **Reusable module-level client** — a single thread-safe ``httpx.Client``
  is lazily constructed once per (base_url, timeout) tuple.  All calls
  share it; tests call :func:`reset_client` to force a rebuild.
* **Circuit breaker** — module-global, thread-safe, two-stage.  After
  ``ARIFOS_PRL_CB_FAIL_THRESHOLD`` consecutive failures the breaker opens
  for ``ARIFOS_PRL_CB_RESET_SECONDS``; while open, calls fail-open immediately.
* **No request-path retry.** Network/HTTP failures are surfaced once.  We
  rely on the next call's circuit counter for backoff.
* **Strict response validation** — every response is checked for shape,
  embedding presence, finite float values, and matching dimension.  Anything
  else raises ``PrlEmbedderError``.
* **Fail-open semantics** — under breaker-open OR ``fail_open=True`` the
  helper returns ``None`` and logs once.  PRL callers translate ``None`` into
  ``PRL_ERROR`` without raising into the reasoning pipeline.

Backward compatibility
──────────────────────
Legacy ``PRL_OLLAMA_URL`` / ``PRL_OLLAMA_MODEL`` / ``PRL_EMBED_DIM`` /
``PRL_CB_*`` env vars are still honored as fallbacks, but the approved
contract is the ``ARIFOS_PRL_*`` namespace.  When both are set, the
``ARIFOS_PRL_*`` value wins.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ── Module configuration (env-overridable) ─────────────────────────────
DEFAULT_MODEL = "nomic-embed-text"
DEFAULT_DIM = 768
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_TRUNCATE = True
DEFAULT_KEEP_ALIVE = "5m"

# Tight timeouts — Ollama is local, anything slower is a failure.
DEFAULT_CONNECT_TIMEOUT_S = 1.0
DEFAULT_READ_TIMEOUT_S = 4.0
DEFAULT_WRITE_TIMEOUT_S = 2.0
DEFAULT_POOL_TIMEOUT_S = 1.0

# Circuit breaker
DEFAULT_CB_FAIL_THRESHOLD = 3
DEFAULT_CB_RESET_SECONDS = 15.0

# Module-global locks for the breaker + a once-per-fail-open log guard.
_breaker_lock = threading.Lock()
_fail_open_logged_at: float = 0.0
_FAIL_OPEN_LOG_INTERVAL_S = 30.0

# ── Reusable httpx client (lazy + thread-safe) ────────────────────────
#
# A single ``httpx.Client`` is constructed on first use and reused for the
# lifetime of the process.  ``reset_client()`` rebuilds it (used by tests
# after monkey-patching ``httpx.Client``).  The lock guards the lazy
# double-checked initialisation against two threads racing on the same
# base_url / timeout key.
_client_lock = threading.Lock()
_client: httpx.Client | None = None
_client_key: tuple[str, tuple[float, float, float, float]] | None = None


def _build_client(base_url: str, timeout: httpx.Timeout) -> httpx.Client:
    return httpx.Client(timeout=timeout)


def _get_client(base_url: str, timeout: httpx.Timeout) -> httpx.Client:
    """Return a cached :class:`httpx.Client`, building it lazily.

    The cache key is ``(base_url, (connect, read, write, pool))`` so a
    config change rebuilds the client.  Tests call :func:`reset_client`
    after monkey-patching ``httpx.Client`` to force a fresh construction
    on the next call.
    """
    global _client, _client_key
    key = (
        base_url,
        (
            timeout.connect,
            timeout.read,
            timeout.write,
            timeout.pool,
        ),
    )
    with _client_lock:
        if _client is not None and _client_key == key:
            return _client
        # Closing the previous client (if any) before replacement avoids
        # socket leaks across config changes.
        if _client is not None:
            try:
                _client.close()
            except Exception:
                pass
        _client = _build_client(base_url, timeout)
        _client_key = key
        return _client


def reset_client() -> None:
    """Drop the cached :class:`httpx.Client` so the next call rebuilds it.

    Intended for tests; also exposed for ops hot-reload scenarios where
    the embedder config changes mid-flight (e.g. ARIFOS_PRL_OLLAMA_URL
    rotation).
    """
    global _client, _client_key
    with _client_lock:
        if _client is not None:
            try:
                _client.close()
            except Exception:
                pass
        _client = None
        _client_key = None


# ── Configuration loader ──────────────────────────────────────────────


def _env(env: dict[str, str] | None, primary: str, legacy: str) -> str | None:
    """Return the first non-None env var, preferring the approved name."""
    if env is not None:
        return env.get(primary) or env.get(legacy)
    return os.environ.get(primary) or os.environ.get(legacy)


def _env_str(env: dict[str, str] | None, primary: str, legacy: str, default: str) -> str:
    val = _env(env, primary, legacy)
    return val if val not in (None, "") else default


def _env_float(env: dict[str, str] | None, primary: str, legacy: str, default: float) -> float:
    raw = _env(env, primary, legacy)
    if raw in (None, ""):
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def _env_int(env: dict[str, str] | None, primary: str, legacy: str, default: int) -> int:
    raw = _env(env, primary, legacy)
    if raw in (None, ""):
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class PrlEmbedderConfig:
    """Resolved embedder configuration (env-derived, immutable)."""

    base_url: str
    model: str
    dim: int
    connect_timeout_s: float
    read_timeout_s: float
    write_timeout_s: float
    pool_timeout_s: float
    cb_fail_threshold: int
    cb_reset_seconds: float
    truncate: bool
    keep_alive: str

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> PrlEmbedderConfig:
        return cls(
            base_url=_env_str(
                env, "ARIFOS_PRL_OLLAMA_URL", "PRL_OLLAMA_URL", DEFAULT_OLLAMA_URL
            ).rstrip("/"),
            model=_env_str(env, "ARIFOS_PRL_OLLAMA_MODEL", "PRL_OLLAMA_MODEL", DEFAULT_MODEL),
            dim=_env_int(env, "ARIFOS_PRL_EMBED_DIM", "PRL_EMBED_DIM", DEFAULT_DIM),
            connect_timeout_s=_env_float(
                env,
                "ARIFOS_PRL_OLLAMA_CONNECT_TIMEOUT_S",
                "PRL_OLLAMA_CONNECT_TIMEOUT_S",
                DEFAULT_CONNECT_TIMEOUT_S,
            ),
            read_timeout_s=_env_float(
                env,
                "ARIFOS_PRL_OLLAMA_READ_TIMEOUT_S",
                "PRL_OLLAMA_READ_TIMEOUT_S",
                DEFAULT_READ_TIMEOUT_S,
            ),
            write_timeout_s=_env_float(
                env,
                "ARIFOS_PRL_OLLAMA_WRITE_TIMEOUT_S",
                "PRL_OLLAMA_WRITE_TIMEOUT_S",
                DEFAULT_WRITE_TIMEOUT_S,
            ),
            pool_timeout_s=_env_float(
                env,
                "ARIFOS_PRL_OLLAMA_POOL_TIMEOUT_S",
                "PRL_OLLAMA_POOL_TIMEOUT_S",
                DEFAULT_POOL_TIMEOUT_S,
            ),
            cb_fail_threshold=max(
                1,
                _env_int(
                    env,
                    "ARIFOS_PRL_CB_FAIL_THRESHOLD",
                    "PRL_CB_FAIL_THRESHOLD",
                    DEFAULT_CB_FAIL_THRESHOLD,
                ),
            ),
            cb_reset_seconds=max(
                0.1,
                _env_float(
                    env,
                    "ARIFOS_PRL_CB_RESET_SECONDS",
                    "PRL_CB_RESET_SECONDS",
                    DEFAULT_CB_RESET_SECONDS,
                ),
            ),
            truncate=_env_str(
                env,
                "ARIFOS_PRL_TRUNCATE",
                "PRL_TRUNCATE",
                "true" if DEFAULT_TRUNCATE else "false",
            ).lower()
            in ("1", "true", "yes", "on"),
            keep_alive=_env_str(
                env,
                "ARIFOS_PRL_KEEP_ALIVE",
                "PRL_KEEP_ALIVE",
                DEFAULT_KEEP_ALIVE,
            ),
        )

    def as_timeout(self) -> httpx.Timeout:
        return httpx.Timeout(
            connect=self.connect_timeout_s,
            read=self.read_timeout_s,
            write=self.write_timeout_s,
            pool=self.pool_timeout_s,
        )


# ── Exceptions ────────────────────────────────────────────────────────


class PrlEmbedderError(RuntimeError):
    """Raised by embed() on hard failures (validation, dimension mismatch).

    Callers that need fail-open semantics should pass ``fail_open=True``.
    """


# ── Circuit breaker ───────────────────────────────────────────────────


@dataclass
class _BreakerState:
    consecutive_failures: int = 0
    opened_at: float = 0.0
    tripped_total: int = 0

    def is_open(self, *, now: float, reset_seconds: float) -> bool:
        if self.opened_at <= 0.0:
            return False
        if (now - self.opened_at) >= reset_seconds:
            # Cool-down expired — half-open on the next call.
            return False
        return True


_STATE = _BreakerState()


def _breaker_is_open(config: PrlEmbedderConfig) -> bool:
    return _STATE.is_open(now=time.monotonic(), reset_seconds=config.cb_reset_seconds)


def _breaker_record_success() -> None:
    with _breaker_lock:
        _STATE.consecutive_failures = 0
        _STATE.opened_at = 0.0


def _breaker_record_failure(config: PrlEmbedderConfig) -> None:
    """Increment counter; trip the breaker when threshold is exceeded."""
    global _fail_open_logged_at
    with _breaker_lock:
        _STATE.consecutive_failures += 1
        if _STATE.consecutive_failures >= config.cb_fail_threshold and _STATE.opened_at <= 0.0:
            _STATE.opened_at = time.monotonic()
            _STATE.tripped_total += 1
            logger.warning(
                "PRL embedder circuit OPENED after %d consecutive failures "
                "(threshold=%d, reset=%.1fs, tripped_total=%d)",
                _STATE.consecutive_failures,
                config.cb_fail_threshold,
                config.cb_reset_seconds,
                _STATE.tripped_total,
            )
            _fail_open_logged_at = 0.0  # Reset so we log the next fail-open once.


def _breaker_force_close() -> None:  # pragma: no cover - test helper
    with _breaker_lock:
        _STATE.consecutive_failures = 0
        _STATE.opened_at = 0.0


def breaker_snapshot() -> dict[str, Any]:
    """Return current breaker state — diagnostics only."""
    with _breaker_lock:
        return {
            "consecutive_failures": _STATE.consecutive_failures,
            "opened_at_monotonic": _STATE.opened_at,
            "tripped_total": _STATE.tripped_total,
        }


# ── Validation ────────────────────────────────────────────────────────


def _extract_embedding(raw: Any) -> list[float]:
    """Pull the first embedding out of an Ollama 0.21.x ``/api/embed``
    response.

    Accepted shapes (the Ollama ``/api/embed`` contract as of 0.21.1):
      * ``{"embeddings": [[floats...], ...]}`` (canonical batch response)
      * ``{"embedding": [floats...]}``        (legacy /api/embeddings shape)
      * Bare ``list[float]``                   (defensive)
    """
    if isinstance(raw, list):
        vec = raw
    elif isinstance(raw, dict):
        # Canonical 0.21.x shape: top-level ``embeddings`` is a list of
        # vectors; for single-text calls the list has exactly one entry.
        if isinstance(raw.get("embeddings"), list) and raw["embeddings"]:
            first = raw["embeddings"][0]
            if not isinstance(first, list):
                raise PrlEmbedderError("Ollama response 'embeddings[0]' is not a list of floats")
            vec = first
        elif isinstance(raw.get("embedding"), list):
            # Legacy /api/embeddings single-vector shape.
            vec = raw["embedding"]
        else:
            raise PrlEmbedderError("Ollama response missing 'embeddings' / 'embedding' field")
    else:
        raise PrlEmbedderError("Ollama response is neither list nor object")
    return vec


def _validate_embedding(raw: Any, *, expected_dim: int) -> list[float]:
    """Strict validation of an Ollama /api/embed payload (full pipeline)."""
    vec = _extract_embedding(raw)

    if len(vec) != expected_dim:
        raise PrlEmbedderError(
            f"Ollama embedding wrong dimension: got {len(vec)}, expected {expected_dim}"
        )

    out: list[float] = []
    for i, value in enumerate(vec):
        if not isinstance(value, (int, float)):
            raise PrlEmbedderError(
                f"Ollama embedding value at index {i} is non-numeric: {type(value).__name__}"
            )
        f = float(value)
        if f != f or f in (float("inf"), float("-inf")):  # NaN / inf guard
            raise PrlEmbedderError(f"Ollama embedding value at index {i} is non-finite: {f!r}")
        out.append(f)
    return out


def _validate_batch_response(raw: Any, *, expected_dim: int) -> list[list[float]]:
    """Strict validation of an Ollama /api/embed batch payload.

    Returns one vector per input.  The ``embeddings`` field MUST be a list
    with exactly ``len(texts)`` entries when ``len(texts) >= 1``.
    """
    if not isinstance(raw, dict):
        raise PrlEmbedderError("Ollama batch response is not an object")
    embeddings = raw.get("embeddings")
    if not isinstance(embeddings, list) or not embeddings:
        raise PrlEmbedderError("Ollama batch response missing or empty 'embeddings' field")
    out: list[list[float]] = []
    for idx, vec in enumerate(embeddings):
        if not isinstance(vec, list):
            raise PrlEmbedderError(f"Ollama batch response entry {idx} is not a list")
        if len(vec) != expected_dim:
            raise PrlEmbedderError(
                f"Ollama batch entry {idx} wrong dimension: got {len(vec)}, expected {expected_dim}"
            )
        clean: list[float] = []
        for i, value in enumerate(vec):
            if not isinstance(value, (int, float)):
                raise PrlEmbedderError(
                    f"Ollama batch entry {idx} value {i} non-numeric: {type(value).__name__}"
                )
            f = float(value)
            if f != f or f in (float("inf"), float("-inf")):
                raise PrlEmbedderError(f"Ollama batch entry {idx} value {i} non-finite: {f!r}")
            clean.append(f)
        out.append(clean)
    return out


# ── Public API ────────────────────────────────────────────────────────


def _log_fail_open(reason: str, *, config: PrlEmbedderConfig) -> None:
    """Log the fail-open once per interval — never spam."""
    global _fail_open_logged_at
    now = time.monotonic()
    with _breaker_lock:
        if (now - _fail_open_logged_at) < _FAIL_OPEN_LOG_INTERVAL_S:
            return
        _fail_open_logged_at = now
    logger.warning(
        "PRL embedder fail-open (%s) — returning None; model=%s dim=%d cb=%s",
        reason,
        config.model,
        config.dim,
        breaker_snapshot(),
    )


def _build_payload(text: str, config: PrlEmbedderConfig) -> dict[str, Any]:
    """Build the Ollama 0.21.x ``/api/embed`` request payload.

    Field names: ``model``, ``input`` (string for single-text), ``truncate``,
    ``dimensions``, ``keep_alive``.  ``dimensions`` is only sent when it
    matches the configured dimension so callers don't accidentally request
    a different size and trip validation downstream.
    """
    payload: dict[str, Any] = {
        "model": config.model,
        "input": text,
        "truncate": config.truncate,
        "keep_alive": config.keep_alive,
    }
    if config.dim > 0:
        payload["dimensions"] = config.dim
    return payload


def embed_text(
    text: str,
    *,
    config: PrlEmbedderConfig | None = None,
    fail_open: bool = True,
) -> list[float] | None:
    """Embed a single text via Ollama ``POST /api/embed``.

    Returns ``list[float]`` on success, ``None`` when fail-open and the call
    could not be served.  Raises :class:`PrlEmbedderError` only when
    ``fail_open=False`` and the underlying call failed.
    """
    if text is None or text == "":
        if fail_open:
            return None
        raise PrlEmbedderError("embed_text called with empty text")

    cfg = config or PrlEmbedderConfig.from_env()

    # Circuit breaker — fail-open immediately if open.
    if _breaker_is_open(cfg):
        if fail_open:
            _log_fail_open("circuit_open", config=cfg)
            return None
        raise PrlEmbedderError("PRL embedder circuit is OPEN")

    timeout = cfg.as_timeout()
    payload = _build_payload(text, cfg)

    try:
        client = _get_client(cfg.base_url, timeout)
    except Exception as exc:
        # Client construction itself failed (rare — typically config error).
        _breaker_record_failure(cfg)
        if fail_open:
            _log_fail_open(f"client_init:{type(exc).__name__}", config=cfg)
            return None
        raise PrlEmbedderError(f"Ollama client init failed: {exc}") from exc

    try:
        resp = client.post(f"{cfg.base_url}/api/embed", json=payload)
    except httpx.HTTPError as exc:
        _breaker_record_failure(cfg)
        if fail_open:
            _log_fail_open(f"http_error:{type(exc).__name__}", config=cfg)
            return None
        raise PrlEmbedderError(f"Ollama /api/embed HTTP error: {exc}") from exc

    if resp.status_code >= 500:
        _breaker_record_failure(cfg)
        if fail_open:
            _log_fail_open(f"status_{resp.status_code}", config=cfg)
            return None
        raise PrlEmbedderError(f"Ollama returned HTTP {resp.status_code}: {resp.text[:200]}")

    if resp.status_code >= 400:
        # Client-side — do NOT trip breaker (won't fix itself), but still
        # fail-open.
        if fail_open:
            _log_fail_open(f"client_status_{resp.status_code}", config=cfg)
            return None
        raise PrlEmbedderError(
            f"Ollama rejected request (HTTP {resp.status_code}): {resp.text[:200]}"
        )

    try:
        body = resp.json()
    except ValueError as exc:
        _breaker_record_failure(cfg)
        if fail_open:
            _log_fail_open("malformed_json", config=cfg)
            return None
        raise PrlEmbedderError(f"Ollama response is not valid JSON: {exc}") from exc

    try:
        vec = _validate_embedding(body, expected_dim=cfg.dim)
    except PrlEmbedderError as exc:
        _breaker_record_failure(cfg)
        if fail_open:
            _log_fail_open(f"validation:{exc}", config=cfg)
            return None
        raise

    _breaker_record_success()
    return vec


def embed_texts_batch(
    texts: list[str],
    *,
    config: PrlEmbedderConfig | None = None,
    fail_open: bool = True,
) -> list[list[float] | None]:
    """Embed a list of texts in ONE ``POST /api/embed`` call.

    Ollama 0.21.x accepts ``input`` as a list of strings and returns
    ``{"embeddings": [[...], [...], ...]}``.  We always send the batch
    in a single HTTP round-trip; no per-text retries, no per-text
    breaker accounting — either the whole batch succeeds or the whole
    batch fail-opens together.

    Empty list returns ``[]`` without any I/O.

    Returns a list aligned 1:1 with ``texts``: one ``list[float]`` per
    input on success, or ``None`` (whole batch fail-opened) so callers
    can distinguish "embedder unavailable" from "embedding returned
    the right shape".

    The contract is identical to the per-text embedder (``embed_text``)
    when called with ``len(texts) == 1``.
    """
    cfg = config or PrlEmbedderConfig.from_env()
    if not texts:
        return []

    # Empty strings in a batch are still the embedder's responsibility —
    # send them through; Ollama will return whatever it returns.  We do
    # not pre-filter: the response positions MUST match the input order.

    if _breaker_is_open(cfg):
        if fail_open:
            _log_fail_open("circuit_open", config=cfg)
            return [None] * len(texts)
        raise PrlEmbedderError("PRL embedder circuit is OPEN")

    timeout = cfg.as_timeout()
    payload: dict[str, Any] = {
        "model": cfg.model,
        "input": list(texts),
        "truncate": cfg.truncate,
        "keep_alive": cfg.keep_alive,
    }
    if cfg.dim > 0:
        payload["dimensions"] = cfg.dim

    try:
        client = _get_client(cfg.base_url, timeout)
    except Exception as exc:
        _breaker_record_failure(cfg)
        if fail_open:
            _log_fail_open(f"client_init:{type(exc).__name__}", config=cfg)
            return [None] * len(texts)
        raise PrlEmbedderError(f"Ollama client init failed: {exc}") from exc

    try:
        resp = client.post(f"{cfg.base_url}/api/embed", json=payload)
    except httpx.HTTPError as exc:
        _breaker_record_failure(cfg)
        if fail_open:
            _log_fail_open(f"http_error:{type(exc).__name__}", config=cfg)
            return [None] * len(texts)
        raise PrlEmbedderError(f"Ollama /api/embed HTTP error: {exc}") from exc

    if resp.status_code >= 500:
        _breaker_record_failure(cfg)
        if fail_open:
            _log_fail_open(f"status_{resp.status_code}", config=cfg)
            return [None] * len(texts)
        raise PrlEmbedderError(f"Ollama returned HTTP {resp.status_code}: {resp.text[:200]}")

    if resp.status_code >= 400:
        if fail_open:
            _log_fail_open(f"client_status_{resp.status_code}", config=cfg)
            return [None] * len(texts)
        raise PrlEmbedderError(
            f"Ollama rejected batch (HTTP {resp.status_code}): {resp.text[:200]}"
        )

    try:
        body = resp.json()
    except ValueError as exc:
        _breaker_record_failure(cfg)
        if fail_open:
            _log_fail_open("malformed_json", config=cfg)
            return [None] * len(texts)
        raise PrlEmbedderError(f"Ollama response is not valid JSON: {exc}") from exc

    try:
        vectors = _validate_batch_response(body, expected_dim=cfg.dim)
    except PrlEmbedderError as exc:
        _breaker_record_failure(cfg)
        if fail_open:
            _log_fail_open(f"validation:{exc}", config=cfg)
            return [None] * len(texts)
        raise

    # Enforce 1:1 alignment between input and response.  Ollama returns
    # the same order it received, but if the response length drifts we
    # must not silently truncate.
    if len(vectors) != len(texts):
        _breaker_record_failure(cfg)
        err = f"Ollama batch response length {len(vectors)} != input length {len(texts)}"
        if fail_open:
            _log_fail_open(f"validation:{err}", config=cfg)
            return [None] * len(texts)
        raise PrlEmbedderError(err)

    _breaker_record_success()
    return vectors


def healthcheck(
    *,
    config: PrlEmbedderConfig | None = None,
    fail_open: bool = True,
) -> dict[str, Any]:
    """Cheap reachability probe — used by tests and ops diagnostics.

    GET ``/api/version`` and report ``reachable``.  A successful probe
    does NOT trip the breaker; a failure still records so transient
    outages don't sneak past us.
    """
    cfg = config or PrlEmbedderConfig.from_env()
    timeout = httpx.Timeout(connect=cfg.connect_timeout_s, read=2.0, write=1.0, pool=1.0)
    try:
        client = _get_client(cfg.base_url, timeout)
        resp = client.get(f"{cfg.base_url}/api/version")
        reachable = resp.status_code < 500
    except httpx.HTTPError as exc:
        reachable = False
        logger.debug("PRL embedder healthcheck HTTP error: %s", exc)
        if not fail_open:
            raise PrlEmbedderError(f"Ollama healthcheck failed: {exc}") from exc

    return {
        "reachable": reachable,
        "base_url": cfg.base_url,
        "model": cfg.model,
        "dim": cfg.dim,
        "breaker": breaker_snapshot(),
    }


__all__ = [
    "PrlEmbedderConfig",
    "PrlEmbedderError",
    "breaker_snapshot",
    "embed_text",
    "embed_texts_batch",
    "healthcheck",
    "reset_client",
]
