"""
tests/runtime/test_sessions.py — Session Management Tests

Tests for runtime/sessions.py — identity binding and session continuity
"""

import pytest


class TestSessionNormalization:
    """Test _normalize_session_id function."""

    def test_normalize_with_valid_session(self):
        """Test normalizing a valid session ID."""
        from arifosmcp.runtime.session import _normalize_session_id

        result = _normalize_session_id("test-session-123")
        assert result == "test-session-123"

    def test_normalize_with_none_creates_new(self):
        """Test that None creates a new session ID."""
        from arifosmcp.runtime.session import _normalize_session_id

        result = _normalize_session_id(None)
        assert result.startswith("session-")
        assert len(result) == 16  # "session-" + 8 hex chars

    def test_normalize_with_empty_string_creates_new(self):
        """Test that empty string creates a new session ID."""
        from arifosmcp.runtime.session import _normalize_session_id

        result = _normalize_session_id("")
        assert result.startswith("session-")


class TestSessionIdentityBinding:
    """Test session identity binding functions."""

    def test_bind_and_get_identity(self):
        """Test binding and retrieving session identity."""
        from arifosmcp.runtime.session import (
            bind_session_identity,
            get_session_identity,
        )

        # Bind identity with explicit verified actor_id
        bind_session_identity(
            session_id="test-bind-001",
            actor_id="ariffazil",
            authority_level="sovereign",
            auth_context={"verified": True},
            human_approval=True,
        )

        # Retrieve identity
        identity = get_session_identity("test-bind-001")
        assert identity is not None
        assert identity["actor_id"] == "ariffazil"  # Explicit verified identity
        assert identity["authority_level"] == "sovereign"
        assert identity["human_approval"] is True

    def test_get_identity_nonexistent(self):
        """Test getting identity for non-existent session."""
        from arifosmcp.runtime.session import get_session_identity

        identity = get_session_identity("nonexistent-session-xyz")
        assert identity is None

    def test_clear_session_identity(self):
        """Test clearing session identity."""
        from arifosmcp.runtime.session import (
            bind_session_identity,
            get_session_identity,
            clear_session_identity,
        )

        # Bind and verify
        bind_session_identity(
            session_id="test-clear-001",
            actor_id="test-user",
            authority_level="user",
            auth_context={},
        )
        assert get_session_identity("test-clear-001") is not None

        # Clear and verify
        clear_session_identity("test-clear-001")
        assert get_session_identity("test-clear-001") is None


class TestActiveSession:
    """Test active session management."""

    def test_set_and_resolve_active_session(self):
        """Test setting and resolving active session."""
        from arifosmcp.runtime.session import set_active_session, _resolve_session_id

        # Set active session
        set_active_session("active-session-001")

        # Resolve with None should return active session
        result = _resolve_session_id(None)
        assert result == "active-session-001"

    def test_resolve_session_with_provided_id(self):
        """Test resolving with provided ID takes precedence."""
        from arifosmcp.runtime.session import set_active_session, _resolve_session_id

        set_active_session("active-session")
        result = _resolve_session_id("provided-session")

        # Provided ID takes precedence
        assert result == "provided-session"


class TestRuntimeContext:
    """Test runtime context resolution."""

    def test_resolve_runtime_context_anonymous(self):
        """Test context resolution for anonymous user."""
        from arifosmcp.runtime.session import resolve_runtime_context

        context = resolve_runtime_context(
            incoming_session_id=None,
            auth_context=None,
            actor_id=None,
            declared_name=None,
        )

        assert context["canonical_actor_id"] == "anonymous"
        assert context["transport_session_id"] == "global"

    def test_resolve_runtime_context_with_actor(self):
        """Test context resolution with verified actor ID."""
        from arifosmcp.runtime.session import resolve_runtime_context

        context = resolve_runtime_context(
            incoming_session_id="session-123",
            auth_context=None,
            actor_id="ariffazil",
            declared_name="Arif Fazil",
        )

        # Explicit verified identity preserved
        assert context["canonical_actor_id"] == "ariffazil"
        assert context["display_name"] == "Arif Fazil"

    def test_resolve_runtime_context_invalid_actor(self):
        """Test context resolution with invalid/malformed actor_id is rejected."""
        from arifosmcp.runtime.session import resolve_runtime_context

        # Malformed actor_id (contains special chars) should be rejected
        context = resolve_runtime_context(
            incoming_session_id="session-123",
            auth_context=None,
            actor_id="arif<script>alert(1)</script>",
            declared_name=None,
        )

        # Invalid actor should fall back to anonymous
        assert context["canonical_actor_id"] == "anonymous"


class TestSessionCounting:
    """Test session counting functionality."""

    def test_list_active_sessions_count(self):
        """Test counting active sessions."""
        from arifosmcp.runtime.session import (
            bind_session_identity,
            list_active_sessions_count,
            clear_session_identity,
        )

        # Get initial count
        initial_count = list_active_sessions_count()

        # Bind a new session
        bind_session_identity(
            session_id="count-test-001",
            actor_id="test",
            authority_level="user",
            auth_context={},
        )

        # Count should increase
        new_count = list_active_sessions_count()
        assert new_count == initial_count + 1

        # Cleanup
        clear_session_identity("count-test-001")


class TestIdentityMismatchCases:
    """Zero-Day hardening mismatch test cases per external validator amendments."""

    def test_resolve_canonical_actor_guessable_alias_rejected(self):
        """Test that guessable alias 'arif' is NOT promoted to ariffazil."""
        from arifosmcp.runtime.session import _resolve_canonical_actor

        # "arif" is NOT in the sovereign identity map and should not be promoted
        result = _resolve_canonical_actor("arif", None)
        assert result == "arif"  # Preserved as-is, not promoted

    def test_resolve_canonical_actor_explicit_verified(self):
        """Test that explicit verified ariffazil is recognized."""
        from arifosmcp.runtime.session import _resolve_canonical_actor

        result = _resolve_canonical_actor("ariffazil", None)
        assert result == "ariffazil"

    def test_resolve_canonical_actor_malformed_rejected(self):
        """Test that malformed actor_id is rejected."""
        from arifosmcp.runtime.session import _resolve_canonical_actor

        # Script injection attempt should be rejected
        result = _resolve_canonical_actor("<script>alert(1)</script>", None)
        assert result == "anonymous"

        # Path traversal attempt should be rejected
        result = _resolve_canonical_actor("../../../etc/passwd", None)
        assert result == "anonymous"

    def test_resolve_runtime_context_token_overrides_transport(self):
        """Test that verified token identity outranks transport-provided actor."""
        from arifosmcp.runtime.session import resolve_runtime_context

        # auth_context has verified session, transport has different actor
        context = resolve_runtime_context(
            incoming_session_id="transport-session",
            auth_context={"session_id": "verified-token-session"},
            actor_id="untrusted-actor",
            declared_name=None,
        )

        # Token should win
        assert context["session_id"] == "verified-token-session"
        assert context["authority_source"] == "token"

    def test_resolve_runtime_context_stale_session_with_valid_token(self):
        """Test stale session_id + valid token uses token."""
        from arifosmcp.runtime.session import resolve_runtime_context

        context = resolve_runtime_context(
            incoming_session_id="stale-session-xyz",
            auth_context={"session_id": "fresh-valid-token"},
            actor_id="some-actor",
            declared_name=None,
        )

        # Token identity should win over stale transport session
        assert context["session_id"] == "fresh-valid-token"
        assert context["authority_source"] == "token"

    def test_resolve_runtime_context_anonymous_transport_no_session(self):
        """Test anonymous transport without session gets anonymous identity."""
        from arifosmcp.runtime.session import resolve_runtime_context

        context = resolve_runtime_context(
            incoming_session_id=None,
            auth_context=None,
            actor_id=None,
            declared_name=None,
        )

        assert context["canonical_actor_id"] == "anonymous"
        assert context["transport_session_id"] == "global"
        assert context["authority_source"] == "fallback"


# ═══════════════════════════════════════════════════════════════════════════════
# Regression: _FileSessionStore.get() must accept default kwarg.
# Bug: TypeError → SAFE_VOID_FALLBACK in arif_triage.
# Commit that fixed: 665db9a85
# ═══════════════════════════════════════════════════════════════════════════════


class TestFileSessionStoreGetDefault:
    """Regression: .get(key, default) must match dict.get() signature."""

    def test_get_with_default_kwarg_returns_default_for_missing_key(self):
        """Missing key + default={} → return {} (not None, not TypeError)."""
        import tempfile
        from arifosmcp.runtime.tools import _FileSessionStore

        with tempfile.TemporaryDirectory() as tmp:
            store = _FileSessionStore(path=f"{tmp}/sessions.json")
            result = store.get("nonexistent-session-id", {})
            assert result == {}, f"expected empty dict, got {result!r}"

    def test_get_with_default_positional_works(self):
        """3-arg call .get(key, default) used by callers in kernel.py:173 etc."""
        import tempfile
        from arifosmcp.runtime.tools import _FileSessionStore

        with tempfile.TemporaryDirectory() as tmp:
            store = _FileSessionStore(path=f"{tmp}/sessions.json")
            # Simulate the buggy caller pattern: store.get(session_id, default_value)
            result = store.get("missing", {"fallback": True})
            assert result == {"fallback": True}

    def test_get_with_no_default_returns_none(self):
        """Single-arg .get(key) still returns None for missing key."""
        import tempfile
        from arifosmcp.runtime.tools import _FileSessionStore

        with tempfile.TemporaryDirectory() as tmp:
            store = _FileSessionStore(path=f"{tmp}/sessions.json")
            result = store.get("nonexistent")
            assert result is None

    def test_get_returns_stored_value_when_key_exists(self):
        """Round-trip: set() then get() returns the stored dict.

        Zen collapse 2026-07-24: proxy upserts into the unified identity store
        and may enrich TTL/metadata fields — assert payload fields preserved.
        """
        import tempfile
        from arifosmcp.runtime.tools import _FileSessionStore

        with tempfile.TemporaryDirectory() as tmp:
            store = _FileSessionStore(path=f"{tmp}/sessions.json")
            payload = {"actor_id": "arif", "stage": "888"}
            store.set("SEAL-test123", payload)
            result = store.get("SEAL-test123", {})
            assert isinstance(result, dict)
            assert result.get("actor_id") == "arif"
            assert result.get("stage") == "888"

    def test_get_existing_key_with_default_ignores_default(self):
        """When key exists, .get() returns the value, not the default."""
        import tempfile
        from arifosmcp.runtime.tools import _FileSessionStore

        with tempfile.TemporaryDirectory() as tmp:
            store = _FileSessionStore(path=f"{tmp}/sessions.json")
            store.set("k1", {"real": "value"})
            result = store.get("k1", {"fallback": "ignored"})
            assert isinstance(result, dict)
            assert result.get("real") == "value"
            assert "fallback" not in result

@pytest.fixture
def isolated_session_store(tmp_path, monkeypatch):
    """Seed the unified session store in isolation and restore module state after."""
    from arifosmcp.runtime import session as sess

    identity, actor_map = dict(sess._SESSION_IDENTITY), dict(sess._ACTOR_SESSION_MAP)
    continuity, active = dict(sess._SESSION_CONTINUITY_STATE), sess._ACTIVE_SESSION_ID
    loaded, mtime_ns = sess._STORE_LOADED, sess._STORE_MTIME_NS
    with sess._STORE_LOCK:
        sess._SESSION_IDENTITY.clear()
        sess._ACTOR_SESSION_MAP.clear()
        sess._SESSION_CONTINUITY_STATE.clear()
    monkeypatch.setattr(sess, "_SESSION_STORE_PATH", tmp_path / "runtime_sessions.json")
    monkeypatch.setattr(sess, "_LEGACY_MIGRATED", True)
    yield sess
    with sess._STORE_LOCK:
        sess._SESSION_IDENTITY.clear()
        sess._SESSION_IDENTITY.update(identity)
        sess._ACTOR_SESSION_MAP.clear()
        sess._ACTOR_SESSION_MAP.update(actor_map)
        sess._SESSION_CONTINUITY_STATE.clear()
        sess._SESSION_CONTINUITY_STATE.update(continuity)
        sess._ACTIVE_SESSION_ID = active
        sess._STORE_LOADED, sess._STORE_MTIME_NS = loaded, mtime_ns


def _counting_persist(sess, monkeypatch):
    """Wrap the module's _persist_store so a test can count whole-store rewrites."""
    writes = []
    real_persist = sess._persist_store

    def counting_persist():
        writes.append(1)
        real_persist()

    monkeypatch.setattr(sess, "_persist_store", counting_persist)
    return writes


def _seed(sess, session_id: str, seconds_to_expiry: float) -> dict:
    """Put one session record straight into the in-memory store."""
    from datetime import UTC, datetime, timedelta

    record = {
        "session_id": session_id,
        "actor_id": "write-amp-test",
        "expires_at": (datetime.now(UTC) + timedelta(seconds=seconds_to_expiry)).isoformat(),
    }
    with sess._STORE_LOCK:
        sess._SESSION_IDENTITY[session_id] = record
        sess._ACTOR_SESSION_MAP[session_id] = record["actor_id"]
        sess._SESSION_CONTINUITY_STATE[session_id] = {"state": {"session": session_id}}
    return record


class TestStoreWriteAmplification:
    """Regression tests for the 2026-11-25 kernel event-loop stall.

    Every session-store write rewrites the whole file under ``_STORE_LOCK``
    (~15MB in production). Paths that changed nothing, or that changed N
    records one at a time, turned one MCP call into many whole-store rewrites
    and starved the kernel's event loop (2310 loop-lag events in 24h).
    """

    def test_expired_sweep_rewrites_the_store_once(self, isolated_session_store, monkeypatch):
        """A mass expiry costs ONE whole-store rewrite, not one per expired record."""
        import json

        sess = isolated_session_store
        for i in range(40):
            _seed(sess, f"dead-{i}", seconds_to_expiry=-60)
        for i in range(5):
            _seed(sess, f"live-{i}", seconds_to_expiry=3600)
        writes = _counting_persist(sess, monkeypatch)

        assert sess.list_active_sessions_count() == 5

        assert len(writes) == 1
        assert sorted(sess._SESSION_IDENTITY) == sorted(f"live-{i}" for i in range(5))
        assert not any(key.startswith("dead-") for key in sess._ACTOR_SESSION_MAP)
        assert not any(key.startswith("dead-") for key in sess._SESSION_CONTINUITY_STATE)
        on_disk = json.loads(sess._SESSION_STORE_PATH.read_text(encoding="utf-8"))
        assert sorted(on_disk["sessions"]) == sorted(f"live-{i}" for i in range(5))

    def test_clearing_an_unknown_session_writes_nothing(self, isolated_session_store, monkeypatch):
        """An id that is not anchored changes nothing, so the store is not rewritten."""
        sess = isolated_session_store
        _seed(sess, "known-1", seconds_to_expiry=3600)
        writes = _counting_persist(sess, monkeypatch)

        sess.clear_session_identity("never-anchored")
        assert writes == []

        sess.clear_session_identity("known-1")
        assert len(writes) == 1
        assert "known-1" not in sess._SESSION_IDENTITY
        assert "known-1" not in sess._ACTOR_SESSION_MAP
        assert "known-1" not in sess._SESSION_CONTINUITY_STATE

    def test_looking_up_a_missing_session_writes_nothing(self, isolated_session_store, monkeypatch):
        """Every MCP call resolves its session first; a miss must stay a read."""
        sess = isolated_session_store
        writes = _counting_persist(sess, monkeypatch)

        assert sess.get_session_execution_state("missing-sid") is None
        assert sess._ensure_active_record("missing-sid") is None
        assert writes == []


class _CountingPath:
    """Minimal Path stand-in that counts whole-store reads and delegates the rest."""

    def __init__(self, real):
        self._real = real
        self.reads = 0

    def __getattr__(self, name):
        return getattr(self._real, name)

    def __fspath__(self):
        return str(self._real)

    def read_text(self, *args, **kwargs):
        self.reads += 1
        return self._real.read_text(*args, **kwargs)


class TestOwnWriteReload:
    """Regression test for the 2026-11-25 kernel event-loop stall (second half).

    ``_persist_store`` never advanced the mtime cache, so the read right after a
    write re-parsed the whole file (≈0.12s at 15MB) under ``_STORE_LOCK`` — the
    file this process had just written. Writes by OTHER processes must still
    force a reload (the P1 2026-10-06 staleness guarantee).
    """

    def test_own_write_does_not_reread_the_store(self, isolated_session_store, monkeypatch):
        sess = isolated_session_store
        proxy = _CountingPath(sess._SESSION_STORE_PATH)
        monkeypatch.setattr(sess, "_SESSION_STORE_PATH", proxy)
        _seed(sess, "own-1", seconds_to_expiry=3600)
        sess._load_store()  # store file absent -> loaded, nothing read

        sess._write_record("own-2", {"session_id": "own-2", "actor_id": "write-amp-test"})
        assert proxy._real.exists()
        assert proxy.reads == 0

        sess._load_store()
        assert proxy.reads == 0

    def test_write_by_another_process_still_forces_a_reread(
        self, isolated_session_store, monkeypatch
    ):
        import json
        import os

        sess = isolated_session_store
        proxy = _CountingPath(sess._SESSION_STORE_PATH)
        monkeypatch.setattr(sess, "_SESSION_STORE_PATH", proxy)
        _seed(sess, "own-1", seconds_to_expiry=3600)
        sess._load_store()
        sess._write_record("own-2", {"session_id": "own-2", "actor_id": "write-amp-test"})
        assert proxy.reads == 0

        foreign = {"version": 2, "sessions": {"ext-1": {"session_id": "ext-1", "actor_id": "other"}}}
        proxy._real.write_text(json.dumps(foreign), encoding="utf-8")
        future_ns = (proxy._real.stat().st_mtime_ns // 1_000_000_000 + 5) * 1_000_000_000
        os.utime(proxy._real, ns=(future_ns, future_ns))

        sess._load_store()

        assert proxy.reads == 1
        assert "ext-1" in sess._SESSION_IDENTITY
        # A stale "own write" fingerprint must never be trusted as current.
        sess._remember_own_write((future_ns - 1, 1))
        assert sess._STORE_MTIME_NS == future_ns
