"""CloudEvents v1.0.2 conformance tests."""
import json
from arifosmcp.core.protocols.cloudevents import CloudEvent, federation_event


def test_cloudevent_required_attributes():
    """CloudEvents spec requires specversion, type, source, id."""
    evt = CloudEvent("com.test.event", "/organs/test", {"hello": "world"})
    d = evt.to_dict()
    assert d["specversion"] == "1.0"
    assert d["type"] == "com.test.event"
    assert d["source"] == "/organs/test"
    assert "id" in d
    assert len(d["id"]) > 0

def test_cloudevent_time_iso8601():
    """time must be ISO 8601."""
    evt = CloudEvent("com.test.event", "/organs/test")
    assert "T" in evt.time  # ISO 8601 has T separator

def test_cloudevent_json_roundtrip():
    evt = CloudEvent("com.test.event", "/organs/test", {"key": "value"}, subject="prospect-1")
    json_str = evt.to_json()
    parsed = CloudEvent.from_json(json_str)
    assert parsed.type == "com.test.event"
    assert parsed.source == "/organs/test"
    assert parsed.subject == "prospect-1"
    assert parsed.data == {"key": "value"}

def test_cloudevent_dataschema_optional():
    evt = CloudEvent("com.test.event", "/organs/test", dataschema="https://arif-fazil.com/schemas/prospect")
    d = evt.to_dict()
    assert d["dataschema"] == "https://arif-fazil.com/schemas/prospect"

def test_federation_event_types():
    evt = federation_event("geox.prospect.evaluated", "geox", {"pos": 0.35})
    assert evt.type == "com.ariffazil.geox.prospect.evaluated"
    assert evt.source == "/organs/geox"

def test_federation_event_all_known_types():
    """All FEDERATION_EVENT_TYPES must produce valid events."""
    from arifosmcp.core.protocols.cloudevents import FEDERATION_EVENT_TYPES
    for key in FEDERATION_EVENT_TYPES:
        evt = federation_event(key, "test-organ")
        assert evt.specversion == "1.0"
        assert evt.source == "/organs/test-organ"
        assert len(evt.id) > 0
