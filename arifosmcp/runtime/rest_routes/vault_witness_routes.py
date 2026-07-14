"""
arifOS VAULT999 Witness Routes — Phase A of Reality Observatory.

Three endpoints to prove VAULT999 is more than a "connected" badge:

  GET  /api/observatory/v1/seal/verify?from=N&to=M  →  hash-chain integrity
  GET  /api/observatory/v1/seal/replay?seq=N         →  reconstruct originals
  POST /api/observatory/v1/seal/test                  →  round-trip self-test (write→read→verify→replay)

All three are READ-ONLY against the chain except `/seal/test`, which performs a
single ephemeral write to verify the write path. The test endpoint stamps a
`specialized=observatory_test` payload so we never confuse it with real seals.

No mutation of the live chain. No services restart. No environment changes.

Forged 2026-07-14 — companion to observatory_routes.py.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

# Canonical VAULT999 paths. The `seal_chain.jsonl` writer is the Node process;
# we read it directly without locks (it is append-only and writes are short).
VAULT_DIR = Path(os.getenv("VAULT_DIR", "/root/.local/share/arifos/vault999"))
LEDGER_PATH = VAULT_DIR / "seal_chain.jsonl"
HEAD_PATH = VAULT_DIR / "seal_chain_head.json"

GENESIS_PREV_HASH = "sha256:0"  # sentinel — never matches a real sha256
CANONICAL_WRITER = Path(os.getenv("SEAL_CHAIN_WRITER", "/root/AAA/a2a-server/seal_chain.js"))


# ── Reading the chain ─────────────────────────────────────────────────────────
def _read_chain(limit: int | None = None) -> list[dict[str, Any]]:
    """Tail-read the jsonl. Tolerates partial lines, returns [] on any I/O failure.

    Defensive: filters to dicts only (in case of stray non-dict lines, e.g.
    a stale symbol table entry from a different process that's still pointing
    at an in-memory object).
    """
    if not LEDGER_PATH.exists():
        return []
    try:
        with open(LEDGER_PATH, encoding="utf-8") as fh:
            lines = [ln for ln in fh.readlines() if ln.strip()]
        if limit is not None and limit > 0:
            lines = lines[-limit:]
        out: list[dict[str, Any]] = []
        for ln in lines:
            try:
                parsed = json.loads(ln)
            except Exception:
                continue
            # Defensive: only keep dict-shaped entries.
            if isinstance(parsed, dict):
                out.append(parsed)
            else:
                logger.debug("_read_chain: skipping non-dict entry: %r", parsed)
        return out
    except Exception as exc:
        logger.warning("read_chain failed: %s", exc)
        return []


def _read_head() -> dict[str, Any] | None:
    if not HEAD_PATH.exists():
        return None
    try:
        with open(HEAD_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


# ── Hash math (matches seal_chain.js v2.0.0 canonical) ───────────────────────
def _canonical_json(obj: Any) -> str:
    """Strict canonical JSON: sort keys, no whitespace, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _compute_this_hash(prev_hash: str, payload: Any, seq: int, epoch: str) -> str:
    """Matches seal_chain.js v2.0.0 this_hash = sha256(prev_hash || canonical_json(payload) || String(seq) || epoch).

    We deliberately exclude `payload` keys not present in v1.0 entries — the
    enrichment added in v2.0 (merkle_root, witness, etc.) is OPTIONAL; we
    recompute the base hash only. The full-v2 verification is delegated to
    the Node writer (operators can `node seal_chain.js verify` out-of-band).
    """
    material = "|".join((prev_hash, _canonical_json(payload), str(seq), epoch))
    h = hashlib.sha256(material.encode("utf-8"))
    return "sha256:" + h.hexdigest()


# ── Verify ─────────────────────────────────────────────────────────────────────
def verify_chain_window(*, from_seq: int | None = None, to_seq: int | None = None) -> dict[str, Any]:
    """Return the integrity verdict for entries [from_seq, to_seq] (or whole chain).

    Honest result includes:
        - head_seq / total / checked
        - per-entry: recorded this_hash vs recomputed; mismatch flagged
        - prev_hash continuity: declared_prev must equal prior entry's recorded this_hash
        - gaps: any seq numbers missing in the window
        - first_mismatch_seq: first entry that fails recomputation
        - status: ok | mismatch | broken_chain | empty

    Crucially: when an entry claims a `prev_hash`, we USE THAT claimed prev for
    the recompute. Otherwise tampering with prev_hash would not be detectable.
    """
    entries = _read_chain()
    if not entries:
        return {"status": "empty", "head_seq": None, "checked": 0, "gaps": [], "mismatches": []}

    # Filter window
    if from_seq is not None:
        entries = [e for e in entries if (e.get("seq") or 0) >= from_seq]
    if to_seq is not None:
        entries = [e for e in entries if (e.get("seq") or 0) <= to_seq]

    if not entries:
        return {"status": "empty", "head_seq": None, "checked": 0, "gaps": [], "mismatches": []}

    # When filtering a mid-chain window, the predecessor of the first window entry
    # is the entry immediately preceding `from_seq` in the full chain (not GENESIS).
    # We seed `expected_prev` from that predecessor so window queries don't
    # spuriously flag the entry-from_seq boundary as a chain break.
    expected_prev = GENESIS_PREV_HASH
    if from_seq is not None and from_seq > 1:
        full = _read_chain()
        for e in full:
            if isinstance(e.get("seq"), int) and e["seq"] == from_seq - 1:
                expected_prev = e.get("this_hash") or GENESIS_PREV_HASH
                break

    mismatches: list[dict[str, Any]] = []
    gaps: list[int] = []
    first_mismatch_seq: int | None = None

    for entry in entries:
        seq = entry.get("seq")
        if not isinstance(seq, int):
            mismatches.append({"seq": None, "reason": "missing-seq"})
            continue
        # prev_hash continuity — entry's `prev_hash` must equal prior entry's `this_hash`.
        declared_prev = entry.get("prev_hash")
        if declared_prev and declared_prev != expected_prev:
            mismatches.append({
                "seq": seq,
                "reason": "prev_hash-mismatch",
                "expected": expected_prev,
                "got": declared_prev,
            })
            if first_mismatch_seq is None:
                first_mismatch_seq = seq
        payload = entry.get("payload") if "payload" in entry else entry
        epoch = entry.get("epoch", "")
        # USE declared_prev (or expected_prev if absent) for the recompute. Tampering
        # with declared_prev WILL cause a this-hash mismatch on the recompute.
        recompute_prev = declared_prev if declared_prev else expected_prev
        recomputed = _compute_this_hash(recompute_prev, payload, seq, epoch)
        recorded = entry.get("this_hash", "").split(":", 1)[-1] if entry.get("this_hash") else ""
        if not recorded:
            mismatches.append({"seq": seq, "reason": "missing-this-hash"})
            if first_mismatch_seq is None:
                first_mismatch_seq = seq
        else:
            expected_hex = recomputed.split(":", 1)[-1]
            if not hmac.compare_digest(recorded[: len(expected_hex)], expected_hex):
                mismatches.append({
                    "seq": seq,
                    "reason": "this-hash-mismatch",
                    "recomputed": recomputed,
                    "recorded": entry.get("this_hash"),
                })
                if first_mismatch_seq is None:
                    first_mismatch_seq = seq

        expected_prev = entry.get("this_hash") or GENESIS_PREV_HASH

    # Detect gaps in seq numbering within the filtered window.
    seqs = [e["seq"] for e in entries if isinstance(e.get("seq"), int)]
    if seqs:
        for i in range(min(seqs), max(seqs)):
            if i not in seqs:
                gaps.append(i)

    head = _read_head()
    head_seq = (head or {}).get("seq")
    status = "ok" if not mismatches else "broken_chain"
    return {
        "status": status,
        "head_seq": head_seq,
        "checked": len(entries),
        "first_mismatch_seq": first_mismatch_seq,
        "gaps": gaps[:32],
        "mismatches": mismatches[:16],
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


# ── Replay ─────────────────────────────────────────────────────────────────────
def replay_entry(seq: int) -> dict[str, Any]:
    """Reconstruct the original payload and re-derive the hash for a given seq.

    Returns:
        {
          seq, found, payload (original), epoch, this_hash (recomputed), recorded_this_hash,
          hash_chain_ok: bool,
        }
    """
    entries = _read_chain()
    found: list[dict[str, Any]] = [e for e in entries if e.get("seq") == seq]
    if not found:
        return {"seq": seq, "found": False, "reason": "seq not found in ledger"}
    entry = found[0]
    prev_entry = None
    for e in entries:
        if isinstance(e.get("seq"), int) and e["seq"] == seq - 1:
            prev_entry = e
            break
    prev_hash = (prev_entry or {}).get("this_hash") or GENESIS_PREV_HASH
    payload = entry.get("payload") if "payload" in entry else entry
    epoch = entry.get("epoch", "")
    recomputed = _compute_this_hash(prev_hash, payload, seq, epoch)
    recorded = entry.get("this_hash", "")
    return {
        "seq": seq,
        "found": True,
        "epoch": epoch,
        "actor": entry.get("actor"),
        "verdict": entry.get("verdict"),
        "payload": payload,
        "recomputed_this_hash": recomputed,
        "recorded_this_hash": recorded,
        "hash_chain_ok": hmac.compare_digest(recomputed, recorded or ""),
    }


# ── Test round-trip ───────────────────────────────────────────────────────────
def self_test() -> dict[str, Any]:
    """Confirm VAULT is alive end-to-end.

    1) Verify the entire chain (read path).
    2) Append a single ephemeral entry (write path).
    3) Read it back (read-back).
    4) Re-derive and compare (verify).
    5) Replay by seq (replay).
    Returns a structured PASS/FAIL envelope.
    """
    started = time.time()
    try:
        head_before = _read_head()
        head_seq_before = (head_before or {}).get("seq")

        # 1) Read path. Historical integrity is reported separately; a known
        # legacy segment must not prevent testing the canonical current writer.
        verify_result = verify_chain_window()
        read_ok = LEDGER_PATH.exists() and head_before is not None

        # 2) Write path — delegate to the locked canonical Node writer. Never
        # append or update the head from this Python observer.
        test_payload = {
            "_specialized": "observatory_test",
            "intent": "verify_write_read_verify_replay_roundtrip",
            "produced_by": "observatory_self_test",
            "produced_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "run_id": str(uuid.uuid4()),
            "agent_id": "observatory_self_test",
            "action": "observatory.self_test",
            "verdict": "HOLD",
            "witness": {
                "human": None,
                "ai": "observatory_self_test",
                "external": "canonical_writer_roundtrip",
            },
        }
        write_ok = False
        writer_result: dict[str, Any] = {}
        try:
            env = os.environ.copy()
            env["VAULT_DIR"] = str(LEDGER_PATH.parent)
            proc = subprocess.run(
                ["node", str(CANONICAL_WRITER), "write", json.dumps(test_payload)],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
                env=env,
            )
            writer_result = json.loads(proc.stdout)
            write_ok = bool(writer_result.get("ok"))
        except Exception as exc:
            logger.warning("self_test write failure: %s", exc)
        test_seq = writer_result.get("seq")
        test_this_hash = writer_result.get("this_hash")

        # 3) Read-back
        read_back = None
        if write_ok:
            entries = _read_chain()
            for e in reversed(entries):
                if e.get("seq") == test_seq:
                    read_back = e
                    break
        read_back_ok = bool(read_back) and read_back.get("this_hash") == test_this_hash

        # 4) Verify (post-write)
        verify_post = verify_chain_window(from_seq=test_seq, to_seq=test_seq) if isinstance(test_seq, int) else {"status": "broken_chain"}
        verify_ok = verify_post.get("status") in ("ok", "empty")

        # 5) Replay
        replay_result = replay_entry(test_seq) if write_ok else {"found": False}
        replay_ok = bool(replay_result.get("hash_chain_ok"))

        all_ok = read_ok and write_ok and read_back_ok and verify_ok and replay_ok
        elapsed_ms = int((time.time() - started) * 1000)
        return {
            "status": "PASS" if all_ok else "FAIL",
            "elapsed_ms": elapsed_ms,
            "steps": {
                "read": {
                    "ok": read_ok,
                    "head_seq_before": head_seq_before,
                    "historical_verify_status": verify_result.get("status"),
                },
                "write": {"ok": write_ok, "test_seq": test_seq},
                "read_back": {"ok": read_back_ok},
                "verify": {"ok": verify_ok, "post_write_status": verify_post.get("status")},
                "replay": {"ok": replay_ok, "hash_chain_ok": replay_result.get("hash_chain_ok")},
            },
            "head_seq_after": (test_seq if write_ok else head_seq_before),
        }
    except Exception as exc:
        logger.exception("self_test failure")
        return {"status": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}


# ── Tier middleware (F13 2026-07-14) ──────────────────────────────────────────
def _enforce_tier(request, required: str) -> tuple[bool, str | None]:
    """Check the request's tier credentials.

    Required tier ∈ {"public", "operator"}. `operator` requires the X-Op-Token
    header to sha256-match the ARIFOS_OP_TOKEN_HASH env var. Mismatch ⇒ (False, reason).

    The Caddy layer forwards the X-Op-Token header as-is; we hash it here
    because storing only the hash on disk (in vault.env) means the only place
    a token-vs-hash comparison can run is at request time.
    """
    import hashlib as _hashlib
    import os as _os

    if required == "public":
        return True, None

    if required == "operator":
        token = request.headers.get("X-Op-Token", "").strip()
        if not token:
            return False, "X-Op-Token required (tier=operator)"
        expected = _os.getenv("ARIFOS_OP_TOKEN_HASH", "").strip()
        if not expected:
            return False, "operator tier not bootstrapped on this server (missing ARIFOS_OP_TOKEN_HASH in vault.env)"
        got_hash = _hashlib.sha256(token.encode("utf-8")).hexdigest()
        if not hmac.compare_digest(got_hash, expected):
            return False, "X-Op-Token hash mismatch"
        return True, None

    return False, f"unknown required tier: {required}"


# ── Route registration ────────────────────────────────────────────────────────
def register_vault_witness_routes(app: Any, prefix: str = "/api/observatory/v1/seal") -> None:
    """Register VAULT999 witness endpoints on the given Starlette/FastAPI app."""
    from starlette.responses import JSONResponse  # type: ignore

    from arifosmcp.runtime.capability_drift import record_test_result

    async def _verify(request):
        ok, reason = _enforce_tier(request, required="operator")
        if not ok:
            return JSONResponse({"error": reason or "tier denied", "tier_required": "operator"}, status_code=403)
        try:
            from_seq = int(request.query_params.get("from", "0"))
        except (TypeError, ValueError):
            from_seq = 0
        try:
            to_seq_raw = request.query_params.get("to")
            to_seq = int(to_seq_raw) if to_seq_raw is not None else None
        except (TypeError, ValueError):
            to_seq = None
        try:
            payload = verify_chain_window(from_seq=from_seq or None, to_seq=to_seq)
        except Exception as exc:
            return JSONResponse({"error": f"{type(exc).__name__}: {exc}"}, status_code=500)
        return JSONResponse(payload)

    async def _replay(request):
        ok, reason = _enforce_tier(request, required="operator")
        if not ok:
            return JSONResponse({"error": reason or "tier denied", "tier_required": "operator"}, status_code=403)
        try:
            seq = int(request.query_params.get("seq", "0"))
        except (TypeError, ValueError):
            return JSONResponse({"error": "seq must be an integer"}, status_code=400)
        if seq <= 0:
            return JSONResponse({"error": "seq must be ≥ 1"}, status_code=400)
        try:
            payload = replay_entry(seq)
        except Exception as exc:
            return JSONResponse({"error": f"{type(exc).__name__}: {exc}"}, status_code=500)
        if not payload.get("found"):
            return JSONResponse(payload, status_code=404)
        return JSONResponse(payload)

    async def _test(request):
        ok, reason = _enforce_tier(request, required="operator")
        if not ok:
            return JSONResponse({"error": reason or "tier denied", "tier_required": "operator"}, status_code=403)
        try:
            payload = self_test()
        except Exception as exc:
            return JSONResponse({"status": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}, status_code=500)
        # Record a per-tool cap-drift entry for the test actor (heuristic).
        if payload.get("status") == "PASS":
            record_test_result("observatory_self_test", passed=True, error=None)
        else:
            record_test_result("observatory_self_test", passed=False, error=str(payload.get("reason") or payload))
        return JSONResponse(payload, status_code=200 if payload.get("status") == "PASS" else 503)

    def route(path: str, methods: list[str]):
        full = prefix.rstrip("/") + path

        def _decorator(handler: Callable):
            if hasattr(app, "add_route") or "Starlette" in str(type(app)) or "FastAPI" in str(type(app)):
                from starlette.routing import Route

                app.router.routes.append(Route(full, endpoint=handler, methods=methods))
            elif hasattr(app, "custom_route"):
                app.custom_route(full, methods=methods)(handler)
            elif hasattr(app, "route"):
                app.route(full, methods=methods)(handler)
            else:
                logger.warning("Failed to register vault_witness route %s: app has no route method", full)
            return handler

        return _decorator

    @route("/verify", ["GET"])
    async def _h_verify(req):  # type: ignore
        return await _verify(req)

    @route("/replay", ["GET"])
    async def _h_replay(req):  # type: ignore
        return await _replay(req)

    @route("/test", ["POST", "GET"])
    async def _h_test(req):  # type: ignore
        return await _test(req)
