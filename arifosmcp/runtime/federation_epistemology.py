"""
Federation epistemic read layer for arifOS.

Builds a queryable institutional belief state across federated nodes by
normalizing epistemic events into a local VAULT999-backed ledger and
synthesizing claim state, witness completeness, and truth drift.
"""

from __future__ import annotations

import json
import logging
import math
import os
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from arifosmcp.schemas.claim import (
    AuthorityClass,
    ClaimPolarity,
    EpistemicEventType,
    FederationEpistemicEvent,
)

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS federation_subjects (
    subject_id TEXT PRIMARY KEY,
    subject_name TEXT NOT NULL,
    aliases_json TEXT NOT NULL DEFAULT '[]',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS federation_epistemic_events (
    event_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    claim_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    agent_role TEXT NOT NULL,
    domain TEXT NOT NULL,
    authority_class TEXT NOT NULL,
    event_type TEXT NOT NULL,
    polarity TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_value TEXT NOT NULL DEFAULT '',
    claim_text TEXT NOT NULL,
    confidence REAL NOT NULL,
    evidence_refs_json TEXT NOT NULL DEFAULT '[]',
    supporting_claim_ids_json TEXT NOT NULL DEFAULT '[]',
    contradicting_claim_ids_json TEXT NOT NULL DEFAULT '[]',
    decision_refs_json TEXT NOT NULL DEFAULT '[]',
    outcome_refs_json TEXT NOT NULL DEFAULT '[]',
    witness_required INTEGER NOT NULL DEFAULT 0,
    claim_status TEXT NOT NULL DEFAULT 'proposed',
    seal_level TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    timestamp TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'ledger'
);

CREATE INDEX IF NOT EXISTS idx_federation_events_subject
    ON federation_epistemic_events(subject_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_federation_events_claim
    ON federation_epistemic_events(claim_id, timestamp);
"""

_AUTHORITY_WEIGHTS: dict[str, float] = {
    AuthorityClass.GROUND_EVIDENCE.value: 1.25,
    AuthorityClass.CAPITAL_ANALYSIS.value: 1.05,
    AuthorityClass.DELIBERATIVE_JUDGMENT.value: 1.15,
    AuthorityClass.GOVERNANCE_CONTROL.value: 1.15,
    AuthorityClass.HUMAN_SUBSTRATE.value: 1.0,
    AuthorityClass.EXECUTION_REALITY.value: 1.2,
    AuthorityClass.OPS_TELEMETRY.value: 0.95,
    AuthorityClass.MEMORY_LINEAGE.value: 0.9,
}

_EVENT_WEIGHTS: dict[str, float] = {
    EpistemicEventType.ASSERTION.value: 1.0,
    EpistemicEventType.VERIFICATION.value: 1.15,
    EpistemicEventType.WITNESS.value: 1.1,
    EpistemicEventType.DECISION.value: 0.95,
    EpistemicEventType.OUTCOME.value: 1.25,
    EpistemicEventType.RETRACTION.value: 1.2,
    EpistemicEventType.SEAL.value: 1.2,
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _vault_dir() -> Path:
    raw = (
        os.getenv("ARIFOS_VAULT_DIR")
        or os.getenv("VAULT999_PATH")
        or str(Path(__file__).resolve().parents[2] / "VAULT999")
    )
    path = Path(raw)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _db_path() -> Path:
    return _vault_dir() / "federation_epistemology.db"


def _audit_path() -> Path:
    return _vault_dir() / "FEDERATION_EPISTEMIC_EVENTS.jsonl"


def _sealed_events_path() -> Path:
    return _vault_dir() / "SEALED_EVENTS.jsonl"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


def _json_load(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _row_to_event(row: sqlite3.Row) -> FederationEpistemicEvent:
    return FederationEpistemicEvent(
        event_id=row["event_id"],
        subject_id=row["subject_id"],
        claim_id=row["claim_id"],
        node_id=row["node_id"],
        agent_role=row["agent_role"],
        domain=row["domain"],
        authority_class=row["authority_class"],
        event_type=row["event_type"],
        polarity=row["polarity"],
        predicate=row["predicate"],
        object_value=row["object_value"],
        claim_text=row["claim_text"],
        confidence=row["confidence"],
        evidence_refs=_json_load(row["evidence_refs_json"], []),
        supporting_claim_ids=_json_load(row["supporting_claim_ids_json"], []),
        contradicting_claim_ids=_json_load(row["contradicting_claim_ids_json"], []),
        decision_refs=_json_load(row["decision_refs_json"], []),
        outcome_refs=_json_load(row["outcome_refs_json"], []),
        witness_required=bool(row["witness_required"]),
        claim_status=row["claim_status"],
        seal_level=row["seal_level"],
        metadata=_json_load(row["metadata_json"], {}),
        timestamp=datetime.fromisoformat(row["timestamp"]),
    )


def _enum_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _event_to_dict(event: FederationEpistemicEvent) -> dict[str, Any]:
    return {
        "event_id": event.event_id,
        "subject_id": event.subject_id,
        "subject_name": event.subject_name,
        "claim_id": event.claim_id,
        "claim_text": event.claim_text,
        "predicate": event.predicate,
        "object_value": event.object_value,
        "event_type": _enum_value(event.event_type),
        "polarity": _enum_value(event.polarity),
        "node_id": event.node_id,
        "agent_role": event.agent_role,
        "domain": event.domain,
        "authority_class": _enum_value(event.authority_class),
        "confidence": event.confidence,
        "evidence_refs": list(event.evidence_refs),
        "supporting_claim_ids": list(event.supporting_claim_ids),
        "contradicting_claim_ids": list(event.contradicting_claim_ids),
        "decision_refs": list(event.decision_refs),
        "outcome_refs": list(event.outcome_refs),
        "witness_required": event.witness_required,
        "claim_status": event.claim_status,
        "seal_level": event.seal_level,
        "timestamp": event.timestamp.isoformat(),
        "metadata": dict(event.metadata),
    }


def _normalise_subject_key(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def _default_subject_name(subject_id: str) -> str:
    return subject_id.replace("-", " ").replace("_", " ").strip() or subject_id


def _freshness_weight(timestamp: datetime) -> float:
    age_days = max(0.0, (_utcnow() - timestamp).total_seconds() / 86_400.0)
    return max(0.45, math.pow(0.985, age_days))


def _confidence_band(score: float) -> str:
    if score >= 0.85:
        return "very_high"
    if score >= 0.7:
        return "high"
    if score >= 0.55:
        return "moderate"
    if score >= 0.4:
        return "low"
    return "very_low"


def _coerce_event(payload: dict[str, Any], source: str) -> FederationEpistemicEvent | None:
    raw = dict(payload)
    candidate = raw.get("epistemic") or raw.get("federation_epistemic")
    if candidate is None and isinstance(raw.get("payload"), dict):
        body = dict(raw["payload"])
        candidate = body.get("epistemic") or body.get("federation_epistemic")
        if candidate is None and {"subject_id", "claim_id", "predicate"} <= set(body):
            candidate = body
    elif {"subject_id", "claim_id", "predicate"} <= set(raw):
        candidate = raw

    if not isinstance(candidate, dict):
        return None

    subject_id = str(candidate.get("subject_id") or "").strip()
    claim_id = str(candidate.get("claim_id") or "").strip()
    predicate = str(candidate.get("predicate") or "").strip()
    if not subject_id or not claim_id or not predicate:
        return None

    claim_text = str(candidate.get("claim_text") or candidate.get("claim") or "").strip()
    if not claim_text:
        object_value = str(candidate.get("object_value") or candidate.get("value") or "").strip()
        claim_text = f"{subject_id}::{predicate}::{object_value}".strip(":")
    else:
        object_value = str(candidate.get("object_value") or candidate.get("value") or "").strip()

    timestamp_raw = candidate.get("timestamp") or raw.get("sealed_at") or raw.get("created_at")
    try:
        timestamp = (
            datetime.fromisoformat(timestamp_raw) if isinstance(timestamp_raw, str) else _utcnow()
        )
    except ValueError:
        timestamp = _utcnow()

    try:
        return FederationEpistemicEvent(
            event_id=str(candidate.get("event_id") or raw.get("event_id") or claim_id),
            subject_id=subject_id,
            subject_name=candidate.get("subject_name"),
            claim_id=claim_id,
            claim_text=claim_text,
            predicate=predicate,
            object_value=object_value,
            event_type=candidate.get("event_type") or raw.get("event_type") or "assertion",
            polarity=candidate.get("polarity") or "supports",
            node_id=str(candidate.get("node_id") or raw.get("actor_id") or "vault"),
            agent_role=str(candidate.get("agent_role") or raw.get("stage") or "vault"),
            domain=str(candidate.get("domain") or "federation"),
            authority_class=str(
                candidate.get("authority_class") or AuthorityClass.MEMORY_LINEAGE.value
            ),
            confidence=float(candidate.get("confidence", 0.5)),
            evidence_refs=list(candidate.get("evidence_refs") or candidate.get("evidence") or []),
            supporting_claim_ids=list(candidate.get("supporting_claim_ids") or []),
            contradicting_claim_ids=list(candidate.get("contradicting_claim_ids") or []),
            decision_refs=list(candidate.get("decision_refs") or []),
            outcome_refs=list(candidate.get("outcome_refs") or []),
            witness_required=bool(candidate.get("witness_required", False)),
            claim_status=str(candidate.get("claim_status") or raw.get("verdict") or "proposed"),
            seal_level=candidate.get("seal_level"),
            timestamp=timestamp,
            metadata={"source": source},
        )
    except Exception as exc:
        logger.debug("Skipping malformed epistemic event from %s: %s", source, exc)
        return None


class FederationEpistemicLedger:
    def __init__(self) -> None:
        self._conn = _connect()

    def close(self) -> None:
        self._conn.close()

    def record_event(self, event: FederationEpistemicEvent) -> dict[str, Any]:
        now = _utcnow().isoformat()
        subject_name = event.subject_name or _default_subject_name(event.subject_id)
        self._conn.execute(
            """
            INSERT INTO federation_subjects (
                subject_id, subject_name, aliases_json, metadata_json, created_at, updated_at
            ) VALUES (?, ?, '[]', '{}', ?, ?)
            ON CONFLICT(subject_id) DO UPDATE SET
                subject_name = excluded.subject_name,
                updated_at = excluded.updated_at
            """,
            (event.subject_id, subject_name, now, now),
        )
        self._conn.execute(
            """
            INSERT OR REPLACE INTO federation_epistemic_events (
                event_id, subject_id, claim_id, node_id, agent_role, domain,
                authority_class, event_type, polarity, predicate, object_value, claim_text,
                confidence, evidence_refs_json, supporting_claim_ids_json,
                contradicting_claim_ids_json, decision_refs_json, outcome_refs_json,
                witness_required, claim_status, seal_level, metadata_json, timestamp, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ledger')
            """,
            (
                event.event_id,
                event.subject_id,
                event.claim_id,
                event.node_id,
                event.agent_role,
                event.domain,
                _enum_value(event.authority_class),
                _enum_value(event.event_type),
                _enum_value(event.polarity),
                event.predicate,
                event.object_value,
                event.claim_text,
                event.confidence,
                json.dumps(event.evidence_refs),
                json.dumps(event.supporting_claim_ids),
                json.dumps(event.contradicting_claim_ids),
                json.dumps(event.decision_refs),
                json.dumps(event.outcome_refs),
                1 if event.witness_required else 0,
                event.claim_status,
                event.seal_level,
                json.dumps(event.metadata),
                event.timestamp.isoformat(),
            ),
        )
        self._conn.commit()
        with _audit_path().open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(_event_to_dict(event), ensure_ascii=False) + "\n")
        return {"status": "recorded", "event_id": event.event_id, "subject_id": event.subject_id}

    def stats(self) -> dict[str, Any]:
        subject_count = self._conn.execute(
            "SELECT COUNT(*) AS count FROM federation_subjects"
        ).fetchone()["count"]
        event_count = self._conn.execute(
            "SELECT COUNT(*) AS count FROM federation_epistemic_events"
        ).fetchone()["count"]
        bootstrap_count = sum(1 for _ in self._bootstrap_events())
        return {
            "status": "enabled",
            "subjects": int(subject_count),
            "ledger_events": int(event_count),
            "bootstrap_events": int(bootstrap_count),
            "sources": ["ledger", "vault_bootstrap"],
            "witness_oracle": "active",
            "belief_query": "active",
        }

    def belief_state(
        self,
        *,
        query: str | None = None,
        subject_id: str | None = None,
        claim_id: str | None = None,
        include_events: bool = False,
        include_lineage: bool = True,
    ) -> dict[str, Any]:
        all_events = self._events_with_bootstrap()
        if claim_id:
            claim_events = [event for event in all_events if event.claim_id == claim_id]
            if not claim_events:
                return {
                    "status": "no_evidence",
                    "federation_position": "held",
                    "claim_id": claim_id,
                    "reason": "No epistemic events found for the requested claim.",
                }
            resolved_subject = claim_events[0].subject_id
            subject_events = [event for event in all_events if event.subject_id == resolved_subject]
        else:
            resolved_subject = subject_id or self._resolve_subject_id(all_events, query)
            if not resolved_subject:
                return {
                    "status": "no_evidence",
                    "federation_position": "held",
                    "query": query,
                    "reason": "No matching federation subject found.",
                }
            subject_events = [event for event in all_events if event.subject_id == resolved_subject]

        if not subject_events:
            return {
                "status": "no_evidence",
                "federation_position": "held",
                "subject_id": resolved_subject,
                "reason": "No epistemic events found for the resolved subject.",
            }

        claim_groups: dict[str, list[FederationEpistemicEvent]] = defaultdict(list)
        for event in subject_events:
            claim_groups[event.claim_id].append(event)

        claim_states = [
            self._synthesise_claim_state(events)
            for events in sorted(
                claim_groups.values(),
                key=lambda group: max(item.timestamp for item in group),
                reverse=True,
            )
        ]
        top_claim = claim_states[0]
        contributors = sorted({node for state in claim_states for node in state["contributors"]})
        last_changed_at = max(event.timestamp for event in subject_events).isoformat()
        aggregate_score = sum(state["belief_score"] for state in claim_states) / max(
            len(claim_states), 1
        )
        witness = self._subject_witness_audit(subject_events, claim_states)
        contradiction_count = sum(len(state["contradicting_claims"]) for state in claim_states)
        position = top_claim["state"] if len(claim_states) == 1 else "compound"
        result = {
            "status": "ok",
            "subject_id": resolved_subject,
            "subject_name": self._subject_name(resolved_subject, subject_events),
            "query": query,
            "federation_position": position,
            "confidence_band": _confidence_band(aggregate_score),
            "belief_score": round(aggregate_score, 4),
            "contributors": contributors,
            "claims": claim_states,
            "contradiction_count": contradiction_count,
            "witness_status": witness["status"],
            "witness_audit": witness if include_lineage else {"status": witness["status"]},
            "last_changed_at": last_changed_at,
            "truth_dynamics": self._truth_dynamics(subject_events, claim_states),
        }
        if include_events:
            result["events"] = [
                _event_to_dict(event)
                for event in sorted(subject_events, key=lambda item: item.timestamp, reverse=True)
            ]
        return result

    def claim_lineage(self, claim_id: str) -> dict[str, Any]:
        events = [event for event in self._events_with_bootstrap() if event.claim_id == claim_id]
        if not events:
            return {
                "status": "not_found",
                "claim_id": claim_id,
                "reason": "No lineage found for the requested claim.",
            }
        state = self._synthesise_claim_state(events)
        return {
            "status": "ok",
            "claim_id": claim_id,
            "subject_id": events[0].subject_id,
            "claim_state": state,
            "lineage": [
                _event_to_dict(event) for event in sorted(events, key=lambda item: item.timestamp)
            ],
            "witness_audit": self._claim_witness_audit(events, state),
        }

    def witness_audit(
        self,
        *,
        subject_id: str | None = None,
        claim_id: str | None = None,
        query: str | None = None,
    ) -> dict[str, Any]:
        if claim_id:
            lineage = self.claim_lineage(claim_id)
            return lineage.get("witness_audit", {"status": "not_found", "claim_id": claim_id})
        state = self.belief_state(
            subject_id=subject_id,
            query=query,
            include_events=False,
            include_lineage=True,
        )
        if state.get("status") != "ok":
            return {
                "status": "not_found",
                "subject_id": subject_id,
                "query": query,
                "reason": state.get("reason", "No witness chain available."),
            }
        return dict(state["witness_audit"], subject_id=state["subject_id"])

    def _events_with_bootstrap(self) -> list[FederationEpistemicEvent]:
        events = self._ledger_events()
        seen_ids = {event.event_id for event in events}
        for event in self._bootstrap_events():
            if event.event_id not in seen_ids:
                events.append(event)
                seen_ids.add(event.event_id)
        return events

    def _ledger_events(self) -> list[FederationEpistemicEvent]:
        rows = self._conn.execute(
            "SELECT * FROM federation_epistemic_events ORDER BY timestamp ASC"
        ).fetchall()
        return [_row_to_event(row) for row in rows]

    def _bootstrap_events(self) -> list[FederationEpistemicEvent]:
        bootstrap: list[FederationEpistemicEvent] = []
        for path, source in (
            (_audit_path(), "ledger_audit"),
            (_sealed_events_path(), "vault_bootstrap"),
        ):
            if not path.exists():
                continue
            with path.open(encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        raw = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    event = _coerce_event(raw, source)
                    if event is not None:
                        bootstrap.append(event)
        return bootstrap

    def _resolve_subject_id(
        self, events: list[FederationEpistemicEvent], query: str | None
    ) -> str | None:
        if not query:
            return None
        needle = _normalise_subject_key(query)
        score_map: dict[str, int] = defaultdict(int)
        for event in events:
            haystacks = {
                _normalise_subject_key(event.subject_id),
                _normalise_subject_key(event.subject_name or ""),
                _normalise_subject_key(event.claim_text),
                _normalise_subject_key(event.predicate),
                _normalise_subject_key(event.object_value),
            }
            for haystack in haystacks:
                if not haystack:
                    continue
                if needle == haystack:
                    score_map[event.subject_id] += 5
                elif needle in haystack or haystack in needle:
                    score_map[event.subject_id] += 2
        if not score_map:
            return None
        return max(score_map.items(), key=lambda item: item[1])[0]

    def _subject_name(self, subject_id: str, events: list[FederationEpistemicEvent]) -> str:
        row = self._conn.execute(
            "SELECT subject_name FROM federation_subjects WHERE subject_id = ?",
            (subject_id,),
        ).fetchone()
        if row and row["subject_name"]:
            return row["subject_name"]
        for event in events:
            if event.subject_name:
                return event.subject_name
        return _default_subject_name(subject_id)

    def _event_weight(self, event: FederationEpistemicEvent) -> float:
        authority = _AUTHORITY_WEIGHTS.get(_enum_value(event.authority_class), 1.0)
        event_weight = _EVENT_WEIGHTS.get(_enum_value(event.event_type), 1.0)
        return (
            authority
            * event_weight
            * max(0.05, event.confidence)
            * _freshness_weight(event.timestamp)
        )

    def _synthesise_claim_state(self, events: list[FederationEpistemicEvent]) -> dict[str, Any]:
        ordered = sorted(events, key=lambda item: item.timestamp)
        support = 0.0
        contradict = 0.0
        uncertain = 0.0
        contributors: set[str] = set()
        evidence_refs: set[str] = set()
        contradicting_claims: set[str] = set()
        decision_refs: set[str] = set()
        outcome_refs: set[str] = set()
        latest = ordered[-1]

        for event in ordered:
            weight = self._event_weight(event)
            contributors.add(event.node_id)
            evidence_refs.update(event.evidence_refs)
            contradicting_claims.update(event.contradicting_claim_ids)
            decision_refs.update(event.decision_refs)
            outcome_refs.update(event.outcome_refs)
            if _enum_value(event.polarity) == ClaimPolarity.SUPPORTS.value:
                support += weight
            elif _enum_value(event.polarity) == ClaimPolarity.CONTRADICTS.value:
                contradict += weight
            else:
                uncertain += weight

        total = support + contradict + uncertain
        score = (
            0.5 if total == 0 else max(0.0, min(1.0, (support - contradict + total) / (2 * total)))
        )
        has_verification = any(
            _enum_value(event.event_type)
            in {
                EpistemicEventType.VERIFICATION.value,
                EpistemicEventType.WITNESS.value,
            }
            for event in ordered
        )
        has_seal = any(
            _enum_value(event.event_type) == EpistemicEventType.SEAL.value for event in ordered
        )
        has_retraction = any(
            _enum_value(event.event_type) == EpistemicEventType.RETRACTION.value
            for event in ordered
        ) or latest.claim_status in {"retracted", "superseded"}

        if has_retraction:
            state = (
                latest.claim_status
                if latest.claim_status in {"retracted", "superseded"}
                else "retracted"
            )
        elif contradict > 0 and abs(support - contradict) / max(total, 0.01) < 0.2:
            state = "contested"
        elif has_seal and score >= 0.75:
            state = "sealed"
        elif has_verification and score >= 0.65:
            state = "verified"
        elif score >= 0.55:
            state = "provisional"
        else:
            state = "unsupported"

        return {
            "claim_id": latest.claim_id,
            "claim_text": latest.claim_text,
            "predicate": latest.predicate,
            "object_value": latest.object_value,
            "state": state,
            "belief_score": round(score, 4),
            "confidence_band": _confidence_band(score),
            "contributors": sorted(contributors),
            "evidence_refs": sorted(evidence_refs),
            "contradicting_claims": sorted(contradicting_claims),
            "decision_refs": sorted(decision_refs),
            "outcome_refs": sorted(outcome_refs),
            "last_event_type": _enum_value(latest.event_type),
            "last_changed_at": latest.timestamp.isoformat(),
            "witness_required": any(event.witness_required for event in ordered),
        }

    def _claim_witness_audit(
        self, events: list[FederationEpistemicEvent], claim_state: dict[str, Any]
    ) -> dict[str, Any]:
        event_types = {_enum_value(event.event_type) for event in events}
        evidence_refs = sorted({ref for event in events for ref in event.evidence_refs})
        gaps: list[str] = []
        if not evidence_refs:
            gaps.append("evidence_missing")
        if EpistemicEventType.DECISION.value in event_types and not evidence_refs:
            gaps.append("decision_without_evidence")
        if claim_state["witness_required"] and not (
            EpistemicEventType.WITNESS.value in event_types
            or EpistemicEventType.VERIFICATION.value in event_types
            or EpistemicEventType.SEAL.value in event_types
        ):
            gaps.append("witness_missing")
        if (
            claim_state["state"] in {"verified", "sealed"}
            and EpistemicEventType.VERIFICATION.value not in event_types
            and EpistemicEventType.WITNESS.value not in event_types
        ):
            gaps.append("verification_missing")

        if gaps:
            status = "trace-partial"
        elif evidence_refs:
            status = "trace-complete"
        else:
            status = "evidence-gap"

        return {
            "status": status,
            "claim_id": claim_state["claim_id"],
            "evidence_refs": evidence_refs,
            "event_types": sorted(event_types),
            "gaps": gaps,
            "decision_refs": claim_state["decision_refs"],
            "outcome_refs": claim_state["outcome_refs"],
        }

    def _subject_witness_audit(
        self,
        events: list[FederationEpistemicEvent],
        claim_states: list[dict[str, Any]],
    ) -> dict[str, Any]:
        claim_audits = [
            self._claim_witness_audit(
                [event for event in events if event.claim_id == claim_state["claim_id"]],
                claim_state,
            )
            for claim_state in claim_states
        ]
        statuses = {audit["status"] for audit in claim_audits}
        if statuses == {"trace-complete"}:
            status = "trace-complete"
        elif "trace-partial" in statuses or "evidence-gap" in statuses:
            status = "trace-partial"
        else:
            status = "held"
        return {
            "status": status,
            "claims": claim_audits,
            "gaps": sorted({gap for audit in claim_audits for gap in audit.get("gaps", [])}),
        }

    def _truth_dynamics(
        self,
        events: list[FederationEpistemicEvent],
        claim_states: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not events:
            return {"mode": "held", "reason": "no_events"}
        latest_at = max(event.timestamp for event in events)
        recent = [
            event for event in events if (latest_at - event.timestamp).total_seconds() <= 86_400 * 7
        ]
        contradictions = sum(
            1 for event in recent if _enum_value(event.polarity) == ClaimPolarity.CONTRADICTS.value
        )
        reversals = sum(
            1
            for event in recent
            if _enum_value(event.event_type) == EpistemicEventType.RETRACTION.value
        )
        if reversals:
            mode = "reversing"
        elif contradictions and contradictions >= len(recent) / 3:
            mode = "contested"
        elif len(recent) >= max(2, len(events) // 2):
            mode = "strengthening"
        else:
            mode = "stabilizing"
        return {
            "mode": mode,
            "recent_event_count": len(recent),
            "contradictions_last_7d": contradictions,
            "retractions_last_7d": reversals,
            "active_claims": len(claim_states),
        }
