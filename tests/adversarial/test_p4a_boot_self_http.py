"""P4a — boot attestation must never make a synchronous self-HTTP call on the loop.

RED-FIRST CONTRACT
------------------
Pre-patch, Q1 resolves identity ONLY via HTTP /sessions/lookup, and Q2 falls
back to HTTP /health. Both are synchronous urllib calls executed on the ASGI
event loop — the documented deadlock class (boot_attestation.py:233).

Post-patch:
  * Q1 answers from the in-process session store first.
  * _local_url_get() returns None when a loop is running (callers degrade
    conservatively instead of blocking the loop).
  * CLI / out-of-process callers keep the HTTP fallback byte-identically.

Run this file on the pre-patch commit: tests 1-4 must FAIL (urlopen reached).
Run after: all green.
"""

import asyncio
import time

import arifosmcp.runtime.boot_attestation as ba


def _forbid_self_http(monkeypatch):
    def boom(*args, **kwargs):
        raise AssertionError("SELF_HTTP_ON_LOOP: synchronous self-call reached the event loop")

    monkeypatch.setattr(ba, "urlopen", boom)


def test_q1_uses_in_process_lookup_inside_loop(monkeypatch):
    _forbid_self_http(monkeypatch)
    monkeypatch.setattr(
        "arifosmcp.runtime.session.get_session_identity",
        lambda sid: {"actor_id": "333-AGI"},
    )

    async def run():
        return ba._answer_q1_identity_bind("sess-test")

    ans = asyncio.run(run())
    assert ans.answer == "YES"


def test_q1_degrades_without_self_http_inside_loop(monkeypatch):
    _forbid_self_http(monkeypatch)
    monkeypatch.setattr("arifosmcp.runtime.session.get_session_identity", lambda sid: None)

    async def run():
        return ba._answer_q1_identity_bind("sess-test")

    ans = asyncio.run(run())
    assert ans.answer == "PARTIAL"


def test_q2_degrades_without_self_http_inside_loop(monkeypatch):
    _forbid_self_http(monkeypatch)
    monkeypatch.setattr("arifosmcp.runtime.law.get_floor_count", lambda: 0)

    async def run():
        return ba._answer_q2_constitution_load()

    ans = asyncio.run(run())
    assert ans.answer in ("NO", "PARTIAL")


def test_64_loop_calls_never_block(monkeypatch):
    _forbid_self_http(monkeypatch)

    async def call():
        return ba._local_url_get("http://127.0.0.1:8088/health")

    async def run():
        t0 = time.perf_counter()
        results = await asyncio.gather(*[call() for _ in range(64)])
        return results, time.perf_counter() - t0

    results, elapsed = asyncio.run(run())
    assert all(r is None for r in results)
    assert elapsed < 0.5, f"loop path took {elapsed:.3f}s"


def test_cli_path_keeps_http_fallback(monkeypatch):
    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"actor_id":"cli-actor"}'

    monkeypatch.setattr("arifosmcp.runtime.session.get_session_identity", lambda sid: None)
    monkeypatch.setattr(ba, "urlopen", lambda req, timeout=0: FakeResp())

    ans = ba._answer_q1_identity_bind("sess-cli")
    assert ans.answer == "YES"
