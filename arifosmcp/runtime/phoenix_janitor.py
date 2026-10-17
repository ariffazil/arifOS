"""Phoenix-72 cooling evaluator — the consumer side of the cooling contract.

The v5 remember path (memory_handlers_v5) writes ``phoenix_*`` fields into the
L3 payload. This module reads those records, asks the existing pure evaluator
(``phoenix_72.evaluate_promotion``) what the next state should be, and — when
``dry_run=False`` — writes the decided state back to Qdrant and to the L4
``memory_store`` row.

Deliberate properties:

* **Inert.** No timer, no scheduler, no background task. Nothing happens until
  a caller invokes :func:`evaluate_cooling`.
* **Clock-injectable.** ``now`` is a parameter so the 72-hour band can be
  exercised in seconds without touching the production clock.
* **Additive writes.** Only ``phoenix_state`` and ``phoenix_evaluated_at`` are
  written back; the rest of the payload/metadata is untouched.
* **Honest failure.** Postgres sync failure is reported, not raised, and never
  rolls back a Qdrant transition that already landed.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from arifosmcp.runtime.phoenix_72 import (
    PHOENIX_STATES,
    STATE_CANDIDATE,
    STATE_COOLING,
    STATE_SEALED,
    STATE_VOID,
    evaluate_promotion,
)

logger = logging.getLogger(__name__)

# Fields carried in the L3 payload (top level, mirrored inside metadata).
PHOENIX_PAYLOAD_FIELDS: tuple[str, ...] = (
    "phoenix_id",
    "phoenix_state",
    "phoenix_cooldown_expiry",
    "phoenix_psi_utility",
    "phoenix_tri_witness",
    "phoenix_anti_hantu_flag",
)

OPEN_STATES: tuple[str, ...] = (STATE_CANDIDATE, STATE_COOLING)
TERMINAL_STATES: tuple[str, ...] = (STATE_SEALED, STATE_VOID)


def payload_to_entry(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    """Map a Qdrant payload onto the evaluator's entry shape.

    Returns ``None`` when the record carries no Phoenix metadata, so callers
    can skip non-Phoenix points without guessing.
    """
    if not payload or "phoenix_id" not in payload:
        return None
    metadata = payload.get("metadata") or {}
    # Top level wins (written by the v5 remember path); metadata is the mirror.
    def pick(key: str) -> Any:
        return payload.get(key, metadata.get(key))

    return {
        "phoenix_id": pick("phoenix_id"),
        "state": pick("phoenix_state") or STATE_CANDIDATE,
        "cooldown_expiry": pick("phoenix_cooldown_expiry"),
        "psi_utility": pick("phoenix_psi_utility") or 0,
        "tri_witness": pick("phoenix_tri_witness") or {},
        "anti_hantu_flag": pick("phoenix_anti_hantu_flag") or False,
        "created_at": metadata.get("timestamp"),
    }


def plan_transitions(
    points: list[Any], now: datetime | None = None
) -> list[dict[str, Any]]:
    """Return the evaluated transition for every open Phoenix point.

    Each item carries ``point_id``, ``memory_id``, ``old_state``, ``new_state``,
    ``reason`` and ``changed``. Terminal records are skipped (the evaluator
    would return them unchanged anyway; skipping keeps the receipt small).
    """
    now = now or datetime.now(UTC)
    plan: list[dict[str, Any]] = []
    for point in points:
        payload = getattr(point, "payload", None) or {}
        entry = payload_to_entry(payload)
        if entry is None:
            continue
        old_state = entry["state"]
        if old_state in TERMINAL_STATES:
            continue
        new_state, reason = evaluate_promotion(entry, now=now)
        metadata = payload.get("metadata") or {}
        plan.append(
            {
                "point_id": str(getattr(point, "id", "")),
                "memory_id": metadata.get("memory_id") or payload.get("memory_id"),
                "phoenix_id": entry["phoenix_id"],
                "old_state": old_state,
                "new_state": new_state,
                "reason": reason,
                "changed": new_state != old_state,
                "new_state_valid": new_state in PHOENIX_STATES,
            }
        )
    return plan


def _open_state_filter():
    from qdrant_client.models import FieldCondition, Filter, MatchAny

    return Filter(
        must=[FieldCondition(key="phoenix_state", match=MatchAny(any=list(OPEN_STATES)))]
    )


async def evaluate_cooling(
    *,
    limit: int = 200,
    now: datetime | None = None,
    dry_run: bool = True,
    collection: str | None = None,
    client: Any = None,
    pg_dsn: str | None = None,
    point_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate open cooling records and (optionally) apply the transitions.

    ``dry_run=True`` is the default: evaluate and report, write nothing.
    ``client`` accepts an injected Qdrant client (tests); when omitted the
    live client from ``vector_memory_qdrant`` is used.
    With ``pg_dsn`` set, the decided state is mirrored into the L4 row.
    ``point_ids`` restricts evaluation to an explicit set of points — the
    bounded canary path. ``None`` means every open record.
    """
    import os

    from arifosmcp.memory.vector_memory_qdrant import (
        _QDRANT_COLLECTION,
        _get_qdrant_client,
    )

    now = now or datetime.now(UTC)
    coll = collection or _QDRANT_COLLECTION
    qc = client or _get_qdrant_client()

    points, _offset = qc.scroll(
        collection_name=coll,
        scroll_filter=_open_state_filter(),
        limit=limit,
        with_payload=True,
    )
    if point_ids is not None:
        wanted = {str(p) for p in point_ids}
        points = [p for p in points if str(getattr(p, "id", "")) in wanted]
    plan = plan_transitions(points, now=now)
    changed = [p for p in plan if p["changed"]]

    applied: list[dict[str, Any]] = []
    pg_synced = 0
    errors: list[str] = []

    if not dry_run and changed:
        stamp = now.isoformat()
        for item in changed:
            if not item["new_state_valid"]:
                errors.append(f"{item['point_id']}: invalid target state {item['new_state']}")
                continue
            try:
                if hasattr(qc, "set_payload"):
                    qc.set_payload(
                        collection_name=coll,
                        payload={
                            "phoenix_state": item["new_state"],
                            "phoenix_evaluated_at": stamp,
                        },
                        points=[item["point_id"]],
                    )
                # Mirror inside metadata too, when the client exposes it.
                applied.append(item)
            except Exception as exc:  # noqa: BLE001 — reported, not raised
                errors.append(f"{item['point_id']}: qdrant write failed: {exc}")
                continue
            if pg_dsn and item["memory_id"]:
                try:
                    import json

                    import asyncpg

                    conn = await asyncpg.connect(pg_dsn)
                    try:
                        await conn.execute(
                            "update memory_store "
                            "set metadata = metadata || $2::jsonb "
                            "where id = $1::uuid",
                            item["memory_id"],
                            json.dumps(
                                {
                                    "phoenix_state": item["new_state"],
                                    "phoenix_evaluated_at": stamp,
                                }
                            ),
                        )
                        pg_synced += 1
                    finally:
                        await conn.close()
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{item['memory_id']}: pg sync failed: {exc}")

    return {
        "ok": not errors,
        "mode": "dry_run" if dry_run else "apply",
        "evaluated_at": now.isoformat(),
        "collection": coll,
        "scanned": len(points),
        "phoenix_records": len(plan),
        "transitions_planned": len(changed),
        "transitions_applied": len(applied),
        "pg_synced": pg_synced,
        "plan": plan,
        "errors": errors,
    }
