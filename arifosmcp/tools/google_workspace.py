"""
arifOS Google Workspace Tools
═══════════════════════════════════════════════════════════════════════════════

MCP tools for Gmail, Calendar, Drive, and Sheets management.
Uses OAuth 2.0 credentials from a mounted token.json.

Governance:
  - All mutations (send, create, delete, share) require actor_id for audit.
  - Read-only operations are guarded but lower risk.
  - Token auto-refreshes via google-auth.

Mount point (container): /run/secrets/google_workspace/token.json
Mount point (host):       /root/AAA/.apex/token.json

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

import base64
import json
import logging
import os
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ─── Token resolution ────────────────────────────────────────────────────────
_TOKEN_PATHS = [
    Path("/run/secrets/google_workspace/token.json"),
    Path("/app/google_workspace/token.json"),
    Path(__file__).parents[3] / "AAA" / ".apex" / "token.json",
    Path.home() / ".openclaw" / "gog" / "token.json",
]


def _token_path() -> Path | None:
    for p in _TOKEN_PATHS:
        if p.exists():
            return p
    return None


def _load_creds() -> Any:
    """Load Google OAuth credentials from token.json."""
    from google.oauth2.credentials import Credentials

    p = _token_path()
    if p is None:
        raise RuntimeError(
            "Google Workspace token.json not found. "
            "Run setup_workspace_auth.py first to obtain OAuth tokens."
        )
    return Credentials.from_authorized_user_file(str(p))


def _service(name: str, version: str) -> Any:
    """Build a Google API service client."""
    from googleapiclient.discovery import build

    creds = _load_creds()
    return build(name, version, credentials=creds, cache_discovery=False)


def _result(status: str, data: dict[str, Any], error: str | None = None) -> dict[str, Any]:
    out = {"status": status, "result": data}
    if error:
        out["error"] = error
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# Gmail
# ═══════════════════════════════════════════════════════════════════════════════

def google_gmail_read_unread(
    max_results: int = 10,
    query: str = "is:unread",
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Read unread emails from Gmail.

    Args:
        max_results: Max emails to return (1-50).
        query: Gmail search query, e.g. 'is:unread', 'from:boss@example.com'.
        actor_id: Sovereign actor identifier for audit.
    """
    try:
        svc = _service("gmail", "v1")
        results = (
            svc.users()
            .messages()
            .list(userId="me", q=query, maxResults=min(max_results, 50))
            .execute()
        )
        messages = results.get("messages", [])
        items: list[dict[str, Any]] = []
        for m in messages[:max_results]:
            detail = (
                svc.users()
                .messages()
                .get(
                    userId="me",
                    id=m["id"],
                    format="metadata",
                    metadataHeaders=["Subject", "From", "Date"],
                )
                .execute()
            )
            headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
            items.append(
                {
                    "id": m["id"],
                    "subject": headers.get("Subject", "(no subject)"),
                    "from": headers.get("From", "?"),
                    "date": headers.get("Date", "?"),
                }
            )
        return _result("SEAL", {"count": len(items), "emails": items, "actor_id": actor_id})
    except Exception as e:
        logger.warning(f"google_gmail_read_unread failed: {e}")
        return _result("HOLD", {}, error=str(e))


def google_gmail_send(
    to: str,
    subject: str,
    body: str,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Send an email via Gmail.

    Args:
        to: Recipient email address.
        subject: Email subject.
        body: Plain text body.
        actor_id: Sovereign actor identifier (required for audit).
    """
    if not actor_id:
        return _result("HOLD", {}, error="actor_id is required for send operations (F11 AUTH)")
    try:
        svc = _service("gmail", "v1")
        msg = MIMEText(body)
        msg["to"] = to
        msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        result = svc.users().messages().send(userId="me", body={"raw": raw}).execute()
        return _result(
            "SEAL",
            {
                "message_id": result.get("id"),
                "to": to,
                "subject": subject,
                "actor_id": actor_id,
            },
        )
    except Exception as e:
        logger.warning(f"google_gmail_send failed: {e}")
        return _result("HOLD", {}, error=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Calendar
# ═══════════════════════════════════════════════════════════════════════════════

def google_calendar_list_events(
    max_results: int = 10,
    calendar_id: str = "primary",
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    List upcoming calendar events.

    Args:
        max_results: Number of events to return (1-50).
        calendar_id: Calendar ID ('primary' for main calendar).
        actor_id: Sovereign actor identifier for audit.
    """
    try:
        from datetime import datetime, timezone

        svc = _service("calendar", "v3")
        now = datetime.now(timezone.utc).isoformat()
        events = (
            svc.events()
            .list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=min(max_results, 50),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
            .get("items", [])
        )
        items: list[dict[str, Any]] = []
        for e in events:
            start = e["start"].get("dateTime", e["start"].get("date"))
            items.append(
                {
                    "id": e.get("id"),
                    "summary": e.get("summary", "(no title)"),
                    "start": start,
                    "organizer": e.get("organizer", {}).get("email"),
                    "html_link": e.get("htmlLink"),
                }
            )
        return _result("SEAL", {"count": len(items), "events": items, "actor_id": actor_id})
    except Exception as e:
        logger.warning(f"google_calendar_list_events failed: {e}")
        return _result("HOLD", {}, error=str(e))


def google_calendar_create_event(
    summary: str,
    start_iso: str,
    end_iso: str,
    description: str = "",
    calendar_id: str = "primary",
    timezone: str = "Asia/Kuala_Lumpur",
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Create a calendar event.

    Args:
        summary: Event title.
        start_iso: Start datetime ISO 8601 (e.g. '2026-05-20T10:00:00+08:00').
        end_iso: End datetime ISO 8601.
        description: Event description.
        calendar_id: Calendar ID ('primary' for main calendar).
        timezone: Timezone string.
        actor_id: Sovereign actor identifier (required for audit).
    """
    if not actor_id:
        return _result("HOLD", {}, error="actor_id is required for create operations (F11 AUTH)")
    try:
        svc = _service("calendar", "v3")
        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_iso, "timeZone": timezone},
            "end": {"dateTime": end_iso, "timeZone": timezone},
        }
        result = svc.events().insert(calendarId=calendar_id, body=event).execute()
        return _result(
            "SEAL",
            {
                "event_id": result.get("id"),
                "html_link": result.get("htmlLink"),
                "summary": summary,
                "actor_id": actor_id,
            },
        )
    except Exception as e:
        logger.warning(f"google_calendar_create_event failed: {e}")
        return _result("HOLD", {}, error=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Drive
# ═══════════════════════════════════════════════════════════════════════════════

def google_drive_list_files(
    page_size: int = 15,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    List recent Google Drive files.

    Args:
        page_size: Number of files to return (1-50).
        actor_id: Sovereign actor identifier for audit.
    """
    try:
        svc = _service("drive", "v3")
        files = (
            svc.files()
            .list(
                pageSize=min(page_size, 50),
                fields="files(id,name,mimeType,modifiedTime,webViewLink)",
                orderBy="modifiedTime desc",
            )
            .execute()
            .get("files", [])
        )
        items: list[dict[str, Any]] = []
        for f in files:
            items.append(
                {
                    "id": f["id"],
                    "name": f["name"],
                    "type": f["mimeType"].split(".")[-1],
                    "modified": f["modifiedTime"][:10] if f.get("modifiedTime") else None,
                    "link": f.get("webViewLink"),
                }
            )
        return _result("SEAL", {"count": len(items), "files": items, "actor_id": actor_id})
    except Exception as e:
        logger.warning(f"google_drive_list_files failed: {e}")
        return _result("HOLD", {}, error=str(e))


def google_drive_search(
    query: str,
    page_size: int = 10,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Search Google Drive by file name.

    Args:
        query: Search term for file names.
        page_size: Max results (1-50).
        actor_id: Sovereign actor identifier for audit.
    """
    try:
        svc = _service("drive", "v3")
        escaped = query.replace("'", "\\'")
        q = f"name contains '{escaped}'"
        files = (
            svc.files()
            .list(q=q, pageSize=min(page_size, 50), fields="files(id,name,webViewLink)")
            .execute()
            .get("files", [])
        )
        return _result(
            "SEAL",
            {
                "count": len(files),
                "files": [{"id": f["id"], "name": f["name"], "link": f.get("webViewLink")} for f in files],
                "actor_id": actor_id,
            },
        )
    except Exception as e:
        logger.warning(f"google_drive_search failed: {e}")
        return _result("HOLD", {}, error=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Sheets
# ═══════════════════════════════════════════════════════════════════════════════

def google_sheets_read(
    spreadsheet_id: str,
    range_name: str = "Sheet1!A1:Z100",
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Read values from a Google Sheet.

    Args:
        spreadsheet_id: The Sheet ID from the URL (/d/SHEET_ID/).
        range_name: A1 notation range (e.g. 'Sheet1!A1:E20').
        actor_id: Sovereign actor identifier for audit.
    """
    try:
        svc = _service("sheets", "v4")
        result = svc.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        rows = result.get("values", [])
        return _result(
            "SEAL",
            {
                "spreadsheet_id": spreadsheet_id,
                "range": range_name,
                "row_count": len(rows),
                "rows": rows,
                "actor_id": actor_id,
            },
        )
    except Exception as e:
        logger.warning(f"google_sheets_read failed: {e}")
        return _result("HOLD", {}, error=str(e))


def google_sheets_append(
    spreadsheet_id: str,
    values: list[list[str]],
    range_name: str = "Sheet1",
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Append rows to a Google Sheet.

    Args:
        spreadsheet_id: The Sheet ID from the URL.
        values: List of rows, each row is a list of strings.
        range_name: Target sheet name (e.g. 'Sheet1').
        actor_id: Sovereign actor identifier (required for audit).
    """
    if not actor_id:
        return _result("HOLD", {}, error="actor_id is required for append operations (F11 AUTH)")
    try:
        svc = _service("sheets", "v4")
        body = {"values": values}
        result = (
            svc.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )
        return _result(
            "SEAL",
            {
                "spreadsheet_id": spreadsheet_id,
                "updated_range": result.get("updates", {}).get("updatedRange"),
                "rows_appended": len(values),
                "actor_id": actor_id,
            },
        )
    except Exception as e:
        logger.warning(f"google_sheets_append failed: {e}")
        return _result("HOLD", {}, error=str(e))
