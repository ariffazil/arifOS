"""
producer_context — two-layer model provenance for kernel write lanes.
ARIFOS::AAA_MODEL_GOVERNANCE_RUNTIME_WIRING (producer-context edge, 2026-10-31).

DESIGN LAW (external-critique corrected): the INIT governance card is SESSION
context, NOT per-production-event identity evidence. A card may say glm-5.3
while a fallback/delegation/subagent actually produced an artifact. So this
block NEVER claims observed producer identity — v1 attribution state is
``session_only`` with the limitation named. Honesty over convenience.

Layers:
  session     — what was bound at INIT (card hash, lane, actor)
  production  — what produced THIS artifact (kind; refs stay null until the
                invocation-envelope edge is wired — declared UNKNOWN, never
                copied from the card)
  attribution — explicit state: session_only | session_card | unknown;
                observed_producer_identity stays None in v1.

Fail-closed: no session and no actor → explicit UNKNOWN block with zeroed
references — never fabricated, never silently omitted. Missing provenance
lowers assurance; it does NOT block diagnostic write lanes (each lane decides
its own policy; this module only labels).

Callers can NOT inject a producer_context — only this module mints it,
server-side, from kernel state. Caller-supplied values are never read.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from datetime import datetime, timezone

SCHEMA = "producer-context.v1"
_WRITE_NOTE = "no_per_invocation_identity_evidence"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _from_card(card: dict | None) -> dict:
    """Two-layer block from a stored session governance card."""
    if not isinstance(card, dict):
        return _unknown(None, None)
    sess_binding = card.get("session_binding") or {}
    return {
        "schema": SCHEMA,
        "session": {
            "lane": sess_binding.get("lane") or card.get("lane_id"),
            "actor_id": sess_binding.get("actor_id"),
            "governance_card_hash": card.get("card_hash"),
            "registry_revision": card.get("registry_revision"),
        },
        "production": {
            "producer_kind": "model",
            "invocation_ref": None,
            "requested_model": card.get("requested_model"),
            "provider_reported_model": None,
            "route_receipt_ref": card.get("resolution_evidence_ref"),
        },
        "attribution": {
            "state": "session_only",
            "basis": "stored_session_card",
            "observed_producer_identity": None,
            "identity_state": card.get("identity_state"),
            "limitations": [_WRITE_NOTE],
        },
        "produced_at": _now(),
    }


def _unknown(session_id, actor_id) -> dict:
    """Fail-closed block — explicit, never fabricated, never silent."""
    return {
        "schema": SCHEMA,
        "session": {
            "session_id": session_id,
            "actor_id": actor_id,
            "governance_card_hash": None,
            "registry_revision": None,
        },
        "production": {
            "producer_kind": "unknown",
            "invocation_ref": None,
            "requested_model": None,
            "provider_reported_model": None,
            "route_receipt_ref": None,
        },
        "attribution": {
            "state": "unknown",
            "basis": "no_session_card",
            "observed_producer_identity": None,
            "identity_state": "UNKNOWN",
            "limitations": [_WRITE_NOTE, "no_session_card"],
        },
        "produced_at": _now(),
    }


def build_producer_context(
    session_id: str | None = None,
    actor_id: str | None = None,
    session_token: str | None = None,  # reserved: SCT-keyed lookup when wired
) -> dict:
    """Mint one producer_context block. Server-side only; never caller-supplied."""
    card = None
    if session_id:
        try:
            from arifosmcp.runtime.tools import _SESSIONS

            sess = _SESSIONS.get(session_id)
            if isinstance(sess, dict):
                card = sess.get("model_governance")
        except Exception:  # noqa: BLE001 — provenance must never break a write lane
            card = None
    if card is None and actor_id:
        try:
            from arifosmcp.tools.session import _build_model_governance

            card = _build_model_governance(actor_id)
        except Exception:  # noqa: BLE001
            card = None
    if card is None:
        return _unknown(session_id, actor_id)
    block = _from_card(card)
    block["session"]["session_id"] = session_id
    block["session"]["actor_id"] = block["session"].get("actor_id") or actor_id
    return block
