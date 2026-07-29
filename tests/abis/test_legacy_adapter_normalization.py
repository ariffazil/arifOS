from arifosmcp.abi.legacy_adapter import normalize_to_v1


def test_unknown_versioned_cloudevent_wraps_in_non_strict_mode() -> None:
    raw = {
        "specversion": "1.0",
        "id": "external-event-1",
        "type": "com.example.unknown",
        "source": "external://producer",
        "data": {"message": "hello"},
    }

    normalized = normalize_to_v1(raw)

    assert normalized.type == "arifos.record.v1.unknown"
    assert normalized.data["_format"] == "1.0"
    assert normalized.data["_raw"] == raw


def test_unknown_named_format_is_sanitized_for_record_type() -> None:
    normalized = normalize_to_v1({"_format": "vendor-format.v2", "payload": True})

    assert normalized.type == "arifos.record.v1.unknown_vendor_format_v"
    assert normalized.data["_format"] == "vendor-format.v2"
