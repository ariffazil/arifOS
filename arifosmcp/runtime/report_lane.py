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
        "sender": (sender or "unknown").strip()[:120],
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
    row["content_hash"] = "sha256:" + hashlib.sha256(
        json.dumps({k2: row[k2] for k2 in ("sender", "subject", "body", "ts")}, sort_keys=True).encode()
    ).hexdigest()

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
) -> dict[str, Any]:
    """Read reports filed by other agents. Pull-only — nothing is pushed."""
    rows = _read_all(INBOX)
    cursor = _load_cursor(reader)
    if since is None and cursor:
        since = cursor

    out: list[dict[str, Any]] = []
    for row in rows:
        if since and str(row.get("ts", "")) <= since:
            continue
        if sender and row.get("sender") != sender:
            continue
        if kind and row.get("kind") != kind:
            continue
        out.append(
            {
                "report_id": row.get("report_id"),
                "ts": row.get("ts"),
                "sender": row.get("sender"),
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

    return {
        "status": "ok",
        "count": len(out),
        "total_filed": len(rows),
        "cursor": latest,
        "reports": out,
        "reminder": "Reports are SELF_REPORTED by the sender. Probe before relying on one.",
    }


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


def _thread_ackers(thread_id: str | None) -> list[str]:
    """Distinct agent ids that have vouched for this thread. Never the author."""
    if not thread_id:
        return []
    seen: list[str] = []
    for row in _read_all(ACKS):
        if row.get("thread_id") != thread_id:
            continue
        who = row.get("reader")
        if who and who not in seen:
            seen.append(who)
    return seen


def ack(*, reader: str, report_id: str, thread_id: str | None = None) -> dict[str, Any]:
    """Vouch for a thread. Agents acknowledge to agents — the human is not told.

    Two distinct acknowledgements on a thread are what allow an unverified
    sender's decision report to reach F13. Acknowledgement is a coordination
    act, not a verdict: it says 'another agent saw this', never 'this is true'.
    """
    thread = (thread_id or "").strip() or _thread_of(report_id)
    if not thread:
        return {
            "status": "rejected",
            "reason": "no thread_id and report carries none — ack needs a thread to vouch for",
            "report_id": report_id,
        }
    row = {"ts": _now(), "reader": (reader or "unknown")[:120], "report_id": report_id, "thread_id": thread}
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
    """Reports queued for a human that have not yet been pushed."""
    queued = {r.get("report_id") for r in _read_all(OUTBOX) if not r.get("pushed")}
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
        _append(OUTBOX, {"report_id": r.get("report_id"), "pushed": sent, "pushed_at": now, "detail": detail})
    return {"status": "pushed" if sent else "send_failed", "pushed": len(rows) if sent else 0, "detail": detail}


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
