"""
CloudEvents v1.0.2 — Inter-Organ Event Envelope.

https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md

Every inter-organ event in the federation MUST be wrapped in a CloudEvents
envelope. This ensures all 9 repos speak the same event language.

TRINITY-33: C9 CLOUD_EVENTS
Layer: Cross-cutting (all organs)
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

# ── CloudEvents v1.0.2 Required Attributes ──────────────────────────
# specversion: "1.0" (fixed)
# type: reverse-DNS event type (e.g., "com.ariffazil.geox.prospect.evaluated")
# source: URI identifying the event producer (e.g., "/organs/geox")
# id: unique event identifier (UUID v4)

# ── Optional Attributes ─────────────────────────────────────────────
# time: ISO 8601 timestamp
# datacontenttype: MIME type of data (default: application/json)
# dataschema: URI to schema
# subject: entity the event is about
# dataref: URI reference to data (for large payloads)


class CloudEvent:
    """CloudEvents v1.0.2 envelope for federation organ events."""

    SPEC_VERSION = "1.0"

    def __init__(
        self,
        event_type: str,
        source: str,
        data: Any = None,
        *,
        subject: str | None = None,
        datacontenttype: str = "application/json",
        dataschema: str | None = None,
        dataref: str | None = None,
        time: str | None = None,
        id: str | None = None,
    ):
        self.specversion = self.SPEC_VERSION
        self.type = event_type
        self.source = source
        self.id = id or str(uuid.uuid4())
        self.time = time or datetime.now(UTC).isoformat()
        self.datacontenttype = datacontenttype
        self.subject = subject
        self.dataschema = dataschema
        self.dataref = dataref
        self.data = data

    def to_dict(self) -> dict:
        """Serialize to CloudEvents JSON format."""
        d = {
            "specversion": self.specversion,
            "type": self.type,
            "source": self.source,
            "id": self.id,
            "time": self.time,
        }
        if self.subject:
            d["subject"] = self.subject
        if self.datacontenttype:
            d["datacontenttype"] = self.datacontenttype
        if self.dataschema:
            d["dataschema"] = self.dataschema
        if self.dataref:
            d["dataref"] = self.dataref
        if self.data is not None:
            d["data"] = self.data
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, d: dict) -> CloudEvent:
        return cls(
            event_type=d["type"],
            source=d["source"],
            data=d.get("data"),
            subject=d.get("subject"),
            datacontenttype=d.get("datacontenttype", "application/json"),
            dataschema=d.get("dataschema"),
            dataref=d.get("dataref"),
            time=d.get("time"),
            id=d.get("id"),
        )

    @classmethod
    def from_json(cls, s: str) -> CloudEvent:
        return cls.from_dict(json.loads(s))


# ── Federation Event Types ──────────────────────────────────────────
# Standardized event types for all organs

FEDERATION_EVENT_TYPES = {
    # GEOX events
    "geox.prospect.evaluated": "com.ariffazil.geox.prospect.evaluated",
    "geox.basin.profiled": "com.ariffazil.geox.basin.profiled",
    "geox.seismic.interpreted": "com.ariffazil.geox.seismic.interpreted",
    "geox.well.ingested": "com.ariffazil.geox.well.ingested",
    # WEALTH events
    "wealth.capital.computed": "com.ariffazil.wealth.capital.computed",
    "wealth.market.snapshot": "com.ariffazil.wealth.market.snapshot",
    "wealth.stress.evaluated": "com.ariffazil.wealth.stress.evaluated",
    # WELL events
    "well.vitality.assessed": "com.ariffazil.well.vitality.assessed",
    "well.readiness.validated": "com.ariffazil.well.readiness.validated",
    # arifOS events
    "arifos.judge.verdict": "com.ariffazil.arifos.judge.verdict",
    "arifos.seal.appended": "com.ariffazil.arifos.seal.appended",
    "arifos.session.init": "com.ariffazil.arifos.session.init",
    # A-FORGE events
    "aforge.execution.started": "com.ariffazil.aforge.execution.started",
    "aforge.execution.completed": "com.ariffazil.aforge.execution.completed",
    "aforge.agent.spawned": "com.ariffazil.aforge.agent.spawned",
    # AAA events
    "aaa.state.registered": "com.ariffazil.aaa.state.registered",
    "aaa.cockpit.alert": "com.ariffazil.aaa.cockpit.alert",
}


def federation_event(
    event_type: str,
    source_organ: str,
    data: Any = None,
    subject: str | None = None,
) -> CloudEvent:
    """Create a federation-standard CloudEvent.

    Args:
        event_type: Key from FEDERATION_EVENT_TYPES or full reverse-DNS type
        source_organ: Organ name (e.g., "geox", "arifos")
        data: Event payload
        subject: Entity the event is about
    """
    if event_type in FEDERATION_EVENT_TYPES:
        event_type = FEDERATION_EVENT_TYPES[event_type]
    return CloudEvent(
        event_type=event_type,
        source=f"/organs/{source_organ}",
        data=data,
        subject=subject,
    )
