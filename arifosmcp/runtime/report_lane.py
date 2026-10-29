"""arifosmcp/runtime/report_lane.py — Agent Report Lane (F13 2026-10-20)

PURPOSE
-------
Take the human out of the agent loop.

Before this lane, every agent that wanted to say something said it to Arif.
Twelve agents x every task = a firehose aimed at one human, and the human
becomes the message bus. That is the chaos.

This lane inverts it:

  agents ──report──▶ kernel ──classify──▶ agents (peer inbox)
                                 │
                                 └── escalate only ──▶ human, batched

The human receives ONLY what is genuinely his: a decision no agent may make,
or a block no agent may clear. Everything else lands in a peer inbox that
agents read, so agents coordinate with agents.

DIVERGENCE FROM LIVENESS
------------------------
A report is an agent's claim about its own work. It is SELF-REPORTED until
something else probes it. `claim_state` records that, and nothing here may
promote a report to verified truth. Peer reports are opinions; evidence is
a probe.

STORAGE
-------
/var/lib/arifos/reports/inbox.jsonl   append-only, one JSON object per line
/var/lib/arifos/reports/outbox.jsonl  escalation queue awaiting human push

No deletion API. Append-only, mirroring VAULT999 discipline at a lower tier.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPORT_DIR = Path(os.getenv("ARIFOS_REPORT_DIR", "/var/lib/arifos/reports"))
INBOX = REPORT_DIR / "inbox.jsonl"
OUTBOX = REPORT_DIR / "outbox.jsonl"
CURSOR_DIR = REPORT_DIR / "cursors"

# Kinds that are allowed to interrupt a human. Deliberately narrow: this tuple
# is the entire reason the human can leave the loop.
HUMAN_CLASSES: frozenset[str] = frozenset({"decision", "blocked"})

# Everything an agent may file. Anything else is coerced to "fyi".
VALID_KINDS: tuple[str, ...] = ("fyi", "peer", "decision", "blocked", "done", "claim")

# Human pushes are coalesced. One message per window, never a stream.
PUSH_WINDOW_MINUTES = int(os.getenv("ARIFOS_REPORT_PUSH_WINDOW_MIN", "20"))
MAX_ITEMS_PER_PUSH = 6
BODY_PREVIEW_CHARS = 220

# Distinct agents that must vouch for an unverified decision report before it may
# interrupt the human. Agents triage agents; the person is the exception path.
PEER_QUORUM = int(os.getenv("ARIFOS_REPORT_PEER_QUORUM", "2"))
# [F13 2026-10-21 — insiden t-ext-1] Lantai persidangan: ack hanya kira ke
# quorum selepas ACK_DELIBERATION_MIN_S daripada laporan PERTAMA thread.
# Bukti insiden: 6 ack dalam 3.1s (codex 3x + gemini 3x) atas thread berumur
# 1s mengeluarkan quorum untuk umpan "wire money" stranger. Id berbeza ≠
# kebebasan bila burst berskrip (kin: Scar-2026-10-01-002).
ACK_DELIBERATION_MIN_S = int(os.getenv("ARIFOS_REPORT_ACK_DELIBERATION_S", "30"))

ACKS = REPORT_DIR / "acks.jsonl"


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _ensure_dirs() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    CURSOR_DIR.mkdir(parents=True, exist_ok=True)


def _append(path: Path, row: dict[str, Any]) -> None:
    _ensure_dirs()
    line = json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
    # O_APPEND + single write() = atomic for lines under PIPE_BUF on Linux.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o640)
    try:
        os.write(fd, line.encode("utf-8"))
    finally:
        os.close(fd)


def _read_all(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue
                if isinstance(obj, dict):
                    rows.append(obj)
    except OSError:
        logger.exception("report lane: read failed for %s", path)
    return rows


def _classify(kind: str, sender: str, subject: str, body: str) -> tuple[str, str]:
    """Return (kind, why). Coerce unknown kinds instead of trusting the caller."""
    k = (kind or "").strip().lower()
    if k not in VALID_KINDS:
        return "fyi", f"unknown kind {kind!r} coerced to fyi"
    if k in HUMAN_CLASSES:
        return k, "caller declared a human-class report"
    return k, "non-interrupting class"


def report(
    *,
    sender: str,
    platform: str,
    kind: str,
    subject: str,
    body: str,
    session_id: str | None = None,
    thread_id: str | None = None,
    evidence: Any = None,
    needs_human: bool | None = None,
    verified_actor: bool = False,
    dry_run: bool = False,
    server_actor: str | None = None,
    envelope_call_hash: str | None = None,
) -> dict[str, Any]:
    """File one report into the lane. Never raises on bad input; coerces.

    ESCALATION LAW (F13 2026-10-20). An unverified caller may NOT decide that it
    deserves the human's attention. Reaching F13 requires one of:
      (a) a cryptographically verified actor token, or
      (b) PEER QUORUM — at least two distinct agents ack the same thread_id.
    Otherwise a decision/blocked report is downgraded to peer class and the
    reason is recorded. This is what keeps the human out of the noise: agents
    must agree before they are allowed to interrupt a person.
    """
    k, why = _classify(kind, sender, subject, body)
    needs_human_flag = (k in HUMAN_CLASSES) if needs_human is None else bool(needs_human)

    escalate = False
    withheld: str | None = None
    if k in HUMAN_CLASSES:
        if verified_actor:
            escalate = True
        else:
            quorum = _thread_ackers(thread_id) if thread_id else []
            if len(quorum) >= PEER_QUORUM:
                escalate = True
            else:
                escalate = False
                withheld = (
                    f"needs_peer_quorum: {len(quorum)}/{PEER_QUORUM} agents acked "
                    f"thread {thread_id!r} — unverified sender may not interrupt the human"
                )
                k = "peer"
                why = "escalation withheld (unverified sender, no peer quorum)"

    report_id = f"rep-{uuid.uuid4().hex[:12]}"
    row = {
        "schema": "arifos.report.v1",
        "report_id": report_id,
        "ts": _now(),
        # Server stamps the caller identity; `sender_claimed` is what the
        # caller WROTE for itself (AgentsRoom pattern — agents may not mint
        # their own identity). They differ whenever an unverified caller
        # names itself "codex" or "stranger".
        "sender": (server_actor or "anonymous").strip()[:120],
        "sender_claimed": (sender or "").strip()[:120] or None,
        "platform": (platform or "unknown").strip()[:40],
        "kind": k,
        "kind_requested": kind,
        "class_reason": why,
        "subject": (subject or "").strip()[:200],
        "body": (body or "").strip()[:8000],
        "thread_id": (thread_id or "").strip()[:80] or None,
        "session_id": (session_id or "").strip()[:80] or None,
        "evidence": evidence if isinstance(evidence, (dict, list, str)) else None,
        "needs_human_flag": needs_human_flag,
        "escalated": escalate,
        "escalation_withheld": withheld,
        "sender_verified": bool(verified_actor),
        # A report is the sender's own claim. Never verified here.
        "claim_state": "SELF_REPORTED",
        "verified_by": None,
        "ack_by": [],
    }
    row["content_hash"] = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(
                {k2: row[k2] for k2 in ("sender", "subject", "body", "ts")}, sort_keys=True
            ).encode()
        ).hexdigest()
    )
    # PACKET-AB Changeset A (F13 authorized 2026-10-29, plan_hash
    # sha256:1a411120afbac012d79c1cfb…): a ΔS claim in a report body is
    # prose until bound to an envelope call_hash by a later, separately
    # authorized wiring. Until then every prose ΔS stores UNMEASURED —
    # it can never enter a governance field as a number.
    row["delta_s_claim"] = bind_delta_s(body, envelope_call_hash)

    if dry_run:
        # F2 honesty: a dry run must not touch the store. Preview only.
        return {
            "status": "dry_run",
            "would_write": True,
            "report_id": None,
            "kind": k,
            "queued_for_human": escalate,
            "escalation_withheld": withheld,
            "claim_state": "SELF_REPORTED",
            "delta_s_claim": row["delta_s_claim"],
            "note": "Dry run — nothing written to the store.",
        }

    _append(INBOX, row)
    if escalate:
        _append(OUTBOX, {"report_id": report_id, "queued_at": _now(), "pushed": False})
        row["queued_for_human"] = True
    else:
        row["queued_for_human"] = False

    return {
        "status": "recorded",
        "report_id": report_id,
        "kind": k,
        "queued_for_human": escalate,
        "escalation_withheld": withheld,
        "claim_state": "SELF_REPORTED",
        "note": (
            "Report stored in the peer lane. Only kind=decision|blocked reaches "
            "the human, and only in a coalesced push."
        ),
    }


def inbox(
    *,
    since: str | None = None,
    sender: str | None = None,
    kind: str | None = None,
    limit: int = 20,
    mark_read: bool = False,
    reader: str = "unknown",
    verified_actor: bool = False,
) -> dict[str, Any]:
    """Read reports filed by other agents. Pull-only — nothing is pushed.

    F13 2026-10-21 (privacy floor): the peer board (fyi/peer/done/claim) is
    open — that is the messageboard. Rows of HUMAN_CLASSES (decision/blocked)
    carry operational secrets (tokens, hosts, infrastructure) and are visible
    ONLY to verified actors. Unverified readers never see them.
    """
    rows = _read_all(INBOX)
    cursor = _load_cursor(reader)
    if since is None and cursor:
        since = cursor

    out: list[dict[str, Any]] = []
    hidden_sensitive = 0
    for row in rows:
        if since and str(row.get("ts", "")) <= since:
            continue
        if sender and row.get("sender") != sender:
            continue
        if kind and row.get("kind") != kind:
            continue
        row_kind = row.get("kind")
        # Downgraded human-class rows carry `kind_requested` = decision/blocked
        # (the escalation law rewrites kind to peer on withhold) — the CONTENT
        # is the sensitive part, so filter on requested class + escalation.
        sensitive = (
            row_kind in HUMAN_CLASSES
            or row.get("kind_requested") in HUMAN_CLASSES
            or bool(row.get("escalated"))
        )
        if sensitive and not verified_actor:
            hidden_sensitive += 1
            continue
        out.append(
            {
                "report_id": row.get("report_id"),
                "ts": row.get("ts"),
                "sender": row.get("sender"),
                "sender_claimed": row.get("sender_claimed"),
                "platform": row.get("platform"),
                "kind": row.get("kind"),
                "subject": row.get("subject"),
                "body": (row.get("body") or "")[:1200],
                "thread_id": row.get("thread_id"),
                "claim_state": row.get("claim_state"),
                "escalated": row.get("escalated"),
            }
        )
        if len(out) >= max(1, min(int(limit or 20), 200)):
            break

    latest = rows[-1].get("ts") if rows else since
    if mark_read and latest:
        _save_cursor(reader, latest)

    result: dict[str, Any] = {
        "status": "ok",
        "count": len(out),
        "total_filed": len(rows),
        "cursor": latest,
        "reports": out,
        "reminder": "Reports are SELF_REPORTED by the sender. Probe before relying on one.",
    }
    if hidden_sensitive:
        result["hidden_sensitive"] = hidden_sensitive
        result["hidden_reason"] = (
            "decision/blocked rows are visible to verified actors only (F13 2026-10-21)"
        )
    return result


def _cursor_path(reader: str) -> Path:
    safe = "".join(c for c in (reader or "unknown") if c.isalnum() or c in "-_")[:40] or "unknown"
    return CURSOR_DIR / f"{safe}.cursor"


def _load_cursor(reader: str) -> str | None:
    p = _cursor_path(reader)
    try:
        return p.read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def _save_cursor(reader: str, ts: str) -> None:
    _ensure_dirs()
    try:
        _cursor_path(reader).write_text(ts, encoding="utf-8")
    except OSError:
        logger.exception("report lane: cursor write failed")


def _parse_ts(v: Any) -> datetime | None:
    if not isinstance(v, str) or not v:
        return None
    try:
        dt = datetime.fromisoformat(v)
    except ValueError:
        return None
    return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt


def _thread_first_ts(thread_id: str) -> datetime | None:
    """Timestamp laporan PERTAMA dalam thread (dari INBOX)."""
    ts_list = [
        t
        for t in (
            _parse_ts(r.get("ts")) for r in _read_all(INBOX) if r.get("thread_id") == thread_id
        )
        if t is not None
    ]
    return min(ts_list) if ts_list else None


def _ack_after_floor(ack_ts: Any, first_ts: datetime) -> bool:
    a = _parse_ts(ack_ts)
    if a is None:
        return False  # ts tak boleh parse — jangan kira (fail-closed)
    return (a - first_ts).total_seconds() >= ACK_DELIBERATION_MIN_S


def _thread_ackers(thread_id: str | None) -> list[str]:
    """Distinct agent ids that have vouched for this thread. Never the author.

    [F13 2026-10-21] Lantai persidangan — ack kira HANYA jika difailkan
    ≥ ACK_DELIBERATION_MIN_S selepas laporan pertama thread. Thread tanpa
    laporan pertama yang diketahui (bukan dalam INBOX) tidak boleh capai
    quorum langsung (fail-closed).
    """
    if not thread_id:
        return []
    first_ts = _thread_first_ts(thread_id)
    if first_ts is None:
        return []
    seen: list[str] = []
    for row in _read_all(ACKS):
        if row.get("thread_id") != thread_id:
            continue
        # F13 2026-10-21 (sovereign "ya"): quorum counts VERIFIED acks only.
        # Rows before this field existed (burst-ack test data) carry no
        # reader_verified → excluded. Fail-closed.
        if not row.get("reader_verified"):
            continue
        if not _ack_after_floor(row.get("ts"), first_ts):
            continue
        who = row.get("reader")
        if who and who not in seen:
            seen.append(who)
    return seen


def ack(
    *,
    reader: str,
    report_id: str,
    thread_id: str | None = None,
    verified_actor: bool = False,
) -> dict[str, Any]:
    """Vouch for a thread. Agents acknowledge to agents — the human is not told.

    F13 2026-10-21 (sovereign "ya"): ack WAJIB verified session. A self-declared
    reader name is forgeable by any caller, so an unverified "2-ack quorum" was
    worth nothing. Only cryptographically verified agents may vouch — their
    quorum can still escalate an unverified thread, but the vouches themselves
    are no longer spoofable.
    """
    if not verified_actor:
        return {
            "status": "rejected",
            "reason": (
                "ack needs a verified session (ACT/SCT) — self-declared reader "
                "names are forgeable, so they carry no quorum weight. Bind via "
                "arif_init + identity challenge first."
            ),
            "report_id": report_id,
            "reader_verified": False,
        }
    thread = (thread_id or "").strip() or _thread_of(report_id)
    if not thread:
        return {
            "status": "rejected",
            "reason": "no thread_id and report carries none — ack needs a thread to vouch for",
            "report_id": report_id,
        }
    row = {
        "ts": _now(),
        "reader": (reader or "unknown")[:120],
        "reader_verified": True,
        "report_id": report_id,
        "thread_id": thread,
    }
    _append(ACKS, row)
    quorum = _thread_ackers(thread)
    return {
        "status": "recorded",
        "report_id": report_id,
        "thread_id": thread,
        "reader": row["reader"],
        "thread_ackers": quorum,
        "peer_quorum": PEER_QUORUM,
        "quorum_met": len(quorum) >= PEER_QUORUM,
        "note": "Acknowledgement stays in the peer lane; the human is not notified.",
        "ts": row["ts"],
    }


def _thread_of(report_id: str) -> str | None:
    for row in _read_all(INBOX):
        if row.get("report_id") == report_id:
            return row.get("thread_id")
    return None


def pending_for_human() -> list[dict[str, Any]]:
    """Reports queued for a human that have not yet been successfully pushed.

    A report id with ANY successful push (pushed=true) is consumed. Failed
    attempts (pushed=false) stay pending and retry on the next flush — but a
    report never re-pings the human after one successful push (dup-kill,
    fixed 2026-10-21: previously any failed attempt kept the id pending
    forever, so every flush re-pushed the same decisions).
    """
    outbox_rows = _read_all(OUTBOX)
    pushed = {r.get("report_id") for r in outbox_rows if r.get("pushed")}
    queued = {r.get("report_id") for r in outbox_rows} - pushed
    if not queued:
        return []
    return [r for r in _read_all(INBOX) if r.get("report_id") in queued]


def build_human_message(rows: list[dict[str, Any]]) -> str:
    """Compose ONE plain-language message. No jargon, no tables, no menus."""
    if not rows:
        return ""
    lines: list[str] = []
    n = len(rows)
    lines.append(f"{n} perkara tunggu hang." if n > 1 else "Satu perkara tunggu hang.")
    shown = rows[:MAX_ITEMS_PER_PUSH]
    for i, r in enumerate(shown, 1):
        sender = r.get("sender") or "agent"
        subj = (r.get("subject") or "").strip()
        body = (r.get("body") or "").strip().replace("\n", " ")
        if len(body) > BODY_PREVIEW_CHARS:
            body = body[:BODY_PREVIEW_CHARS].rstrip() + "…"
        block = f"\n{i}. {sender}: {subj}"
        if body:
            block += f"\n   {body}"
        lines.append(block)
    if n > len(shown):
        lines.append(f"\nLagi {n - len(shown)} dalam inbox — tak mendesak.")
    lines.append("\nSemua yang tak perlu hang, agent dah handle sendiri.")
    return "\n".join(lines)


def _last_push_ts() -> str | None:
    for row in reversed(_read_all(OUTBOX)):
        if row.get("pushed") and row.get("pushed_at"):
            return str(row.get("pushed_at"))
    return None


def _push_allowed() -> tuple[bool, str]:
    last = _last_push_ts()
    if not last:
        return True, "no prior push"
    try:
        last_dt = datetime.fromisoformat(last)
    except ValueError:
        return True, "unparseable last push timestamp"
    if last_dt.tzinfo is None:
        last_dt = last_dt.replace(tzinfo=UTC)
    wait_until = last_dt + timedelta(minutes=PUSH_WINDOW_MINUTES)
    now = datetime.now(UTC)
    if now < wait_until:
        mins = int((wait_until - now).total_seconds() // 60) + 1
        return False, f"within push window, {mins}m remaining"
    return True, "window elapsed"


def flush_human(*, force: bool = False, dry_run: bool = False) -> dict[str, Any]:
    """Coalesce queued escalations into at most one human message."""
    rows = pending_for_human()
    if not rows:
        return {"status": "nothing_pending", "pushed": 0}

    allowed, why = _push_allowed()
    if not (allowed or force):
        return {"status": "held", "reason": why, "pending": len(rows), "pushed": 0}

    text = build_human_message(rows)
    if dry_run:
        return {"status": "dry_run", "pending": len(rows), "message": text}

    sent, detail = _send_telegram(text)
    now = _now()
    for r in rows:
        _append(
            OUTBOX,
            {"report_id": r.get("report_id"), "pushed": sent, "pushed_at": now, "detail": detail},
        )
    return {
        "status": "pushed" if sent else "send_failed",
        "pushed": len(rows) if sent else 0,
        "detail": detail,
    }


def _send_telegram(text: str) -> tuple[bool, str]:
    """Push to the sovereign DM. Fails closed: never raises, never retries blindly."""
    token = os.getenv("ARIFOS_REPORT_BOT_TOKEN", "").strip()
    chat_id = os.getenv("ARIFOS_REPORT_CHAT_ID", "267378578").strip()
    if not token:
        return False, "no token configured (ARIFOS_REPORT_BOT_TOKEN unset)"
    try:
        import requests

        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": text, "disable_web_page_preview": "true"},
            timeout=20,
        )
        if resp.status_code == 200 and '"ok":true' in resp.text.replace(" ", ""):
            return True, f"message_id={resp.json().get('result', {}).get('message_id')}"
        return False, f"http {resp.status_code}: {resp.text[:160]}"
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


def stats() -> dict[str, Any]:
    rows = _read_all(INBOX)
    by_kind: dict[str, int] = {}
    by_sender: dict[str, int] = {}
    for r in rows:
        by_kind[r.get("kind", "?")] = by_kind.get(r.get("kind", "?"), 0) + 1
        by_sender[r.get("sender", "?")] = by_sender.get(r.get("sender", "?"), 0) + 1
    return {
        "status": "ok",
        "total_reports": len(rows),
        "by_kind": by_kind,
        "by_sender": by_sender,
        "pending_for_human": len(pending_for_human()),
        "push_window_minutes": PUSH_WINDOW_MINUTES,
        "human_classes": sorted(HUMAN_CLASSES),
        "store": str(INBOX),
    }


# ═══════════════════════════════════════════════════════════════════════════
# SESSION RESOLUTION + ΔS ADMISSION — PACKET-AB Changeset A (2026-10-29)
# F13 authorization bound to PACKET-AB-20261029 v1.1, plan_hash
# sha256:1a411120afbac012d79c1cfb…. Fail closed at ADMISSIBILITY, never at
# write: rows keep flowing; only readiness counting refuses to trust them.
# ═══════════════════════════════════════════════════════════════════════════

import re as _re

from arifosmcp.runtime.act_token import UNMEASURED as _UNMEASURED

SESSION_RESOLUTION_VOCAB: frozenset[str] = frozenset(
    {"real", "synthetic", "legacy_unclassified"}
)

# Named limitation (packet §8 R1): shape-based, NOT provenance. A writer can
# mint a real-shaped session id. Provenance binding (envelope call_hash) is
# follow-up packet scope; until then this admission is shape-admission.
_REAL_SESSION_RE = _re.compile(r"^session_[0-9a-f]{8,}")

# ΔS-shaped prose: the pattern two different agents emitted (-0.85, -0.48).
_DELTA_S_CLAIM_RE = _re.compile(r"(?:ΔS|delta_S|delta S)\s*[:=]?\s*-?\d", _re.IGNORECASE)


def classify_session(session: str | None) -> str:
    """Classify a session id by shape into the closed vocabulary."""
    s = (session or "").strip()
    return "real" if _REAL_SESSION_RE.match(s) else "synthetic"


def resolve_row_resolution(row: dict) -> str:
    """Read-time resolution of a telemetry row.

    A row's own stamped field wins when valid; a missing field reads as
    legacy_unclassified (history is never rewritten); anything outside the
    closed vocabulary is invalid and the caller fails closed.
    """
    stamped = row.get("session_resolution")
    if stamped in SESSION_RESOLUTION_VOCAB:
        return stamped
    if stamped is None:
        return "legacy_unclassified"
    return "__invalid__"


def admit_for_readiness(row: dict, *, test_scope: bool = False) -> bool:
    """Admission rule: only real rows may satisfy production readiness.

    synthetic rows count only inside a designated test scope; legacy and
    invalid rows never count. Missing resolution fails CLOSED.
    """
    resolution = resolve_row_resolution(row)
    if resolution == "real":
        return True
    if resolution == "synthetic":
        return bool(test_scope)
    return False  # legacy_unclassified, __invalid__ → fail closed


def readiness_counts(rows: list[dict], *, test_scope: bool = False) -> dict:
    """Aggregate admissibility over a telemetry store.

    readiness is UNMEASURED (house sentinel) when zero real rows are
    admitted — an empty or fixture-only store is not a green reading.
    """
    admitted = sum(1 for r in rows if admit_for_readiness(r, test_scope=test_scope))
    synthetic = sum(1 for r in rows if resolve_row_resolution(r) == "synthetic")
    legacy = sum(1 for r in rows if resolve_row_resolution(r) == "legacy_unclassified")
    invalid = sum(1 for r in rows if resolve_row_resolution(r) == "__invalid__")
    return {
        "admitted_real": admitted,
        "synthetic": synthetic,
        "legacy_unclassified": legacy,
        "invalid": invalid,
        "readiness": "MEASURED" if admitted > 0 else _UNMEASURED,
    }


def bind_delta_s(body: str | None, envelope_call_hash: str | None = None) -> dict:
    """Admission gate for ΔS claims in report prose.

    A ΔS-shaped claim without an envelope call_hash (the only binding a
    later wiring may supply — a hash-shaped string inside the prose itself
    is NOT evidence) stores UNMEASURED with the reason. It can never reach
    a governance field as a number.
    """
    if not _DELTA_S_CLAIM_RE.search(body or ""):
        return {"present": False}
    if envelope_call_hash:
        return {
            "present": True,
            "delta_S": {"value": None, "call_hash": envelope_call_hash},
            "note": "binding wiring lands in a separately authorized changeset",
        }
    return {"present": True, "delta_S": _UNMEASURED, "reason": "NO_BOUND_CALL_HASH"}


if "__all__" in globals():
    __all__ += [
        "SESSION_RESOLUTION_VOCAB",
        "classify_session",
        "resolve_row_resolution",
        "admit_for_readiness",
        "readiness_counts",
        "bind_delta_s",
    ]
